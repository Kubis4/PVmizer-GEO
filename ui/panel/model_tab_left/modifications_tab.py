#!/usr/bin/env python3
"""
ui/panel/model_tab_left/modifications_tab.py
CLEANED - No hardcoded styles
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QProgressBar, QGroupBox, QMessageBox, 
                            QTabWidget)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
import math

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

# Import environment tab with fallback
try:
    from ui.panel.model_tab_left.environment_tab import EnvironmentTab
    ENVIRONMENT_TAB_AVAILABLE = True
except ImportError:
    ENVIRONMENT_TAB_AVAILABLE = False
    print("⚠️ EnvironmentTab not available")

class ModificationsTab(QWidget):
    """Enhanced Modifications tab widget for 3D model tab"""
    
    # Signals
    solar_panel_config_changed = pyqtSignal(dict)
    obstacle_placement_requested = pyqtSignal(str, tuple)
    environment_action_requested = pyqtSignal(str, dict)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Control references for original functionality
        self.solar_config_btn = None
        self.obstacle_btn = None
        self.power_label = None
        self.energy_label = None
        self.efficiency_label = None
        self.performance_progress = None
        self.performance_timer = None
        
        # Tab system and environment tab
        self.modifications_tabs = None
        self.environment_tab = None
        
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
        self.setup_performance_timer()
        
        print("✅ Enhanced ModificationsTab initialized")
    
    def setup_ui(self):
        """Enhanced UI setup with tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # CREATE TABBED INTERFACE FOR MODIFICATIONS
        self.modifications_tabs = QTabWidget()
        self.modifications_tabs.setTabPosition(QTabWidget.North)
        
        # Tab 1: Original modifications (Solar + Obstacles)
        original_tab = QWidget()
        self.setup_original_modifications_tab(original_tab)
        self.modifications_tabs.addTab(original_tab, "🔋 Solar & Obstacles")
        
        # Tab 2: Environment tab
        if ENVIRONMENT_TAB_AVAILABLE:
            try:
                self.environment_tab = EnvironmentTab(self.main_window)
                self.modifications_tabs.addTab(self.environment_tab, "🌲 Environment")
                
                # Connect environment signals
                self.environment_tab.environment_action_requested.connect(
                    self.environment_action_requested.emit
                )
                
                print("✅ Environment tab added successfully")
            except Exception as e:
                print(f"❌ Error adding environment tab: {e}")
                self._create_fallback_environment_tab()
        else:
            self._create_fallback_environment_tab()
        
        layout.addWidget(self.modifications_tabs)
        
        # Add stretch to push everything up
        layout.addStretch()

    def setup_original_modifications_tab(self, tab_widget):
        """Setup the original solar panel and obstacle controls"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Solar Panel Configuration Section
        self.setup_solar_panel_section(layout)
        
        # Obstacle Placement Section
        self.setup_obstacle_section(layout)
        
        # Performance Section
        self.setup_performance_section(layout)
        
        # Add stretch
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
        info_label.setObjectName("performanceInfo")  # For styling
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

    def _create_fallback_environment_tab(self):
        """Create fallback environment tab when EnvironmentTab is not available"""
        fallback_tab = QWidget()
        
        fallback_layout = QVBoxLayout(fallback_tab)
        fallback_layout.setContentsMargins(20, 20, 20, 20)
        
        # Error message
        error_label = QLabel("⚠️ Environment Tab Not Available")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setObjectName("environmentError")  # For styling
        fallback_layout.addWidget(error_label)
        
        # Instructions
        instructions = QLabel("""
        To enable environment features:
        
        1. Create the file: ui/panel/model_tab_left/environment_tab.py
        2. Copy the EnvironmentTab class implementation
        3. Restart the application
        
        Environment features include:
        • Deciduous, Pine, and Oak trees
        • Utility poles with power lines  
        • Automatic scene population
        • Shadow casting integration
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("environmentInstructions")  # For styling
        fallback_layout.addWidget(instructions)
        
        fallback_layout.addStretch()
        
        self.modifications_tabs.addTab(fallback_tab, "🌲 Environment (Missing)")
        print("⚠️ Using fallback environment tab")
    
    def setup_performance_timer(self):
        """Setup performance update timer"""
        try:
            self.performance_timer = QTimer()
            self.performance_timer.timeout.connect(self._update_performance)
            self.performance_timer.start(30000)  # Update every 30 seconds
            
            # Initial update
            self._update_performance()
            
            print("✅ Performance timer initialized")
            
        except Exception as e:
            print(f"❌ Error setting up performance timer: {e}")
    
    def _update_performance(self):
        """Update solar performance metrics"""
        try:
            # Calculate solar parameters
            solar_elevation = self._calculate_solar_elevation()
            solar_azimuth = self._calculate_solar_azimuth()
            
            # Calculate irradiance (simplified model)
            if solar_elevation > 0:
                # Base irradiance calculation
                air_mass = 1 / math.sin(math.radians(solar_elevation))
                air_mass = max(1.0, min(air_mass, 10.0))
                
                # Atmospheric attenuation
                clear_sky_irradiance = 1000 * (0.7 ** (air_mass ** 0.678))
                
                # Panel efficiency factor
                efficiency_factor = self.panel_config['efficiency']
                
                # Calculate power output
                panel_area = self.panel_config['panel_area']
                panel_count = self.panel_config['panel_count']
                
                current_power = (clear_sky_irradiance * panel_area * panel_count * 
                               efficiency_factor) / 1000  # Convert to kW
                
                # Daily energy estimate (simplified)
                peak_sun_hours = max(0, 6 + 2 * math.sin(math.radians(solar_elevation)))
                daily_energy = current_power * peak_sun_hours
                
                # System efficiency
                system_efficiency = (current_power / 
                                   (panel_count * self.panel_config['panel_power'] / 1000)) * 100
                system_efficiency = min(100, max(0, system_efficiency))
                
                # Irradiance percentage
                irradiance_percent = min(100, (clear_sky_irradiance / 1000) * 100)
                
            else:
                current_power = 0.0
                daily_energy = 0.0
                system_efficiency = 0.0
                irradiance_percent = 0.0
            
            # Update UI
            self.power_label.setText(f"Current Power: {current_power:.1f} kW")
            self.energy_label.setText(f"Daily Energy: {daily_energy:.1f} kWh")
            self.efficiency_label.setText(f"System Efficiency: {system_efficiency:.1f}%")
            self.performance_progress.setValue(int(irradiance_percent))
            
        except Exception as e:
            print(f"❌ Error updating performance: {e}")
    
    def _calculate_solar_elevation(self):
        """Calculate solar elevation angle"""
        try:
            # Convert day of year to solar declination
            declination = 23.45 * math.sin(math.radians(360 * (284 + self.day_of_year) / 365))
            
            # Convert time to hour angle
            hour_angle = 15 * (self.current_time - 12)
            
            # Calculate solar elevation
            lat_rad = math.radians(self.latitude)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)
            
            elevation = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad) +
                math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
            )
            
            return math.degrees(elevation)
            
        except Exception as e:
            print(f"❌ Error calculating solar elevation: {e}")
            return 45.0  # Default value
    
    def _calculate_solar_azimuth(self):
        """Calculate solar azimuth angle"""
        try:
            # Simplified azimuth calculation
            hour_angle = 15 * (self.current_time - 12)
            return 180 + hour_angle  # Simplified model
            
        except Exception as e:
            print(f"❌ Error calculating solar azimuth: {e}")
            return 180.0  # Default value
    
    def update_solar_parameters(self, time=None, day=None, latitude=None, longitude=None):
        """Update solar calculation parameters"""
        try:
            if time is not None:
                self.current_time = time
            if day is not None:
                self.day_of_year = day
            if latitude is not None:
                self.latitude = latitude
            if longitude is not None:
                self.longitude = longitude
            
            # Trigger immediate update
            self._update_performance()
            
            print(f"✅ Solar parameters updated: time={self.current_time}, day={self.day_of_year}")
            
        except Exception as e:
            print(f"❌ Error updating solar parameters: {e}")
    
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

    def connect_environment_to_model_tab(self, model_tab):
        """Connect environment actions to the model tab's roof system"""
        if not self.environment_tab or not model_tab:
            return
            
        try:
            # Connect environment action signal to model tab handler
            self.environment_tab.environment_action_requested.connect(
                lambda action, params: self._handle_environment_action(model_tab, action, params)
            )
            print("✅ Environment tab connected to model tab")
        except Exception as e:
            print(f"❌ Error connecting environment to model tab: {e}")

    def _handle_environment_action(self, model_tab, action_type, parameters):
        """Handle environment actions by calling appropriate BaseRoof methods"""
        try:
            # Get the current roof from model tab
            current_roof = getattr(model_tab, 'current_roof', None)
            if not current_roof:
                print("No active roof in model tab")
                return False
            
            print(f"Handling environment action: {action_type}")
            
            # Handle different environment actions
            if action_type == 'add_tree':
                tree_type = parameters.get('tree_type', 'deciduous')
                # Set the tree type index before adding
                if tree_type == 'pine':
                    current_roof.tree_type_index = 1
                elif tree_type == 'oak':
                    current_roof.tree_type_index = 2
                else:  # deciduous
                    current_roof.tree_type_index = 0
                
                success = current_roof.add_environment_obstacle_at_point('tree')
                return success
                
            elif action_type == 'add_multiple_trees':
                count = parameters.get('count', 5)
                success_count = 0
                for i in range(count):
                    # Cycle through tree types
                    tree_types = ['deciduous', 'pine', 'oak']
                    current_roof.tree_type_index = i % len(tree_types)
                    if current_roof.add_environment_obstacle_at_point('tree'):
                        success_count += 1
                
                print(f"Added {success_count}/{count} trees")
                return success_count > 0
                
            elif action_type == 'add_pole':
                success = current_roof.add_environment_obstacle_at_point('pole')
                return success
                
            elif action_type == 'toggle_attachment_points':
                try:
                    current_roof.hide_environment_attachment_points()
                except:
                    # If hide fails, try show
                    current_roof.show_environment_attachment_points()
                return True
                
            elif action_type == 'clear_all_environment':
                current_roof.clear_environment_obstacles()
                return True
                
            elif action_type == 'auto_populate_scene':
                success_count = 0
                
                # Add 3 deciduous trees
                current_roof.tree_type_index = 0
                for _ in range(3):
                    if current_roof.add_environment_obstacle_at_point('tree'):
                        success_count += 1
                
                # Add 2 pine trees  
                current_roof.tree_type_index = 1
                for _ in range(2):
                    if current_roof.add_environment_obstacle_at_point('tree'):
                        success_count += 1
                
                # Add 1 oak tree
                current_roof.tree_type_index = 2
                if current_roof.add_environment_obstacle_at_point('tree'):
                    success_count += 1
                
                # Add 2 poles
                for _ in range(2):
                    current_roof.add_environment_obstacle_at_point('pole')
                
                print(f"Added {success_count} trees + poles")
                return True
            
            else:
                print(f"Unknown environment action: {action_type}")
                return False
                
        except Exception as e:
            print(f"Error handling environment action '{action_type}': {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_theme(self, is_dark_theme):
        """Update theme - no hardcoded styles"""
        pass

    def connect_signals(self):
        """Enhanced signal connections including environment"""
        try:
            # Connect environment tab if available
            if self.environment_tab and hasattr(self.environment_tab, 'environment_action_requested'):
                self.environment_tab.environment_action_requested.connect(
                    self.environment_action_requested.emit
                )
                print("Environment signals connected")
                
        except Exception as e:
            print(f"Error connecting environment signals: {e}")

    def cleanup(self):
        """Enhanced cleanup with environment tab"""
        try:
            # Stop performance timer
            if hasattr(self, 'performance_timer') and self.performance_timer:
                try:
                    self.performance_timer.stop()
                except Exception as timer_error:
                    print(f"Error stopping performance timer: {timer_error}")
                finally:
                    self.performance_timer = None
            
            # Cleanup environment tab
            if hasattr(self, 'environment_tab') and self.environment_tab:
                try:
                    if hasattr(self.environment_tab, 'cleanup'):
                        self.environment_tab.cleanup()
                except Exception as env_error:
                    print(f"Error cleaning up environment tab: {env_error}")
                finally:
                    self.environment_tab = None
            
            # Clear control references safely
            control_refs = [
                'solar_config_btn', 'obstacle_btn', 'power_label', 
                'energy_label', 'efficiency_label', 'performance_progress', 
                'update_btn', 'panel_status', 'obstacle_status'
            ]
            
            for ref in control_refs:
                if hasattr(self, ref):
                    setattr(self, ref, None)
            
            # Clear group references safely
            group_refs = ['panel_group', 'obstacle_group', 'performance_group']
            for ref in group_refs:
                if hasattr(self, ref):
                    setattr(self, ref, None)
            
            # Clear tab widget
            if hasattr(self, 'modifications_tabs') and self.modifications_tabs:
                try:
                    # Clear all tabs first
                    while self.modifications_tabs.count() > 0:
                        widget = self.modifications_tabs.widget(0)
                        self.modifications_tabs.removeTab(0)
                        if widget:
                            widget.deleteLater()
                except Exception as tab_error:
                    print(f"Error clearing tabs: {tab_error}")
                finally:
                    self.modifications_tabs = None
            
            # Clear configuration data
            if hasattr(self, 'panel_config'):
                self.panel_config = None
            
            # Clear main window reference last
            self.main_window = None
                
            print("Enhanced ModificationsTab cleanup completed")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
