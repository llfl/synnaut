# Recruiting Rules

> Guidelines for Pilot selection and Worker dispatch.

## Pilot Selection Matrix

| Task Signal | Recommended Pilot | Rationale |
|-------------|-------------------|-----------|
| "research", "analyze", "compare", "investigate" | pilot-research | Information-intensive |
| "build", "implement", "code", "fix", "deploy" | pilot-build | Implementation-intensive |
| General / ambiguous / multi-domain | pilot-general | Flexible orchestration |

## Worker Dispatch Rules

| Worker Tag | Agent ID | Use When | Tools |
|------------|----------|----------|-------|
| #动力与开拓 | `worker-drive` | 实现、编码、交付 | exec, write, read |
| #结构与风控 | `worker-guard` | Testing, review, validation | exec (test only), read |
| #感知与策略 | `worker-sense` | Research, analysis, judgment | web_search, web_fetch, read, write |

When spawning a Worker, use the exact `agentId` from the table above:

```
sessions_spawn({ agentId: "worker-drive", ... })
sessions_spawn({ agentId: "worker-guard", ... })
sessions_spawn({ agentId: "worker-sense", ... })
```

## Constraints

- One Worker = one objective, no role drift
- Max 2 Workers per Pilot
- Workers are leaf nodes — never spawn further
