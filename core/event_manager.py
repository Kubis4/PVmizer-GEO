"""
Event Management Module
Handles event processing and routing
"""

import traceback
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer


class EventManager:
    """Manages event processing and routing"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def handle_snip_request(self):
        """Handle snip screenshot request"""
        try:
            print("🔧 Processing snip request...")
            
            # Method 1: Use content tabs snipping manager (PREFERRED)
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'snipping_manager'):
                snipping_manager = self.main_window.content_tabs.snipping_manager
                if hasattr(snipping_manager, 'start_snipping'):
                    print("📸 Using snipping manager")
                    result = snipping_manager.start_snipping()
                    if result:
                        print("✅ Snipping started successfully")
                        return
                    else:
                        print("❌ Snipping manager returned False")
            
            # Method 2: Try content tabs direct method
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'handle_snip_request'):
                print("📸 Using content tabs handle_snip_request")
                self.main_window.content_tabs.handle_snip_request()
                return
            
            # Method 3: Try content tabs screenshot method
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'start_screenshot'):
                print("📸 Using content tabs start_screenshot")
                self.main_window.content_tabs.start_screenshot()
                return
            
            # Fallback: Show unavailable message
            print("⚠️ No snipping method available")
            self._show_snip_unavailable_message()
            
        except Exception as e:
            print(f"❌ Snip request failed: {e}")
            traceback.print_exc()
            self._show_snip_unavailable_message()
    
    def handle_snip_completed(self, pixmap):
        """Handle snip completion"""
        try:
            # Use debug manager for detailed logging
            self.main_window.debug_manager.debug_snip_completion(pixmap)
            
            if pixmap and not pixmap.isNull():
                # Step 1: Update ContentTabWidget workflow state
                if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'on_screenshot_taken'):
                    self.main_window.content_tabs.on_screenshot_taken(pixmap)
                
                # Step 2: Set background in drawing tab
                self.main_window.canvas_manager.process_captured_pixmap(pixmap)
                
                # Step 3: Show status message
                self.main_window.statusBar().showMessage("📸 Screenshot captured! Switching to Drawing tab...", 3000)
                
                # Step 4: Auto-switch to drawing tab
                QTimer.singleShot(200, lambda: self.main_window.tab_manager.switch_to_drawing_tab_with_debug())
            else:
                print("❌ Invalid or null pixmap received")
            
        except Exception as e:
            print(f"❌ Error in snip completion: {e}")
            traceback.print_exc()
    
    def handle_search_location(self, location):
        """Handle search location request"""
        try:
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'search_location'):
                self.main_window.content_tabs.search_location(location)
        except Exception as e:
            print(f"❌ Search location failed: {e}")
    
    def handle_undo_request(self):
        """Handle undo request"""
        try:
            self.main_window.canvas_manager.undo_last_point()
        except Exception as e:
            print(f"❌ Undo failed: {e}")
    
    def handle_clear_request(self):
        """Handle clear drawing request"""
        try:
            self.main_window.canvas_manager.clear_drawing()
        except Exception as e:
            print(f"❌ Clear request failed: {e}")
    
    def handle_generate_building(self):
        """Handle generate building request"""
        try:
            print("🔧 Processing building generation request...")
            
            # Ensure building generator is ready
            if not self.main_window.building_manager.ensure_building_generator():
                self._show_error("Generator Error", "Could not initialize building generator")
                return
            
            points = self.main_window.canvas_manager.get_drawing_points()
            if not points or len(points) < 3:
                self._show_error("Generation Error", "Need at least 3 points to generate building")
                return
            
            settings = self.main_window.canvas_manager.get_building_settings()
            
            # Switch to model tab
            self.main_window.tab_manager.force_switch_to_model_tab()
            
            # Generate building
            QTimer.singleShot(100, lambda: self.main_window.building_manager.generate_building_with_settings(points, settings))
            
        except Exception as e:
            print(f"❌ Building generation failed: {e}")
            self._show_error("Generation Error", f"Failed to generate building: {str(e)}")
    
    def handle_generate_building_from_drawing_tab(self):
        """Handle generate building request from DrawingTabPanel"""
        try:
            print("🏗️ === GENERATE BUILDING FROM DRAWING TAB START ===")
            
            # Step 1: Get drawing points
            points = self.main_window.canvas_manager.get_drawing_points()
            print(f"🏗️ Drawing points count: {len(points) if points else 0}")
            
            if not points or len(points) < 3:
                print("❌ Insufficient points for building generation")
                self._show_error("Generation Error", 
                               "Need at least 3 points to generate building.\n\n"
                               "Please complete your building outline first.")
                return
            
            print(f"✅ Valid points found: {points[:3]}..." if len(points) > 3 else f"✅ Valid points: {points}")
            
            # Step 2: Get building settings
            settings = self.main_window.canvas_manager.get_building_settings()
            print(f"🏗️ Building settings: {settings}")
            
            # Step 3: FORCE switch to model tab BEFORE generation
            print("🔄 === SWITCHING TO MODEL TAB ===")
            model_tab_switched = self.main_window.tab_manager.force_switch_to_model_tab()
            
            if not model_tab_switched:
                print("⚠️ Model tab switch failed, but continuing with generation...")
            
            # Step 4: Update status
            self.main_window.statusBar().showMessage("🏗️ Generating 3D building model...", 5000)
            
            # Step 5: Generate building with delay to allow tab switch
            QTimer.singleShot(200, lambda: self.main_window.building_manager.generate_building_with_settings(points, settings))
            
            print("🏗️ === GENERATE BUILDING REQUEST PROCESSED ===")
            
        except Exception as e:
            print(f"❌ Error in generate building from drawing tab: {e}")
            traceback.print_exc()
            self._show_error("Generation Error", f"Failed to generate building: {str(e)}")
    
    def handle_building_generated(self, building_data=None):
        """Handle building generated signal"""
        try:
            self.main_window._building_generated = True
            
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'building_created'):
                self.main_window.content_tabs.building_created = True
                if hasattr(self.main_window.content_tabs, '_update_tab_accessibility'):
                    self.main_window.content_tabs._update_tab_accessibility()
            
            self.main_window.statusBar().showMessage("✅ 3D Building generated successfully!", 3000)
            print("✅ Building generated successfully")
            
        except Exception as e:
            print(f"❌ Building generated handler failed: {e}")
    
    def handle_solar_time_changed(self, hour):
        """Handle solar time changed signal"""
        try:
            # Implementation depends on your UI structure
            print(f"🔧 Solar time changed to: {hour}")
        except Exception as e:
            print(f"❌ Solar time handler failed: {e}")
    
    def handle_screenshot_captured(self, *args):
        """Handle screenshot captured"""
        try:
            pixmap = None
            for arg in args:
                if hasattr(arg, 'save'):  # QPixmap
                    pixmap = arg
                    break
            
            if pixmap:
                if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'on_screenshot_taken'):
                    self.main_window.content_tabs.on_screenshot_taken(pixmap)
                
                self.main_window.canvas_manager.process_captured_pixmap(pixmap)
            
            self.main_window.statusBar().showMessage("📸 Screenshot captured! Drawing tab is now available.", 3000)
            QTimer.singleShot(500, lambda: self.main_window.tab_manager.switch_to_drawing_tab_with_debug())
            
        except Exception as e:
            print(f"❌ Screenshot capture handler failed: {e}")
    
    def handle_boundary_completed(self, boundary_points):
        """Handle boundary completion WITHOUT auto-switching"""
        try:
            print(f"🎯 Boundary completed with {len(boundary_points)} points")
            
            self.main_window._current_drawing_points = boundary_points
            
            # Update ContentTabWidget workflow state
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, '_on_drawing_completed'):
                self.main_window.content_tabs._on_drawing_completed(boundary_points)
                print("✅ Updated ContentTabWidget drawing state")
            
            # Enable generate button in left panel
            if hasattr(self.main_window.left_panel, 'enable_generate_button'):
                self.main_window.left_panel.enable_generate_button()
                print("✅ Enabled generate button")
            
            # Update measurements
            self.main_window.canvas_manager.update_measurements(boundary_points)
            print(f"✅ Updated measurements")
            
        except Exception as e:
            print(f"❌ Boundary completion handler failed: {e}")
    
    def _show_snip_unavailable_message(self):
        """Show message when snipping tool is unavailable"""
        msg = QMessageBox(self.main_window)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Screenshot Tool")
        msg.setText("Screenshot tool is not available.")
        msg.setInformativeText(
            "Please use your system's screenshot tool and paste the image to the Drawing tab."
        )
        msg.exec_()
    
    def _show_error(self, title, message):
        """Show error message"""
        try:
            QMessageBox.warning(self.main_window, title, message)
        except Exception as e:
            print(f"❌ Could not show error dialog: {e}")

    def handle_roof_button_click(self, roof_type):
        """Handle roof button click to show dialog and create roof"""
        try:
            print(f"🏠 Handling {roof_type} roof button click...")
            
            # Force enable model tab access
            if hasattr(self.main_window, 'content_tabs'):
                # Try to use the force switch method if available
                if hasattr(self.main_window.content_tabs, 'force_switch_to_model_tab'):
                    # This method will be called after the dialog is accepted
                    print("✅ Force switch method available")
                else:
                    # Manually force enable the model tab
                    self._force_enable_model_tab()
            
            # Show roof dialog
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
        
    def handle_roof_generated(self, roof_object):
        """Handle when a roof is generated"""
        try:
            print(f"🏠 Roof generated: {type(roof_object).__name__}")
            
            # Update building generated state
            self.main_window._building_generated = True
            
            # Update ContentTabWidget state if available
            if hasattr(self.main_window, 'content_tabs') and self.main_window.content_tabs:
                if hasattr(self.main_window.content_tabs, 'building_created'):
                    self.main_window.content_tabs.building_created = True
                    
                if hasattr(self.main_window.content_tabs, '_update_tab_accessibility'):
                    self.main_window.content_tabs._update_tab_accessibility()
            
            # Show success message
            self.main_window.statusBar().showMessage("✅ 3D Roof model created successfully!", 3000)
            
        except Exception as e:
            print(f"❌ Roof generated handler failed: {e}")      