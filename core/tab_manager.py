"""
Tab Management Module
Handles tab switching, finding, and accessibility management
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


class TabManager:
    """Manages tab operations and navigation"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def switch_to_drawing_tab_with_debug(self):
        """Switch to drawing tab with detailed debugging"""
        try:
            print("🔍 === TAB SWITCH DEBUG START ===")
            
            if not self.main_window.content_tabs:
                print("❌ No content_tabs available")
                return False
            
            # Check current state
            current_index = self.main_window.content_tabs.currentIndex()
            print(f"🔄 Current tab index: {current_index}")
            
            # Find drawing tab
            drawing_tab_index = self._find_drawing_tab_index()
            if drawing_tab_index is None:
                print("❌ Could not find drawing tab")
                return False
            
            # Check if tab is accessible
            if hasattr(self.main_window.content_tabs, '_is_tab_accessible'):
                accessible = self.main_window.content_tabs._is_tab_accessible(drawing_tab_index)
                print(f"🔄 Drawing tab accessible: {accessible}")
                
                if not accessible:
                    print("❌ Drawing tab is not accessible - checking workflow state")
                    self._debug_workflow_state()
                    return False
            
            # Attempt to switch
            success = self._perform_tab_switch(drawing_tab_index)
            
            if success:
                self._post_switch_actions()
            
            print("🔍 === TAB SWITCH DEBUG END ===")
            return success
            
        except Exception as e:
            print(f"❌ Error in tab switch: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def force_switch_to_model_tab(self):
        """Force switch to model tab with multiple methods"""
        try:
            print("🔄 === FORCE MODEL TAB SWITCH START ===")
            
            if not self.main_window.content_tabs:
                print("❌ No content_tabs available")
                return False
            
            # Get current state
            current_index = self.main_window.content_tabs.currentIndex()
            tab_count = self.main_window.content_tabs.count()
            print(f"🔄 Current tab: {current_index}, Total tabs: {tab_count}")
            
            # Method 1: Use ContentTabWidget's dedicated method
            if hasattr(self.main_window.content_tabs, 'switch_to_model_tab'):
                print("🔄 Trying ContentTabWidget.switch_to_model_tab()...")
                try:
                    result = self.main_window.content_tabs.switch_to_model_tab()
                    if result:
                        print("✅ Model tab switched via switch_to_model_tab()")
                        return True
                    else:
                        print("❌ switch_to_model_tab() returned False")
                except Exception as e:
                    print(f"❌ switch_to_model_tab() failed: {e}")
            
            # Method 2: Find model tab by name and switch
            model_tab_index = self._find_model_tab_index()
            if model_tab_index is not None:
                success = self._force_switch_to_index(model_tab_index)
                if success:
                    return True
            
            # Method 3: Force switch to last tab (often the model tab)
            last_tab_index = tab_count - 1
            if last_tab_index > 0:
                print(f"🔄 Trying to switch to last tab (index {last_tab_index})...")
                self.main_window.content_tabs.setCurrentIndex(last_tab_index)
                
                new_index = self.main_window.content_tabs.currentIndex()
                if new_index == last_tab_index:
                    print(f"✅ Switched to last tab (index {last_tab_index})")
                    return True
            
            print("❌ All model tab switch methods failed")
            return False
            
        except Exception as e:
            print(f"❌ Error in force model tab switch: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Add to the existing TabManager class:

    def handle_roof_button_click(self, roof_type):
        """Handle roof button click to show dialog and create roof"""
        try:
            print(f"🏠 Handling {roof_type} roof button click...")
            
            # IMPORTANT: Force enable model tab access BEFORE showing dialog
            self._force_enable_model_tab_for_roof()
            
            # Show roof dialog using the roof generation manager
            if hasattr(self.main_window, 'roof_generation_manager'):
                dialog_result = self.main_window.roof_generation_manager.show_roof_dialog(roof_type)
                
                if dialog_result:
                    print(f"✅ Roof dialog completed successfully")
                    return True
                else:
                    print("⚠️ Roof dialog was cancelled or failed")
                    return False
            else:
                print("❌ No roof_generation_manager available")
                return False
            
        except Exception as e:
            print(f"❌ Error handling roof button click: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _force_enable_model_tab_for_roof(self):
        """Force enable model tab specifically for roof generation"""
        try:
            print("🔧 FORCE ENABLING MODEL TAB FOR ROOF GENERATION")
            
            if hasattr(self.main_window, 'content_tabs'):
                content_tabs = self.main_window.content_tabs
                
                # Save original state to restore later if needed
                original_states = {
                    'screenshot_taken': getattr(content_tabs, 'screenshot_taken', False),
                    'drawing_completed': getattr(content_tabs, 'drawing_completed', False),
                    'building_created': getattr(content_tabs, 'building_created', False)
                }
                
                # Set all workflow state flags to True
                if hasattr(content_tabs, 'screenshot_taken'):
                    content_tabs.screenshot_taken = True
                
                if hasattr(content_tabs, 'drawing_completed'):
                    content_tabs.drawing_completed = True
                
                if hasattr(content_tabs, 'building_created'):
                    content_tabs.building_created = True
                
                # Update tab accessibility
                if hasattr(content_tabs, '_update_tab_accessibility'):
                    content_tabs._update_tab_accessibility()
                
                print("✅ Model tab forcibly enabled for roof generation")
                
                # Store original states in the content_tabs for potential restoration
                if not hasattr(content_tabs, '_original_workflow_states'):
                    content_tabs._original_workflow_states = original_states
            
        except Exception as e:
            print(f"❌ Error forcing model tab for roof: {e}")
            
    def _find_drawing_tab_index(self):
        """Find drawing tab index by searching tab names"""
        drawing_keywords = ['drawing', 'draw', '✏️']
        
        for i in range(self.main_window.content_tabs.count()):
            tab_text = self.main_window.content_tabs.tabText(i).lower()
            print(f"🔄 Checking tab {i}: '{tab_text}'")
            if any(keyword in tab_text for keyword in drawing_keywords):
                print(f"🎯 Found drawing tab at index: {i}")
                return i
        
        # Default assumption if no match found
        return 1 if self.main_window.content_tabs.count() > 1 else None
    
    def _find_model_tab_index(self):
        """Find the model tab index by searching tab names"""
        try:
            if not self.main_window.content_tabs:
                return None
            
            # Search for model-related keywords in tab names
            model_keywords = ['model', '3d', 'building', 'pyvista', 'render']
            
            for i in range(self.main_window.content_tabs.count()):
                tab_text = self.main_window.content_tabs.tabText(i).lower()
                print(f"🔄 Checking tab {i}: '{tab_text}'")
                
                for keyword in model_keywords:
                    if keyword in tab_text:
                        print(f"🎯 Found model tab at index {i} (keyword: '{keyword}')")
                        return i
            
            # If no keyword match, assume last tab is model tab
            last_index = self.main_window.content_tabs.count() - 1
            if last_index > 0:
                print(f"🎯 Assuming model tab is last tab (index {last_index})")
                return last_index
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding model tab index: {e}")
            return None
    
    def _perform_tab_switch(self, tab_index):
        """Perform actual tab switch"""
        current_index = self.main_window.content_tabs.currentIndex()
        print(f"🔄 Attempting to switch from {current_index} to {tab_index}")
        
        # Method 1: Use ContentTabWidget's switch method
        if hasattr(self.main_window.content_tabs, 'switch_to_drawing_tab'):
            print("🔄 Using switch_to_drawing_tab method...")
            success = self.main_window.content_tabs.switch_to_drawing_tab()
            print(f"✅ switch_to_drawing_tab result: {success}")
            if success:
                return True
        
        # Method 2: Direct index setting
        print("🔄 Using setCurrentIndex method...")
        self.main_window.content_tabs.setCurrentIndex(tab_index)
        
        # Verify switch
        new_index = self.main_window.content_tabs.currentIndex()
        print(f"🔄 New tab index: {new_index}")
        success = (new_index == tab_index)
        print(f"✅ Switch successful: {success}")
        
        return success
    
    def _force_switch_to_index(self, tab_index):
        """Force switch to specific tab index"""
        print(f"🔄 Found model tab at index: {tab_index}")
        
        # Check accessibility
        if hasattr(self.main_window.content_tabs, '_is_tab_accessible'):
            accessible = self.main_window.content_tabs._is_tab_accessible(tab_index)
            print(f"🔄 Model tab accessible: {accessible}")
            
            if not accessible:
                # Force enable the tab
                if hasattr(self.main_window.content_tabs, '_force_enable_tab'):
                    self.main_window.content_tabs._force_enable_tab(tab_index)
                    print("🔧 Forced model tab to be accessible")
                elif hasattr(self.main_window.content_tabs, 'building_created'):
                    self.main_window.content_tabs.building_created = True
                    print("🔧 Set building_created to True")
        
        # Switch to model tab
        self.main_window.content_tabs.setCurrentIndex(tab_index)
        
        # Verify switch
        new_index = self.main_window.content_tabs.currentIndex()
        if new_index == tab_index:
            print(f"✅ Successfully switched to model tab (index {tab_index})")
            
            # Force UI update
            self.main_window.content_tabs.update()
            self.main_window.content_tabs.repaint()
            QApplication.processEvents()
            
            return True
        else:
            print(f"❌ Tab switch failed: still at index {new_index}")
            return False
    
    def _post_switch_actions(self):
        """Actions to perform after successful tab switch"""
        try:
            # Update status message
            self.main_window.statusBar().showMessage("✅ Ready to draw! Trace the building outline.", 5000)
            
            # Update left panel if needed
            if hasattr(self.main_window.left_panel, 'switch_to_tab_content'):
                print("🔄 Updating left panel content...")
                self.main_window.left_panel.switch_to_tab_content(1)
            
            # Force UI update
            self.main_window.content_tabs.update()
            self.main_window.content_tabs.repaint()
            
        except Exception as e:
            print(f"❌ Error in post-switch actions: {e}")
    
    def _debug_workflow_state(self):
        """Debug workflow state for tab accessibility"""
        if hasattr(self.main_window.content_tabs, 'screenshot_taken'):
            print(f"📸 Screenshot taken: {self.main_window.content_tabs.screenshot_taken}")
        if hasattr(self.main_window.content_tabs, 'drawing_completed'):
            print(f"✏️ Drawing completed: {self.main_window.content_tabs.drawing_completed}")
    
    def debug_tab_switching(self):
        """Debug method to check tab switching capabilities"""
        try:
            print("🔍 === TAB SWITCHING DEBUG ===")
            
            if self.main_window.content_tabs:
                print(f"📊 Total tabs: {self.main_window.content_tabs.count()}")
                print(f"📊 Current tab: {self.main_window.content_tabs.currentIndex()}")
                
                # List all tabs
                for i in range(self.main_window.content_tabs.count()):
                    tab_text = self.main_window.content_tabs.tabText(i)
                    widget = self.main_window.content_tabs.widget(i)
                    widget_type = type(widget).__name__ if widget else "None"
                    
                    accessible = "Unknown"
                    if hasattr(self.main_window.content_tabs, '_is_tab_accessible'):
                        try:
                            accessible = self.main_window.content_tabs._is_tab_accessible(i)
                        except:
                            pass
                    
                    print(f"📋 Tab {i}: '{tab_text}' ({widget_type}) - Accessible: {accessible}")
                
                # Check workflow state
                if hasattr(self.main_window.content_tabs, 'screenshot_taken'):
                    print(f"📸 Screenshot taken: {self.main_window.content_tabs.screenshot_taken}")
                if hasattr(self.main_window.content_tabs, 'drawing_completed'):
                    print(f"✏️ Drawing completed: {self.main_window.content_tabs.drawing_completed}")
                if hasattr(self.main_window.content_tabs, 'building_created'):
                    print(f"🏗️ Building created: {self.main_window.content_tabs.building_created}")
            
            print("🔍 === TAB SWITCHING DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Tab switching debug failed: {e}")