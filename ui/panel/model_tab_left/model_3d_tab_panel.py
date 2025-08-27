#!/usr/bin/env python3
"""
ui/panel/model_tab_left/model_3d_tab_panel.py
CLEANED - Matching left panel 450px width, no horizontal scroll
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QGroupBox, 
                            QPushButton, QProgressBar, QHBoxLayout, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette

# Import the separated control classes
try:
    from .datetime_controls import DateTimeControls
    DATETIME_CONTROLS_AVAILABLE = True
except ImportError:
    DATETIME_CONTROLS_AVAILABLE = False

try:
    from .location_controls import LocationControls
    LOCATION_CONTROLS_AVAILABLE = True
except ImportError:
    LOCATION_CONTROLS_AVAILABLE = False

try:
    from .modifications_tab import ModificationsTab
    MODIFICATIONS_TAB_AVAILABLE = True
except ImportError:
    MODIFICATIONS_TAB_AVAILABLE = False

class Model3DTabPanel(QWidget):
    """Model3DTabPanel - active tabs without visible containers, matching left panel width"""
    
    # Signals
    solar_parameter_changed = pyqtSignal(str, object)
    animation_toggled = pyqtSignal(bool)
    solar_panel_config_changed = pyqtSignal(dict)
    obstacle_placement_requested = pyqtSignal(str, tuple)
    location_changed = pyqtSignal(float, float)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.is_dark_theme = True
        
        # Control modules (using separated classes)
        self.datetime_controls = None
        self.location_controls = None
        self.modifications_tab = None
        self.tab_widget = None
        
        # Performance display components
        self.performance_power_label = None
        self.performance_energy_label = None
        self.performance_efficiency_label = None
        self.performance_progress = None
        self.irradiance_progress = None
        
        try:
            self.setup_ui()
            self.connect_signals()
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup main UI with active tabs but no visible containers, matching left panel width"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Apply your blue styling to the main widget with DEFAULT FONT SIZES
        self.setStyleSheet("""
            QWidget {
                background-color: #34495e !important;
            }
            
            /* Group Boxes with your styling and DEFAULT FONT SIZES */
            QGroupBox {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
                margin-top: 15px !important;
                padding-top: 15px !important;
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-bottom: 10px !important;
                font-weight: bold !important;
                font-size: 13px !important;
                color: #ffffff !important;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin !important;
                subcontrol-position: top center !important;
                padding: 4px 15px !important;
                margin-top: 1px !important;
                color: #5dade2 !important;
                background-color: #34495e !important;
                font-size: 20px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
            }
            
            /* Labels with your styling and DEFAULT FONT SIZES */
            QLabel {
                color: #ffffff !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 12px !important;
                font-weight: normal !important;
            }
            
            /* Buttons with your styling and DEFAULT FONT SIZES */
            QPushButton {
                background-color: #5dade2 !important;
                color: #ffffff !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 8px 12px !important;
                font-weight: bold !important;
                font-size: 13px !important;
                min-height: 32px !important;
                text-align: center !important;
            }
            
            QPushButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
                color: #ffffff !important;
            }
            
            QPushButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
            }
            
            QPushButton:disabled {
                background-color: #7f8c8d !important;
                border: 2px solid #7f8c8d !important;
                color: #95a5a6 !important;
            }
            
            QProgressBar {
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                text-align: center !important;
                font-weight: bold !important;
                min-height: 25px !important;
            }
            
            QProgressBar::chunk {
                background-color: #5dade2 !important;
                border-radius: 4px !important;
            }
        """)
        
        # Create tab widget with INVISIBLE containers but active tabs - MATCHING LEFT PANEL WIDTH
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setUsesScrollButtons(False)
        # MATCH LEFT PANEL WIDTH (450px) minus margins (20px total) = 430px max
        self.tab_widget.setMaximumWidth(430)
        self.tab_widget.setMinimumWidth(410)
        
        # Hide tab containers but keep tabs functional
        self.tab_widget.setStyleSheet("""
            /* INVISIBLE CONTAINERS - matching left panel */
            QTabWidget::pane {
                border: none !important;
                background-color: transparent !important;
                margin: 0px !important;
                padding: 0px !important;
                max-width: 430px !important;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }
            
            /* VISIBLE TABS with your blue styling - CONSTRAINED WIDTH */
            QTabBar::tab {
                background-color: #34495e !important;
                color: #b8c5ce !important;
                border: 2px solid #5dade2 !important;
                border-bottom: none !important;
                padding: 10px 16px !important;
                margin-right: 2px !important;
                border-top-left-radius: 8px !important;
                border-top-right-radius: 8px !important;
                font-size: 13px !important;
                font-weight: bold !important;
                max-width: 140px !important;
            }
            
            QTabBar::tab:selected {
                background-color: #5dade2 !important;
                color: #ffffff !important;
                font-weight: bold !important;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #3498db !important;
                color: #ffffff !important;
            }
            
            QTabBar {
                alignment: center;
                qproperty-expanding: true;
                max-width: 430px !important;
            }
            
            /* TAB CONTENT - transparent background and width constrained */
            QTabWidget > QWidget {
                background-color: transparent !important;
                max-width: 430px !important;
            }
        """)
        
        # Tab 1: Modifications (keeping original name as requested)
        if MODIFICATIONS_TAB_AVAILABLE:
            try:
                self.modifications_tab = ModificationsTab(self.main_window)
                self.tab_widget.addTab(self.modifications_tab, "🔧 Mods")
            except Exception as e:
                self._create_fallback_modifications_tab()
        else:
            self._create_fallback_modifications_tab()
        
        # Tab 2: Solar Simulation (using separated control classes)
        solar_tab = QWidget()
        self.setup_solar_simulation_tab(solar_tab)
        self.tab_widget.addTab(solar_tab, "☀️ Solar")
        
        # Tab 3: Stats (SHORTENED from Performance as requested)
        stats_tab = QWidget()
        self.setup_stats_tab(stats_tab)
        self.tab_widget.addTab(stats_tab, "📊 Stats")
        
        layout.addWidget(self.tab_widget)
        layout.addStretch()
    
    def setup_solar_simulation_tab(self, tab_widget):
        """Setup solar simulation tab with transparent background and width constraints"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Make tab content transparent and width-constrained to match left panel
        tab_widget.setStyleSheet("""
            
            QWidget {
                background-color: transparent !important;
                max-width: 410px !important;
            }
        """)
        
        # Date/Time Controls (using separated DateTimeControls)
        if DATETIME_CONTROLS_AVAILABLE:
            try:
                self.datetime_controls = DateTimeControls(self.main_window)
                layout.addWidget(self.datetime_controls)
            except Exception as e:
                self._create_fallback_datetime_controls(layout)
        else:
            self._create_fallback_datetime_controls(layout)
        
        # Location Controls (using separated LocationControls)
        if LOCATION_CONTROLS_AVAILABLE:
            try:
                self.location_controls = LocationControls(self.main_window)
                layout.addWidget(self.location_controls)
            except Exception as e:
                self._create_fallback_location_controls(layout)
        else:
            self._create_fallback_location_controls(layout)
        
        layout.addStretch()
    
    def setup_stats_tab(self, tab_widget):
        """Setup stats tab with transparent background, default font sizes, and width constraints"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        
        # Make tab content transparent and width-constrained to match left panel
        tab_widget.setStyleSheet("""
            QWidget {
                background-color: transparent !important;
                max-width: 410px !important;
            }
        """)
        
        # Current Performance Metrics with DEFAULT FONT SIZES and WIDTH CONSTRAINTS
        current_group = QGroupBox("⚡ Current Performance")
        current_group.setMaximumWidth(410)
        current_layout = QVBoxLayout(current_group)
        current_layout.setSpacing(8)
        current_layout.setContentsMargins(8, 15, 8, 8)
        
        # Power display with DEFAULT FONT SIZE
        self.performance_power_label = QLabel("Current Power: Calculating...")
        self.performance_power_label.setWordWrap(True)  # Prevent horizontal overflow
        current_layout.addWidget(self.performance_power_label)
        
        # Energy display with DEFAULT FONT SIZE
        self.performance_energy_label = QLabel("Daily Energy: Calculating...")
        self.performance_energy_label.setWordWrap(True)  # Prevent horizontal overflow
        current_layout.addWidget(self.performance_energy_label)
        
        # Efficiency display with DEFAULT FONT SIZE
        self.performance_efficiency_label = QLabel("System Efficiency: Calculating...")
        self.performance_efficiency_label.setWordWrap(True)  # Prevent horizontal overflow
        current_layout.addWidget(self.performance_efficiency_label)
        
        layout.addWidget(current_group)
        
        # Visual Indicators with DEFAULT FONT SIZES and WIDTH CONSTRAINTS
        indicators_group = QGroupBox("📊 Performance Indicators")
        indicators_group.setMaximumWidth(410)
        indicators_layout = QVBoxLayout(indicators_group)
        indicators_layout.setSpacing(8)
        indicators_layout.setContentsMargins(8, 15, 8, 8)
        
        # Irradiance progress with DEFAULT FONT SIZE
        irradiance_label = QLabel("☀️ Solar Irradiance")
        irradiance_label.setWordWrap(True)  # Prevent horizontal overflow
        indicators_layout.addWidget(irradiance_label)
        
        self.irradiance_progress = QProgressBar()
        self.irradiance_progress.setRange(0, 100)
        self.irradiance_progress.setValue(0)
        self.irradiance_progress.setTextVisible(True)
        self.irradiance_progress.setFormat("Irradiance: %p%")
        self.irradiance_progress.setMaximumHeight(25)
        self.irradiance_progress.setMaximumWidth(390)  # Constrain progress bar width
        indicators_layout.addWidget(self.irradiance_progress)
        
        # Performance progress with DEFAULT FONT SIZE
        performance_label = QLabel("⚡ System Performance")
        performance_label.setWordWrap(True)  # Prevent horizontal overflow
        indicators_layout.addWidget(performance_label)
        
        self.performance_progress = QProgressBar()
        self.performance_progress.setRange(0, 100)
        self.performance_progress.setValue(0)
        self.performance_progress.setTextVisible(True)
        self.performance_progress.setFormat("Performance: %p%")
        self.performance_progress.setMaximumHeight(25)
        self.performance_progress.setMaximumWidth(390)  # Constrain progress bar width
        indicators_layout.addWidget(self.performance_progress)
        
        layout.addWidget(indicators_group)
        
        # Controls with DEFAULT FONT SIZES and WIDTH CONSTRAINTS
        controls_group = QGroupBox("🔄 Performance Controls")
        controls_group.setMaximumWidth(410)
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(8, 15, 8, 8)
        
        # Update button with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        update_btn = QPushButton("🔄 Refresh Performance Data")
        update_btn.setMaximumHeight(32)  # Match default button height
        update_btn.setMaximumWidth(390)  # Constrain button width
        update_btn.clicked.connect(self._manual_performance_update)
        controls_layout.addWidget(update_btn)
        
        # Auto-update info with DEFAULT FONT SIZE
        auto_info = QLabel("📝 Performance data automatically updates every 30 seconds")
        auto_info.setWordWrap(True)  # Prevent horizontal overflow
        auto_info.setMaximumWidth(390)  # Constrain label width
        controls_layout.addWidget(auto_info)
        
        layout.addWidget(controls_group)
        layout.addStretch()
    
    def _manual_performance_update(self):
        """Manual performance update trigger"""
        try:
            if self.modifications_tab and hasattr(self.modifications_tab, '_update_performance'):
                self.modifications_tab._update_performance()
        except Exception as e:
            pass
    
    def connect_signals(self):
        """Connect all module signals to model tab - RESTORED ALL CONNECTIONS"""
        try:
            # DateTime signals
            if self.datetime_controls:
                if hasattr(self.datetime_controls, 'time_changed'):
                    self.datetime_controls.time_changed.connect(self._on_time_changed)
                if hasattr(self.datetime_controls, 'date_changed'):
                    self.datetime_controls.date_changed.connect(self._on_date_changed)
                if hasattr(self.datetime_controls, 'animation_toggled'):
                    self.datetime_controls.animation_toggled.connect(self.animation_toggled)
            
            # Location signals
            if self.location_controls:
                if hasattr(self.location_controls, 'location_changed'):
                    self.location_controls.location_changed.connect(self._on_location_changed)
            
            # Modifications signals - RESTORED ALL
            if self.modifications_tab:
                if hasattr(self.modifications_tab, 'solar_panel_config_changed'):
                    self.modifications_tab.solar_panel_config_changed.connect(
                        self.solar_panel_config_changed.emit
                    )
                    
                if hasattr(self.modifications_tab, 'obstacle_placement_requested'):
                    self.modifications_tab.obstacle_placement_requested.connect(
                        self.obstacle_placement_requested.emit
                    )
                
                # Connect performance updates
                if hasattr(self.modifications_tab, 'performance_updated'):
                    self.modifications_tab.performance_updated.connect(self._update_performance_display)
                
                # Connect environment signals - RESTORED
                if hasattr(self.modifications_tab, 'environment_action_requested'):
                    self.modifications_tab.environment_action_requested.connect(
                        lambda action, params: self._forward_to_model_tab('handle_environment_action', action, params)
                    )
            
        except Exception as e:
            pass
    
    def _update_performance_display(self, power, energy, efficiency, irradiance_percent=0):
        """Update performance display in the stats tab"""
        try:
            if hasattr(self, 'performance_power_label') and self.performance_power_label:
                self.performance_power_label.setText(f"Current Power: {power:.1f} kW")
            if hasattr(self, 'performance_energy_label') and self.performance_energy_label:
                self.performance_energy_label.setText(f"Daily Energy: {energy:.1f} kWh")
            if hasattr(self, 'performance_efficiency_label') and self.performance_efficiency_label:
                self.performance_efficiency_label.setText(f"System Efficiency: {efficiency:.1f}%")
            
            # Update progress bars
            if hasattr(self, 'performance_progress') and self.performance_progress:
                self.performance_progress.setValue(min(100, max(0, int(efficiency))))
            
            if hasattr(self, 'irradiance_progress') and self.irradiance_progress:
                self.irradiance_progress.setValue(min(100, max(0, int(irradiance_percent))))
                
        except Exception as e:
            pass
    
    # Signal handlers that connect to model tab - RESTORED ALL
    def _on_time_changed(self, decimal_time):
        """Handle time change and update model tab"""
        try:
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'update_solar_time'):
                model_tab.update_solar_time(decimal_time)
            
            if self.modifications_tab:
                self.modifications_tab.update_solar_parameters(time=decimal_time)
            
            self.solar_parameter_changed.emit("time_of_day", decimal_time)
            
        except Exception as e:
            pass
    
    def _on_date_changed(self, day_of_year):
        """Handle date change and update model tab"""
        try:
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'update_solar_day'):
                model_tab.update_solar_day(day_of_year)
            
            if self.modifications_tab:
                self.modifications_tab.update_solar_parameters(day=day_of_year)
            
            self.solar_parameter_changed.emit("day_of_year", day_of_year)
            
        except Exception as e:
            pass
            
    def _on_location_changed(self, latitude, longitude):
        """Handle location change and update model tab"""
        try:
            if self.datetime_controls:
                self.datetime_controls.set_location(latitude, longitude)
            
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'set_location'):
                model_tab.set_location(latitude, longitude)
            
            self.location_changed.emit(latitude, longitude)
            
        except Exception as e:
            pass
    
    def _get_model_tab(self):
        """Get model tab from content tabs"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                tab_count = self.main_window.content_tabs.count()
                for i in range(tab_count):
                    tab_text = self.main_window.content_tabs.tabText(i).lower()
                    if 'model' in tab_text or '3d' in tab_text:
                        model_tab = self.main_window.content_tabs.widget(i)
                        return model_tab
                return None
            else:
                return None
                
        except Exception as e:
            return None
    
    # Fallback methods for missing control classes
    def _create_fallback_modifications_tab(self):
        """Create fallback modifications tab with width constraints"""
        fallback_widget = QWidget()
        fallback_widget.setMaximumWidth(410)
        layout = QVBoxLayout(fallback_widget)
        
        label = QLabel("⚠️ ModificationsTab class not found\nPlease check ui/panel/model_tab_left/modifications_tab.py")
        label.setWordWrap(True)
        label.setMaximumWidth(390)
        layout.addWidget(label)
        
        self.tab_widget.addTab(fallback_widget, "🔧 Mods (Missing)")
    
    def _create_fallback_datetime_controls(self, layout):
        """Create fallback datetime controls with width constraints"""
        group = QGroupBox("📅 Date & Time Control (Missing)")
        group.setMaximumWidth(410)
        
        group_layout = QVBoxLayout(group)
        label = QLabel("⚠️ DateTimeControls class not found\nPlease check ui/panel/model_tab_left/datetime_controls.py")
        label.setWordWrap(True)
        label.setMaximumWidth(390)
        group_layout.addWidget(label)
        
        layout.addWidget(group)
    
    def _create_fallback_location_controls(self, layout):
        """Create fallback location controls with width constraints"""
        group = QGroupBox("🌍 Location Settings (Missing)")
        group.setMaximumWidth(410)
        
        group_layout = QVBoxLayout(group)
        label = QLabel("⚠️ LocationControls class not found\nPlease check ui/panel/model_tab_left/location_controls.py")
        label.setWordWrap(True)
        label.setMaximumWidth(390)
        group_layout.addWidget(label)
        
        layout.addWidget(group)
    
    # Public API methods - RESTORED ALL
    def get_current_date_time(self):
        """Get current date and time from datetime controls"""
        try:
            if self.datetime_controls and hasattr(self.datetime_controls, 'get_current_date_time'):
                return self.datetime_controls.get_current_date_time()
            return None
        except Exception as e:
            return None
    
    def get_location(self):
        """Get current location from location controls"""
        try:
            if self.location_controls and hasattr(self.location_controls, 'get_location'):
                return self.location_controls.get_location()
            return (48.3061, 18.0764)  # Default Nitra
        except Exception as e:
            return (48.3061, 18.0764)
    
    def update_theme(self, is_dark_theme):
        """Update theme for the panel"""
        self.is_dark_theme = is_dark_theme
        
        if self.datetime_controls and hasattr(self.datetime_controls, 'update_theme'):
            self.datetime_controls.update_theme(is_dark_theme)
        
        if self.location_controls and hasattr(self.location_controls, 'update_theme'):
            self.location_controls.update_theme(is_dark_theme)
        
        if self.modifications_tab and hasattr(self.modifications_tab, 'update_theme'):
            self.modifications_tab.update_theme(is_dark_theme)
    
    def cleanup(self):
        """Cleanup all modules"""
        try:
            if self.datetime_controls and hasattr(self.datetime_controls, 'cleanup'):
                self.datetime_controls.cleanup()
            
            if self.modifications_tab and hasattr(self.modifications_tab, 'cleanup'):
                self.modifications_tab.cleanup()
            
            if self.location_controls and hasattr(self.location_controls, 'cleanup'):
                self.location_controls.cleanup()
            
        except Exception as e:
            pass

    def _forward_to_model_tab(self, method_name, *args):
        """Generic forwarder to model tab methods - RESTORED"""
        try:
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, method_name):
                method = getattr(model_tab, method_name)
                result = method(*args)
                return result
            else:
                pass
                
        except Exception as e:
            import traceback
            traceback.print_exc()
