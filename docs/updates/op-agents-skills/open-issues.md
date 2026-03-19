# op-agent Open Issues

## 1. Next-step output should eventually support exact builder invocation commands

### Issue

`op-agent` currently ends with a short next-step action, but it does not
guarantee an exact CLI invocation command for the selected builder.

### Current decision

Do not hardcode a builder invocation command in `skills/op-agent/SKILL.md` yet.

Current output should stay at the level of:

- which builder is the best fit
- why that builder fits
- what the next action is

### Why this is deferred

The current repository does not yet define a single, stable builder invocation
command format such as:

- `/build cpu-native`
- `ms-cli build cpu-native`
- another canonical builder entry command

The `commands/` directory describes command-facing builder entries, but it does
not yet freeze one exact invocation syntax that `op-agent` can safely emit as a
hard requirement.

### Future closure condition

When the project freezes a canonical builder invocation format in `ms-cli` or
an equivalent command contract, update `skills/op-agent/SKILL.md` so the final
recommendation includes the exact next-step command instead of only a next-step
action.
