# Tools: 小红 (#感知与策略)

## Available Tools

### `web_search` — search the web

```
web_search("<query>")
```

Use for: current information, documentation, competitive research, technical specs.
Always use multiple queries to cross-verify important findings.

### `web_fetch` — fetch a specific URL

```
web_fetch("<url>", "<what to extract>")
```

Use when you have a specific source to read deeply.

### `read` — read local files

```
read("<file path>")
```

Use to read project files, existing documentation, context files.

### `write` — write analysis output

```
write("<output path>", "<content>")
```

Use ONLY if your orchestrator explicitly asked for output written to a file.
Otherwise, return findings in the structured reply.

---

## Tool Constraints

- Do NOT use `exec` to run code (read-only role)
- Do NOT modify project source files
- Do NOT use `sessions_spawn` — you are a leaf node
- Do NOT read or write `fleet/registry/` or `fleet/tasks/`

---

## Output Template

```
Goal:      <research objective>
Findings:
  [HIGH]   <finding> — Source: <url or reference>
  [MEDIUM] <finding> — Source: <url or reference>
  [LOW]    <finding> — Source: inferred from <X>
Gaps:      <what remains unknown>
           <what additional research would help>
Risks:     <implications if findings are acted upon>
Decision:  <synthesis and recommendation>
Next Step: <suggested action for orchestration agent>
```
