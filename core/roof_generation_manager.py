"""
Roof Generation Management Module
Handles roof model generation and 3D model display
"""

import os
import sys
import importlib
import traceback
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
import numpy as np

# Import your GableRoof class - with fallback handling
try:
    from roofs.concrete.gable_roof import GableRoof
    GABLE_ROOF_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import GableRoof from roofs.gable_roof")
    GABLE_ROOF_AVAILABLE = False
    GableRoof = None

# Try to import other roof types
try:
    from roofs.concrete.flat_roof import FlatRoof
    FLAT_ROOF_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import FlatRoof from roofs.flat_roof")
    FLAT_ROOF_AVAILABLE = False
    FlatRoof = None

try:
    from roofs.concrete.hip_roof import HipRoof
    HIP_ROOF_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import HipRoof from roofs.hip_roof")
    HIP_ROOF_AVAILABLE = False
    HipRoof = None

try:
    from roofs.concrete.pyramid_roof import PyramidRoof
    PYRAMID_ROOF_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import PyramidRoof from roofs.pyramid_roof")
    PYRAMID_ROOF_AVAILABLE = False
    PyramidRoof = None

# Import the existing roof dialog
try:
    from ui.dialogs.roof_dialog import RoofDimensionDialog
    ROOF_DIALOG_AVAILABLE = True
except ImportError:
    print("⚠️ Could not import RoofDimensionDialog from ui.dialogs.roof_dialog")
    ROOF_DIALOG_AVAILABLE = False


class RoofGenerationManager(QObject):
    """Manages roof generation and integration with roof algorithms"""
    
    # Signal to notify when a roof is generated
    roof_generated = pyqtSignal(object)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_roof = None
        self.plotter = None
        self.external_plotter = False
        self.roof_actors = []  # Keep track of actors added by the roof
        
        # Initialize PyVista plotter
        self._initialize_plotter()
    
    def _initialize_plotter(self):
        """Initialize PyVista plotter for 3D model display"""
        try:
            import pyvista as pv
            from pyvistaqt import QtInteractor
            
            print("✅ PyVista and PyVistaQt available for 3D visualization")
            self.pyvista_available = True
        except ImportError:
            print("⚠️ PyVista or PyVistaQt not available. 3D visualization will be limited.")
            self.pyvista_available = False
    
    def show_roof_dialog(self, roof_type):
        """Show roof dimension dialog for the specified roof type"""
        try:
            if not ROOF_DIALOG_AVAILABLE:
                print("❌ RoofDimensionDialog not available")
                self._show_error("Dialog Error", "Roof dialog component is not available.")
                return False
            
            print(f"🏠 Opening {roof_type} roof dialog...")
            
            # Create dialog
            dialog = RoofDimensionDialog(roof_type.title(), self.main_window)
            
            # Show dialog
            result = dialog.exec_()
            
            # Check result
            if result == dialog.Accepted and dialog.dimensions:
                print(f"✅ Roof dialog accepted with dimensions: {dialog.dimensions}")
                
                # IMPORTANT: Force enable model tab access BEFORE switching
                self._force_enable_model_tab()
                
                # Now switch to model tab (should work without restrictions)
                if hasattr(self.main_window, 'content_tabs'):
                    # Force current index directly without validation
                    self.main_window.content_tabs.blockSignals(True)
                    self.main_window.content_tabs.setCurrentIndex(2)  # Model tab index
                    self.main_window.content_tabs.blockSignals(False)
                    print("✅ Forced switch to model tab for roof generation")
                
                # Generate roof with the specified dimensions
                self.generate_roof(roof_type, dialog.dimensions)
                return True
            else:
                print("❌ Roof dialog cancelled or no dimensions provided")
                return False
            
        except Exception as e:
            print(f"❌ Error showing roof dialog: {e}")
            traceback.print_exc()
            self._show_error("Dialog Error", f"Error showing roof dialog: {str(e)}")
            return False
    
    def _force_enable_model_tab(self):
        """Force enable model tab access by setting all necessary workflow flags"""
        try:
            print("🔧 FORCE ENABLING MODEL TAB ACCESS FOR ROOF GENERATION")
            
            # Set main window flag
            self.main_window._building_generated = True
            
            # Set content tabs flags
            if hasattr(self.main_window, 'content_tabs'):
                content_tabs = self.main_window.content_tabs
                
                # Set all workflow state flags to True
                if hasattr(content_tabs, 'screenshot_taken'):
                    content_tabs.screenshot_taken = True
                
                if hasattr(content_tabs, 'drawing_completed'):
                    content_tabs.drawing_completed = True
                
                if hasattr(content_tabs, 'building_created'):
                    content_tabs.building_created = True
                
                # Update tab accessibility if method exists
                if hasattr(content_tabs, '_update_tab_accessibility'):
                    content_tabs._update_tab_accessibility()
                
                # Force unlock if method exists
                if hasattr(content_tabs, '_force_unlock_model_tab'):
                    content_tabs._force_unlock_model_tab()
                
                print("✅ Model tab access forcibly enabled for roof generation")
            
        except Exception as e:
            print(f"❌ Error forcing model tab access: {e}")
    
    def _clean_previous_roof(self):
        """Clean up previous roof instance if it exists - ENHANCED VERSION"""
        try:
            print("🧹 Cleaning up previous roof...")
            
            # STEP 1: Clean the current roof object
            if hasattr(self, 'current_roof') and self.current_roof:
                # Clean solar panels if handler exists
                if hasattr(self.current_roof, 'solar_panel_handler'):
                    try:
                        if hasattr(self.current_roof.solar_panel_handler, 'clear_panels'):
                            self.current_roof.solar_panel_handler.clear_panels()
                            print("✅ Cleared solar panels")
                        
                        # Detach solar panel handler
                        self.current_roof.solar_panel_handler = None
                    except Exception as e:
                        print(f"⚠️ Could not clear solar panels: {e}")
                
                # Clean obstacles
                if hasattr(self.current_roof, 'obstacles'):
                    try:
                        # Clear obstacles list
                        self.current_roof.obstacles = []
                        print("✅ Cleared obstacles list")
                    except Exception as e:
                        print(f"⚠️ Could not clear obstacles list: {e}")
                
                if hasattr(self.current_roof, 'clear_obstacles'):
                    try:
                        self.current_roof.clear_obstacles()
                        print("✅ Cleared obstacles")
                    except Exception as e:
                        print(f"⚠️ Could not clear obstacles: {e}")
                
                # Clean attachment points
                if hasattr(self.current_roof, 'attachment_points'):
                    try:
                        self.current_roof.attachment_points = []
                        print("✅ Cleared attachment points")
                    except Exception as e:
                        print(f"⚠️ Could not clear attachment points: {e}")
                
                if hasattr(self.current_roof, 'attachment_point_actor') and self.current_roof.attachment_point_actor:
                    try:
                        if hasattr(self.current_roof, 'plotter') and self.current_roof.plotter:
                            self.current_roof.plotter.remove_actor(self.current_roof.attachment_point_actor)
                        self.current_roof.attachment_point_actor = None
                        print("✅ Cleared attachment point actor")
                    except Exception as e:
                        print(f"⚠️ Could not clear attachment point actor: {e}")
                
                # Clean placement instruction
                if hasattr(self.current_roof, 'placement_instruction') and self.current_roof.placement_instruction:
                    try:
                        if hasattr(self.current_roof, 'plotter') and self.current_roof.plotter:
                            self.current_roof.plotter.remove_actor(self.current_roof.placement_instruction)
                        self.current_roof.placement_instruction = None
                        print("✅ Cleared placement instruction")
                    except Exception as e:
                        print(f"⚠️ Could not clear placement instruction: {e}")
                
                # Clean any other references
                if hasattr(self.current_roof, 'plotter') and self.current_roof.plotter:
                    try:
                        # Remove key bindings
                        if hasattr(self.current_roof.plotter, 'remove_key_event'):
                            for key in ['1', '2', '3', 'c', 'C', 'Left', 'Right', 'r', 'R', 'h', 'H', 's', 'S', 'o', 'O']:
                                try:
                                    self.current_roof.plotter.remove_key_event(key)
                                except:
                                    pass
                        print("✅ Removed key bindings")
                        
                        # Disable picking
                        if hasattr(self.current_roof.plotter, 'disable_picking'):
                            try:
                                self.current_roof.plotter.disable_picking()
                                print("✅ Disabled picking")
                            except:
                                pass
                    except Exception as e:
                        print(f"⚠️ Could not clean plotter references: {e}")
                
                # Set current_roof to None
                self.current_roof = None
                print("✅ Previous roof cleaned up")
            
            # STEP 2: Clear tracked actors
            if hasattr(self, 'roof_actors') and self.roof_actors:
                plotter = self.get_plotter_from_model_tab()
                if plotter:
                    for actor in self.roof_actors:
                        try:
                            plotter.remove_actor(actor)
                        except:
                            pass
                self.roof_actors = []
                print("✅ Cleared tracked roof actors")
                
        except Exception as e:
            print(f"❌ Error cleaning previous roof: {e}")
            traceback.print_exc()
    
    def _remove_all_key_bindings(self, plotter):
        """Remove all key bindings from the plotter"""
        try:
            if not plotter:
                return
                
            # Get all key events
            if hasattr(plotter, '_key_press_event_callbacks'):
                keys = list(plotter._key_press_event_callbacks.keys())
                for key in keys:
                    try:
                        plotter.remove_key_event(key)
                    except:
                        pass
                print(f"✅ Removed {len(keys)} key bindings")
            
            # Common keys to remove
            common_keys = ['1', '2', '3', 'c', 'C', 'Left', 'Right', 'r', 'R', 'h', 'H', 's', 'S', 'o', 'O']
            for key in common_keys:
                try:
                    plotter.remove_key_event(key)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error removing key bindings: {e}")
    
    def _override_roof_key_bindings(self, plotter):
        """Override the roof's key bindings with our safe ones"""
        try:
            print("🔧 Overriding roof key bindings with safe handlers...")
            
            # First, remove all existing key bindings
            self._remove_all_key_bindings(plotter)
            
            # Now add our safe key handlers
            self._add_safe_key_handlers(plotter)
            
            # If the roof has a setup_key_bindings method, disable it
            if hasattr(self.current_roof, 'setup_key_bindings'):
                # Save the original method
                original_setup = self.current_roof.setup_key_bindings
                
                # Replace it with a dummy method
                def dummy_setup(*args, **kwargs):
                    print("⚠️ Roof tried to set up key bindings, but was prevented")
                    return
                
                # Replace the method
                self.current_roof.setup_key_bindings = dummy_setup
                print("✅ Disabled roof's original key binding setup method")
            
            print("✅ Roof key bindings successfully overridden")
            
        except Exception as e:
            print(f"❌ Error overriding roof key bindings: {e}")
            traceback.print_exc()
    
    def _add_safe_key_handlers(self, plotter):
        """Add safe key handlers that check for None before using handlers"""
        try:
            if not plotter or not self.current_roof:
                return
                
            # Check roof type for specific handlers
            roof_type = type(self.current_roof).__name__
            print(f"🔧 Adding safe key handlers for {roof_type}...")
            
            # FlatRoof specific handlers
            if roof_type == 'FlatRoof':
                # ✅ FIXED: Use add_panels() method instead of place_panels()
                def safe_place_panels_north():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 FLAT: Adding panels to NORTH area")
                            self.current_roof.solar_panel_handler.add_panels(area="north")  # ✅ CORRECT METHOD
                        else:
                            print("⚠️ Cannot place north panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error placing north panels: {e}")
                        
                def safe_place_panels_center():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 FLAT: Adding panels to CENTER area")
                            self.current_roof.solar_panel_handler.add_panels(area="center")  # ✅ CORRECT METHOD
                        else:
                            print("⚠️ Cannot place center panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error placing center panels: {e}")
                        
                def safe_place_panels_south():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 FLAT: Adding panels to SOUTH area")
                            self.current_roof.solar_panel_handler.add_panels(area="south")  # ✅ CORRECT METHOD
                        else:
                            print("⚠️ Cannot place south panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error placing south panels: {e}")
                
                def safe_place_panels_east():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 FLAT: Adding panels to EAST area")
                            self.current_roof.solar_panel_handler.add_panels(area="east")  # ✅ CORRECT METHOD
                        else:
                            print("⚠️ Cannot place east panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error placing east panels: {e}")
                
                def safe_place_panels_west():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 FLAT: Adding panels to WEST area")
                            self.current_roof.solar_panel_handler.add_panels(area="west")  # ✅ CORRECT METHOD
                        else:
                            print("⚠️ Cannot place west panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error placing west panels: {e}")
                        
                def safe_clear_panels():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 FLAT: Clearing panels")
                            self.current_roof.solar_panel_handler.clear_panels()
                        else:
                            print("⚠️ Cannot clear panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error clearing panels: {e}")
                        
                # ✅ CORRECT FLAT ROOF KEY MAPPINGS
                plotter.add_key_event("1", safe_place_panels_north)   # Key 1 → NORTH
                plotter.add_key_event("2", safe_place_panels_center)  # Key 2 → CENTER
                plotter.add_key_event("3", safe_place_panels_south)   # Key 3 → SOUTH
                plotter.add_key_event("4", safe_place_panels_east)    # Key 4 → EAST
                plotter.add_key_event("5", safe_place_panels_west)    # Key 5 → WEST
                plotter.add_key_event("c", safe_clear_panels)
                plotter.add_key_event("C", safe_clear_panels)
                
                print("✅ Added FlatRoof-specific safe key handlers")
                print("✅ Key 1 → NORTH, Key 2 → CENTER, Key 3 → SOUTH, Key 4 → EAST, Key 5 → WEST")

            
            # ✅ GABLE ROOF SPECIFIC HANDLERS
            elif roof_type == 'GableRoof':
                def safe_add_panels_left():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 GABLE: Adding panels to LEFT side")
                            self.current_roof.solar_panel_handler.add_panels("left")
                        else:
                            print("⚠️ Cannot add left panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error adding left panels: {e}")
                        
                def safe_add_panels_right():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 GABLE: Adding panels to RIGHT side")
                            self.current_roof.solar_panel_handler.add_panels("right")
                        else:
                            print("⚠️ Cannot add right panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error adding right panels: {e}")
                        
                def safe_clear_panels():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 GABLE: Clearing panels")
                            self.current_roof.solar_panel_handler.clear_panels()
                        else:
                            print("⚠️ Cannot clear panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error clearing panels: {e}")
                
                # ✅ CORRECT GABLE ROOF KEY MAPPINGS
                plotter.add_key_event("1", safe_add_panels_left)   # Key 1 → LEFT (correct!)
                plotter.add_key_event("2", safe_add_panels_right)  # Key 2 → RIGHT (correct!)
                plotter.add_key_event("c", safe_clear_panels)
                plotter.add_key_event("C", safe_clear_panels)
                plotter.add_key_event("Left", safe_add_panels_left)   # Arrow key support
                plotter.add_key_event("Right", safe_add_panels_right) # Arrow key support
                
                print("✅ Added GABLE roof specific safe key handlers")
                print("✅ Key 1 → LEFT, Key 2 → RIGHT")
            
            # ✅ HIP/PYRAMID ROOF SPECIFIC HANDLERS  
            elif roof_type in ['HipRoof', 'PyramidRoof']:
                # ✅ ADD CALL PROTECTION
                _last_call_time = {}
                
                def safe_add_panels_front():
                    try:
                        # ✅ CALL PROTECTION
                        import time
                        current_time = time.time()
                        if 'front' in _last_call_time and current_time - _last_call_time['front'] < 0.5:
                            print(f"🚨 BLOCKED RAPID CALL: Front panel call too soon")
                            return
                        _last_call_time['front'] = current_time
                        
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 {roof_type.upper()}: Adding panels to FRONT side")
                            self.current_roof.solar_panel_handler.add_panels("front")
                        else:
                            print("⚠️ Cannot add front panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error adding front panels: {e}")
                
                # ✅ ADD SAME PROTECTION TO OTHER METHODS
                def safe_add_panels_right():
                    try:
                        import time
                        current_time = time.time()
                        if 'right' in _last_call_time and current_time - _last_call_time['right'] < 0.5:
                            print(f"🚨 BLOCKED RAPID CALL: Right panel call too soon")
                            return
                        _last_call_time['right'] = current_time
                        
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 {roof_type.upper()}: Adding panels to RIGHT side")
                            self.current_roof.solar_panel_handler.add_panels("right")
                        else:
                            print("⚠️ Cannot add right panels - solar panel handler not available")
                    except Exception as e:
                        # ✅ ADD EXCEPTION HANDLING
                     print(f"⚠️ Error adding right panels: {e}")
                        
                def safe_add_panels_back():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 {roof_type.upper()}: Adding panels to BACK side")
                            self.current_roof.solar_panel_handler.add_panels("back")
                        else:
                            print("⚠️ Cannot add back panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error adding back panels: {e}")
                        
                def safe_add_panels_left():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 {roof_type.upper()}: Adding panels to LEFT side")
                            self.current_roof.solar_panel_handler.add_panels("left")
                        else:
                            print("⚠️ Cannot add left panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error adding left panels: {e}")
                        
                def safe_clear_panels():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            print(f"🔧 {roof_type.upper()}: Clearing panels")
                            self.current_roof.solar_panel_handler.clear_panels()
                        else:
                            print("⚠️ Cannot clear panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error clearing panels: {e}")
                
                # ✅ CORRECT HIP/PYRAMID KEY MAPPINGS
                plotter.add_key_event("1", safe_add_panels_front)  # Key 1 → FRONT
                plotter.add_key_event("2", safe_add_panels_right)  # Key 2 → RIGHT  
                plotter.add_key_event("3", safe_add_panels_back)   # Key 3 → BACK
                plotter.add_key_event("4", safe_add_panels_left)   # Key 4 → LEFT
                plotter.add_key_event("c", safe_clear_panels)
                plotter.add_key_event("C", safe_clear_panels)
                
                print("✅ Added Hip/Pyramid roof specific safe key handlers")
                print("✅ Key 1 → FRONT, Key 2 → RIGHT, Key 3 → BACK, Key 4 → LEFT")
            
            # Unknown roof type fallback
            else:
                print(f"⚠️ Unknown roof type: {roof_type}, using basic handlers")
                # Add basic clear handler
                def safe_clear_panels():
                    try:
                        if self.current_roof and hasattr(self.current_roof, 'solar_panel_handler') and self.current_roof.solar_panel_handler:
                            self.current_roof.solar_panel_handler.clear_panels()
                        else:
                            print("⚠️ Cannot clear panels - solar panel handler not available")
                    except Exception as e:
                        print(f"⚠️ Error clearing panels: {e}")
                
                plotter.add_key_event("c", safe_clear_panels)
                plotter.add_key_event("C", safe_clear_panels)
            
            # Common handlers for all roof types
            def safe_reset_camera():
                try:
                    if self.current_roof and hasattr(self.current_roof, 'reset_camera'):
                        self.current_roof.reset_camera()
                    elif plotter and hasattr(plotter, 'reset_camera'):
                        plotter.reset_camera()
                except Exception as e:
                    print(f"⚠️ Error resetting camera: {e}")
                    
            def safe_toggle_help():
                try:
                    if self.current_roof and hasattr(self.current_roof, 'toggle_help'):
                        self.current_roof.toggle_help()
                except Exception as e:
                    print(f"⚠️ Error toggling help: {e}")
                    
            def safe_save_screenshot():
                try:
                    if self.current_roof and hasattr(self.current_roof, 'save_roof_screenshot'):
                        self.current_roof.save_roof_screenshot()
                except Exception as e:
                    print(f"⚠️ Error saving screenshot: {e}")
                    
            def safe_clear_obstacles():
                try:
                    if self.current_roof and hasattr(self.current_roof, 'clear_obstacles'):
                        self.current_roof.clear_obstacles()
                except Exception as e:
                    print(f"⚠️ Error clearing obstacles: {e}")
                    
            # Add common handlers
            plotter.add_key_event("r", safe_reset_camera)
            plotter.add_key_event("R", safe_reset_camera)
            plotter.add_key_event("h", safe_toggle_help)
            plotter.add_key_event("H", safe_toggle_help)
            plotter.add_key_event("s", safe_save_screenshot)
            plotter.add_key_event("S", safe_save_screenshot)
            plotter.add_key_event("o", safe_clear_obstacles)
            plotter.add_key_event("O", safe_clear_obstacles)
            
            print("✅ Added common safe key handlers")
                
        except Exception as e:
            print(f"⚠️ Error adding safe key handlers: {e}")
            traceback.print_exc()

    
    def generate_roof(self, roof_type, dimensions):
        """Generate roof with the given dimensions"""
        try:
            print(f"🏗️ Generating {roof_type} roof with dimensions: {dimensions}")
            
            # Update status
            self.main_window.statusBar().showMessage(f"Generating {roof_type} roof model...", 3000)
            
            # IMPORTANT: Clean up previous roof first
            self._clean_previous_roof()
            
            # IMPORTANT: Reset model tab plotter if available
            if hasattr(self.main_window, 'content_tabs') and hasattr(self.main_window.content_tabs, 'model_tab'):
                model_tab = self.main_window.content_tabs.model_tab
                if hasattr(model_tab, 'reset_plotter'):
                    model_tab.reset_plotter()
                    print("✅ Used model_tab.reset_plotter()")
            
            # Get plotter from the model tab
            plotter = self.get_plotter_from_model_tab()
            
            if not plotter:
                print("❌ Could not get plotter from model tab")
                self._show_error("Plotter Error", "Could not get 3D visualization plotter from model tab.\n\nMake sure the 3D Model tab is properly initialized.")
                return False
            
            # Thoroughly clear the plotter
            self._thorough_plotter_clear(plotter)
            
            # IMPORTANT: Check if plotter has an interactor
            if not hasattr(plotter, 'iren') or not plotter.iren:
                print("❌ Plotter does not have an interactor")
                self._show_error("Plotter Error", "The 3D visualization plotter does not have an interactor.\n\nTry switching to the 3D Model tab first, then try again.")
                return False
            
            # IMPORTANT: Remove all key bindings from the plotter
            self._remove_all_key_bindings(plotter)
            
            # Store original actor count to track new actors
            original_actor_count = 0
            if hasattr(plotter, 'renderer') and hasattr(plotter.renderer, 'actors'):
                original_actor_count = len(plotter.renderer.actors)
                print(f"📊 Original actor count: {original_actor_count}")
            
            # Create roof based on type
            if roof_type.lower() == 'gable':
                if not GABLE_ROOF_AVAILABLE:
                    print("❌ GableRoof class not available")
                    self._show_error("Generation Error", "GableRoof class not available.")
                    return False
                
                # Extract dimensions from the dictionary
                length = float(dimensions.get('length', 10.0))
                width = float(dimensions.get('width', 8.0))
                height = float(dimensions.get('height', 5.0))
                
                # Create the roof with correct parameters
                self.current_roof = GableRoof(
                    plotter=plotter,
                    dimensions=(length, width, height),
                    theme="light"
                )
                print("✅ Gable roof created successfully")
                
            elif roof_type.lower() == 'flat':
                if not FLAT_ROOF_AVAILABLE:
                    print("❌ FlatRoof class not available")
                    self._show_error("Generation Error", "FlatRoof class not available.")
                    return False
                
                # Extract dimensions from the dictionary
                length = float(dimensions.get('length', 10.0))
                width = float(dimensions.get('width', 8.0))
                height = float(dimensions.get('height', 3.0))
                
                # Create flat roof
                self.current_roof = FlatRoof(
                    plotter=plotter,
                    dimensions=(length, width, height),
                    theme="light"
                )
                print("✅ Flat roof created successfully")
                
            elif roof_type.lower() == 'hip':
                if not HIP_ROOF_AVAILABLE:
                    print("❌ HipRoof class not available")
                    self._show_error("Generation Error", "HipRoof class not available.")
                    return False
                
                # Extract dimensions from the dictionary
                length = float(dimensions.get('length', 10.0))
                width = float(dimensions.get('width', 8.0))
                height = float(dimensions.get('height', 4.0))
                
                # Create hip roof
                self.current_roof = HipRoof(
                    plotter=plotter,
                    dimensions=(length, width, height),
                    theme="light"
                )
                print("✅ Hip roof created successfully")
                
            elif roof_type.lower() == 'pyramid':
                if not PYRAMID_ROOF_AVAILABLE:
                    print("❌ PyramidRoof class not available")
                    self._show_error("Generation Error", "PyramidRoof class not available.")
                    return False
                
                # Extract dimensions from the dictionary
                length = float(dimensions.get('length', 10.0))
                width = float(dimensions.get('width', 8.0))
                height = float(dimensions.get('height', 4.0))
                
                # Create pyramid roof
                self.current_roof = PyramidRoof(
                    plotter=plotter,
                    dimensions=(length, width, height),
                    theme="light"
                )
                print("✅ Pyramid roof created successfully")
                
            else:
                print(f"❌ Unknown roof type: {roof_type}")
                self._show_error("Generation Error", f"Unknown roof type: {roof_type}")
                return False
            
            # IMPORTANT: Override the roof's key bindings with our safe ones
            self._override_roof_key_bindings(plotter)
            
            # Track new actors added by the roof
            if hasattr(plotter, 'renderer') and hasattr(plotter.renderer, 'actors'):
                current_actor_count = len(plotter.renderer.actors)
                new_actor_count = current_actor_count - original_actor_count
                print(f"📊 Current actor count: {current_actor_count}, New actors: {new_actor_count}")
                
                # Get the new actors
                if new_actor_count > 0:
                    all_actors = list(plotter.renderer.actors.keys())
                    new_actors = all_actors[-new_actor_count:]
                    self.roof_actors = new_actors
                    print(f"📊 Tracking {len(new_actors)} new actors")
            
            # Emit signal that roof was generated
            self.roof_generated.emit(self.current_roof)
            
            # Update main window state
            self.main_window._building_generated = True
            if hasattr(self.main_window, 'building_generated'):
                self.main_window.building_generated.emit({
                    'type': 'roof',
                    'roof_type': roof_type,
                    'dimensions': dimensions
                })
            
            # Update status
            self.main_window.statusBar().showMessage(f"✅ {roof_type.title()} roof created successfully!", 3000)
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating roof: {e}")
            traceback.print_exc()
            self._show_error("Generation Error", f"Failed to generate roof: {str(e)}")
            return False
    
    def get_plotter_from_model_tab(self):
        """Get PyVista plotter from the 3D model tab"""
        try:
            # Try to get plotter from content tabs
            if hasattr(self.main_window, 'content_tabs'):
                # Method 1: Check if content_tabs has a get_model_plotter method
                if hasattr(self.main_window.content_tabs, 'get_model_plotter'):
                    plotter = self.main_window.content_tabs.get_model_plotter()
                    if plotter:
                        print("✅ Got plotter from content_tabs.get_model_plotter()")
                        return plotter
                
                # Method 2: Check if model tab has a plotter attribute
                model_tab_index = self.find_model_tab_index()
                if model_tab_index is not None:
                    model_tab = self.main_window.content_tabs.widget(model_tab_index)
                    if model_tab:
                        # Try different attribute names
                        for attr_name in ['plotter', 'pv_widget', 'pyvista_widget', 'vtk_widget']:
                            if hasattr(model_tab, attr_name):
                                plotter = getattr(model_tab, attr_name)
                                if plotter:
                                    print(f"✅ Got plotter from model_tab.{attr_name}")
                                    return plotter
            
            # Method 3: If we have pyvista_integration, try to get plotter from there
            if hasattr(self.main_window, 'pyvista_integration'):
                if hasattr(self.main_window.pyvista_integration, 'get_plotter'):
                    plotter = self.main_window.pyvista_integration.get_plotter()
                    if plotter:
                        print("✅ Got plotter from pyvista_integration.get_plotter()")
                        return plotter
                
                # Try to get the plotter directly from the integration
                if hasattr(self.main_window.pyvista_integration, 'plotter'):
                    plotter = self.main_window.pyvista_integration.plotter
                    if plotter:
                        print("✅ Got plotter directly from pyvista_integration")
                        return plotter
            
            # IMPORTANT: Do NOT create a new plotter - it won't have the interactor set up properly
            print("❌ Could not find an existing plotter - will NOT create a new one")
            return None
            
        except Exception as e:
            print(f"❌ Error getting plotter from model tab: {e}")
            return None
    
    def find_model_tab_index(self):
        """Find the model tab index"""
        try:
            if not hasattr(self.main_window, 'content_tabs'):
                return None
                
            # Search for model-related keywords in tab names
            model_keywords = ['model', '3d', 'building', 'pyvista', 'render']
            
            for i in range(self.main_window.content_tabs.count()):
                tab_text = self.main_window.content_tabs.tabText(i).lower()
                
                for keyword in model_keywords:
                    if keyword in tab_text:
                        return i
            
            # If no keyword match, assume last tab is model tab
            return self.main_window.content_tabs.count() - 1
            
        except Exception as e:
            print(f"❌ Error finding model tab index: {e}")
            return None
    
    def _thorough_plotter_clear(self, plotter):
        """Thoroughly clear the plotter and reset all state - ENHANCED VERSION"""
        try:
            print("🧹 Performing thorough plotter clearing...")
            
            # STEP 1: Clear all actors
            if hasattr(plotter, 'clear'):
                plotter.clear()
                print("✅ Plotter.clear() called")
            
            # STEP 2: Remove all actors manually
            if hasattr(plotter, 'renderer') and hasattr(plotter.renderer, 'actors'):
                actors = list(plotter.renderer.actors.keys())
                for actor in actors:
                    try:
                        plotter.remove_actor(actor)
                    except Exception as e:
                        print(f"⚠️ Could not remove actor {actor}: {e}")
                print(f"✅ Removed {len(actors)} actors manually")
            
            # STEP 3: Reset camera and view
            if hasattr(plotter, 'reset_camera'):
                plotter.reset_camera()
                print("✅ Reset camera")
            
            # STEP 4: Disable picking
            if hasattr(plotter, 'disable_picking'):
                try:
                    plotter.disable_picking()
                    print("✅ Disabled picking")
                except:
                    pass
            
            # STEP 5: Remove all key bindings
            if hasattr(plotter, '_key_press_event_callbacks'):
                keys = list(plotter._key_press_event_callbacks.keys())
                for key in keys:
                    try:
                        plotter.remove_key_event(key)
                    except:
                        pass
                print(f"✅ Removed {len(keys)} key bindings")
            
            # STEP 6: Restore axes
            if hasattr(plotter, 'add_axes'):
                try:
                    plotter.add_axes()
                    print("✅ Restored axes")
                except:
                    pass
            
            # STEP 7: Force update
            if hasattr(plotter, 'update'):
                plotter.update()
            
            if hasattr(plotter, 'render'):
                plotter.render()
            
            print("✅ Plotter thoroughly cleared")
            return plotter
            
        except Exception as e:
            print(f"❌ Error in thorough plotter clear: {e}")
            traceback.print_exc()
            return plotter
    
    def clear_plotter(self, plotter):
        """Clear the plotter before generating a new roof"""
        try:
            if plotter:
                # Method 1: Use clear method if available
                if hasattr(plotter, 'clear'):
                    plotter.clear()
                    return True
                
                # Method 2: Remove all actors
                if hasattr(plotter, 'remove_actor'):
                    # Get all actor keys if available
                    if hasattr(plotter, 'renderer') and hasattr(plotter.renderer, 'actors'):
                        actors = list(plotter.renderer.actors.keys())
                        for actor in actors:
                            plotter.remove_actor(actor)
                    return True
                
                # Method 3: Reset the camera if nothing else worked
                if hasattr(plotter, 'reset_camera'):
                    plotter.reset_camera()
            
            return False
            
        except Exception as e:
            print(f"❌ Error clearing plotter: {e}")
            return False
    
    def _show_error(self, title, message):
        """Show error message"""
        try:
            QMessageBox.warning(self.main_window, title, message)
        except Exception as e:
            print(f"❌ Could not show error dialog: {e}")