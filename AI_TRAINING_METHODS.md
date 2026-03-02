# AI Training Methods Without Increasing Context

## Your Question
"Is it possible to set specific instructions so when I say 'send message to someone on WhatsApp', the AI knows the exact place to click? Can we train the AI without increasing context or tokens?"

## Answer: YES! Here are 4 methods:

---

## Method 1: Workflow Configuration Files ⭐ RECOMMENDED

**How it works**: Define exact UI paths in YAML files that are loaded on-demand.

**File**: `app_workflows.yaml`

```yaml
whatsapp:
  workflows:
    send_message:
      steps:
        - action: tap
          selector: {resource_id: "com.whatsapp:id/fab"}
        - action: type_text
          input: "{contact_name}"
        - action: tap
          selector: {text: "{contact_name}"}
        - action: type_text
          input: "{message}"
        - action: tap
          selector: {resource_id: "com.whatsapp:id/send"}
```

**Usage**: 
```
AI: "I'll use the WhatsApp send_message workflow"
execute_workflow("whatsapp", "send_message", {"contact_name": "John", "message": "Hi"})
```

**Benefits**:
- ✅ Zero context overhead (loaded only when needed)
- ✅ Exact paths, no guessing
- ✅ Easy to update
- ✅ Works for all contacts/messages

---

## Method 2: MCP Tool Descriptions

**How it works**: Embed instructions directly in tool descriptions.

```python
Tool(
    name="send_whatsapp_message",
    description="""Send WhatsApp message. 
    Steps: 1) Tap FAB (resource_id: com.whatsapp:id/fab)
           2) Search contact in search_src_text field
           3) Tap contact name
           4) Type in entry field
           5) Tap send button""",
    inputSchema={...}
)
```

**Benefits**:
- ✅ Instructions always available
- ⚠️ Increases tool description size slightly
- ✅ No external files needed

---

## Method 3: Kiro Steering Files

**How it works**: Create context files that load automatically when relevant.

**File**: `.kiro/steering/whatsapp-automation.md`

```markdown
---
inclusion: fileMatch
fileMatchPattern: "whatsapp|messaging"
---

# WhatsApp Automation Guide

When sending WhatsApp messages:
1. Tap the green FAB button (resource_id: com.whatsapp:id/fab)
2. Search for contact in search field
3. Select contact from results
4. Type message in entry field (resource_id: com.whatsapp:id/entry)
5. Tap send button (resource_id: com.whatsapp:id/send)
```

**Benefits**:
- ✅ Loads only when WhatsApp is mentioned
- ✅ Can include detailed instructions
- ✅ Easy to edit without code changes

---

## Method 4: App-Specific MCP Tools

**How it works**: Create dedicated tools for each app workflow.

```python
Tool(
    name="whatsapp_send_message",
    description="Send WhatsApp message using predefined workflow",
    inputSchema={
        "contact_name": "string",
        "message": "string"
    }
)
```

**Benefits**:
- ✅ Simple interface
- ✅ Encapsulates complexity
- ⚠️ Need one tool per workflow

---

## Comparison

| Method | Context Size | Flexibility | Ease of Update | Best For |
|--------|-------------|-------------|----------------|----------|
| Workflow Files | Minimal | High | Easy | Multiple apps, complex flows |
| Tool Descriptions | Small | Medium | Requires code | Simple, fixed workflows |
| Steering Files | Conditional | High | Very Easy | Documentation, guidelines |
| Dedicated Tools | Minimal | Low | Requires code | Single-purpose actions |

---

## Recommended Approach

**Use Method 1 (Workflow Files)** because:

1. **Zero Context Overhead**: Workflows load on-demand
2. **Scalable**: Add unlimited apps without bloating context
3. **Maintainable**: Update UI paths in one place
4. **Flexible**: Support parameters, conditions, fallbacks
5. **Fast**: Direct execution, no exploration needed

---

## Implementation Status

✅ Created `app_workflows.yaml` with WhatsApp, Instagram, Telegram workflows
✅ Created `WorkflowEngine` class to execute workflows
✅ Added `execute_workflow` and `list_workflows` MCP tools
✅ Integrated into MCP server

---

## Usage Example

**Before** (AI explores UI every time):
```
User: "Send 'Hi' to John on WhatsApp"
AI: Opens WhatsApp → Explores screen → Finds buttons → Clicks → Types → Sends
Time: 30-60 seconds, 5-10 tool calls
```

**After** (AI uses workflow):
```
User: "Send 'Hi' to John on WhatsApp"
AI: execute_workflow("whatsapp", "send_message", {"contact_name": "John", "message": "Hi"})
Time: 5-10 seconds, 1 tool call
```

---

## Adding New Workflows

1. Explore the app UI once: `get_current_screen_structure()`
2. Note resource IDs, text, content descriptions
3. Add workflow to `app_workflows.yaml`
4. Test with `execute_workflow`
5. Done! AI now knows the exact path forever.

---

## Key Insight

You're not "training" the AI in the traditional sense. You're giving it a **reference manual** that it consults when needed, like a developer reading API documentation. The AI doesn't need to memorize paths—it looks them up in the workflow file when executing tasks.
