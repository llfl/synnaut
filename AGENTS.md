# Synnaut — Liquid Fleet 3.0

> Multi-Agent orchestration system built on OpenClaw.
> Architecture: bounded recursion + parallel task pool + file-based state machine.

## Project Structure

```
synnaut/
├── README.md                        # Public-facing architecture and design guide
├── README.cn.md                     # Chinese public-facing architecture and design guide
├── openclaw.json                    # OpenClaw gateway configuration
├── install.py                       # Fleet installer script
├── workspace-main/                  # 大副 / Chief Mate — permanent orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-general/         # 通用领航员 / General Pilot — flexible task orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-research/        # 研究领航员 / Research Pilot — intelligence orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-build/           # 构建领航员 / Build Pilot — implementation orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-worker-drive/          # 水手·轮机手 / Sailor·Engineer — implement, code, deliver
│   └── AGENTS.md                    #   system prompt & constraints
├── workspace-worker-guard/          # 水手·机械师 / Sailor·Mechanic — test, review, validate
│   └── AGENTS.md                    #   system prompt & constraints
├── workspace-worker-sense/          # 水手·瞭望手 / Sailor·Lookout — search, analyze, judge
│   └── AGENTS.md                    #   system prompt & constraints
└── fleet/                           # Runtime state & memory (file-based)
    ├── bin/
    │   ├── taskbus.py               #   Task Bus CLI — task state management
    │   └── dashboard.py             #   Terminal dashboard — read-only fleet status view
    ├── registry/
    │   ├── tasks.json               #   global task index (machine-readable)
    │   └── active.md                #   active task summary (human-readable)
    ├── memory/
    │   ├── captain-preferences.md   #   Captain style & preferences
    │   ├── role-names.md            #   canonical role name reference (Chinese ↔ English)
    │   ├── synergy-patterns.md      #   领航员/Pilot + 水手/Sailor collaboration effectiveness
    │   └── recruiting-rules.md      #   领航员/Pilot selection & 水手/Sailor dispatch rules
    └── tasks/
        └── .template/               #   task file templates
            ├── TASK.md              #     goal, scope, deadline, sailor policy, captain style
            ├── PLAN.md              #     decomposition & sailor dispatch plan
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
大副 / Chief Mate (main)       ← permanent, sole entry point
    │
    ├── taskbus.py             ← task state management (create/list/switch/update/archive)
    │
    ├── 通用领航员 / General Pilot   ×N    ← depth-1, task-scoped, parallel
    ├── 研究领航员 / Research Pilot  ×N    ← depth-1, research-specialized
    └── 构建领航员 / Build Pilot     ×N    ← depth-1, implementation-specialized
         │
         ├── worker-drive (轮机手 / Engineer)     ← depth-2, leaf, allowAgents: []
         ├── worker-guard (机械师 / Mechanic)    ← depth-2, leaf, allowAgents: []
         └── worker-sense (瞭望手 / Lookout)     ← depth-2, leaf, allowAgents: []
```

## Agent Inventory

| Agent ID | Role | Depth | Spawns? | Key Tools |
|----------|------|-------|---------|-----------|
| main | 大副 / Chief Mate | 0 | yes (领航员/Pilots, max 3) | sessions_spawn, sessions_send, read, write, web_search, exec |
| pilot-general | 通用领航员 / General Pilot | 1 | yes (水手/Sailors, max 2) | sessions_spawn, read, write, web_search, exec |
| pilot-research | 研究领航员 / Research Pilot | 1 | yes (水手/Sailors, max 2) | sessions_spawn, read, write, web_search, web_fetch |
| pilot-build | 构建领航员 / Build Pilot | 1 | yes (水手/Sailors, max 2) | sessions_spawn, read, write, exec |
| worker-drive | 轮机手 / Engineer | 2 | no | read, write, exec |
| worker-guard | 机械师 / Mechanic | 2 | no | read, exec |
| worker-sense | 瞭望手 / Lookout | 2 | no | read, write, web_search, web_fetch |

## Key Design Decisions

- **Bounded recursion**: `allowAgents` enforces spawn topology (who can spawn whom); sailors have `allowAgents: []`
- **File-based state**: task state lives in files, managed by Task Bus CLI
- **Canonical runtime root**: `fleet/` and all `workspace-*` directories are siblings under the OpenClaw config directory that contains `openclaw.json`
- **Parallel task pool**: up to 3 领航员 / Pilots concurrent
- **Explicit Task Cards**: 领航员 / Pilots receive full context, no implicit inheritance
- **Dual switching**: thread-binding (mode A) or soft-switch (mode B)
- **Task Bus**: `fleet/bin/taskbus.py` enforces state machine transitions

## Runtime Root Contract

All relative paths in fleet prompts and docs are resolved from the OpenClaw config root:

```text
<OPENCLAW_HOME>/
  openclaw.json
  fleet/
  workspace-main/
  ...
```

`fleet/` is shared runtime state at the OpenClaw root. It is not workspace-local state.

## Task State Machine

`NEW` → `RUNNING` → `WAITING_USER` / `BLOCKED` / `SYNTHESIZING` → `DONE` / `FAILED` → `ARCHIVED`

Only 大副 / Chief Mate changes primary state via Task Bus. 领航员 / Pilots suggest, 大副 / Chief Mate decides.

## Concurrency Limits

| Parameter | Value | Enforcement |
|-----------|-------|-------------|
| Max active 领航员 / Pilots | 3 | prompt-enforced (OpenClaw has no per-agent spawn count) |
| Max 水手 / Sailors per 领航员 / Pilot | 2 | prompt-enforced (OpenClaw has no per-agent spawn count) |
| Max total sessions | 10 | prompt-enforced |
| 水手 / Sailor timeout | 900s | config: `agents.defaults.subagents.runTimeoutSeconds` |
| Session archive | 120min | config: `agents.defaults.subagents.archiveAfterMinutes` |
