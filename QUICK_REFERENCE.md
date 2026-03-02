# Workflow System - Quick Reference

## For Users

### Send WhatsApp Message
```
"Send 'Hello!' to John on WhatsApp"
```
AI automatically uses: `execute_workflow("whatsapp", "send_message", {...})`

### Send Instagram DM
```
"DM Sarah on Instagram saying 'See you tomorrow'"
```
AI automatically uses: `execute_workflow("instagram", "send_dm", {...})`

### Send Telegram Message
```
"Message Alex on Telegram: 'Meeting at 5pm'"
```
AI automatically uses: `execute_workflow("telegram", "send_message", {...})`

---

## For Developers

### List Available Workflows
```python
list_workflows()
# Returns: {"whatsapp": ["send_message"], "instagram": ["send_dm"], ...}
```

### Execute Workflow
```python
execute_workflow(
    app_name="whatsapp",
    workflow_name="send_message",
    parameters={
        "contact_name": "John",
        "message": "Hi there!"
    }
)
```

### Add New Workflow

1. **Find UI Elements**:
```python
get_current_screen_structure()
# Look for resource_id, text, content_desc
```

2. **Add to app_workflows.yaml**:
```yaml
myapp:
  package: "com.example.myapp"
  workflows:
    my_action:
      steps:
        - action: tap
          selector: {resource_id: "com.example:id/button"}
        - action: type_text
          input: "{param1}"
```

3. **Use It**:
```python
execute_workflow("myapp", "my_action", {"param1": "value"})
```

---

## Workflow Actions

| Action | Description | Example |
|--------|-------------|---------|
| `tap` | Click element | `{action: tap, selector: {text: "Send"}}` |
| `type_text` | Enter text | `{action: type_text, input: "{message}"}` |
| `wait` | Pause | `{action: wait, duration: 2}` |
| `swipe` | Swipe gesture | `{action: swipe, coordinates: {...}}` |

---

## Selectors

| Selector | Description | Example |
|----------|-------------|---------|
| `text` | Visible text | `{text: "Send"}` |
| `content_desc` | Accessibility label | `{content_desc: "New message"}` |
| `resource_id` | Android resource ID | `{resource_id: "com.app:id/button"}` |

---

## Parameters

Use `{parameter_name}` in workflows for dynamic values:

```yaml
input: "{contact_name}"  # Replaced with actual contact name
input: "{message}"       # Replaced with actual message
```

---

## Benefits

✅ **10x Faster**: 1 tool call vs 10-15 calls
✅ **Zero Context**: Workflows loaded on-demand
✅ **Reliable**: Exact paths, no guessing
✅ **Maintainable**: Update once, works everywhere
✅ **Scalable**: Add unlimited apps

---

## Files

- `app_workflows.yaml` - Workflow definitions
- `mcp_server/workflow_engine.py` - Execution engine
- `WORKFLOW_GUIDE.md` - Detailed guide
- `AI_TRAINING_METHODS.md` - Explanation of methods
- `examples/workflow_example.py` - Code examples
