# Recruiting Rules

> Guidelines for Pilot selection and Sailor dispatch.

## Pilot Selection Matrix

| Task Signal | Recommended Pilot | Rationale |
|-------------|-------------------|-----------|
| "research", "analyze", "compare", "investigate" | pilot-research | Information-intensive |
| "build", "implement", "code", "fix", "deploy" | pilot-build | Implementation-intensive |
| General / ambiguous / multi-domain | pilot-general | Flexible orchestration |

## Sailor Dispatch Rules

| Sailor Tag | Agent ID | Use When | Tools |
|------------|----------|----------|-------|
| #动力与开拓 | `worker-drive` | 实现、编码、交付 | exec, write, read |
| #结构与风控 | `worker-guard` | 审查、测试、验证 | exec (test only), read |
| #感知与策略 | `worker-sense` | 调研、分析、判断 | web_search, web_fetch, read, write |

When spawning a Sailor, use the exact `agentId` from the table above:

```
sessions_spawn({ agentId: "worker-drive", ... })
sessions_spawn({ agentId: "worker-guard", ... })
sessions_spawn({ agentId: "worker-sense", ... })
```

## Constraints

- One Sailor = one objective, no role drift
- Max 2 Sailors per Pilot
- Sailors are leaf nodes — never spawn further
