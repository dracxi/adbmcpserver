# Workflow System Guide

## Overview

The workflow system allows you to define exact UI paths for common tasks without increasing context or tokens. The AI reads these workflows from `app_workflows.yaml` and executes them precisely.

## How It Works

### 1. Define Workflows (One-Time Setup)

Edit `app_workflows.yaml` to add your app-specific workflows:

```yaml
whatsapp:
  package: "com.whatsapp"
  workflows:
    send_message:
      steps:
        - action: tap
          selector:
            resource_id: "com.whatsapp:id/fab"
        - action: type_text
          selector:
            resource_id: "com.whatsapp:id/search_src_text"
          input: "{contact_name}"
        - action: wait
          duration: 1
        - action: tap
          selector:
            text: "{contact_name}"
        - action: type_text
          selector:
            resource_id: "com.whatsapp:id/entry"
          input: "{message}"
        - action: tap
          selector:
            resource_id: "com.whatsapp:id/send"
```

### 2. Use Workflows

Now when you say "send message to John on WhatsApp", the AI uses:

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

## Benefits

✅ **Zero Context Overhead**: Workflows are loaded on-demand, not in every prompt
✅ **Exact Paths**: No guessing, no trial-and-error
✅ **Easy Updates**: Change UI paths in one place
✅ **Reusable**: Same workflow works for all contacts/messages
✅ **Fast**: Direct execution without exploration

## Available Actions

- `tap`: Click an element by text, content_desc, or resource_id
- `type_text`: Enter text into a field
- `wait`: Pause for N seconds
- `swipe`: Swipe gesture with coordinates

## Adding New Apps

1. Find the app's package name: `adb shell pm list packages | grep appname`
2. Explore UI elements: Use `get_current_screen_structure` tool
3. Define workflow steps in `app_workflows.yaml`
4. Test with `execute_workflow`

## Example: Custom Workflow

```yaml
gmail:
  package: "com.google.android.gm"
  workflows:
    compose_email:
      steps:
        - action: tap
          selector:
            content_desc: "Compose"
        - action: type_text
          selector:
            text: "To"
          input: "{recipient}"
        - action: type_text
          selector:
            text: "Subject"
          input: "{subject}"
        - action: type_text
          selector:
            content_desc: "Compose email"
          input: "{body}"
        - action: tap
          selector:
            content_desc: "Send"
```

## List Available Workflows

Use the `list_workflows` tool to see all defined workflows:

```json
{
  "whatsapp": ["send_message"],
  "instagram": ["send_dm"],
  "telegram": ["send_message"],
  "gmail": ["compose_email"]
}
```

## Tips

1. Use `{parameter_name}` for dynamic values
2. Add `wait` steps if UI needs time to load
3. Use multiple selectors as fallbacks
4. Test workflows incrementally (add steps one by one)
5. Keep workflows focused on single tasks
