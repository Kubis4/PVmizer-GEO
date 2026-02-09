#!/usr/bin/env python3
"""
ui/tabs/model_tab.py - Complete version with environment integration
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
    """Model Tab with environment integration"""
    
    building_generated = pyqtSignal(object)
    model_updated = pyqtSignal(object)
    view_changed = pyqtSignal(str)
    roof_generated = pyqtSignal(object)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        
        self.main_window = main_window
        
        self.current_building = None
        self.current_roof = None
        self.environment_tab = None
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

    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05, dimensions=None):
        """Create building in 3D view - FIXED with explicit dimensions"""
        try:
            print(f"🏗️ ModelTab.create_building called")
            print(f"   Points: {points}")
            print(f"   Height: {height}m")
            print(f"   Roof type: {roof_type}")
            print(f"   Scale: {scale}")
            print(f"   Explicit dimensions: {dimensions}")
            
            if not points or len(points) < 3:
                print(f"❌ Invalid points")
                return False
            
            # Clear previous building
            if self.plotter:
                self._clear_building_actors()
                self.plotter.set_background('#87CEEB', top='#E6F3FF')
            
            # Store building data
            building_data = {
                'points': points,
                'height': height,
                'roof_type': roof_type,
                'roof_pitch': roof_pitch,
                'scale': scale,
                'created_at': datetime.now()
            }
            
            self.current_building = building_data
            
            # Calculate building dimensions
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            building_width = abs(max(xs) - min(xs))
            building_length = abs(max(ys) - min(ys))
            
            print(f"📐 Building dimensions: L={building_length}m, W={building_width}m, H={height}m")
            
            # Update sun system
            if self.enhanced_sun_system:
                center_x = (min(xs) + max(xs)) / 2
                center_y = (min(ys) + max(ys)) / 2
                
                self.enhanced_sun_system.set_building_center([center_x, center_y, height/2])
                self.enhanced_sun_system.set_building_dimensions(building_width, building_length, height, 2.0)
                print(f"✅ Sun system updated")
            
            # Create roof object - pass explicit dimensions
            self._create_roof_object(roof_type, points, height, scale, explicit_dimensions=dimensions)
            
            # Update solar systems
            self._update_all_solar_systems()
            
            # Emit signal
            self.building_generated.emit(building_data)
            
            # Force plotter update
            if self.plotter:
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                if hasattr(self.plotter, 'update'):
                    self.plotter.update()
                print(f"✅ Plotter updated")
            
            print(f"✅ Building creation completed")
            return True
            
        except Exception as e:
            print(f"❌ Error creating building: {e}")
            import traceback
            traceback.print_exc()
            return False

    
    def _clear_building_actors(self):
        """Clear building actors - COMPLETE VERSION with roof cleanup"""
        try:
            print("🧹 Clearing all building actors and roof objects...")
            
            # 1. CRITICAL: Cleanup current roof object first
            if hasattr(self, 'current_roof') and self.current_roof:
                try:
                    print(f"🧹 Cleaning up current roof: {type(self.current_roof).__name__}")
                    
                    # Call roof's cleanup method if it exists
                    if hasattr(self.current_roof, 'cleanup'):
                        self.current_roof.cleanup()
                        print("✅ Roof cleanup() called")
                    
                    # Delete the roof object
                    del self.current_roof
                    self.current_roof = None
                    print("✅ Current roof object deleted")
                    
                except Exception as e:
                    print(f"⚠️ Error cleaning up roof: {e}")
                    self.current_roof = None
            
            # 2. Clear mesh lists
            self.building_meshes.clear()
            self.roof_meshes.clear()
            self.panel_meshes.clear()
            print("✅ Mesh lists cleared")
            
            # 3. Remove all building-related actors from plotter
            if self.plotter:
                actors_to_remove = [
                    # Building components
                    'test_building', 'wall', 'roof', 'foundation', 'building',
                    'building_walls', 'roof_surface', 'parapet_front', 'parapet_back',
                    'parapet_left', 'parapet_right',
                    
                    # Roof components
                    'roof_mesh', 'roof_surface', 'roof_top', 'roof_bottom',
                    'roof_front', 'roof_back', 'roof_left', 'roof_right',
                    
                    # Solar panels
                    'panel', 'solar_panel', 'panels',
                    
                    # Annotations
                    'annotation', 'dimension_line', 'dimension_text',
                    'length_line', 'width_line', 'height_line',
                    'length_text', 'width_text', 'height_text',
                    
                    # Environment objects
                    'attachment_points', 'environment_object',
                    
                    # Other components
                    'ground', 'shadow'
                ]
                
                removed_count = 0
                for name in actors_to_remove:
                    try:
                        self.plotter.remove_actor(name)
                        removed_count += 1
                    except:
                        pass
                
                print(f"✅ Attempted to remove {len(actors_to_remove)} actor types, removed {removed_count}")
                
                # 4. CRITICAL: Remove ALL actors that might be from the roof
                # This catches any actors with dynamic names
                try:
                    all_actors = list(self.plotter.renderer.actors.values())
                    for actor in all_actors:
                        # Skip the ground plane and sun-related actors
                        actor_name = getattr(actor, 'name', '')
                        if actor_name and actor_name not in ['main_ground_plane', 'sun', 'sun_light', 'sky']:
                            try:
                                self.plotter.remove_actor(actor)
                            except:
                                pass
                    print(f"✅ Removed all building-related actors")
                except Exception as e:
                    print(f"⚠️ Error removing all actors: {e}")
                
                # 5. Force plotter update
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                if hasattr(self.plotter, 'update'):
                    self.plotter.update()
                
                print("✅ Plotter updated after cleanup")
            
            # 6. Clear building data
            self.current_building = None
            
            print("✅ All building actors cleared successfully")
            
        except Exception as e:
            print(f"❌ Error in _clear_building_actors: {e}")
            import traceback
            traceback.print_exc()


    def _create_roof_object(self, roof_type, points, height, scale, explicit_dimensions=None):
        """Create roof object with environment support - FIXED dimension calculation"""
        try:
            print(f"🔧 Creating {roof_type} roof object...")
            
            # Use explicit dimensions if provided, otherwise calculate from points
            if explicit_dimensions:
                length = explicit_dimensions.get('length', 10.0)
                width = explicit_dimensions.get('width', 8.0)
                print(f"📐 Using explicit dimensions: L={length}m, W={width}m")
            elif len(points) >= 4:
                # Extract X and Y coordinates
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                
                # Calculate actual dimensions
                length = abs(max(ys) - min(ys))
                width = abs(max(xs) - min(xs))
                
                print(f"📐 Calculated dimensions from points: L={length}m, W={width}m")
            else:
                length = 10.0
                width = 8.0
                print(f"⚠️ Using default dimensions: L={length}m, W={width}m")
            
            # Cleanup previous roof
            if hasattr(self, 'current_roof') and self.current_roof:
                try:
                    if hasattr(self.current_roof, 'cleanup'):
                        self.current_roof.cleanup()
                    del self.current_roof
                    print(f"✅ Previous roof cleaned up")
                except:
                    pass
            
            # Map hip to pyramid if needed
            if roof_type == 'hip':
                print(f"⚠️ Hip roof mapped to pyramid")
                roof_type = 'pyramid'
            
            # Create new roof based on type
            if roof_type == 'pyramid':
                from roofs.concrete.pyramid_roof import PyramidRoof
                dimensions = (length, width, height)
                
                self.current_roof = PyramidRoof(
                    plotter=self.plotter,
                    dimensions=dimensions,
                    theme="light",
                    rotation_angle=0
                )
                print(f"✅ PyramidRoof created with dimensions: {dimensions}")
                
            elif roof_type == 'gable':
                from roofs.concrete.gable_roof import GableRoof
                dimensions = (length, width, height)
                
                self.current_roof = GableRoof(
                    plotter=self.plotter,
                    dimensions=dimensions,
                    theme="light",
                    rotation_angle=0
                )
                print(f"✅ GableRoof created with dimensions: {dimensions}")
                
            elif roof_type == 'flat':
                from roofs.concrete.flat_roof import FlatRoof
                # Flat roof needs (length, width, parapet_height, parapet_width)
                dimensions = (length, width, 0.5, 0.3)
                
                self.current_roof = FlatRoof(
                    plotter=self.plotter,
                    dimensions=dimensions,
                    theme="light"
                )
                print(f"✅ FlatRoof created with dimensions: {dimensions}")
                
            else:
                print(f"❌ Unknown roof type: {roof_type}")
                self.current_roof = None
                return
            
            # Reconnect environment tab if it exists
            if self.current_roof:
                if hasattr(self, 'environment_tab') and self.environment_tab:
                    self._reconnect_environment_tab()
                
                # Emit signal
                self.roof_generated.emit(self.current_roof)
                print(f"✅ Roof object created and signal emitted")
            
        except Exception as e:
            print(f"❌ Error creating roof object: {e}")
            import traceback
            traceback.print_exc()
            self.current_roof = None


    def connect_environment_tab(self, environment_tab):
        """Connect environment tab to current roof"""
        try:
            if not environment_tab:
                return False
            
            # Store reference
            self.environment_tab = environment_tab
            
            # Connect the signal
            if hasattr(environment_tab, 'environment_action_requested'):
                # Disconnect any previous connections
                try:
                    environment_tab.environment_action_requested.disconnect()
                except:
                    pass
                
                # Connect to our handler
                environment_tab.environment_action_requested.connect(
                    self._handle_environment_tab_action
                )
                
                return True
            else:
                return False
            
        except Exception as e:
            return False

    def _handle_environment_tab_action(self, action_type, parameters):
        """Handle actions from EnvironmentTab - routes to current roof"""
        try:
            # Special handling for test connection
            if action_type == 'test_connection':
                return True
            
            if not self.current_roof:
                # If it's just toggle points and no roof, ignore
                if action_type == 'toggle_attachment_points':
                    pass
                return False
            
            # Route the action to the current roof's handle_environment_action
            if hasattr(self.current_roof, 'handle_environment_action'):
                self.current_roof.handle_environment_action(action_type, parameters)
                
                # Force render after environment action
                if self.plotter and hasattr(self.plotter, 'render'):
                    self.plotter.render()
                
                return True
            else:
                return False
                
        except Exception as e:
            return False

    def _reconnect_environment_tab(self):
        """Reconnect environment tab to current roof"""
        try:
            if not hasattr(self, 'environment_tab') or not self.environment_tab:
                return
            
            if not self.current_roof:
                return
            
            # The connection is already through our handler, just verify roof can handle it
            if hasattr(self.current_roof, 'handle_environment_action'):
                # Test if environment manager exists
                if hasattr(self.current_roof, 'environment_manager'):
                    pass
            
        except Exception as e:
            pass

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

    def pause_rendering(self):
        """Pause PyVista rendering when switching away from Model tab"""
        try:
            if self.plotter and self.vtk_widget:
                self.vtk_widget.setParent(None)
        except Exception as e:
            pass

    def resume_rendering(self, layout=None):
        """Resume PyVista rendering when switching back to Model tab"""
        try:
            if self.plotter and self.vtk_widget:
                if layout is None:
                    # Try to re-add back to our own layout
                    layout = self.layout().itemAt(0).widget().layout()
                layout.addWidget(self.vtk_widget)
        except Exception as e:
            pass
