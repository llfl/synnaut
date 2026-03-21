# Tools: 构建领航员

## Available Tools

### `exec` — run scripts and build tools

```bash
# Fleet state
python fleet/bin/taskbus.py show    <TASK_ID>
python fleet/bin/taskbus.py update  <TASK_ID> --state <S> --next "<action>"
cat fleet/tasks/<TASK_ID>/TASK.md

# Build / test commands (task-specific)
# Use exec to run whatever the project requires
```

### `sessions_spawn` — dispatch Sailors

```
# Primary: implementation
sessions_spawn({
  agentId: "worker-drive",
  initialMessage: "OBJECTIVE: <specific implementation goal>\nFILES TO MODIFY: <list>\nCONSTRAINTS: <what NOT to touch>\nACCEPTANCE CRITERIA: <what done looks like>\nOUTPUT FORMAT: Goal/Findings/Risks/Decision/Next Step"
})

# Quality gate: test and validate
sessions_spawn({
  agentId: "worker-guard",
  initialMessage: "VALIDATE: <what to test/review>\nCRITERIA: <acceptance criteria>\nSCOPE: read-only review, do not modify code\nOUTPUT FORMAT: Goal/Findings/Risks/Decision/Next Step"
})
```

Max concurrent: 2. Never spawn `worker-sense` as primary — use it only if research is unexpectedly needed.

### `read` / `write` — task and project files

```
read("fleet/tasks/<ID>/TASK.md")
write("fleet/tasks/<ID>/PLAN.md", "<architecture + implementation plan>")
write("fleet/tasks/<ID>/CONTEXT.md", "<build progress, decisions>")
write("fleet/tasks/<ID>/DECISIONS.md", "<technical decisions>")
write("fleet/tasks/<ID>/HANDOFF.md", "<recovery snapshot>")
```

---

## Build Quality Gate Protocol

Every significant implementation MUST go through a quality gate:

```
1. worker-drive implements
2. worker-drive reports: files changed, approach taken
3. IMMEDIATELY spawn worker-guard with: "Review the following changes for correctness..."
4. worker-guard reports: pass / fail + findings
5. If fail → worker-drive iterates
6. If pass → report to 大副 as DONE
```

Do NOT report build completion without at least one guard pass.

---

## Common Patterns

### Standard Build Flow

```
1. Write PLAN.md: architecture + breakdown
2. taskbus.py update --state RUNNING --next "Implementation phase 1"
3. dispatch worker-drive: implement phase 1
4. dispatch worker-guard: review phase 1
5. Iterate if needed
6. write CONTEXT.md: what was built, what changed
7. taskbus.py update --state SYNTHESIZING
8. Report to 大副 with deliverables
```
