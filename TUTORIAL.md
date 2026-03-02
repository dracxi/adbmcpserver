# Tutorial: Teaching AI Exact UI Paths Without Increasing Context

## Your Goal
You want to say "send message to John on WhatsApp" and have the AI know exactly where to click, without exploring the UI every time, and without bloating the context.

## Solution: Workflow Configuration System

This tutorial shows you how to "teach" the AI once, and it remembers forever (without actually increasing context size).

---

## Part 1: Understanding the Problem

### What Happens Without Workflows

```
You: "Send 'Hi' to John on WhatsApp"

AI thinks:
1. "I need to open WhatsApp" ✓
2. "Now I need to figure out the UI..." ✗
3. Gets screen structure (100+ elements)
4. Analyzes which button to click
5. Clicks button
6. Gets new screen structure
7. Analyzes again...
... 12+ steps later ...
16. Finally sends message

Problem: Steps 2-15 happen EVERY SINGLE TIME
```

### What Happens With Workflows

```
You: "Send 'Hi' to John on WhatsApp"

AI thinks:
1. "I need to send a WhatsApp message" ✓
2. "I have a workflow for that!" ✓
3. Executes workflow with parameters
4. Done!

Solution: AI looks up the exact path from a config file
```

---

## Part 2: How It Works (The Magic)

### The Secret: On-Demand Loading

The workflow file (`app_workflows.yaml`) is NOT loaded into the AI's context. Instead:

1. **AI sees tool description**: "execute_workflow - Execute predefined workflow"
2. **AI decides to use it**: Based on your request
3. **Tool loads workflow**: Only when called
4. **Tool executes steps**: Following the exact path
5. **Tool returns result**: Success or failure

**Key Insight**: The AI doesn't need to know the workflow details. It just needs to know the workflow EXISTS and how to call it.

---

## Part 3: Setting Up Your First Workflow

### Step 1: Explore the App UI (One Time Only)

```python
# Connect to device
list_devices()
select_device("your_device_id")

# Open WhatsApp
open_app("whatsapp")

# Get UI structure
get_current_screen_structure()
```

**Output** (simplified):
```json
{
  "elements": [
    {
      "resource_id": "com.whatsapp:id/fab",
      "content_desc": "New chat",
      "clickable": true
    },
    {
      "resource_id": "com.whatsapp:id/search_src_text",
      "text": "Search...",
      "clickable": true
    },
    ...
  ]
}
```

**Note down**:
- FAB button: `resource_id: "com.whatsapp:id/fab"`
- Search field: `resource_id: "com.whatsapp:id/search_src_text"`
- Message field: `resource_id: "com.whatsapp:id/entry"`
- Send button: `resource_id: "com.whatsapp:id/send"`

### Step 2: Define the Workflow

Edit `app_workflows.yaml`:

```yaml
whatsapp:
  package: "com.whatsapp"
  workflows:
    send_message:
      steps:
        # Step 1: Click the new chat button
        - action: tap
          selector:
            resource_id: "com.whatsapp:id/fab"
        
        # Step 2: Type contact name in search
        - action: type_text
          selector:
            resource_id: "com.whatsapp:id/search_src_text"
          input: "{contact_name}"  # This will be replaced
        
        # Step 3: Wait for search results
        - action: wait
          duration: 1
        
        # Step 4: Click the contact
        - action: tap
          selector:
            text: "{contact_name}"  # This will be replaced
        
        # Step 5: Type the message
        - action: type_text
          selector:
            resource_id: "com.whatsapp:id/entry"
          input: "{message}"  # This will be replaced
        
        # Step 6: Click send
        - action: tap
          selector:
            resource_id: "com.whatsapp:id/send"
```

### Step 3: Test the Workflow

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

**Result**:
```json
{
  "success": true,
  "message": "Workflow 'send_message' completed successfully",
  "steps_executed": 6
}
```

### Step 4: Use It Forever

Now you can just say:
- "Send 'Hello' to Sarah on WhatsApp"
- "Message John on WhatsApp: 'Meeting at 3pm'"
- "WhatsApp Alex saying 'See you tomorrow'"

The AI automatically uses the workflow!

---

## Part 4: Adding More Apps

### Example: Instagram DM

```yaml
instagram:
  package: "com.instagram.android"
  workflows:
    send_dm:
      steps:
        - action: tap
          selector:
            content_desc: "Direct"
        - action: tap
          selector:
            content_desc: "New message"
        - action: type_text
          selector:
            text: "Search..."
          input: "{contact_name}"
        - action: wait
          duration: 1
        - action: tap
          selector:
            text: "{contact_name}"
        - action: tap
          selector:
            text: "Chat"
        - action: type_text
          selector:
            text: "Message..."
          input: "{message}"
        - action: tap
          selector:
            content_desc: "Send"
```

### Example: Gmail

```yaml
gmail:
  package: "com.google.android.gm"
  workflows:
    send_email:
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

---

## Part 5: Advanced Features

### Multiple Selectors (Fallbacks)

```yaml
- action: tap
  selector:
    resource_id: "com.app:id/button"
  fallback:
    text: "Send"
```

If resource_id fails, tries text.

### Conditional Steps

```yaml
- action: tap
  selector:
    text: "Accept"
  optional: true  # Don't fail if not found
```

### Dynamic Waits

```yaml
- action: wait
  duration: 2
  reason: "Waiting for search results"
```

---

## Part 6: Troubleshooting

### Workflow Fails at Step 3

**Problem**: Element not found

**Solution**:
1. Run `get_current_screen_structure()` at that point
2. Check if element exists
3. Update selector in workflow
4. Add wait step before if needed

### Workflow Too Slow

**Problem**: Too many wait steps

**Solution**:
1. Reduce wait durations
2. Use element waiting instead of fixed waits
3. Remove unnecessary waits

### UI Changed

**Problem**: App updated, workflow broken

**Solution**:
1. Explore UI again
2. Update selectors in workflow
3. Test workflow
4. Done! All future uses work again

---

## Part 7: Best Practices

### 1. Use Specific Selectors

✅ Good: `resource_id: "com.app:id/send_button"`
❌ Bad: `text: "Send"` (might match multiple elements)

### 2. Add Waits Strategically

```yaml
# After actions that trigger loading
- action: tap
  selector: {text: "Search"}
- action: wait
  duration: 1  # Wait for results
```

### 3. Use Descriptive Parameter Names

✅ Good: `{contact_name}`, `{message}`, `{recipient}`
❌ Bad: `{param1}`, `{x}`, `{data}`

### 4. Test Incrementally

Don't write the entire workflow at once. Test each step:

```yaml
# Test step 1
send_message_step1:
  steps:
    - action: tap
      selector: {resource_id: "...fab"}

# Then add step 2
send_message_step2:
  steps:
    - action: tap
      selector: {resource_id: "...fab"}
    - action: type_text
      input: "{contact_name}"
```

### 5. Document Your Workflows

```yaml
whatsapp:
  workflows:
    send_message:
      description: "Send a message to a contact"
      parameters:
        - contact_name: "Name of the contact"
        - message: "Message text to send"
      steps:
        # ... steps ...
```

---

## Part 8: Understanding Context Savings

### Without Workflows (Per Request)

```
System Prompt: 2000 tokens
Conversation History: 1000 tokens
Current Screen Structure: 500 tokens
Previous Screen Structures: 1500 tokens
AI Reasoning: 800 tokens
Tool Results: 1200 tokens
---
Total: 7000 tokens per request
```

### With Workflows (Per Request)

```
System Prompt: 2000 tokens
Conversation History: 1000 tokens
Workflow Call: 50 tokens
Workflow Result: 100 tokens
---
Total: 3150 tokens per request

Savings: 55% reduction!
```

### Over 100 Requests

- Without workflows: 700,000 tokens ($14 at $0.02/1K)
- With workflows: 315,000 tokens ($6.30 at $0.02/1K)
- **Savings: $7.70 and 385,000 tokens**

---

## Part 9: FAQ

### Q: Does the AI need to be retrained?

**A**: No! The AI just needs to know the tool exists. The workflow file is read at runtime.

### Q: What if I have 100 workflows?

**A**: No problem! They're loaded on-demand, not all at once.

### Q: Can I use variables in workflows?

**A**: Yes! Use `{variable_name}` syntax.

### Q: What if the workflow fails?

**A**: The AI can fall back to exploratory mode or ask you to update the workflow.

### Q: Can workflows call other workflows?

**A**: Not yet, but you can create composite workflows manually.

---

## Part 10: Next Steps

1. ✅ Explore your most-used apps
2. ✅ Create workflows for common tasks
3. ✅ Test workflows thoroughly
4. ✅ Update workflows when UIs change
5. ✅ Share workflows with your team

---

## Summary

You've learned how to:
- ✅ Define exact UI paths in configuration files
- ✅ Use workflows without increasing context
- ✅ Add new apps and workflows
- ✅ Troubleshoot and optimize workflows
- ✅ Save tokens and time

**Key Takeaway**: Workflows are like giving the AI a cookbook. It doesn't need to memorize recipes (context), it just looks them up when needed (on-demand loading).

Happy automating! 🚀
