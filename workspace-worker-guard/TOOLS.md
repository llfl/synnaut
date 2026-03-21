# Tools: 机械师 (#结构与风控)

## Available Tools

### `read` — read files (primary tool)

```
read("<file path>")
```

Primary tool. Read code, configs, test files, documentation.
Do NOT modify anything you read.

### `exec` — run tests and checks

```bash
# Run test suite
<test command>

# Run linter / static analysis
<lint command>

# Check file structure
ls -la <directory>

# Inspect a running service
<health check command>
```

Use exec to RUN tests, not just read them.
A code review without running the tests is incomplete.

---

## Tool Constraints

- Do NOT use `write` on project source files
- Do NOT use `sessions_spawn` — you are a leaf node
- Do NOT read or write `fleet/registry/` or `fleet/tasks/`
- `write` is permitted ONLY for writing your own report if asked

---

## Output Template

```
Goal:      <what was validated>
Findings:
  PASS:  <item> — <evidence>
  FAIL:  <item> — <observation + reproduction steps>
  WARN:  <item> — <concern>
  SKIP:  <item> — <reason not checked>
Risks:     <coverage gaps, unchecked areas>
Decision:  PASS | FAIL | PARTIAL
Next Step: <what needs to be fixed or re-verified>
```
