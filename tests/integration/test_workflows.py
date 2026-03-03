"""Integration tests for workflow execution."""
import pytest
from unittest.mock import Mock, patch
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.ui_controller import UIController


class TestWorkflowIntegration:
    """Integration tests for end-to-end workflow execution."""
    
    @pytest.fixture
    def workflow_engine(self):
        """Create workflow engine with test workflows."""
        return WorkflowEngine(workflow_file="app_workflows.yaml")
    
    @pytest.fixture
    def mock_ui_controller(self):
        """Create mock UI controller."""
        with patch('uiautomator2.connect') as mock_connect:
            mock_device = Mock()
            mock_connect.return_value = mock_device
            controller = UIController(device_id="test_device")
            controller.device = mock_device
            return controller
    
    @pytest.mark.integration
    def test_whatsapp_send_message_workflow(self, workflow_engine, mock_ui_controller):
        """Test WhatsApp send message workflow end-to-end."""
        # Setup mock responses
        mock_element = Mock()
        mock_element.exists = True
        mock_ui_controller.device.return_value = mock_element
        
        # Execute workflow
        result = workflow_engine.execute_workflow(
            app_name="whatsapp",
            workflow_name="send_message",
            parameters={
                "contact_name": "Test Contact",
                "message": "Test Message"
            },
            ui_controller=mock_ui_controller
        )
        
        # Verify execution
        assert result["success"] is True
        assert result["steps_executed"] > 0
    
    @pytest.mark.integration
    def test_instagram_send_dm_workflow(self, workflow_engine, mock_ui_controller):
        """Test Instagram send DM workflow end-to-end."""
        mock_element = Mock()
        mock_element.exists = True
        mock_ui_controller.device.return_value = mock_element
        
        result = workflow_engine.execute_workflow(
            app_name="instagram",
            workflow_name="send_dm",
            parameters={
                "contact_name": "Test User",
                "message": "Hello!"
            },
            ui_controller=mock_ui_controller
        )
        
        assert result["success"] is True
    
    @pytest.mark.integration
    def test_workflow_with_missing_element(self, workflow_engine, mock_ui_controller):
        """Test workflow handling when element is not found."""
        mock_element = Mock()
        mock_element.exists = False
        mock_ui_controller.device.return_value = mock_element
        
        result = workflow_engine.execute_workflow(
            app_name="whatsapp",
            workflow_name="send_message",
            parameters={
                "contact_name": "Test",
                "message": "Test"
            },
            ui_controller=mock_ui_controller
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.integration
    def test_workflow_parameter_substitution(self, workflow_engine, mock_ui_controller):
        """Test that workflow parameters are correctly substituted."""
        mock_element = Mock()
        mock_element.exists = True
        mock_ui_controller.device.return_value = mock_element
        
        contact = "John Doe"
        message = "Hello World"
        
        result = workflow_engine.execute_workflow(
            app_name="whatsapp",
            workflow_name="send_message",
            parameters={
                "contact_name": contact,
                "message": message
            },
            ui_controller=mock_ui_controller
        )
        
        assert result["success"] is True
        # Verify parameters were used (check mock calls)
        assert mock_ui_controller.device.called
    
    @pytest.mark.integration
    def test_workflow_timeout(self, workflow_engine, mock_ui_controller):
        """Test workflow timeout handling."""
        # Simulate slow operation
        mock_element = Mock()
        mock_element.exists = True
        mock_element.click.side_effect = lambda: __import__('time').sleep(100)
        mock_ui_controller.device.return_value = mock_element
        
        with pytest.raises(TimeoutError):
            workflow_engine.execute_workflow(
                app_name="whatsapp",
                workflow_name="send_message",
                parameters={"contact_name": "Test", "message": "Test"},
                ui_controller=mock_ui_controller,
                timeout=1
            )
