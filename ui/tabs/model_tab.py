#!/usr/bin/env python3
"""
ui/tabs/model_tab.py - Complete version with environment integration and debug
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont
import math
import numpy as np
from datetime import datetime, timedelta

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

try:
    from solar_system.solar_calculations import SolarCalculations
    SOLAR_CALCULATIONS_AVAILABLE = True
except ImportError:
    SOLAR_CALCULATIONS_AVAILABLE = False

try:
    from solar_system.enhanced_sun_system import EnhancedRealisticSunSystem
    ENHANCED_SUN_AVAILABLE = True
except ImportError as e:
    ENHANCED_SUN_AVAILABLE = False

class ModelTab(QWidget):
    """Model Tab with environment integration and debug capabilities"""
    
    building_generated = pyqtSignal(object)
    model_updated = pyqtSignal(object)
    view_changed = pyqtSignal(str)
    roof_generated = pyqtSignal(object)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        
        self.main_window = main_window
        
        self.current_building = None
        self.current_roof = None
        self.environment_tab = None  # Initialize environment_tab reference
        self.plotter = None
        self.vtk_widget = None
        
        self.ground_plane_actor = None
        
        self.building_meshes = []
        self.roof_meshes = []
        self.panel_meshes = []
        
        self.current_time = 12.0
        self.current_day = 172
        self.latitude = 40.7128
        self.longitude = -74.0060
        self.weather_factor = 1.0
        self.shadows_enabled = True
        self.sunshafts_enabled = False
        self.quality_level = 'medium'
        
        self.animation_active = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_solar_position)
        
        self.solar_calculations = None
        self.enhanced_sun_system = None
        
        self.sun_position = None
        
        self.camera_interacting = False
        
        self.setup_ui()
        self._initialize_solar_systems()
        self._calculate_initial_sun_position()
        self._create_single_ground_plane()
        self._force_create_initial_sun()

    def setup_ui(self):
        """Setup the UI with only the 3D plotter"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        view_container = QFrame()
        view_container.setFrameStyle(QFrame.StyledPanel)
        
        view_layout = QVBoxLayout(view_container)
        view_layout.setContentsMargins(5, 5, 5, 5)
        view_layout.setSpacing(5)
        
        if PYVISTA_AVAILABLE:
            self.setup_pyvista_view(view_layout)
        else:
            self.setup_fallback_3d_view(view_layout)
        
        main_layout.addWidget(view_container)

    def setup_pyvista_view(self, layout):
        """Setup PyVista 3D view"""
        try:
            self.plotter = QtInteractor(layout.parent())
            self.plotter.setMinimumHeight(500)
            
            self.plotter.model_tab = self
            
            if hasattr(self.plotter, 'enable_shadows'):
                self.plotter.enable_shadows()
            
            if hasattr(self.plotter, 'enable_anti_aliasing'):
                self.plotter.enable_anti_aliasing()
            
            if hasattr(self.plotter, 'enable_depth_peeling'):
                self.plotter.enable_depth_peeling()
            
            if hasattr(self.plotter, 'iren'):
                try:
                    self.plotter.iren.add_observer('StartInteractionEvent', self._on_camera_start)
                    self.plotter.iren.add_observer('EndInteractionEvent', self._on_camera_end)
                except Exception as e:
                    pass
            
            self.plotter.set_background('#87CEEB', top='#E6F3FF')
            
            if hasattr(self.plotter, 'show_axes'):
                self.plotter.show_axes()
            if hasattr(self.plotter, 'show_grid'):
                self.plotter.show_grid()
            
            self.vtk_widget = self.plotter.interactor
            layout.addWidget(self.vtk_widget)
            
        except Exception as e:
            self.plotter = None
            self.vtk_widget = None
            self.setup_fallback_3d_view(layout)
    
    def _on_camera_start(self, obj, event):
        """Called when camera interaction starts"""
        self.camera_interacting = True
        if self.enhanced_sun_system:
            self.enhanced_sun_system.set_interactive_mode(True)
    
    def _on_camera_end(self, obj, event):
        """Called when camera interaction ends"""
        self.camera_interacting = False
        if self.enhanced_sun_system:
            self.enhanced_sun_system.set_interactive_mode(False)

    def setup_fallback_3d_view(self, layout):
        """Setup fallback 3D view placeholder"""
        placeholder = QLabel("3D View Not Available")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(500)
        layout.addWidget(placeholder)
        self.plotter = None
        self.vtk_widget = None

    def _initialize_solar_systems(self):
        """Initialize solar system modules"""
        if not self.plotter:
            return
        
        if SOLAR_CALCULATIONS_AVAILABLE:
            self.solar_calculations = SolarCalculations
        
        if ENHANCED_SUN_AVAILABLE:
            try:
                self.enhanced_sun_system = EnhancedRealisticSunSystem(self.plotter)
                
                import sys
                sys.modules[__name__]._global_sun_system = self.enhanced_sun_system
                
                if hasattr(self.enhanced_sun_system, 'set_quality_level'):
                    self.enhanced_sun_system.set_quality_level(self.quality_level)
                
                if hasattr(self.enhanced_sun_system, 'enable_shadows'):
                    self.enhanced_sun_system.enable_shadows(True)
                
                if hasattr(self.enhanced_sun_system, 'min_shadow_elevation'):
                    self.enhanced_sun_system.min_shadow_elevation = 25.0
                
                self.enhanced_sun_system.set_building_center([0, 0, 1.5])
                self.enhanced_sun_system.set_building_dimensions(8.0, 10.0, 3.0, 2.0)
                
            except Exception as e:
                self.enhanced_sun_system = None

    def _calculate_initial_sun_position(self):
        """Calculate initial sun position"""
        if SOLAR_CALCULATIONS_AVAILABLE:
            try:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude
                )
            except Exception as e:
                self.sun_position = [30, 30, 30]
        else:
            self.sun_position = [30, 30, 30]

    def _create_single_ground_plane(self):
        """Create a SINGLE ground plane for the entire scene"""
        if not self.plotter:
            return
        
        try:
            if self.ground_plane_actor:
                try:
                    self.plotter.remove_actor('main_ground_plane')
                except:
                    pass
                self.ground_plane_actor = None
            
            ground_size = 50
            ground = pv.Plane(
                center=(0, 0, 0),
                direction=(0, 0, 1),
                i_size=ground_size,
                j_size=ground_size,
                i_resolution=30,
                j_resolution=30
            )
            
            self.ground_plane_actor = self.plotter.add_mesh(
                ground,
                color='#7CFC00',
                opacity=1.0,
                name='main_ground_plane',
                lighting=True,
                ambient=0.4,
                diffuse=0.7,
                specular=0.05,
                smooth_shading=True,
                pickable=False
            )
            
        except Exception as e:
            pass

    def _force_create_initial_sun(self):
        """Force create initial sun"""
        if not self.enhanced_sun_system:
            return
        
        if not self.sun_position:
            self.sun_position = [30, 30, 30]
        
        try:
            solar_settings = {
                'current_hour': self.current_time,
                'weather_factor': self.weather_factor,
                'sun_elevation': 45.0,
                'sun_azimuth': 180.0
            }
            
            self.enhanced_sun_system.create_photorealistic_sun(
                self.sun_position, 
                solar_settings
            )
            
            if self.plotter and hasattr(self.plotter, 'render'):
                self.plotter.render()
            
        except Exception as e:
            pass

    def _update_all_solar_systems(self):
        """Update all solar systems"""
        if self.camera_interacting:
            return
        
        if SOLAR_CALCULATIONS_AVAILABLE:
            try:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude,
                    3.0
                )
                
                self._update_background_for_time()
                
            except Exception as e:
                self.sun_position = [30, 30, 30]
        
        if self.enhanced_sun_system and self.sun_position:
            try:
                sun_elevation = 45.0
                if self.sun_position[2] > 0:
                    h_dist = np.sqrt(self.sun_position[0]**2 + self.sun_position[1]**2)
                    if h_dist > 0:
                        sun_elevation = np.degrees(np.arctan2(self.sun_position[2], h_dist))
                
                solar_settings = {
                    'current_hour': self.current_time,
                    'weather_factor': self.weather_factor,
                    'sun_elevation': sun_elevation,
                    'sun_azimuth': np.degrees(np.arctan2(self.sun_position[1], self.sun_position[0])),
                    'shadows_enabled': self.shadows_enabled
                }
                
                self.enhanced_sun_system.update_sun_position(
                    self.sun_position, 
                    solar_settings
                )
                
            except Exception as e:
                pass
    
    def _update_background_for_time(self):
        """Update background color based on time"""
        if not self.plotter:
            return
            
        try:
            if self.sun_position and self.sun_position[2] > 0:
                if 10 <= self.current_time <= 14:
                    bg_color = '#87CEEB'
                    top_color = '#E6F3FF'
                elif self.current_time < 6 or self.current_time > 20:
                    bg_color = '#FF6B35'
                    top_color = '#4A5A8A'
                elif self.current_time < 8 or self.current_time > 18:
                    bg_color = '#FFA500'
                    top_color = '#87CEEB'
                else:
                    bg_color = '#87CEEB'
                    top_color = '#B0E0E6'
            else:
                bg_color = '#0A0A1A'
                top_color = '#1A1A3A'
            
            self.plotter.set_background(bg_color, top=top_color)
            
        except Exception as e:
            pass

    def update_solar_time(self, decimal_time):
        """Update solar time"""
        if self.camera_interacting:
            return
        
        self.current_time = decimal_time
        self._update_all_solar_systems()

    def update_solar_day(self, day_of_year):
        """Update solar day"""
        if self.camera_interacting:
            return
        
        self.current_day = day_of_year
        self._update_all_solar_systems()

    def set_location(self, latitude, longitude):
        """Set location"""
        self.latitude = latitude
        self.longitude = longitude
        self._update_all_solar_systems()

    def set_weather_factor(self, factor):
        """Set weather factor"""
        self.weather_factor = factor
        self._update_all_solar_systems()

    def toggle_solar_effects(self, shadows=None, sunshafts=None):
        """Toggle solar effects"""
        if shadows is not None:
            self.shadows_enabled = shadows
            if self.enhanced_sun_system:
                self.enhanced_sun_system.enable_shadows(shadows)
        
        self._update_all_solar_systems()

    def set_quality_level(self, quality):
        """Set quality level"""
        self.quality_level = quality
        
        if self.enhanced_sun_system:
            if hasattr(self.enhanced_sun_system, 'set_quality_level'):
                self.enhanced_sun_system.set_quality_level(quality)

    def handle_animation_toggle(self, enabled):
        """Handle animation toggle"""
        self.animation_active = enabled
        
        if enabled:
            self.animation_timer.start(500)
        else:
            self.animation_timer.stop()

    def _animate_solar_position(self):
        """Animate solar position"""
        if not self.animation_active:
            return
        
        self.current_time += 0.2
        
        if self.current_time >= 24:
            self.current_time = 0
        
        self._update_all_solar_systems()

    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05):
        """Create building in 3D view"""
        try:
            if not points or len(points) < 3:
                return False
            
            if self.plotter:
                self._clear_building_actors()
                self.plotter.set_background('#87CEEB', top='#E6F3FF')
            
            building_data = {
                'points': points,
                'height': height,
                'roof_type': roof_type,
                'roof_pitch': roof_pitch,
                'scale': scale,
                'created_at': datetime.now()
            }
            
            self.current_building = building_data
            
            if self.enhanced_sun_system:
                xs = []
                ys = []
                for point in points:
                    if hasattr(point, 'x') and hasattr(point, 'y'):
                        x, y = point.x() * scale, point.y() * scale
                    else:
                        x, y = point[0] * scale, point[1] * scale
                    xs.append(x)
                    ys.append(y)
                
                if xs and ys:
                    center_x = (min(xs) + max(xs)) / 2
                    center_y = (min(ys) + max(ys)) / 2
                    width = max(xs) - min(xs)
                    length = max(ys) - min(ys)
                    
                    self.enhanced_sun_system.set_building_center([center_x, center_y, height/2])
                    self.enhanced_sun_system.set_building_dimensions(width, length, height, 2.0)
            
            self._create_roof_object(roof_type, points, height, scale)
            self._update_all_solar_systems()
            self.building_generated.emit(building_data)
            
            return True
            
        except Exception as e:
            return False
    
    def _clear_building_actors(self):
        """Clear building actors"""
        try:
            self.building_meshes.clear()
            self.roof_meshes.clear()
            self.panel_meshes.clear()
            
            actors_to_remove = ['test_building', 'wall', 'roof', 'foundation', 'building', 'panel']
            
            for name in actors_to_remove:
                try:
                    self.plotter.remove_actor(name)
                except:
                    pass
            
        except Exception as e:
            pass

    def _create_roof_object(self, roof_type, points, height, scale):
        """Create roof object with environment support"""
        try:
            base_points = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    x, y = point.x() * scale, point.y() * scale
                else:
                    x, y = point[0] * scale, point[1] * scale
                base_points.append([x, y, 0])
            
            # Cleanup previous roof
            if hasattr(self, 'current_roof') and self.current_roof:
                try:
                    if hasattr(self.current_roof, 'cleanup'):
                        self.current_roof.cleanup()
                    del self.current_roof
                except:
                    pass
            
            # Create new roof based on type
            if roof_type == 'pyramid':
                from roofs.concrete.pyramid_roof import PyramidRoof
                self.current_roof = PyramidRoof(
                    plotter=self.plotter,
                    base_points=base_points[:4],
                    apex_height=height,
                    building_height=0
                )
            elif roof_type == 'gable':
                from roofs.concrete.gable_roof import GableRoof
                if len(base_points) >= 4:
                    length = abs(base_points[1][1] - base_points[0][1])
                    width = abs(base_points[2][0] - base_points[1][0])
                    dimensions = (length, width, height)
                else:
                    dimensions = (10.0, 8.0, height)
                
                self.current_roof = GableRoof(
                    plotter=self.plotter,
                    dimensions=dimensions,
                    theme="light",
                    rotation_angle=0
                )
            elif roof_type == 'flat':
                from roofs.concrete.flat_roof import FlatRoof
                roof_points = []
                for point in points:
                    if hasattr(point, 'x') and hasattr(point, 'y'):
                        x, y = point.x() * scale, point.y() * scale
                    else:
                        x, y = point[0] * scale, point[1] * scale
                    roof_points.append([x, y, height])
                
                self.current_roof = FlatRoof(
                    plotter=self.plotter,
                    base_points=roof_points,
                    building_height=height
                )
            else:
                self.current_roof = None
            
            # IMPORTANT: Reconnect environment tab to new roof
            if self.current_roof:
                print(f"✅ Created {roof_type} roof")
                
                # Initialize the roof if it has the method
                if hasattr(self.current_roof, 'initialize_roof'):
                    if hasattr(self.current_roof, 'dimensions'):
                        self.current_roof.initialize_roof(self.current_roof.dimensions)
                    else:
                        # Try to create dimensions from points
                        if len(base_points) >= 4:
                            length = abs(base_points[1][1] - base_points[0][1])
                            width = abs(base_points[2][0] - base_points[1][0])
                            dimensions = (length, width, height)
                            self.current_roof.initialize_roof(dimensions)
                
                # Reconnect environment tab if it exists
                if hasattr(self, 'environment_tab') and self.environment_tab:
                    self._reconnect_environment_tab()
            
            self.roof_generated.emit(self.current_roof)
                
        except Exception as e:
            print(f"❌ Error creating roof: {e}")
            import traceback
            traceback.print_exc()
            self.current_roof = None

    def connect_environment_tab(self, environment_tab):
        """Connect environment tab to current roof - FIXED FOR PyQt5"""
        try:
            if not environment_tab:
                print("⚠️ No environment tab provided")
                return False
            
            # Store reference
            self.environment_tab = environment_tab
            print("✅ Stored environment_tab reference")
            
            # Connect the signal
            if hasattr(environment_tab, 'environment_action_requested'):
                # Disconnect any previous connections
                try:
                    environment_tab.environment_action_requested.disconnect()
                    print("✅ Disconnected previous connections")
                except:
                    print("ℹ️ No previous connections to disconnect")
                
                # Connect to our handler
                environment_tab.environment_action_requested.connect(
                    self._handle_environment_tab_action
                )
                print("✅ Connected signal to _handle_environment_tab_action")
                
                # REMOVED THE .receivers() CHECK - IT DOESN'T EXIST IN PyQt5
                # Just return True since we connected successfully
                print(f"✅ Environment tab connected successfully")
                
                return True
            else:
                print("❌ EnvironmentTab missing environment_action_requested signal!")
                return False
            
        except Exception as e:
            print(f"❌ Error connecting environment tab: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _handle_environment_tab_action(self, action_type, parameters):
        """Handle actions from EnvironmentTab - routes to current roof"""
        try:
            print(f"📡 ModelTab received environment action: {action_type}")
            print(f"   Parameters: {parameters}")
            
            # Special handling for test connection
            if action_type == 'test_connection':
                print("✅ Test connection received successfully!")
                return True
            
            if not self.current_roof:
                print("⚠️ No current roof to handle environment action")
                # If it's just toggle points and no roof, ignore
                if action_type == 'toggle_attachment_points':
                    print("   Ignoring toggle points - no roof yet")
                return False
            
            # Route the action to the current roof's handle_environment_action
            if hasattr(self.current_roof, 'handle_environment_action'):
                print(f"   Routing to {self.current_roof.__class__.__name__}.handle_environment_action")
                self.current_roof.handle_environment_action(action_type, parameters)
                
                # Force render after environment action
                if self.plotter and hasattr(self.plotter, 'render'):
                    self.plotter.render()
                
                return True
            else:
                print(f"⚠️ Current roof doesn't support environment actions")
                return False
                
        except Exception as e:
            print(f"❌ Error handling environment tab action: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _reconnect_environment_tab(self):
        """Reconnect environment tab to current roof"""
        try:
            if not hasattr(self, 'environment_tab') or not self.environment_tab:
                print("⚠️ No environment tab to reconnect")
                return
            
            if not self.current_roof:
                print("⚠️ No current roof to connect to")
                return
            
            print(f"🔗 Reconnecting environment tab to {self.current_roof.__class__.__name__}")
            
            # The connection is already through our handler, just verify roof can handle it
            if hasattr(self.current_roof, 'handle_environment_action'):
                print("   ✅ Roof has handle_environment_action method")
                
                # Test if environment manager exists
                if hasattr(self.current_roof, 'environment_manager'):
                    print("   ✅ Roof has environment_manager")
                else:
                    print("   ⚠️ Roof missing environment_manager")
            else:
                print("   ⚠️ Roof missing handle_environment_action method")
            
        except Exception as e:
            print(f"⚠️ Error reconnecting environment tab: {e}")

    # ==================== DEBUG AND TEST METHODS ====================

    def test_environment_system(self):
        """Comprehensive test of the environment system"""
        print("\n" + "="*60)
        print("ENVIRONMENT SYSTEM DIAGNOSTIC TEST")
        print("="*60)
        
        # Check plotter
        if self.plotter:
            print(f"✅ Plotter exists: {type(self.plotter)}")
        else:
            print("❌ No plotter!")
            return
        
        # Check current roof
        if hasattr(self, 'current_roof') and self.current_roof:
            roof = self.current_roof
            print(f"✅ Current roof: {roof.__class__.__name__}")
            
            # Check environment manager
            if hasattr(roof, 'environment_manager'):
                env_mgr = roof.environment_manager
                print(f"✅ Environment manager exists")
                
                # Check attachment points
                if hasattr(env_mgr, 'environment_attachment_points'):
                    points = env_mgr.environment_attachment_points
                    print(f"✅ Attachment points: {len(points)} points")
                    
                    # Show first few points
                    for i, point in enumerate(points[:3]):
                        print(f"   Point {i}: {point['position']}, occupied: {point['occupied']}")
                else:
                    print("❌ No attachment points list")
                
                # Check if ground exists
                if hasattr(env_mgr, 'ground_mesh') and env_mgr.ground_mesh:
                    print(f"✅ Ground mesh exists")
                else:
                    print("❌ No ground mesh")
                
                # Try to show points manually
                print("\n🔧 Attempting to show attachment points manually...")
                try:
                    env_mgr.show_environment_attachment_points()
                    print("✅ Called show_environment_attachment_points()")
                    
                    # Force render
                    if hasattr(self.plotter, 'render'):
                        self.plotter.render()
                        print("✅ Called render()")
                        
                except Exception as e:
                    print(f"❌ Error showing points: {e}")
                    import traceback
                    traceback.print_exc()
                    
            else:
                print("❌ Roof has no environment_manager")
        else:
            print("⚠️ No current roof - create a building first")
            
        # Check environment tab connection
        if hasattr(self, 'environment_tab') and self.environment_tab:
            print("✅ Environment tab connected")
        else:
            print("❌ Environment tab NOT connected")
        
        print("="*60 + "\n")
        return True

    def test_add_visible_spheres(self):
        """Test adding highly visible spheres to verify rendering works"""
        if not self.plotter:
            print("❌ No plotter")
            return False
        
        print("\n🔴 Adding test spheres...")
        
        try:
            # Add spheres at different positions with bright colors
            test_positions = [
                ([5, 0, 2], 'red', 0.5),
                ([0, 5, 2], 'blue', 0.5),
                ([-5, 0, 2], 'green', 0.5),
                ([0, -5, 2], 'yellow', 0.5),
                ([0, 0, 5], 'magenta', 0.8)  # One high up
            ]
            
            for i, (pos, color, radius) in enumerate(test_positions):
                sphere = pv.Sphere(center=pos, radius=radius)
                actor = self.plotter.add_mesh(
                    sphere,
                    color=color,
                    name=f'test_sphere_{color}',
                    opacity=1.0,
                    smooth_shading=True
                )
                print(f"  ✅ Added {color} sphere at {pos}")
            
            # Force render
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
            # Reset camera to see all
            if hasattr(self.plotter, 'reset_camera'):
                self.plotter.reset_camera()
                
            print("✅ Test spheres added - you should see 5 colored spheres")
            return True
            
        except Exception as e:
            print(f"❌ Error adding test spheres: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_manual_attachment_points(self):
        """Manually create and show attachment points"""
        if not self.current_roof:
            print("❌ No roof - create building first")
            return False
        
        if not self.plotter:
            print("❌ No plotter")
            return False
        
        print("\n🔵 Creating manual attachment points...")
        
        try:
            # Create points in a circle around origin at ground level
            radius = 10
            num_points = 8
            for i in range(num_points):
                angle = (2 * np.pi * i) / num_points
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                z = 1.0  # 1 meter above ground for visibility
                
                # Create a sphere at each point
                sphere = pv.Sphere(center=[x, y, z], radius=0.3)
                self.plotter.add_mesh(
                    sphere,
                    color='black',
                    name=f'manual_attachment_{i}',
                    opacity=1.0
                )
                print(f"  Added black sphere at ({x:.1f}, {y:.1f}, {z})")
            
            # Add a larger central sphere for reference
            center_sphere = pv.Sphere(center=[0, 0, 1], radius=0.5)
            self.plotter.add_mesh(
                center_sphere,
                color='red',
                name='center_reference',
                opacity=1.0
            )
            print("  Added red reference sphere at center")
            
            # Force render
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
            print("✅ Manual attachment points created")
            return True
            
        except Exception as e:
            print(f"❌ Error creating manual points: {e}")
            import traceback
            traceback.print_exc()
            return False

    def force_show_attachment_points(self):
        """Force show attachment points with maximum visibility"""
        if not self.current_roof:
            print("❌ No roof exists")
            return False
        
        if not hasattr(self.current_roof, 'environment_manager'):
            print("❌ No environment manager")
            return False
        
        env_mgr = self.current_roof.environment_manager
        
        print("\n⚫ Forcing attachment points display...")
        
        try:
            # First ensure points exist
            if not env_mgr.environment_attachment_points:
                print("❌ No attachment points exist - creating them...")
                env_mgr._create_environment_attachment_points()
            
            points = env_mgr.environment_attachment_points
            print(f"📍 Found {len(points)} attachment points")
            
            # Clear any existing actors
            for i in range(50):
                try:
                    self.plotter.remove_actor(f'forced_attachment_{i}')
                except:
                    pass
            
            # Add each point as a visible sphere
            for i, point_data in enumerate(points[:20]):  # Limit to first 20
                pos = point_data['position']
                # Raise the Z coordinate for visibility
                visible_pos = [pos[0], pos[1], pos[2] + 1.0]
                
                sphere = pv.Sphere(center=visible_pos, radius=0.4)
                color = 'red' if point_data['occupied'] else 'black'
                
                self.plotter.add_mesh(
                    sphere,
                    color=color,
                    name=f'forced_attachment_{i}',
                    opacity=1.0,
                    smooth_shading=True
                )
                
                if i < 3:  # Print first 3
                    print(f"  Point {i}: {visible_pos} - {color}")
            
            # Add ground reference plane
            ground_plane = pv.Plane(
                center=(0, 0, 0),
                direction=(0, 0, 1),
                i_size=30,
                j_size=30,
                i_resolution=1,
                j_resolution=1
            )
            self.plotter.add_mesh(
                ground_plane,
                color='gray',
                opacity=0.3,
                name='reference_ground'
            )
            
            # Force render and reset camera
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
            if hasattr(self.plotter, 'reset_camera'):
                self.plotter.reset_camera()
            
            print("✅ Forced attachment points display complete")
            print("   Black spheres = available, Red spheres = occupied")
            return True
            
        except Exception as e:
            print(f"❌ Error forcing attachment points: {e}")
            import traceback
            traceback.print_exc()
            return False

    def list_scene_actors(self):
        """List all actors currently in the scene"""
        if not self.plotter:
            print("❌ No plotter")
            return
        
        print("\n📋 Scene Contents:")
        
        try:
            if hasattr(self.plotter, 'renderer'):
                renderer = self.plotter.renderer
                
                # Get actors collection
                actors = renderer.GetActors()
                actors.InitTraversal()
                
                num_actors = actors.GetNumberOfItems()
                print(f"Total actors in scene: {num_actors}")
                
                # List each actor
                for i in range(min(num_actors, 20)):  # Limit to first 20
                    actor = actors.GetNextActor()
                    if actor:
                        # Try to get bounds
                        bounds = actor.GetBounds()
                        if bounds:
                            x_range = f"{bounds[0]:.1f} to {bounds[1]:.1f}"
                            y_range = f"{bounds[2]:.1f} to {bounds[3]:.1f}"
                            z_range = f"{bounds[4]:.1f} to {bounds[5]:.1f}"
                            print(f"  Actor {i}: X[{x_range}], Y[{y_range}], Z[{z_range}]")
                        else:
                            print(f"  Actor {i}: {actor}")
                
                if num_actors > 20:
                    print(f"  ... and {num_actors - 20} more actors")
                    
            else:
                print("❌ No renderer available")
                
        except Exception as e:
            print(f"❌ Error listing actors: {e}")
            import traceback
            traceback.print_exc()

    def debug_camera_position(self):
        """Show current camera position and settings"""
        if not self.plotter:
            print("❌ No plotter")
            return
        
        print("\n📷 Camera Information:")
        
        try:
            if hasattr(self.plotter, 'camera_position'):
                cam_pos = self.plotter.camera_position
                print(f"Camera position: {cam_pos}")
            
            if hasattr(self.plotter, 'camera'):
                camera = self.plotter.camera
                print(f"Camera focal point: {camera.focal_point}")
                print(f"Camera distance: {camera.distance}")
                print(f"Camera clipping range: {camera.clipping_range}")
                
        except Exception as e:
            print(f"❌ Error getting camera info: {e}")

    # ==================== ENVIRONMENT AND PANEL METHODS ====================

    def add_obstacle(self, obstacle_type, dimensions):
        """Add obstacle to current roof"""
        try:
            if not self.current_roof:
                return False
            
            if hasattr(self.current_roof, 'add_obstacle'):
                return self.current_roof.add_obstacle(obstacle_type, dimensions)
            return False
        except Exception as e:
            return False

    def add_solar_panels(self, config):
        """Add solar panels to current roof"""
        try:
            if not self.current_roof:
                return False
            
            if hasattr(self.current_roof, 'update_panel_config'):
                return self.current_roof.update_panel_config(config)
            return False
        except Exception as e:
            return False

    def add_environment_object(self, object_type, parameters=None):
        """Add environment object to current roof"""
        try:
            if not self.current_roof:
                return False
            
            if object_type == 'tree':
                tree_type = parameters.get('tree_type', 'deciduous') if parameters else 'deciduous'
                if tree_type == 'pine':
                    self.current_roof.tree_type_index = 1
                elif tree_type == 'oak':
                    self.current_roof.tree_type_index = 2
                else:
                    self.current_roof.tree_type_index = 0
                
                return self.current_roof.add_environment_obstacle_at_point('tree')
                
            elif object_type == 'pole':
                return self.current_roof.add_environment_obstacle_at_point('pole')
                
            return False
        except Exception as e:
            return False

    def clear_environment_objects(self):
        """Clear all environment objects"""
        try:
            if self.current_roof and hasattr(self.current_roof, 'clear_environment_obstacles'):
                self.current_roof.clear_environment_obstacles()
                return True
            return False
        except Exception as e:
            return False

    def get_environment_statistics(self):
        """Get current environment object counts"""
        if not self.current_roof:
            return {}
            
        try:
            stats = {
                'deciduous_trees': 0,
                'pine_trees': 0,
                'oak_trees': 0,
                'poles': 0
            }
            
            if hasattr(self.current_roof, 'environment_obstacles'):
                for obstacle in self.current_roof.environment_obstacles:
                    obs_type = obstacle.get('type', '')
                    if obs_type == 'tree_deciduous':
                        stats['deciduous_trees'] += 1
                    elif obs_type == 'tree_pine':
                        stats['pine_trees'] += 1
                    elif obs_type == 'tree_oak':
                        stats['oak_trees'] += 1
                    elif obs_type == 'pole':
                        stats['poles'] += 1
            
            return stats
            
        except Exception as e:
            return {}

    def connect_modifications_tab(self, modifications_tab):
        """Connect modifications tab to this model tab"""
        try:
            if hasattr(modifications_tab, 'connect_environment_to_model_tab'):
                modifications_tab.connect_environment_to_model_tab(self)
            
            if hasattr(modifications_tab, 'solar_panel_config_changed'):
                modifications_tab.solar_panel_config_changed.connect(
                    lambda config: self.add_solar_panels(config)
                )
            
            if hasattr(modifications_tab, 'obstacle_placement_requested'):
                modifications_tab.obstacle_placement_requested.connect(
                    lambda obs_type, dims: self.add_obstacle(obs_type, dims)
                )
            
            if hasattr(modifications_tab, 'environment_action_requested'):
                modifications_tab.environment_action_requested.connect(
                    self._handle_environment_action
                )
                
        except Exception as e:
            pass

    def _handle_environment_action(self, action_type, parameters):
        """Handle environment actions from modifications tab"""
        try:
            if not self.current_roof:
                return False
            
            # This is for the old-style direct actions from modifications tab
            # The new environment tab actions go through _handle_environment_tab_action
            
            if action_type == 'add_tree':
                tree_type = parameters.get('tree_type', 'deciduous')
                return self.add_environment_object('tree', {'tree_type': tree_type})
                
            elif action_type == 'add_multiple_trees':
                count = parameters.get('count', 5)
                success_count = 0
                for i in range(count):
                    tree_types = ['deciduous', 'pine', 'oak']
                    tree_type = tree_types[i % len(tree_types)]
                    if self.add_environment_object('tree', {'tree_type': tree_type}):
                        success_count += 1
                return success_count > 0
                
            elif action_type == 'add_pole':
                return self.add_environment_object('pole')
                
            elif action_type == 'toggle_attachment_points':
                if self.current_roof:
                    if hasattr(self.current_roof, 'environment_manager'):
                        visible = parameters.get('visible', False)
                        if visible:
                            self.current_roof.environment_manager.show_environment_attachment_points()
                        else:
                            self.current_roof.environment_manager.hide_environment_attachment_points()
                return True
                
            elif action_type == 'clear_all_environment':
                return self.clear_environment_objects()
                
            elif action_type == 'auto_populate_scene':
                success_count = 0
                
                for _ in range(3):
                    if self.add_environment_object('tree', {'tree_type': 'deciduous'}):
                        success_count += 1
                for _ in range(2):
                    if self.add_environment_object('tree', {'tree_type': 'pine'}):
                        success_count += 1
                if self.add_environment_object('tree', {'tree_type': 'oak'}):
                    success_count += 1
                
                for _ in range(2):
                    self.add_environment_object('pole')
                
                return True
            
            return False
            
        except Exception as e:
            return False

    # ==================== UTILITY METHODS ====================

    def get_solar_performance(self):
        """Get solar performance metrics"""
        try:
            base_power = 5.0
            base_energy = 40.0
            base_efficiency = 75.0
            
            weather_adj = self.weather_factor
            time_adj = 1.0 if 6 <= self.current_time <= 18 else 0.1
            
            if self.sun_position and len(self.sun_position) > 2 and self.sun_position[2] > 0:
                elev_adj = min(1.0, self.sun_position[2] / 20.0)
            else:
                elev_adj = 0.0
            
            power = base_power * weather_adj * time_adj * elev_adj
            energy = base_energy * weather_adj * elev_adj
            efficiency = base_efficiency * weather_adj * elev_adj
            
            return power, energy, efficiency
            
        except:
            return 0.0, 0.0, 0.0

    def refresh_view(self):
        """Refresh view"""
        if self.plotter:
            if hasattr(self.plotter, 'update'):
                self.plotter.update()
            if hasattr(self.plotter, 'reset_camera'):
                self.plotter.reset_camera()
            self._update_all_solar_systems()

    def reset_plotter(self, camera_position=None):
        """Reset plotter"""
        try:
            if PYVISTA_AVAILABLE and self.plotter:
                self._clear_building_actors()
                
                if self.enhanced_sun_system:
                    self.enhanced_sun_system.destroy()
                    self.enhanced_sun_system = EnhancedRealisticSunSystem(self.plotter)
                    if hasattr(self.enhanced_sun_system, 'set_quality_level'):
                        self.enhanced_sun_system.set_quality_level(self.quality_level)
                    if hasattr(self.enhanced_sun_system, 'enable_shadows'):
                        self.enhanced_sun_system.enable_shadows(True)
                
                self.plotter.set_background('#87CEEB', top='#E6F3FF')
                
                if camera_position:
                    self.plotter.camera_position = camera_position
                else:
                    if hasattr(self.plotter, 'reset_camera'):
                        self.plotter.reset_camera()
                
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                
                return True
            return False
        except:
            return False

    def cleanup(self):
        """Cleanup resources"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        
        if self.enhanced_sun_system:
            self.enhanced_sun_system.destroy()
            self.enhanced_sun_system = None
        
        if hasattr(self, 'current_roof') and self.current_roof:
            if hasattr(self.current_roof, 'cleanup'):
                self.current_roof.cleanup()
            del self.current_roof
            self.current_roof = None
        
        self.building_meshes.clear()
        self.roof_meshes.clear()
        self.panel_meshes.clear()
        self.current_building = None
        
        import sys
        if hasattr(sys.modules[__name__], '_global_sun_system'):
            delattr(sys.modules[__name__], '_global_sun_system')
        
        if PYVISTA_AVAILABLE and self.plotter:
            if hasattr(self.plotter, 'close'):
                self.plotter.close()

    def has_building(self):
        """Check if building exists"""
        return self.current_building is not None

    def get_plotter(self):
        """Get plotter"""
        return self.plotter

    def get_valid_plotter(self):
        """Get valid plotter"""
        try:
            if self.plotter and hasattr(self.plotter, 'add_mesh'):
                return self.plotter
            return None
        except:
            return None

    def debug_environment_connection(self):
        """Debug the entire environment connection chain"""
        print("\n" + "="*60)
        print("🔍 ENVIRONMENT CONNECTION DEBUG")
        print("="*60)
        
        # 1. Check if environment tab exists
        if hasattr(self, 'environment_tab') and self.environment_tab:
            print("✅ Step 1: environment_tab exists")
        else:
            print("❌ Step 1: NO environment_tab reference!")
            return
        
        # 2. Check if current roof exists
        if hasattr(self, 'current_roof') and self.current_roof:
            print(f"✅ Step 2: current_roof exists ({self.current_roof.__class__.__name__})")
        else:
            print("❌ Step 2: NO current_roof!")
            return
        
        # 3. Check if roof has handle_environment_action
        if hasattr(self.current_roof, 'handle_environment_action'):
            print("✅ Step 3: Roof has handle_environment_action method")
        else:
            print("❌ Step 3: Roof missing handle_environment_action!")
            return
        
        # 4. Check if roof has environment_manager
        if hasattr(self.current_roof, 'environment_manager'):
            print("✅ Step 4: Roof has environment_manager")
            env_mgr = self.current_roof.environment_manager
        else:
            print("❌ Step 4: Roof missing environment_manager!")
            return
        
        # 5. Check if environment_manager has handle method
        if hasattr(env_mgr, 'handle_environment_action'):
            print("✅ Step 5: environment_manager has handle_environment_action")
        else:
            print("❌ Step 5: environment_manager missing handle_environment_action!")
            return
        
        # 6. Test direct call to environment manager
        print("\n🧪 Testing direct calls...")
        try:
            # Test showing attachment points directly
            env_mgr.show_environment_attachment_points()
            print("✅ Direct call to show_environment_attachment_points worked")
            
            # Check if plotter exists and can render
            if self.plotter:
                self.plotter.render()
                print("✅ Plotter render called")
            else:
                print("❌ No plotter available!")
                
        except Exception as e:
            print(f"❌ Direct call failed: {e}")
            import traceback
            traceback.print_exc()
        
        # 7. Check signal connection
        print("\n📡 Checking signal connections...")
        if hasattr(self.environment_tab, 'environment_action_requested'):
            signal = self.environment_tab.environment_action_requested
            
            # Check if signal has any connections
            try:
                # This is PyQt5 specific way to check connections
                receivers = signal.receivers(signal)
                print(f"Signal has {receivers} receiver(s)")
                
                if receivers == 0:
                    print("❌ Signal is NOT connected to anything!")
                    print("\n🔧 Attempting to connect signal now...")
                    
                    # Try to connect it
                    signal.connect(self._handle_environment_tab_action)
                    print("✅ Connected signal to _handle_environment_tab_action")
                    
            except Exception as e:
                print(f"⚠️ Could not check signal receivers: {e}")
        
        print("="*60 + "\n")

    # Updated connection method with better debugging:
    def connect_environment_tab(self, environment_tab):
        """Connect environment tab to current roof with debugging"""
        try:
            print("\n🔗 Connecting EnvironmentTab...")
            
            if not environment_tab:
                print("❌ No environment tab provided")
                return False
            
            # Store reference
            self.environment_tab = environment_tab
            print("✅ Stored environment_tab reference")
            
            # Check if signal exists
            if not hasattr(environment_tab, 'environment_action_requested'):
                print("❌ EnvironmentTab missing environment_action_requested signal!")
                return False
            
            # Disconnect any previous connections
            try:
                environment_tab.environment_action_requested.disconnect()
                print("✅ Disconnected previous connections")
            except:
                print("ℹ️ No previous connections to disconnect")
            
            # Connect to our handler
            environment_tab.environment_action_requested.connect(
                self._handle_environment_tab_action
            )
            print("✅ Connected signal to _handle_environment_tab_action")
            
            # Verify connection
            receivers = environment_tab.environment_action_requested.receivers(
                environment_tab.environment_action_requested
            )
            print(f"✅ Signal now has {receivers} receiver(s)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error connecting environment tab: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Updated handler with more debugging:
    def _handle_environment_tab_action(self, action_type, parameters):
        """Handle actions from EnvironmentTab with debugging"""
        try:
            print(f"\n📨 ModelTab._handle_environment_tab_action called!")
            print(f"   Action: {action_type}")
            print(f"   Parameters: {parameters}")
            
            if not self.current_roof:
                print("❌ No current roof to handle action")
                return False
            
            print(f"✅ Have current roof: {self.current_roof.__class__.__name__}")
            
            # Check if roof has handler
            if not hasattr(self.current_roof, 'handle_environment_action'):
                print("❌ Roof doesn't have handle_environment_action method!")
                return False
            
            print("✅ Calling roof.handle_environment_action...")
            
            # Call the roof's handler
            self.current_roof.handle_environment_action(action_type, parameters)
            
            print("✅ Roof handler called successfully")
            
            # Force render
            if self.plotter and hasattr(self.plotter, 'render'):
                self.plotter.render()
                print("✅ Forced render")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in _handle_environment_tab_action: {e}")
            import traceback
            traceback.print_exc()
            return False
        