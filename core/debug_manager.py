
"""
Debug Management Module
Handles debugging, logging, and diagnostics
"""


class DebugManager:
    """Manages debugging, logging, and diagnostics"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def debug_component_status(self):
        """Debug component initialization status"""
        try:
            print("🔍 === COMPONENT STATUS DEBUG ===")
            components = {
                'config': self.main_window.config,
                'theme_manager': self.main_window.theme_manager,
                'left_panel': self.main_window.left_panel,
                'content_tabs': self.main_window.content_tabs,
                'canvas_manager': self.main_window.canvas_manager,
                'canvas_integrator': self.main_window.canvas_integrator,
                'building_generator': self.main_window.building_generator,
                'toolbar_manager': getattr(self.main_window, 'toolbar_manager', None)
            }
            
            for name, component in components.items():
                status = "✅" if component is not None else "❌"
                print(f"{status} {name}: {type(component).__name__ if component else 'None'}")
            
            print("🔍 === COMPONENT STATUS END ===")
        except Exception as e:
            print(f"❌ Error in component debug: {e}")
    
    def debug_signal_connections(self):
        """Debug signal connections"""
        try:
            print("🔍 === SIGNAL CONNECTIONS DEBUG ===")
            
            # Check left panel signals
            if self.main_window.left_panel:
                left_panel_signals = [
                    'snip_requested', 'search_location_requested', 'undo_requested',
                    'clear_drawing_requested', 'scale_changed', 'generate_model_requested'
                ]
                
                for signal_name in left_panel_signals:
                    has_signal = hasattr(self.main_window.left_panel, signal_name)
                    status = "✅" if has_signal else "❌"
                    print(f"{status} LeftPanel.{signal_name}")
            
            # Check content tabs signals
            if self.main_window.content_tabs:
                content_tab_signals = [
                    'snip_completed', 'building_generated', 'screenshot_captured'
                ]
                
                for signal_name in content_tab_signals:
                    has_signal = hasattr(self.main_window.content_tabs, signal_name)
                    status = "✅" if has_signal else "❌"
                    print(f"{status} ContentTabs.{signal_name}")
            
            # Check for DrawingTabPanel signals
            drawing_panel = self._find_drawing_tab_panel()
            if drawing_panel:
                drawing_signals = [
                    'generate_model_requested', 'scale_changed', 'angle_snap_toggled', 'clear_drawing_requested'
                ]
                
                for signal_name in drawing_signals:
                    has_signal = hasattr(drawing_panel, signal_name)
                    status = "✅" if has_signal else "❌"
                    print(f"{status} DrawingTabPanel.{signal_name}")
            
            print("🔍 === SIGNAL CONNECTIONS END ===")
        except Exception as e:
            print(f"❌ Error in signal debug: {e}")
    
    def _find_drawing_tab_panel(self):
        """Find the DrawingTabPanel widget in the UI hierarchy"""
        try:
            if self.main_window.content_tabs:
                # Method 1: Check if content_tabs has drawing_tab_panel attribute
                if hasattr(self.main_window.content_tabs, 'drawing_tab_panel'):
                    return self.main_window.content_tabs.drawing_tab_panel
                
                # Method 2: Search through tab widgets
                for i in range(self.main_window.content_tabs.count()):
                    tab_widget = self.main_window.content_tabs.widget(i)
                    if tab_widget:
                        # Check if the tab widget is DrawingTabPanel
                        if tab_widget.__class__.__name__ == 'DrawingTabPanel':
                            return tab_widget
                        
                        # Search children for DrawingTabPanel
                        drawing_panel = self._find_widget_by_class(tab_widget, 'DrawingTabPanel')
                        if drawing_panel:
                            return drawing_panel
            
            return None
        except Exception as e:
            print(f"❌ Error finding DrawingTabPanel: {e}")
            return None
    
    def _find_widget_by_class(self, parent, class_name):
        """Find widget by class name recursively"""
        try:
            from PyQt5.QtWidgets import QWidget
            
            if parent.__class__.__name__ == class_name:
                return parent
            
            for child in parent.findChildren(QWidget):
                if child.__class__.__name__ == class_name:
                    return child
            
            return None
        except Exception as e:
            return None
    
    def debug_workflow_state(self):
        """Debug workflow state"""
        try:
            if self.main_window.content_tabs:
                screenshot_taken = getattr(self.main_window.content_tabs, 'screenshot_taken', 'Not set')
                drawing_completed = getattr(self.main_window.content_tabs, 'drawing_completed', 'Not set')
                building_created = getattr(self.main_window.content_tabs, 'building_created', 'Not set')
                
                print(f"🔍 Workflow State Debug:")
                print(f"   Screenshot taken: {screenshot_taken}")
                print(f"   Drawing completed: {drawing_completed}")
                print(f"   Building created: {building_created}")
                
                # Check tab accessibility
                for i in range(self.main_window.content_tabs.count()):
                    tab_name = self.main_window.content_tabs.tabText(i)
                    accessible = self.main_window.content_tabs._is_tab_accessible(i) if hasattr(self.main_window.content_tabs, '_is_tab_accessible') else 'Unknown'
                    print(f"   Tab {i} ({tab_name}): {accessible}")
            
        except Exception as e:
            print(f"❌ Workflow debug failed: {e}")
    
    def debug_auto_switch(self):
        """Debug version of auto-switch with detailed logging"""
        try:
            print("🔍 === AUTO-SWITCH DEBUG START ===")
            print(f"🔄 Content tabs available: {self.main_window.content_tabs is not None}")
            
            if self.main_window.content_tabs:
                print(f"🔄 Current tab index: {self.main_window.content_tabs.currentIndex()}")
                print(f"🔄 Tab count: {self.main_window.content_tabs.count()}")
                
                # List all tabs
                for i in range(self.main_window.content_tabs.count()):
                    tab_text = self.main_window.content_tabs.tabText(i)
                    print(f"🔄 Tab {i}: {tab_text}")
                
                # Check workflow state
                if hasattr(self.main_window.content_tabs, 'screenshot_taken'):
                    print(f"🔄 Screenshot taken state: {self.main_window.content_tabs.screenshot_taken}")
                
                if hasattr(self.main_window.content_tabs, '_is_tab_accessible'):
                    drawing_accessible = self.main_window.content_tabs._is_tab_accessible(1)
                    print(f"🔄 Drawing tab accessible: {drawing_accessible}")
                
                # Attempt switch
                print("🔄 Attempting to switch to drawing tab...")
                switch_success = self.main_window.tab_manager.switch_to_drawing_tab_with_debug()
                print(f"🔄 Switch result: {switch_success}")
            else:
                print("❌ No content_tabs available for switching")
            
            print("🔍 === AUTO-SWITCH DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Error in debug auto-switch: {e}")
            import traceback
            traceback.print_exc()
    
    def debug_snip_completion(self, pixmap):
        """Debug snip completion process"""
        try:
            print("🔍 === SNIP COMPLETION DEBUG START ===")
            print(f"✂️ _on_snip_completed called with pixmap: {pixmap is not None}")
            print(f"✂️ Pixmap valid: {pixmap is not None and not pixmap.isNull()}")
            
            if pixmap and not pixmap.isNull():
                print(f"✂️ Pixmap size: {pixmap.size()}")
                
                # Step 1: Update ContentTabWidget workflow state
                print("🔄 Step 1: Updating ContentTabWidget workflow state...")
                if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'on_screenshot_taken'):
                    print("✂️ ContentTabWidget has on_screenshot_taken method")
                    success = self.main_window.content_tabs.on_screenshot_taken(pixmap)
                    print(f"📸 ContentTabWidget screenshot update result: {success}")
                else:
                    print("❌ ContentTabWidget missing or no on_screenshot_taken method")
                    if self.main_window.content_tabs:
                        available_methods = [attr for attr in dir(self.main_window.content_tabs) if not attr.startswith('_')]
                        print(f"Available methods: {available_methods}")
                
                # Step 2: Set background in drawing tab
                print("🔄 Step 2: Setting background in drawing tab...")
                bg_success = self.main_window.canvas_manager.process_captured_pixmap(pixmap)
                print(f"🖼️ Background setting result: {bg_success}")
                
                # Step 3: Show status message
                print("🔄 Step 3: Showing status message...")
                self.main_window.statusBar().showMessage("📸 Screenshot captured! Switching to Drawing tab...", 3000)
                
                # Step 4: Auto-switch to drawing tab
                print("🔄 Step 4: Starting auto-switch...")
                self.debug_auto_switch()
                
                # Step 5: Debug workflow state
                self.debug_workflow_state()
            else:
                print("❌ Invalid or null pixmap received")
            
            print("🔍 === SNIP COMPLETION DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Error in snip completion debug: {e}")
            import traceback
            traceback.print_exc()
