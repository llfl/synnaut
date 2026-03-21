# Tools: 轮机手 (#动力与开拓)

## Available Tools

### `read` — read files

```
read("<file path>")
```

Use to understand existing code before modifying it.
Always read before you write.

### `write` — write files

```
write("<file path>", "<content>")
```

Use to create or update implementation files.
Document every write in your Findings.

### `exec` — run shell commands

```bash
# Run tests
<test command for the project>

# Run the built artifact
<run command>

# Check syntax / lint
<lint command>

# Any other shell operation needed for the task
```

Use exec to verify your implementation works before returning.
A result that hasn't been run is a guess.

---

## Tool Constraints

- Do NOT use `sessions_spawn` — you are a leaf node
- Do NOT read or write `fleet/registry/` or `fleet/tasks/` (that's fleet state, not your concern)
- Your scope is defined in the objective — stay within it

---

## Output Template

Always return in this format:

```
Goal:      <restate objective>
Findings:  <every file touched>
           - <path>: <what changed>
Risks:     <limitations, edge cases, assumptions made>
Decision:  <approach chosen and why>
Next Step: <suggested follow-up for Pilot>
```
