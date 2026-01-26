---
name: /openspec-apply
id: openspec-apply
category: OpenSpec
description: Implement an approved OpenSpec change with PromptX role switching and memory retrieval.
---

**集成 OpenSpec + PromptX 提案实现流程**

<!-- OPENSPEC:START -->
**Guardrails**
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` for OpenSpec conventions.
- **Do NOT start implementation until proposal is approved.**
- **You MUST use PromptX MCP tools** - never describe role activation in natural language.
- **Role switching is MANDATORY** before each task group based on role annotations.

**Steps (MUST follow in order)**
Track these steps as TODOS and complete them one by one.

## Step 1: Read Proposal Documents
Read these files to understand scope and acceptance criteria:
```python
proposal = read_file("openspec/changes/{CHANGE_ID}/proposal.md")
design = read_file("openspec/changes/{CHANGE_ID}/design.md")  # if exists
tasks = read_file("openspec/changes/{CHANGE_ID}/tasks.md")
```

## Step 2: Analyze Tasks and Identify Roles
1. Parse `tasks.md` to extract task groups and their role annotations
2. Role annotation format: `**角色**：`ROLE_ID`` at end of each task group
3. Build a list of task groups in order

## Step 3: Activate Primary Role and Retrieve Memory

### 3.1 Activate Primary Role (First task group's role)
```
mcp_promptx_action(role="FIRST_TASK_GROUP_ROLE")
```

### 3.2 DMN Full Scan
```
mcp_promptx_recall(role="CURRENT_ROLE", query=null, mode="balanced")
```

### 3.3 Retrieve Implementation Memory
```
mcp_promptx_recall(role="CURRENT_ROLE", query="implementation best-practices", mode="focused")
```

## Step 4: Implement Tasks (Sequential, Role-Switching REQUIRED)

For EACH task group in order:

### 4.1 Check Current Role
Extract required role from task group's `**角色**：`ROLE_ID`` annotation.

### 4.2 Switch Role if Needed (MANDATORY)
If current role != required role:
```
mcp_promptx_action(role="REQUIRED_ROLE")
mcp_promptx_recall(role="REQUIRED_ROLE", query=null, mode="balanced")  # DMN scan
mcp_promptx_recall(role="REQUIRED_ROLE", query="task_keywords", mode="focused")  # Focused
```

### 4.3 Implement Task Group
Execute all task items in the group using memories to guide implementation.

### 4.4 Save Implementation Experience
After completing the task group:
```
mcp_promptx_remember(
    role="CURRENT_ROLE",
    engrams=[{
        content: "Completed task group: KEY_DECISIONS and lessons learned",
        schema: "implementation TASK_GROUP_KEYWORDS",
        strength: 0.8,
        type: "LINK"
    }]
)
```

### 4.5 Update Task Status
Only mark as complete AFTER confirming all items in the group are done:
- Change `- [ ]` to `- [x]` in tasks.md

## Step 5: Update Project Plan (MANDATORY)
Update `docs/PROJECT_PLAN.md`:
- Find corresponding requirement entry
- Change `[ ]` to `[x]`
- Add completion date and notes

## Step 6: Save Project-Level Experience
```
mcp_promptx_remember(
    role="PRIMARY_ROLE",
    engrams=[{
        content: "Completed FEATURE_NAME. Key decisions: DECISIONS. Lessons: LESSONS",
        schema: "project-experience feature-completion FEATURE_NAME",
        strength: 0.8,
        type: "PATTERN"
    }]
)
```

**Checklist (MUST complete all)**
- [ ] Step 1: Read proposal.md, design.md (if exists), and tasks.md
- [ ] Step 2: Parsed tasks.md and extracted all task groups with roles
- [ ] Step 3.1: Activated first task group's role with `mcp_promptx_action()`
- [ ] Step 3.2: Executed DMN scan with `recall(role, null, "balanced")`
- [ ] Step 3.3: Retrieved implementation memory with `recall(query, "focused")`
- [ ] Step 4.1: For EACH task group, extracted role annotation
- [ ] Step 4.2: Switched role with `mcp_promptx_action()` when needed
- [ ] Step 4.2: Performed DMN scan after each role switch
- [ ] Step 4.3: Implemented all task items in each group
- [ ] Step 4.4: Saved experience with `remember()` after each task group
- [ ] Step 4.5: Updated task status in tasks.md after each group completion
- [ ] Step 5: Updated PROJECT_PLAN.md (marked as completed)
- [ ] Step 6: Saved project-level experience with `remember()`

**Role Switching Pattern (CRITICAL)**
```
FOR each task_group IN task_groups:
    required_role = extract_role_from(task_group)
    
    IF current_role != required_role:
        mcp_promptx_action(role=required_role)  # SWITCH ROLE
        memory_network = mcp_promptx_recall(role, null, "balanced")  # DMN SCAN
        task_memory = mcp_promptx_recall(role, "keywords", "focused")  # FOCUSED
    
    implement_all_items_in(task_group)
    
    mcp_promptx_remember(role, experience)  # SAVE EXPERIENCE
    update_task_status(task_group, completed=True)
```

**Reference**
- Use `openspec show <id> --json --deltas-only` for additional context
- Run `openspec list` to check change status
- Read `openspec/AGENTS.md` for implementation conventions
