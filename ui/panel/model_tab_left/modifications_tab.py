#!/usr/bin/env python3
"""
ui/panel/model_tab_left/modifications_tab.py
Modifications tab with solar panels and obstacles for 3D model tab - Dark theme
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QProgressBar, QGroupBox, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QTimer
import math

try:
    from styles.ui_styles import (
        get_model3d_groupbox_style,
        get_model3d_button_style,
        get_model3d_label_style,
        get_model3d_progress_style
    )
    STYLES_AVAILABLE = True
except ImportError:
    STYLES_AVAILABLE = False
    print("⚠️ Styles not available for ModificationsTab")

# Import dialogs with fallback
try:
    from ui.dialogs.solar_panel_dialog import show_solar_panel_dialog
    SOLAR_PANEL_DIALOG_AVAILABLE = True
except ImportError:
    SOLAR_PANEL_DIALOG_AVAILABLE = False

try:
    from ui.dialogs.obstacle_dialogs import RoofObstacleDialogs
    OBSTACLE_DIALOG_AVAILABLE = True
except ImportError:
    OBSTACLE_DIALOG_AVAILABLE = False

class ModificationsTab(QWidget):
    """Modifications tab widget for 3D model tab - Dark theme"""
    
    # Signals
    solar_panel_config_changed = pyqtSignal(dict)
    obstacle_placement_requested = pyqtSignal(str, tuple)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Control references
        self.solar_config_btn = None
        self.obstacle_btn = None
        self.power_label = None
        self.energy_label = None
        self.efficiency_label = None
        self.performance_progress = None
        self.performance_timer = None
        
        # Solar parameters
        self.current_time = 12.0  # Noon
        self.day_of_year = 172  # Summer solstice
        self.latitude = 48.3061  # Nitra
        self.longitude = 18.0764
        self.panel_config = {
            'panel_count': 0,
            'panel_power': 400,  # Watts per panel
            'panel_area': 2.0,  # m² per panel
            'efficiency': 0.20  # 20% efficiency
        }
        
        self.setup_ui()
        self.apply_styles()
        self.setup_performance_timer()
        
        print("✅ ModificationsTab initialized with dark theme")
    
    def setup_ui(self):
        """Setup modifications tab UI"""
        # Set background
        self.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Solar Panel Configuration Section
        self.setup_solar_panel_section(layout)
        
        # Obstacle Placement Section
        self.setup_obstacle_section(layout)
        
        # Performance Section
        self.setup_performance_section(layout)
        
        # Add stretch to push everything up
        layout.addStretch()
    
    def setup_solar_panel_section(self, layout):
        """Setup solar panel configuration section"""
        panel_group = QGroupBox("🔋 Solar Panel Configuration")
        
        panel_layout = QVBoxLayout(panel_group)
        panel_layout.setContentsMargins(10, 15, 10, 10)
        panel_layout.setSpacing(10)
        
        # Info label
        panel_info = QLabel("Configure solar panel placement, specifications, and optimization settings")
        panel_info.setWordWrap(True)
        panel_layout.addWidget(panel_info)
        
        # Solar panel button
        self.solar_config_btn = QPushButton("🔋 Configure Solar Panels")
        self.solar_config_btn.setMinimumHeight(40)
        self.solar_config_btn.clicked.connect(self._open_solar_panel_dialog)
        self.solar_config_btn.setEnabled(SOLAR_PANEL_DIALOG_AVAILABLE)
        
        panel_layout.addWidget(self.solar_config_btn)
        
        # Panel status
        if SOLAR_PANEL_DIALOG_AVAILABLE:
            panel_status = QLabel("✅ Solar panel configuration available")
            self.panel_status = panel_status
        else:
            panel_status = QLabel("⚠️ Solar panel dialog not available")
            self.panel_status = panel_status
        panel_layout.addWidget(panel_status)
        
        layout.addWidget(panel_group)
        self.panel_group = panel_group
    
    def setup_obstacle_section(self, layout):
        """Setup obstacle placement section"""
        obstacle_group = QGroupBox("🏗️ Roof Obstacles")
        
        obstacle_layout = QVBoxLayout(obstacle_group)
        obstacle_layout.setContentsMargins(10, 15, 10, 10)
        obstacle_layout.setSpacing(10)
        
        # Info label
        obstacle_info = QLabel("Add obstacles like chimneys, vents, HVAC equipment, and other roof structures")
        obstacle_info.setWordWrap(True)
        obstacle_layout.addWidget(obstacle_info)
        
        # Obstacle button
        self.obstacle_btn = QPushButton("🏗️ Add Roof Obstacles")
        self.obstacle_btn.setMinimumHeight(40)
        self.obstacle_btn.clicked.connect(self._open_obstacle_dialog)
        self.obstacle_btn.setEnabled(OBSTACLE_DIALOG_AVAILABLE)
        
        obstacle_layout.addWidget(self.obstacle_btn)
        
        # Obstacle status
        if OBSTACLE_DIALOG_AVAILABLE:
            obstacle_status = QLabel("✅ Obstacle placement available")
            self.obstacle_status = obstacle_status
        else:
            obstacle_status = QLabel("⚠️ Obstacle dialog not available")
            self.obstacle_status = obstacle_status
        obstacle_layout.addWidget(obstacle_status)
        
        layout.addWidget(obstacle_group)
        self.obstacle_group = obstacle_group
    
    def setup_performance_section(self, layout):
        """Setup performance metrics section"""
        performance_group = QGroupBox("📊 Solar Performance Metrics")
        
        performance_layout = QVBoxLayout(performance_group)
        performance_layout.setContentsMargins(10, 15, 10, 10)
        performance_layout.setSpacing(10)
        
        # Info about metrics
        info_label = QLabel("Real-time calculations based on sun position, panel configuration, and location")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #95a5a6; font-size: 11px; font-style: italic;")
        performance_layout.addWidget(info_label)
        
        # Performance metrics
        self.power_label = QLabel("Current Power: 0.0 kW")
        self.energy_label = QLabel("Daily Energy: 0.0 kWh")
        self.efficiency_label = QLabel("System Efficiency: 0.0%")
        
        performance_layout.addWidget(self.power_label)
        performance_layout.addWidget(self.energy_label)
        performance_layout.addWidget(self.efficiency_label)
        
        # Performance progress bar
        self.performance_progress = QProgressBar()
        self.performance_progress.setRange(0, 100)
        self.performance_progress.setValue(0)
        self.performance_progress.setTextVisible(True)
        self.performance_progress.setFormat("Solar Irradiance: %p%")
        
        performance_layout.addWidget(self.performance_progress)
        
        # Update button
        update_btn = QPushButton("🔄 Update Performance")
        update_btn.clicked.connect(self._update_performance)
        update_btn.setMinimumHeight(35)
        self.update_btn = update_btn
        
        performance_layout.addWidget(update_btn)
        
        layout.addWidget(performance_group)
        self.performance_group = performance_group
    
    def apply_styles(self):
        """Apply dark theme styles"""
        if STYLES_AVAILABLE:
            # Group boxes
            for group in [self.panel_group, self.obstacle_group, self.performance_group]:
                group.setStyleSheet(get_model3d_groupbox_style())
            
            # Buttons
            for button in self.findChildren(QPushButton):
                button.setStyleSheet(get_model3d_button_style())
            
            # Progress bar
            self.performance_progress.setStyleSheet(get_model3d_progress_style())
            
            # Labels - apply specific styles
            info_style = "color: #bdc3c7; font-size: 12px; font-weight: normal; background-color: transparent;"
            status_available_style = "color: #27ae60; font-size: 11px; font-weight: normal; background-color: transparent;"
            status_unavailable_style = "color: #e74c3c; font-size: 11px; font-weight: normal; background-color: transparent;"
            power_style = "color: #3498db; font-weight: bold; font-size: 13px; background-color: transparent;"
            energy_style = "color: #2ecc71; font-weight: bold; font-size: 13px; background-color: transparent;"
            efficiency_style = "color: #f39c12; font-weight: bold; font-size: 13px; background-color: transparent;"
            
            # Apply to specific labels
            for label in self.findChildren(QLabel):
                text = label.text()
                if "Configure solar panel" in text or "Add obstacles" in text:
                    label.setStyleSheet(info_style)
                elif "✅" in text:
                    label.setStyleSheet(status_available_style)
                elif "⚠️" in text:
                    label.setStyleSheet(status_unavailable_style)
                elif "Current Power" in text:
                    label.setStyleSheet(power_style)
                elif "Daily Energy" in text:
                    label.setStyleSheet(energy_style)
                elif "System Efficiency" in text:
                    label.setStyleSheet(efficiency_style)
        else:
            # Fallback styles
            group_style = """
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
            """
            
            for group in [self.panel_group, self.obstacle_group, self.performance_group]:
                group.setStyleSheet(group_style)
            
            button_style = """
                QPushButton {
                    background-color: #3498db;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
            
            for button in self.findChildren(QPushButton):
                button.setStyleSheet(button_style)
            
            self.performance_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #3498db;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                    background-color: #34495e;
                    color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #3498db;
                    border-radius: 3px;
                }
            """)
            
            # Labels
            for label in self.findChildren(QLabel):
                label.setStyleSheet("color: #ffffff; background-color: transparent;")
    
    def setup_performance_timer(self):
        """Setup timer for automatic performance updates"""
        try:
            self.performance_timer = QTimer()
            self.performance_timer.timeout.connect(self._update_performance)
            self.performance_timer.setInterval(5000)  # Update every 5 seconds
            self.performance_timer.start()
            
            # Initial update
            self._update_performance()
            
            print("✅ Performance timer setup completed")
            
        except Exception as e:
            print(f"❌ Error setting up performance timer: {e}")
    
    def calculate_solar_position(self):
        """Calculate sun position based on time, date, and location"""
        # Simplified solar position calculation
        # Convert time to solar angle
        solar_noon = 12.0
        hour_angle = 15.0 * (self.current_time - solar_noon)  # degrees
        
        # Declination angle (simplified)
        declination = 23.45 * math.sin(math.radians((360/365) * (self.day_of_year - 81)))
        
        # Solar elevation angle
        lat_rad = math.radians(self.latitude)
        dec_rad = math.radians(declination)
        hour_rad = math.radians(hour_angle)
        
        elevation = math.asin(
            math.sin(lat_rad) * math.sin(dec_rad) + 
            math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
        )
        
        elevation_deg = math.degrees(elevation)
        
        # Azimuth calculation (simplified)
        azimuth = math.atan2(
            -math.sin(hour_rad),
            math.tan(dec_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(hour_rad)
        )
        azimuth_deg = math.degrees(azimuth) + 180
        
        return elevation_deg, azimuth_deg
    
    def calculate_solar_irradiance(self, elevation_deg):
        """Calculate solar irradiance based on sun elevation"""
        if elevation_deg <= 0:
            return 0.0
        
        # Air mass calculation
        if elevation_deg > 0:
            air_mass = 1 / math.sin(math.radians(elevation_deg))
        else:
            air_mass = 40  # Maximum practical value
        
        # Direct normal irradiance (simplified atmospheric model)
        dni_max = 900  # W/m² at sea level
        atmospheric_extinction = 0.14  # Typical value
        dni = dni_max * math.exp(-atmospheric_extinction * air_mass)
        
        # Global horizontal irradiance (includes diffuse)
        ghi = dni * math.sin(math.radians(elevation_deg)) + 100  # Add diffuse component
        
        return max(0, ghi)
    
    def calculate_panel_output(self, irradiance):
        """Calculate panel output based on irradiance and configuration"""
        if self.panel_config['panel_count'] == 0:
            return 0.0, 0.0, 0.0
        
        # Temperature effect (simplified - assumes 25°C cell temp at 1000 W/m²)
        temp_coefficient = -0.004  # -0.4% per °C
        cell_temp = 25 + (irradiance / 1000) * 20  # Simplified NOCT model
        temp_factor = 1 + temp_coefficient * (cell_temp - 25)
        
        # Power calculation
        panel_power_stc = self.panel_config['panel_power']  # Watts at STC
        actual_power = panel_power_stc * (irradiance / 1000) * temp_factor * self.panel_config['efficiency']
        total_power = actual_power * self.panel_config['panel_count'] / 1000  # Convert to kW
        
        # System efficiency (includes inverter, wiring losses)
        system_efficiency = 0.85
        total_power *= system_efficiency
        
        # Daily energy estimation (simplified)
        # Assumes symmetric day with peak at solar noon
        if self.current_time >= 6 and self.current_time <= 18:
            hours_of_sun = 12
            daily_energy = total_power * hours_of_sun * 0.6  # Peak sun hours factor
        else:
            daily_energy = 0
        
        # Overall efficiency
        theoretical_max = self.panel_config['panel_count'] * self.panel_config['panel_power'] / 1000
        if theoretical_max > 0:
            efficiency = (total_power / theoretical_max) * 100
        else:
            efficiency = 0
        
        return total_power, daily_energy, efficiency
    
    def _update_performance(self):
        """Update solar performance display with real calculations"""
        try:
            # Calculate sun position
            elevation, azimuth = self.calculate_solar_position()
            
            # Calculate irradiance
            irradiance = self.calculate_solar_irradiance(elevation)
            
            # Calculate panel output
            power, energy, efficiency = self.calculate_panel_output(irradiance)
            
            # Update labels
            self.power_label.setText(f"Current Power: {power:.2f} kW")
            self.energy_label.setText(f"Daily Energy: {energy:.1f} kWh")
            self.efficiency_label.setText(f"System Efficiency: {efficiency:.1f}%")
            
            # Update progress bar (shows irradiance as percentage of max)
            irradiance_percent = min(100, int((irradiance / 1000) * 100))
            self.performance_progress.setValue(irradiance_percent)
            self.performance_progress.setFormat(f"Solar Irradiance: {irradiance:.0f} W/m² ({irradiance_percent}%)")
            
                    
        except Exception as e:
            print(f"❌ Error updating performance: {e}")
    
    def update_solar_parameters(self, time=None, day=None, latitude=None, longitude=None):
        """Update solar parameters from external controls"""
        if time is not None:
            self.current_time = time
        if day is not None:
            self.day_of_year = day
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        
        # Immediate update
        self._update_performance()
    
    def _open_solar_panel_dialog(self):
        """Open solar panel configuration dialog"""
        try:
            if not SOLAR_PANEL_DIALOG_AVAILABLE:
                QMessageBox.warning(self, "Not Available", "Solar panel dialog not available.")
                return
            
            # Show dialog
            config = show_solar_panel_dialog(parent=self, is_flat_roof=False)
            
            if config:
                # Update panel configuration
                self.panel_config['panel_count'] = config.get('panel_count', 10)
                self.panel_config['panel_power'] = config.get('panel_power', 400)
                self.panel_config['efficiency'] = config.get('efficiency', 0.20)
                
                # Apply panels to roof
                if self._apply_panels_to_roof(config):
                    self._update_performance()  # Immediate update
                    QMessageBox.information(self, "Success", 
                        f"Solar panel configuration applied!\n{self.panel_config['panel_count']} panels configured.")
                else:
                    QMessageBox.warning(self, "Warning", 
                        "Configuration saved but could not apply panels to 3D model.\n"
                        "Make sure the 3D model tab is open and a building is created.")
                        
        except Exception as e:
            print(f"❌ Error opening solar panel dialog: {e}")
            # Set some default panels for testing
            self.panel_config['panel_count'] = 10
            self._update_performance()
            QMessageBox.critical(self, "Error", f"Error opening solar panel dialog: {e}")
    
    def _open_obstacle_dialog(self):
        """Open obstacle placement dialog"""
        try:
            if not OBSTACLE_DIALOG_AVAILABLE:
                QMessageBox.warning(self, "Not Available", "Obstacle dialog not available.")
                return
            
            dialog = RoofObstacleDialogs(parent=self)
            result = dialog.exec_()
            
            if result == dialog.Accepted:
                obstacle_type, dimensions, use_default = dialog.get_selection()
                if obstacle_type and dimensions:
                    # Try to apply directly to model
                    model_tab = self._get_model_tab()
                    if model_tab:
                        if hasattr(model_tab, 'add_obstacle'):
                            success = model_tab.add_obstacle(obstacle_type, dimensions)
                            if success:
                                QMessageBox.information(self, "Success", 
                                    f"Obstacle '{obstacle_type}' placed successfully!")
                            else:
                                QMessageBox.warning(self, "Warning", 
                                    f"Could not place obstacle '{obstacle_type}'")
                        else:
                            # Emit signal as fallback
                            self.obstacle_placement_requested.emit(obstacle_type, dimensions)
                            QMessageBox.information(self, "Success", 
                                f"Obstacle '{obstacle_type}' configuration sent!")
                    else:
                        self.obstacle_placement_requested.emit(obstacle_type, dimensions)
                            
        except Exception as e:
            print(f"❌ Error opening obstacle dialog: {e}")
            QMessageBox.critical(self, "Error", f"Error opening obstacle dialog: {e}")
    
    def update_theme(self, is_dark_theme):
        """Update theme (always dark for this panel)"""
        self.apply_styles()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.performance_timer:
                self.performance_timer.stop()
                self.performance_timer = None
                
            print("✅ ModificationsTab cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def _apply_panels_to_roof(self, config):
        """Apply solar panels to the roof in the 3D model"""
        try:
            # Get the model tab
            model_tab = self._get_model_tab()
            if not model_tab:
                print("❌ Model tab not found")
                return False
            
            # Format config for panel handler
            handler_config = {
                'panel_width': config.get('panel_width', 1017),     # mm
                'panel_length': config.get('panel_length', 1835),   # mm
                'panel_gap': config.get('panel_gap', 50),          # mm
                'panel_power': config.get('panel_power', 400),     # W
                'edge_offset': config.get('edge_offset', 300),     # mm
                'panel_offset': config.get('panel_offset', 100),   # mm (height above roof)
            }
            
            # Check if model tab has the required method
            if hasattr(model_tab, 'add_solar_panels'):
                success = model_tab.add_solar_panels(handler_config)
                if success:
                    print(f"✅ Solar panels applied to roof")
                    return True
                else:
                    print("❌ Failed to add solar panels to model")
                    return False
            else:
                print("⚠️ Model tab doesn't have add_solar_panels method")
                # Try emitting signal as fallback
                self.solar_panel_config_changed.emit(config)
                return True
                
        except Exception as e:
            print(f"❌ Error applying panels to roof: {e}")
            return False
    
    def _get_model_tab(self):
        """Get the model tab from main window"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                tab_count = self.main_window.content_tabs.count()
                for i in range(tab_count):
                    tab_text = self.main_window.content_tabs.tabText(i).lower()
                    if 'model' in tab_text or '3d' in tab_text:
                        return self.main_window.content_tabs.widget(i)
            return None
        except Exception as e:
            print(f"❌ Error getting model tab: {e}")
            return None
