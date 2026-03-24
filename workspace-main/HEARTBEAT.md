# Heartbeat: 大副

> These writes happen BEFORE announcing anything to Captain.
> Never skip. They make recovery possible after any interruption.

---

## After Receiving Captain Input

1. Determine intent (new task / follow-up / switch / end / report)
2. Resolve all `fleet/...` paths against the OpenClaw config root, not `workspace-main/`
3. If new task → run `taskbus.py create` BEFORE spawning Pilot
4. Verify formal task records exist:
   - `fleet/registry/tasks.json`
   - `fleet/tasks/<TASK_ID>/TASK.md`
   - `fleet/registry/active.md`
5. If state change → run `taskbus.py update` BEFORE responding

If step 3 or 4 fails, stop and tell Captain the task was not formally registered.

## After Dispatching a Pilot

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state RUNNING \
    --session-id <spawned-session-id> \
    --next "Pilot is executing"
```

## After Receiving a Pilot Report

If the report implies a natural next phase and the following are all true:

- goal is still clear
- scope is still clear
- no high-risk or critical ambiguity appeared

then continue the task immediately. Update state and next action, and keep the task moving.
Do NOT convert normal continuation into a Captain confirmation step.

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state <NEW_STATE> \
    --next "<next action>" \
    [--waiting | --no-waiting]
```

Then synthesize for Captain.

Use `--waiting` only when Captain input is actually required.

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
> The first Write is also not optional: no Task Card, no execution.
