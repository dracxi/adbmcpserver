"""
Example: Using Workflow System for WhatsApp Automation

This demonstrates how workflows eliminate the need for AI to explore UI every time.
"""

import asyncio
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.ui_controller import UIController
from mcp_server.adb_controller import ADBController


async def example_without_workflow():
    """Traditional approach: AI explores UI each time"""
    print("=== WITHOUT WORKFLOW (Slow, exploratory) ===\n")
    
    # AI would need to:
    # 1. Get screen structure
    # 2. Find the FAB button
    # 3. Click it
    # 4. Get new screen structure
    # 5. Find search field
    # 6. Type contact name
    # 7. Get screen structure again
    # 8. Find contact in results
    # 9. Click contact
    # 10. Get screen structure again
    # 11. Find message field
    # 12. Type message
    # 13. Find send button
    # 14. Click send
    
    print("Steps: 14+ tool calls")
    print("Time: 30-60 seconds")
    print("Context: Large (multiple screen structures)")
    print("Reliability: Medium (UI changes break it)")


async def example_with_workflow():
    """Workflow approach: AI uses predefined path"""
    print("\n=== WITH WORKFLOW (Fast, direct) ===\n")
    
    # Initialize workflow engine
    # In real usage, this is done automatically by MCP server
    workflow_engine = WorkflowEngine(None, "app_workflows.yaml")
    
    # Single tool call with all parameters
    result = workflow_engine.execute_workflow(
        app_name="whatsapp",
        workflow_name="send_message",
        parameters={
            "contact_name": "John Doe",
            "message": "Hey! How are you?"
        }
    )
    
    print("Steps: 1 tool call (execute_workflow)")
    print("Time: 5-10 seconds")
    print("Context: Minimal (just parameters)")
    print("Reliability: High (exact paths defined)")
    print(f"\nResult: {result}")


async def example_list_workflows():
    """List all available workflows"""
    print("\n=== AVAILABLE WORKFLOWS ===\n")
    
    workflow_engine = WorkflowEngine(None, "app_workflows.yaml")
    workflows = workflow_engine.list_available_workflows()
    
    for app_name, workflow_list in workflows.items():
        print(f"{app_name}:")
        for workflow in workflow_list:
            print(f"  - {workflow}")


async def example_custom_workflow():
    """Example: Adding a custom workflow for a new app"""
    print("\n=== CUSTOM WORKFLOW EXAMPLE ===\n")
    
    custom_workflow = """
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
"""
    
    print("To add Gmail support:")
    print("1. Add this to app_workflows.yaml:")
    print(custom_workflow)
    print("\n2. Use it:")
    print("""
    execute_workflow(
        app_name="gmail",
        workflow_name="send_email",
        parameters={
            "recipient": "john@example.com",
            "subject": "Meeting Tomorrow",
            "body": "Let's meet at 3pm"
        }
    )
    """)


async def main():
    """Run all examples"""
    await example_without_workflow()
    await example_with_workflow()
    await example_list_workflows()
    await example_custom_workflow()
    
    print("\n" + "="*50)
    print("KEY TAKEAWAY:")
    print("="*50)
    print("""
Workflows are like giving the AI a cookbook:
- Without workflow: AI figures out recipe each time (slow, error-prone)
- With workflow: AI follows exact recipe (fast, reliable)

The workflow file is NOT loaded into context every time.
It's only read when execute_workflow is called.
This means ZERO context overhead!
    """)


if __name__ == "__main__":
    asyncio.run(main())
