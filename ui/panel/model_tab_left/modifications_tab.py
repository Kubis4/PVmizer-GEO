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
            'panel_power': 440,  # SunPower Maxeon 440W
            'panel_area': 1.94,  # m² per panel (1046mm x 1690mm ~Maxeon 6)
            'efficiency': 0.227  # 22.7% efficiency
        }
        
        self.setup_ui()
        self.setup_timers()
        self.setup_connections()
    
    def setup_ui(self):
        """Enhanced UI setup with proper styling"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignHCenter)
        
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
        """Apply environment action to roof — single tree/pole use interactive dot mode"""
        try:
            if not hasattr(roof, 'handle_environment_action'):
                return False

            # Single tree/pole → interactive placement (show dots, click to place)
            if action_type == 'add_tree':
                action_type = 'prepare_tree_placement'
            elif action_type == 'add_pole':
                action_type = 'prepare_pole_placement'

            result = roof.handle_environment_action(action_type, parameters)

            if result:
                self._trigger_render()

            return result

        except Exception as e:
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
                # Calculate panel area from dialog dimensions (mm → m²)
                p_len_mm = config.get('panel_length', 1700)
                p_wid_mm = config.get('panel_width', 1000)
                panel_area = (p_len_mm / 1000.0) * (p_wid_mm / 1000.0)

                # Update panel configuration
                self.panel_config.update({
                    'panel_power': config.get('panel_power', 400),
                    'panel_area': panel_area,
                    'efficiency': config.get('efficiency', 0.20)
                })

                # Emit signal for roof application (places panels on roof)
                self.solar_panel_config_changed.emit(config)

                # Update performance (reads actual placed panels from roof)
                self._update_performance()

                panel_count = self.panel_config['panel_count']
                QMessageBox.information(self, "Success",
                    f"Solar panel configuration applied!\n"
                    f"Panel area: {panel_area:.2f} m² | Power: {config.get('panel_power', 400)}W\n"
                    f"Panels placed: {panel_count}")
                        
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
    
    # Side name → facing azimuth (degrees, 0=N, 90=E, 180=S, 270=W)
    SIDE_AZIMUTH = {
        # Gable roof sides (ridge runs along Y-axis)
        'left': 270.0,   # faces west
        'right': 90.0,   # faces east
        # Hip / Pyramid roof sides
        'front': 180.0,  # faces south
        'back': 0.0,     # faces north
        # Flat roof zones — all face up (tilt overrides to 0)
        'center': 180.0, 'north': 180.0, 'south': 180.0,
        'east': 180.0, 'west': 180.0,
    }

    @staticmethod
    def _clear_sky_irradiance(sin_elev):
        """Compute clear-sky DNI and DHI from sun elevation (Hottel + Liu-Jordan).
        Returns (dni, dhi) in W/m².  sin_elev must be > 0."""
        air_mass = min(1.0 / max(sin_elev, 0.01), 38.0)
        # Kasten-Young clear-sky DNI (W/m²)
        dni = 1353.0 * 0.7 ** (air_mass ** 0.678)
        # Diffuse ≈ 10-15% of GHI; GHI = DNI * sin_elev + DHI
        dhi = max(0.0, 120.0 * sin_elev)  # simplified clear-sky diffuse
        return max(0.0, dni), max(0.0, dhi)

    def _update_performance(self):
        """Update solar performance based on actual panel placement per roof side"""
        try:
            # Get per-side panel counts from the actual roof
            sides_info = self._get_panels_per_side()

            if not sides_info:
                # No panels placed on the roof
                self.performance_updated.emit(0.0, 0.0, 0.0, 0.0)
                return

            panel_area = self.panel_config['panel_area']
            panel_power_w = self.panel_config['panel_power']
            efficiency = self.panel_config['efficiency']
            total_panel_count = sum(s['count'] for s in sides_info)

            # Sun position
            solar_elevation = self._calculate_solar_elevation()
            solar_azimuth = self._calculate_solar_azimuth()

            if solar_elevation <= 0:
                self.performance_updated.emit(0.0, 0.0, 0.0, 0.0)
                return

            elev_rad = math.radians(solar_elevation)
            sin_elev = math.sin(elev_rad)
            cos_elev = math.cos(elev_rad)

            # Clear-sky DNI and DHI (separate beam/diffuse)
            dni, dhi = self._clear_sky_irradiance(sin_elev)

            # Shadow factors from ray-tracing (tree crowns blocking panels)
            shadow_factors = self._shadow_factors_for_sun(
                sides_info, solar_elevation, solar_azimuth)

            # Sum power across all sides (each has its own tilt + azimuth)
            total_power_kw = 0.0
            weighted_poa = 0.0  # for average irradiance display

            for side in sides_info:
                tilt = side['tilt']
                az = side['azimuth']
                count = side['count']

                # cos(AOI) per side — angle between sun ray and panel normal
                az_diff = math.radians(solar_azimuth - az)
                cos_aoi = (sin_elev * math.cos(tilt) +
                           cos_elev * math.sin(tilt) * math.cos(az_diff))
                cos_aoi = max(0.0, cos_aoi)  # sun behind this face → 0

                # POA = beam component + diffuse component (isotropic sky model)
                poa_beam = dni * cos_aoi
                poa_diffuse = dhi * (1.0 + math.cos(tilt)) / 2.0
                poa = poa_beam + poa_diffuse
                poa = min(poa, 1200.0)

                # Apply shadow factor (fraction of panels lit) — only blocks beam
                sf = shadow_factors.get(side['name'], 1.0)
                poa_effective = poa_beam * sf + poa_diffuse

                side_power = (poa_effective * panel_area * count * efficiency) / 1000.0
                # Clamp: no side can exceed its panels' nameplate total
                max_side_kw = count * panel_power_w / 1000.0
                side_power = min(side_power, max_side_kw)
                total_power_kw += side_power
                weighted_poa += poa * count * sf

            avg_poa = weighted_poa / total_panel_count if total_panel_count > 0 else 0.0

            # Daily energy (integrate over all sides)
            daily_energy = self._estimate_daily_energy_per_side(sides_info, panel_area, efficiency)

            # System efficiency vs nameplate
            nameplate_kw = total_panel_count * panel_power_w / 1000.0
            system_efficiency = (total_power_kw / nameplate_kw * 100.0) if nameplate_kw > 0 else 0.0
            system_efficiency = min(100.0, max(0.0, system_efficiency))

            irradiance_percent = min(100.0, (avg_poa / 1000.0) * 100.0)

            self.performance_updated.emit(total_power_kw, daily_energy,
                                          system_efficiency, irradiance_percent)
        except Exception:
            pass

    def _get_panels_per_side(self):
        """Get list of dicts with count/tilt/azimuth for each side that has panels"""
        try:
            # Use self.current_roof directly (set via on_roof_created signal)
            roof = self.current_roof
            if not roof or not hasattr(roof, 'solar_panel_handler') or not roof.solar_panel_handler:
                # Fallback: try via model tab
                model_tab = self._get_model_tab()
                if model_tab and hasattr(model_tab, 'current_roof'):
                    roof = model_tab.current_roof
            if not roof or not hasattr(roof, 'solar_panel_handler') or not roof.solar_panel_handler:
                return []
            handler = roof.solar_panel_handler
            if not hasattr(handler, 'panels_count_by_side'):
                return []

            counts = handler.panels_count_by_side
            if sum(counts.values()) == 0:
                return []

            # Roof tilt
            tilt_rad = 0.0
            if hasattr(roof, 'slope_angle'):
                tilt_rad = float(roof.slope_angle)
            elif hasattr(roof, 'roof_angle'):
                tilt_rad = math.radians(float(roof.roof_angle))

            # Flat roof override
            is_flat = tilt_rad < 0.05  # ~3 degrees
            if hasattr(handler, 'panel_tilt') and handler.panel_tilt > 0:
                tilt_rad = math.radians(handler.panel_tilt)
                is_flat = False

            sides = []
            for side_name, count in counts.items():
                if count <= 0:
                    continue
                face_az = self.SIDE_AZIMUTH.get(side_name, 180.0)
                face_tilt = 0.0 if is_flat else tilt_rad
                sides.append({'name': side_name, 'count': count,
                              'tilt': face_tilt, 'azimuth': face_az})

            # Update total panel_config count for display
            self.panel_config['panel_count'] = sum(s['count'] for s in sides)
            return sides
        except Exception:
            return []

    def _estimate_daily_energy_per_side(self, sides_info, panel_area, efficiency):
        """Integrate daily energy across all sides in 30-min steps with shadow ray-tracing"""
        try:
            lat_rad = math.radians(self.latitude)
            dec = math.radians(
                23.45 * math.sin(math.radians(360.0 * (284 + self.day_of_year) / 365.0)))

            cos_ws = max(-1.0, min(1.0, -math.tan(lat_rad) * math.tan(dec)))
            sunrise_ha = math.acos(cos_ws)
            sunrise = 12.0 - math.degrees(sunrise_ha) / 15.0
            sunset = 12.0 + math.degrees(sunrise_ha) / 15.0

            # Pre-fetch tree crowns once for the whole day
            crowns = self._get_tree_crowns()
            has_trees = len(crowns) > 0

            # Get handler for panel positions (used for shadow checks)
            handler = None
            if has_trees and self.current_roof:
                handler = getattr(self.current_roof, 'solar_panel_handler', None)

            panel_power_w = self.panel_config.get('panel_power', 440)
            total_wh = 0.0
            step = 0.5
            t = sunrise
            while t < sunset:
                ha = math.radians(15.0 * (t - 12.0))
                sin_elev = (math.sin(lat_rad) * math.sin(dec) +
                            math.cos(lat_rad) * math.cos(dec) * math.cos(ha))
                if sin_elev <= 0.01:
                    t += step
                    continue
                elev_rad = math.asin(sin_elev)
                cos_elev = math.cos(elev_rad)

                # Sun azimuth at this time step
                cos_az = (math.sin(dec) - math.sin(lat_rad) * sin_elev) / \
                         (math.cos(lat_rad) * cos_elev) if cos_elev > 0.001 else 0.0
                cos_az = max(-1.0, min(1.0, cos_az))
                az_deg = math.degrees(math.acos(cos_az))
                if t > 12.0:
                    az_deg = 360.0 - az_deg

                # DNI / DHI clear-sky model (same as _update_performance)
                dni, dhi = self._clear_sky_irradiance(sin_elev)

                # Shadow factors at this time step
                step_shadow = {}
                if has_trees and handler and hasattr(handler, 'panel_positions_by_side'):
                    elev_deg = math.degrees(elev_rad)
                    step_shadow = self._shadow_factors_for_sun(
                        sides_info, elev_deg, az_deg)

                for side in sides_info:
                    az_diff = math.radians(az_deg - side['azimuth'])
                    cos_aoi = (sin_elev * math.cos(side['tilt']) +
                               cos_elev * math.sin(side['tilt']) * math.cos(az_diff))
                    cos_aoi = max(0.0, cos_aoi)
                    poa_beam = dni * cos_aoi
                    poa_diffuse = dhi * (1.0 + math.cos(side['tilt'])) / 2.0
                    sf = step_shadow.get(side['name'], 1.0)
                    # Shadow blocks beam only; diffuse still reaches
                    poa_effective = poa_beam * sf + poa_diffuse
                    side_w = poa_effective * panel_area * side['count'] * efficiency
                    # Clamp at nameplate
                    max_w = side['count'] * panel_power_w
                    side_w = min(side_w, max_w)
                    total_wh += side_w * step

                t += step
            return total_wh / 1000.0
        except Exception:
            return 0.0
    
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
        """Calculate solar azimuth angle (0=N, 90=E, 180=S, 270=W)"""
        try:
            declination = 23.45 * math.sin(math.radians(360 * (284 + self.day_of_year) / 365))
            hour_angle = 15 * (self.current_time - 12)

            lat_rad = math.radians(self.latitude)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)

            sin_elev = (math.sin(lat_rad) * math.sin(dec_rad) +
                        math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad))
            elev_rad = math.asin(max(-1.0, min(1.0, sin_elev)))
            cos_elev = math.cos(elev_rad)

            if cos_elev < 0.001:
                return 180.0

            cos_az = (math.sin(dec_rad) - math.sin(lat_rad) * sin_elev) / \
                     (math.cos(lat_rad) * cos_elev)
            cos_az = max(-1.0, min(1.0, cos_az))
            azimuth = math.degrees(math.acos(cos_az))

            # Afternoon → west side (azimuth > 180)
            if hour_angle > 0:
                azimuth = 360.0 - azimuth

            return azimuth

        except Exception:
            return 180.0

    # ==================== RAY-SHADOW CALCULATIONS ====================

    def _get_tree_crowns(self):
        """Extract tree crown spheres from roof's environment obstacles.
        Returns list of (cx, cy, cz, radius) tuples.
        """
        roof = self.current_roof
        if not roof:
            return []
        obstacles = getattr(roof, 'environment_obstacles', [])
        crowns = []
        for obs in obstacles:
            if 'tree' not in obs.get('type', ''):
                continue
            pos = obs.get('position', [0, 0])
            h = obs.get('height', 7.0)
            r = obs.get('radius', 2.0)
            # Crown sphere center sits atop the trunk
            crowns.append((float(pos[0]), float(pos[1]), float(h - r), float(r)))
        return crowns

    @staticmethod
    def _ray_intersects_sphere(px, py, pz, dx, dy, dz, cx, cy, cz, r):
        """Test if ray from (px,py,pz) toward direction (dx,dy,dz) hits sphere (cx,cy,cz,r).
        Returns True if sphere blocks the ray (intersection at t > 0).
        """
        ocx = px - cx
        ocy = py - cy
        ocz = pz - cz
        b = 2.0 * (ocx * dx + ocy * dy + ocz * dz)
        c = ocx * ocx + ocy * ocy + ocz * ocz - r * r
        disc = b * b - 4.0 * c
        if disc < 0:
            return False
        sqrt_d = math.sqrt(disc)
        t2 = (-b + sqrt_d) / 2.0  # far intersection
        return t2 > 0.0

    def _shadow_factors_for_sun(self, sides_info, solar_elevation, solar_azimuth):
        """Compute per-side shadow factor (0=fully shadowed, 1=fully lit).
        Casts a ray from each stored panel center toward the sun and checks
        intersection with tree crown spheres.
        """
        try:
            roof = self.current_roof
            if not roof:
                return {}

            handler = getattr(roof, 'solar_panel_handler', None)
            if not handler or not hasattr(handler, 'panel_positions_by_side'):
                return {}

            crowns = self._get_tree_crowns()
            if not crowns:
                return {}  # no trees → no shadow reduction

            elev_rad = math.radians(solar_elevation)
            az_rad = math.radians(solar_azimuth)
            sun_dx = math.cos(elev_rad) * math.sin(az_rad)
            sun_dy = math.cos(elev_rad) * math.cos(az_rad)
            sun_dz = math.sin(elev_rad)

            factors = {}
            for side in sides_info:
                name = side['name']
                positions = handler.panel_positions_by_side.get(name, [])
                if not positions:
                    continue
                lit = 0
                for p in positions:
                    blocked = False
                    for (cx, cy, cz, cr) in crowns:
                        if self._ray_intersects_sphere(
                                p[0], p[1], p[2],
                                sun_dx, sun_dy, sun_dz,
                                cx, cy, cz, cr):
                            blocked = True
                            break
                    if not blocked:
                        lit += 1
                factors[name] = lit / len(positions)
            return factors
        except Exception:
            return {}

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
