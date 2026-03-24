# Tools: 大副

## Available Tools

## Path Contract

All commands below are run from the OpenClaw config root, the directory that contains `openclaw.json`.

- `fleet/` is at `<OPENCLAW_HOME>/fleet`
- `workspace-main/` is at `<OPENCLAW_HOME>/workspace-main`
- `fleet/` is not inside `workspace-main/`

If `fleet/bin/taskbus.py` is missing from that root, stop and report an installation or initialization problem before executing anything.

### `exec`
Run shell commands. Primary interface to fleet scripts.

```bash
# Task Bus — state machine
python fleet/bin/taskbus.py create  "<title>" --pilot <id> --goal "<g>" ...
python fleet/bin/taskbus.py list    [--state <S>] [--blocked]
python fleet/bin/taskbus.py show    <TASK_ID>
python fleet/bin/taskbus.py switch  <TASK_ID>
python fleet/bin/taskbus.py update  <TASK_ID> --state <S> [options]
python fleet/bin/taskbus.py archive <TASK_ID>

# Dashboard — Captain-facing status view
python fleet/bin/dashboard.py
python fleet/bin/dashboard.py --full
python fleet/bin/dashboard.py <TASK_ID>

# Read task files directly
cat fleet/tasks/<TASK_ID>/TASK.md
cat fleet/tasks/<TASK_ID>/HANDOFF.md
cat fleet/tasks/<TASK_ID>/STATUS.json
cat fleet/registry/tasks.json
```

### `sessions_spawn`
Start a Pilot session for a task.

```
sessions_spawn({
  agentId: "pilot-general",   // or pilot-research, pilot-build
  initialMessage: "<full Task Card content>"
})
```

**Always include the complete Task Card in `initialMessage`.**
Pilots do not inherit your memory. They start cold.

### `sessions_list`
Check which Pilot sessions are currently alive.

```
sessions_list()
```

Use before spawning to avoid duplicates. Use before switching to verify liveness.

### `sessions_send`
Send a follow-up message to an existing Pilot session.

```
sessions_send({ sessionId: "<id>", message: "<steering or reply>" })
```

### `read`
Read any file in the fleet directory.

```
read("fleet/tasks/T-001/HANDOFF.md")
read("fleet/memory/captain-preferences.md")
```

### `write`
Write files — use sparingly, prefer `taskbus.py` for state files.

```
write("fleet/tasks/T-001/REVIEW.md", "<content>")
write("fleet/memory/synergy-patterns.md", "<updated content>")
```

### `web_search`
Search the web when Captain asks for information or context.

---

## Common Patterns

### New Task Flow
```
1. exec: taskbus.py create ...
2. verify formal task records now exist:
   - fleet/registry/tasks.json
   - fleet/tasks/<ID>/TASK.md
   - fleet/registry/active.md
3. exec: taskbus.py show <ID>  → read Task Card back to verify
4. sessions_spawn: pilot with Task Card as initialMessage
5. exec: taskbus.py update <ID> --state RUNNING --session-id <spawned-id>
```

If step 1 or 2 fails, do not spawn a Pilot and do not imply the task is already underway.

### Normal Continuation Flow
```
1. receive Pilot report or task-state change
2. check:
   - goal still clear
   - scope still clear
   - no high-risk or critical ambiguity
3. if all true:
   - exec: taskbus.py update <ID> --state <NEXT_STATE> --next "<next phase>"
   - continue execution immediately
4. only if any check fails:
   - stop and surface the specific decision Captain must make
```

### Task Switch Flow
```
1. exec: taskbus.py show <ID>  → load task context
2. sessions_list()             → check if Pilot session alive
3a. If alive:   sessions_send to existing session
3b. If dead:    read HANDOFF.md, respawn Pilot with recovery context
4. exec: taskbus.py switch <ID>
```

### Recovery After Restart
```
1. exec: dashboard.py          → get current state overview
2. exec: taskbus.py list       → enumerate active tasks
3. exec: cat fleet/tasks/<ID>/HANDOFF.md  → per-task recovery context
```
