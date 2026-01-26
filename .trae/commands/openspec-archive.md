---
name: /openspec-archive
id: openspec-archive
category: OpenSpec
description: Archive a deployed OpenSpec change with PromptX memory summary and project plan update.
---

**集成 OpenSpec + PromptX 提案归档流程**

<!-- OPENSPEC:START -->
**Guardrails**
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` for OpenSpec conventions.
- **You MUST update PROJECT_PLAN.md** - this is a hard rule.
- **You MUST use PromptX MCP tools** - never describe role activation in natural language.

**Steps (MUST follow in order)**
Track these steps as TODOS and complete them one by one.

## Step 1: Identify Change ID
1. If change ID is provided in prompt (e.g., `<ChangeId>`), use it directly.
2. If conversation references a change loosely, run:
   ```bash
   openspec list
   ```
   Share candidates and confirm the intended change ID.
3. If no change ID can be identified, STOP and ask user.
4. If multiple changes match, STOP and ask user to specify.

## Step 2: Validate Change ID
```bash
openspec list
# OR
openspec show {CHANGE_ID}
```
Stop if:
- Change is missing
- Change is already archived
- Change is not ready to archive

## Step 3: Execute Archive
```bash
openspec archive {CHANGE_ID} --yes
```
Use `--skip-specs` only for tooling-only work.

## Step 4: Verify Archive Result
1. Check that specs were updated:
   ```bash
   openspec list --specs
   ```
2. Verify change is in archive:
   ```bash
   openspec/changes/archive/
   ```

## Step 5: Read Archived Documents
```python
proposal = read_file(f"openspec/changes/archive/{DATE}-{CHANGE_ID}/proposal.md")
tasks = read_file(f"openspec/changes/archive/{DATE}-{CHANGE_ID}/tasks.md")

# Extract:
# - Feature module
# - Corresponding project plan entry
# - Completion notes from proposal
```

## Step 6: Update Project Plan (MANDATORY - HARD RULE)
Update `docs/PROJECT_PLAN.md`:
1. Find corresponding requirement entry
2. Change `[ ]` to `[x]`
3. Add completion date (use archive date)
4. Add completion notes (from proposal.md "What Changes" section)

## Step 7: Save Project-Level Experience (MANDATORY)
```
mcp_promptx_remember(
    role="ai-framework-architect",  # Use architect for project-level
    engrams=[{
        content: "Archived CHANGE_ID. Feature: FEATURE_SUMMARY. Lessons: LESSONS",
        schema: "project-experience archive FEATURE_SUMMARY PROJECT_PLAN_SYNC",
        strength: 0.8,
        type: "PATTERN"
    }]
)
```

## Step 8: Final Validation
```bash
openspec validate --strict
```
Fix any issues before completing.

**Checklist (MUST complete all)**
- [ ] Step 1: Identified and confirmed change ID
- [ ] Step 2: Validated change exists and is ready for archive
- [ ] Step 3: Executed `openspec archive {CHANGE_ID} --yes`
- [ ] Step 4: Verified specs updated and change in archive
- [ ] Step 5: Read archived proposal.md and tasks.md
- [ ] Step 6: Updated PROJECT_PLAN.md (marked as completed, added date and notes)
- [ ] Step 6.4: Verified PROJECT_PLAN update matches archive content
- [ ] Step 7: Saved project-level experience with `remember()`
- [ ] Step 8: Ran `openspec validate --strict` and fixed issues

**Project Plan Update Rules**
1. **Must Update**: Archive requires PROJECT_PLAN update if not already done
2. **Sync Check**: Verify PROJECT_PLAN status matches archived state
3. **Completion Date**: Use archive date
4. **Notes**: Extract from proposal.md "What Changes" section

**Reference**
- Use `openspec list` to confirm change IDs
- Use `openspec list --specs` to verify spec updates
- Read `openspec/AGENTS.md` for archiving conventions
