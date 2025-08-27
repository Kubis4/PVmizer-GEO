#!/usr/bin/env python3
"""
ui/panel/model_tab_left/modifications_tab.py
CLEANED - Matching left panel width, no horizontal scroll, "Roof" tab name
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QProgressBar, QGroupBox, QMessageBox, 
                            QTabWidget, QFrame)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont
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

class ModificationsTab(QWidget):
    """Enhanced Modifications tab widget with invisible containers but active tabs, matching left panel width"""
    
    # Signals
    solar_panel_config_changed = pyqtSignal(dict)
    obstacle_placement_requested = pyqtSignal(str, tuple)
    environment_action_requested = pyqtSignal(str, dict)
    performance_updated = pyqtSignal(float, float, float, float)  # power, energy, efficiency, irradiance
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Control references for roof modifications
        self.solar_config_btn = None
        self.obstacle_btn = None
        self.performance_timer = None
        
        # Tab system and environment tab
        self.modifications_tabs = None
        self.environment_tab = None
        
        # Solar parameters for performance calculations
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
    
    def setup_ui(self):
        """Enhanced UI setup with invisible containers, active tabs, default font sizes, and width constraints"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Apply your blue styling with DEFAULT FONT SIZES and WIDTH CONSTRAINTS
        self.setStyleSheet("""
            QWidget {
                background-color: transparent !important;
                max-width: 410px !important;
            }
            
            /* Group Boxes with your styling, DEFAULT FONT SIZES, and WIDTH CONSTRAINTS */
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
                max-width: 410px !important;
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
            
            /* Labels with your styling, DEFAULT FONT SIZES, and WIDTH CONSTRAINTS */
            QLabel {
                color: #ffffff !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 12px !important;
                font-weight: normal !important;
                max-width: 390px !important;
            }
            
            /* Buttons with your styling, DEFAULT FONT SIZES, and WIDTH CONSTRAINTS */
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
                max-width: 390px !important;
            }
            
            QPushButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
                color: #ffffff !important;
            }
            
            QPushButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
                padding: 9px 11px 7px 13px !important;
            }
            
            QPushButton:disabled {
                background-color: #7f8c8d !important;
                border: 2px solid #7f8c8d !important;
                color: #95a5a6 !important;
            }
        """)
        
        # CREATE INTERNAL TABS WITH INVISIBLE CONTAINERS BUT ACTIVE TABS - MATCHING LEFT PANEL WIDTH
        self.modifications_tabs = QTabWidget()
        self.modifications_tabs.setTabPosition(QTabWidget.North)
        self.modifications_tabs.setUsesScrollButtons(False)
        # MATCH LEFT PANEL WIDTH (450px) minus margins (40px total) = 410px max
        self.modifications_tabs.setMaximumWidth(410)
        self.modifications_tabs.setMinimumWidth(390)
        
        # Hide internal tab containers but keep tabs functional with width constraints
        self.modifications_tabs.setStyleSheet("""
            /* INVISIBLE CONTAINERS - matching left panel with width constraints */
            QTabWidget::pane {
                border: none !important;
                background-color: transparent !important;
                margin: 0px !important;
                padding: 0px !important;
                max-width: 410px !important;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
                max-width: 410px !important;
            }
            
            /* VISIBLE TABS with your blue styling and WIDTH CONSTRAINTS */
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
                max-width: 200px !important;
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
                max-width: 410px !important;
            }
            
            /* TAB CONTENT - transparent background and width constrained */
            QTabWidget > QWidget {
                background-color: transparent !important;
                max-width: 410px !important;
            }
        """)
        
        # Tab 1: Roof (CHANGED from "Solar & Obstacles" as requested)
        roof_modifications_tab = QWidget()
        self.setup_roof_modifications_tab(roof_modifications_tab)
        self.modifications_tabs.addTab(roof_modifications_tab, "🏠 Roof")
        
        # Tab 2: Environment tab (using full text)
        if ENVIRONMENT_TAB_AVAILABLE:
            try:
                self.environment_tab = EnvironmentTab(self.main_window)
                self.modifications_tabs.addTab(self.environment_tab, "🌲 Environment")
                
                # Connect environment signals
                self.environment_tab.environment_action_requested.connect(
                    self.environment_action_requested.emit
                )
                
            except Exception as e:
                self._create_fallback_environment_tab()
        else:
            self._create_fallback_environment_tab()
        
        layout.addWidget(self.modifications_tabs)
        layout.addStretch()

    def setup_roof_modifications_tab(self, tab_widget):
        """Setup the roof modifications with transparent background and width constraints"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Make tab content transparent and width-constrained to match left panel
        tab_widget.setStyleSheet("""
            QWidget {
                background-color: transparent !important;
                max-width: 390px !important;
            }
        """)
        
        # Solar Panel Configuration Section
        self.setup_solar_panel_section(layout)
        
        # Obstacle Placement Section
        self.setup_obstacle_section(layout)
        
        layout.addStretch()
    
    def setup_solar_panel_section(self, layout):
        """Setup solar panel configuration section with default font sizes and width constraints"""
        panel_group = QGroupBox("🔋 Solar Panel Configuration")
        panel_group.setMaximumWidth(390)
        
        panel_layout = QVBoxLayout(panel_group)
        panel_layout.setContentsMargins(10, 15, 10, 10)
        panel_layout.setSpacing(10)
        
        # Info label with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        panel_info = QLabel("Configure solar panel placement, specifications, and optimization settings")
        panel_info.setWordWrap(True)
        panel_info.setMaximumWidth(370)
        panel_layout.addWidget(panel_info)
        
        # Solar panel button with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        self.solar_config_btn = QPushButton("🔋 Configure Solar Panels")
        self.solar_config_btn.setMinimumHeight(32)  # Match default button height
        self.solar_config_btn.setMaximumWidth(370)
        self.solar_config_btn.clicked.connect(self._open_solar_panel_dialog)
        self.solar_config_btn.setEnabled(SOLAR_PANEL_DIALOG_AVAILABLE)
        
        panel_layout.addWidget(self.solar_config_btn)
        
        # Panel status with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        if SOLAR_PANEL_DIALOG_AVAILABLE:
            panel_status = QLabel("✅ Solar panel configuration available")
            self.panel_status = panel_status
        else:
            panel_status = QLabel("⚠️ Solar panel dialog not available")
            self.panel_status = panel_status
        
        panel_status.setWordWrap(True)
        panel_status.setMaximumWidth(370)
        panel_layout.addWidget(panel_status)
        
        layout.addWidget(panel_group)
        self.panel_group = panel_group
    
    def setup_obstacle_section(self, layout):
        """Setup obstacle placement section with default font sizes and width constraints"""
        obstacle_group = QGroupBox("🏗️ Roof Obstacles")
        obstacle_group.setMaximumWidth(390)
        
        obstacle_layout = QVBoxLayout(obstacle_group)
        obstacle_layout.setContentsMargins(10, 15, 10, 10)
        obstacle_layout.setSpacing(10)
        
        # Info label with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        obstacle_info = QLabel("Add obstacles like chimneys, vents, HVAC equipment, and other roof structures")
        obstacle_info.setWordWrap(True)
        obstacle_info.setMaximumWidth(370)
        obstacle_layout.addWidget(obstacle_info)
        
        # Obstacle button with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        self.obstacle_btn = QPushButton("🏗️ Add Roof Obstacles")
        self.obstacle_btn.setMinimumHeight(32)  # Match default button height
        self.obstacle_btn.setMaximumWidth(370)
        self.obstacle_btn.clicked.connect(self._open_obstacle_dialog)
        self.obstacle_btn.setEnabled(OBSTACLE_DIALOG_AVAILABLE)
        
        obstacle_layout.addWidget(self.obstacle_btn)
        
        # Obstacle status with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        if OBSTACLE_DIALOG_AVAILABLE:
            obstacle_status = QLabel("✅ Obstacle placement available")
            self.obstacle_status = obstacle_status
        else:
            obstacle_status = QLabel("⚠️ Obstacle dialog not available")
            self.obstacle_status = obstacle_status
        
        obstacle_status.setWordWrap(True)
        obstacle_status.setMaximumWidth(370)
        obstacle_layout.addWidget(obstacle_status)
        
        layout.addWidget(obstacle_group)
        self.obstacle_group = obstacle_group

    def _create_fallback_environment_tab(self):
        """Create fallback environment tab with width constraints"""
        fallback_tab = QWidget()
        
        # Make tab content transparent and width-constrained to match left panel
        fallback_tab.setStyleSheet("""
            QWidget {
                background-color: transparent !important;
                max-width: 390px !important;
            }
        """)
        
        fallback_layout = QVBoxLayout(fallback_tab)
        fallback_layout.setContentsMargins(20, 20, 20, 20)
        
        # Error message with DEFAULT FONT SIZE and WIDTH CONSTRAINT
        error_label = QLabel("⚠️ Environment Tab Not Available")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setMaximumWidth(350)
        fallback_layout.addWidget(error_label)
        
        # Instructions with DEFAULT FONT SIZE and WIDTH CONSTRAINT
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
        instructions.setMaximumWidth(350)
        fallback_layout.addWidget(instructions)
        
        fallback_layout.addStretch()
        
        self.modifications_tabs.addTab(fallback_tab, "🌲 Environment")
    
    def setup_performance_timer(self):
        """Setup performance update timer"""
        try:
            self.performance_timer = QTimer()
            self.performance_timer.timeout.connect(self._update_performance)
            self.performance_timer.start(30000)  # Update every 30 seconds
            
            # Initial update
            self._update_performance()
            
        except Exception as e:
            pass
    
    def _update_performance(self):
        """Update solar performance metrics and emit signal"""
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
                                   (panel_count * self.panel_config['panel_power'] / 1000)) * 100 if panel_count > 0 else 0.0
                system_efficiency = min(100, max(0, system_efficiency))
                
                # Irradiance percentage
                irradiance_percent = min(100, (clear_sky_irradiance / 1000) * 100)
                
            else:
                current_power = 0.0
                daily_energy = 0.0
                system_efficiency = 0.0
                irradiance_percent = 0.0
            
            # Emit performance update signal with irradiance
            self.performance_updated.emit(current_power, daily_energy, system_efficiency, irradiance_percent)
            
        except Exception as e:
            pass
    
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
            return 45.0  # Default value
    
    def _calculate_solar_azimuth(self):
        """Calculate solar azimuth angle"""
        try:
            # Simplified azimuth calculation
            hour_angle = 15 * (self.current_time - 12)
            return 180 + hour_angle  # Simplified model
            
        except Exception as e:
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
            
        except Exception as e:
            pass
    
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
            QMessageBox.critical(self, "Error", f"Error opening obstacle dialog: {e}")
    
    def _apply_panels_to_roof(self, config):
        """Apply solar panels to the roof in the 3D model"""
        try:
            # Get the model tab
            model_tab = self._get_model_tab()
            if not model_tab:
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
                    return True
                else:
                    return False
            else:
                # Try emitting signal as fallback
                self.solar_panel_config_changed.emit(config)
                return True
                
        except Exception as e:
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
        except Exception as e:
            pass

    def _handle_environment_action(self, model_tab, action_type, parameters):
        """Handle environment actions by calling appropriate BaseRoof methods"""
        try:
            # Get the current roof from model tab
            current_roof = getattr(model_tab, 'current_roof', None)
            if not current_roof:
                return False
            
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
                
                return True
            
            else:
                return False
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def update_theme(self, is_dark_theme):
        """Update theme - uses your blue styling"""
        pass

    def connect_signals(self):
        """Enhanced signal connections including environment"""
        try:
            # Connect environment tab if available
            if self.environment_tab and hasattr(self.environment_tab, 'environment_action_requested'):
                self.environment_tab.environment_action_requested.connect(
                    self.environment_action_requested.emit
                )
                
        except Exception as e:
            pass

    def cleanup(self):
        """Enhanced cleanup with environment tab"""
        try:
            # Stop performance timer
            if hasattr(self, 'performance_timer') and self.performance_timer:
                try:
                    self.performance_timer.stop()
                except Exception as timer_error:
                    pass
                finally:
                    self.performance_timer = None
            
            # Cleanup environment tab
            if hasattr(self, 'environment_tab') and self.environment_tab:
                try:
                    if hasattr(self.environment_tab, 'cleanup'):
                        self.environment_tab.cleanup()
                except Exception as env_error:
                    pass
                finally:
                    self.environment_tab = None
            
            # Clear control references safely
            control_refs = [
                'solar_config_btn', 'obstacle_btn', 'panel_status', 'obstacle_status'
            ]
            
            for ref in control_refs:
                if hasattr(self, ref):
                    setattr(self, ref, None)
            
            # Clear group references safely
            group_refs = ['panel_group', 'obstacle_group']
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
                    pass
                finally:
                    self.modifications_tabs = None
            
            # Clear configuration data
            if hasattr(self, 'panel_config'):
                self.panel_config = None
            
            # Clear main window reference last
            self.main_window = None
                
        except Exception as e:
            import traceback
            traceback.print_exc()
