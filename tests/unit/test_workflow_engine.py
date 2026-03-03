"""Unit tests for Workflow Engine."""
import pytest
from unittest.mock import Mock, patch, mock_open
from mcp_server.workflow_engine import WorkflowEngine


class TestWorkflowEngine:
    """Test suite for Workflow Engine."""
    
    @pytest.fixture
    def workflow_engine(self):
        """Create workflow engine instance for testing."""
        return WorkflowEngine(workflow_file="test_workflows.yaml")
    
    @pytest.fixture
    def sample_workflow(self):
        """Sample workflow definition."""
        return {
            "whatsapp": {
                "package": "com.whatsapp",
                "workflows": {
                    "send_message": {
                        "steps": [
                            {
                                "action": "tap",
                                "selector": {"resource_id": "com.whatsapp:id/fab"}
                            },
                            {
                                "action": "type_text",
                                "input": "{message}"
                            }
                        ]
                    }
                }
            }
        }
    
    def test_init(self, workflow_engine):
        """Test workflow engine initialization."""
        assert workflow_engine.workflow_file == "test_workflows.yaml"
        assert workflow_engine.workflows is not None
    
    @patch('builtins.open', new_callable=mock_open, read_data="whatsapp:\n  package: com.whatsapp")
    @patch('yaml.safe_load')
    def test_load_workflows(self, mock_yaml, mock_file, workflow_engine, sample_workflow):
        """Test workflow loading from file."""
        mock_yaml.return_value = sample_workflow
        
        workflows = workflow_engine.load_workflows()
        
        assert "whatsapp" in workflows
        assert workflows["whatsapp"]["package"] == "com.whatsapp"
    
    def test_get_workflow(self, workflow_engine, sample_workflow):
        """Test retrieving a specific workflow."""
        workflow_engine.workflows = sample_workflow
        
        workflow = workflow_engine.get_workflow("whatsapp", "send_message")
        
        assert workflow is not None
        assert "steps" in workflow
        assert len(workflow["steps"]) == 2
    
    def test_get_workflow_not_found(self, workflow_engine):
        """Test retrieving non-existent workflow."""
        workflow_engine.workflows = {}
        
        workflow = workflow_engine.get_workflow("invalid_app", "invalid_workflow")
        
        assert workflow is None
    
    def test_list_workflows(self, workflow_engine, sample_workflow):
        """Test listing all available workflows."""
        workflow_engine.workflows = sample_workflow
        
        workflows = workflow_engine.list_workflows()
        
        assert "whatsapp" in workflows
        assert "send_message" in workflows["whatsapp"]
    
    def test_validate_workflow_valid(self, workflow_engine, sample_workflow):
        """Test validation of valid workflow."""
        workflow = sample_workflow["whatsapp"]["workflows"]["send_message"]
        
        is_valid = workflow_engine.validate_workflow(workflow)
        
        assert is_valid is True
    
    def test_validate_workflow_missing_steps(self, workflow_engine):
        """Test validation of workflow without steps."""
        workflow = {"description": "Test workflow"}
        
        is_valid = workflow_engine.validate_workflow(workflow)
        
        assert is_valid is False
    
    def test_validate_workflow_invalid_action(self, workflow_engine):
        """Test validation of workflow with invalid action."""
        workflow = {
            "steps": [
                {"action": "invalid_action", "selector": {}}
            ]
        }
        
        is_valid = workflow_engine.validate_workflow(workflow)
        
        assert is_valid is False
    
    def test_substitute_parameters(self, workflow_engine):
        """Test parameter substitution in workflow steps."""
        step = {
            "action": "type_text",
            "input": "{message}"
        }
        parameters = {"message": "Hello World"}
        
        substituted = workflow_engine.substitute_parameters(step, parameters)
        
        assert substituted["input"] == "Hello World"
    
    def test_substitute_parameters_missing(self, workflow_engine):
        """Test parameter substitution with missing parameter."""
        step = {
            "action": "type_text",
            "input": "{message}"
        }
        parameters = {}
        
        with pytest.raises(KeyError):
            workflow_engine.substitute_parameters(step, parameters)
    
    @patch('mcp_server.ui_controller.UIController')
    def test_execute_workflow(self, mock_ui, workflow_engine, sample_workflow):
        """Test workflow execution."""
        workflow_engine.workflows = sample_workflow
        mock_ui_instance = Mock()
        mock_ui.return_value = mock_ui_instance
        
        result = workflow_engine.execute_workflow(
            "whatsapp",
            "send_message",
            {"message": "Test"},
            mock_ui_instance
        )
        
        assert result["success"] is True
        assert result["steps_executed"] > 0
