#!/usr/bin/env python3
"""
Component Management Module
Handles creation and management of UI components
Enhanced with tab integration support
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class ComponentManager:
    """Manages UI component creation and lifecycle"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.components = {}
    
    def initialize_component_references(self):
        """Initialize UI component references"""
        # UI components
        self.main_window.left_panel = None
        self.main_window.content_tabs = None
        self.main_window.canvas_manager = None
        self.main_window.canvas_integrator = None
        self.main_window.pyvista_integration = None
        self.main_window.model_generator = None
        self.main_window.snipping_tool = None
        
        # Tab references (will be set by ContentTabWidget)
        self.main_window.default_tab = None
        self.main_window.model_tab = None
        self.main_window.maps_tab = None
        self.main_window.environment_tab = None
        self.main_window.modifications_tab = None
        
        # Control components (managed by LeftControlPanel)
        self.main_window.wall_height_input = None
        self.main_window.wall_height_slider = None
        self.main_window.roof_type_combo = None
        self.main_window.roof_pitch_input = None
        self.main_window.roof_pitch_slider = None
        self.main_window.time_input = None
        self.main_window.time_slider = None
        self.main_window.day_input = None
        self.main_window.day_slider = None
        
        # Action components
        self.main_window.generate_btn = None
        self.main_window.measurements_display = None
        self.main_window.tips_content = None
        self.main_window.scale_input = None
        self.main_window.angle_snap_btn = None
        self.main_window.stacked_widget = None
        self.main_window.export_btn = None
        self.main_window.animate_btn = None
        
        print("✅ Component references initialized")
    
    def create_ui_components(self):
        """Create main UI components with enhanced error handling"""
        try:
            print("🔧 Creating UI components...")
            
            # Create Left Panel
            self._create_left_panel()
            
            # Create Content Tabs (this also creates individual tabs)
            self._create_content_tabs()
            
            print("✅ UI components creation completed")
            
        except Exception as e:
            print(f"❌ Component creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_left_panel(self):
        """Create left control panel component"""
        try:
            from ui.panel.left_control_panel import LeftControlPanel
            self.main_window.left_panel = LeftControlPanel(self.main_window)
            self.components['left_panel'] = self.main_window.left_panel
            print("✅ LeftControlPanel created")
        except ImportError:
            print("❌ LeftControlPanel class not available")
            self.main_window.left_panel = None
        except Exception as e:
            print(f"❌ LeftControlPanel creation failed: {e}")
            self.main_window.left_panel = None
    
    def _create_content_tabs(self):
        """Create content tab widget component"""
        try:
            from ui.tabs.content_tab_widget import ContentTabWidget
            print("🔧 Attempting to create ContentTabWidget...")
            self.main_window.content_tabs = ContentTabWidget(self.main_window)
            self.components['content_tabs'] = self.main_window.content_tabs
            
            # Store references to individual tabs (set by ContentTabWidget)
            if hasattr(self.main_window.content_tabs, 'default_tab'):
                self.main_window.default_tab = self.main_window.content_tabs.default_tab
                print("✅ Default tab reference stored")
            
            if hasattr(self.main_window.content_tabs, 'model_tab'):
                self.main_window.model_tab = self.main_window.content_tabs.model_tab
                print("✅ Model tab reference stored")
            
            if hasattr(self.main_window.content_tabs, 'maps_tab'):
                self.main_window.maps_tab = self.main_window.content_tabs.maps_tab
                print("✅ Maps tab reference stored")
            
            if hasattr(self.main_window.content_tabs, 'environment_tab'):
                self.main_window.environment_tab = self.main_window.content_tabs.environment_tab
                print("✅ Environment tab reference stored")
            
            if hasattr(self.main_window.content_tabs, 'modifications_tab'):
                self.main_window.modifications_tab = self.main_window.content_tabs.modifications_tab
                print("✅ Modifications tab reference stored")
            
            print("✅ ContentTabWidget created")
            
        except ImportError:
            print("❌ ContentTabWidget class not available")
            self.main_window.content_tabs = None
        except Exception as e:
            print(f"❌ ContentTabWidget creation failed: {e}")
            import traceback
            traceback.print_exc()
            self.main_window.content_tabs = None
    
    def _create_minimal_canvas_manager(self):
        """Create minimal canvas manager as fallback"""
        class MinimalCanvasManager:
            def __init__(self, main_window):
                self.main_window = main_window
                
            def create_canvas(self):
                return None
                
            def get_canvas(self):
                return None
                
            def cleanup(self):
                pass
        
        return MinimalCanvasManager(self.main_window)
    
    def create_fallback_ui(self, layout):
        """Create fallback UI when components fail"""
        fallback_label = QLabel("UI components failed to load.\nCheck console for errors.")
        fallback_label.setAlignment(Qt.AlignCenter)
        fallback_label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
        layout.addWidget(fallback_label)
        print("⚠️ Fallback UI created")
    
    def setup_integration(self):
        """Setup integration between components"""
        try:
            print("🔧 Setting up component integration...")
            
            # Setup PyVista integration
            self._setup_pyvista_integration()
            
            # CRITICAL: Initialize tab references in TabManager
            if hasattr(self.main_window, 'tab_manager'):
                print("🔧 Initializing tab references in TabManager...")
                self.main_window.tab_manager.initialize_tab_references()
                print("✅ Tab references initialized in TabManager")
            else:
                print("⚠️ TabManager not available for tab reference initialization")
            
            # Connect environment tab if available
            if hasattr(self.main_window, 'model_tab') and hasattr(self.main_window, 'environment_tab'):
                if self.main_window.model_tab and self.main_window.environment_tab:
                    self.main_window.model_tab.connect_environment_tab(
                        self.main_window.environment_tab
                    )
                    print("✅ Environment tab connected to model tab")
            
            # Connect modifications tab if available
            if hasattr(self.main_window, 'model_tab') and hasattr(self.main_window, 'modifications_tab'):
                if self.main_window.model_tab and self.main_window.modifications_tab:
                    self.main_window.model_tab.connect_modifications_tab(
                        self.main_window.modifications_tab
                    )
                    print("✅ Modifications tab connected to model tab")
            
            print("✅ Component integration completed")
            
        except Exception as e:
            print(f"❌ Integration setup failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_pyvista_integration(self):
        """Setup PyVista integration"""
        try:
            from utils.pyvista_integration import EnhancedPyVistaIntegration
            self.main_window.pyvista_integration = EnhancedPyVistaIntegration(self.main_window)
            
            if hasattr(self.main_window.pyvista_integration, 'get_building_generator'):
                self.main_window.model_generator = self.main_window.pyvista_integration.get_building_generator()
            else:
                self.main_window.model_generator = self.main_window.building_generator
                
            print("✅ PyVista integration setup")
                
        except ImportError:
            print("⚠️ PyVista integration not available")
            self.main_window.pyvista_integration = None
            self.main_window.model_generator = getattr(self.main_window, 'building_generator', None)
        except Exception as e:
            print(f"❌ PyVista integration failed: {e}")
            self.main_window.pyvista_integration = None
            self.main_window.model_generator = getattr(self.main_window, 'building_generator', None)
    
    def cleanup_components(self):
        """Cleanup all managed components"""
        cleanup_list = [
            'building_generator', 'canvas_integrator', 'canvas_manager',
            'content_tabs', 'pyvista_integration', 'theme_manager',
            'default_tab', 'model_tab', 'maps_tab', 'environment_tab', 'modifications_tab'
        ]
        
        for component_name in cleanup_list:
            try:
                component = getattr(self.main_window, component_name, None)
                if component and hasattr(component, 'cleanup'):
                    component.cleanup()
                    print(f"✅ Cleaned up {component_name}")
            except Exception as cleanup_error:
                print(f"❌ Cleanup failed for {component_name}: {cleanup_error}")
