# Heartbeat: Pilot

> These writes happen BEFORE reporting to 大副 or spawning Sailors.
> Every. Single. Time. No exceptions.

---

## After Each Phase Completion

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state <STATE> \
    --goal  "<current sub-goal>" \
    --next  "<next action>"
```

Then update HANDOFF.md manually:

```bash
write("fleet/tasks/<TASK_ID>/HANDOFF.md", """
# Handoff: <TASK_ID>

## Current Goal
<what are we trying to achieve right now>

## Latest Conclusion
<what was the last significant finding or output>

## Current Blockers
<anything preventing progress, or "none">

## Next Action
<exactly what happens next>

## Sailor Results Summary
<brief summary of each worker's output so far>

## Waiting on Captain
<Yes/No — and what specifically>
""")
```

## After Spawning a Sailor

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --next "Sailor <agent-id> dispatched for: <objective>"
```

Note the worker's session ID for later collection.

## After Collecting a Sailor Result

Append to `fleet/tasks/<TASK_ID>/CONTEXT.md`:

```bash
write("fleet/tasks/<TASK_ID>/CONTEXT.md", "<existing content>\n\n## Sailor Result: <agent-id>\n<result>")
```

## When Blocked

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state BLOCKED \
    --blocker "<what is blocking and why>"
```

Then update HANDOFF.md. Then notify 大副.

## Before Any Pause or Context Switch

Update HANDOFF.md. Verify STATUS.json is current.
A future Pilot must be able to resume from those two files alone.
