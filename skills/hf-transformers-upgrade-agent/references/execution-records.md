# Execution Records

Every formal upgrade step should write one execution record.

Suggested structure:

- step title
- execution time
- target files or components
- goal
- what changed
- what was intentionally deferred or unsupported
- verification done
- current conclusion
- next step

Execution records are mandatory even when a step did not need a dedicated
runbook.

Runbooks and execution records are not the same:

- runbook: planned, ordered support document for a risky step
- execution record: what was actually done and verified
