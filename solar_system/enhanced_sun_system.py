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
        print(f"🏗️ Building center set to: {self.building_center}")
        
        # Force immediate shadow update if sun exists
        if hasattr(self, 'sun_position') and self.sun_position is not None:
            self._force_shadow_update()
    
    def set_building_dimensions(self, width, length, height, roof_height=0):
        """Set building dimensions for accurate shadow calculation"""
        self.building_width = width
        self.building_length = length
        self.building_height = height
        self.roof_height = roof_height
        self._invalidate_shadow_cache()
        print(f"🏗️ Building dimensions: {width}x{length}x{height} (roof: {roof_height})")
        
        # Force immediate shadow update if sun exists
        if hasattr(self, 'sun_position') and self.sun_position is not None:
            self._force_shadow_update()
    
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
            
            print(f"🌞 Creating sun at elevation {self.sun_elevation:.1f}°, position {self.sun_position}")
            
            # Clear previous elements
            self._clear_sun_elements()
            
            # Create sun elements based on elevation
            if self.sun_elevation > 0:
                self._create_sun_sphere()
                self._create_sun_lighting()
                
                # Always try to create shadows if elevation is sufficient
                if self.sun_elevation > 5:
                    self._create_building_shadows()
                    print(f"✅ Shadows created for elevation {self.sun_elevation:.1f}°")
                else:
                    print(f"⚠️ Sun too low for shadows: {self.sun_elevation:.1f}°")
                
                if self.rays_enabled:
                    self._create_sun_rays()
                
                if self.atmosphere_enabled:
                    self._create_atmospheric_effects()
            else:
                self._create_night_lighting()
                print("🌙 Night lighting created")
            
            # Force render to show changes immediately
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
            # Emit update signal
            self.sun_updated.emit({
                'position': self.sun_position,
                'elevation': self.sun_elevation,
                'azimuth': self.sun_azimuth,
                'time': self.time_of_day,
                'weather': self.weather_factor
            })
            
            print(f"✅ Sun system updated successfully")
            
        except Exception as e:
            logger.error(f"Error creating sun: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.updating = False
    
    def _create_sun_sphere(self):
        """Create the sun sphere with debug cone to show direction"""
        try:
            # Much smaller sun with minimal visual impact
            base_radius = 1.5
            distance_factor = np.linalg.norm(self.sun_position) / 200.0
            
            sun_radius = base_radius * distance_factor
            sun_radius = np.clip(sun_radius, 0.8, 2.5)
            
            # Create simple sun sphere
            sun_sphere = pv.Sphere(
                radius=sun_radius,
                center=self.sun_position,
                phi_resolution=8,
                theta_resolution=8
            )
            
            # Simple, non-glaring sun color
            sun_color = [1.0, 0.9, 0.7]
            
            self.sun_actor = self.plotter.add_mesh(
                sun_sphere,
                color=sun_color,
                opacity=0.8,
                lighting=False,
                name='sun_sphere'
            )
            
            # Add debug cone to show sun direction
            self._create_sun_debug_cone()
            
            print(f"✅ Sun sphere and debug cone created")
            
        except Exception as e:
            logger.error(f"Error creating sun sphere: {e}")
    
    def _create_sun_debug_cone(self):
        """Create a debug cone showing sun light direction"""
        try:
            # Calculate cone direction (from sun to building center)
            direction = self.building_center - self.sun_position
            direction_length = np.linalg.norm(direction)
            
            if direction_length > 0:
                direction_normalized = direction / direction_length
                
                # Create cone showing light direction
                cone_height = min(direction_length * 0.7, 15.0)
                cone_radius = cone_height * 0.2
                
                # Position cone starting from sun
                cone_center = self.sun_position + direction_normalized * (cone_height / 2)
                
                debug_cone = pv.Cone(
                    center=cone_center,
                    direction=direction_normalized,
                    height=cone_height,
                    radius=cone_radius,
                    resolution=12
                )
                
                # Add cone with semi-transparent yellow
                cone_actor = self.plotter.add_mesh(
                    debug_cone,
                    color='yellow',
                    opacity=0.3,
                    lighting=False,
                    name='sun_debug_cone'
                )
                
                if cone_actor:
                    # Store as sun actor for cleanup
                    if not hasattr(self, 'debug_actors'):
                        self.debug_actors = []
                    self.debug_actors.append(cone_actor)
                    print(f"✅ Debug cone created showing sun direction")
                
        except Exception as e:
            logger.error(f"Error creating debug cone: {e}")
    
    def _calculate_sun_color(self):
        """Calculate sun color with reduced intensity to minimize glare"""
        # More subtle base colors
        if self.sun_elevation > 60:
            # High sun - soft white/yellow
            base_color = np.array([1.0, 0.95, 0.8])  # Less intense
        elif self.sun_elevation > 30:
            # Medium sun - warm yellow
            base_color = np.array([1.0, 0.9, 0.6])   # Less intense
        elif self.sun_elevation > 10:
            # Low sun - soft orange
            base_color = np.array([1.0, 0.8, 0.5])   # Less intense
        else:
            # Very low sun - muted red/orange
            base_color = np.array([0.9, 0.6, 0.3])   # Much less intense
        
        # Apply weather factor with reduced impact
        weather_adjustment = 0.7 + 0.2 * self.weather_factor  # Reduced intensity
        return base_color * weather_adjustment
    
    def _create_sun_lighting(self):
        """Create balanced sun lighting for roof visibility"""
        try:
            # Remove existing lights
            self.plotter.remove_all_lights()
            self.current_lights.clear()
            
            # Calculate balanced light intensity
            base_intensity = 1.2  # Slightly increased for better roof visibility
            elevation_factor = np.sin(np.radians(max(5, self.sun_elevation))) * 0.3
            weather_factor = 0.4 + 0.4 * self.weather_factor  # More balanced range
            
            light_intensity = base_intensity + elevation_factor + weather_factor
            light_intensity = np.clip(light_intensity, 0.8, 2.2)  # Good range for visibility
            
            # Main sun light with warm color
            sun_light = pv.Light(
                position=tuple(self.sun_position),
                focal_point=tuple(self.building_center),
                light_type='scenelight',
                intensity=light_intensity,
                color=[1.0, 0.95, 0.85],  # Warm white light
                positional=True,
                cone_angle=120,
                show_actor=False
            )
            
            self.plotter.add_light(sun_light)
            self.current_lights.append(sun_light)
            
            # Balanced ambient light for proper shadow contrast
            ambient_intensity = 0.35 * self.weather_factor
            ambient_light = pv.Light(
                light_type='cameralight',
                intensity=ambient_intensity,
                color=[0.85, 0.9, 1.0]  # Cool ambient
            )
            
            self.plotter.add_light(ambient_light)
            self.current_lights.append(ambient_light)
            
            print(f"✅ Balanced lighting created (main: {light_intensity:.2f}, ambient: {ambient_intensity:.2f})")
            
        except Exception as e:
            logger.error(f"Error creating sun lighting: {e}")
    
    def _create_building_shadows(self):
        """Create realistic building shadows with proper grass placement"""
        try:
            if self.sun_elevation <= 5:
                print(f"⚠️ No shadows - sun elevation too low: {self.sun_elevation}°")
                return
            
            print(f"🌑 Creating shadows - elevation: {self.sun_elevation}°, center: {self.building_center}")
            
            # Calculate shadow parameters
            shadow_length = self._calculate_shadow_length()
            shadow_direction = self._calculate_shadow_direction()
            shadow_width = self._calculate_shadow_width()
            shadow_opacity = self._calculate_shadow_opacity()
            
            print(f"🌑 Shadow params - Length: {shadow_length:.1f}, Width: {shadow_width:.1f}, Opacity: {shadow_opacity:.2f}")
            print(f"🌑 Shadow direction: [{shadow_direction[0]:.2f}, {shadow_direction[1]:.2f}]")
            
            # Create multiple shadow layers for better visibility
            shadows_created = []
            
            # Main building shadow - positioned correctly on grass
            main_shadow = self._create_main_building_shadow(
                shadow_length, shadow_direction, shadow_width, shadow_opacity
            )
            if main_shadow:
                shadows_created.append(main_shadow)
                print("✅ Main building shadow created")
            
            # Additional shadow for roof overhang
            if self.roof_height > 0:
                roof_shadow = self._create_roof_shadow(
                    shadow_length, shadow_direction, shadow_width, shadow_opacity
                )
                if roof_shadow:
                    shadows_created.append(roof_shadow)
                    print("✅ Roof shadow created")
            
            # Create a subtle ground shadow for better visibility
            ground_shadow = self._create_ground_contact_shadow(shadow_direction, shadow_opacity)
            if ground_shadow:
                shadows_created.append(ground_shadow)
                print("✅ Ground contact shadow created")
            
            print(f"✅ Created {len(shadows_created)} shadows total")
            
            # Force render to show shadows immediately
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
        except Exception as e:
            logger.error(f"Error creating building shadows: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_main_building_shadow(self, length, direction, width, opacity):
        """Create highly visible building shadow on grass with debug info"""
        try:
            # Calculate shadow center - ensure it's visible on grass
            shadow_offset_distance = length * 0.6  # Increased for better visibility
            shadow_center = self.building_center.copy()
            shadow_center[0] += direction[0] * shadow_offset_distance
            shadow_center[1] += direction[1] * shadow_offset_distance
            shadow_center[2] = -0.045  # Slightly below grass for guaranteed visibility
            
            print(f"🌑 SHADOW DEBUG:")
            print(f"   Building center: {self.building_center}")
            print(f"   Shadow direction: {direction}")
            print(f"   Shadow offset: {shadow_offset_distance:.1f}")
            print(f"   Shadow center: [{shadow_center[0]:.2f}, {shadow_center[1]:.2f}, {shadow_center[2]:.3f}]")
            print(f"   Shadow size: {length:.1f} x {width:.1f}")
            print(f"   Shadow opacity: {opacity:.2f}")
            
            # Create larger, more visible shadow
            shadow_plane = pv.Plane(
                center=shadow_center,
                direction=(0, 0, 1),
                i_size=length * 1.5,  # Much larger
                j_size=width * 1.5,
                i_resolution=50,  # High resolution
                j_resolution=40
            )
            
            # Ensure proper normals
            shadow_plane.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Rotate shadow
            shadow_angle = np.degrees(np.arctan2(direction[1], direction[0]))
            shadow_plane.rotate_z(shadow_angle, inplace=True)
            
            # Add shadow with maximum contrast
            shadow_actor = self.plotter.add_mesh(
                shadow_plane,
                color='#000000',  # Pure black
                opacity=0.9,  # Very high opacity
                lighting=False,
                name='main_building_shadow'
            )
            
            if shadow_actor:
                self.shadow_actors.append(shadow_actor)
                print(f"✅ HIGHLY VISIBLE shadow created at {shadow_center}")
                
                # Create debug marker at shadow center
                self._create_shadow_debug_marker(shadow_center)
                
                return {
                    'type': 'main_shadow',
                    'center': shadow_center,
                    'length': length,
                    'width': width,
                    'opacity': 0.9,
                    'angle': shadow_angle
                }
            else:
                print(f"❌ Failed to create shadow actor")
            
        except Exception as e:
            logger.error(f"Error creating main building shadow: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _create_shadow_debug_marker(self, shadow_center):
        """Create a debug marker to show exactly where shadow should be"""
        try:
            # Create small red sphere at shadow center
            marker = pv.Sphere(
                radius=0.5,
                center=shadow_center,
                phi_resolution=8,
                theta_resolution=8
            )
            
            marker_actor = self.plotter.add_mesh(
                marker,
                color='red',
                opacity=1.0,
                lighting=False,
                name='shadow_debug_marker'
            )
            
            if marker_actor:
                if not hasattr(self, 'debug_actors'):
                    self.debug_actors = []
                self.debug_actors.append(marker_actor)
                print(f"✅ Debug marker placed at shadow center")
            
        except Exception as e:
            logger.error(f"Error creating shadow debug marker: {e}")
    
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
    
    def _create_ground_contact_shadow(self, direction, opacity):
        """Create a subtle shadow directly under the building for better ground contact"""
        try:
            # Create a shadow directly under the building
            contact_shadow_center = self.building_center.copy()
            contact_shadow_center[2] = self.shadow_level + 0.002  # Slightly above main shadow
            
            # Smaller shadow directly under building
            contact_width = self.building_width * 0.8
            contact_length = self.building_length * 0.8
            
            contact_shadow = pv.Plane(
                center=contact_shadow_center,
                direction=(0, 0, 1),
                i_size=contact_length,
                j_size=contact_width,
                i_resolution=20,
                j_resolution=20
            )
            
            # Ensure proper normals
            contact_shadow.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Add with reduced opacity
            contact_opacity = opacity * 0.6
            contact_actor = self.plotter.add_mesh(
                contact_shadow,
                color='#1a1a1a',  # Dark gray
                opacity=contact_opacity,
                lighting=False,
                name='ground_contact_shadow'
            )
            
            if contact_actor:
                self.shadow_actors.append(contact_actor)
                print(f"✅ Ground contact shadow created with opacity {contact_opacity:.2f}")
                
                return {
                    'type': 'contact_shadow',
                    'center': contact_shadow_center,
                    'width': contact_width,
                    'length': contact_length,
                    'opacity': contact_opacity
                }
            else:
                print("❌ Failed to create ground contact shadow")
                
        except Exception as e:
            logger.error(f"Error creating ground contact shadow: {e}")
        
        return None
    
    def _create_atmospheric_effects(self):
        """Disable atmospheric effects to eliminate yellow flare"""
        # Completely disable atmospheric effects to remove flare
        print("🚫 Atmospheric effects disabled to remove flare")
        return
    
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
        base_opacity = 0.8  # Even darker base
        elevation_factor = np.sin(np.radians(max(5, self.sun_elevation))) * 0.15
        weather_factor = 0.05 + 0.2 * self.weather_factor
        
        opacity = base_opacity + elevation_factor + weather_factor
        final_opacity = np.clip(opacity, 0.7, 0.98)  # Much darker range
        
        print(f"🌑 Shadow opacity calculation: base={base_opacity}, elevation_factor={elevation_factor:.2f}, weather_factor={weather_factor:.2f}, final={final_opacity:.2f}")
        return final_opacity
    
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
    
    def _force_shadow_update(self):
        """Force immediate shadow update with enhanced debugging"""
        try:
            print("🔄 Forcing shadow update...")
            
            # Clear existing shadows
            for actor in self.shadow_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.shadow_actors.clear()
            
            # Clear cache to force recreation
            self.shadow_cache.clear()
            
            # Validate shadow parameters
            print(f"🔧 Shadow parameters:")
            print(f"   Building center: {self.building_center}")
            print(f"   Building dimensions: {self.building_width}x{self.building_length}x{self.building_height}")
            print(f"   Shadow level: {self.shadow_level}")
            print(f"   Sun elevation: {self.sun_elevation}°")
            print(f"   Sun position: {self.sun_position}")
            
            # Force create shadows with test parameters if needed
            if self.sun_elevation <= 5:
                print("⚠️ Sun elevation too low, setting test elevation")
                self.sun_elevation = 45.0
                
            if np.allclose(self.building_center, [0, 0, 0]):
                print("⚠️ Building center at origin, setting default")
                self.building_center = np.array([0, 0, 1.5])
            
            # Recreate shadows immediately
            self._create_building_shadows()
            
            # Force render twice to ensure visibility
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                import time
                time.sleep(0.1)  # Small delay
                self.plotter.render()
                print("✅ Double render completed")
                
            shadow_count = len(self.shadow_actors)
            if shadow_count > 0:
                print(f"✅ Forced shadow update completed - {shadow_count} shadows created")
            else:
                print("❌ No shadows created despite forced update")
                
        except Exception as e:
            print(f"❌ Force shadow update failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _invalidate_shadow_cache(self):
        """Clear shadow cache when parameters change"""
        self.shadow_cache.clear()
        print("🗑️ Shadow cache cleared")
    
    def _clear_sun_elements(self):
        """Clear all sun-related visual elements including debug elements"""
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
            
            # Remove debug actors (cone, markers, etc.)
            if hasattr(self, 'debug_actors'):
                for actor in self.debug_actors:
                    try:
                        self.plotter.remove_actor(actor)
                    except:
                        pass
                self.debug_actors.clear()
            
            # Remove debug elements by name
            debug_names = ['sun_debug_cone', 'shadow_debug_marker']
            for name in debug_names:
                try:
                    self.plotter.remove_actor(name)
                except:
                    pass
            
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
    
    def test_shadows_immediately(self):
        """Test method to immediately create visible shadows for debugging"""
        try:
            print("🧪 Testing shadows immediately...")
            
            # Set optimal parameters for shadow testing
            self.building_center = np.array([0, 0, 1.5])
            self.building_width = 8.0
            self.building_length = 10.0
            self.building_height = 3.0
            self.roof_height = 4.0
            self.shadow_level = -0.04
            self.sun_elevation = 45.0
            self.sun_azimuth = 180.0
            self.weather_factor = 1.0
            
            # Set good sun position
            test_sun_position = [20, 20, 20]
            self.sun_position = np.array(test_sun_position)
            
            print(f"🧪 Test parameters set:")
            print(f"   Building center: {self.building_center}")
            print(f"   Sun position: {self.sun_position}")
            print(f"   Sun elevation: {self.sun_elevation}°")
            
            # Force shadow creation
            self._force_shadow_update()
            
            # Create a test ground plane if none exists
            self._create_test_ground_for_shadows()
            
            return len(self.shadow_actors) > 0
            
        except Exception as e:
            print(f"❌ Shadow test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_test_ground_for_shadows(self):
        """Create a test ground plane to receive shadows"""
        try:
            # Check if ground already exists
            existing_ground = False
            for actor in self.plotter.renderer.actors:
                if hasattr(actor, 'name') and 'ground' in str(actor.name).lower():
                    existing_ground = True
                    break
            
            if existing_ground:
                print("✅ Ground plane already exists")
                return
            
            print("🧪 Creating test ground for shadow visibility...")
            
            # Create a simple ground plane
            ground_size = 40.0
            ground_level = self.shadow_level - 0.01  # Slightly below shadow level
            
            ground_plane = pv.Plane(
                center=[0, 0, ground_level],
                direction=(0, 0, 1),
                i_size=ground_size,
                j_size=ground_size,
                i_resolution=50,
                j_resolution=50
            )
            
            # Ensure proper normals
            ground_plane.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Add ground plane with shadow-receiving properties
            ground_actor = self.plotter.add_mesh(
                ground_plane,
                color='#6BCD6B',  # Grass green
                opacity=1.0,
                lighting=True,
                smooth_shading=True,
                ambient=0.4,
                diffuse=0.9,
                specular=0.0,
                name='test_ground_for_shadows'
            )
            
            if ground_actor:
                print("✅ Test ground created for shadow visibility")
            else:
                print("❌ Failed to create test ground")
                
        except Exception as e:
            print(f"❌ Error creating test ground: {e}")
    
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
            
            print("✅ Enhanced sun system destroyed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.updating = False