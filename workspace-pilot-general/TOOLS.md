# Tools: 通用领航员

## Available Tools

### `exec` — run fleet scripts and shell commands

```bash
# Read task state
python fleet/bin/taskbus.py show    <TASK_ID>
python fleet/bin/taskbus.py update  <TASK_ID> --state <S> --next "<action>"

# Read task files
cat fleet/tasks/<TASK_ID>/TASK.md
cat fleet/tasks/<TASK_ID>/HANDOFF.md
cat fleet/tasks/<TASK_ID>/PLAN.md
cat fleet/memory/recruiting-rules.md
```

### `sessions_spawn` — dispatch a Sailor

```
sessions_spawn({
  agentId: "worker-drive",
  initialMessage: "OBJECTIVE: <single clear goal>\nCONTEXT: <all relevant info>\nSCOPE: <what NOT to do>\nOUTPUT FORMAT: Goal/Findings/Risks/Decision/Next Step"
})
```

Valid agentIds: `worker-drive`, `worker-guard`, `worker-sense`
Max concurrent: 2

### `read` — read any file

```
read("fleet/tasks/T-001/TASK.md")
read("fleet/memory/recruiting-rules.md")
```

### `write` — write task files

```
write("fleet/tasks/T-001/PLAN.md", "<content>")
write("fleet/tasks/T-001/HANDOFF.md", "<content>")
write("fleet/tasks/T-001/DECISIONS.md", "<content>")
write("fleet/tasks/T-001/CONTEXT.md", "<content>")
```

### `web_search` — search for information

Use when the task requires current information unavailable in context.

### `exec` (general purpose)

Can run any shell command in the working environment.
Use for: file inspection, running checks, running tests.

---

## Sailor Dispatch Reference

| Task Type              | Primary Sailor   | Secondary Sailor |
|------------------------|-----------------|-----------------|
| Implementation / code  | worker-drive    | worker-guard    |
| Research / analysis    | worker-sense    | —               |
| Testing / validation   | worker-guard    | —               |
| Mixed implementation   | worker-drive    | worker-guard    |

See `fleet/memory/recruiting-rules.md` for full dispatch rules.

---

## Common Patterns

### Decompose and Dispatch

```
1. write PLAN.md with decomposition
2. sessions_spawn worker-drive with objective A
3. sessions_spawn worker-guard with objective B  (if needed)
4. wait for results
5. write CONTEXT.md with collected results
6. write HANDOFF.md with synthesis
7. taskbus.py update --state SYNTHESIZING
```

### Blocked on External Dependency

```
1. taskbus.py update <ID> --state BLOCKED --blocker "<reason>"
2. write HANDOFF.md with exact blocker and what would unblock it
3. Report to 大副: state + blocker + suggested unblock
```
