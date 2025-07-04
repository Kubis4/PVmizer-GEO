
"""
Initialization Management Module
Handles application initialization and setup
"""

from PyQt5.QtCore import QTimer


class InitializationManager:
    """Manages application initialization and setup"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def post_initialization(self):
        """Post-initialization tasks"""
        try:
            if self.main_window.pyvista_integration and hasattr(self.main_window.pyvista_integration, 'finalize_initialization'):
                self.main_window.pyvista_integration.finalize_initialization()
            
            self.main_window.statusBar().showMessage(
                "✅ PVmizer GEO Enhanced ready! Click 'Snip Screenshot' to start.", 3000)
            
            self.main_window._initialization_complete = True
            self.main_window.initialization_completed.emit()
            print("✅ Post-initialization completed")
            
        except Exception as e:
            print(f"❌ Post-initialization failed: {e}")
    
    def apply_auto_switch_blocking(self):
        """Apply auto-switch blocking"""
        try:
            if self.main_window.canvas_integrator and hasattr(self.main_window.canvas_integrator, 'boundary_completed'):
                try:
                    self.main_window.canvas_integrator.boundary_completed.disconnect()
                except:
                    pass  # Signal might not be connected
                
                if hasattr(self.main_window, '_on_boundary_completed_no_switch'):
                    self.main_window.canvas_integrator.boundary_completed.connect(self.main_window._on_boundary_completed_no_switch)
                elif hasattr(self.main_window.event_manager, 'handle_boundary_completed'):
                    self.main_window.canvas_integrator.boundary_completed.connect(self.main_window.event_manager.handle_boundary_completed)
            
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, '_auto_switch_enabled'):
                self.main_window.content_tabs._auto_switch_enabled = False
            
            self.main_window._auto_switch_blocked = True
            print("✅ Auto-switch blocking applied")
            
        except Exception as e:
            print(f"❌ Auto-switch blocking failed: {e}")
    
    def initialize_delayed_components(self):
        """Initialize components that require delayed initialization"""
        try:
            # Any components that need to be initialized after the UI is shown
            QTimer.singleShot(500, self._initialize_pyvista_components)
            QTimer.singleShot(1000, self._initialize_drawing_components)
            
            print("✅ Delayed component initialization scheduled")
            
        except Exception as e:
            print(f"❌ Delayed initialization scheduling failed: {e}")
    
    def _initialize_pyvista_components(self):
        """Initialize PyVista components after UI is shown"""
        try:
            if self.main_window.pyvista_integration and hasattr(self.main_window.pyvista_integration, 'initialize_delayed'):
                self.main_window.pyvista_integration.initialize_delayed()
                print("✅ PyVista components initialized")
            
        except Exception as e:
            print(f"❌ PyVista component initialization failed: {e}")
    
    def _initialize_drawing_components(self):
        """Initialize drawing components after UI is shown"""
        try:
            if self.main_window.canvas_integrator and hasattr(self.main_window.canvas_integrator, 'initialize_delayed'):
                self.main_window.canvas_integrator.initialize_delayed()
                print("✅ Drawing components initialized")
            
        except Exception as e:
            print(f"❌ Drawing component initialization failed: {e}")
