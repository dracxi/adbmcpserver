"""UI Controller for Android UI automation using uiautomator2."""

import logging
import time
import hashlib
from dataclasses import dataclass
from typing import Optional, List, Tuple
import uiautomator2 as u2
from mcp_server.adb_controller import ADBController


logger = logging.getLogger("adb_mcp_server.ui")


@dataclass
class UIElement:
    """Represents a UI element."""
    text: str
    content_desc: str
    resource_id: str
    class_name: str
    bounds: Tuple[int, int, int, int]  # (left, top, right, bottom)
    clickable: bool
    focusable: bool
    enabled: bool
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center coordinates of element."""
        left, top, right, bottom = self.bounds
        return ((left + right) // 2, (top + bottom) // 2)


@dataclass
class UIHierarchy:
    """Represents the UI hierarchy tree."""
    root: Optional[UIElement]
    all_elements: List[UIElement]
    actionable_elements: List[UIElement]


class UIController:
    """Handles UI hierarchy parsing and semantic interaction."""
    
    def __init__(self, device_id: str, adb_controller: ADBController):
        """
        Initialize UI controller.
        
        Args:
            device_id: Device identifier
            adb_controller: ADB controller instance
        """
        self.device_id = device_id
        self.adb = adb_controller
        self.device = u2.connect(device_id)
        self.element_cache: dict = {}
        self.cache_screen_hash: Optional[str] = None
        
        logger.info(f"Initialized UI controller for device: {device_id}")
    
    def get_ui_hierarchy(self) -> UIHierarchy:
        """
        Retrieve and parse current UI hierarchy.
        
        Returns:
            UIHierarchy with parsed elements
        """
        try:
            # Get XML hierarchy from device
            xml_hierarchy = self.device.dump_hierarchy()
            
            # Parse elements from XML
            all_elements = self._parse_hierarchy_xml(xml_hierarchy)
            
            # Filter actionable elements
            actionable = [
                elem for elem in all_elements
                if elem.clickable or elem.focusable or elem.text or elem.content_desc
            ]
            
            root = all_elements[0] if all_elements else None
            
            return UIHierarchy(
                root=root,
                all_elements=all_elements,
                actionable_elements=actionable
            )
            
        except Exception as e:
            logger.error(f"Failed to get UI hierarchy: {e}")
            return UIHierarchy(root=None, all_elements=[], actionable_elements=[])
    
    def _parse_hierarchy_xml(self, xml_str: str) -> List[UIElement]:
        """
        Parse UI elements from XML hierarchy.
        
        Args:
            xml_str: XML hierarchy string
            
        Returns:
            List of UIElement objects
        """
        import xml.etree.ElementTree as ET
        
        elements = []
        
        try:
            root = ET.fromstring(xml_str)
            
            def parse_node(node):
                # Extract attributes
                text = node.get('text', '')
                content_desc = node.get('content-desc', '')
                resource_id = node.get('resource-id', '')
                class_name = node.get('class', '')
                clickable = node.get('clickable', 'false') == 'true'
                focusable = node.get('focusable', 'false') == 'true'
                enabled = node.get('enabled', 'true') == 'true'
                
                # Parse bounds [left,top][right,bottom]
                bounds_str = node.get('bounds', '[0,0][0,0]')
                try:
                    parts = bounds_str.replace('][', ',').strip('[]').split(',')
                    bounds = tuple(map(int, parts))
                except:
                    bounds = (0, 0, 0, 0)
                
                element = UIElement(
                    text=text,
                    content_desc=content_desc,
                    resource_id=resource_id,
                    class_name=class_name,
                    bounds=bounds,
                    clickable=clickable,
                    focusable=focusable,
                    enabled=enabled
                )
                
                elements.append(element)
                
                # Recursively parse children
                for child in node:
                    parse_node(child)
            
            parse_node(root)
            
        except Exception as e:
            logger.error(f"Failed to parse XML hierarchy: {e}")
        
        return elements
    
    def find_elements(
        self,
        text: Optional[str] = None,
        content_desc: Optional[str] = None,
        resource_id: Optional[str] = None,
        class_name: Optional[str] = None
    ) -> List[UIElement]:
        """
        Find elements matching criteria.
        
        Args:
            text: Text to match
            content_desc: Content description to match
            resource_id: Resource ID to match
            class_name: Class name to match
            
        Returns:
            List of matching UIElement objects
        """
        hierarchy = self.get_ui_hierarchy()
        matches = []
        
        for element in hierarchy.all_elements:
            if text and element.text != text:
                continue
            if content_desc and element.content_desc != content_desc:
                continue
            if resource_id and element.resource_id != resource_id:
                continue
            if class_name and element.class_name != class_name:
                continue
            
            matches.append(element)
        
        logger.debug(f"Found {len(matches)} elements matching criteria")
        return matches
    
    def find_element(self, **criteria) -> Optional[UIElement]:
        """
        Find single element (returns first match).
        
        Args:
            **criteria: Element search criteria
            
        Returns:
            First matching UIElement or None
        """
        elements = self.find_elements(**criteria)
        return elements[0] if elements else None
    
    def click_element(
        self,
        element: Optional[UIElement] = None,
        **criteria
    ) -> bool:
        """
        Click element by reference or criteria.
        
        Args:
            element: UIElement to click (or use criteria)
            **criteria: Element search criteria if element not provided
            
        Returns:
            True if click succeeded
        """
        start_time = time.time()
        
        try:
            if element is None:
                element = self.find_element(**criteria)
            
            if element is None:
                logger.error(f"Element not found for click: {criteria}")
                return False
            
            # Click at element center
            x, y = element.center
            success = self.adb.input_tap(x, y)
            
            duration = time.time() - start_time
            from mcp_server.utils.logging import log_ui_interaction
            log_ui_interaction(
                "click",
                {"text": element.text, "content_desc": element.content_desc},
                "success" if success else "failed",
                duration
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    def type_into_element(
        self,
        text: str,
        element: Optional[UIElement] = None,
        **criteria
    ) -> bool:
        """
        Type text into element.
        
        Args:
            text: Text to type
            element: UIElement to type into (or use criteria)
            **criteria: Element search criteria if element not provided
            
        Returns:
            True if typing succeeded
        """
        try:
            # Click element first to focus
            if element is None:
                element = self.find_element(**criteria)
            
            if element is None:
                logger.error(f"Element not found for typing: {criteria}")
                return False
            
            # Click to focus
            self.click_element(element=element)
            time.sleep(0.3)  # Wait for focus
            
            # Type text
            success = self.adb.input_text(text)
            
            from mcp_server.utils.logging import log_ui_interaction
            log_ui_interaction(
                "type",
                {"text": element.text, "content_desc": element.content_desc},
                f"typed: {text}" if success else "failed"
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return False
    
    def scroll(self, direction: str = "down", steps: int = 1) -> bool:
        """
        Scroll in specified direction.
        
        Args:
            direction: Scroll direction (up, down, left, right)
            steps: Number of scroll steps
            
        Returns:
            True if scroll succeeded
        """
        try:
            # Get screen dimensions
            info = self.device.info
            width = info.get('displayWidth', 1080)
            height = info.get('displayHeight', 1920)
            
            # Calculate scroll coordinates
            center_x = width // 2
            center_y = height // 2
            scroll_distance = height // 3
            
            for _ in range(steps):
                if direction == "down":
                    self.adb.input_swipe(center_x, center_y + scroll_distance, 
                                        center_x, center_y - scroll_distance)
                elif direction == "up":
                    self.adb.input_swipe(center_x, center_y - scroll_distance,
                                        center_x, center_y + scroll_distance)
                elif direction == "left":
                    self.adb.input_swipe(center_x + scroll_distance, center_y,
                                        center_x - scroll_distance, center_y)
                elif direction == "right":
                    self.adb.input_swipe(center_x - scroll_distance, center_y,
                                        center_x + scroll_distance, center_y)
                
                time.sleep(0.5)  # Wait between scrolls
            
            logger.debug(f"Scrolled {direction} {steps} step(s)")
            return True
            
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    def wait_for_element(
        self,
        timeout: int = 10,
        **criteria
    ) -> Optional[UIElement]:
        """
        Wait for element to appear.
        
        Args:
            timeout: Maximum wait time in seconds
            **criteria: Element search criteria
            
        Returns:
            UIElement if found, None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            element = self.find_element(**criteria)
            if element:
                logger.debug(f"Element found after {time.time() - start_time:.2f}s")
                return element
            
            time.sleep(0.5)  # Poll every 500ms
        
        logger.warning(f"Element not found after {timeout}s timeout")
        return None
    
    def get_screen_structure(self, include_decorative: bool = False) -> dict:
        """
        Get structured representation of screen.
        
        Args:
            include_decorative: Whether to include decorative elements
            
        Returns:
            Dictionary with screen structure
        """
        hierarchy = self.get_ui_hierarchy()
        
        elements_to_include = (
            hierarchy.all_elements if include_decorative 
            else hierarchy.actionable_elements
        )
        
        # Get current app info
        try:
            current_app = self.device.app_current()
            app_package = current_app.get('package', 'unknown')
            activity = current_app.get('activity', 'unknown')
        except:
            app_package = 'unknown'
            activity = 'unknown'
        
        # Build structured representation
        elements = []
        for i, elem in enumerate(elements_to_include):
            elem_dict = {
                "id": f"elem_{i}",
                "type": self._classify_element_type(elem),
                "text": elem.text if elem.text else None,
                "description": elem.content_desc if elem.content_desc else None,
                "resource_id": elem.resource_id if elem.resource_id else None,
                "clickable": elem.clickable,
                "bounds": elem.bounds
            }
            elements.append(elem_dict)
        
        return {
            "app_package": app_package,
            "activity": activity,
            "elements": elements,
            "total_elements": len(elements)
        }
    
    def _classify_element_type(self, element: UIElement) -> str:
        """Classify element type based on class name."""
        class_name = element.class_name.lower()
        
        if 'button' in class_name:
            return 'button'
        elif 'edit' in class_name or 'input' in class_name:
            return 'text_field'
        elif 'text' in class_name:
            return 'text'
        elif 'image' in class_name:
            return 'image'
        else:
            return 'unknown'
    
    def invalidate_cache(self) -> None:
        """Clear element cache."""
        self.element_cache.clear()
        self.cache_screen_hash = None
        logger.debug("Element cache invalidated")
    
    def _calculate_screen_hash(self) -> str:
        """
        Calculate hash of current screen for cache invalidation.
        
        Returns:
            MD5 hash of screen hierarchy
        """
        try:
            xml_hierarchy = self.device.dump_hierarchy()
            return hashlib.md5(xml_hierarchy.encode()).hexdigest()
        except:
            return ""
    
    def _intelligent_match(self, criteria: dict) -> List[UIElement]:
        """
        Attempt intelligent matching with fallbacks.
        
        Args:
            criteria: Search criteria
            
        Returns:
            List of matching elements with confidence
        """
        # Try exact match first
        matches = self.find_elements(**criteria)
        if matches:
            return matches
        
        # Try partial text match
        if 'text' in criteria and criteria['text']:
            hierarchy = self.get_ui_hierarchy()
            partial_matches = [
                elem for elem in hierarchy.all_elements
                if criteria['text'].lower() in elem.text.lower()
            ]
            if partial_matches:
                logger.debug(f"Found {len(partial_matches)} partial text matches")
                return partial_matches
        
        # Try alternative attributes
        if 'resource_id' in criteria and criteria['resource_id']:
            # Try content_desc fallback
            hierarchy = self.get_ui_hierarchy()
            fallback_matches = [
                elem for elem in hierarchy.all_elements
                if elem.content_desc or elem.text
            ]
            if fallback_matches:
                logger.debug(f"Using fallback matching, found {len(fallback_matches)} candidates")
                return fallback_matches
        
        return []
