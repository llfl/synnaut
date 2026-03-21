# Heartbeat: 大副

> These writes happen BEFORE announcing anything to Captain.
> Never skip. They make recovery possible after any interruption.

---

## After Receiving Captain Input

1. Determine intent (new task / follow-up / switch / end / report)
2. If new task → run `taskbus.py create` BEFORE spawning Pilot
3. If state change → run `taskbus.py update` BEFORE responding

## After Dispatching a Pilot

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state RUNNING \
    --session-id <spawned-session-id> \
    --next "Pilot is executing"
```

## After Receiving a Pilot Report

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state <NEW_STATE> \
    --next "<next action>" \
    [--waiting | --no-waiting]
```

Then synthesize for Captain.

## After Task Completion

```bash
python fleet/bin/taskbus.py update <TASK_ID> --state DONE
# Write review
# Then archive when Captain confirms:
python fleet/bin/taskbus.py archive <TASK_ID>
```

## On Session End (or Before Switching Context)

Ensure `fleet/registry/active.md` reflects current state:

```bash
python fleet/bin/taskbus.py list
```

Review output. If any task has stale state, correct it now.

---

> Rhythm: Receive → Write → Act → Write → Report
> The second Write is not optional.
