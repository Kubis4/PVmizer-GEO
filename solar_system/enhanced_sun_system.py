#!/usr/bin/env python3
"""
enhanced_sun_system.py - Optimized Realistic Sun System
Features: Dynamic shadows, sun rays, atmospheric effects, performance optimization
"""
import numpy as np
import pyvista as pv
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import logging
import time
import math

logger = logging.getLogger(__name__)

class EnhancedRealisticSunSystem(QObject):
    """Realistic sun system with dynamic shadows, rays, and atmospheric effects"""
    
    sun_updated = pyqtSignal(dict)
    
    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        
        # Sun storage
        self.sun_actor = None
        self.shadow_actors = []
        self.ray_actors = []
        self.atmosphere_actors = []
        self.current_lights = []
        
        # Sun properties
        self.sun_position = np.array([50, 0, 50])
        self.sun_elevation = 45.0
        self.sun_azimuth = 180.0
        self.time_of_day = 12.0
        self.weather_factor = 1.0
        
        # Building dimensions for shadow calculation
        self.building_height = 3.0
        self.roof_height = 4.0
        self.building_width = 8.0
        self.building_length = 10.0
        self.building_center = np.array([0, 0, 0])
        
        # Ground and shadow levels
        self.grass_ground_level = -0.05
        self.shadow_level = -0.04
        
        # Performance optimization
        self.update_cooldown = 0.1
        self.last_update_time = 0
        self.updating = False
        self.pending_update = None
        self.quality_level = 'high'  # 'low', 'medium', 'high', 'ultra'
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._process_pending_update)
        self.update_timer.setSingleShot(True)
        
        # Scene management
        self.interactive_mode = False
        self.scene_objects = []
        self.shadow_cache = {}
        
        # Sun ray properties (debug only)
        self.rays_enabled = False  # Default off, debug only
        self.ray_count = 4  # Reduced for debug
        self.ray_length = 15.0
        
        # Atmospheric properties
        self.atmosphere_enabled = True
        self.atmosphere_density = 0.3
        
    def set_building_center(self, center):
        """Set the center position of the building for shadow calculations"""
        self.building_center = np.array(center)
        self._invalidate_shadow_cache()
    
    def set_building_dimensions(self, width, length, height, roof_height=0):
        """Set building dimensions for accurate shadow calculation"""
        self.building_width = width
        self.building_length = length
        self.building_height = height
        self.roof_height = roof_height
        self._invalidate_shadow_cache()
    
    def set_quality_level(self, quality):
        """Set rendering quality level"""
        quality_settings = {
            'low': {'ray_count': 3, 'shadow_res': 20, 'atmosphere_res': 10},
            'medium': {'ray_count': 4, 'shadow_res': 30, 'atmosphere_res': 15},
            'high': {'ray_count': 4, 'shadow_res': 40, 'atmosphere_res': 20},
            'ultra': {'ray_count': 6, 'shadow_res': 60, 'atmosphere_res': 30}
        }
        
        self.quality_level = quality
        settings = quality_settings.get(quality, quality_settings['high'])
        self.ray_count = settings['ray_count']
        self.shadow_resolution = settings['shadow_res']
        self.atmosphere_resolution = settings['atmosphere_res']
        
        self._invalidate_shadow_cache()
    
    def create_photorealistic_sun(self, sun_position, solar_settings=None):
        """Create photorealistic sun with shadows, rays, and atmospheric effects"""
        current_time = time.time()
        
        # Throttle updates for performance
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
        
        try:
            # Update sun properties
            self.sun_position = np.array(sun_position)
            
            if solar_settings:
                self.sun_elevation = solar_settings.get('sun_elevation', 45.0)
                self.sun_azimuth = solar_settings.get('sun_azimuth', 180.0)
                self.time_of_day = solar_settings.get('current_hour', 12.0)
                self.weather_factor = solar_settings.get('weather_factor', 1.0)
            
            # Clear previous elements
            self._clear_sun_elements()
            
            # Create sun elements based on elevation
            if self.sun_elevation > 0:
                self._create_sun_sphere()
                self._create_sun_lighting()
                self._create_building_shadows()
                
                if self.rays_enabled:
                    self._create_sun_rays()
                
                if self.atmosphere_enabled:
                    self._create_atmospheric_effects()
            else:
                self._create_night_lighting()
            
            # Emit update signal
            self.sun_updated.emit({
                'position': self.sun_position,
                'elevation': self.sun_elevation,
                'azimuth': self.sun_azimuth,
                'time': self.time_of_day,
                'weather': self.weather_factor
            })
            
        except Exception as e:
            logger.error(f"Error creating sun: {e}")
        finally:
            self.updating = False
    
    def _create_sun_sphere(self):
        """Create the sun sphere with appropriate size and glow"""
        try:
            # Calculate sun size based on distance and time of day
            base_radius = 4.0
            distance_factor = np.linalg.norm(self.sun_position) / 100.0
            time_factor = 1.0 + 0.3 * abs(np.cos(np.pi * (self.time_of_day - 12) / 12))
            
            sun_radius = base_radius * distance_factor * time_factor
            sun_radius = np.clip(sun_radius, 2.0, 8.0)
            
            # Create sun sphere
            sun_sphere = pv.Sphere(
                radius=sun_radius,
                center=self.sun_position,
                phi_resolution=20,
                theta_resolution=20
            )
            
            # Calculate sun color based on elevation and time
            sun_color = self._calculate_sun_color()
            
            self.sun_actor = self.plotter.add_mesh(
                sun_sphere,
                color=sun_color,
                opacity=0.9,
                lighting=False,
                name='sun_sphere'
            )
            
        except Exception as e:
            logger.error(f"Error creating sun sphere: {e}")
    
    def _calculate_sun_color(self):
        """Calculate sun color based on elevation and atmospheric conditions"""
        # Base colors for different times
        if self.sun_elevation > 60:
            # High sun - white/yellow
            base_color = np.array([1.0, 1.0, 0.9])
        elif self.sun_elevation > 30:
            # Medium sun - yellow
            base_color = np.array([1.0, 0.95, 0.7])
        elif self.sun_elevation > 10:
            # Low sun - orange
            base_color = np.array([1.0, 0.7, 0.4])
        else:
            # Very low sun - red/orange
            base_color = np.array([1.0, 0.5, 0.2])
        
        # Apply weather factor
        weather_adjustment = 0.8 + 0.2 * self.weather_factor
        return base_color * weather_adjustment
    
    def _create_sun_lighting(self):
        """Create realistic sun lighting"""
        try:
            # Remove existing lights
            self.plotter.remove_all_lights()
            self.current_lights.clear()
            
            # Calculate light intensity based on sun elevation and weather
            base_intensity = 1.0
            elevation_factor = np.sin(np.radians(max(5, self.sun_elevation)))
            weather_factor = 0.3 + 0.7 * self.weather_factor
            
            light_intensity = base_intensity * elevation_factor * weather_factor
            light_intensity = np.clip(light_intensity, 0.1, 2.0)
            
            # Main sun light
            sun_light = pv.Light(
                position=tuple(self.sun_position),
                focal_point=tuple(self.building_center),
                light_type='scenelight',
                intensity=light_intensity,
                color=self._calculate_sun_color(),
                positional=True,
                cone_angle=120,
                show_actor=False
            )
            
            self.plotter.add_light(sun_light)
            self.current_lights.append(sun_light)
            
            # Add ambient light for realism
            ambient_intensity = 0.3 * weather_factor
            ambient_light = pv.Light(
                light_type='cameralight',
                intensity=ambient_intensity,
                color=[0.8, 0.9, 1.0]  # Slightly blue ambient
            )
            
            self.plotter.add_light(ambient_light)
            self.current_lights.append(ambient_light)
            
        except Exception as e:
            logger.error(f"Error creating sun lighting: {e}")
    
    def _create_building_shadows(self):
        """Create realistic building shadows"""
        try:
            if self.sun_elevation <= 5:  # No shadows for very low sun
                return
            
            # Check cache first
            cache_key = self._get_shadow_cache_key()
            if cache_key in self.shadow_cache and self.quality_level != 'ultra':
                cached_shadows = self.shadow_cache[cache_key]
                for shadow_data in cached_shadows:
                    self._add_cached_shadow(shadow_data)
                return
            
            # Calculate shadow parameters
            shadow_length = self._calculate_shadow_length()
            shadow_direction = self._calculate_shadow_direction()
            shadow_width = self._calculate_shadow_width()
            shadow_opacity = self._calculate_shadow_opacity()
            
            # Create main building shadow
            shadows_created = []
            main_shadow = self._create_main_building_shadow(
                shadow_length, shadow_direction, shadow_width, shadow_opacity
            )
            if main_shadow:
                shadows_created.append(main_shadow)
            
            # Create additional shadows for complex geometry
            if self.roof_height > 0:
                roof_shadow = self._create_roof_shadow(
                    shadow_length, shadow_direction, shadow_width, shadow_opacity
                )
                if roof_shadow:
                    shadows_created.append(roof_shadow)
            
            # Cache shadows for performance
            if shadows_created and self.quality_level != 'ultra':
                self.shadow_cache[cache_key] = shadows_created
            
        except Exception as e:
            logger.error(f"Error creating building shadows: {e}")
    
    def _create_main_building_shadow(self, length, direction, width, opacity):
        """Create the main building shadow"""
        try:
            # Calculate shadow center (preserving original offset logic)
            shadow_offset_distance = length * 0.4  # Original offset calculation
            shadow_center = self.building_center.copy()
            shadow_center[0] += direction[0] * shadow_offset_distance
            shadow_center[1] += direction[1] * shadow_offset_distance
            shadow_center[2] = self.shadow_level
            
            # Create shadow plane
            shadow_plane = pv.Plane(
                center=shadow_center,
                direction=(0, 0, 1),
                i_size=length,
                j_size=width,
                i_resolution=max(20, self.shadow_resolution),
                j_resolution=max(15, int(self.shadow_resolution * 0.75))
            )
            
            # Apply shadow shape (more realistic building outline)
            shadow_points = self._create_building_shadow_shape(shadow_plane, direction)
            if shadow_points is not None:
                shadow_plane = shadow_points
            
            # Rotate shadow to match sun direction
            shadow_angle = np.degrees(np.arctan2(direction[1], direction[0]))
            shadow_plane.rotate_z(shadow_angle, inplace=True)
            
            # Add shadow to scene with darker color
            shadow_actor = self.plotter.add_mesh(
                shadow_plane,
                color='#000000',  # Pure black for darker shadows
                opacity=opacity,
                lighting=False,
                name='main_building_shadow'
            )
            
            if shadow_actor:
                self.shadow_actors.append(shadow_actor)
                return {
                    'type': 'main_shadow',
                    'center': shadow_center,
                    'length': length,
                    'width': width,
                    'opacity': opacity,
                    'angle': shadow_angle
                }
            
        except Exception as e:
            logger.error(f"Error creating main building shadow: {e}")
        
        return None
    
    def _create_roof_shadow(self, length, direction, width, opacity):
        """Create roof shadow overlay"""
        try:
            # Roof shadow is slightly offset and smaller
            roof_shadow_length = length * 0.8
            roof_shadow_width = width * 0.6
            roof_opacity = opacity * 0.7
            
            shadow_offset = length * 0.6
            roof_shadow_center = self.building_center.copy()
            roof_shadow_center[0] += direction[0] * shadow_offset
            roof_shadow_center[1] += direction[1] * shadow_offset
            roof_shadow_center[2] = self.shadow_level + 0.001  # Slightly above main shadow
            
            roof_shadow_plane = pv.Plane(
                center=roof_shadow_center,
                direction=(0, 0, 1),
                i_size=roof_shadow_length,
                j_size=roof_shadow_width,
                i_resolution=max(15, int(self.shadow_resolution * 0.75)),
                j_resolution=max(10, int(self.shadow_resolution * 0.5))
            )
            
            shadow_angle = np.degrees(np.arctan2(direction[1], direction[0]))
            roof_shadow_plane.rotate_z(shadow_angle, inplace=True)
            
            roof_shadow_actor = self.plotter.add_mesh(
                roof_shadow_plane,
                color='#0d0d0d',  # Very dark gray for roof shadow
                opacity=roof_opacity,
                lighting=False,
                name='roof_shadow'
            )
            
            if roof_shadow_actor:
                self.shadow_actors.append(roof_shadow_actor)
                return {
                    'type': 'roof_shadow',
                    'center': roof_shadow_center,
                    'length': roof_shadow_length,
                    'width': roof_shadow_width,
                    'opacity': roof_opacity,
                    'angle': shadow_angle
                }
            
        except Exception as e:
            logger.error(f"Error creating roof shadow: {e}")
        
        return None
    
    def _create_building_shadow_shape(self, shadow_plane, direction):
        """Create more realistic building-shaped shadow"""
        try:
            # This could be expanded to create complex shadow shapes
            # For now, return the basic plane
            return shadow_plane
            
        except Exception as e:
            logger.error(f"Error creating shadow shape: {e}")
            return shadow_plane
    
    def _create_sun_rays(self):
        """Create debug sun rays (minimal, for debugging only)"""
        try:
            if self.sun_elevation < 10:  # No rays for very low sun
                return
            
            # Very subtle rays for debug only
            ray_opacity = 0.05 + 0.05 * self.weather_factor
            ray_opacity = np.clip(ray_opacity, 0.02, 0.1)
            
            # Create minimal rays for debugging
            for i in range(self.ray_count):
                angle = (2 * np.pi * i) / self.ray_count
                self._create_single_ray(angle, ray_opacity)
            
        except Exception as e:
            logger.error(f"Error creating debug sun rays: {e}")
    
    def _create_single_ray(self, angle, opacity):
        """Create a single sun ray"""
        try:
            # Calculate ray direction
            ray_direction = np.array([
                np.cos(angle) * 0.3,
                np.sin(angle) * 0.3,
                -0.8  # Rays point mostly downward
            ])
            ray_direction = ray_direction / np.linalg.norm(ray_direction)
            
            # Create ray geometry
            ray_start = self.sun_position.copy()
            ray_end = ray_start + ray_direction * self.ray_length
            
            # Create cylinder for ray
            ray_cylinder = pv.Cylinder(
                center=(ray_start + ray_end) / 2,
                direction=ray_direction,
                radius=0.5,
                height=self.ray_length,
                resolution=8
            )
            
            ray_actor = self.plotter.add_mesh(
                ray_cylinder,
                color='yellow',
                opacity=opacity,
                lighting=False,
                name=f'sun_ray_{len(self.ray_actors)}'
            )
            
            if ray_actor:
                self.ray_actors.append(ray_actor)
            
        except Exception as e:
            logger.error(f"Error creating single ray: {e}")
    
    def _create_atmospheric_effects(self):
        """Create atmospheric haze and glow effects"""
        try:
            if self.atmosphere_density <= 0:
                return
            
            # Create atmospheric glow around sun
            glow_radius = 15.0 * (1.0 + self.atmosphere_density)
            
            atmosphere_sphere = pv.Sphere(
                radius=glow_radius,
                center=self.sun_position,
                phi_resolution=self.atmosphere_resolution,
                theta_resolution=self.atmosphere_resolution
            )
            
            # Atmospheric color based on sun elevation
            if self.sun_elevation > 30:
                atm_color = [1.0, 1.0, 0.9]
            elif self.sun_elevation > 10:
                atm_color = [1.0, 0.8, 0.6]
            else:
                atm_color = [1.0, 0.6, 0.4]
            
            atm_opacity = 0.05 + 0.1 * self.atmosphere_density * self.weather_factor
            atm_opacity = np.clip(atm_opacity, 0.02, 0.15)
            
            atmosphere_actor = self.plotter.add_mesh(
                atmosphere_sphere,
                color=atm_color,
                opacity=atm_opacity,
                lighting=False,
                name='atmosphere_glow'
            )
            
            if atmosphere_actor:
                self.atmosphere_actors.append(atmosphere_actor)
            
        except Exception as e:
            logger.error(f"Error creating atmospheric effects: {e}")
    
    def _create_night_lighting(self):
        """Create subtle night lighting"""
        try:
            self.plotter.remove_all_lights()
            self.current_lights.clear()
            
            # Dim ambient light for night
            night_light = pv.Light(
                light_type='cameralight',
                intensity=0.2,
                color=[0.4, 0.5, 0.8]  # Blue moonlight
            )
            
            self.plotter.add_light(night_light)
            self.current_lights.append(night_light)
            
        except Exception as e:
            logger.error(f"Error creating night lighting: {e}")
    
    def _calculate_shadow_length(self):
        """Calculate shadow length based on sun elevation (preserving original logic)"""
        if self.sun_elevation <= 0:
            return 15.0  # Default for very low sun
        
        total_height = self.building_height + self.roof_height
        if self.sun_elevation < 5:
            shadow_length = total_height * 20  # Very long shadows for low sun
        else:
            elevation_rad = np.radians(max(1, self.sun_elevation))
            shadow_length = total_height / np.tan(elevation_rad)
        
        return max(shadow_length, 8.0)  # Minimum shadow length
    
    def _calculate_shadow_direction(self):
        """Calculate shadow direction based on sun position (preserving original logic)"""
        # Use the original logic that was working with your roof
        sun_horizontal = np.array([self.sun_position[0], self.sun_position[1]])
        
        if np.linalg.norm(sun_horizontal) < 0.1:
            # Use azimuth if sun is directly overhead (original logic)
            azimuth_rad = np.radians(self.sun_azimuth)
            direction = np.array([
                np.sin(azimuth_rad),
                -np.cos(azimuth_rad)
            ])
        else:
            # Shadow direction away from sun (original logic)
            distance = np.linalg.norm(sun_horizontal)
            direction = -sun_horizontal / distance
        
        return direction
    
    def _calculate_shadow_width(self):
        """Calculate shadow width based on building dimensions and sun angle"""
        diagonal = np.sqrt(self.building_width**2 + self.building_length**2)
        
        if self.sun_elevation < 20:
            width_factor = 1.5
        elif self.sun_elevation < 45:
            width_factor = 1.2
        else:
            width_factor = 1.0
        
        return diagonal * width_factor
    
    def _calculate_shadow_opacity(self):
        """Calculate shadow opacity - much darker shadows"""
        base_opacity = 0.7  # Much darker base
        elevation_factor = np.sin(np.radians(max(5, self.sun_elevation))) * 0.2
        weather_factor = 0.1 + 0.3 * self.weather_factor
        
        opacity = base_opacity + elevation_factor + weather_factor
        return np.clip(opacity, 0.6, 0.95)  # Much darker range
    
    def _get_shadow_cache_key(self):
        """Generate cache key for shadow optimization"""
        return f"{self.sun_elevation:.0f}_{self.sun_azimuth:.0f}_{self.weather_factor:.1f}_{self.building_height:.1f}"
    
    def _add_cached_shadow(self, shadow_data):
        """Add cached shadow to scene"""
        try:
            if shadow_data['type'] == 'main_shadow':
                shadow_plane = pv.Plane(
                    center=shadow_data['center'],
                    direction=(0, 0, 1),
                    i_size=shadow_data['length'],
                    j_size=shadow_data['width'],
                    i_resolution=max(20, self.shadow_resolution),
                    j_resolution=max(15, int(self.shadow_resolution * 0.75))
                )
                shadow_plane.rotate_z(shadow_data['angle'], inplace=True)
                
                shadow_actor = self.plotter.add_mesh(
                    shadow_plane,
                    color='black',
                    opacity=shadow_data['opacity'],
                    lighting=False,
                    name='cached_main_shadow'
                )
                
                if shadow_actor:
                    self.shadow_actors.append(shadow_actor)
            
        except Exception as e:
            logger.error(f"Error adding cached shadow: {e}")
    
    def _invalidate_shadow_cache(self):
        """Clear shadow cache when parameters change"""
        self.shadow_cache.clear()
    
    def _clear_sun_elements(self):
        """Clear all sun-related visual elements"""
        try:
            # Remove sun actor
            if self.sun_actor:
                try:
                    self.plotter.remove_actor('sun_sphere')
                except:
                    pass
                self.sun_actor = None
            
            # Remove shadows
            for actor in self.shadow_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.shadow_actors.clear()
            
            # Remove rays
            for actor in self.ray_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.ray_actors.clear()
            
            # Remove atmosphere
            for actor in self.atmosphere_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.atmosphere_actors.clear()
            
        except Exception as e:
            logger.error(f"Error clearing sun elements: {e}")
    
    def _process_pending_update(self):
        """Process pending update from timer"""
        if self.pending_update and not self.updating:
            sun_pos, settings = self.pending_update
            self.pending_update = None
            self.create_photorealistic_sun(sun_pos, settings)
    
    def update_sun_position(self, sun_position, solar_settings=None):
        """Update sun position (public interface)"""
        self.create_photorealistic_sun(sun_position, solar_settings)
    
    def set_interactive_mode(self, interactive):
        """Enable/disable interactive mode for performance"""
        self.interactive_mode = interactive
        if interactive:
            self.set_quality_level('medium')
        else:
            self.set_quality_level('high')
    
    def enable_debug_rays(self, enabled=True):
        """Enable/disable debug rays"""
        self.rays_enabled = enabled
        if not enabled:
            for actor in self.ray_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.ray_actors.clear()
    
    def set_rays_enabled(self, enabled):
        """Enable/disable sun rays (alias for debug rays)"""
        self.enable_debug_rays(enabled)
    
    def set_atmosphere_enabled(self, enabled):
        """Enable/disable atmospheric effects"""
        self.atmosphere_enabled = enabled
        if not enabled:
            for actor in self.atmosphere_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.atmosphere_actors.clear()
    
    def set_atmosphere_density(self, density):
        """Set atmospheric density (0.0 to 1.0)"""
        self.atmosphere_density = np.clip(density, 0.0, 1.0)
    
    def register_scene_object(self, mesh, name, cast_shadow=True):
        """Register object that should cast shadows"""
        self.scene_objects.append({
            'mesh': mesh,
            'name': name,
            'cast_shadow': cast_shadow
        })
        self._invalidate_shadow_cache()
    
    def create_building_shadows(self, building_bounds, sun_position, weather_factor=1.0):
        """Create shadows for multiple buildings"""
        # This method can be expanded for complex scenes with multiple buildings
        self.weather_factor = weather_factor
        self.create_photorealistic_sun(sun_position)
    
    def destroy(self):
        """Clean up all resources"""
        try:
            self.updating = True
            self.update_timer.stop()
            
            self._clear_sun_elements()
            
            # Remove all lights
            for light in self.current_lights:
                try:
                    self.plotter.remove_light(light)
                except:
                    pass
            self.current_lights.clear()
            
            # Clear caches
            self.shadow_cache.clear()
            self.scene_objects.clear()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.updating = False