#!/usr/bin/env python3
"""
ui/content_tabs/model_tab.py
Model Tab with only plotter - left panel is separate
ENHANCED with advanced solar system integration - COMPLETE VERSION
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont
import math
import numpy as np
from datetime import datetime, timedelta

# Import PyVista components for 3D view
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
    print("✅ PyVista available for 3D visualization")
except ImportError:
    PYVISTA_AVAILABLE = False
    print("⚠️ PyVista not available - 3D view will be limited")

# Import your advanced solar system modules
try:
    from solar_system.solar_calculations import SolarCalculations
    SOLAR_CALCULATIONS_AVAILABLE = True
    print("✅ SolarCalculations module available")
except ImportError:
    SOLAR_CALCULATIONS_AVAILABLE = False
    print("⚠️ SolarCalculations module not found")

try:
    from solar_system.solar_lighting_system import SolarLightingSystem
    SOLAR_LIGHTING_AVAILABLE = True
    print("✅ SolarLightingSystem module available")
except ImportError:
    SOLAR_LIGHTING_AVAILABLE = False
    print("⚠️ SolarLightingSystem module not found")

try:
    from solar_system.solar_simulation import AdvancedSolarVisualization
    SOLAR_SIMULATION_AVAILABLE = True
    print("✅ AdvancedSolarVisualization module available")
except ImportError:
    SOLAR_SIMULATION_AVAILABLE = False
    print("⚠️ AdvancedSolarVisualization module not found")

try:
    from solar_system.unified_sun_system import UnifiedSunSystem
    UNIFIED_SUN_AVAILABLE = True
    print("✅ UnifiedSunSystem module available")
except ImportError:
    UNIFIED_SUN_AVAILABLE = False
    print("⚠️ UnifiedSunSystem module not found")

class ModelTab(QWidget):
    """
    Model Tab - Contains only the 3D plotter/viewer
    Left panel is handled separately in ui/panel/model_tab_left
    ENHANCED with advanced solar system integration
    """
    
    # Signals
    building_generated = pyqtSignal(object)
    model_updated = pyqtSignal(object)
    view_changed = pyqtSignal(str)
    roof_generated = pyqtSignal(object)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Initialize state
        self.current_building = None
        self.current_roof = None
        self.plotter = None
        self.vtk_widget = None
        self.debug_mode = True
        
        # Building meshes and materials
        self.building_meshes = []
        self.roof_meshes = []
        self.panel_meshes = []
        
        # Solar simulation state
        self.current_time = 12.0  # Decimal hours (noon)
        self.current_day = 172  # Day of year (summer solstice)
        self.latitude = 40.7128  # Default NYC
        self.longitude = -74.0060
        self.weather_factor = 1.0  # Clear sky
        self.shadows_enabled = True
        self.sunshafts_enabled = False
        
        # Solar panel configuration
        self.solar_panel_config = {
            'panel_type': 'monocrystalline',
            'efficiency': 0.20,
            'tilt_angle': 30.0,
            'azimuth_angle': 180.0,  # South facing
            'panel_width': 1.0,
            'panel_height': 2.0,
            'spacing': 0.1
        }
        
        # Animation state
        self.animation_active = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_solar_position)
        
        # Initialize advanced solar system modules
        self.solar_calculations = None
        self.solar_lighting_system = None
        self.solar_visualization = None
        self.unified_sun_system = None
        
        # Sun position and lighting
        self.sun_position = None
        self.sun_actor = None
        self.shadow_actors = []
        
        print("🏗️ Initializing Advanced Solar ModelTab...")
        
        try:
            self.setup_ui()
            self._initialize_solar_systems()
            self._calculate_initial_sun_position()
            print("✅ Advanced Solar ModelTab initialized successfully")
        except Exception as e:
            print(f"❌ ModelTab initialization failed: {e}")
            import traceback
            traceback.print_exc()

    def setup_ui(self):
        """Setup the UI with only the 3D plotter"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create 3D view container
        view_container = QFrame()
        view_container.setFrameStyle(QFrame.StyledPanel)
        
        view_layout = QVBoxLayout(view_container)
        view_layout.setContentsMargins(5, 5, 5, 5)
        view_layout.setSpacing(5)
        
        # Title bar
        title_frame = QFrame()
        title_frame.setMaximumHeight(40)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 4px;
            }
        """)
        
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)
                
        # 3D View Area
        if PYVISTA_AVAILABLE:
            self.setup_pyvista_view(view_layout)
        else:
            self.setup_fallback_3d_view(view_layout)
        
        main_layout.addWidget(view_container)
        
        print("✅ Advanced Solar ModelTab UI setup completed")

    def setup_pyvista_view(self, layout):
        """Setup PyVista 3D view with advanced solar capabilities"""
        try:
            # Create PyVista plotter widget
            self.plotter = QtInteractor(layout.parent())
            self.plotter.setMinimumHeight(500)
            
            # Set up the plotter with enhanced lighting
            self.plotter.set_background('lightblue')
            self.plotter.show_axes()
            self.plotter.show_grid()
            
            # NO WELCOME TEXT - Keep plotter clean
            
            # Store reference to the VTK widget
            self.vtk_widget = self.plotter.interactor
            layout.addWidget(self.vtk_widget)
            
            print("✅ Advanced PyVista 3D view initialized")
            
        except Exception as e:
            print(f"❌ PyVista view setup failed: {e}")
            import traceback
            traceback.print_exc()
            self.plotter = None
            self.vtk_widget = None
            self.setup_fallback_3d_view(layout)

    def setup_fallback_3d_view(self, layout):
        """Setup fallback 3D view placeholder"""
        placeholder = QLabel("3D View Area")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(500)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                border: 2px dashed #7f8c8d;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Add some helpful text
        placeholder.setText("""
🌞 Advanced Solar Model View

PyVista not available
3D visualization limited

To enable full 3D features:
pip install pyvista pyvistaqt

Current status: Fallback mode
        """)
        
        layout.addWidget(placeholder)
        self.plotter = None
        self.vtk_widget = None
        
        print("⚠️ Using fallback 3D view")

    def _initialize_solar_systems(self):
        """Initialize all solar system modules"""
        try:
            if not self.plotter:
                print("⚠️ No plotter available for solar system initialization")
                return
            
            # Initialize SolarCalculations (static class, no instance needed)
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.solar_calculations = SolarCalculations
                print("✅ SolarCalculations initialized")
            
            # Initialize SolarLightingSystem
            if SOLAR_LIGHTING_AVAILABLE:
                self.solar_lighting_system = SolarLightingSystem(self.plotter)
                print("✅ SolarLightingSystem initialized")
            
            # Initialize AdvancedSolarVisualization
            if SOLAR_SIMULATION_AVAILABLE:
                self.solar_visualization = AdvancedSolarVisualization(self.plotter)
                # Connect performance signal
                self.solar_visualization.performance_updated.connect(self._on_performance_updated)
                print("✅ AdvancedSolarVisualization initialized")
            
            # Initialize UnifiedSunSystem
            if UNIFIED_SUN_AVAILABLE:
                self.unified_sun_system = UnifiedSunSystem(self.plotter)
                print("✅ UnifiedSunSystem initialized")
            
            print("✅ All available solar systems initialized")
            
        except Exception as e:
            print(f"❌ Solar system initialization failed: {e}")
            import traceback
            traceback.print_exc()

    def _on_performance_updated(self, power, energy, efficiency):
        """Handle performance updates from solar visualization"""
        try:
            print(f"📊 Solar performance updated: {power:.1f}kW, {energy:.1f}kWh, {efficiency:.1f}%")
            # Update info display
            self._update_solar_info_display()
        except Exception as e:
            print(f"❌ Performance update handling failed: {e}")

    # ===========================================
    # SOLAR SIMULATION METHODS (Left Panel Signals)
    # ===========================================

    def update_solar_time(self, decimal_time):
        """Update solar time simulation - handles time_changed signal"""
        try:
            print(f"🌞 Updating solar time to {decimal_time}")
            
            # Store current time
            self.current_time = decimal_time
            
            # Update all solar systems
            self._update_all_solar_systems()
            
            print(f"✅ Solar time updated to {decimal_time}")
            
        except Exception as e:
            print(f"❌ Solar time update failed: {e}")
            import traceback
            traceback.print_exc()

    def update_solar_day(self, day_of_year):
        """Update solar day simulation - handles date_changed signal"""
        try:
            print(f"🌞 Updating solar day to {day_of_year}")
            
            # Store current day
            self.current_day = day_of_year
            
            # Update all solar systems
            self._update_all_solar_systems()
            
            print(f"✅ Solar day updated to {day_of_year}")
            
        except Exception as e:
            print(f"❌ Solar day update failed: {e}")
            import traceback
            traceback.print_exc()

    def set_location(self, latitude, longitude):
        """Set location - handles location_changed signal"""
        try:
            print(f"🌍 Setting location to {latitude}, {longitude}")
            
            # Store location
            self.latitude = latitude
            self.longitude = longitude
            
            # Update all solar systems
            self._update_all_solar_systems()
            
            print(f"✅ Location set to {latitude}, {longitude}")
            
        except Exception as e:
            print(f"❌ Location setting failed: {e}")
            import traceback
            traceback.print_exc()

    def set_weather_factor(self, factor):
        """Set weather factor - handles weather_changed signal"""
        try:
            print(f"🌤️ Setting weather factor to {factor}")
            
            # Store weather factor
            self.weather_factor = factor
            
            # Update solar visualization
            if self.solar_visualization:
                self.solar_visualization.set_weather_factor(factor)
            
            # Update all solar systems
            self._update_all_solar_systems()
            
            print(f"✅ Weather factor set to {factor}")
            
        except Exception as e:
            print(f"❌ Weather factor setting failed: {e}")
            import traceback
            traceback.print_exc()

    def toggle_solar_effects(self, shadows=None, sunshafts=None):
        """Toggle solar effects - handles solar_effects_toggled signal"""
        try:
            if shadows is not None:
                print(f"🌑 Shadows: {shadows}")
                self.shadows_enabled = shadows
                
            if sunshafts is not None:
                print(f"☀️ Sunshafts: {sunshafts}")
                self.sunshafts_enabled = sunshafts
            
            # Update solar visualization
            if self.solar_visualization:
                self.solar_visualization.set_visual_effects(
                    shadows=shadows,
                    sunshafts=sunshafts
                )
            
            # Update unified sun system
            self._update_unified_sun_system()
            
            print("✅ Solar effects updated")
            
        except Exception as e:
            print(f"❌ Solar effects toggle failed: {e}")
            import traceback
            traceback.print_exc()

    def handle_animation_toggle(self, enabled):
        """Handle animation toggle - handles animation_toggled signal"""
        try:
            print(f"🎬 Animation toggled: {enabled}")
            
            self.animation_active = enabled
            
            if enabled:
                # Start animation timer (update every 100ms)
                self.animation_timer.start(100)
                print("✅ Solar animation started")
            else:
                # Stop animation timer
                self.animation_timer.stop()
                print("✅ Solar animation stopped")
                
        except Exception as e:
            print(f"❌ Animation toggle failed: {e}")

    def handle_solar_panel_config_change(self, config):
        """Handle solar panel configuration change - handles solar_panel_config_changed signal"""
        try:
            print(f"🔧 Solar panel config changed: {config}")
            
            # Update solar panel configuration
            self.solar_panel_config.update(config)
            
            # Update solar visualization
            if self.solar_visualization:
                # Update panel efficiency and power
                if 'efficiency' in config:
                    self.solar_visualization.panel_efficiency = config['efficiency']
                if 'power' in config:
                    self.solar_visualization.panel_power = config['power']
                
                # Recreate solar panels if building exists
                if self.current_building:
                    self.solar_visualization.create_advanced_solar_panels()
            
            print("✅ Solar panel configuration updated")
            
        except Exception as e:
            print(f"❌ Solar panel config change failed: {e}")
            import traceback
            traceback.print_exc()

    def handle_obstacle_placement(self, obstacle_type, position):
        """Handle obstacle placement - handles obstacle_placement_requested signal"""
        try:
            print(f"🚧 Placing obstacle: {obstacle_type} at {position}")
            
            if not self.plotter:
                print("❌ No plotter available for obstacle placement")
                return
            
            # Create obstacle based on type
            if obstacle_type == "tree":
                self._place_tree_obstacle(position)
            elif obstacle_type == "building":
                self._place_building_obstacle(position)
            elif obstacle_type == "chimney":
                self._place_chimney_obstacle(position)
            
            # Update shadow calculations in solar visualization
            if self.solar_visualization:
                self.solar_visualization.update_comprehensive_shadows()
            
            print(f"✅ Obstacle {obstacle_type} placed at {position}")
            
        except Exception as e:
            print(f"❌ Obstacle placement failed: {e}")
            import traceback
            traceback.print_exc()

    def handle_export_model_request(self):
        """Handle export model request - handles export_model_requested signal"""
        try:
            print("💾 Exporting advanced solar model")
            
            if not self.plotter:
                print("❌ No plotter available for export")
                return False
            
            # Get solar performance data
            power, energy, efficiency = self.get_solar_performance()
            
            # Export model data
            export_data = {
                'building': self.current_building,
                'solar_config': self.solar_panel_config,
                'location': {'latitude': self.latitude, 'longitude': self.longitude},
                'time': self.current_time,
                'day': self.current_day,
                'weather': self.weather_factor,
                'performance': {
                    'power': power,
                    'energy': energy,
                    'efficiency': efficiency
                },
                'solar_systems': {
                    'calculations_available': SOLAR_CALCULATIONS_AVAILABLE,
                    'lighting_available': SOLAR_LIGHTING_AVAILABLE,
                    'simulation_available': SOLAR_SIMULATION_AVAILABLE,
                    'unified_sun_available': UNIFIED_SUN_AVAILABLE
                }
            }
            
            # You can add actual file export logic here
            print(f"✅ Advanced solar model export data prepared: {len(str(export_data))} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ Model export failed: {e}")
            return False

    # ===========================================
    # SOLAR SYSTEM INTEGRATION METHODS
    # ===========================================

    def _calculate_initial_sun_position(self):
        """Calculate initial sun position using advanced solar calculations"""
        try:
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude
                )
                print(f"✅ Initial sun position calculated: {self.sun_position}")
            else:
                # Fallback calculation
                self.sun_position = [100, 100, 50]
                print("⚠️ Using fallback sun position calculation")
                
        except Exception as e:
            print(f"❌ Initial sun position calculation failed: {e}")
            self.sun_position = [100, 100, 50]

    def _update_all_solar_systems(self):
        """Update all solar systems with current parameters - FIXED"""
        try:
            # Get building height if available
            building_height = 3.0  # Default
            if self.current_building:
                building_height = self.current_building.get('height', 3.0)
            
            # Calculate new sun position with building height
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude,
                    building_height  # Pass building height
                )
            
            # Update solar lighting system
            if self.solar_lighting_system:
                solar_settings = {
                    'current_hour': self.current_time,
                    'current_day': self.current_day,
                    'latitude': self.latitude,
                    'longitude': self.longitude,
                    'weather_factor': self.weather_factor
                }
                self.solar_lighting_system.setup_solar_lighting(self.sun_position, solar_settings)
            
            # Update solar visualization - FIXED METHOD CALLS
            if self.solar_visualization:
                self.solar_visualization.current_hour = self.current_time
                self.solar_visualization.current_day = self.current_day
                self.solar_visualization.latitude = self.latitude
                self.solar_visualization.longitude = self.longitude
                self.solar_visualization.weather_factor = self.weather_factor
                
                # Update sun and shadows - FIXED METHOD NAMES
                self.solar_visualization.create_realistic_sun()  # ✅ FIXED
                if self.shadows_enabled:
                    self.solar_visualization.update_comprehensive_shadows()  # ✅ FIXED
            
            # Update unified sun system
            self._update_unified_sun_system()
            
            # Update info display
            self._update_solar_info_display()
            
            print("✅ All solar systems updated")
            
        except Exception as e:
            print(f"❌ Solar systems update failed: {e}")
            import traceback
            traceback.print_exc()


    def _update_unified_sun_system(self):
        """Update unified sun system"""
        try:
            if self.unified_sun_system and self.sun_position:
                solar_settings = {
                    'current_hour': self.current_time,
                    'current_day': self.current_day,
                    'latitude': self.latitude,
                    'longitude': self.longitude,
                    'weather_factor': self.weather_factor,
                    'sunshafts_enabled': self.sunshafts_enabled
                }
                self.unified_sun_system.create_unified_sun(self.sun_position, solar_settings)
                
        except Exception as e:
            print(f"❌ Unified sun system update failed: {e}")

    def _update_solar_info_display(self):
        """Update solar information display using advanced calculations"""
        try:
            # REMOVED - No text display in plotter for cleaner view
            # Just calculate and store values internally
            if not self.plotter:
                return
            
            # Get solar metrics (still calculate but don't display)
            power, energy, efficiency = self.get_solar_performance()
            
            # Get sunrise/sunset times (still calculate but don't display)
            if SOLAR_CALCULATIONS_AVAILABLE:
                sunrise, sunset = self.solar_calculations.get_time_range(self.latitude, self.current_day)
            else:
                sunrise, sunset = 6.0, 18.0
            
            # Calculate sun intensity (still calculate but don't display)
            if SOLAR_CALCULATIONS_AVAILABLE and self.sun_position:
                sun_intensity = self.solar_calculations.calculate_sun_intensity(
                    self.sun_position, self.weather_factor
                )
            
            # NO TEXT DISPLAY - Keep plotter clean
            print(f"📊 Solar metrics calculated: {power:.1f}kW, {energy:.1f}kWh, {efficiency:.1f}%")
            
        except Exception as e:
            print(f"❌ Solar info calculation failed: {e}")

    def _animate_solar_position(self):
        """Animate solar position over time"""
        try:
            if not self.animation_active:
                return
            
            # Increment time by 0.1 hours (6 minutes)
            self.current_time += 0.1
            
            # Reset at end of day
            if self.current_time >= 24:
                self.current_time = 0
            
            # Update all solar systems
            self._update_all_solar_systems()
            
        except Exception as e:
            print(f"❌ Solar animation failed: {e}")

    # ===========================================
    # OBSTACLE PLACEMENT METHODS
    # ===========================================

    def _place_tree_obstacle(self, position):
        """Place tree obstacle at position"""
        try:
            if not self.plotter:
                return
            
            x, y = position
            
            # Create simple tree (cylinder + sphere)
            trunk = pv.Cylinder(center=(x, y, 1), direction=(0, 0, 1), radius=0.2, height=2)
            leaves = pv.Sphere(center=(x, y, 2.5), radius=1)
            
            # Add to plotter
            self.plotter.add_mesh(trunk, color='brown', name=f'tree_trunk_{x}_{y}')
            self.plotter.add_mesh(leaves, color='green', name=f'tree_leaves_{x}_{y}')
            
            print(f"🌳 Tree placed at ({x}, {y})")
            
        except Exception as e:
            print(f"❌ Tree placement failed: {e}")

    def _place_building_obstacle(self, position):
        """Place building obstacle at position"""
        try:
            if not self.plotter:
                return
            
            x, y = position
            
            # Create simple building (box)
            building = pv.Box(bounds=(x-1, x+1, y-1, y+1, 0, 3))
            
            # Add to plotter
            self.plotter.add_mesh(building, color='lightgray', name=f'obstacle_building_{x}_{y}')
            
            print(f"🏢 Building obstacle placed at ({x}, {y})")
            
        except Exception as e:
            print(f"❌ Building obstacle placement failed: {e}")

    def _place_chimney_obstacle(self, position):
        """Place chimney obstacle at position"""
        try:
            if not self.plotter:
                return
            
            x, y = position
            
            # Create chimney (tall cylinder)
            chimney = pv.Cylinder(center=(x, y, 2), direction=(0, 0, 1), radius=0.3, height=4)
            
            # Add to plotter
            self.plotter.add_mesh(chimney, color='red', name=f'chimney_{x}_{y}')
            
            print(f"🏭 Chimney placed at ({x}, {y})")
            
        except Exception as e:
            print(f"❌ Chimney placement failed: {e}")

    # ===========================================
    # EXISTING METHODS (Enhanced)
    # ===========================================

    def refresh_view(self):
        """Refresh the 3D view"""
        try:
            print("🔧 Refreshing Advanced ModelTab view")
            
            if self.plotter:
                self.plotter.update()
                # Reset camera if needed
                if hasattr(self.plotter, 'reset_camera'):
                    self.plotter.reset_camera()
                
                # Update solar visualization
                self._update_all_solar_systems()
            
            print("✅ Advanced 3D view refreshed")
            
        except Exception as e:
            print(f"❌ View refresh failed: {e}")

    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05):
        """Create building in 3D view with advanced solar features"""
        try:
            print(f"🔧 Creating advanced building with {len(points)} points")
            
            if not points or len(points) < 3:
                print("❌ Invalid points for building creation")
                return False
            
            # Clear existing building
            if self.plotter:
                self.plotter.clear()
                self.plotter.set_background('lightblue')
                self.plotter.show_axes()
                self.plotter.show_grid()
            
            # Create building data
            building_data = {
                'points': points,
                'height': height,
                'roof_type': roof_type,
                'roof_pitch': roof_pitch,
                'scale': scale,
                'created_at': datetime.now()
            }
            
            # Store building
            self.current_building = building_data
            
            # Add building to 3D view
            if self.plotter:
                success = self._add_building_to_plotter(building_data)
                if not success:
                    print("❌ Building creation failed")
                    return False
            
            # Create roof object based on type
            try:
                if roof_type == 'pyramid':
                    from roofs.concrete.pyramid_roof import PyramidRoof
                    # Convert points to proper format for roof
                    base_points = []
                    for point in points:
                        if hasattr(point, 'x') and hasattr(point, 'y'):
                            x, y = point.x() * scale, point.y() * scale
                        else:
                            x, y = point[0] * scale, point[1] * scale
                        base_points.append([x, y, 0])
                    
                    self.current_roof = PyramidRoof(
                        plotter=self.plotter,
                        base_points=base_points[:4],  # Pyramid needs 4 points
                        apex_height=height,
                        building_height=0  # Base at ground level
                    )
                    print("✅ Created PyramidRoof object with panel handler")
                    
                elif roof_type == 'gable':
                    from roofs.concrete.gable_roof import GableRoof
                    # Similar conversion for gable roof
                    base_points = []
                    for point in points:
                        if hasattr(point, 'x') and hasattr(point, 'y'):
                            x, y = point.x() * scale, point.y() * scale
                        else:
                            x, y = point[0] * scale, point[1] * scale
                        base_points.append([x, y, 0])
                    
                    self.current_roof = GableRoof(
                        plotter=self.plotter,
                        base_points=base_points[:4],
                        ridge_height=height,
                        building_height=0
                    )
                    print("✅ Created GableRoof object with panel handler")
                    
                elif roof_type == 'flat':
                    from roofs.concrete.flat_roof import FlatRoof
                    # Flat roof creation
                    base_points = []
                    for point in points:
                        if hasattr(point, 'x') and hasattr(point, 'y'):
                            x, y = point.x() * scale, point.y() * scale
                        else:
                            x, y = point[0] * scale, point[1] * scale
                        base_points.append([x, y, height])
                    
                    self.current_roof = FlatRoof(
                        plotter=self.plotter,
                        base_points=base_points,
                        building_height=height
                    )
                    print("✅ Created FlatRoof object with panel handler")
                    
                else:
                    print(f"⚠️ Roof type '{roof_type}' not implemented yet")
                    self.current_roof = None
                    
            except Exception as e:
                print(f"❌ Error creating roof object: {e}")
                import traceback
                traceback.print_exc()
                self.current_roof = None
            
            # Set building in solar visualization
            if self.solar_visualization:
                building_mesh = self._create_building_mesh(building_data)
                if building_mesh:
                    self.solar_visualization.set_building(building_mesh)
            
            # Update all solar systems
            self._update_all_solar_systems()
            
            # Emit signal
            self.building_generated.emit(building_data)
            
            print("✅ Advanced building created successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Building creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False


    def _create_building_mesh(self, building_data):
        """Create building mesh for solar system"""
        try:
            points = building_data['points']
            height = building_data['height']
            scale = building_data['scale']
            
            # Convert points to 3D coordinates
            vertices = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    x, y = point.x() * scale, point.y() * scale
                else:
                    x, y = point[0] * scale, point[1] * scale
                vertices.append([x, y, height])  # Top vertices
            
            if len(vertices) > 2:
                # Create simple building mesh
                building_mesh = pv.PolyData(vertices)
                return building_mesh
            
            return None
            
        except Exception as e:
            print(f"❌ Building mesh creation failed: {e}")
            return None

    def _add_building_to_plotter(self, building_data):
        """Add building geometry to PyVista plotter (enhanced)"""
        try:
            if not self.plotter:
                print("❌ No plotter available")
                return False
            
            points = building_data['points']
            height = building_data['height']
            scale = building_data['scale']
            
            # Convert points to 3D coordinates
            vertices = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    x, y = point.x() * scale, point.y() * scale
                else:
                    x, y = point[0] * scale, point[1] * scale
                vertices.append([x, y, 0])  # Base
                vertices.append([x, y, height])  # Top
            
            # Create building visualization
            import numpy as np
            
            if len(vertices) > 0:
                vertices_array = np.array(vertices)
                
                # Add building points
                self.plotter.add_points(
                    vertices_array,
                    color='red',
                    point_size=8,
                    render_points_as_spheres=True
                )
                
                # Add building outline
                base_points = vertices_array[::2]  # Every other point (base)
                if len(base_points) > 2:
                    # Close the polygon
                    base_points = np.vstack([base_points, base_points[0]])
                    
                    # Create polyline for base
                    lines = []
                    for i in range(len(base_points) - 1):
                        lines.extend([2, i, i + 1])
                    
                    poly = pv.PolyData(base_points)
                    poly.lines = lines
                    
                    building_actor = self.plotter.add_mesh(poly, color='blue', line_width=4)
                    self.building_meshes.append(building_actor)
                    
                    # Add walls (vertical lines)
                    for i in range(0, len(vertices_array), 2):
                        if i + 1 < len(vertices_array):
                            wall_points = np.array([vertices_array[i], vertices_array[i+1]])
                            wall_lines = [2, 0, 1]
                            wall_poly = pv.PolyData(wall_points)
                            wall_poly.lines = wall_lines
                            wall_actor = self.plotter.add_mesh(wall_poly, color='green', line_width=3)
                            self.building_meshes.append(wall_actor)
            
            # NO INFO TEXT - Keep plotter clean
            
            # Reset camera to show full building
            self.plotter.reset_camera()
            
            print("✅ Advanced building added to 3D view successfully")
            return True
            
        except Exception as e:
            print(f"❌ Adding building to plotter failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_solar_performance(self):
        """Get solar performance metrics using advanced calculations"""
        try:
            if self.solar_visualization:
                return self.solar_visualization.calculate_solar_performance()
            
            # Fallback calculation
            if not self.current_building:
                return 0.0, 0.0, 0.0
            
            # Enhanced solar performance calculation
            base_power = 5.0  # kW
            base_energy = 40.0  # kWh
            base_efficiency = 75.0  # %
            
            # Weather factor adjustment
            weather_adjustment = self.weather_factor
            
            # Time of day adjustment
            if 6 <= self.current_time <= 18:
                time_adjustment = 1.0
            else:
                time_adjustment = 0.1
            
            # Sun elevation adjustment
            if self.sun_position and self.sun_position[2] > 0:
                elevation_adjustment = min(1.0, self.sun_position[2] / 20.0)
            else:
                elevation_adjustment = 0.0
            
            # Panel efficiency adjustment
            panel_efficiency = self.solar_panel_config.get('efficiency', 0.20)
            efficiency_adjustment = panel_efficiency / 0.20
            
            # Calculate final values
            power = base_power * weather_adjustment * time_adjustment * elevation_adjustment * efficiency_adjustment
            energy = base_energy * weather_adjustment * elevation_adjustment * efficiency_adjustment
            efficiency = base_efficiency * weather_adjustment * elevation_adjustment * efficiency_adjustment
            
            return power, energy, efficiency
            
        except Exception as e:
            print(f"❌ Solar performance calculation failed: {e}")
            return 0.0, 0.0, 0.0

    def get_time_range(self):
        """Get time range for current location and date using advanced calculations"""
        try:
            if SOLAR_CALCULATIONS_AVAILABLE:
                return self.solar_calculations.get_time_range(self.latitude, self.current_day)
            
            # Fallback calculation
            return 6.0, 18.0
            
        except Exception as e:
            print(f"❌ Time range calculation failed: {e}")
            return 6.0, 18.0

    def has_building(self):
        """Check if building exists"""
        return self.current_building is not None

    def get_plotter(self):
        """Get the 3D plotter"""
        return self.plotter

    def get_valid_plotter(self):
        """Get a valid plotter instance"""
        try:
            if self.plotter and hasattr(self.plotter, 'add_mesh'):
                return self.plotter
            return None
        except Exception as e:
            print(f"❌ Error getting valid plotter: {e}")
            return None

    def reset_plotter(self, camera_position=None):
        """Reset the plotter to clean state (enhanced)"""
        try:
            if PYVISTA_AVAILABLE and self.plotter:
                # Clear all actors
                self.plotter.clear()
                
                # Clear mesh lists
                self.building_meshes.clear()
                self.roof_meshes.clear()
                self.panel_meshes.clear()
                self.shadow_actors.clear()
                
                # Clear solar visualization
                if self.solar_visualization:
                    self.solar_visualization.clear_all()
                
                # Reset background and basic elements
                self.plotter.set_background('lightblue')
                self.plotter.show_axes()
                self.plotter.show_grid()
                
                # NO WELCOME TEXT - Keep plotter clean
                
                # Reset camera
                if camera_position:
                    try:
                        self.plotter.camera_position = camera_position
                    except:
                        pass
                else:
                    # Reset camera
                    if hasattr(self.plotter, 'reset_camera'):
                        self.plotter.reset_camera()
                
                # Force update
                if hasattr(self.plotter, 'update'):
                    self.plotter.update()
                
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                
                print("✅ Advanced model tab plotter reset")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error resetting plotter: {e}")
            return False

    def set_title(self, title):
        """Set tab title"""
        try:
            # This might be handled by the parent ContentTabWidget
            pass
        except Exception as e:
            print(f"❌ Set title failed: {e}")

    def cleanup(self):
        """Cleanup resources (enhanced)"""
        try:
            # Stop animation
            if self.animation_timer.isActive():
                self.animation_timer.stop()
            
            # Clear solar visualization
            if self.solar_visualization:
                self.solar_visualization.clear_all()

            # Clear current roof
            if hasattr(self, 'current_roof') and self.current_roof:
                del self.current_roof
                self.current_roof = None
            
            # Clear buildings
            self.building_meshes.clear()
            self.roof_meshes.clear()
            self.panel_meshes.clear()
            self.shadow_actors.clear()
            self.current_building = None
            
            # Close plotter
            if PYVISTA_AVAILABLE and self.plotter:
                if hasattr(self.plotter, 'close'):
                    self.plotter.close()
            
            print("✅ Advanced Model Tab cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    def visualize_sun_path(self):
        """Visualize the sun's path across the sky"""
        try:
            if not self.plotter or not SOLAR_CALCULATIONS_AVAILABLE:
                return
            
            # Get building height
            building_height = 3.0
            if self.current_building:
                building_height = self.current_building.get('height', 3.0)
            
            # Calculate sun path
            sun_path = self.solar_calculations.calculate_realistic_sun_path(
                self.latitude, self.current_day, building_height
            )
            
            if len(sun_path) > 1:
                # Create path line
                path_line = pv.PolyData(np.array(sun_path))
                path_line.lines = np.hstack([[len(sun_path)] + list(range(len(sun_path)))])
                
                # Add to plotter
                self.plotter.add_mesh(
                    path_line,
                    color='yellow',
                    line_width=2,
                    opacity=0.5,
                    name='sun_path'
                )
                
                # Add markers for key positions
                key_positions = self.solar_calculations.get_cardinal_sun_positions(
                    self.latitude, self.current_day, building_height
                )
                
                for name, pos in key_positions.items():
                    if pos[2] > 0:  # Only show if above horizon
                        sphere = pv.Sphere(radius=0.5, center=pos)
                        self.plotter.add_mesh(
                            sphere,
                            color='orange',
                            name=f'sun_{name}'
                        )
            
            print("✅ Sun path visualization added")
            
        except Exception as e:
            print(f"❌ Sun path visualization failed: {e}")
            
    def _update_all_solar_systems(self):
        """Update all solar systems with current parameters - FIXED FOR NOON BRIGHTNESS"""
        try:
            # Get building height if available
            building_height = 3.0  # Default
            if self.current_building:
                building_height = self.current_building.get('height', 3.0)
            
            # Calculate new sun position
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude,
                    building_height
                )
                
                # Get sunrise and sunset times
                sunrise, sunset = self.solar_calculations.get_time_range(self.latitude, self.current_day)
                
                # FORCE BRIGHT BACKGROUND AT NOON
                if 10 <= self.current_time <= 14:  # Between 10 AM and 2 PM
                    bg_color = '#87CEEB'  # Bright sky blue
                else:
                    bg_color = self.solar_calculations.get_background_color(self.current_time, sunrise, sunset)
                
                if self.plotter:
                    self.plotter.set_background(bg_color)
                    print(f"🎨 Background set to {bg_color} for time {self.current_time:.1f}")
            
            # Handle sun visibility
            if self.sun_position is None:
                # It's night - hide sun
                self._hide_sun()
                self._set_night_lighting()
            else:
                # It's day - show sun
                self._show_sun()
                
                # ENSURE BRIGHT LIGHTING AT NOON
                if self.solar_lighting_system:
                    solar_settings = {
                        'current_hour': self.current_time,
                        'current_day': self.current_day,
                        'latitude': self.latitude,
                        'longitude': self.longitude,
                        'weather_factor': self.weather_factor
                    }
                    self.solar_lighting_system.setup_solar_lighting(self.sun_position, solar_settings)
                    
                    # ADD EXTRA BRIGHTNESS AT NOON
                    if 11 <= self.current_time <= 13:
                        self._add_noon_brightness()
                
                # Update solar visualization
                if self.solar_visualization:
                    self.solar_visualization.current_hour = self.current_time
                    self.solar_visualization.current_day = self.current_day
                    self.solar_visualization.latitude = self.latitude
                    self.solar_visualization.longitude = self.longitude
                    self.solar_visualization.weather_factor = self.weather_factor
                    
                    # Update sun and shadows
                    self.solar_visualization.create_realistic_sun()
                    if self.shadows_enabled:
                        self.solar_visualization.update_comprehensive_shadows()
                
                # Update unified sun system
                self._update_unified_sun_system()
            
            # Update info display
            self._update_solar_info_display()
            
            # Don't print every update - only significant changes
            if hasattr(self, '_last_update_hour') and abs(self._last_update_hour - self.current_time) < 0.1:
                return  # Skip printing for minor updates
            
            self._last_update_hour = self.current_time
            print(f"✅ Solar systems updated for time {self.current_time:.1f}")
            
        except Exception as e:
            print(f"❌ Solar systems update failed: {e}")
            import traceback
            traceback.print_exc()

    def _add_noon_brightness(self):
        """Add extra brightness at noon"""
        try:
            if not self.plotter:
                return
                
            # Add additional overhead light for noon
            noon_light = pv.Light(
                position=(0, 0, 50),
                focal_point=(0, 0, 0),
                color=[1.0, 1.0, 1.0],  # Pure white
                intensity=0.5
            )
            self.plotter.add_light(noon_light)
            
            # Ensure bright ambient
            ambient_light = pv.Light(
                position=(10, 10, 30),
                focal_point=(0, 0, 0),
                color=[0.9, 0.95, 1.0],  # Slight blue tint
                intensity=0.4
            )
            self.plotter.add_light(ambient_light)
            
        except Exception as e:
            print(f"❌ Error adding noon brightness: {e}")


    def _hide_sun(self):
        """Hide sun during night time"""
        try:
            # List of sun-related actors to hide
            sun_actors = [
                'sun', 'sun_core', 'sun_glow', 'sun_corona',
                'sunshafts', 'sunshaft_particles'
            ]
            
            for actor_name in sun_actors:
                try:
                    self.plotter.remove_actor(actor_name)
                except:
                    pass
            
            # Also hide stored sun actor
            if hasattr(self, 'sun_actor') and self.sun_actor:
                try:
                    self.plotter.remove_actor(self.sun_actor)
                    self.sun_actor = None
                except:
                    pass
            
            print("🌙 Sun hidden (night time)")
            
        except Exception as e:
            print(f"❌ Error hiding sun: {e}")

    def _show_sun(self):
        """Show sun during day time"""
        # The sun will be recreated by the solar visualization systems
        print("☀️ Sun visible (day time)")

    def _set_night_lighting(self):
        """Set minimal lighting for night time"""
        try:
            if hasattr(self.plotter, 'remove_all_lights'):
                self.plotter.remove_all_lights()
            
            # Add dim ambient light for night
            night_light = pv.Light(
                position=(0, 0, 30),
                focal_point=(0, 0, 0),
                color=[0.2, 0.2, 0.4],  # Dim blue
                intensity=0.3
            )
            self.plotter.add_light(night_light)
            
            # Add a subtle moon light from the side
            moon_light = pv.Light(
                position=(20, 20, 20),
                focal_point=(0, 0, 0),
                color=[0.8, 0.8, 1.0],  # Cool white
                intensity=0.2
            )
            self.plotter.add_light(moon_light)
            
            print("🌙 Night lighting set")
            
        except Exception as e:
            print(f"❌ Error setting night lighting: {e}")

    def add_solar_panels(self, config):
        """Add solar panels to the current roof with the given configuration"""
        try:
            # Check if we have a roof
            if not hasattr(self, 'current_roof') or not self.current_roof:
                print("❌ No roof available for solar panel placement")
                return False
            
            # Check if the roof has a solar panel handler
            if not hasattr(self.current_roof, 'solar_panel_handler') or not self.current_roof.solar_panel_handler:
                print("❌ Current roof doesn't have a solar panel handler")
                return False
            
            # Update the solar panel handler configuration
            success = self.current_roof.solar_panel_handler.update_panel_config(config)
            if not success:
                print("❌ Failed to update panel configuration")
                return False
            
            print(f"✅ Solar panel configuration updated successfully")
            
            # For pyramid roof, we need to trigger panel placement on at least one side
            # You can modify this to add panels to specific sides based on your requirements
            if hasattr(self.current_roof, 'get_solar_panel_areas'):
                areas = self.current_roof.get_solar_panel_areas()
                if areas and len(areas) > 0:
                    # Add panels to the first side (front) by default
                    # You can modify this logic as needed
                    default_side = areas[0]  # This will be "front" for pyramid
                    print(f"🔧 Adding panels to default side: {default_side}")
                    self.current_roof.solar_panel_handler.add_panels(default_side)
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding solar panels: {e}")
            import traceback
            traceback.print_exc()
            return False


    def clear_solar_panels(self):
        """Clear all solar panels from the roof"""
        try:
            if hasattr(self, 'current_roof') and self.current_roof:
                if hasattr(self.current_roof, 'panel_handler') and self.current_roof.panel_handler:
                    self.current_roof.panel_handler.clear_panels()
                    print("✅ Solar panels cleared using panel handler")
                    return
                    
            print("⚠️ No roof or panel handler available for clearing")
            
        except Exception as e:
            print(f"❌ Error clearing solar panels: {e}")

    def add_obstacle(self, obstacle_type, dimensions):
        """Add obstacle to the roof"""
        try:
            print(f"🚧 Adding obstacle: {obstacle_type} with dimensions {dimensions}")
            
            if not self.plotter:
                print("❌ No plotter available for obstacles")
                return False
                
            # Check if we have a roof
            if not hasattr(self, 'current_roof') or not self.current_roof:
                print("❌ No roof available for obstacles")
                return False
                
            # Add obstacle to roof if it has the method
            if hasattr(self.current_roof, 'add_obstacle'):
                success = self.current_roof.add_obstacle(obstacle_type, dimensions)
                print(f"✅ Obstacle added via roof object")
                return success
            else:
                # Fallback: add obstacle directly
                return self._add_obstacle_fallback(obstacle_type, dimensions)
                
        except Exception as e:
            print(f"❌ Error adding obstacle: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _add_obstacle_fallback(self, obstacle_type, dimensions):
        """Fallback method to add obstacle directly to plotter"""
        try:
            if not self.current_building:
                print("❌ No building available for obstacle placement")
                return False
                
            # Get building parameters
            building_height = self.current_building.get('height', 3.0)
            points = self.current_building.get('points', [])
            scale = self.current_building.get('scale', 0.05)
            
            # Calculate building center
            xs = []
            ys = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    x, y = point.x() * scale, point.y() * scale
                else:
                    x, y = point[0] * scale, point[1] * scale
                xs.append(x)
                ys.append(y)
            
            if not xs or not ys:
                return False
            
            center_x = (min(xs) + max(xs)) / 2
            center_y = (min(ys) + max(ys)) / 2
            
            # Extract dimensions
            width, length, height = dimensions
            
            # Create obstacle based on type
            if obstacle_type.lower() in ['chimney', 'ventilation']:
                # Cylindrical obstacle
                obstacle = pv.Cylinder(
                    center=(center_x, center_y, building_height + height/2),
                    direction=(0, 0, 1),
                    radius=width/2,
                    height=height
                )
                color = 'red' if 'chimney' in obstacle_type.lower() else 'gray'
            else:
                # Box obstacle
                obstacle = pv.Box(bounds=(
                    center_x - width/2, center_x + width/2,
                    center_y - length/2, center_y + length/2,
                    building_height, building_height + height
                ))
                color = 'darkgray'
            
            # Add to plotter
            self.plotter.add_mesh(
                obstacle,
                color=color,
                name=f'obstacle_{obstacle_type}_{len(self.plotter.actors)}'
            )
            
            # Update shadows if solar visualization available
            if self.solar_visualization and self.shadows_enabled:
                self.solar_visualization.update_comprehensive_shadows()
            
            print(f"✅ Obstacle '{obstacle_type}' added to roof (fallback)")
            return True
            
        except Exception as e:
            print(f"❌ Error in fallback obstacle placement: {e}")
            return False
