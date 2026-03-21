# Synnaut — Liquid Fleet 3.0

> Multi-Agent orchestration system built on OpenClaw.
> Architecture: bounded recursion + parallel task pool + file-based state machine.

## Project Structure

```
synnaut/
├── openclaw.json                    # OpenClaw gateway configuration
├── install.py                       # Fleet installer script
├── workspace-main/                  # Chief Mate (大副) — permanent orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-general/         # General Pilot (通用领航员) — flexible task orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-research/        # Research Pilot (研究领航员) — intelligence orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-build/           # Build Pilot (构建领航员) — implementation orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-worker-drive/          # Worker #动力与开拓 — implement, code, deliver
│   └── AGENTS.md                    #   system prompt & constraints
├── workspace-worker-guard/          # Worker #结构与风控 — test, review, validate
│   └── AGENTS.md                    #   system prompt & constraints
├── workspace-worker-sense/          # Worker #感知与策略 — search, analyze, judge
│   └── AGENTS.md                    #   system prompt & constraints
└── fleet/                           # Runtime state & memory (file-based)
    ├── bin/
    │   └── taskbus.py               #   Task Bus CLI — task state management
    ├── registry/
    │   ├── tasks.json               #   global task index (machine-readable)
    │   └── active.md                #   active task summary (human-readable)
    ├── memory/
    │   ├── captain-preferences.md   #   Captain style & preferences
    │   ├── synergy-patterns.md      #   Pilot+Worker combo effectiveness
    │   └── recruiting-rules.md      #   Pilot selection & Worker dispatch rules
    └── tasks/
        └── .template/               #   task file templates
            ├── TASK.md              #     goal, scope, deadline, worker policy, captain style
            ├── PLAN.md              #     decomposition & worker dispatch plan
            ├── CONTEXT.md           #     accumulated context
            ├── DECISIONS.md         #     key decisions log
            ├── STATUS.json          #     machine-readable state + session/thread metadata
            ├── HANDOFF.md           #     recovery snapshot for task switching
            └── REVIEW.md            #     post-completion review + experience events
```

## Architecture

```
Captain (Human)
    │
    ▼
Chief Mate (main)              ← permanent, sole entry point
    │
    ├── taskbus.py             ← task state management (create/list/switch/update/archive)
    │
    ├── Pilot General    ×N    ← depth-1, task-scoped, parallel
    ├── Pilot Research   ×N    ← depth-1, research-specialized
    └── Pilot Build      ×N    ← depth-1, implementation-specialized
         │
         ├── worker-drive (动力与开拓)  ← depth-2, leaf, maxSpawnDepth=0
         ├── worker-guard (结构与风控)  ← depth-2, leaf, maxSpawnDepth=0
         └── worker-sense (感知与策略)  ← depth-2, leaf, maxSpawnDepth=0
```

## Agent Inventory

| Agent ID | Role | Depth | Spawns? | Key Tools |
|----------|------|-------|---------|-----------|
| main | Chief Mate | 0 | yes (pilots) | sessions_*, exec, file_* |
| pilot-general | General Pilot | 1 | yes (workers) | sessions_spawn, exec, file_* |
| pilot-research | Research Pilot | 1 | yes (workers) | sessions_spawn, web_*, file_* |
| pilot-build | Build Pilot | 1 | yes (workers) | sessions_spawn, exec, code_interpret |
| worker-drive | #动力与开拓 | 2 | no | exec, file_*, code_interpret |
| worker-guard | #结构与风控 | 2 | no | exec (read/test), file_read |
| worker-sense | #感知与策略 | 2 | no | web_*, file_* |

## Key Design Decisions

- **Bounded recursion**: maxSpawnDepth=2, workers cannot spawn further
- **File-based state**: task state lives in files, managed by Task Bus CLI
- **Parallel task pool**: up to 3 Pilots concurrent (MVP)
- **Explicit Task Cards**: Pilots receive full context, no implicit inheritance
- **Dual switching**: thread-binding (mode A) or soft-switch (mode B)
- **Task Bus**: `fleet/bin/taskbus.py` enforces state machine transitions

## Task State Machine

`NEW` → `RUNNING` → `WAITING_USER` / `BLOCKED` / `SYNTHESIZING` → `DONE` / `FAILED` → `ARCHIVED`

Only Chief Mate changes primary state via Task Bus. Pilots suggest, Chief Mate decides.

## MVP Limits

| Parameter | Value |
|-----------|-------|
| Max active Pilots | 3 |
| Max Workers per Pilot | 2 |
| Max total sessions | 10 |
| Worker timeout | 900s |
| Session archive | 120min |
