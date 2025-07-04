#!/usr/bin/env python3
"""
Enhanced Main Window - MODULAR VERSION
PVmizer GEO - Enhanced Building Designer with Advanced Solar Simulation
- Modular architecture with separated concerns
- Clean separation of responsibilities
- Enhanced maintainability and testability
- Complete roof generation workflow
"""

import traceback
import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QTabWidget, QMessageBox, QApplication, QSlider,
                              QDoubleSpinBox, QComboBox, QSpinBox, QLabel)
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen

# Core imports
from core import (WindowManager, ComponentManager, SignalManager, 
                 TabManager, BuildingManager, CanvasManager, 
                 DebugManager, EventManager, InitializationManager,
                 RoofGenerationManager)
# UI imports with fallbacks
try:
    from core.configuration_manager import ConfigurationManager
except ImportError:
    print("⚠️ Could not import ConfigurationManager")
    ConfigurationManager = None

try:
    from ui.styles.theme_manager import ThemeManager
except ImportError:
    print("⚠️ Could not import ThemeManager")
    ThemeManager = None

try:
    from ui.toolbar.toolbar_manager import ToolbarManager
except ImportError:
    print("⚠️ Could not import ToolbarManager")
    ToolbarManager = None


class MainWindow(QMainWindow):
    """
    Enhanced main window - MODULAR ARCHITECTURE VERSION
    
    Features:
    - Separated into logical core modules
    - Clean separation of concerns
    - Enhanced maintainability
    - Comprehensive debugging
    - Complete workflow state management
    - Roof generation from maps tab
    """
    
    # Signals for external communication
    building_generated = pyqtSignal(dict)
    canvas_updated = pyqtSignal()
    drawing_completed = pyqtSignal(list)
    initialization_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PVmizer GEO - Enhanced Building Designer")
        
        # Initialize core attributes
        self._auto_switch_blocked = False
        self._initialization_complete = False
        self._building_generated = False
        self._current_drawing_points = []
        self._current_scale = 0.05
        self._debug_mode = True
        self._last_error = None
        self.angle_snap_enabled = True
        
        # Initialize measurements
        self.current_measurements = {
            'points': 0, 
            'area': 0.0, 
            'perimeter': 0.0, 
            'is_complete': False
        }
        
        # Initialize core managers
        self._initialize_core_managers()
        
        # Initialize modular managers
        self._initialize_modular_managers()
        
        # Timer for checking completion
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_drawing_completion)
        
        # Setup and show
        self._setup_and_show()
        
        # Schedule delayed initialization
        self._schedule_delayed_initialization()
    
    def _initialize_core_managers(self):
        """Initialize configuration and theme managers"""
        # Configuration manager
        if ConfigurationManager:
            try:
                self.config = ConfigurationManager()
                print("✅ ConfigurationManager initialized")
            except Exception as e:
                print(f"❌ ConfigurationManager failed: {e}")
                self.config = None
        else:
            self.config = None
        
        # Theme manager
        if ThemeManager:
            try:
                self.theme_manager = ThemeManager(self)
                print("✅ ThemeManager initialized")
            except Exception as e:
                print(f"❌ ThemeManager failed: {e}")
                self.theme_manager = None
        else:
            self.theme_manager = None
    
    def _initialize_modular_managers(self):
        """Initialize all modular managers"""
        try:
            # Core modular managers
            self.window_manager = WindowManager(self)
            self.component_manager = ComponentManager(self)
            self.signal_manager = SignalManager(self)
            self.tab_manager = TabManager(self)
            self.building_manager = BuildingManager(self)
            self.canvas_manager = CanvasManager(self)
            self.debug_manager = DebugManager(self)
            self.event_manager = EventManager(self)
            self.initialization_manager = InitializationManager(self)
            
            # Add roof generation manager
            self.roof_generation_manager = RoofGenerationManager(self)
            
            # Connect roof generation signals
            if hasattr(self.roof_generation_manager, 'roof_generated'):
                # CHANGED: Use handle_building_generated instead of handle_roof_generated
                self.roof_generation_manager.roof_generated.connect(self.event_manager.handle_building_generated)
                print("✅ Connected roof_generated signal")
            
            print("✅ All modular managers initialized")
            
        except Exception as e:
            print(f"❌ Modular manager initialization failed: {e}")
            traceback.print_exc()
    
    def _setup_and_show(self):
        """Setup UI and show window"""
        try:
            # Setup window size BEFORE showing
            self.window_manager.setup_initial_window_size()
            
            # Setup UI
            self._setup_ui()
            
            # Show window
            self.window_manager.show_and_activate()
            
        except Exception as e:
            print(f"❌ Setup and show failed: {e}")
            traceback.print_exc()
    
    def _schedule_delayed_initialization(self):
        """Schedule delayed initialization tasks"""
        # Window maximization
        self.window_manager.schedule_maximization_attempts()
        
        # Theme and setup
        QTimer.singleShot(100, self._apply_theme)
        QTimer.singleShot(200, self._apply_auto_switch_blocking)
        QTimer.singleShot(300, self._post_initialization)
        
        # Debug checks
        QTimer.singleShot(500, self.debug_manager.debug_component_status)
        QTimer.singleShot(1000, self.debug_manager.debug_signal_connections)
        QTimer.singleShot(2000, self.tab_manager.debug_tab_switching)
    
    def _setup_ui(self):
        """Setup the main UI"""
        try:
            print("🔧 Setting up main UI...")
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            main_layout.setSpacing(10)
            
            # Setup toolbar
            self._setup_toolbar()
            
            # Initialize component references
            self.component_manager.initialize_component_references()
            
            # Initialize building generator
            self.building_manager.initialize_building_generator()
            
            # Create UI components
            self.component_manager.create_ui_components()
            
            # Setup layout
            if self.left_panel and self.content_tabs:
                main_layout.addWidget(self.left_panel)
                main_layout.addWidget(self.content_tabs)
                main_layout.setStretch(0, 1)  # Left panel
                main_layout.setStretch(1, 3)  # Content tabs
                print("✅ Main layout created successfully")
            else:
                self.component_manager.create_fallback_ui(main_layout)
                print("⚠️ Using fallback UI")
            
            # Setup integration
            self.component_manager.setup_integration()
            
            # Connect signals
            self.signal_manager.connect_all_signals()
            
            # Initialize status bar
            self.statusBar().showMessage("PVmizer GEO Enhanced - Initializing...", 3000)
            
            print("✅ Main UI setup completed")
            
        except Exception as e:
            print(f"❌ UI setup failed: {e}")
            traceback.print_exc()
    
    def _setup_toolbar(self):
        """Setup toolbar"""
        if ToolbarManager:
            try:
                self.toolbar_manager = ToolbarManager(self)
                
                if hasattr(self.toolbar_manager, 'setup_toolbar'):
                    self.toolbar_manager.setup_toolbar()
                
                if hasattr(self.toolbar_manager, 'toolbar'):
                    toolbar = self.toolbar_manager.toolbar
                    if toolbar:
                        self.addToolBar(toolbar)
                        toolbar.setVisible(True)
                        print("✅ Toolbar setup completed")
                
            except Exception as e:
                print(f"❌ Toolbar setup failed: {e}")
        else:
            print("⚠️ ToolbarManager not available")
    
    def _apply_theme(self):
        """Apply theme using theme manager"""
        try:
            if self.theme_manager:
                self.theme_manager.apply_theme()
                print("✅ Theme applied")
            else:
                print("⚠️ No theme manager available")
        except Exception as e:
            print(f"❌ Theme application failed: {e}")
    
    # ==========================================
    # ROOF BUTTON HANDLERS
    # ==========================================
    
    def handle_flat_roof_button(self):
        """Handle flat roof button click"""
        print("🏠 Flat roof button clicked")
        self.tab_manager.handle_roof_button_click('flat')
    
    def handle_gable_roof_button(self):
        """Handle gable roof button click"""
        print("🏠 Gable roof button clicked")
        self.tab_manager.handle_roof_button_click('gable')
    
    def handle_hip_roof_button(self):
        """Handle hip roof button click"""
        print("🏠 Hip roof button clicked")
        self.tab_manager.handle_roof_button_click('hip')
    
    def handle_pyramid_roof_button(self):
        """Handle pyramid roof button click"""
        print("🏠 Pyramid roof button clicked")
        self.tab_manager.handle_roof_button_click('pyramid')
    
    # ==========================================
    # DELEGATION METHODS - Route to appropriate managers
    # ==========================================
    
    def _handle_snip_request(self):
        """Handle snip screenshot request"""
        self.event_manager.handle_snip_request()
    
    def _on_snip_completed(self, pixmap):
        """Handle snip completion"""
        self.event_manager.handle_snip_completed(pixmap)
    
    def _handle_generate_building_from_drawing_tab(self):
        """Handle generate building request from DrawingTabPanel"""
        self.event_manager.handle_generate_building_from_drawing_tab()
    
    def _generate_building_with_settings(self, points, settings):
        """Generate building with given points and settings"""
        return self.building_manager.generate_building_with_settings(points, settings)
    
    def _force_switch_to_model_tab(self):
        """Force switch to model tab"""
        return self.tab_manager.force_switch_to_model_tab()
    
    def _switch_to_drawing_tab_with_debug(self):
        """Switch to drawing tab with debugging"""
        return self.tab_manager.switch_to_drawing_tab_with_debug()
    
    # ==========================================
    # SIMPLE DELEGATION METHODS
    # ==========================================
    
    def _handle_search_location(self, location):
        """Handle search location request"""
        self.event_manager.handle_search_location(location)
    
    def _handle_undo_request(self):
        """Handle undo request"""
        self.event_manager.handle_undo_request()
    
    def _handle_clear_request(self):
        """Handle clear drawing request"""
        self.event_manager.handle_clear_request()
    
    def _handle_scale_change(self, scale):
        """Handle scale change"""
        self._current_scale = scale
        
    def _handle_angle_snap_toggle(self, enabled):
        """Handle angle snap toggle"""
        self.angle_snap_enabled = enabled
        print(f"🔧 Angle snap {'enabled' if enabled else 'disabled'}")
    
    def _handle_generate_building(self):
        """Handle generate building request"""
        self.event_manager.handle_generate_building()
    
    # ==========================================
    # UTILITY METHODS - Keep simple ones here
    # ==========================================
    
    def get_drawing_points(self):
        """Get current drawing points"""
        return self.canvas_manager.get_drawing_points()
    
    def get_building_settings(self):
        """Get current building settings"""
        return self.canvas_manager.get_building_settings()
    
    def switch_to_model_tab(self):
        """Switch to 3D model tab"""
        return self.tab_manager.force_switch_to_model_tab()
    
    # ==========================================
    # EVENT HANDLERS - Keep minimal
    # ==========================================
    
    def _on_building_generated(self, building_data=None):
        """Handle building generated signal"""
        self.event_manager.handle_building_generated(building_data)
    
    def _on_solar_time_changed(self, hour):
        """Handle solar time changed signal"""
        self.event_manager.handle_solar_time_changed(hour)
    
    def _on_screenshot_captured(self, *args):
        """Handle screenshot captured"""
        self.event_manager.handle_screenshot_captured(*args)
    
    # ==========================================
    # LIFECYCLE METHODS
    # ==========================================
    
    def _post_initialization(self):
        """Post-initialization tasks"""
        self.initialization_manager.post_initialization()
    
    def _apply_auto_switch_blocking(self):
        """Apply auto-switch blocking"""
        self.initialization_manager.apply_auto_switch_blocking()
    
    def _check_drawing_completion(self):
        """Check if drawing is complete"""
        return False  # Implementation moved to appropriate manager
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            print("🔧 Closing application...")
            
            # Cleanup through component manager
            self.component_manager.cleanup_components()
            
            event.accept()
            print("✅ Application closed successfully")
            
        except Exception as e:
            print(f"❌ Close event failed: {e}")
            event.accept()
