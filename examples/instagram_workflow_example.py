#!/usr/bin/env python3
"""
Instagram Workflow Examples
Demonstrates how to use Instagram workflows for common tasks
"""

import asyncio
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.device_manager import DeviceManager
from mcp_server.adb_controller import ADBController

async def main():
    # Initialize components
    device_manager = DeviceManager()
    adb = ADBController(device_manager)
    workflow_engine = WorkflowEngine(adb, workflow_file="app_workflows.yaml")
    
    print("Instagram Workflow Examples")
    print("=" * 50)
    
    # Example 1: Check Instagram messages
    print("\n1. Checking Instagram messages...")
    result = await workflow_engine.execute_workflow(
        app_name="instagram",
        workflow_name="check_messages"
    )
    print(f"Result: {result['status']}")
    if result['status'] == 'success':
        print("Messages checked successfully!")
    
    # Example 2: Send a direct message
    print("\n2. Sending a direct message...")
    result = await workflow_engine.execute_workflow(
        app_name="instagram",
        workflow_name="send_message",
        parameters={
            "contact_name": "john_doe",
            "message": "Hey! How are you doing?"
        }
    )
    print(f"Result: {result['status']}")
    if result['status'] == 'success':
        print("Message sent successfully!")
    
    # Example 3: Read a specific conversation
    print("\n3. Reading conversation with a contact...")
    result = await workflow_engine.execute_workflow(
        app_name="instagram",
        workflow_name="read_conversation",
        parameters={
            "contact_name": "jane_smith"
        }
    )
    print(f"Result: {result['status']}")
    if result['status'] == 'success':
        print("Conversation read successfully!")
    
    # Example 4: Check notifications
    print("\n4. Checking Instagram notifications...")
    result = await workflow_engine.execute_workflow(
        app_name="instagram",
        workflow_name="check_notifications"
    )
    print(f"Result: {result['status']}")
    if result['status'] == 'success':
        print("Notifications checked successfully!")
    
    # Example 5: Reply to a message
    print("\n5. Replying to a message...")
    result = await workflow_engine.execute_workflow(
        app_name="instagram",
        workflow_name="reply_to_message",
        parameters={
            "contact_name": "mike_wilson",
            "message": "Thanks for your message! I'll get back to you soon."
        }
    )
    print(f"Result: {result['status']}")
    if result['status'] == 'success':
        print("Reply sent successfully!")
    
    print("\n" + "=" * 50)
    print("All Instagram workflow examples completed!")

if __name__ == "__main__":
    asyncio.run(main())
