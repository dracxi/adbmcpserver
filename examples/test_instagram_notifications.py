#!/usr/bin/env python3
"""
Test Instagram Notifications Workflow
Demonstrates how to read Instagram notifications using the workflow
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
    
    print("=" * 60)
    print("Instagram Notifications Reader")
    print("=" * 60)
    
    # Execute the check_notifications workflow
    print("\nReading Instagram notifications...")
    print("-" * 60)
    
    result = await workflow_engine.execute_workflow(
        app_name="instagram",
        workflow_name="check_notifications"
    )
    
    if result['status'] == 'success':
        print("\n✅ Successfully read Instagram notifications!")
        print("\nWorkflow completed successfully.")
        
        # If there's screen text in the result, display it
        if 'screen_text' in result:
            print("\nNotifications found:")
            print("-" * 60)
            for line in result['screen_text']:
                print(f"  • {line}")
    else:
        print(f"\n❌ Failed to read notifications: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
