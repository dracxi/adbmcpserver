"""
Workflow Engine for executing predefined app-specific workflows.
Reads from app_workflows.yaml to execute complex multi-step actions.
"""

import yaml
import time
from typing import Dict, Any, Optional, List
from pathlib import Path


class WorkflowEngine:
    """Execute predefined workflows from configuration files."""
    
    def __init__(self, ui_controller, config_path: str = "app_workflows.yaml"):
        self.ui_controller = ui_controller
        self.workflows = self._load_workflows(config_path)
    
    def _load_workflows(self, config_path: str) -> Dict[str, Any]:
        """Load workflow definitions from YAML file."""
        path = Path(config_path)
        if not path.exists():
            return {}
        
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def execute_workflow(
        self,
        app_name: str,
        workflow_name: str,
        parameters: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Execute a predefined workflow for an app.
        
        Args:
            app_name: Name of the app (e.g., 'whatsapp', 'instagram')
            workflow_name: Name of the workflow (e.g., 'send_message')
            parameters: Dictionary of parameters to substitute (e.g., {'contact_name': 'John', 'message': 'Hi'})
        
        Returns:
            Dictionary with execution results
        """
        # Get workflow definition
        if app_name not in self.workflows:
            return {
                "success": False,
                "error": f"No workflows defined for app: {app_name}"
            }
        
        app_config = self.workflows[app_name]
        if workflow_name not in app_config.get('workflows', {}):
            return {
                "success": False,
                "error": f"Workflow '{workflow_name}' not found for {app_name}"
            }
        
        workflow = app_config['workflows'][workflow_name]
        steps = workflow.get('steps', [])
        
        # Execute each step
        results = []
        for i, step in enumerate(steps):
            try:
                result = self._execute_step(step, parameters)
                results.append({
                    "step": i + 1,
                    "action": step.get('action'),
                    "success": result.get('success', True),
                    "details": result
                })
                
                if not result.get('success', True):
                    return {
                        "success": False,
                        "error": f"Step {i + 1} failed",
                        "step_results": results
                    }
            
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Step {i + 1} error: {str(e)}",
                    "step_results": results
                }
        
        return {
            "success": True,
            "message": f"Workflow '{workflow_name}' completed successfully",
            "steps_executed": len(results),
            "step_results": results
        }
    
    def _execute_step(self, step: Dict[str, Any], parameters: Dict[str, str]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        action = step.get('action')
        
        if action == 'tap':
            selector = self._substitute_parameters(step.get('selector', {}), parameters)
            return self.ui_controller.tap_element(**selector)
        
        elif action == 'type_text':
            selector = self._substitute_parameters(step.get('selector', {}), parameters)
            text = self._substitute_parameters(step.get('input', ''), parameters)
            return self.ui_controller.type_text(text=text, **selector)
        
        elif action == 'wait':
            duration = step.get('duration', 1)
            time.sleep(duration)
            return {"success": True, "waited": duration}
        
        elif action == 'swipe':
            return self.ui_controller.swipe(**step.get('coordinates', {}))
        
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _substitute_parameters(self, value: Any, parameters: Dict[str, str]) -> Any:
        """Substitute {parameter_name} placeholders with actual values."""
        if isinstance(value, str):
            for key, val in parameters.items():
                value = value.replace(f"{{{key}}}", val)
            return value
        
        elif isinstance(value, dict):
            return {k: self._substitute_parameters(v, parameters) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._substitute_parameters(item, parameters) for item in value]
        
        return value
    
    def list_available_workflows(self) -> Dict[str, List[str]]:
        """List all available workflows by app."""
        result = {}
        for app_name, app_config in self.workflows.items():
            workflows = list(app_config.get('workflows', {}).keys())
            result[app_name] = workflows
        return result
