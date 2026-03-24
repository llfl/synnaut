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
├── workspace-main/                  # 王熙凤 / Wang Xifeng — permanent orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-general/         # 贾宝玉 / Jia Baoyu — flexible task orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-research/        # 林黛玉 / Lin Daiyu — intelligence orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-pilot-build/           # 贾探春 / Jia Tanchun — implementation orchestrator
│   └── AGENTS.md                    #   system prompt & protocols
├── workspace-worker-drive/          # 执行代理·晴雯 / Execution Agent·Qingwen — implement, code, deliver
│   └── AGENTS.md                    #   system prompt & constraints
├── workspace-worker-guard/          # 执行代理·袭人 / Execution Agent·Xiren — test, review, validate
│   └── AGENTS.md                    #   system prompt & constraints
├── workspace-worker-sense/          # 执行代理·小红 / Execution Agent·Xiaohong — search, analyze, judge
│   └── AGENTS.md                    #   system prompt & constraints
└── fleet/                           # Runtime state & memory (file-based)
    ├── bin/
    │   ├── taskbus.py               #   Task Bus CLI — task state management
    │   └── dashboard.py             #   Terminal dashboard — read-only fleet status view
    ├── registry/
    │   ├── tasks.json               #   global task index (machine-readable)
    │   └── active.md                #   active task summary (human-readable)
    ├── memory/
    │   ├── jiamu-preferences.md    #   Jia Mu style & preferences
    │   ├── role-names.md            #   canonical role name reference (Chinese ↔ English)
    │   ├── synergy-patterns.md      #   编排代理/orchestration agent + 执行代理/execution agent collaboration effectiveness
    │   └── recruiting-rules.md      #   编排代理/orchestration agent selection & 执行代理/execution agent dispatch rules
    └── tasks/
        └── .template/               #   task file templates
            ├── TASK.md              #     goal, scope, deadline, execution agent policy, Jia Mu style
            ├── PLAN.md              #     decomposition & execution agent dispatch plan
            ├── CONTEXT.md           #     accumulated context
            ├── DECISIONS.md         #     key decisions log
            ├── STATUS.json          #     machine-readable state + session/thread metadata
            ├── HANDOFF.md           #     recovery snapshot for task switching
            └── REVIEW.md            #     post-completion review + experience events
```

## Architecture

```
Jia Mu / 贾母 (Human)
    │
    ▼
王熙凤 / Wang Xifeng (main)       ← permanent, sole entry point
    │
    ├── taskbus.py             ← task state management (create/list/switch/update/archive)
    │
    ├── 贾宝玉 / Jia Baoyu   ×N    ← depth-1, task-scoped, parallel
    ├── 林黛玉 / Lin Daiyu  ×N    ← depth-1, research-specialized
    └── 贾探春 / Jia Tanchun     ×N    ← depth-1, implementation-specialized
         │
         ├── worker-drive (晴雯 / Qingwen)     ← depth-2, leaf, allowAgents: []
         ├── worker-guard (袭人 / Xiren)    ← depth-2, leaf, allowAgents: []
         └── worker-sense (小红 / Xiaohong)     ← depth-2, leaf, allowAgents: []
```

## Agent Inventory

| Agent ID | Role | Depth | Spawns? | Key Tools |
|----------|------|-------|---------|-----------|
| main | 王熙凤 / Wang Xifeng | 0 | yes (编排代理/orchestration agents, max 3) | sessions_spawn, sessions_send, read, write, web_search, exec |
| pilot-general | 贾宝玉 / Jia Baoyu | 1 | yes (执行代理/execution agents, max 2) | sessions_spawn, read, write, web_search, exec |
| pilot-research | 林黛玉 / Lin Daiyu | 1 | yes (执行代理/execution agents, max 2) | sessions_spawn, read, write, web_search, web_fetch |
| pilot-build | 贾探春 / Jia Tanchun | 1 | yes (执行代理/execution agents, max 2) | sessions_spawn, read, write, exec |
| worker-drive | 晴雯 / Qingwen | 2 | no | read, write, exec |
| worker-guard | 袭人 / Xiren | 2 | no | read, exec |
| worker-sense | 小红 / Xiaohong | 2 | no | read, write, web_search, web_fetch |

## Key Design Decisions

- **Bounded recursion**: `allowAgents` enforces spawn topology (who can spawn whom); execution agents have `allowAgents: []`
- **File-based state**: task state lives in files, managed by Task Bus CLI
- **Canonical runtime root**: `fleet/` and all `workspace-*` directories are siblings under the OpenClaw config directory that contains `openclaw.json`
- **Parallel task pool**: up to 3 编排代理 / orchestration agents concurrent
- **Explicit Task Cards**: 编排代理 / orchestration agents receive full context, no implicit inheritance
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

Only 王熙凤 / Wang Xifeng changes primary state via Task Bus. 编排代理 / orchestration agents suggest, 王熙凤 / Wang Xifeng decides.

## Concurrency Limits

| Parameter | Value | Enforcement |
|-----------|-------|-------------|
| Max active 编排代理 / orchestration agents | 3 | prompt-enforced (OpenClaw has no per-agent spawn count) |
| Max 执行代理 / execution agents per 编排代理 / orchestration agent | 2 | prompt-enforced (OpenClaw has no per-agent spawn count) |
| Max total sessions | 10 | prompt-enforced |
| 执行代理 / execution agent timeout | 900s | config: `agents.defaults.subagents.runTimeoutSeconds` |
| Session archive | 120min | config: `agents.defaults.subagents.archiveAfterMinutes` |
