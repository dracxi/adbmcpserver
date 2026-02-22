"""High-level app automation workflows."""

import logging
import time
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from mcp_server.ui_controller import UIController
from mcp_server.adb_controller import ADBController


logger = logging.getLogger("adb_mcp_server.workflow")


# App registry mapping friendly names to package IDs
APP_REGISTRY = {
    "instagram": "com.instagram.android",
    "whatsapp": "com.whatsapp",
    "telegram": "org.telegram.messenger",
    "gmail": "com.google.android.gm",
    "chrome": "com.android.chrome",
    "messages": "com.google.android.apps.messaging",
    "sms": "com.android.mms",
    "phone": "com.android.dialer",
    "contacts": "com.android.contacts",
    "settings": "com.android.settings",
}


@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    action: str
    parameters: Dict[str, Any]
    retry_on_failure: bool = True
    optional: bool = False


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    success: bool
    completed_steps: int
    total_steps: int
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Represents a multi-step workflow."""
    name: str
    steps: List[WorkflowStep]
    
    def execute(self, context: 'WorkflowContext') -> WorkflowResult:
        """Execute all steps in sequence."""
        completed = 0
        
        for i, step in enumerate(self.steps, 1):
            from mcp_server.utils.logging import log_workflow_step
            
            try:
                # Execute step action
                if step.action == "launch_app":
                    success = context.adb.launch_app(step.parameters['package'])
                elif step.action == "wait":
                    time.sleep(step.parameters.get('seconds', 1))
                    success = True
                elif step.action == "tap":
                    success = context.ui.click_element(**step.parameters)
                elif step.action == "type":
                    success = context.ui.type_into_element(**step.parameters)
                elif step.action == "wait_for_element":
                    element = context.ui.wait_for_element(**step.parameters)
                    success = element is not None
                else:
                    success = False
                
                if success:
                    completed += 1
                    log_workflow_step(self.name, i, len(self.steps), step.action, "completed")
                else:
                    if not step.optional:
                        log_workflow_step(self.name, i, len(self.steps), step.action, "failed")
                        return WorkflowResult(
                            success=False,
                            completed_steps=completed,
                            total_steps=len(self.steps),
                            error=f"Step {i} failed: {step.action}"
                        )
                    else:
                        log_workflow_step(self.name, i, len(self.steps), step.action, "skipped (optional)")
                
            except Exception as e:
                log_workflow_step(self.name, i, len(self.steps), step.action, f"error: {e}")
                if not step.optional:
                    return WorkflowResult(
                        success=False,
                        completed_steps=completed,
                        total_steps=len(self.steps),
                        error=str(e)
                    )
        
        return WorkflowResult(
            success=True,
            completed_steps=completed,
            total_steps=len(self.steps)
        )


@dataclass
class WorkflowContext:
    """Context passed through workflow execution."""
    ui: UIController
    adb: ADBController
    state: Dict[str, Any] = field(default_factory=dict)


class AppActions:
    """High-level app automation workflows."""
    
    def __init__(self, ui_controller: UIController, adb_controller: ADBController):
        """
        Initialize app actions.
        
        Args:
            ui_controller: UI controller instance
            adb_controller: ADB controller instance
        """
        self.ui = ui_controller
        self.adb = adb_controller
        self.workflows: Dict[str, Workflow] = {}
        self._register_workflows()
    
    def _register_workflows(self) -> None:
        """Register predefined workflows."""
        # Workflows are defined in specific methods
        pass
    
    def execute_workflow(self, workflow_name: str, **params) -> WorkflowResult:
        """
        Execute a named workflow.
        
        Args:
            workflow_name: Name of workflow to execute
            **params: Workflow parameters
            
        Returns:
            WorkflowResult with execution details
        """
        if workflow_name in self.workflows:
            context = WorkflowContext(ui=self.ui, adb=self.adb, state=params)
            return self.workflows[workflow_name].execute(context)
        else:
            return WorkflowResult(
                success=False,
                completed_steps=0,
                total_steps=0,
                error=f"Workflow not found: {workflow_name}"
            )
    
    def send_message_instagram(self, contact_name: str, message: str) -> WorkflowResult:
        """
        Send message on Instagram.
        
        Args:
            contact_name: Contact name to send to
            message: Message text
            
        Returns:
            WorkflowResult
        """
        steps = [
            WorkflowStep("launch_app", {"package": APP_REGISTRY["instagram"]}),
            WorkflowStep("wait", {"seconds": 3}),
            WorkflowStep("tap", {"content_desc": "Direct"}, optional=True),
            WorkflowStep("tap", {"content_desc": "Search"}, optional=True),
            WorkflowStep("wait", {"seconds": 1}),
            WorkflowStep("type", {"text": contact_name}),
            WorkflowStep("wait", {"seconds": 2}),
            WorkflowStep("tap", {"text": contact_name}),
            WorkflowStep("wait", {"seconds": 2}),
            WorkflowStep("tap", {"text": "Message"}),
            WorkflowStep("wait", {"seconds": 1}),
            WorkflowStep("type", {"text": message}),
            WorkflowStep("tap", {"content_desc": "Send"}),
        ]
        
        workflow = Workflow("instagram_send_message", steps)
        context = WorkflowContext(ui=self.ui, adb=self.adb)
        return workflow.execute(context)
    
    def send_message_whatsapp(self, contact_name: str, message: str) -> WorkflowResult:
        """
        Send message on WhatsApp.
        
        Args:
            contact_name: Contact name
            message: Message text
            
        Returns:
            WorkflowResult
        """
        steps = [
            WorkflowStep("launch_app", {"package": APP_REGISTRY["whatsapp"]}),
            WorkflowStep("wait", {"seconds": 2}),
            WorkflowStep("tap", {"content_desc": "Search"}),
            WorkflowStep("wait", {"seconds": 1}),
            WorkflowStep("type", {"text": contact_name}),
            WorkflowStep("wait", {"seconds": 2}),
            WorkflowStep("tap", {"text": contact_name}),
            WorkflowStep("wait", {"seconds": 1}),
            WorkflowStep("type", {"text": message}),
            WorkflowStep("tap", {"content_desc": "Send"}),
        ]
        
        workflow = Workflow("whatsapp_send_message", steps)
        context = WorkflowContext(ui=self.ui, adb=self.adb)
        return workflow.execute(context)
    
    def send_message_telegram(self, contact_name: str, message: str) -> WorkflowResult:
        """
        Send message on Telegram.
        
        Args:
            contact_name: Contact name
            message: Message text
            
        Returns:
            WorkflowResult
        """
        steps = [
            WorkflowStep("launch_app", {"package": APP_REGISTRY["telegram"]}),
            WorkflowStep("wait", {"seconds": 2}),
            WorkflowStep("tap", {"content_desc": "Search"}),
            WorkflowStep("wait", {"seconds": 1}),
            WorkflowStep("type", {"text": contact_name}),
            WorkflowStep("wait", {"seconds": 2}),
            WorkflowStep("tap", {"text": contact_name}),
            WorkflowStep("wait", {"seconds": 1}),
            WorkflowStep("type", {"text": message}),
            WorkflowStep("tap", {"content_desc": "Send"}),
        ]
        
        workflow = Workflow("telegram_send_message", steps)
        context = WorkflowContext(ui=self.ui, adb=self.adb)
        return workflow.execute(context)
    
    def open_app_by_name(self, app_name: str) -> WorkflowResult:
        """
        Open app by friendly name.
        
        Args:
            app_name: Friendly app name
            
        Returns:
            WorkflowResult
        """
        app_name_lower = app_name.lower()
        package = APP_REGISTRY.get(app_name_lower)
        
        if not package:
            return WorkflowResult(
                success=False,
                completed_steps=0,
                total_steps=1,
                error=f"Unknown app: {app_name}"
            )
        
        success = self.adb.launch_app(package)
        
        return WorkflowResult(
            success=success,
            completed_steps=1 if success else 0,
            total_steps=1,
            data={"package": package}
        )
    
    def search_in_app(self, query: str) -> WorkflowResult:
        """
        Search within current app.
        
        Args:
            query: Search query
            
        Returns:
            WorkflowResult
        """
        # Try common search patterns
        search_element = self.ui.find_element(content_desc="Search")
        if not search_element:
            search_element = self.ui.find_element(text="Search")
        
        if not search_element:
            return WorkflowResult(
                success=False,
                completed_steps=0,
                total_steps=2,
                error="Search element not found"
            )
        
        # Click search and type query
        self.ui.click_element(element=search_element)
        time.sleep(0.5)
        success = self.ui.type_into_element(query)
        
        return WorkflowResult(
            success=success,
            completed_steps=2 if success else 1,
            total_steps=2
        )
    
    def extract_otp_from_sms(self) -> WorkflowResult:
        """
        Extract OTP from SMS app.
        
        Returns:
            WorkflowResult with OTP in data
        """
        # Try to open messages app
        for package in [APP_REGISTRY["messages"], APP_REGISTRY["sms"]]:
            try:
                self.adb.launch_app(package)
                time.sleep(2)
                break
            except:
                continue
        
        # Get screen text
        hierarchy = self.ui.get_ui_hierarchy()
        all_text = " ".join([elem.text for elem in hierarchy.all_elements if elem.text])
        
        # Extract OTP using regex (4-8 digit sequences)
        otp_patterns = [
            r'\b(\d{6})\b',  # 6 digits
            r'\b(\d{4})\b',  # 4 digits
            r'\b(\d{8})\b',  # 8 digits
        ]
        
        for pattern in otp_patterns:
            match = re.search(pattern, all_text)
            if match:
                otp = match.group(1)
                logger.info(f"Extracted OTP: {otp}")
                return WorkflowResult(
                    success=True,
                    completed_steps=1,
                    total_steps=1,
                    data={"otp": otp}
                )
        
        return WorkflowResult(
            success=False,
            completed_steps=0,
            total_steps=1,
            error="No OTP found in messages"
        )
