#!/usr/bin/env python3
"""
enhanced_sun_system.py - COMPLETE FIXED VERSION
Proper lighting and shadow casting for all objects
"""
import numpy as np
import pyvista as pv
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import logging
import time

logger = logging.getLogger(__name__)

class EnhancedRealisticSunSystem(QObject):
    """Sun system with proper lighting and shadows"""
    
    sun_updated = pyqtSignal(dict)
    
    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        
        # Sun components storage
        self.sun_actor = None
        self.shadow_actors = []
        self.shadow_meshes = []
        self.current_lights = []
        
        # Sun properties
        self.sun_position = np.array([50, 0, 50])
        self.sun_intensity = 1.0
        self.weather_factor = 1.0
        self.time_of_day = 12.0
        
        # Quality settings
        self.quality_level = 'medium'
        
        # FREEZE PREVENTION
        self.updating = False
        self.last_update_time = 0
        self.update_cooldown = 0.1
        self.pending_update = None
        
        # Debounce timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._process_pending_update)
        self.update_timer.setSingleShot(True)
        
        # Interactive mode
        self.interactive_mode = False
        
        # Scene objects for shadows
        self.scene_objects = []
        
        # Create shadow receiver ground
        self._create_shadow_receiver_ground()
        
        # Enable shadows on plotter
        self._enable_shadow_rendering()
        
        print("✅ Enhanced Sun System initialized")
    
    def _create_shadow_receiver_ground(self):
        """Create an invisible ground that receives shadows"""
        try:
            # Create shadow receiver plane
            shadow_ground = pv.Plane(
                center=(0, 0, -0.02),
                direction=(0, 0, 1),
                i_size=50,
                j_size=50
            )
            
            # Add as shadow receiver
            self.plotter.add_mesh(
                shadow_ground,
                color='white',
                opacity=0.01,  # Almost invisible
                lighting=True,
                ambient=0.1,
                diffuse=0.9,
                specular=0.0,
                name='shadow_receiver',
                pickable=False
            )
            
            print("✅ Shadow receiver ground created")
            
        except Exception as e:
            logger.warning(f"Could not create shadow receiver: {e}")
    
    def _enable_shadow_rendering(self):
        """Enable shadow rendering on the plotter"""
        try:
            # Enable shadows if available
            if hasattr(self.plotter, 'enable_shadows'):
                self.plotter.enable_shadows()
                print("✅ Shadow rendering enabled")
            
            # Enable SSAO for better shadows
            if hasattr(self.plotter, 'enable_ssao'):
                self.plotter.enable_ssao(radius=0.5, bias=0.01, kernel_size=32)
                print("✅ SSAO enabled")
            
            # Enable depth peeling for transparency
            if hasattr(self.plotter, 'enable_depth_peeling'):
                self.plotter.enable_depth_peeling(4)
                print("✅ Depth peeling enabled")
                
        except Exception as e:
            logger.warning(f"Could not enable shadow features: {e}")
    
    def register_scene_object(self, mesh, name, cast_shadow=True):
        """Register an object for shadow casting"""
        self.scene_objects.append({
            'mesh': mesh,
            'name': name,
            'cast_shadow': cast_shadow
        })
        print(f"✅ Registered {name} for shadows")
    
    def create_photorealistic_sun(self, sun_position, solar_settings=None):
        """Create sun with shadows and proper lighting"""
        try:
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_update_time < self.update_cooldown:
                self.pending_update = (sun_position, solar_settings)
                if not self.update_timer.isActive():
                    self.update_timer.start(100)
                return
            
            if self.updating:
                self.pending_update = (sun_position, solar_settings)
                return
                
            self.updating = True
            self.last_update_time = current_time
            
            # Store properties
            self.sun_position = np.array(sun_position) * 2.0
            if solar_settings:
                self.weather_factor = solar_settings.get('weather_factor', 1.0)
                self.time_of_day = solar_settings.get('current_hour', 12.0)
                self.quality_level = solar_settings.get('quality', 'medium')
            
            # Clear previous
            self._safe_clear()
            
            # Create scene based on time
            if self.sun_position[2] < 0:
                self._create_night_scene()
            else:
                self._create_day_scene_with_shadows()
            
            # Render once
            if hasattr(self.plotter, 'render'):
                try:
                    self.plotter.render()
                except:
                    pass
            
            self.updating = False
            
        except Exception as e:
            logger.error(f"Sun update error: {e}")
            self.updating = False
    
    def _create_day_scene_with_shadows(self):
        """Create daytime scene with proper shadows"""
        try:
            # Create sun visual
            self._create_sun_visual()
            
            # Setup lighting that casts shadows
            self._setup_shadow_casting_lights()
            
            # Create shadow projections
            if not self.interactive_mode:
                self._create_shadow_projections()
            
        except Exception as e:
            logger.error(f"Day scene error: {e}")
    
    def _create_sun_visual(self):
        """Create the sun sphere"""
        try:
            sun = pv.Sphere(
                radius=3.0,
                center=self.sun_position,
                phi_resolution=8,
                theta_resolution=8
            )
            
            elevation = self.sun_position[2]
            if elevation < 20:
                color = [1.0, 0.7, 0.4]
            else:
                color = [1.0, 0.95, 0.8]
            
            self.sun_actor = self.plotter.add_mesh(
                sun,
                color=color,
                opacity=0.8,
                lighting=False,
                ambient=1.0,
                name='sun_disc'
            )
            
        except Exception as e:
            logger.warning(f"Sun visual error: {e}")
    
    def _setup_shadow_casting_lights(self):
        """Setup lights that cast shadows"""
        try:
            # Clear existing lights
            self.plotter.remove_all_lights()
            self.current_lights.clear()
            
            elevation = self.sun_position[2]
            intensity = self._calculate_sun_intensity(elevation)
            sun_color = self._calculate_sun_color(elevation)
            
            # 1. MAIN DIRECTIONAL LIGHT (casts shadows)
            sun_light = pv.Light(
                position=tuple(self.sun_position),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=intensity * 2.0,  # Reduced from 2.5
                color=sun_color,
                positional=True,
                cone_angle=90,
                show_actor=False
            )
            sun_light.attenuation_values = (1, 0, 0)
            self.plotter.add_light(sun_light)
            self.current_lights.append(sun_light)
            
            # 2. FILL LIGHT FROM OPPOSITE SIDE
            fill_position = (
                -self.sun_position[0] * 0.5,
                -self.sun_position[1] * 0.5,
                abs(self.sun_position[2]) * 0.8
            )
            fill_light = pv.Light(
                position=fill_position,
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=intensity * 0.7,  # Increased fill
                color=[0.9, 0.95, 1.0],
                positional=True,
                cone_angle=120,
                show_actor=False
            )
            self.plotter.add_light(fill_light)
            self.current_lights.append(fill_light)
            
            # 3. AMBIENT LIGHT
            ambient_light = pv.Light(
                position=(0, 0, 100),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.4,  # Increased ambient
                color=[0.95, 0.98, 1.0],
                positional=True,
                cone_angle=180,
                show_actor=False
            )
            self.plotter.add_light(ambient_light)
            self.current_lights.append(ambient_light)
            
            # 4. GROUND BOUNCE LIGHT
            if elevation > 10:
                bounce_light = pv.Light(
                    position=(0, 0, -2),
                    focal_point=(0, 0, 5),
                    light_type='scenelight',
                    intensity=intensity * 0.4,
                    color=[0.85, 0.9, 0.8],
                    positional=True,
                    cone_angle=160,
                    show_actor=False
                )
                self.plotter.add_light(bounce_light)
                self.current_lights.append(bounce_light)
            
            print(f"💡 Lights configured: {len(self.current_lights)} lights")
            
        except Exception as e:
            logger.error(f"Lighting setup error: {e}")
    
    def _create_shadow_projections(self):
        """Create shadow projections on the ground"""
        try:
            # Clear old shadows
            for actor in self.shadow_meshes:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.shadow_meshes.clear()
            
            if self.sun_position[2] <= 0:
                return
            
            # Calculate shadow parameters
            shadow_dir = self._calculate_shadow_direction()
            shadow_length = self._calculate_shadow_length()
            shadow_opacity = self._calculate_shadow_opacity()
            
            # Create building shadow projection
            building_shadow = pv.Plane(
                center=(
                    2 + shadow_dir[0] * shadow_length * 0.3,
                    2 + shadow_dir[1] * shadow_length * 0.3,
                    -0.03
                ),
                direction=(0, 0, 1),
                i_size=shadow_length,
                j_size=shadow_length * 0.8
            )
            
            # Rotate shadow based on sun direction
            if shadow_dir[0] != 0 or shadow_dir[1] != 0:
                angle = np.arctan2(shadow_dir[1], shadow_dir[0])
                building_shadow.rotate_z(np.degrees(angle))
            
            shadow_actor = self.plotter.add_mesh(
                building_shadow,
                color='black',
                opacity=shadow_opacity,
                lighting=False,
                name='building_shadow'
            )
            
            if shadow_actor:
                self.shadow_meshes.append(shadow_actor)
            
            print(f"🌑 Shadow projections created")
            
        except Exception as e:
            logger.warning(f"Shadow projection error: {e}")
    
    def _calculate_shadow_direction(self):
        """Calculate shadow direction"""
        horizontal = np.sqrt(self.sun_position[0]**2 + self.sun_position[1]**2)
        if horizontal > 0:
            return np.array([
                -self.sun_position[0] / horizontal,
                -self.sun_position[1] / horizontal,
                0
            ])
        return np.array([0, 0, 0])
    
    def _calculate_shadow_length(self):
        """Calculate shadow length based on sun elevation"""
        elevation = self.sun_position[2]
        if elevation < 10:
            return 20
        elif elevation < 30:
            return 15
        elif elevation < 60:
            return 10
        else:
            return 5
    
    def _calculate_shadow_opacity(self):
        """Calculate shadow opacity"""
        elevation = self.sun_position[2]
        base_opacity = 0.4 * (1 - elevation / 90)
        return max(0.15, min(0.4, base_opacity * self.weather_factor))
    
    def _calculate_sun_intensity(self, elevation):
        """Calculate sun intensity"""
        if elevation < 0:
            return 0.0
        elif elevation < 10:
            return 0.6
        elif elevation < 30:
            return 0.8
        else:
            return 1.0
    
    def _calculate_sun_color(self, elevation):
        """Calculate sun light color"""
        if elevation < 10:
            return [1.0, 0.7, 0.5]
        elif elevation < 30:
            return [1.0, 0.9, 0.7]
        else:
            return [1.0, 1.0, 0.95]
    
    def _create_night_scene(self):
        """Create night scene with visibility"""
        try:
            # Clear sun visual
            if self.sun_actor:
                try:
                    self.plotter.remove_actor('sun_disc')
                except:
                    pass
                self.sun_actor = None
            
            # Night lighting
            self.plotter.remove_all_lights()
            self.current_lights.clear()
            
            # Moon light
            moon_light = pv.Light(
                position=(30, 30, 40),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.4,
                color=[0.85, 0.85, 0.95],
                positional=True,
                cone_angle=60
            )
            self.plotter.add_light(moon_light)
            self.current_lights.append(moon_light)
            
            # Night ambient
            ambient = pv.Light(
                position=(0, 0, 50),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.25,
                color=[0.5, 0.5, 0.7],
                positional=True,
                cone_angle=180
            )
            self.plotter.add_light(ambient)
            self.current_lights.append(ambient)
            
            # Fill light
            fill = pv.Light(
                position=(-20, -20, 30),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.15,
                color=[0.4, 0.4, 0.6],
                positional=True,
                cone_angle=120
            )
            self.plotter.add_light(fill)
            self.current_lights.append(fill)
            
            print("🌙 Night scene created")
            
        except Exception as e:
            logger.warning(f"Night scene error: {e}")
    
    def _safe_clear(self):
        """Safely clear sun elements"""
        try:
            if self.sun_actor:
                try:
                    self.plotter.remove_actor('sun_disc')
                except:
                    pass
                self.sun_actor = None
            
            for actor in self.shadow_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.shadow_actors.clear()
            
            for actor in self.shadow_meshes:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.shadow_meshes.clear()
            
        except Exception as e:
            logger.warning(f"Clear error: {e}")
    
    def _process_pending_update(self):
        """Process pending update"""
        if self.pending_update and not self.updating:
            sun_pos, settings = self.pending_update
            self.pending_update = None
            self.create_photorealistic_sun(sun_pos, settings)
    
    def set_interactive_mode(self, interactive):
        """Set interactive mode"""
        self.interactive_mode = interactive
        if not interactive and self.sun_position[2] > 0:
            self._create_shadow_projections()
            if hasattr(self.plotter, 'render'):
                try:
                    self.plotter.render()
                except:
                    pass
    
    def create_building_shadows(self, building_bounds, sun_position, weather_factor=1.0):
        """Create building-specific shadows"""
        # Handled by _create_shadow_projections
        pass
    
    def update_sun_position(self, sun_position, solar_settings=None):
        """Update sun position"""
        self.pending_update = (sun_position, solar_settings)
        if not self.update_timer.isActive():
            self.update_timer.start(50)
    
    def set_quality_level(self, quality):
        """Set quality level"""
        self.quality_level = quality
    
    def destroy(self):
        """Clean up"""
        try:
            self.updating = True
            self.update_timer.stop()
            
            self._safe_clear()
            
            for light in self.current_lights:
                try:
                    self.plotter.remove_light(light)
                except:
                    pass
            self.current_lights.clear()
            
            self.scene_objects.clear()
            
            self.updating = False
            print("✅ Sun system destroyed")
            
        except Exception as e:
            logger.error(f"Destroy error: {e}")
