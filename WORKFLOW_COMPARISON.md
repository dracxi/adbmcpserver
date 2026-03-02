# Workflow System: Before vs After

## The Problem

When you say "Send a message to John on WhatsApp", the AI needs to:
1. Understand what you want
2. Figure out how to do it
3. Execute the steps

**Without workflows**, step 2 requires exploring the UI every single time.

---

## Before: Exploratory Approach

```
User: "Send 'Hi' to John on WhatsApp"

AI Process:
┌─────────────────────────────────────────┐
│ 1. open_app("whatsapp")                 │ ← 1 tool call
├─────────────────────────────────────────┤
│ 2. get_current_screen_structure()       │ ← 1 tool call
│    Returns: 50+ UI elements             │
├─────────────────────────────────────────┤
│ 3. Analyze structure, find FAB button   │ ← AI reasoning
├─────────────────────────────────────────┤
│ 4. tap(resource_id="...fab")            │ ← 1 tool call
├─────────────────────────────────────────┤
│ 5. get_current_screen_structure()       │ ← 1 tool call
│    Returns: 40+ UI elements             │
├─────────────────────────────────────────┤
│ 6. Find search field                    │ ← AI reasoning
├─────────────────────────────────────────┤
│ 7. type_text("John", element_id="...")  │ ← 1 tool call
├─────────────────────────────────────────┤
│ 8. wait(1)                              │ ← 1 tool call
├─────────────────────────────────────────┤
│ 9. get_current_screen_structure()       │ ← 1 tool call
│    Returns: 30+ UI elements             │
├─────────────────────────────────────────┤
│ 10. Find "John" in results              │ ← AI reasoning
├─────────────────────────────────────────┤
│ 11. tap(text="John")                    │ ← 1 tool call
├─────────────────────────────────────────┤
│ 12. get_current_screen_structure()      │ ← 1 tool call
│     Returns: 25+ UI elements            │
├─────────────────────────────────────────┤
│ 13. Find message input field            │ ← AI reasoning
├─────────────────────────────────────────┤
│ 14. type_text("Hi", element_id="...")   │ ← 1 tool call
├─────────────────────────────────────────┤
│ 15. Find send button                    │ ← AI reasoning
├─────────────────────────────────────────┤
│ 16. tap(resource_id="...send")          │ ← 1 tool call
└─────────────────────────────────────────┘

Total: 12+ tool calls
Time: 30-60 seconds
Context: ~500+ UI elements analyzed
Reliability: Medium (UI changes break it)
```

---

## After: Workflow Approach

```
User: "Send 'Hi' to John on WhatsApp"

AI Process:
┌─────────────────────────────────────────┐
│ execute_workflow(                       │ ← 1 tool call
│   app_name="whatsapp",                  │
│   workflow_name="send_message",         │
│   parameters={                          │
│     "contact_name": "John",             │
│     "message": "Hi"                     │
│   }                                     │
│ )                                       │
│                                         │
│ Workflow engine reads app_workflows.yaml│
│ and executes all steps automatically:   │
│   - Tap FAB                             │
│   - Type "John" in search               │
│   - Wait 1 second                       │
│   - Tap "John" in results               │
│   - Type "Hi" in message field          │
│   - Tap send button                     │
└─────────────────────────────────────────┘

Total: 1 tool call
Time: 5-10 seconds
Context: Just the parameters
Reliability: High (exact paths defined)
```

---

## Key Differences

| Aspect | Before (Exploratory) | After (Workflow) |
|--------|---------------------|------------------|
| **Tool Calls** | 12-15 | 1 |
| **Time** | 30-60 seconds | 5-10 seconds |
| **Context Size** | Large (500+ elements) | Minimal (parameters only) |
| **Tokens Used** | High | Very Low |
| **Reliability** | Medium | High |
| **Maintenance** | None needed | Update YAML if UI changes |
| **Reusability** | None | Works for all contacts/messages |

---

## How It Works

### 1. Define Once (in app_workflows.yaml)

```yaml
whatsapp:
  workflows:
    send_message:
      steps:
        - action: tap
          selector: {resource_id: "com.whatsapp:id/fab"}
        - action: type_text
          selector: {resource_id: "com.whatsapp:id/search_src_text"}
          input: "{contact_name}"
        - action: wait
          duration: 1
        - action: tap
          selector: {text: "{contact_name}"}
        - action: type_text
          selector: {resource_id: "com.whatsapp:id/entry"}
          input: "{message}"
        - action: tap
          selector: {resource_id: "com.whatsapp:id/send"}
```

### 2. Use Forever

```python
# Works for any contact, any message
execute_workflow("whatsapp", "send_message", {
    "contact_name": "John",
    "message": "Hi"
})

execute_workflow("whatsapp", "send_message", {
    "contact_name": "Sarah",
    "message": "See you tomorrow!"
})

execute_workflow("whatsapp", "send_message", {
    "contact_name": "Team",
    "message": "Meeting at 3pm"
})
```

---

## Context Overhead Comparison

### Before (Exploratory)
```
Every request includes:
- Current screen structure (100-200 tokens)
- Previous screen structures (300-600 tokens)
- AI reasoning about UI elements (200-400 tokens)
- Multiple tool call results (400-800 tokens)

Total per request: ~1000-2000 tokens
```

### After (Workflow)
```
Every request includes:
- Workflow name (5 tokens)
- Parameters (10-20 tokens)
- Result (50-100 tokens)

Total per request: ~65-125 tokens

Savings: 93-95% reduction in tokens!
```

---

## Real-World Impact

### Scenario: Send 10 messages in a conversation

**Before (Exploratory)**:
- Tool calls: 120-150
- Time: 5-10 minutes
- Tokens: 10,000-20,000
- Cost: $0.20-$0.40 (at $0.02/1K tokens)

**After (Workflow)**:
- Tool calls: 10
- Time: 1-2 minutes
- Tokens: 650-1,250
- Cost: $0.01-$0.03

**Improvement**: 10x faster, 15x fewer tokens, 10x cheaper

---

## When to Use Workflows

✅ **Use workflows for**:
- Repetitive tasks (sending messages, emails)
- Well-defined UI paths (login, navigation)
- Multi-step processes (checkout, form filling)
- Apps you use frequently

❌ **Don't use workflows for**:
- One-time exploratory tasks
- Dynamic/changing UIs
- Tasks requiring visual analysis
- Apps you rarely use

---

## Adding New Workflows

### Step 1: Explore UI Once
```python
get_current_screen_structure()
# Note down resource IDs, text, content descriptions
```

### Step 2: Define Workflow
```yaml
myapp:
  workflows:
    my_action:
      steps:
        - action: tap
          selector: {resource_id: "com.myapp:id/button"}
        - action: type_text
          input: "{param1}"
```

### Step 3: Use It
```python
execute_workflow("myapp", "my_action", {"param1": "value"})
```

### Step 4: Enjoy Forever
The AI now knows the exact path and will use it every time!

---

## Summary

Workflows transform your Android automation from:
- **Exploratory** (slow, token-heavy, unreliable)
- **Deterministic** (fast, token-efficient, reliable)

It's like giving the AI a GPS instead of making it explore the map every time.
