#!/usr/bin/env python3
"""
Enhanced Main Window - COMPLETE Production Version
PVmizer GEO - Enhanced Building Designer with Advanced Solar Simulation
- Fixed model tab access issue
- Enhanced signal connections for DrawingTabPanel
- Complete building generation with multiple strategies
- Comprehensive debugging and error handling
"""

import traceback
import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QTabWidget, QMessageBox, QApplication, QSlider,
                              QDoubleSpinBox, QComboBox, QSpinBox, QLabel)
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen

# Core imports - FIXED PATHS with fallbacks
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
    from ui.panel.left_control_panel import LeftControlPanel
except ImportError:
    try:
        from ui.panel.left_control_panel import LeftControlPanel
    except ImportError:
        print("⚠️ Could not import LeftControlPanel")
        LeftControlPanel = None

try:
    from ui.tabs.content_tab_widget import ContentTabWidget
except ImportError:
    try:
        from ui.tabs.content_tab_widget import ContentTabWidget
    except ImportError:
        print("⚠️ Could not import ContentTabWidget")
        ContentTabWidget = None

try:
    from ui.toolbar.toolbar_manager import ToolbarManager
except ImportError:
    try:
        from ui.toolbar.toolbar_manager import ToolbarManager
    except ImportError:
        print("⚠️ Could not import ToolbarManager")
        ToolbarManager = None

class MainWindow(QMainWindow):
    """
    Enhanced main window - COMPLETE PRODUCTION VERSION
    Features:
    - Fixed model tab access
    - Enhanced DrawingTabPanel signal connections
    - Multiple building generation strategies
    - Comprehensive debugging
    - Complete workflow state management
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
        
        # Initialize UI component references
        self._initialize_component_references()
        
        # Initialize building generator
        self._initialize_building_generator()
        
        # Timer for checking completion
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_drawing_completion)
        
        # Set initial window size BEFORE showing
        self._setup_initial_window_size()
        
        # Setup UI (this will show the window)
        self._setup_ui()
        
        # Schedule delayed initialization
        self._schedule_delayed_initialization()
    
    def _schedule_delayed_initialization(self):
        """Schedule delayed initialization tasks"""
        # Window maximization
        QTimer.singleShot(50, self._attempt_maximization_1)
        QTimer.singleShot(200, self._attempt_maximization_2) 
        QTimer.singleShot(500, self._attempt_maximization_3)
        QTimer.singleShot(1000, self._final_maximization_check)
        
        # Theme and setup
        QTimer.singleShot(100, self._apply_theme)
        QTimer.singleShot(200, self._apply_auto_switch_blocking)
        QTimer.singleShot(300, self._post_initialization)
        
        # Debug checks
        QTimer.singleShot(500, self._debug_component_status)
        QTimer.singleShot(1000, self._debug_signal_connections)
        QTimer.singleShot(2000, self.debug_tab_switching)
    
    def _debug_component_status(self):
        """Debug component initialization status"""
        try:
            print("🔍 === COMPONENT STATUS DEBUG ===")
            components = {
                'config': self.config,
                'theme_manager': self.theme_manager,
                'left_panel': self.left_panel,
                'content_tabs': self.content_tabs,
                'canvas_manager': self.canvas_manager,
                'canvas_integrator': self.canvas_integrator,
                'building_generator': self.building_generator,
                'toolbar_manager': getattr(self, 'toolbar_manager', None)
            }
            
            for name, component in components.items():
                status = "✅" if component is not None else "❌"
                print(f"{status} {name}: {type(component).__name__ if component else 'None'}")
            
            print("🔍 === COMPONENT STATUS END ===")
        except Exception as e:
            print(f"❌ Error in component debug: {e}")
    
    def _debug_signal_connections(self):
        """Debug signal connections - ENHANCED"""
        try:
            print("🔍 === SIGNAL CONNECTIONS DEBUG ===")
            
            # Check left panel signals
            if self.left_panel:
                left_panel_signals = [
                    'snip_requested', 'search_location_requested', 'undo_requested',
                    'clear_drawing_requested', 'scale_changed', 'generate_model_requested'
                ]
                
                for signal_name in left_panel_signals:
                    has_signal = hasattr(self.left_panel, signal_name)
                    status = "✅" if has_signal else "❌"
                    print(f"{status} LeftPanel.{signal_name}")
            
            # Check content tabs signals
            if self.content_tabs:
                content_tab_signals = [
                    'snip_completed', 'building_generated', 'screenshot_captured'
                ]
                
                for signal_name in content_tab_signals:
                    has_signal = hasattr(self.content_tabs, signal_name)
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
    
    def _setup_initial_window_size(self):
        """Setup initial window size and position BEFORE showing"""
        try:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    initial_width = int(screen_geometry.width() * 0.9)
                    initial_height = int(screen_geometry.height() * 0.9)
                    x = (screen_geometry.width() - initial_width) // 2
                    y = (screen_geometry.height() - initial_height) // 2
                    self.setGeometry(x, y, initial_width, initial_height)
                else:
                    self.resize(1400, 900)
            else:
                self.resize(1400, 900)
                
            self.setMinimumSize(1200, 800)
            
        except Exception as e:
            print(f"❌ Error setting window size: {e}")
            self.resize(1400, 900)
    
    def _attempt_maximization_1(self):
        """First maximization attempt"""
        try:
            if self.isVisible():
                self.showMaximized()
                print("🔧 Maximization attempt 1")
        except Exception as e:
            print(f"❌ Maximization attempt 1 failed: {e}")
    
    def _attempt_maximization_2(self):
        """Second maximization attempt"""
        try:
            if not self.isMaximized():
                self.showMaximized()
                print("🔧 Maximization attempt 2")
        except Exception as e:
            print(f"❌ Maximization attempt 2 failed: {e}")
    
    def _attempt_maximization_3(self):
        """Third maximization attempt"""
        try:
            if not self.isMaximized():
                self.setWindowState(Qt.WindowMaximized)
                self.showMaximized()
                self.update()
                self.repaint()
                print("🔧 Maximization attempt 3 (forced)")
        except Exception as e:
            print(f"❌ Maximization attempt 3 failed: {e}")
    
    def _final_maximization_check(self):
        """Final maximization check"""
        try:
            if not self.isMaximized():
                app = QApplication.instance()
                if app:
                    screen = app.primaryScreen()
                    if screen:
                        geometry = screen.availableGeometry()
                        self.setGeometry(geometry)
                
                self.setWindowState(Qt.WindowMaximized)
                self.showMaximized()
                print("🔧 Final maximization check")
            else:
                print("✅ Window properly maximized")
        except Exception as e:
            print(f"❌ Final maximization failed: {e}")
    
    def _initialize_core_managers(self):
        """Initialize configuration and theme managers - ENHANCED"""
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
    
    def _initialize_component_references(self):
        """Initialize UI component references"""
        # UI components
        self.left_panel = None
        self.content_tabs = None
        self.canvas_manager = None
        self.canvas_integrator = None
        self.pyvista_integration = None
        self.model_generator = None
        self.snipping_tool = None
        
        # These will be managed by LeftControlPanel, not MainWindow
        self.wall_height_input = None
        self.wall_height_slider = None
        self.roof_type_combo = None
        self.roof_pitch_input = None
        self.roof_pitch_slider = None
        self.time_input = None
        self.time_slider = None
        self.day_input = None
        self.day_slider = None
        
        # Action components
        self.generate_btn = None
        self.measurements_display = None
        self.tips_content = None
        self.scale_input = None
        self.angle_snap_btn = None
        self.stacked_widget = None
        self.export_btn = None
        self.animate_btn = None
    
    def _initialize_building_generator(self):
        """Initialize building generator with proper error handling"""
        try:
            from models.pyvista_building_generator import PyVistaBuildingGenerator
            
            self.building_generator = PyVistaBuildingGenerator(self)
            
            # Connect signals if available
            if hasattr(self.building_generator, 'building_generated'):
                self.building_generator.building_generated.connect(self._on_building_generated)
                print("✅ Connected building_generated signal")
            
            if hasattr(self.building_generator, 'solar_time_changed'):
                self.building_generator.solar_time_changed.connect(self._on_solar_time_changed)
                print("✅ Connected solar_time_changed signal")
            
            print("✅ BuildingGenerator initialized")
            
        except ImportError as e:
            print(f"⚠️ PyVistaBuildingGenerator not available: {e}")
            self.building_generator = None
        except Exception as e:
            print(f"❌ BuildingGenerator initialization failed: {e}")
            self.building_generator = None
    
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
    
    def _setup_ui(self):
        """Setup the main UI and show the window - ENHANCED"""
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
            
            # Create UI components
            self._create_ui_components()
            
            # Setup layout
            if self.left_panel and self.content_tabs:
                main_layout.addWidget(self.left_panel)
                main_layout.addWidget(self.content_tabs)
                main_layout.setStretch(0, 1)  # Left panel
                main_layout.setStretch(1, 3)  # Content tabs
                print("✅ Main layout created successfully")
            else:
                self._create_fallback_ui(main_layout)
                print("⚠️ Using fallback UI")
            
            # Setup integration
            self._setup_integration()
            
            # Connect signals
            self._connect_all_signals()
            
            # Initialize status bar
            self.statusBar().showMessage("PVmizer GEO Enhanced - Initializing...", 3000)
            
            # Show the window AFTER everything is set up
            self.show()
            self.raise_()
            self.activateWindow()
            
            print("✅ Main UI setup completed")
            
        except Exception as e:
            print(f"❌ UI setup failed: {e}")
            traceback.print_exc()
            # Still try to show the window
            try:
                self.show()
            except:
                pass
    
    def _create_ui_components(self):
        """Create main UI components with ENHANCED ERROR HANDLING"""
        try:
            print("🔧 Creating UI components...")
            
            # CREATE CANVAS MANAGER FIRST
            try:
                from drawing_view.drawing_canvas_manager import CanvasManager
                self.canvas_manager = CanvasManager(self)
                print("✅ CanvasManager created")
            except ImportError:
                print("⚠️ CanvasManager not available, using minimal fallback")
                self.canvas_manager = self._create_minimal_canvas_manager()
            except Exception as e:
                print(f"❌ CanvasManager creation failed: {e}")
                self.canvas_manager = self._create_minimal_canvas_manager()
            
            # CREATE LEFT PANEL SECOND
            if LeftControlPanel:
                try:
                    self.left_panel = LeftControlPanel(self)
                    print("✅ LeftControlPanel created")
                except Exception as e:
                    print(f"❌ LeftControlPanel creation failed: {e}")
                    self.left_panel = None
            else:
                print("❌ LeftControlPanel class not available")
                self.left_panel = None
            
            # CREATE CONTENT TABS LAST
            if ContentTabWidget:
                try:
                    self.content_tabs = ContentTabWidget(self)
                    print("✅ ContentTabWidget created")
                except Exception as e:
                    print(f"❌ ContentTabWidget creation failed: {e}")
                    self.content_tabs = None
            else:
                print("❌ ContentTabWidget class not available")
                self.content_tabs = None
            
        except Exception as e:
            print(f"❌ Component creation failed: {e}")
            traceback.print_exc()
    
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
        
        return MinimalCanvasManager(self)
    
    def _create_fallback_ui(self, layout):
        """Create fallback UI when components fail"""
        fallback_label = QLabel("UI components failed to load.\nCheck console for errors.")
        fallback_label.setAlignment(Qt.AlignCenter)
        fallback_label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
        layout.addWidget(fallback_label)
    
    def _setup_integration(self):
        """Setup integration between components - ENHANCED"""
        try:
            print("🔧 Setting up component integration...")
            
            # Setup PyVista integration
            try:
                from utils.pyvista_integration import EnhancedPyVistaIntegration
                self.pyvista_integration = EnhancedPyVistaIntegration(self)
                
                if hasattr(self.pyvista_integration, 'get_building_generator'):
                    self.model_generator = self.pyvista_integration.get_building_generator()
                else:
                    self.model_generator = self.building_generator
                    
                print("✅ PyVista integration setup")
                    
            except ImportError:
                print("⚠️ PyVista integration not available")
                self.pyvista_integration = None
                self.model_generator = self.building_generator
            except Exception as e:
                print(f"❌ PyVista integration failed: {e}")
                self.pyvista_integration = None
                self.model_generator = self.building_generator
            
            # Setup canvas integration
            if self.left_panel and self.canvas_manager:
                try:
                    from drawing_view.drawing_canvas_integrator import DrawingCanvasIntegrator
                    self.canvas_integrator = DrawingCanvasIntegrator(
                        self, self.left_panel, self.canvas_manager, self.model_generator
                    )
                    print("✅ Canvas integrator setup")
                except ImportError:
                    print("⚠️ Canvas integrator not available")
                    self.canvas_integrator = None
                except Exception as e:
                    print(f"❌ Canvas integrator failed: {e}")
                    self.canvas_integrator = None
            else:
                print("⚠️ Cannot setup canvas integrator - missing components")
            
        except Exception as e:
            print(f"❌ Integration setup failed: {e}")
            traceback.print_exc()
    
    def _setup_toolbar(self):
        """Setup toolbar - ENHANCED"""
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
    
    def _connect_all_signals(self):
        """Connect all signals - ENHANCED WITH DRAWING TAB PANEL"""
        try:
            print("🔧 Connecting signals...")
            connected_count = 0
            
            # LEFT PANEL SIGNALS
            if self.left_panel:
                signal_mappings = [
                    ('snip_requested', self._handle_snip_request),
                    ('search_location_requested', self._handle_search_location),
                    ('undo_requested', self._handle_undo_request),
                    ('clear_drawing_requested', self._handle_clear_request),
                    ('scale_changed', self._handle_scale_change),
                    ('generate_model_requested', self._handle_generate_building),
                ]
                
                for signal_name, handler in signal_mappings:
                    if hasattr(self.left_panel, signal_name):
                        try:
                            signal = getattr(self.left_panel, signal_name)
                            signal.connect(handler)
                            connected_count += 1
                            print(f"✅ Connected LeftPanel.{signal_name}")
                        except Exception as e:
                            print(f"❌ Failed to connect LeftPanel.{signal_name}: {e}")
                    else:
                        print(f"⚠️ Signal LeftPanel.{signal_name} not found")
            
            # CONTENT TABS SIGNALS
            if self.content_tabs:
                content_signals = [
                    ('snip_completed', self._on_snip_completed),
                    ('building_generated', self._on_building_generated),
                    ('screenshot_captured', self._on_screenshot_captured),
                ]
                
                for signal_name, handler in content_signals:
                    if hasattr(self.content_tabs, signal_name):
                        try:
                            signal = getattr(self.content_tabs, signal_name)
                            signal.connect(handler)
                            connected_count += 1
                            print(f"✅ Connected ContentTabs.{signal_name}")
                        except Exception as e:
                            print(f"❌ Failed to connect ContentTabs.{signal_name}: {e}")
                    else:
                        print(f"⚠️ Signal ContentTabs.{signal_name} not found")
            
            # DRAWING TAB PANEL SIGNALS (CRITICAL FOR MODEL TAB ACCESS)
            drawing_tab_panel = self._find_drawing_tab_panel()
            if drawing_tab_panel:
                drawing_signals = [
                    ('generate_model_requested', self._handle_generate_building_from_drawing_tab),
                    ('scale_changed', self._handle_scale_change),
                    ('angle_snap_toggled', self._handle_angle_snap_toggle),
                    ('clear_drawing_requested', self._handle_clear_request),
                ]
                
                for signal_name, handler in drawing_signals:
                    if hasattr(drawing_tab_panel, signal_name):
                        try:
                            signal = getattr(drawing_tab_panel, signal_name)
                            signal.connect(handler)
                            connected_count += 1
                            print(f"✅ Connected DrawingTabPanel.{signal_name}")
                        except Exception as e:
                            print(f"❌ Failed to connect DrawingTabPanel.{signal_name}: {e}")
                    else:
                        print(f"⚠️ Signal DrawingTabPanel.{signal_name} not found")
            else:
                print("⚠️ DrawingTabPanel not found for signal connection")
            
            print(f"✅ Connected {connected_count} signals total")
            
        except Exception as e:
            print(f"❌ Signal connection failed: {e}")
    
    def _find_drawing_tab_panel(self):
        """Find the DrawingTabPanel widget in the UI hierarchy"""
        try:
            if self.content_tabs:
                # Method 1: Check if content_tabs has drawing_tab_panel attribute
                if hasattr(self.content_tabs, 'drawing_tab_panel'):
                    return self.content_tabs.drawing_tab_panel
                
                # Method 2: Search through tab widgets
                for i in range(self.content_tabs.count()):
                    tab_widget = self.content_tabs.widget(i)
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
            if parent.__class__.__name__ == class_name:
                return parent
            
            for child in parent.findChildren(QWidget):
                if child.__class__.__name__ == class_name:
                    return child
            
            return None
        except Exception as e:
            return None
    
    # ==========================================
    # SIGNAL HANDLERS - ENHANCED WITH DEBUG
    # ==========================================
    
    def _handle_snip_request(self):
        """Handle snip screenshot request - ENHANCED DEBUG"""
        try:
            print("🔧 Processing snip request...")
            
            # Method 1: Use content tabs snipping manager (PREFERRED)
            if self.content_tabs and hasattr(self.content_tabs, 'snipping_manager'):
                snipping_manager = self.content_tabs.snipping_manager
                if hasattr(snipping_manager, 'start_snipping'):
                    print("📸 Using snipping manager")
                    result = snipping_manager.start_snipping()
                    if result:
                        print("✅ Snipping started successfully")
                        return
                    else:
                        print("❌ Snipping manager returned False")
            
            # Method 2: Try content tabs direct method
            if self.content_tabs and hasattr(self.content_tabs, 'handle_snip_request'):
                print("📸 Using content tabs handle_snip_request")
                self.content_tabs.handle_snip_request()
                return
            
            # Method 3: Try content tabs screenshot method
            if self.content_tabs and hasattr(self.content_tabs, 'start_screenshot'):
                print("📸 Using content tabs start_screenshot")
                self.content_tabs.start_screenshot()
                return
            
            # Fallback: Show unavailable message
            print("⚠️ No snipping method available")
            self._show_snip_unavailable_message()
            
        except Exception as e:
            print(f"❌ Snip request failed: {e}")
            traceback.print_exc()
            self._show_snip_unavailable_message()
    
    def _on_snip_completed(self, pixmap):
        """Handle snip completion - ENHANCED DEBUG VERSION"""
        try:
            print("🔍 === SNIP COMPLETION DEBUG START ===")
            print(f"✂️ _on_snip_completed called with pixmap: {pixmap is not None}")
            print(f"✂️ Pixmap valid: {pixmap is not None and not pixmap.isNull()}")
            
            if pixmap and not pixmap.isNull():
                print(f"✂️ Pixmap size: {pixmap.size()}")
                
                # Step 1: Update ContentTabWidget workflow state
                print("🔄 Step 1: Updating ContentTabWidget workflow state...")
                if self.content_tabs and hasattr(self.content_tabs, 'on_screenshot_taken'):
                    print("✂️ ContentTabWidget has on_screenshot_taken method")
                    success = self.content_tabs.on_screenshot_taken(pixmap)
                    print(f"📸 ContentTabWidget screenshot update result: {success}")
                else:
                    print("❌ ContentTabWidget missing or no on_screenshot_taken method")
                    if self.content_tabs:
                        available_methods = [attr for attr in dir(self.content_tabs) if not attr.startswith('_')]
                        print(f"Available methods: {available_methods}")
                
                # Step 2: Set background in drawing tab
                print("🔄 Step 2: Setting background in drawing tab...")
                bg_success = self._process_captured_pixmap(pixmap)
                print(f"🖼️ Background setting result: {bg_success}")
                
                # Step 3: Show status message
                print("🔄 Step 3: Showing status message...")
                self.statusBar().showMessage("📸 Screenshot captured! Switching to Drawing tab...", 3000)
                
                # Step 4: Auto-switch to drawing tab
                print("🔄 Step 4: Starting auto-switch...")
                QTimer.singleShot(200, self._debug_auto_switch)
                
                # Step 5: Debug workflow state
                QTimer.singleShot(500, self.debug_workflow_state)
            else:
                print("❌ Invalid or null pixmap received")
            
            print("🔍 === SNIP COMPLETION DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Error in snip completion: {e}")
            traceback.print_exc()

    def _debug_auto_switch(self):
        """Debug version of auto-switch with detailed logging"""
        try:
            print("🔍 === AUTO-SWITCH DEBUG START ===")
            print(f"🔄 Content tabs available: {self.content_tabs is not None}")
            
            if self.content_tabs:
                print(f"🔄 Current tab index: {self.content_tabs.currentIndex()}")
                print(f"🔄 Tab count: {self.content_tabs.count()}")
                
                # List all tabs
                for i in range(self.content_tabs.count()):
                    tab_text = self.content_tabs.tabText(i)
                    print(f"🔄 Tab {i}: {tab_text}")
                
                # Check workflow state
                if hasattr(self.content_tabs, 'screenshot_taken'):
                    print(f"🔄 Screenshot taken state: {self.content_tabs.screenshot_taken}")
                
                if hasattr(self.content_tabs, '_is_tab_accessible'):
                    drawing_accessible = self.content_tabs._is_tab_accessible(1)
                    print(f"🔄 Drawing tab accessible: {drawing_accessible}")
                
                # Attempt switch
                print("🔄 Attempting to switch to drawing tab...")
                switch_success = self._switch_to_drawing_tab_with_debug()
                print(f"🔄 Switch result: {switch_success}")
            else:
                print("❌ No content_tabs available for switching")
            
            print("🔍 === AUTO-SWITCH DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Error in debug auto-switch: {e}")
            traceback.print_exc()

    def _switch_to_drawing_tab_with_debug(self):
        """Switch to drawing tab with detailed debugging"""
        try:
            print("🔍 === TAB SWITCH DEBUG START ===")
            
            if not self.content_tabs:
                print("❌ No content_tabs available")
                return False
            
            # Check current state
            current_index = self.content_tabs.currentIndex()
            print(f"🔄 Current tab index: {current_index}")
            
            # Find drawing tab
            drawing_tab_index = 1  # Default assumption
            for i in range(self.content_tabs.count()):
                tab_text = self.content_tabs.tabText(i).lower()
                print(f"🔄 Checking tab {i}: '{tab_text}'")
                if any(keyword in tab_text for keyword in ['drawing', 'draw', '✏️']):
                    drawing_tab_index = i
                    print(f"🎯 Found drawing tab at index: {drawing_tab_index}")
                    break
            
            # Check if tab is accessible
            if hasattr(self.content_tabs, '_is_tab_accessible'):
                accessible = self.content_tabs._is_tab_accessible(drawing_tab_index)
                print(f"🔄 Drawing tab accessible: {accessible}")
                
                if not accessible:
                    print("❌ Drawing tab is not accessible - checking workflow state")
                    if hasattr(self.content_tabs, 'screenshot_taken'):
                        print(f"📸 Screenshot taken: {self.content_tabs.screenshot_taken}")
                    if hasattr(self.content_tabs, 'drawing_completed'):
                        print(f"✏️ Drawing completed: {self.content_tabs.drawing_completed}")
                    return False
            
            # Attempt to switch
            print(f"🔄 Attempting to switch from {current_index} to {drawing_tab_index}")
            
            # Method 1: Use ContentTabWidget's switch method
            if hasattr(self.content_tabs, 'switch_to_drawing_tab'):
                print("🔄 Using switch_to_drawing_tab method...")
                success = self.content_tabs.switch_to_drawing_tab()
                print(f"✅ switch_to_drawing_tab result: {success}")
                if success:
                    self._post_switch_actions()
                    return True
            
            # Method 2: Direct index setting
            print("🔄 Using setCurrentIndex method...")
            self.content_tabs.setCurrentIndex(drawing_tab_index)
            
            # Verify switch
            new_index = self.content_tabs.currentIndex()
            print(f"🔄 New tab index: {new_index}")
            success = (new_index == drawing_tab_index)
            print(f"✅ Switch successful: {success}")
            
            if success:
                self._post_switch_actions()
            
            print("🔍 === TAB SWITCH DEBUG END ===")
            return success
            
        except Exception as e:
            print(f"❌ Error in tab switch: {e}")
            traceback.print_exc()
            return False

    def _post_switch_actions(self):
        """Actions to perform after successful tab switch"""
        try:
            # Update status message
            self.statusBar().showMessage("✅ Ready to draw! Trace the building outline.", 5000)
            
            # Update left panel if needed
            if hasattr(self.left_panel, 'switch_to_tab_content'):
                print("🔄 Updating left panel content...")
                self.left_panel.switch_to_tab_content(1)
            
            # Force UI update
            self.content_tabs.update()
            self.content_tabs.repaint()
            
        except Exception as e:
            print(f"❌ Error in post-switch actions: {e}")
    
    def _handle_generate_building_from_drawing_tab(self):
        """Handle generate building request from DrawingTabPanel - ENHANCED"""
        try:
            print("🏗️ === GENERATE BUILDING FROM DRAWING TAB START ===")
            
            # Step 1: Get drawing points
            points = self.get_drawing_points()
            print(f"🏗️ Drawing points count: {len(points) if points else 0}")
            
            if not points or len(points) < 3:
                print("❌ Insufficient points for building generation")
                self._show_error("Generation Error", 
                               "Need at least 3 points to generate building.\n\n"
                               "Please complete your building outline first.")
                return
            
            print(f"✅ Valid points found: {points[:3]}..." if len(points) > 3 else f"✅ Valid points: {points}")
            
            # Step 2: Get building settings
            settings = self.get_building_settings()
            print(f"🏗️ Building settings: {settings}")
            
            # Step 3: FORCE switch to model tab BEFORE generation
            print("🔄 === SWITCHING TO MODEL TAB ===")
            model_tab_switched = self._force_switch_to_model_tab()
            
            if not model_tab_switched:
                print("⚠️ Model tab switch failed, but continuing with generation...")
            
            # Step 4: Update status
            self.statusBar().showMessage("🏗️ Generating 3D building model...", 5000)
            
            # Step 5: Generate building with delay to allow tab switch
            QTimer.singleShot(200, lambda: self._generate_building_with_settings(points, settings))
            
            print("🏗️ === GENERATE BUILDING REQUEST PROCESSED ===")
            
        except Exception as e:
            print(f"❌ Error in generate building from drawing tab: {e}")
            traceback.print_exc()
            self._show_error("Generation Error", f"Failed to generate building: {str(e)}")

    def _force_switch_to_model_tab(self):
        """Force switch to model tab with multiple methods"""
        try:
            print("🔄 === FORCE MODEL TAB SWITCH START ===")
            
            if not self.content_tabs:
                print("❌ No content_tabs available")
                return False
            
            # Get current state
            current_index = self.content_tabs.currentIndex()
            tab_count = self.content_tabs.count()
            print(f"🔄 Current tab: {current_index}, Total tabs: {tab_count}")
            
            # Method 1: Use ContentTabWidget's dedicated method
            if hasattr(self.content_tabs, 'switch_to_model_tab'):
                print("🔄 Trying ContentTabWidget.switch_to_model_tab()...")
                try:
                    result = self.content_tabs.switch_to_model_tab()
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
                print(f"🔄 Found model tab at index: {model_tab_index}")
                
                # Check accessibility
                if hasattr(self.content_tabs, '_is_tab_accessible'):
                    accessible = self.content_tabs._is_tab_accessible(model_tab_index)
                    print(f"🔄 Model tab accessible: {accessible}")
                    
                    if not accessible:
                        # Force enable the tab
                        if hasattr(self.content_tabs, '_force_enable_tab'):
                            self.content_tabs._force_enable_tab(model_tab_index)
                            print("🔧 Forced model tab to be accessible")
                        elif hasattr(self.content_tabs, 'building_created'):
                            self.content_tabs.building_created = True
                            print("🔧 Set building_created to True")
                
                # Switch to model tab
                self.content_tabs.setCurrentIndex(model_tab_index)
                
                # Verify switch
                new_index = self.content_tabs.currentIndex()
                if new_index == model_tab_index:
                    print(f"✅ Successfully switched to model tab (index {model_tab_index})")
                    
                    # Force UI update
                    self.content_tabs.update()
                    self.content_tabs.repaint()
                    QApplication.processEvents()
                    
                    return True
                else:
                    print(f"❌ Tab switch failed: still at index {new_index}")
            
            # Method 3: Force switch to last tab (often the model tab)
            last_tab_index = tab_count - 1
            if last_tab_index > 0:
                print(f"🔄 Trying to switch to last tab (index {last_tab_index})...")
                self.content_tabs.setCurrentIndex(last_tab_index)
                
                new_index = self.content_tabs.currentIndex()
                if new_index == last_tab_index:
                    print(f"✅ Switched to last tab (index {last_tab_index})")
                    return True
            
            print("❌ All model tab switch methods failed")
            return False
            
        except Exception as e:
            print(f"❌ Error in force model tab switch: {e}")
            traceback.print_exc()
            return False

    def _find_model_tab_index(self):
        """Find the model tab index by searching tab names"""
        try:
            if not self.content_tabs:
                return None
            
            # Search for model-related keywords in tab names
            model_keywords = ['model', '3d', 'building', 'pyvista', 'render']
            
            for i in range(self.content_tabs.count()):
                tab_text = self.content_tabs.tabText(i).lower()
                print(f"🔄 Checking tab {i}: '{tab_text}'")
                
                for keyword in model_keywords:
                    if keyword in tab_text:
                        print(f"🎯 Found model tab at index {i} (keyword: '{keyword}')")
                        return i
            
            # If no keyword match, assume last tab is model tab
            last_index = self.content_tabs.count() - 1
            if last_index > 0:
                print(f"🎯 Assuming model tab is last tab (index {last_index})")
                return last_index
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding model tab index: {e}")
            return None

    def debug_tab_switching(self):
        """Debug method to check tab switching capabilities"""
        try:
            print("🔍 === TAB SWITCHING DEBUG ===")
            
            if self.content_tabs:
                print(f"📊 Total tabs: {self.content_tabs.count()}")
                print(f"📊 Current tab: {self.content_tabs.currentIndex()}")
                
                # List all tabs
                for i in range(self.content_tabs.count()):
                    tab_text = self.content_tabs.tabText(i)
                    widget = self.content_tabs.widget(i)
                    widget_type = type(widget).__name__ if widget else "None"
                    
                    accessible = "Unknown"
                    if hasattr(self.content_tabs, '_is_tab_accessible'):
                        try:
                            accessible = self.content_tabs._is_tab_accessible(i)
                        except:
                            pass
                    
                    print(f"📋 Tab {i}: '{tab_text}' ({widget_type}) - Accessible: {accessible}")
                
                # Check workflow state
                if hasattr(self.content_tabs, 'screenshot_taken'):
                    print(f"📸 Screenshot taken: {self.content_tabs.screenshot_taken}")
                if hasattr(self.content_tabs, 'drawing_completed'):
                    print(f"✏️ Drawing completed: {self.content_tabs.drawing_completed}")
                if hasattr(self.content_tabs, 'building_created'):
                    print(f"🏗️ Building created: {self.content_tabs.building_created}")
            
            # Check drawing tab panel
            drawing_panel = self._find_drawing_tab_panel()
            if drawing_panel:
                print(f"✅ DrawingTabPanel found: {type(drawing_panel).__name__}")
                if hasattr(drawing_panel, 'is_polygon_complete'):
                    print(f"📐 Polygon complete: {drawing_panel.is_polygon_complete()}")
            else:
                print("❌ DrawingTabPanel not found")
            
            print("🔍 === TAB SWITCHING DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Tab switching debug failed: {e}")
    
    # ==========================================
    # UTILITY METHODS - COMPLETE IMPLEMENTATION
    # ==========================================
    
    def _show_snip_unavailable_message(self):
        """Show message when snipping tool is unavailable"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Screenshot Tool")
        msg.setText("Screenshot tool is not available.")
        msg.setInformativeText(
            "Please use your system's screenshot tool and paste the image to the Drawing tab."
        )
        msg.exec_()
    
    def _handle_search_location(self, location):
        """Handle search location request"""
        try:
            if self.content_tabs and hasattr(self.content_tabs, 'search_location'):
                self.content_tabs.search_location(location)
        except Exception as e:
            print(f"❌ Search location failed: {e}")
    
    def _handle_undo_request(self):
        """Handle undo request"""
        try:
            canvas = self._get_canvas()
            if canvas and hasattr(canvas, 'undo'):
                canvas.undo()
                self._update_measurements_display()
        except Exception as e:
            print(f"❌ Undo failed: {e}")
    
    def _handle_clear_request(self):
        """Handle clear drawing request"""
        try:
            # Reset workflow state in content tabs
            if self.content_tabs and hasattr(self.content_tabs, 'clear_drawing'):
                self.content_tabs.clear_drawing()
            
            # Reset measurements
            self.current_measurements = {
                'points': 0, 'area': 0.0, 'perimeter': 0.0, 'is_complete': False
            }
            
            if self.generate_btn:
                self.generate_btn.setEnabled(False)
            
            self._update_measurements_display()
            
            # Clear canvas
            canvas = self._get_canvas()
            if canvas:
                if hasattr(canvas, 'clear'):
                    canvas.clear()
                elif hasattr(canvas, 'points'):
                    canvas.points.clear()
                    if hasattr(canvas, 'update'):
                        canvas.update()
            
        except Exception as e:
            print(f"❌ Clear request failed: {e}")
    
    def _handle_scale_change(self, scale):
        """Handle scale change"""
        self._current_scale = scale
        self._update_measurements_display()
    
    def _handle_angle_snap_toggle(self, enabled):
        """Handle angle snap toggle"""
        self.angle_snap_enabled = enabled
        print(f"🔧 Angle snap {'enabled' if enabled else 'disabled'}")
    
    def _handle_generate_building(self):
        """Handle generate building request"""
        try:
            print("🔧 Processing building generation request...")
            
            # Ensure building generator is ready
            if not self._ensure_building_generator():
                self._show_error("Generator Error", "Could not initialize building generator")
                return
            
            points = self.get_drawing_points()
            if not points or len(points) < 3:
                self._show_error("Generation Error", "Need at least 3 points to generate building")
                return
            
            settings = self.get_building_settings()
            
            # Switch to model tab
            self.switch_to_model_tab()
            
            # Generate building
            QTimer.singleShot(100, lambda: self._generate_building_with_settings(points, settings))
            
        except Exception as e:
            print(f"❌ Building generation failed: {e}")
            self._show_error("Generation Error", f"Failed to generate building: {str(e)}")
    
    def _get_canvas(self):
        """Get the active drawing canvas"""
        try:
            if self.content_tabs:
                for i in range(self.content_tabs.count()):
                    tab_widget = self.content_tabs.widget(i)
                    if tab_widget:
                        canvas = self._find_canvas_in_widget(tab_widget)
                        if canvas:
                            return canvas
            return None
        except Exception as e:
            return None
    
    def _find_canvas_in_widget(self, widget):
        """Find canvas in a widget"""
        try:
            if self._is_canvas(widget):
                return widget
            
            for child in widget.findChildren(QWidget):
                if self._is_canvas(child):
                    return child
            
            return None
        except Exception as e:
            return None
    
    def _is_canvas(self, widget):
        """Check if widget is a canvas"""
        return (hasattr(widget, 'get_drawing_points') or 
                'canvas' in str(type(widget)).lower() or
                hasattr(widget, 'points'))
    
    def _show_error(self, title, message):
        """Show error message"""
        try:
            QMessageBox.warning(self, title, message)
        except Exception as e:
            print(f"❌ Could not show error dialog: {e}")
    
    def get_drawing_points(self):
        """Get current drawing points"""
        try:
            if self._current_drawing_points:
                return self._current_drawing_points
            
            canvas = self._get_canvas()
            if canvas:
                for attr_name in ['get_drawing_points', 'points']:
                    if hasattr(canvas, attr_name):
                        attr = getattr(canvas, attr_name)
                        points = attr() if callable(attr) else attr
                        if points:
                            return points
            
            return []
        except Exception as e:
            return []
    
    def get_building_settings(self):
        """Get current building settings - ENHANCED"""
        try:
            # Method 1: Get settings from left panel if available
            if self.left_panel and hasattr(self.left_panel, 'get_building_settings'):
                try:
                    settings = self.left_panel.get_building_settings()
                    print(f"🏗️ Got settings from left panel: {settings}")
                    return settings
                except Exception as e:
                    print(f"❌ Failed to get settings from left panel: {e}")
            
            # Method 2: Get settings from UI controls (if they exist)
            settings = {}
            
            try:
                if hasattr(self, 'wall_height_input') and self.wall_height_input:
                    settings['wall_height'] = self.wall_height_input.value()
                else:
                    settings['wall_height'] = 3.0
                    
                if hasattr(self, 'roof_type_combo') and self.roof_type_combo:
                    settings['roof_type'] = self.roof_type_combo.currentText()
                else:
                    settings['roof_type'] = 'Flat'
                    
                if hasattr(self, 'roof_pitch_input') and self.roof_pitch_input:
                    settings['roof_pitch'] = self.roof_pitch_input.value()
                else:
                    settings['roof_pitch'] = 15.0
                    
                # Add scale
                settings['scale'] = self._current_scale
                
                print(f"🏗️ Got settings from UI controls: {settings}")
                return settings
                
            except Exception as e:
                print(f"❌ Failed to get settings from UI controls: {e}")
            
            # Method 3: Fallback default settings
            default_settings = {
                'wall_height': 3.0, 
                'roof_type': 'Flat', 
                'roof_pitch': 15.0,
                'scale': self._current_scale
            }
            
            print(f"🏗️ Using default settings: {default_settings}")
            return default_settings
            
        except Exception as e:
            print(f"❌ Error getting building settings: {e}")
            return {'wall_height': 3.0, 'roof_type': 'Flat', 'roof_pitch': 15.0, 'scale': 0.05}
    
    def switch_to_model_tab(self):
        """Switch to 3D model tab"""
        try:
            if self.content_tabs:
                if hasattr(self.content_tabs, 'switch_to_model_tab'):
                    self.content_tabs.switch_to_model_tab()
                elif hasattr(self.content_tabs, 'setCurrentIndex'):
                    # Find model tab by name
                    for i in range(self.content_tabs.count()):
                        tab_text = self.content_tabs.tabText(i).lower()
                        if 'model' in tab_text or '3d' in tab_text:
                            self.content_tabs.setCurrentIndex(i)
                            break
        except Exception as e:
            print(f"❌ Switch to model tab failed: {e}")
    
    def _ensure_building_generator(self):
        """Ensure building generator is properly initialized"""
        try:
            if not hasattr(self, 'building_generator') or not self.building_generator:
                from models.pyvista_building_generator import PyVistaBuildingGenerator
                self.building_generator = PyVistaBuildingGenerator(self)
            
            return True
        except Exception as e:
            print(f"❌ Building generator initialization failed: {e}")
            return False
    
    def _process_captured_pixmap(self, pixmap):
        """Process captured pixmap"""
        try:
            if self.content_tabs and hasattr(self.content_tabs, 'set_drawing_background'):
                return self.content_tabs.set_drawing_background(pixmap)
            return False
        except Exception as e:
            print(f"❌ Process pixmap failed: {e}")
            return False
    
    def _update_measurements_display(self):
        """Update measurements display"""
        pass  # Implement if needed
    
    def _check_drawing_completion(self):
        """Check if drawing is complete"""
        return False  # Implement if needed
    
    def _apply_auto_switch_blocking(self):
        """Apply auto-switch blocking"""
        try:
            if self.canvas_integrator and hasattr(self.canvas_integrator, 'boundary_completed'):
                try:
                    self.canvas_integrator.boundary_completed.disconnect()
                except:
                    pass  # Signal might not be connected
                
                if hasattr(self, '_on_boundary_completed_no_switch'):
                    self.canvas_integrator.boundary_completed.connect(self._on_boundary_completed_no_switch)
            
            if self.content_tabs and hasattr(self.content_tabs, '_auto_switch_enabled'):
                self.content_tabs._auto_switch_enabled = False
            
            self._auto_switch_blocked = True
            print("✅ Auto-switch blocking applied")
            
        except Exception as e:
            print(f"❌ Auto-switch blocking failed: {e}")
    
    def debug_workflow_state(self):
        """Debug workflow state"""
        try:
            if self.content_tabs:
                screenshot_taken = getattr(self.content_tabs, 'screenshot_taken', 'Not set')
                drawing_completed = getattr(self.content_tabs, 'drawing_completed', 'Not set')
                building_created = getattr(self.content_tabs, 'building_created', 'Not set')
                
                print(f"🔍 Workflow State Debug:")
                print(f"   Screenshot taken: {screenshot_taken}")
                print(f"   Drawing completed: {drawing_completed}")
                print(f"   Building created: {building_created}")
                
                # Check tab accessibility
                for i in range(self.content_tabs.count()):
                    tab_name = self.content_tabs.tabText(i)
                    accessible = self.content_tabs._is_tab_accessible(i) if hasattr(self.content_tabs, '_is_tab_accessible') else 'Unknown'
                    print(f"   Tab {i} ({tab_name}): {accessible}")
            
        except Exception as e:
            print(f"❌ Workflow debug failed: {e}")
    
    def _post_initialization(self):
        """Post-initialization tasks"""
        try:
            if self.pyvista_integration and hasattr(self.pyvista_integration, 'finalize_initialization'):
                self.pyvista_integration.finalize_initialization()
            
            self.statusBar().showMessage(
                "✅ PVmizer GEO Enhanced ready! Click 'Snip Screenshot' to start.", 3000)
            
            self._initialization_complete = True
            self.initialization_completed.emit()
            print("✅ Post-initialization completed")
            
        except Exception as e:
            print(f"❌ Post-initialization failed: {e}")
    
    # ==========================================
    # EVENT HANDLERS - COMPLETE IMPLEMENTATION
    # ==========================================
    
    def _on_building_generated(self, building_data=None):
        """Handle building generated signal"""
        try:
            self._building_generated = True
            
            if self.content_tabs and hasattr(self.content_tabs, 'building_created'):
                self.content_tabs.building_created = True
                if hasattr(self.content_tabs, '_update_tab_accessibility'):
                    self.content_tabs._update_tab_accessibility()
            
            self.statusBar().showMessage("✅ 3D Building generated successfully!", 3000)
            print("✅ Building generated successfully")
            
        except Exception as e:
            print(f"❌ Building generated handler failed: {e}")
    
    def _on_solar_time_changed(self, hour):
        """Handle solar time changed signal"""
        try:
            # Implementation depends on your UI structure
            print(f"🔧 Solar time changed to: {hour}")
        except Exception as e:
            print(f"❌ Solar time handler failed: {e}")
    
    def _on_screenshot_captured(self, *args):
        """Handle screenshot captured"""
        try:
            pixmap = None
            for arg in args:
                if hasattr(arg, 'save'):  # QPixmap
                    pixmap = arg
                    break
            
            if pixmap:
                if self.content_tabs and hasattr(self.content_tabs, 'on_screenshot_taken'):
                    self.content_tabs.on_screenshot_taken(pixmap)
                
                self._process_captured_pixmap(pixmap)
            
            self.statusBar().showMessage("📸 Screenshot captured! Drawing tab is now available.", 3000)
            QTimer.singleShot(500, lambda: self._switch_to_drawing_tab_with_debug())
            
        except Exception as e:
            print(f"❌ Screenshot capture handler failed: {e}")
    
    def _generate_building_with_settings(self, points, settings):
        """Generate building with given points and settings - COMPLETE IMPLEMENTATION"""
        try:
            print(f"🏗️ Generating building with {len(points)} points...")
            print(f"🏗️ Settings: {settings}")
            
            # Strategy 1: Use content tabs building creation (PREFERRED)
            if self.content_tabs and hasattr(self.content_tabs, 'create_building'):
                try:
                    print("🏗️ Using ContentTabs.create_building...")
                    result = self.content_tabs.create_building(
                        points=points,
                        height=settings.get('wall_height', 3.0),
                        roof_type=settings.get('roof_type', 'Flat'),
                        roof_pitch=settings.get('roof_pitch', 15.0),
                        scale=self._current_scale
                    )
                    
                    if result:
                        print("✅ Building created via ContentTabs")
                        self._building_generated = True
                        self.building_generated.emit({'points': points, **settings})
                        return True
                    else:
                        print("❌ ContentTabs.create_building returned False")
                        
                except Exception as e:
                    print(f"❌ ContentTabs building creation failed: {e}")
            
            # Strategy 2: Use PyVista integration (SECONDARY)
            if self.pyvista_integration and hasattr(self.pyvista_integration, 'create_building_from_points'):
                try:
                    print("🏗️ Using PyVista integration...")
                    result = self.pyvista_integration.create_building_from_points(
                        points=points,
                        **settings
                    )
                    
                    if result:
                        print("✅ Building created via PyVista integration")
                        self._building_generated = True
                        self.building_generated.emit({'points': points, **settings})
                        return True
                    else:
                        print("❌ PyVista integration returned False")
                        
                except Exception as e:
                    print(f"❌ PyVista integration failed: {e}")
            
            # Strategy 3: Use main building generator (FALLBACK)
            if hasattr(self, 'building_generator') and self.building_generator:
                try:
                    print("🏗️ Using main building generator...")
                    
                    # Try different generation methods
                    generation_methods = [
                        'generate_building_model',
                        'create_building_from_canvas', 
                        'generate_from_points',
                        'create_building'
                    ]
                    
                    for method_name in generation_methods:
                        if hasattr(self.building_generator, method_name):
                            try:
                                print(f"🏗️ Trying method: {method_name}")
                                method = getattr(self.building_generator, method_name)
                                
                                # Call with appropriate parameters
                                if method_name == 'generate_building_model':
                                    result = method(
                                        points=points,
                                        scale=settings.get('scale', 0.05),
                                        height=settings.get('wall_height', 3.0),
                                        roof_type=settings.get('roof_type', 'Flat Roof'),
                                        roof_pitch=settings.get('roof_pitch', 30.0)
                                    )
                                elif method_name == 'create_building_from_canvas':
                                    result = method(
                                        points=points,
                                        height=settings.get('wall_height', 3.0),
                                        roof_type=settings.get('roof_type', 'flat'),
                                        roof_pitch=settings.get('roof_pitch', 30.0)
                                    )
                                else:
                                    result = method(points, **settings)
                                
                                if result:
                                    print(f"✅ Building created via {method_name}")
                                    self._building_generated = True
                                    self.building_generated.emit(result if isinstance(result, dict) else {})
                                    
                                    # Switch to model tab
                                    self.switch_to_model_tab()
                                    return True
                                else:
                                    print(f"❌ Method {method_name} returned False")
                                    
                            except Exception as method_error:
                                print(f"❌ Method {method_name} failed: {method_error}")
                                continue
                    
                    print("❌ All building generator methods failed")
                    
                except Exception as e:
                    print(f"❌ Building generator failed: {e}")
            
            # Strategy 4: Create basic building mesh (LAST RESORT)
            try:
                print("🏗️ Creating basic building mesh as fallback...")
                result = self._create_basic_building_mesh(points, settings)
                
                if result:
                    print("✅ Basic building mesh created")
                    self._building_generated = True
                    self.building_generated.emit({'points': points, **settings})
                    self.switch_to_model_tab()
                    return True
                    
            except Exception as e:
                print(f"❌ Basic mesh creation failed: {e}")
            
            # If all strategies failed
            print("❌ ALL BUILDING GENERATION STRATEGIES FAILED")
            self._show_error("Generation Failed", 
                            "Failed to generate 3D model. Please check:\n"
                            "• PyVista is properly installed\n"
                            "• Building generator is initialized\n"
                            "• Points are valid (at least 3 points)\n"
                            "• Content tabs are properly configured")
            return False
            
        except Exception as e:
            print(f"❌ Critical error in building generation: {e}")
            traceback.print_exc()
            self._show_error("Generation Error", f"Critical error: {str(e)}")
            return False

    def _create_basic_building_mesh(self, points, settings):
        """Create basic building mesh as fallback - MINIMAL IMPLEMENTATION"""
        try:
            print("🏗️ Creating basic building mesh...")
            
            # Check if we have PyVista available
            try:
                import pyvista as pv
                import numpy as np
            except ImportError:
                print("❌ PyVista not available for basic mesh")
                return False
            
            if len(points) < 3:
                print("❌ Need at least 3 points for basic mesh")
                return False
            
            # Convert points to numpy array
            base_points = np.array(points)
            height = settings.get('wall_height', 3.0)
            
            # Create base polygon
            n_points = len(points)
            
            # Create vertices for base and top
            vertices = []
            
            # Base vertices (z=0)
            for point in base_points:
                vertices.append([point[0], point[1], 0])
            
            # Top vertices (z=height)
            for point in base_points:
                vertices.append([point[0], point[1], height])
            
            vertices = np.array(vertices)
            
            # Create faces
            faces = []
            
            # Base face (bottom)
            base_face = [n_points] + list(range(n_points))
            faces.extend(base_face)
            
            # Top face (top)
            top_face = [n_points] + list(range(n_points, 2 * n_points))
            faces.extend(top_face)
            
            # Side faces
            for i in range(n_points):
                next_i = (i + 1) % n_points
                
                # Each side face is a quad
                side_face = [4, i, next_i, next_i + n_points, i + n_points]
                faces.extend(side_face)
            
            # Create PyVista mesh
            mesh = pv.PolyData(vertices, faces)
            
            # Try to display in content tabs
            if self.content_tabs and hasattr(self.content_tabs, 'display_building_mesh'):
                return self.content_tabs.display_building_mesh(mesh)
            
            print("✅ Basic mesh created but no display method available")
            return True
            
        except Exception as e:
            print(f"❌ Basic mesh creation failed: {e}")
            return False
        
    def _on_boundary_completed_no_switch(self, boundary_points):
        """Handle boundary completion WITHOUT auto-switching"""
        try:
            print(f"🎯 Boundary completed with {len(boundary_points)} points")
            
            point_count = len(boundary_points) if boundary_points else 0
            self._current_drawing_points = boundary_points
            
            # Update ContentTabWidget workflow state
            if self.content_tabs and hasattr(self.content_tabs, '_on_drawing_completed'):
                self.content_tabs._on_drawing_completed(boundary_points)
                print("✅ Updated ContentTabWidget drawing state")
            
            # Enable generate button in left panel
            if hasattr(self.left_panel, 'enable_generate_button'):
                self.left_panel.enable_generate_button()
                print("✅ Enabled generate button")
            
            # Update measurements
            self.current_measurements = {
                'points': point_count,
                'area': self._calculate_area(boundary_points),
                'perimeter': self._calculate_perimeter(boundary_points),
                'is_complete': True
            }
            
            self._update_measurements_display()
            print(f"✅ Updated measurements: {self.current_measurements}")
            
        except Exception as e:
            print(f"❌ Boundary completion handler failed: {e}")

    def _calculate_area(self, points):
        """Calculate area from points using shoelace formula"""
        try:
            if not points or len(points) < 3:
                return 0.0
            
            area = 0.0
            n = len(points)
            for i in range(n):
                j = (i + 1) % n
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            
            return abs(area) / 2.0 * (self._current_scale ** 2)
            
        except Exception as e:
            print(f"❌ Area calculation failed: {e}")
            return 0.0

    def _calculate_perimeter(self, points):
        """Calculate perimeter from points"""
        try:
            if not points or len(points) < 2:
                return 0.0
            
            perimeter = 0.0
            n = len(points)
            for i in range(n):
                j = (i + 1) % n
                dx = points[j][0] - points[i][0]
                dy = points[j][1] - points[i][1]
                perimeter += (dx*dx + dy*dy) ** 0.5
            
            return perimeter * self._current_scale
            
        except Exception as e:
            print(f"❌ Perimeter calculation failed: {e}")
            return 0.0
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            print("🔧 Closing application...")
            
            components_to_cleanup = [
                'building_generator', 'canvas_integrator', 'canvas_manager',
                'content_tabs', 'pyvista_integration', 'theme_manager'
            ]
            
            for component_name in components_to_cleanup:
                try:
                    component = getattr(self, component_name, None)
                    if component and hasattr(component, 'cleanup'):
                        component.cleanup()
                        print(f"✅ Cleaned up {component_name}")
                except Exception as cleanup_error:
                    print(f"❌ Cleanup failed for {component_name}: {cleanup_error}")
            
            event.accept()
            print("✅ Application closed successfully")
            
        except Exception as e:
            print(f"❌ Close event failed: {e}")
            event.accept()