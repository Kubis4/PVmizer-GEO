#!/usr/bin/env python3
"""
Content Tab Widget - Enhanced with workflow restrictions + DEBUGGING + RACE CONDITION FIXES
"""
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QMessageBox, QApplication
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap
import time
import pyvista as pv
from .maps_tab import MapsTab
from .drawing_tab import DrawingTab
from .model_tab import ModelTab

from utils.pyvista_integration import PyVistaIntegration
from utils.solar_event_handlers import SolarEventHandlers
from utils.snipping_manager import SnippingManager
from utils.tab_utilities import TabUtilities

class ContentTabWidget(QTabWidget):
    """Content Tab Widget with workflow-based tab restrictions + ENHANCED DEBUGGING + RACE CONDITION FIXES"""
    
    snip_completed = pyqtSignal(object)
    building_generated = pyqtSignal(object)
    sun_position_changed = pyqtSignal(float, float)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Workflow state tracking
        self.screenshot_taken = False
        self.drawing_completed = False
        self.building_created = False
        
        # Store the last valid tab index
        self.last_valid_tab = 0
        
        # Debug mode
        self.debug_mode = True
        
        # Auto-check timer for drawing completion
        self.drawing_check_timer = QTimer()
        self.drawing_check_timer.timeout.connect(self._auto_check_drawing_completion)
        self.drawing_check_timer.start(1000)  # Check every second
        
        # Initialize utility components
        self._initialize_utilities()
        
        # Create tabs
        self._create_tabs()
        
        # Connect signals
        self._connect_signals()
        
        # Setup tab change handling with restrictions
        self._setup_tab_restrictions()
        
        # Update initial tab states
        self._update_tab_accessibility()
        
        # Schedule debugging
        if self.debug_mode:
            QTimer.singleShot(2000, self._debug_workflow_state)
    
    def _initialize_utilities(self):
        """Initialize utility components"""
        try:
            self.pyvista_integration = PyVistaIntegration(self)
            if self.debug_mode:
                print("✅ PyVistaIntegration initialized")
        except Exception as e:
            self.pyvista_integration = None
            if self.debug_mode:
                print(f"❌ PyVistaIntegration failed: {e}")
            
        try:
            self.solar_handlers = SolarEventHandlers(self)
            if self.debug_mode:
                print("✅ SolarEventHandlers initialized")
        except Exception as e:
            self.solar_handlers = None
            if self.debug_mode:
                print(f"❌ SolarEventHandlers failed: {e}")
            
        try:
            self.snipping_manager = SnippingManager(self)
            if self.debug_mode:
                print("✅ SnippingManager initialized")
        except Exception as e:
            self.snipping_manager = None
            if self.debug_mode:
                print(f"❌ SnippingManager failed: {e}")
            
        try:
            self.tab_utilities = TabUtilities(self)
            if self.debug_mode:
                print("✅ TabUtilities initialized")
        except Exception as e:
            self.tab_utilities = None
            if self.debug_mode:
                print(f"❌ TabUtilities failed: {e}")
    
    def _create_tabs(self):
        """Create all tabs using separate classes"""
        # Maps Tab
        self.maps_tab = MapsTab(self.main_window)
        self.addTab(self.maps_tab, "🗺️ Google Maps")
        if self.debug_mode:
            print("✅ Maps tab created")
        
        # Drawing Tab
        self.drawing_tab = DrawingTab(self.main_window)
        self.addTab(self.drawing_tab, "✏️ Drawing")
        if self.debug_mode:
            print("✅ Drawing tab created")
        
        # Model Tab
        self.model_tab = ModelTab(self.main_window)
        self.addTab(self.model_tab, "🏗️ 3D Model")
        if self.debug_mode:
            print("✅ Model tab created")
    
    def _setup_tab_restrictions(self):
        """Setup tab access restrictions"""
        # Connect to tab bar clicked to intercept tab changes
        self.tabBar().tabBarClicked.connect(self._on_tab_clicked)
        
        # Connect to current changed for valid changes
        self.currentChanged.connect(self._on_tab_changed)
    
    def _connect_signals(self):
        """Connect signals between tabs and main widget - ENHANCED"""
        signal_count = 0
        
        # Maps tab signals
        if self.maps_tab:
            try:
                self.maps_tab.maps_loaded.connect(self._on_maps_loaded)
                signal_count += 1
                self.maps_tab.maps_error.connect(self._on_maps_error)
                signal_count += 1
                if self.debug_mode:
                    print("✅ Maps tab signals connected")
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Maps tab signals failed: {e}")
        
        # Drawing tab signals - ENHANCED WITH DEBUGGING
        if self.drawing_tab:
            try:
                # Check what signals are available
                available_signals = [attr for attr in dir(self.drawing_tab) 
                                   if attr.endswith('_ready') or attr.endswith('_completed') or attr.endswith('_error')]
                if self.debug_mode:
                    print(f"🔍 Drawing tab available signals: {available_signals}")
                
                # Connect standard signals
                if hasattr(self.drawing_tab, 'canvas_ready'):
                    self.drawing_tab.canvas_ready.connect(self._on_canvas_ready)
                    signal_count += 1
                    if self.debug_mode:
                        print("✅ Connected drawing_tab.canvas_ready")
                
                if hasattr(self.drawing_tab, 'canvas_error'):
                    self.drawing_tab.canvas_error.connect(self._on_canvas_error)
                    signal_count += 1
                    if self.debug_mode:
                        print("✅ Connected drawing_tab.canvas_error")
                
                if hasattr(self.drawing_tab, 'drawing_completed'):
                    self.drawing_tab.drawing_completed.connect(self._on_drawing_completed)
                    signal_count += 1
                    if self.debug_mode:
                        print("✅ Connected drawing_tab.drawing_completed")
                else:
                    if self.debug_mode:
                        print("⚠️ drawing_tab.drawing_completed signal NOT FOUND")
                
                # Try to connect additional signals that might indicate completion
                for signal_name in ['polygon_completed', 'boundary_completed', 'points_completed']:
                    if hasattr(self.drawing_tab, signal_name):
                        try:
                            signal = getattr(self.drawing_tab, signal_name)
                            signal.connect(self._on_drawing_completed_alternate)
                            signal_count += 1
                            if self.debug_mode:
                                print(f"✅ Connected alternate signal: {signal_name}")
                        except Exception as e:
                            if self.debug_mode:
                                print(f"❌ Failed to connect {signal_name}: {e}")
                
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Drawing tab signals failed: {e}")
        
        # Model tab signals
        if self.model_tab:
            try:
                if hasattr(self.model_tab, 'building_generated'):
                    self.model_tab.building_generated.connect(self._on_building_generated)
                    signal_count += 1
                if hasattr(self.model_tab, 'model_updated'):
                    self.model_tab.model_updated.connect(self._on_model_updated)
                    signal_count += 1
                if hasattr(self.model_tab, 'view_changed'):
                    self.model_tab.view_changed.connect(self._on_view_changed)
                    signal_count += 1
                if self.debug_mode:
                    print("✅ Model tab signals connected")
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Model tab signals failed: {e}")
        
        if self.debug_mode:
            print(f"📊 Total signals connected: {signal_count}")
    
    def _refresh_drawing_completion_state(self):
        """Refresh drawing completion state by checking current drawing status - ENHANCED DETECTION"""
        try:
            if not self.drawing_completed and self.drawing_tab:
                # Force check current drawing state
                points = self.get_drawing_points()
                
                if self.debug_mode:
                    print(f"🔄 Refreshing drawing state: {len(points) if points else 0} points")
                
                # Method 1: Check point count and basic completion
                if points and len(points) >= 3:
                    if self.debug_mode:
                        print(f"🔄 Found {len(points)} points, checking closure...")
                    
                    # Check if polygon is complete by closure
                    is_closed = self._is_polygon_closed(points)
                    if self.debug_mode:
                        print(f"🔄 Polygon closed: {is_closed}")
                    
                    # For now, consider any polygon with 3+ points as complete
                    # You can tighten this later by requiring closure
                    if len(points) >= 3:  # Accept any polygon with 3+ points
                        if self.debug_mode:
                            print(f"🔄 ✅ FORCING completion for {len(points)} points")
                        self.drawing_completed = True
                        self._update_tab_accessibility()
                        # Stop auto-check timer
                        if self.drawing_check_timer.isActive():
                            self.drawing_check_timer.stop()
                        
                        # Show status message
                        if hasattr(self.main_window, 'statusBar'):
                            self.main_window.statusBar().showMessage(
                                f"✅ Drawing completed with {len(points)} points! Model tab unlocked.", 3000
                            )
                        return
                
                # Method 2: Check if drawing tab reports completion
                if hasattr(self.drawing_tab, 'is_polygon_complete'):
                    try:
                        if self.drawing_tab.is_polygon_complete():
                            if self.debug_mode:
                                print("🔄 Found completion via is_polygon_complete()")
                            self.drawing_completed = True
                            self._update_tab_accessibility()
                            # Stop auto-check timer
                            if self.drawing_check_timer.isActive():
                                self.drawing_check_timer.stop()
                            return
                    except Exception as e:
                        if self.debug_mode:
                            print(f"🔄 is_polygon_complete() failed: {e}")
                
                # Method 3: Check completion attributes
                completion_attrs = ['is_complete', 'polygon_complete', 'drawing_finished']
                for attr in completion_attrs:
                    if hasattr(self.drawing_tab, attr):
                        try:
                            if getattr(self.drawing_tab, attr):
                                if self.debug_mode:
                                    print(f"🔄 Found completion via {attr}")
                                self.drawing_completed = True
                                self._update_tab_accessibility()
                                # Stop auto-check timer
                                if self.drawing_check_timer.isActive():
                                    self.drawing_check_timer.stop()
                                return
                        except Exception as e:
                            if self.debug_mode:
                                print(f"🔄 {attr} check failed: {e}")
                            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Error refreshing drawing state: {e}")

                                    
    def _auto_check_drawing_completion(self):
        """Auto-check if drawing is completed - FALLBACK MECHANISM"""
        try:
            if not self.drawing_completed and self.drawing_tab:
                # Method 1: Check if drawing tab has points
                points = self.get_drawing_points()
                if points and len(points) >= 3:
                    # Check if it's a closed polygon
                    if self._is_polygon_closed(points):
                        if self.debug_mode:
                            print(f"🔍 Auto-detected completed polygon with {len(points)} points")
                        self._force_drawing_completion(points)
                        return
                
                # Method 2: Check if drawing tab has completion status
                if hasattr(self.drawing_tab, 'is_polygon_complete'):
                    try:
                        if self.drawing_tab.is_polygon_complete():
                            if self.debug_mode:
                                print("🔍 Auto-detected polygon completion via is_polygon_complete()")
                            self._force_drawing_completion(points or [])
                            return
                    except:
                        pass
                
                # Method 3: Check for specific completion attributes
                completion_attrs = ['is_complete', 'polygon_complete', 'drawing_finished']
                for attr in completion_attrs:
                    if hasattr(self.drawing_tab, attr):
                        try:
                            if getattr(self.drawing_tab, attr):
                                if self.debug_mode:
                                    print(f"🔍 Auto-detected completion via {attr}")
                                self._force_drawing_completion(points or [])
                                return
                        except:
                            pass
                            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Auto-check drawing completion failed: {e}")
    
    def _is_polygon_closed(self, points):
        """Check if polygon is closed (first and last points are close) - FIXED"""
        try:
            if len(points) < 3:
                return False
            
            # For debug purposes, let's see the actual points
            if self.debug_mode:
                print(f"🔄 Checking closure for {len(points)} points:")
                print(f"   First point: {points[0]}")
                print(f"   Last point: {points[-1]}")
            
            first_point = points[0]
            last_point = points[-1]
            
            # 🔧 FIX: Properly access QPointF coordinates
            if hasattr(first_point, 'x') and hasattr(first_point, 'y'):
                # QPointF objects
                dx = first_point.x() - last_point.x()
                dy = first_point.y() - last_point.y()
            elif isinstance(first_point, (list, tuple)) and len(first_point) >= 2:
                # List/tuple coordinates
                dx = first_point[0] - last_point[0]
                dy = first_point[1] - last_point[1]
            else:
                # Try to handle other formats
                try:
                    dx = float(first_point[0]) - float(last_point[0])
                    dy = float(first_point[1]) - float(last_point[1])
                except:
                    if self.debug_mode:
                        print(f"⚠️ Unknown point format: {type(first_point)}")
                    return False
            
            distance = (dx*dx + dy*dy) ** 0.5
            
            if self.debug_mode:
                print(f"   Distance: {distance:.2f} pixels")
            
            # Consider closed if distance is less than 30 pixels (more lenient)
            is_closed = distance < 30
            
            if self.debug_mode:
                print(f"   Is closed (< 30px): {is_closed}")
            
            return is_closed
            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Error checking polygon closure: {e}")
            return False
    
    def _force_drawing_completion(self, points):
        """Force drawing completion - MANUAL TRIGGER"""
        try:
            if self.debug_mode:
                print(f"🔧 FORCING drawing completion with {len(points)} points")
            
            self.drawing_completed = True
            self._update_tab_accessibility()
            
            # Show completion message
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "✅ Drawing auto-detected as completed! You can now access the 3D Model tab.", 3000
                )
            
            # Stop the auto-check timer
            if self.drawing_check_timer.isActive():
                self.drawing_check_timer.stop()
                
            if self.debug_mode:
                print("✅ Drawing completion forced successfully")
                
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Force drawing completion failed: {e}")
    
    def _on_tab_clicked(self, index):
        """Handle tab click with restrictions - ENHANCED WITH RETRY LOGIC"""
        try:
            if self.debug_mode:
                print(f"🔍 Tab {index} clicked")
                print(f"   Current workflow state:")
                print(f"   - Screenshot taken: {self.screenshot_taken}")
                print(f"   - Drawing completed: {self.drawing_completed}")
                print(f"   - Building created: {self.building_created}")
            
            # 🔧 FIX: For model tab, force refresh state and retry if not accessible
            if index == 2:
                # Force refresh drawing completion state
                self._refresh_drawing_completion_state()
                
                # Check again after refresh
                if not self._is_tab_accessible(index):
                    if self.debug_mode:
                        print("🔄 Model tab not immediately accessible, retrying in 100ms...")
                    
                    # Retry after short delay to allow signal processing
                    def retry_access():
                        self._refresh_drawing_completion_state()
                        if self._is_tab_accessible(index):
                            if self.debug_mode:
                                print("✅ Model tab accessible after retry")
                            # Switch to the tab directly
                            self.setCurrentIndex(index)
                            return
                        else:
                            if self.debug_mode:
                                print("❌ Model tab still not accessible after retry")
                            self._show_access_denied_message(index)
                    
                    QTimer.singleShot(100, retry_access)
                    return
            
            # Normal accessibility check for other tabs
            if not self._is_tab_accessible(index):
                if self.debug_mode:
                    print(f"❌ Tab {index} access denied")
                self._show_access_denied_message(index)
                return
            
            if self.debug_mode:
                print(f"✅ Tab {index} access allowed")
            
        except Exception as e:
            print(f"Error in tab click handler: {e}")
    
    def _is_tab_accessible(self, index):
        """Check if tab is accessible based on workflow state - ENHANCED WITH STATE REFRESH"""
        if index == 0:  # Maps tab - always accessible
            return True
        elif index == 1:  # Drawing tab - requires screenshot
            return self.screenshot_taken
        elif index == 2:  # Model tab - requires drawing completion
            # 🔧 FIX: For model tab requests, force refresh drawing state first
            if not self.drawing_completed:
                self._refresh_drawing_completion_state()
            
            accessible = self.screenshot_taken and self.drawing_completed
            if self.debug_mode and not accessible:
                print(f"🔍 Model tab not accessible:")
                print(f"   - Screenshot taken: {self.screenshot_taken}")
                print(f"   - Drawing completed: {self.drawing_completed}")
            return accessible
        
        return False
    
    def _show_access_denied_message(self, index):
        """Show appropriate message when tab access is denied - ENHANCED"""
        messages = {
            1: {
                "title": "Screenshot Required",
                "message": "Please take a screenshot from the Maps tab first.\n\n" +
                          "Steps:\n" +
                          "1\. Navigate to your building location\n" +
                          "2\. Click 'Snip Screenshot' button\n" +
                          "3\. Select the area to capture"
            },
            2: {
                "title": "Drawing Required", 
                "message": "Please complete the building drawing first.\n\n" +
                          "Steps:\n" +
                          "1\. Take a screenshot from Maps tab\n" +
                          "2\. Draw the building outline in Drawing tab\n" +
                          "3\. Complete the polygon to proceed\n\n" +
                          f"Current state:\n" +
                          f"• Screenshot taken: {'✅' if self.screenshot_taken else '❌'}\n" +
                          f"• Drawing completed: {'✅' if self.drawing_completed else '❌'}\n\n" +
                          "If you have completed the drawing but still can't access,\n" +
                          "try clicking 'Force Unlock' in the debug menu."
            }
        }
        
        if index in messages:
            msg = QMessageBox(self)
            msg.setWindowTitle(messages[index]["title"])
            msg.setText(messages[index]["message"])
            msg.setIcon(QMessageBox.Information)
            
            # Add debug buttons for model tab
            if index == 2 and self.debug_mode:
                force_unlock_btn = msg.addButton("Force Unlock (Debug)", QMessageBox.ActionRole)
                debug_btn = msg.addButton("Show Debug Info", QMessageBox.ActionRole)
                msg.addButton(QMessageBox.Ok)
                
                result = msg.exec_()
                
                # Handle button clicks
                if msg.clickedButton() == force_unlock_btn:
                    self._force_unlock_model_tab()
                elif msg.clickedButton() == debug_btn:
                    self._show_debug_info()
            else:
                msg.exec_()
    
    def _force_unlock_model_tab(self):
        """Force unlock model tab for debugging"""
        try:
            if self.debug_mode:
                print("🔧 FORCE UNLOCKING MODEL TAB")
                
            self.screenshot_taken = True
            self.drawing_completed = True
            self._update_tab_accessibility()
            
            # Switch to model tab
            self.setCurrentIndex(2)
            
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "🔧 Model tab force unlocked (Debug mode)", 3000
                )
                
            print("✅ Model tab force unlocked")
            
        except Exception as e:
            print(f"❌ Force unlock failed: {e}")
    
    def _show_debug_info(self):
        """Show detailed debug information"""
        try:
            points = self.get_drawing_points()
            
            debug_info = f"""DEBUG INFORMATION:
            
Workflow State:
• Screenshot taken: {self.screenshot_taken}
• Drawing completed: {self.drawing_completed}
• Building created: {self.building_created}

Drawing Tab Info:
• Points count: {len(points) if points else 0}
• Points: {points[:3] if points else 'None'}...
• Drawing tab type: {type(self.drawing_tab).__name__}

Available Methods:
• has is_polygon_complete: {hasattr(self.drawing_tab, 'is_polygon_complete')}
• has drawing_completed signal: {hasattr(self.drawing_tab, 'drawing_completed')}
• has get_drawing_points: {hasattr(self.drawing_tab, 'get_drawing_points')}

Tab Accessibility:
• Maps tab (0): {self._is_tab_accessible(0)}
• Drawing tab (1): {self._is_tab_accessible(1)}
• Model tab (2): {self._is_tab_accessible(2)}
"""
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Debug Information")
            msg.setText(debug_info)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
        except Exception as e:
            print(f"❌ Debug info failed: {e}")
    
    def _update_tab_accessibility(self):
        """Update tab visual states based on accessibility"""
        try:
            # Update tab tooltips and styles
            for i in range(self.count()):
                if self._is_tab_accessible(i):
                    # Accessible tab
                    self.setTabEnabled(i, True)
                    if i == 1:
                        self.setTabToolTip(i, "Drawing tab - Click to draw building outline")
                    elif i == 2:
                        self.setTabToolTip(i, "3D Model tab - View and export your building")
                else:
                    # Restricted tab - show but with tooltip
                    self.setTabEnabled(i, True)  # Keep enabled for click handling
                    if i == 1:
                        self.setTabToolTip(i, "⚠️ Requires screenshot from Maps tab")
                    elif i == 2:
                        self.setTabToolTip(i, "⚠️ Requires completed drawing")
                        
        except Exception as e:
            print(f"Error updating tab accessibility: {e}")
    
    def _on_tab_changed(self, index):
        """Handle valid tab change"""
        try:
            if self.debug_mode:
                print(f"🔍 Tab changed to {index}")
            
            # Only proceed if tab is accessible
            if not self._is_tab_accessible(index):
                # Revert to last valid tab
                self.blockSignals(True)
                self.setCurrentIndex(self.last_valid_tab)
                self.blockSignals(False)
                if self.debug_mode:
                    print(f"❌ Tab {index} not accessible, reverted to {self.last_valid_tab}")
                return
            
            # Update last valid tab
            self.last_valid_tab = index
            
            # Update left panel content
            if hasattr(self.main_window, 'left_panel'):
                self.main_window.left_panel.switch_to_tab_content(index)
            
            # Status messages
            tab_messages = [
                "📍 Navigate to a building and capture a screenshot",
                "✏️ Draw the building outline by clicking points", 
                "🏗️ Adjust building parameters and explore the 3D model"
            ]
            if index < len(tab_messages) and hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(tab_messages[index])
            
            # Special handling for model tab
            if index == 2 and self.model_tab:
                self.model_tab.refresh_view()
                        
        except Exception as e:
            print(f"Error in tab change handler: {e}")
    
    def _debug_workflow_state(self):
        """Debug current workflow state"""
        try:
            print("🔍 === WORKFLOW STATE DEBUG ===")
            print(f"Screenshot taken: {self.screenshot_taken}")
            print(f"Drawing completed: {self.drawing_completed}")
            print(f"Building created: {self.building_created}")
            print(f"Current tab: {self.currentIndex()}")
            
            # Check drawing points
            points = self.get_drawing_points()
            print(f"Drawing points: {len(points) if points else 0}")
            if points:
                print(f"First few points: {points[:3]}")
                print(f"Is polygon closed: {self._is_polygon_closed(points)}")
            
            # Check tab accessibility
            for i in range(self.count()):
                accessible = self._is_tab_accessible(i)
                tab_name = self.tabText(i)
                print(f"Tab {i} ({tab_name}): {'✅' if accessible else '❌'}")
            
            # Check drawing tab methods
            if self.drawing_tab:
                methods = ['is_polygon_complete', 'get_drawing_points', 'has_points']
                for method in methods:
                    has_method = hasattr(self.drawing_tab, method)
                    print(f"DrawingTab.{method}: {'✅' if has_method else '❌'}")
            
            print("🔍 === WORKFLOW STATE DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Workflow debug failed: {e}")
    
    # Signal handlers with state updates - ENHANCED
    def _on_maps_loaded(self):
        """Handle maps loaded"""
        if self.debug_mode:
            print("✅ Google Maps loaded successfully")
    
    def _on_maps_error(self, error):
        """Handle maps error"""
        if self.debug_mode:
            print(f"❌ Maps error: {error}")
    
    def _on_canvas_ready(self):
        """Handle canvas ready"""
        if self.debug_mode:
            print("✅ Drawing canvas ready")
    
    def _on_canvas_error(self, error):
        """Handle canvas error"""
        if self.debug_mode:
            print(f"❌ Canvas error: {error}")
    
    def _on_drawing_completed(self, points):
        """Handle drawing completion - ENHANCED WITH EXACT TIMING"""
        timestamp = time.time()
        
        if self.debug_mode:
            print(f"🎯 DRAWING COMPLETED SIGNAL at {timestamp:.3f} with {len(points)} points")
        
        self.drawing_completed = True
        self._update_tab_accessibility()
        
        # Stop auto-check timer
        if self.drawing_check_timer.isActive():
            self.drawing_check_timer.stop()
        
        # Show completion message
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(
                "✅ Drawing completed! You can now access the 3D Model tab.", 3000
            )
            
        if self.debug_mode:
            print(f"✅ Drawing completion processed at {time.time():.3f}")
    
    def _on_drawing_completed_alternate(self, *args):
        """Handle alternate drawing completion signals"""
        if self.debug_mode:
            print(f"🎯 ALTERNATE DRAWING COMPLETION SIGNAL with args: {args}")
        
        # Try to get points from arguments or drawing tab
        points = []
        for arg in args:
            if isinstance(arg, list) and len(arg) > 0:
                points = arg
                break
        
        if not points:
            points = self.get_drawing_points()
        
        self._on_drawing_completed(points)
    
    def _on_building_generated(self, building_info):
        """Handle building generation - FIXED RACE CONDITION"""
        try:
            if self.debug_mode:
                print("🎯 BUILDING GENERATED - Updating workflow state")
            
            # 🔧 FIX 1: Update workflow states FIRST
            self.drawing_completed = True
            self.building_created = True
            
            # Stop auto-check timer if running
            if hasattr(self, 'drawing_check_timer') and self.drawing_check_timer.isActive():
                self.drawing_check_timer.stop()
            
            # 🔧 FIX 2: Update tab accessibility and wait for propagation
            self._update_tab_accessibility()
            
            # 🔧 FIX 3: Use QTimer to ensure state propagation before tab switch
            def switch_to_model_tab_delayed():
                try:
                    # Double-check accessibility before switching
                    if self._is_tab_accessible(2):
                        self.setCurrentIndex(2)
                        if self.debug_mode:
                            print("✅ Successfully switched to model tab")
                    else:
                        if self.debug_mode:
                            print("❌ Model tab still not accessible after state update")
                            print(f"   - Screenshot taken: {self.screenshot_taken}")
                            print(f"   - Drawing completed: {self.drawing_completed}")
                            print(f"   - Building created: {self.building_created}")
                except Exception as e:
                    print(f"❌ Delayed tab switch failed: {e}")
            
            # Wait 100ms for state propagation
            QTimer.singleShot(100, switch_to_model_tab_delayed)
            
            # Emit the signal
            self.building_generated.emit(building_info)
            
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "🏗️ 3D building model generated successfully!", 5000
                )
            
            # Enable export button if available
            if (hasattr(self.main_window, 'left_panel') and 
                hasattr(self.main_window.left_panel, 'export_btn')):
                if self.main_window.left_panel.export_btn:
                    self.main_window.left_panel.export_btn.setEnabled(True)
            
            if self.debug_mode:
                print("✅ Workflow state updated after building generation")
                print(f"   - Drawing completed: {self.drawing_completed}")
                print(f"   - Building created: {self.building_created}")
            
        except Exception as e:
            print(f"Error handling building generation: {e}")
    
    def _on_model_updated(self, model_info):
        """Handle model update"""
        if self.debug_mode:
            print(f"✅ Model updated: {model_info}")
    
    def _on_view_changed(self, view_type):
        """Handle view change"""
        if self.debug_mode:
            print(f"✅ View changed to: {view_type}")
    
    # Add public method to manually mark drawing as complete
    def mark_drawing_completed(self, points=None):
        """Manually mark drawing as completed - PUBLIC METHOD"""
        try:
            if not points:
                points = self.get_drawing_points()
            
            if self.debug_mode:
                print(f"🔧 Manually marking drawing as completed with {len(points) if points else 0} points")
            
            self._force_drawing_completion(points or [])
            return True
            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Manual drawing completion failed: {e}")
            return False
    
    # Public API Methods with state updates
    def start_snipping(self):
        """Start screenshot snipping"""
        try:
            if self.snipping_manager:
                return self.snipping_manager.start_snipping()
            return False
        except Exception as e:
            return False
    
    def on_screenshot_taken(self, pixmap):
        """Called when screenshot is successfully taken"""
        try:
            if self.debug_mode:
                print("📸 Screenshot taken - updating workflow state")
                
            self.screenshot_taken = True
            self._update_tab_accessibility()
            
            # Show success message
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "📸 Screenshot captured! You can now access the Drawing tab.", 3000
                )
            
            # Set background in drawing tab
            if self.drawing_tab:
                self.drawing_tab.set_background_image(pixmap)
            
            return True
        except Exception as e:
            print(f"Error handling screenshot: {e}")
            return False
    
    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05):
        """Create 3D building - FIXED"""
        try:
            if self.model_tab:
                # 🔧 REMOVE source and emit_signal parameters
                success = self.model_tab.create_building(
                    points=points,
                    height=height,
                    roof_type=roof_type,
                    roof_pitch=roof_pitch,
                    scale=scale
                    # REMOVED: source=source, emit_signal=emit_signal
                )
                
                if success:
                    self.setCurrentIndex(2)  # Switch to model tab
                return success
            return False
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Error creating building: {e}")
            return False
    
    def set_drawing_background(self, pixmap):
        """Set background image for drawing and mark screenshot as taken"""
        try:
            if self.drawing_tab:
                success = self.drawing_tab.set_background_image(pixmap)
                if success:
                    self.screenshot_taken = True
                    self._update_tab_accessibility()
                return success
            return False
        except Exception as e:
            return False
    
    def get_drawing_points(self):
        """Get drawing points"""
        try:
            if self.drawing_tab:
                return self.drawing_tab.get_drawing_points()
            return []
        except Exception as e:
            return []
    
    def clear_drawing(self):
        """Clear drawing and reset completion state"""
        try:
            if self.drawing_tab:
                success = self.drawing_tab.clear_drawing()
                if success:
                    self.drawing_completed = False
                    self.building_created = False
                    self._update_tab_accessibility()
                    
                    # Restart auto-check timer
                    if not self.drawing_check_timer.isActive():
                        self.drawing_check_timer.start(1000)
                        
                return success
            return False
        except Exception as e:
            return False
    
    # Tab switching methods with validation
    def switch_to_maps_tab(self):
        """Switch to maps tab"""
        self.setCurrentIndex(0)
    
    def switch_to_drawing_tab(self):
        """Switch to drawing tab if accessible"""
        if self._is_tab_accessible(1):
            self.setCurrentIndex(1)
        else:
            self._show_access_denied_message(1)
    
    def switch_to_model_tab(self):
        """Switch to model tab if accessible - ENHANCED"""
        if self.debug_mode:
            print(f"🔍 Attempting to switch to model tab")
            print(f"   - Screenshot taken: {self.screenshot_taken}")
            print(f"   - Drawing completed: {self.drawing_completed}")
            print(f"   - Is accessible: {self._is_tab_accessible(2)}")
        
        if self._is_tab_accessible(2):
            self.setCurrentIndex(2)
            if self.debug_mode:
                print("✅ Model tab switch successful")
            return True
        else:
            if self.debug_mode:
                print("❌ Model tab not accessible, showing message")
            self._show_access_denied_message(2)
            return False
    
    # Utility methods
    def get_maps_tab(self):
        """Get maps tab"""
        return self.maps_tab
    
    def get_drawing_tab(self):
        """Get drawing tab"""
        return self.drawing_tab
    
    def get_model_tab(self):
        """Get model tab"""
        return self.model_tab
    
    def has_building(self):
        """Check if building exists"""
        try:
            if self.model_tab:
                return self.model_tab.has_building()
            return False
        except Exception as e:
            return False
    
    # State query methods
    def is_screenshot_taken(self):
        """Check if screenshot has been taken"""
        return self.screenshot_taken
    
    def is_drawing_completed(self):
        """Check if drawing has been completed"""
        return self.drawing_completed
    
    def is_building_created(self):
        """Check if building has been created"""
        return self.building_created
    
    def reset_workflow_state(self):
        """Reset all workflow states (useful for new project)"""
        self.screenshot_taken = False
        self.drawing_completed = False
        self.building_created = False
        self.last_valid_tab = 0
        self._update_tab_accessibility()
        self.setCurrentIndex(0)
        
        # Restart auto-check timer
        if not self.drawing_check_timer.isActive():
            self.drawing_check_timer.start(1000)
        
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage("Workflow reset. Start from Maps tab.", 2000)


    def render_roof_model(self, roof_type, dimensions):
        """Render the roof model in the 3D Model tab and switch to it"""
        print(f"🏗️ Rendering {roof_type} roof with dimensions: {dimensions}")

        # Switch to the 3D Model tab
        self.setCurrentIndex(self.indexOf(self.model_tab))

        # Use the ModelTab's methods to clear and initialize the scene
        self.model_tab.clear_model()

        # Create the roof model
        roof_model = self._create_roof_model(roof_type, dimensions)
        if roof_model:
            # Add the model to the 3D scene
            self.model_tab.plotter.add_mesh(roof_model, color='skyblue', name='roof_model', show_edges=True)
            self.model_tab.plotter.reset_camera()
            print(f"✅ {roof_type} roof rendered successfully")
        else:
            print(f"❌ Failed to create {roof_type} roof model")

    def _create_roof_model(self, roof_type, dimensions):
        """Create a 3D roof model using PyVista"""
        length, width, height = dimensions['length'], dimensions['width'], dimensions['height']

        if roof_type.lower() == "gable":
            # Define the points for the gable roof
            points = [
                [0, 0, 0],  # Bottom-left corner
                [length, 0, 0],  # Bottom-right corner
                [length / 2, width / 2, height],  # Peak of the roof
                [length, width, 0],  # Top-right corner
                [0, width, 0],  # Top-left corner
            ]

            # Define the faces
            faces = [
                3, 0, 1, 2,  # Front triangular face
                3, 1, 3, 2,  # Right triangular face
                3, 3, 4, 2,  # Back triangular face
                3, 4, 0, 2,  # Left triangular face
                4, 0, 1, 3, 4  # Base quadrilateral
            ]

            # Create the PolyData
            return pv.PolyData(points, faces)

        elif roof_type.lower() == "flat":
            # Example for flat roof
            points = [
                [0, 0, 0],
                [length, 0, 0],
                [length, width, 0],
                [0, width, 0],
                [0, 0, height],
                [length, 0, height],
                [length, width, height],
                [0, width, height],
            ]

            faces = [
                4, 0, 1, 2, 3,  # Base
                4, 4, 5, 6, 7,  # Top
                4, 0, 1, 5, 4,  # Front
                4, 1, 2, 6, 5,  # Right
                4, 2, 3, 7, 6,  # Back
                4, 3, 0, 4, 7,  # Left
            ]

            return pv.PolyData(points, faces)

        # Add other roof types (hip, pyramid, etc.) as needed

        else:
            print(f"❌ Unsupported roof type: {roof_type}")
            return None
        

        