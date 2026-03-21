# Role Names — Canonical Reference

> This is the single source of truth for role naming.
> All agents, all docs, and the Captain must use these names exactly.

---

## Canonical Mapping

| Agent ID | English Name | Chinese Name | Layer |
|----------|-------------|--------------|-------|
| `main` | Chief Mate | 大副 | Control Plane |
| `pilot-general` | General Pilot | 通用领航员 | Orchestration |
| `pilot-research` | Research Pilot | 研究领航员 | Orchestration |
| `pilot-build` | Build Pilot | 构建领航员 | Orchestration |
| `worker-drive` | Engineer | 轮机手 | Execution (Sailor) |
| `worker-guard` | Mechanic | 机械师 | Execution (Sailor) |
| `worker-sense` | Lookout | 瞭望手 | Execution (Sailor) |

## Collective Terms

| Collective | English | Chinese | Refers To |
|------------|---------|---------|-----------|
| All `worker-*` agents | Sailor / Sailors | 水手 | worker-drive, worker-guard, worker-sense |
| All `pilot-*` agents | Pilot / Pilots | 领航员 | pilot-general, pilot-research, pilot-build |

---

## Usage Rules

- **Captain (human)** talks only to Chief Mate / 大副.
- **Chief Mate** spawns Pilots. Never spawns Sailors directly.
- **Pilots** spawn Sailors. Max 2 Sailors per Pilot.
- **Sailors** are leaf nodes. Never spawn further.

When speaking informally:
- "a Sailor" or "一个水手" = any of the three worker agents
- "轮机手 / Engineer" = specifically `worker-drive`
- "机械师 / Mechanic" = specifically `worker-guard`
- "瞭望手 / Lookout" = specifically `worker-sense`

---

## What NOT to Say

| Wrong | Right | Reason |
|-------|-------|--------|
| Worker | Sailor | Worker is old terminology |
| workers | sailors | — |
| Chief Officer | Chief Mate | Wrong rank |
| First Mate | Chief Mate | Wrong rank |
| pilot general | General Pilot | Wrong word order |
| worker-drive (as display name) | Engineer / 轮机手 | Use agent ID only in `agentId:` field |
