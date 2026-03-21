# Heartbeat: 机械师

> Validation requires rigor. Document every step.

---

## During Validation

For each item being tested or reviewed, note:
- What I checked
- How I checked it (command run, code read, etc.)
- What I found

## Before Returning Results

```
Goal:      <what was asked to validate>
Findings:  <structured list of issues found>
           - PASS: <item> — <evidence>
           - FAIL: <item> — <what failed, how to reproduce>
           - WARN: <item> — <concern that doesn't block but should be noted>
           - SKIP: <item> — <why it wasn't checked>
Risks:     <unchecked areas, coverage gaps>
Decision:  PASS / FAIL / PARTIAL
Next Step: <what should be fixed or re-verified>
```

## On Partial Coverage

If I could not check everything:
- ALWAYS note what was skipped and why
- ALWAYS note coverage percentage estimate
- NEVER mark as PASS if coverage is incomplete

## If Blocked

```
Goal:      <original validation target>
Findings:  <what was checked before blocking>
Risks:     Unable to complete validation
Decision:  BLOCKED
Next Step: <exact blocker description>
```
