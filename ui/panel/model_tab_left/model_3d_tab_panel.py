#!/usr/bin/env python3
"""
ui/panel/model_tab_left/model_3d_tab_panel.py
FIXED Model3DTabPanel - uses separated classes and connects to model tab
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QGroupBox)
from PyQt5.QtCore import pyqtSignal

# Import centralized styles
try:
    from styles.ui_styles import (
        get_model3d_panel_style,
        get_model3d_tab_widget_style,
        get_model3d_groupbox_style,
        get_model3d_tab_content_style,
        get_model3d_error_label_style
    )
    STYLES_AVAILABLE = True
except ImportError:
    print("⚠️ Centralized styles not found")
    STYLES_AVAILABLE = False

# Import the separated control classes
try:
    from .datetime_controls import DateTimeControls
    DATETIME_CONTROLS_AVAILABLE = True
except ImportError:
    DATETIME_CONTROLS_AVAILABLE = False
    print("❌ DateTimeControls not found in ui/panel/model_tab_left")

try:
    from .location_controls import LocationControls
    LOCATION_CONTROLS_AVAILABLE = True
except ImportError:
    LOCATION_CONTROLS_AVAILABLE = False
    print("❌ LocationControls not found in ui/panel/model_tab_left")

try:
    from .modifications_tab import ModificationsTab
    MODIFICATIONS_TAB_AVAILABLE = True
except ImportError:
    MODIFICATIONS_TAB_AVAILABLE = False
    print("❌ ModificationsTab not found in ui/panel/model_tab_left")

class Model3DTabPanel(QWidget):
    """FIXED Model3DTabPanel - uses separated classes and connects to model tab"""
    
    # Signals
    solar_parameter_changed = pyqtSignal(str, object)
    animation_toggled = pyqtSignal(bool)
    solar_panel_config_changed = pyqtSignal(dict)
    obstacle_placement_requested = pyqtSignal(str, tuple)
    location_changed = pyqtSignal(float, float)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.is_dark_theme = True  # Always use dark theme for this panel
        
        # Control modules (using separated classes)
        self.datetime_controls = None
        self.location_controls = None
        self.modifications_tab = None
        self.tab_widget = None
        
        print("🌞 FIXED Model3DTabPanel initializing with separated classes...")
        
        try:
            self.setup_ui()
            self.connect_signals()
            print("✅ FIXED Model3DTabPanel setup completed with proper connections")
        except Exception as e:
            print(f"❌ Error setting up FIXED Model3DTabPanel: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup main UI using separated control classes"""
        # Set the main widget background
        self.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create tab widget with compact design
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        # Set maximum width to prevent panel expansion
        self.tab_widget.setMaximumWidth(400)
        
        # Tab 1: Modifications (using separated ModificationsTab)
        if MODIFICATIONS_TAB_AVAILABLE:
            try:
                self.modifications_tab = ModificationsTab(self.main_window)
                # Apply dark background to modifications tab
                self.modifications_tab.setStyleSheet("background-color: #2c3e50;")
                self.tab_widget.addTab(self.modifications_tab, "🔧 Mods")
                print("✅ ModificationsTab added from separated class")
            except Exception as e:
                print(f"❌ ModificationsTab creation failed: {e}")
                self._create_fallback_modifications_tab()
        else:
            self._create_fallback_modifications_tab()
        
        # Tab 2: Solar Simulation (using separated control classes)
        solar_tab = QWidget()
        solar_tab.setStyleSheet("background-color: #2c3e50;")
        self.setup_solar_simulation_tab(solar_tab)
        self.tab_widget.addTab(solar_tab, "☀️ Solar")
        
        layout.addWidget(self.tab_widget)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Apply styles after all widgets are created
        self.apply_theme_styles()
        
        print("✅ UI setup completed using separated classes")
    
    def apply_theme_styles(self):
        """Apply theme-appropriate styles to all components"""
        # Enhanced tab widget styling for better visibility
        tab_style = """
            QTabWidget {
                background-color: #2c3e50;
            }
            
            QTabWidget::pane {
                border: 1px solid #34495e;
                background-color: #2c3e50;
                border-radius: 0px;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar {
                background-color: #2c3e50;
            }
            
            QTabBar::tab {
                background-color: #34495e;
                color: #ffffff;
                border: 1px solid #3498db;
                border-bottom: none;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 80px;
                max-width: 120px;
                font-size: 12px;
                font-weight: normal;
            }
            
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
                font-weight: bold;
                padding-bottom: 10px;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #2980b9;
                color: #ffffff;
            }
            
            QTabBar::tab:!selected {
                margin-top: 2px;
                background-color: #34495e;
            }
        """
        
        self.tab_widget.setStyleSheet(tab_style)
    
    def setup_solar_simulation_tab(self, tab_widget):
        """Setup solar simulation tab using separated control classes"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Date/Time Controls (using separated DateTimeControls)
        if DATETIME_CONTROLS_AVAILABLE:
            try:
                self.datetime_controls = DateTimeControls(self.main_window)
                layout.addWidget(self.datetime_controls)
                print("✅ DateTimeControls added from separated class")
            except Exception as e:
                print(f"❌ DateTimeControls creation failed: {e}")
                self._create_fallback_datetime_controls(layout)
        else:
            self._create_fallback_datetime_controls(layout)
        
        # Location Controls (using separated LocationControls)
        if LOCATION_CONTROLS_AVAILABLE:
            try:
                self.location_controls = LocationControls(self.main_window)
                layout.addWidget(self.location_controls)
                print("✅ LocationControls added from separated class")
            except Exception as e:
                print(f"❌ LocationControls creation failed: {e}")
                self._create_fallback_location_controls(layout)
        else:
            self._create_fallback_location_controls(layout)
        
        # Add stretch
        layout.addStretch()
    
    def connect_signals(self):
        """Connect all module signals to model tab"""
        try:
            signal_count = 0
            
            # DateTime signals
            if self.datetime_controls:
                if hasattr(self.datetime_controls, 'time_changed'):
                    self.datetime_controls.time_changed.connect(self._on_time_changed)
                    signal_count += 1
                if hasattr(self.datetime_controls, 'date_changed'):
                    self.datetime_controls.date_changed.connect(self._on_date_changed)
                    signal_count += 1
                if hasattr(self.datetime_controls, 'animation_toggled'):
                    self.datetime_controls.animation_toggled.connect(self.animation_toggled)
                    signal_count += 1
            
            # Location signals
            if self.location_controls:
                if hasattr(self.location_controls, 'location_changed'):
                    self.location_controls.location_changed.connect(self._on_location_changed)
                    signal_count += 1
            
            # Modifications signals
            if self.modifications_tab:
                if hasattr(self.modifications_tab, 'solar_panel_config_changed'):
                    # Direct connection to forward method
                    self.modifications_tab.solar_panel_config_changed.connect(
                        lambda config: self._forward_to_model_tab('add_solar_panels', config)
                    )
                    signal_count += 1
                    
                if hasattr(self.modifications_tab, 'obstacle_placement_requested'):
                    self.modifications_tab.obstacle_placement_requested.connect(
                        lambda obs_type, dims: self._forward_to_model_tab('add_obstacle', obs_type, dims)
                    )
                    signal_count += 1
            
            print(f"✅ Connected {signal_count} signals to model tab")
            
        except Exception as e:
            print(f"❌ Error connecting signals: {e}")
    
    # Signal handlers that connect to model tab
    def _on_time_changed(self, decimal_time):
        """Handle time change and update model tab"""
        try:
            print(f"🕐 Time changed to {decimal_time}")
            
            # Get model tab from content tabs
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'update_solar_time'):
                model_tab.update_solar_time(decimal_time)
                print(f"✅ Updated model tab solar time to {decimal_time}")
            else:
                print("⚠️ Model tab not found or doesn't have update_solar_time method")
            
            # Also update modifications tab if it exists
            if self.modifications_tab:
                self.modifications_tab.update_solar_parameters(time=decimal_time)
            
            self.solar_parameter_changed.emit("time_of_day", decimal_time)
            
        except Exception as e:
            print(f"❌ Error updating time: {e}")
    
    def _on_date_changed(self, day_of_year):
        """Handle date change and update model tab"""
        try:
            print(f"📅 Date changed to day {day_of_year}")
            
            # Get model tab from content tabs
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'update_solar_day'):
                model_tab.update_solar_day(day_of_year)
                print(f"✅ Updated model tab solar day to {day_of_year}")
            else:
                print("⚠️ Model tab not found or doesn't have update_solar_day method")
            
            # Also update modifications tab if it exists
            if self.modifications_tab:
                self.modifications_tab.update_solar_parameters(day=day_of_year)
            
            self.solar_parameter_changed.emit("day_of_year", day_of_year)
            
        except Exception as e:
            print(f"❌ Error updating date: {e}")
            
    def _on_location_changed(self, latitude, longitude):
        """Handle location change and update model tab"""
        try:
            print(f"🌍 Location changed to {latitude}, {longitude}")
            
            # Update datetime controls with new location
            if self.datetime_controls:
                self.datetime_controls.set_location(latitude, longitude)
            
            # Get model tab from content tabs
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'set_location'):
                model_tab.set_location(latitude, longitude)
                print(f"✅ Updated model tab location to {latitude}, {longitude}")
            else:
                print("⚠️ Model tab not found or doesn't have set_location method")
            
            self.location_changed.emit(latitude, longitude)
            
        except Exception as e:
            print(f"❌ Error updating location: {e}")
    
    def _get_model_tab(self):
        """Get model tab from content tabs"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                # Look for model tab
                tab_count = self.main_window.content_tabs.count()
                for i in range(tab_count):
                    tab_text = self.main_window.content_tabs.tabText(i).lower()
                    if 'model' in tab_text or '3d' in tab_text:
                        model_tab = self.main_window.content_tabs.widget(i)
                        print(f"✅ Found model tab at index {i}: {tab_text}")
                        return model_tab
                
                print("⚠️ No model tab found in content tabs")
                return None
            else:
                print("⚠️ Main window has no content_tabs attribute")
                return None
                
        except Exception as e:
            print(f"❌ Error getting model tab: {e}")
            return None
    
    # Fallback methods for missing control classes
    def _create_fallback_modifications_tab(self):
        """Create fallback modifications tab"""
        fallback_widget = QWidget()
        fallback_widget.setStyleSheet("background-color: #2c3e50;")
        layout = QVBoxLayout(fallback_widget)
        
        label = QLabel("⚠️ ModificationsTab class not found\nPlease check ui/panel/model_tab_left/modifications_tab.py")
        label.setWordWrap(True)
        if STYLES_AVAILABLE:
            label.setStyleSheet(get_model3d_error_label_style(self.is_dark_theme))
        else:
            label.setStyleSheet("""
                color: #e74c3c;
                font-size: 11px;
                padding: 10px;
                background-color: rgba(231, 76, 60, 0.1);
                border: 1px solid #e74c3c;
                border-radius: 4px;
            """)
        layout.addWidget(label)
        
        self.tab_widget.addTab(fallback_widget, "🔧 Mods (Missing)")
        print("⚠️ Using fallback modifications tab")
    
    def _create_fallback_datetime_controls(self, layout):
        """Create fallback datetime controls"""
        group = QGroupBox("📅 Date & Time Control (Missing)")
        
        # Apply GroupBox styling
        if STYLES_AVAILABLE:
            group.setStyleSheet(get_model3d_groupbox_style(self.is_dark_theme))
        else:
            group.setStyleSheet("""
                QGroupBox {
                    background-color: #34495e;
                    border: 1px solid #3498db;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 12px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QGroupBox::title {
                    color: #3498db;
                    background-color: #34495e;
                }
            """)
        
        group_layout = QVBoxLayout(group)
        label = QLabel("⚠️ DateTimeControls class not found\nPlease check ui/panel/model_tab_left/datetime_controls.py")
        label.setWordWrap(True)
        label.setStyleSheet("color: #e74c3c; padding: 10px;")
        group_layout.addWidget(label)
        
        layout.addWidget(group)
        print("⚠️ Using fallback datetime controls")
    
    def _create_fallback_location_controls(self, layout):
        """Create fallback location controls"""
        group = QGroupBox("🌍 Location Settings (Missing)")
        
        # Apply GroupBox styling
        if STYLES_AVAILABLE:
            group.setStyleSheet(get_model3d_groupbox_style(self.is_dark_theme))
        else:
            group.setStyleSheet("""
                QGroupBox {
                    background-color: #34495e;
                    border: 1px solid #3498db;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 12px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QGroupBox::title {
                    color: #3498db;
                    background-color: #34495e;
                }
            """)
        
        group_layout = QVBoxLayout(group)
        label = QLabel("⚠️ LocationControls class not found\nPlease check ui/panel/model_tab_left/location_controls.py")
        label.setWordWrap(True)
        label.setStyleSheet("color: #e74c3c; padding: 10px;")
        group_layout.addWidget(label)
        
        layout.addWidget(group)
        print("⚠️ Using fallback location controls")
    
    # Public API methods
    def get_current_date_time(self):
        """Get current date and time from datetime controls"""
        try:
            if self.datetime_controls and hasattr(self.datetime_controls, 'get_current_date_time'):
                return self.datetime_controls.get_current_date_time()
            return None
        except Exception as e:
            print(f"❌ Error getting current date time: {e}")
            return None
    
    def get_location(self):
        """Get current location from location controls"""
        try:
            if self.location_controls and hasattr(self.location_controls, 'get_location'):
                return self.location_controls.get_location()
            return (48.3061, 18.0764)  # Default Nitra
        except Exception as e:
            print(f"❌ Error getting location: {e}")
            return (48.3061, 18.0764)
    
    def update_theme(self, is_dark_theme):
        """Update theme for the panel (always dark for this panel)"""
        self.is_dark_theme = True  # Always dark
        self.apply_theme_styles()
        
        # Update child controls if they have theme update methods
        if self.datetime_controls and hasattr(self.datetime_controls, 'update_theme'):
            self.datetime_controls.update_theme(True)
        
        if self.location_controls and hasattr(self.location_controls, 'update_theme'):
            self.location_controls.update_theme(True)
        
        if self.modifications_tab and hasattr(self.modifications_tab, 'update_theme'):
            self.modifications_tab.update_theme(True)
    
    def cleanup(self):
        """Cleanup all modules"""
        try:
            if self.datetime_controls and hasattr(self.datetime_controls, 'cleanup'):
                self.datetime_controls.cleanup()
            
            if self.modifications_tab and hasattr(self.modifications_tab, 'cleanup'):
                self.modifications_tab.cleanup()
            
            if self.location_controls and hasattr(self.location_controls, 'cleanup'):
                self.location_controls.cleanup()
            
            print("✅ Model3DTabPanel cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    def _forward_to_model_tab(self, method_name, *args):
        """Generic forwarder to model tab methods"""
        try:
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, method_name):
                method = getattr(model_tab, method_name)
                result = method(*args)
                print(f"✅ Called {method_name} on model tab with result: {result}")
                return result
            else:
                print(f"⚠️ Model tab doesn't have {method_name} method")
                
        except Exception as e:
            print(f"❌ Error forwarding to model tab: {e}")
            import traceback
            traceback.print_exc()
