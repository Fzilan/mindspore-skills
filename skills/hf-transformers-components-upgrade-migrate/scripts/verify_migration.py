#!/usr/bin/env python
"""
Verification script for MindSpore transformers migration.
Checks for undefined variables, duplicate definitions, and other common issues.
"""

import ast
import sys
import builtins
from pathlib import Path


def is_builtin(name):
    """Check if a name is a Python builtin."""
    return name in dir(builtins) or name in ('__name__', '__file__', '__doc__', '__spec__')


def get_builtins():
    """Get set of all Python builtin names."""
    builtin_names = set(dir(builtins))
    builtin_names.update(['__name__', '__file__', '__doc__', '__spec__', '__all__', '__version__',
                          'True', 'False', 'None', 'NotImplemented', 'Ellipsis'])
    return builtin_names


def analyze_file(filepath):
    """Analyze a Python file for migration issues."""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)

    # Collect definitions at module level only
    defined_names = set()
    defined_functions = {}  # name -> line number
    defined_classes = {}  # name -> line number

    # Track duplicate definitions
    duplicates = []

    # First pass: collect module-level definitions
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                defined_names.add(name)
        elif isinstance(node, ast.FunctionDef):
            if node.name in defined_functions:
                duplicates.append(('function', node.name, defined_functions[node.name], node.lineno))
            else:
                defined_functions[node.name] = node.lineno
            defined_names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            if node.name in defined_classes:
                duplicates.append(('class', node.name, defined_classes[node.name], node.lineno))
            else:
                defined_classes[node.name] = node.lineno
            defined_names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_names.add(target.id)
        elif isinstance(node, ast.AnnAssign):  # Handle type-annotated assignments like `x: int = 5`
            if isinstance(node.target, ast.Name):
                defined_names.add(node.target.id)

    # For undefined detection, only check function calls at module level
    # (i.e., calls to functions that don't exist)
    undefined = {}

    def find_undefined_calls(node, defined_names):
        """Find calls to undefined functions within a node."""
        undefined_calls = {}

        for child in ast.walk(node):
            # Look for function calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                    if func_name not in defined_names and not is_builtin(func_name):
                        if func_name not in undefined_calls:
                            undefined_calls[func_name] = []
                        undefined_calls[func_name].append(child.lineno)

        return undefined_calls

    # Check module-level code for undefined calls
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            calls = find_undefined_calls(node, defined_names)
            for name, lines in calls.items():
                if name not in undefined:
                    undefined[name] = []
                undefined[name].extend(lines)

    return {
        'defined_functions': defined_functions,
        'defined_classes': defined_classes,
        'duplicates': duplicates,
        'undefined': undefined,
        'source': source
    }


def check_specific_issues(source):
    """Check for specific migration issues in the source code."""
    issues = []
    lines = source.split('\n')

    # Check for duplicate logger definitions
    logger_lines = [i + 1 for i, line in enumerate(lines) if 'logger = logging.get_logger' in line]
    if len(logger_lines) > 1:
        issues.append({
            'type': 'duplicate_logger',
            'message': f'Found {len(logger_lines)} logger definitions at lines: {logger_lines}',
            'lines': logger_lines
        })

    # Check for torch references in code (not comments)
    torch_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
            if 'import torch' in line or 'from torch' in line:
                torch_lines.append(i + 1)
    if torch_lines:
        issues.append({
            'type': 'torch_imports',
            'message': f'Found torch imports at lines: {torch_lines}',
            'lines': torch_lines
        })

    # Check for tracing/dynamo code that should be deleted
    if 'is_tracing(' in source:
        issues.append({
            'type': 'should_delete',
            'message': 'is_tracing() calls should be removed (not defined). MindSpore does not use tracing.',
            'lines': []
        })

    if 'is_flash_attention_requested(' in source and 'def is_flash_attention_requested(' not in source:
        issues.append({
            'type': 'missing_function',
            'message': 'is_flash_attention_requested() is called but not defined',
            'lines': []
        })

    # Check for PyTorch version constants that should be deleted
    if '_is_torch_xpu_available = ' in source:
        issues.append({
            'type': 'should_delete',
            'message': '_is_torch_xpu_available should be deleted (not needed in MindSpore)',
            'lines': []
        })

    if '_is_torch_greater_or_equal_than_2_6 = ' in source:
        issues.append({
            'type': 'should_delete',
            'message': '_is_torch_greater_or_equal_than_2_6 should be deleted (not needed in MindSpore)',
            'lines': []
        })

    return issues


def print_results(filepath, results, issues):
    """Print verification results."""
    print(f"\n{'='*60}")
    print(f"Verification Report: {filepath}")
    print(f"{'='*60}")

    # Summary
    print(f"\n[Summary]")
    print(f"   Functions defined: {len(results['defined_functions'])}")
    print(f"   Classes defined: {len(results['defined_classes'])}")

    # Duplicates
    if results['duplicates']:
        print(f"\n[WARNING] Duplicate Definitions Found:")
        for dup_type, name, first_line, dup_line in results['duplicates']:
            print(f"   {dup_type.capitalize()} '{name}' defined at line {first_line} and line {dup_line}")
    else:
        print(f"\n[OK] No duplicate definitions found")

    # Undefined references
    if results['undefined']:
        print(f"\n[ERROR] Undefined References:")
        for name, lines in sorted(results['undefined'].items()):
            print(f"   '{name}' referenced at lines: {lines}")
    else:
        print(f"\n[OK] No undefined references found")

    # Specific issues
    if issues:
        print(f"\n[INFO] Specific Issues Found:")
        for issue in issues:
            print(f"   {issue['type']}: {issue['message']}")
    else:
        print(f"\n[OK] No specific issues found")

    print(f"\n{'='*60}")

    # Return success/failure
    return len(results['duplicates']) == 0 and len(results['undefined']) == 0 and len(issues) == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_migration.py <filepath>")
        print("\nThis script verifies a migrated MindSpore transformers file for:")
        print("  - Duplicate function/class/variable definitions")
        print("  - Undefined variable/function references")
        print("  - Common migration issues (duplicate logger, torch imports, missing functions)")
        sys.exit(1)

    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    try:
        results = analyze_file(filepath)
        issues = check_specific_issues(results['source'])
        success = print_results(filepath, results, issues)

        sys.exit(0 if success else 1)
    except SyntaxError as e:
        print(f"[ERROR] Syntax Error in file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error analyzing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
