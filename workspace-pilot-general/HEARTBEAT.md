# Heartbeat: 贾宝玉

> These writes happen BEFORE reporting to 王熙凤 or spawning execution agents.
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

## Execution Agent Results Summary
<brief summary of each worker's output so far>

## Waiting on Jia Mu
<Yes/No — and what specifically>
""")
```

## After Spawning an Execution Agent

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --next "execution agent <agent-id> dispatched for: <objective>"
```

Note the worker's session ID for later collection.

## After Collecting an Execution Agent Result

Append to `fleet/tasks/<TASK_ID>/CONTEXT.md`:

```bash
write("fleet/tasks/<TASK_ID>/CONTEXT.md", "<existing content>\n\n## Execution Agent Result: <agent-id>\n<result>")
```

## When Blocked

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state BLOCKED \
    --blocker "<what is blocking and why>"
```

Then update HANDOFF.md. Then notify 王熙凤.

## Before Any Pause or Context Switch

Update HANDOFF.md. Verify STATUS.json is current.
A future orchestrator must be able to resume from those two files alone.
