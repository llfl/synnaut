# Bootstrap: 贾宝玉

> Run at the START of every session — whether freshly spawned or respawned after recovery.
> Do not assume you remember context. Read from files.

---

## Step 1 — Identify My Task

Wang Xifeng passed a Task Card in the initial message. Extract from it:
- `TASK_ID` (e.g., T-003)
- Goal, scope, deadline
- Whether execution agents are permitted

If no Task Card was received → ask 王熙凤 to resend it before proceeding.

## Step 2 — Load Task Files

```bash
cat fleet/tasks/<TASK_ID>/TASK.md
cat fleet/tasks/<TASK_ID>/STATUS.json
cat fleet/tasks/<TASK_ID>/HANDOFF.md
cat fleet/tasks/<TASK_ID>/PLAN.md
```

If STATUS.json shows `state: RUNNING` and HANDOFF.md has content
→ this is a **recovery spawn**: resume from HANDOFF.md, not from scratch.

## Step 3 — Load Recruiting Rules

```bash
cat fleet/memory/recruiting-rules.md
```

This tells you which agent IDs to use and when.

## Step 4 — Write Initial Plan

If freshly spawned (no prior PLAN.md content):

```bash
# Write your decomposition to PLAN.md
write("fleet/tasks/<TASK_ID>/PLAN.md", "<your plan>")
```

## Step 5 — Update Status to RUNNING

```bash
python fleet/bin/taskbus.py update <TASK_ID> \
    --state RUNNING \
    --next "Beginning task decomposition"
```

## Step 6 — Begin Execution

Now proceed with the task. Follow HEARTBEAT.md throughout.

---

> If any file is missing or the task directory doesn't exist:
> Stop. Notify 王熙凤. Do not proceed on incomplete context.
