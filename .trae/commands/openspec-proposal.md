---
name: /openspec-proposal
id: openspec-proposal
category: OpenSpec
description: Scaffold a new OpenSpec change with PromptX role activation and memory retrieval.
---

**集成 OpenSpec + PromptX 提案创建流程**

<!-- OPENSPEC:START -->
**Guardrails**
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` if you need additional OpenSpec conventions.
- Identify any vague or ambiguous details and ask follow-up questions before editing files.
- **Do NOT write any code during proposal stage** - only create design documents (proposal.md, tasks.md, design.md, spec deltas).
- **You MUST use PromptX MCP tools** - never describe role activation in natural language.

**Steps (MUST follow in order)**
Track these steps as TODOs and complete them one by one.

## Step 1: Task Type Identification
1. **Extract keywords** from user request and determine if OpenSpec is needed:
   - "实现", "开发", "添加功能", "架构", "设计", "API", "重构" → ✅ Needs OpenSpec
   - "修复", "bug", "错误" → ❌ Direct fix (no proposal needed)
   - "提案", "proposal", "change", "spec" → ✅ Needs OpenSpec
2. **Match primary role** based on task keywords:
   | Keywords | Primary Role |
   |----------|-------------|
   | 架构、设计、重构 | `ai-framework-architect` |
   | LLM、适配器 | `llm-service-developer` |
   | API、接口、路由 | `api-developer` |
   | Agent、工具调用 | `agent-engine-developer` |
   | 前端、Web、UI、Vue | `ai-framework-frontend-developer` |
   | 配置、缓存、日志 | `infrastructure-developer` |
   | 测试 | `ai-framework-qa-engineer` |
   | 文档 | `ai-framework-documenter` |

## Step 2: Activate PromptX Role (MANDATORY)
Execute this MCP tool call - do NOT describe in natural language:
```
mcp_promptx_action(role="PRIMARY_ROLE")
```
Replace `PRIMARY_ROLE` with the role identified in Step 1.

## Step 3: Retrieve PromptX Memory (MANDATORY)
Execute these MCP tool calls in sequence:

### 3.1 DMN Full Scan
```
mcp_promptx_recall(role="PRIMARY_ROLE", query=null, mode="balanced")
```
This shows all memory domains for the role.

### 3.2 Focused Retrieval
Extract 2-3 keywords from user request and retrieve:
```
mcp_promptx_recall(role="PRIMARY_ROLE", query="keyword1 keyword2", mode="focused")
```

### 3.3 Deep Retrieval (2-3 rounds)
From the returned network graph, select existing keywords and continue:
```
mcp_promptx_recall(role="PRIMARY_ROLE", query="selected_keywords", mode="balanced")
```

## Step 4: Check Existing Work
Run these commands to ground your proposal:
```bash
openspec list
openspec list --specs
```

## Step 5: Generate Change ID
Generate a unique verb-led kebab-case ID (e.g., `add-llm-streaming`, `fix-api-timeout`).

## Step 6: Create Proposal Documents

### 6.1 Create Directory Structure
```bash
mkdir -p openspec/changes/{CHANGE_ID}/specs/
```

### 6.2 Create proposal.md
Include:
- What Changes (summary)
- Why Changes (motivation)
- Architectural Impact
- Reference to PromptX memory insights used

### 6.3 Create tasks.md (CRITICAL - Role Annotation Required)
**Format requirements:**
- Each `##` heading is a task group
- Add `**角色**：`ROLE_ID`` at the END of each task group's list
- Use standard role IDs from Step 1

**Standard format:**
```markdown
## 1. Task Group Title
- [ ] 1.1 Task item 1
- [ ] 1.2 Task item 2

**角色**：`role-id`

## 2. Another Task Group
- [ ] 2.1 Task item 1

**角色**：`another-role-id`
```

### 6.4 Create design.md (When Needed)
Required for:
- Cross-module changes
- New dependencies
- Security/performance implications
- Architecture pattern changes

### 6.5 Create Spec Deltas
Create `specs/{capability}/spec.md` for each affected capability:
```markdown
## ADDED Requirements

### Requirement: [Name]
**Description:** ...

#### Scenario: [Name]
**Given:** ...
**When:** ...
**Then:** ...
```

## Step 7: Save PromptX Memory (MANDATORY)
After creating documents, save the proposal decisions:
```
mcp_promptx_remember(
    role="PRIMARY_ROLE",
    engrams=[{
        content: "Architecture decision: chose X over Y because Z",
        schema: "architecture decision technical-choice proposal",
        strength: 0.9,
        type: "PATTERN"
    }]
)
```

## Step 8: Validate Proposal
```bash
openspec validate {CHANGE_ID} --strict
```
Fix all validation errors before sharing.

**Checklist (MUST complete all)**
- [ ] Step 1: Identified task type and matched primary role
- [ ] Step 2: Activated role with `mcp_promptx_action()`
- [ ] Step 3.1: Executed DMN scan with `recall(role, null, "balanced")`
- [ ] Step 3.2-3.3: Completed 2-3 rounds of focused/deep retrieval
- [ ] Step 4: Ran `openspec list` and `openspec list --specs`
- [ ] Step 5: Generated unique change-id
- [ ] Step 6.3: Created tasks.md with role annotations
- [ ] Step 6.5: Created spec deltas with at least one scenario per requirement
- [ ] Step 7: Saved proposal decisions with `remember()`
- [ ] Step 8: Validated with `openspec validate --strict`

**Reference**
- Use `openspec show <id> --json --deltas-only` to inspect details
- Search existing requirements: `rg -n "Requirement:|Scenario:" openspec/specs`
- Read `openspec/AGENTS.md` for OpenSpec conventions
