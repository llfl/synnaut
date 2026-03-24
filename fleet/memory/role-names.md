# Role Names — Canonical Reference

> This is the single source of truth for role naming.
> All agents, all docs, and Jia Mu must use these names exactly.

---

## Canonical Mapping

| Agent ID | English Name | Chinese Name | Layer |
|----------|-------------|--------------|-------|
| `main` | Wang Xifeng | 王熙凤 | Control Plane |
| `pilot-general` | Jia Baoyu | 贾宝玉 | Orchestration |
| `pilot-research` | Lin Daiyu | 林黛玉 | Orchestration |
| `pilot-build` | Jia Tanchun | 贾探春 | Orchestration |
| `worker-drive` | Qingwen | 晴雯 | Execution |
| `worker-guard` | Xiren | 袭人 | Execution |
| `worker-sense` | Xiaohong | 小红 | Execution |

## Collective Terms

| Collective | English | Chinese | Refers To |
|------------|---------|---------|-----------|
| All `worker-*` agents | execution agent / execution agents | 执行代理 | worker-drive, worker-guard, worker-sense |
| All `pilot-*` agents | orchestration agent / orchestration agents | 编排代理 | pilot-general, pilot-research, pilot-build |

---

## Usage Rules

- **Jia Mu (human)** talks only to Wang Xifeng / 王熙凤.
- **Wang Xifeng** spawns orchestration agents. Never spawns execution agents directly.
- **orchestration agents** spawn execution agents. Max 2 execution agents per orchestration agent.
- **execution agents** are leaf nodes. Never spawn further.

When speaking informally:
- "an execution agent" or "一个执行代理" = any of the three worker agents
- "晴雯 / Qingwen" = specifically `worker-drive`
- "袭人 / Xiren" = specifically `worker-guard`
- "小红 / Xiaohong" = specifically `worker-sense`

---

## What NOT to Say

| Wrong | Right | Reason |
|-------|-------|--------|
| Worker | execution agent | Worker is old terminology |
| workers | execution agents | — |
| Chief Officer | Wang Xifeng | Wrong rank |
| First Mate | Wang Xifeng | Wrong rank |
| pilot general | Jia Baoyu | Wrong word order |
| worker-drive (as display name) | Qingwen / 晴雯 | Use agent ID only in `agentId:` field |
