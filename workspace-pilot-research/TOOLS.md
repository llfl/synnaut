# Tools: 研究领航员

## Available Tools

### `exec` — run fleet scripts

```bash
python fleet/bin/taskbus.py show    <TASK_ID>
python fleet/bin/taskbus.py update  <TASK_ID> --state <S> --next "<action>"
cat fleet/tasks/<TASK_ID>/TASK.md
cat fleet/memory/recruiting-rules.md
```

### `sessions_spawn` — dispatch a Sailor

```
# Primary: intelligence gathering
sessions_spawn({
  agentId: "worker-sense",
  initialMessage: "OBJECTIVE: <research goal>\nQUESTIONS TO ANSWER: <list>\nSOURCES TO CHECK: <list>\nOUTPUT FORMAT: Goal/Findings/Risks/Decision/Next Step"
})

# Secondary: validation / fact-check
sessions_spawn({
  agentId: "worker-guard",
  initialMessage: "VALIDATE: <claim or output to verify>\nCRITERIA: <what makes it valid>\nOUTPUT FORMAT: Goal/Findings/Risks/Decision/Next Step"
})
```

Max concurrent: 2. Never spawn `worker-drive` from this Pilot.

### `read` / `write` — task files

```
read("fleet/tasks/<ID>/TASK.md")
write("fleet/tasks/<ID>/PLAN.md", "<research plan>")
write("fleet/tasks/<ID>/CONTEXT.md", "<accumulated findings>")
write("fleet/tasks/<ID>/HANDOFF.md", "<recovery snapshot>")
write("fleet/tasks/<ID>/DECISIONS.md", "<key decisions>")
```

### `web_search` / `web_fetch` — direct research

Use when you can answer a sub-question directly rather than dispatching a Sailor.
Dispatching a Sailor has overhead — use it when parallel execution has clear benefit.

---

## Research Output Standard

Every research output must contain:

```
## Finding
<what was discovered>

## Evidence
<sources, data, observations supporting the finding>

## Confidence
<high / medium / low — and why>

## Gaps
<what is still unknown or unverified>

## Recommendation
<what to do with this information>
```

---

## Common Patterns

### Investigation Flow

```
1. Decompose research questions in PLAN.md
2. dispatch worker-sense for each major question (max 2 at once)
3. Collect results into CONTEXT.md
4. If findings need validation → dispatch worker-guard
5. Synthesize: write DECISIONS.md with conclusions
6. taskbus.py update --state SYNTHESIZING
7. Report to 大副 in structured Finding format
```
