# Closure Checklist

Do not declare the upgrade complete until the following are handled:

- new upstream-adapted files use the local provenance and license header style
- intentionally empty files remain empty
- `mindone.transformers.__version__` is updated to the target version and the
  local `__version__` declaration matches the completed upgrade
- final completion summary is written
- remaining gaps are classified as:
  - completed
  - deferred review
  - explicitly ignored
- one target-version-added model has been used as a migration proof step
