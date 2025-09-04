#!/usr/bin/env python3
"""
ui/panel/model_tab_left/modifications_tab.py
Enhanced Modifications tab with proper plotter connection and signal handling
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
    """Enhanced Modifications tab with proper plotter connection and signal handling"""
    
    # Signals
    solar_panel_config_changed = pyqtSignal(dict)
    obstacle_placement_requested = pyqtSignal(str, tuple)
    environment_action_requested = pyqtSignal(str, dict)
    performance_updated = pyqtSignal(float, float, float, float)  # power, energy, efficiency, irradiance
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Connection state tracking
        self.current_roof = None
        
        # Control references for roof modifications
        self.solar_config_btn = None
        self.obstacle_btn = None
        self.performance_timer = None
        self.connection_timer = None
        
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
        self.setup_timers()
        self.setup_connections()
    
    def setup_ui(self):
        """Enhanced UI setup with proper styling"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Apply styling with width constraints
        self.setStyleSheet("""
            QWidget {
                background-color: transparent !important;
                max-width: 410px !important;
            }
            
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
            
            QLabel {
                color: #ffffff !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 12px !important;
                font-weight: normal !important;
                max-width: 390px !important;
            }
            
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
        
        # Create internal tabs
        self.setup_tabs(layout)
        
        layout.addStretch()

    def setup_tabs(self, layout):
        """Setup the internal tab system"""
        self.modifications_tabs = QTabWidget()
        self.modifications_tabs.setTabPosition(QTabWidget.North)
        self.modifications_tabs.setUsesScrollButtons(False)
        self.modifications_tabs.setMaximumWidth(410)
        self.modifications_tabs.setMinimumWidth(390)
        
        # Tab styling
        self.modifications_tabs.setStyleSheet("""
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
            
            QTabWidget > QWidget {
                background-color: transparent !important;
                max-width: 410px !important;
            }
        """)
        
        # Tab 1: Roof modifications
        roof_tab = QWidget()
        self.setup_roof_modifications_tab(roof_tab)
        self.modifications_tabs.addTab(roof_tab, "🏠 Roof")
        
        # Tab 2: Environment tab
        self.setup_environment_tab()
        
        layout.addWidget(self.modifications_tabs)

    def setup_roof_modifications_tab(self, tab_widget):
        """Setup the roof modifications tab"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
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
        """Setup solar panel configuration section"""
        panel_group = QGroupBox("🔋 Solar Panel Configuration")
        panel_group.setMaximumWidth(390)
        
        panel_layout = QVBoxLayout(panel_group)
        panel_layout.setContentsMargins(10, 15, 10, 10)
        panel_layout.setSpacing(10)
        
        # Info label
        panel_info = QLabel("Configure solar panel placement, specifications, and optimization settings")
        panel_info.setWordWrap(True)
        panel_info.setMaximumWidth(370)
        panel_layout.addWidget(panel_info)
        
        # Solar panel button
        self.solar_config_btn = QPushButton("🔋 Configure Solar Panels")
        self.solar_config_btn.setMinimumHeight(32)
        self.solar_config_btn.setMaximumWidth(370)
        self.solar_config_btn.clicked.connect(self._open_solar_panel_dialog)
        self.solar_config_btn.setEnabled(SOLAR_PANEL_DIALOG_AVAILABLE)
        panel_layout.addWidget(self.solar_config_btn)
        
        # Panel status
        if SOLAR_PANEL_DIALOG_AVAILABLE:
            self.panel_status = QLabel("✅ Solar panel configuration available")
        else:
            self.panel_status = QLabel("⚠️ Solar panel dialog not available")
        
        self.panel_status.setWordWrap(True)
        self.panel_status.setMaximumWidth(370)
        panel_layout.addWidget(self.panel_status)
        
        layout.addWidget(panel_group)
        self.panel_group = panel_group
    
    def setup_obstacle_section(self, layout):
        """Setup obstacle placement section"""
        obstacle_group = QGroupBox("🏗️ Roof Obstacles")
        obstacle_group.setMaximumWidth(390)
        
        obstacle_layout = QVBoxLayout(obstacle_group)
        obstacle_layout.setContentsMargins(10, 15, 10, 10)
        obstacle_layout.setSpacing(10)
        
        # Info label
        obstacle_info = QLabel("Add obstacles like chimneys, vents, HVAC equipment, and other roof structures")
        obstacle_info.setWordWrap(True)
        obstacle_info.setMaximumWidth(370)
        obstacle_layout.addWidget(obstacle_info)
        
        # Obstacle button
        self.obstacle_btn = QPushButton("🏗️ Add Roof Obstacles")
        self.obstacle_btn.setMinimumHeight(32)
        self.obstacle_btn.setMaximumWidth(370)
        self.obstacle_btn.clicked.connect(self._open_obstacle_dialog)
        self.obstacle_btn.setEnabled(OBSTACLE_DIALOG_AVAILABLE)
        obstacle_layout.addWidget(self.obstacle_btn)
        
        # Obstacle status
        if OBSTACLE_DIALOG_AVAILABLE:
            self.obstacle_status = QLabel("✅ Obstacle placement available")
        else:
            self.obstacle_status = QLabel("⚠️ Obstacle dialog not available")
        
        self.obstacle_status.setWordWrap(True)
        self.obstacle_status.setMaximumWidth(370)
        obstacle_layout.addWidget(self.obstacle_status)
        
        layout.addWidget(obstacle_group)
        self.obstacle_group = obstacle_group

    def setup_environment_tab(self):
        """Setup environment tab"""
        if ENVIRONMENT_TAB_AVAILABLE:
            try:
                self.environment_tab = EnvironmentTab(self.main_window)
                self.modifications_tabs.addTab(self.environment_tab, "🌲 Environment")
                
                # Connect environment signals
                if hasattr(self.environment_tab, 'environment_action_requested'):
                    self.environment_tab.environment_action_requested.connect(
                        self.environment_action_requested.emit
                    )
                
            except Exception as e:
                self._create_fallback_environment_tab()
        else:
            self._create_fallback_environment_tab()

    def _create_fallback_environment_tab(self):
        """Create fallback environment tab"""
        fallback_tab = QWidget()
        fallback_tab.setStyleSheet("""
            QWidget {
                background-color: transparent !important;
                max-width: 390px !important;
            }
        """)
        
        fallback_layout = QVBoxLayout(fallback_tab)
        fallback_layout.setContentsMargins(20, 20, 20, 20)
        
        error_label = QLabel("⚠️ Environment Tab Not Available")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setMaximumWidth(350)
        fallback_layout.addWidget(error_label)
        
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
    
    def setup_timers(self):
        """Setup all timers"""
        try:
            # Performance update timer
            self.performance_timer = QTimer()
            self.performance_timer.timeout.connect(self._update_performance)
            self.performance_timer.start(30000)  # Update every 30 seconds
            
            # Connection monitoring timer
            self.connection_timer = QTimer()
            self.connection_timer.timeout.connect(self._check_connections)
            self.connection_timer.start(2000)  # Check every 2 seconds
            
            # Initial updates
            self._update_performance()
            self._check_connections()
            
        except Exception as e:
            pass

    def setup_connections(self):
        """Setup initial signal connections"""
        try:
            # Connect to main window signals if available
            if hasattr(self.main_window, 'roof_created'):
                self.main_window.roof_created.connect(self.on_roof_created)
            
        except Exception as e:
            pass

    def _check_connections(self):
        """Check and establish connections periodically"""
        try:
            # Find current roof
            new_roof = self._find_current_roof()
            
            # Check if roof changed
            if new_roof != self.current_roof:
                if new_roof:
                    self.current_roof = new_roof
                    self._establish_roof_connections(new_roof)
                else:
                    self.current_roof = None
            
        except Exception as e:
            pass

    def _find_current_roof(self):
        """Find the current roof from various locations"""
        try:
            # Method 1: Through roof generation manager
            if hasattr(self.main_window, 'roof_generation_manager'):
                manager = self.main_window.roof_generation_manager
                if hasattr(manager, 'current_roof') and manager.current_roof:
                    return manager.current_roof
            
            # Method 2: Through model tab
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'current_roof') and model_tab.current_roof:
                return model_tab.current_roof
            
            # Method 3: Through content tabs
            if hasattr(self.main_window, 'content_tabs'):
                for i in range(self.main_window.content_tabs.count()):
                    tab = self.main_window.content_tabs.widget(i)
                    if hasattr(tab, 'current_roof') and tab.current_roof:
                        return tab.current_roof
            
            return None
            
        except Exception as e:
            return None

    def _establish_roof_connections(self, roof):
        """Establish connections with the roof"""
        try:
            if not roof:
                return False
            
            # Connect solar panel handler
            self._connect_solar_handler(roof)
            
            # Connect obstacle handler
            self._connect_obstacle_handler(roof)
            
            # Connect environment handler
            self._connect_environment_handler(roof)
            
            return True
            
        except Exception as e:
            return False

    def _connect_solar_handler(self, roof):
        """Connect solar panel handler"""
        try:
            # Disconnect existing connections
            try:
                self.solar_panel_config_changed.disconnect()
            except:
                pass
            
            # Create handler
            def handle_solar_config(config):
                return self._apply_solar_config_to_roof(config, roof)
            
            # Connect signal
            self.solar_panel_config_changed.connect(handle_solar_config)
            
        except Exception as e:
            pass

    def _connect_obstacle_handler(self, roof):
        """Connect obstacle handler"""
        try:
            # Disconnect existing connections
            try:
                self.obstacle_placement_requested.disconnect()
            except:
                pass
            
            # Create handler
            def handle_obstacle_placement(obstacle_type, dimensions):
                return self._apply_obstacle_to_roof(obstacle_type, dimensions, roof)
            
            # Connect signal
            self.obstacle_placement_requested.connect(handle_obstacle_placement)
            
        except Exception as e:
            pass

    def _connect_environment_handler(self, roof):
        """Connect environment handler"""
        try:
            # Disconnect existing connections
            try:
                self.environment_action_requested.disconnect()
            except:
                pass
            
            # Create handler
            def handle_environment_action(action_type, parameters):
                return self._apply_environment_action_to_roof(action_type, parameters, roof)
            
            # Connect signal
            self.environment_action_requested.connect(handle_environment_action)
            
        except Exception as e:
            pass

    # ==================== SIGNAL HANDLERS ====================

    def _apply_solar_config_to_roof(self, config, roof):
        """Apply solar configuration to roof"""
        try:
            # Method 1: Solar panel handler
            if hasattr(roof, 'solar_panel_handler') and roof.solar_panel_handler:
                handler = roof.solar_panel_handler
                
                # Update handler properties
                for key, value in config.items():
                    if hasattr(handler, key):
                        setattr(handler, key, value)
                
                # Update config if method available
                if hasattr(handler, 'update_config'):
                    handler.update_config(config)
                
                # Generate panels if method available
                if hasattr(handler, 'generate_panels'):
                    handler.generate_panels()
                
                return True
            
            # Method 2: Direct roof method
            elif hasattr(roof, 'add_solar_panels'):
                result = roof.add_solar_panels(config)
                return result
            
            # Method 3: Update panel config method
            elif hasattr(roof, 'update_panel_config'):
                result = roof.update_panel_config(config)
                return result
            
            else:
                return False
                
        except Exception as e:
            return False

    def _apply_obstacle_to_roof(self, obstacle_type, dimensions, roof):
        """Apply obstacle to roof"""
        try:
            # Method 1: Direct add_obstacle
            if hasattr(roof, 'add_obstacle'):
                result = roof.add_obstacle(obstacle_type, dimensions)
                if result:
                    self._trigger_render()
                    return True
            
            # Method 2: Set properties for placement mode
            if hasattr(roof, 'selected_obstacle_type'):
                roof.selected_obstacle_type = obstacle_type
            
            if hasattr(roof, 'obstacle_dimensions'):
                roof.obstacle_dimensions = dimensions
            
            # Method 3: Add attachment points
            if hasattr(roof, 'add_attachment_points'):
                roof.add_attachment_points()
                return True
            
            return True
            
        except Exception as e:
            return False

    def _apply_environment_action_to_roof(self, action_type, parameters, roof):
        """Apply environment action to roof with automatic attachment point management"""
        try:
            placement_successful = False
            
            # Handle direct placement actions (add_tree, add_pole)
            if action_type == 'add_tree' and hasattr(roof, 'add_environment_obstacle_at_point'):
                # Show attachment points temporarily
                if hasattr(roof, 'show_environment_attachment_points'):
                    roof.show_environment_attachment_points()
                elif hasattr(roof, 'add_attachment_points'):
                    roof.add_attachment_points()
                
                # Set tree type
                tree_type = parameters.get('tree_type', 'deciduous')
                if hasattr(roof, 'tree_type_index'):
                    if tree_type == 'pine':
                        roof.tree_type_index = 1
                    elif tree_type == 'oak':
                        roof.tree_type_index = 2
                    else:
                        roof.tree_type_index = 0
                
                # Place the tree
                result = roof.add_environment_obstacle_at_point('tree')
                placement_successful = result
                
                # ALWAYS hide attachment points after placement attempt
                if hasattr(roof, 'hide_environment_attachment_points'):
                    roof.hide_environment_attachment_points()
                elif hasattr(roof, 'attachment_points_actor') and roof.attachment_points_actor:
                    roof.attachment_points_actor.SetVisibility(False)
                
            elif action_type == 'add_pole' and hasattr(roof, 'add_environment_obstacle_at_point'):
                # Show attachment points temporarily
                if hasattr(roof, 'show_environment_attachment_points'):
                    roof.show_environment_attachment_points()
                elif hasattr(roof, 'add_attachment_points'):
                    roof.add_attachment_points()
                
                # Place the pole
                result = roof.add_environment_obstacle_at_point('pole')
                placement_successful = result
                
                # ALWAYS hide attachment points after placement attempt
                if hasattr(roof, 'hide_environment_attachment_points'):
                    roof.hide_environment_attachment_points()
                elif hasattr(roof, 'attachment_points_actor') and roof.attachment_points_actor:
                    roof.attachment_points_actor.SetVisibility(False)
            
            # Handle other action types...
            elif action_type == 'clear_all_environment' and hasattr(roof, 'clear_environment_obstacles'):
                roof.clear_environment_obstacles()
                placement_successful = True
                
                # Hide attachment points when clearing
                if hasattr(roof, 'hide_environment_attachment_points'):
                    roof.hide_environment_attachment_points()
            
            # Handle prepare_tree_placement and prepare_pole_placement (for interactive mode)
            elif action_type in ['prepare_tree_placement', 'prepare_pole_placement']:
                # These are for interactive placement mode - handled by environment manager
                if hasattr(roof, 'handle_environment_action'):
                    result = roof.handle_environment_action(action_type, parameters)
                    placement_successful = result
            
            # Default handler
            elif hasattr(roof, 'handle_environment_action'):
                result = roof.handle_environment_action(action_type, parameters)
                placement_successful = result
            
            # Trigger render after any action
            if placement_successful:
                self._trigger_render()
            
            return placement_successful
                
        except Exception as e:
            # On error, try to hide attachment points anyway
            try:
                if hasattr(roof, 'hide_environment_attachment_points'):
                    roof.hide_environment_attachment_points()
            except:
                pass
            
            return False



    def _trigger_render(self):
        """Trigger plotter render"""
        try:
            if self.current_roof and hasattr(self.current_roof, 'plotter'):
                plotter = self.current_roof.plotter
                if plotter and hasattr(plotter, 'render'):
                    QTimer.singleShot(50, plotter.render)
            
        except Exception as e:
            pass

    # ==================== DIALOG HANDLERS ====================

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
                self.panel_config.update({
                    'panel_count': config.get('panel_count', 10),
                    'panel_power': config.get('panel_power', 400),
                    'efficiency': config.get('efficiency', 0.20)
                })
                
                # Emit signal for roof application
                self.solar_panel_config_changed.emit(config)
                
                # Update performance
                self._update_performance()
                
                QMessageBox.information(self, "Success", 
                    f"Solar panel configuration applied!\n{self.panel_config['panel_count']} panels configured.")
                        
        except Exception as e:
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
                    # Emit signal for roof application
                    self.obstacle_placement_requested.emit(obstacle_type, dimensions)
                    QMessageBox.information(self, "Success", 
                        f"Obstacle '{obstacle_type}' placement requested!")
                            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening obstacle dialog: {e}")

    # ==================== PERFORMANCE CALCULATIONS ====================
    
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
            
            # Emit performance update signal
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

    # ==================== UTILITY METHODS ====================

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

    def on_roof_created(self, roof):
        """Handle roof creation signal"""
        try:
            self.current_roof = roof
            self._establish_roof_connections(roof)
            
        except Exception as e:
            pass

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

    def update_theme(self, is_dark_theme):
        """Update theme - uses blue styling"""
        pass

    def connect_signals(self):
        """Connect additional signals"""
        try:
            # Connect environment tab if available
            if self.environment_tab and hasattr(self.environment_tab, 'environment_action_requested'):
                self.environment_tab.environment_action_requested.connect(
                    self.environment_action_requested.emit
                )
                
        except Exception as e:
            pass

    def cleanup(self):
        """Enhanced cleanup"""
        try:
            # Stop timers
            if self.performance_timer:
                self.performance_timer.stop()
                self.performance_timer = None
            
            if self.connection_timer:
                self.connection_timer.stop()
                self.connection_timer = None
            
            # Cleanup environment tab
            if self.environment_tab and hasattr(self.environment_tab, 'cleanup'):
                self.environment_tab.cleanup()
            
            # Clear references
            self.current_roof = None
            self.main_window = None
                
        except Exception as e:
            pass
