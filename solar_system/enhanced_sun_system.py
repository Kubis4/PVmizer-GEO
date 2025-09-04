#!/usr/bin/env python3
"""
enhanced_sun_system.py - High-performance sun system with OSPRay ray tracing support
DEBUG VERSION - Sun sphere disabled, with position debugging
"""
import numpy as np
import pyvista as pv
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time

class EnhancedRealisticSunSystem(QObject):
    """High-performance sun system with adaptive quality and OSPRay ray tracing"""
    
    sun_updated = pyqtSignal(dict)
    
    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        
        # Performance settings
        self.performance_mode = 'balanced'  # 'performance', 'balanced', 'quality'
        self.adaptive_quality = True
        self.frame_time_target = 16.67  # Target 60 FPS (ms)
        self.last_frame_time = 0
        
        # Caching
        self.shadow_cache = {}
        self.light_cache = {}
        self.last_update_time = 0
        self.update_threshold = 0.5  # Minimum time between updates (seconds)
        
        # LOD (Level of Detail) settings
        self.lod_distance_threshold = 30
        self.current_lod = 'high'
        
        # Components
        self.sun_actor = None
        self.sun_glow_actors = []
        self.shadow_actors = []
        self.current_lights = []
        self.debug_actors = []  # For debug visualization
        
        # Sun parameters
        self.sun_position = np.array([50, 0, 50])
        self.sun_elevation = 45.0  # Degrees above horizon
        self.sun_azimuth = 180.0   # Degrees from north
        self.time_of_day = 12.0
        self.weather_factor = 1.0
        
        # Building info
        self.building_height = 3.0
        self.roof_height = 4.0
        self.building_width = 8.0
        self.building_length = 10.0
        self.building_center = np.array([0, 0, 1.5])
        self.building_rotation = 0
        
        # Environment objects
        self.environment_objects = []
        self.scene_objects = {}
        
        # Shadow settings
        self.shadow_enabled = True
        self.min_shadow_elevation = 5.0
        self.shadow_resolution = 'medium'
        self.shadow_update_frequency = 2  # Update every N frames
        self.shadow_frame_counter = 0
        
        # Lighting settings
        self.use_image_based_lighting = False
        self.ambient_intensity = 0.3
        self.sun_intensity_multiplier = 2.0  # Increased for better coverage
        
        # Visual settings - SUN SPHERE DISABLED FOR DEBUGGING
        self.show_sun_sphere = False  # DISABLED
        self.hide_sun_sphere_with_raytracing = True
        self.show_debug_visualization = True  # Enable debug visualization
        
        # Update timers
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._deferred_update)
        
        # Track state
        self.last_sun_pos = None
        self.camera_moving = False
        self.scene_dirty = False
        
        # Initialize performance monitoring
        self._init_performance_monitoring()
        
        # Set initial complexity
        self._set_sun_complexity('medium')
        
        # Ray tracing state
        self.ray_tracing_enabled = False
        self._tried_enable_ray_tracing = False
        
        print(f"High-Performance Sun System Initialized (DEBUG MODE - Sun Sphere Disabled)")

    def _init_performance_monitoring(self):
        """Initialize performance monitoring"""
        self.fps_history = []
        self.max_fps_history = 10
        self.performance_auto_adjust = True
    
    def _ensure_ray_tracing(self, mode: str = "pathtracing"):
        """Try to enable VTK/OSPRay ray tracing via PyVista"""
        if self._tried_enable_ray_tracing:
            return

        self._tried_enable_ray_tracing = True
        try:
            self.plotter.enable_ray_tracing(mode)
            self.ray_tracing_enabled = True
            if hasattr(self.plotter.renderer, "SetUseFXAA"):
                self.plotter.renderer.SetUseFXAA(True)
            print(f"Ray tracing enabled ({mode})")
        except Exception as e:
            self.ray_tracing_enabled = False
            print(f"Ray tracing not available: {e}")
    
    def set_performance_mode(self, mode):
        """Set performance mode"""
        self.performance_mode = mode
        self._apply_performance_settings()
        
    def _apply_performance_settings(self):
        """Apply settings based on performance mode"""
        if self.performance_mode == 'performance':
            self.shadow_resolution = 'low'
            self.shadow_update_frequency = 4
            self.lod_distance_threshold = 20
            self.ambient_intensity = 0.4
            self._set_sun_complexity('low')
            
        elif self.performance_mode == 'balanced':
            self.shadow_resolution = 'medium'
            self.shadow_update_frequency = 2
            self.lod_distance_threshold = 30
            self.ambient_intensity = 0.3
            self._set_sun_complexity('medium')
            
        else:  # quality
            self.shadow_resolution = 'high'
            self.shadow_update_frequency = 1
            self.lod_distance_threshold = 50
            self.ambient_intensity = 0.25
            self._set_sun_complexity('high')

    def _set_sun_complexity(self, level):
        """Set sun visual complexity"""
        self.sun_complexity = {
            'low': {'theta': 12, 'phi': 12, 'glow_layers': 1},
            'medium': {'theta': 20, 'phi': 20, 'glow_layers': 2},
            'high': {'theta': 32, 'phi': 32, 'glow_layers': 3}
        }.get(level, {'theta': 20, 'phi': 20, 'glow_layers': 2})

    def set_building_center(self, center):
        """Set building center position"""
        self.building_center = np.array(center)
        self.scene_dirty = True

    def set_building_dimensions(self, width, length, height, roof_height=0):
        """Set building dimensions"""
        self.building_width = width
        self.building_length = length
        self.building_height = height
        self.roof_height = roof_height
        self.scene_dirty = True

    def set_building_rotation(self, rotation_angle):
        """Set building rotation angle"""
        self.building_rotation = rotation_angle
        if not self.camera_moving:
            self.update_timer.start(100)

    def register_scene_object(self, mesh, name, cast_shadow=True, receive_shadow=True):
        """Register building parts for shadow calculation"""
        if mesh and name not in self.scene_objects:
            self.scene_objects[name] = {
                'mesh': mesh,
                'name': name,
                'cast_shadow': cast_shadow,
                'receive_shadow': receive_shadow,
                'bounds': mesh.bounds if hasattr(mesh, 'bounds') else None
            }

    def register_environment_object(self, obj_type, position, height, radius=None):
        """Register trees and poles for shadow casting"""
        obj_data = {
            'type': obj_type,
            'position': np.array(position),
            'height': height,
            'radius': radius if radius else (2.0 if 'tree' in obj_type else 0.2),
            'lod_distance': np.linalg.norm(position[:2] - self.building_center[:2])
        }
        self.environment_objects.append(obj_data)
        
        current_time = time.time()
        if current_time - self.last_update_time > self.update_threshold:
            self.update_timer.start(50)
            self.last_update_time = current_time

    def clear_environment_objects(self):
        """Clear all environment objects"""
        self.environment_objects.clear()
        self._clear_shadows()
        self.shadow_cache.clear()

    def create_photorealistic_sun(self, sun_position, solar_settings=None):
        """Create optimized sun with smart rendering - DEBUG VERSION"""
        start_time = time.time()
        
        # Handle night time
        if sun_position is None:
            self._efficient_clear()
            self._clear_debug_visualization()
            self._create_night_lighting()
            print("DEBUG: Night time - no sun position")
            return
        
        self.sun_position = np.array(sun_position)
        
        # Extract or calculate sun angles
        if solar_settings:
            self.sun_elevation = solar_settings.get('sun_elevation', 45.0)
            self.sun_azimuth = solar_settings.get('sun_azimuth', 180.0)
            self.time_of_day = solar_settings.get('current_hour', 12.0)
            self.weather_factor = solar_settings.get('weather_factor', 1.0)
        else:
            self._calculate_angles_from_position()
        
        # DEBUG: Print sun position and angles
        print(f"\n{'='*60}")
        print(f"DEBUG: Sun Position Update")
        print(f"  Time: {self.time_of_day:.2f}h")
        print(f"  Sun Position: [{self.sun_position[0]:.2f}, {self.sun_position[1]:.2f}, {self.sun_position[2]:.2f}]")
        print(f"  Sun Elevation: {self.sun_elevation:.2f}°")
        print(f"  Sun Azimuth: {self.sun_azimuth:.2f}°")
        print(f"  Building Center: [{self.building_center[0]:.2f}, {self.building_center[1]:.2f}, {self.building_center[2]:.2f}]")
        
        # Calculate roof center
        roof_center = self.building_center.copy()
        roof_center[2] = self.building_center[2] + self.building_height + (self.roof_height / 2)
        print(f"  Roof Center: [{roof_center[0]:.2f}, {roof_center[1]:.2f}, {roof_center[2]:.2f}]")
        
        # Calculate sun direction vector
        sun_dir = self.sun_position - roof_center
        sun_dir_normalized = sun_dir / np.linalg.norm(sun_dir)
        print(f"  Sun Direction (normalized): [{sun_dir_normalized[0]:.3f}, {sun_dir_normalized[1]:.3f}, {sun_dir_normalized[2]:.3f}]")
        print(f"{'='*60}\n")
        
        # Check if update is needed
        if self._should_skip_update():
            return
        
        self.last_sun_pos = self.sun_position.copy()
        
        # Clear old components
        self._efficient_clear()
        self._clear_debug_visualization()
        
        # Check for night time based on elevation
        is_night = self.sun_elevation < -10
        
        if is_night:
            self._create_night_lighting()
            print("DEBUG: Night lighting applied (elevation < -10°)")
        else:
            # Enable ray tracing for quality rendering
            self._ensure_ray_tracing(mode="pathtracing" if self.performance_mode == "quality" else "scivis")
            
            # Create sun and lights
            self._create_optimized_sun_and_lights()
            
            # Add debug visualization
            if self.show_debug_visualization:
                self._create_debug_visualization()
            
            # Handle shadows
            if self.shadow_enabled and self.sun_elevation > self.min_shadow_elevation:
                if not self.ray_tracing_enabled and self._should_update_shadows():
                    self._create_optimized_shadows()
                else:
                    self._clear_shadows()
        
        # Monitor performance
        frame_time = (time.time() - start_time) * 1000
        self._update_performance_metrics(frame_time)
        
        # Emit update signal
        self.sun_updated.emit({
            'position': self.sun_position.tolist(),
            'elevation': self.sun_elevation,
            'azimuth': self.sun_azimuth,
            'intensity': self.get_solar_irradiance(),
            'performance': self.performance_mode,
            'fps': self._get_average_fps(),
            'ray_tracing': self.ray_tracing_enabled,
            'sun_sphere_visible': False,  # Always false in debug mode
            'debug_mode': True
        })
        
        if hasattr(self.plotter, 'render'):
            self.plotter.render()

    def _create_debug_visualization(self):
        """Create debug visualization showing sun direction and light paths"""
        # Clear previous debug actors
        self._clear_debug_visualization()
        
        # Use the calculated roof target if available
        if hasattr(self, 'debug_roof_target'):
            roof_target = self.debug_roof_target
        else:
            # Fallback to roof center
            roof_target = self.building_center.copy()
            roof_target[2] = self.building_center[2] + self.building_height + (self.roof_height / 2)
        
        # 1. Create line from sun to roof target (sun-facing surface)
        sun_line = pv.Line(self.sun_position, roof_target)
        sun_line_actor = self.plotter.add_mesh(
            sun_line,
            color='yellow',
            line_width=3,
            opacity=0.8,
            name='debug_sun_line'
        )
        self.debug_actors.append('debug_sun_line')
        
        # 2. Create small sphere at sun position
        sun_marker = pv.Sphere(
            radius=1.0,
            center=self.sun_position,
            theta_resolution=16,
            phi_resolution=16
        )
        sun_marker_actor = self.plotter.add_mesh(
            sun_marker,
            color='orange',
            opacity=0.9,
            lighting=False,
            name='debug_sun_marker'
        )
        self.debug_actors.append('debug_sun_marker')
        
        # 3. Create sphere at roof target (on sun-facing surface)
        roof_marker = pv.Sphere(
            radius=0.5,
            center=roof_target,
            theta_resolution=16,
            phi_resolution=16
        )
        roof_marker_actor = self.plotter.add_mesh(
            roof_marker,
            color='cyan',  # Changed to cyan to indicate surface target
            opacity=0.9,
            lighting=False,
            name='debug_roof_marker'
        )
        self.debug_actors.append('debug_roof_marker')
        
        # 4. Create arrow showing sun direction
        arrow_start = self.sun_position
        arrow_direction = roof_target - self.sun_position
        arrow_length = np.linalg.norm(arrow_direction) * 0.3
        arrow_direction_normalized = arrow_direction / np.linalg.norm(arrow_direction)
        
        arrow = pv.Arrow(
            start=arrow_start,
            direction=arrow_direction_normalized,
            scale=arrow_length,
            shaft_radius=0.2,
            tip_radius=0.4,
            tip_length=0.3
        )
        arrow_actor = self.plotter.add_mesh(
            arrow,
            color='yellow',
            opacity=0.8,
            name='debug_sun_arrow'
        )
        self.debug_actors.append('debug_sun_arrow')
        
        # 5. Add text label with sun info
        text_content = f"Sun: El={self.sun_elevation:.1f}° Az={self.sun_azimuth:.1f}°\nTarget: Roof Surface"
        self.plotter.add_text(
            text_content,
            position='upper_right',
            font_size=10,
            color='yellow',
            name='debug_sun_text'
        )
        self.debug_actors.append('debug_sun_text')
        
        print(f"DEBUG: Visualization created - Sun targeting roof surface at {roof_target}")


    def _clear_debug_visualization(self):
        """Clear debug visualization actors"""
        for actor_name in self.debug_actors:
            try:
                self.plotter.remove_actor(actor_name, reset_camera=False)
            except:
                pass
        self.debug_actors.clear()

    def _calculate_angles_from_position(self):
        """Calculate elevation and azimuth from sun position"""
        # Get position relative to building center
        rel_pos = self.sun_position - self.building_center
        
        # Calculate horizontal distance
        horizontal_dist = np.sqrt(rel_pos[0]**2 + rel_pos[1]**2)
        
        # Calculate elevation angle (angle above horizon)
        if horizontal_dist > 0:
            self.sun_elevation = np.degrees(np.arctan(rel_pos[2] / horizontal_dist))
        else:
            self.sun_elevation = 90.0 if rel_pos[2] > 0 else -90.0
        
        # Calculate azimuth angle (from north, clockwise)
        # North is +Y, East is +X in our coordinate system
        self.sun_azimuth = np.degrees(np.arctan2(rel_pos[0], rel_pos[1]))
        if self.sun_azimuth < 0:
            self.sun_azimuth += 360

    def _should_skip_update(self):
        """Check if update can be skipped"""
        if self.last_sun_pos is None:
            return False
        
        delta = np.linalg.norm(self.sun_position - self.last_sun_pos)
        if delta < 0.5 and not self.scene_dirty:
            return True
        
        current_time = time.time()
        if current_time - self.last_update_time < 0.033:
            return True
        
        self.last_update_time = current_time
        return False

    def _should_update_shadows(self):
        """Determine if shadows should be updated this frame"""
        if not self.shadow_enabled:
            return False
        
        if self.camera_moving and self.performance_mode == 'performance':
            return False
        
        self.shadow_frame_counter += 1
        if self.shadow_frame_counter >= self.shadow_update_frequency:
            self.shadow_frame_counter = 0
            return True
        
        return False

    def _efficient_clear(self):
        """Efficiently clear old components"""
        actors_to_remove = []
        
        if self.sun_actor:
            actors_to_remove.append('sun_sphere')
            self.sun_actor = None
        
        for i in range(3):
            actors_to_remove.append(f'sun_glow_{i}')
        
        for name in actors_to_remove:
            try:
                self.plotter.remove_actor(name, reset_camera=False)
            except:
                pass
        
        self.sun_glow_actors.clear()
        
        if self.current_lights:
            self.plotter.remove_all_lights()
            self.current_lights.clear()

    def _create_night_lighting(self):
        """Create simple night lighting"""
        night_light = pv.Light(
            light_type='headlight',
            intensity=0.1,
            color=[0.2, 0.25, 0.4]
        )
        self.plotter.add_light(night_light)
        self.current_lights.append(night_light)

    def _create_optimized_sun_and_lights(self):
        """Create sun and lighting - OPTIMIZED FOR FULL ROOF ILLUMINATION"""
        complexity = self.sun_complexity
        
        # ============================================
        # EASY ADJUSTMENT CONTROLS
        # ============================================
        # Multiple targets for complete roof coverage
        USE_MULTI_TARGET_LIGHTING = True  # Enable multiple target points
        ROOF_PEAK_PRIORITY = True  # Prioritize lighting the roof peak
        
        # Main target height (for debug sphere)
        TARGET_HEIGHT_RATIO = 2 # Higher to better illuminate roof
        TARGET_HORIZONTAL_OFFSET = 0.0  # Keep centered
        TARGET_SIDE_OFFSET = 0.0
        # ============================================
        
        # Calculate sun visual properties
        sun_size = 2.5 + 0.5 * np.sin(np.radians(max(0, self.sun_elevation)))
        
        # Color based on elevation
        if self.sun_elevation < 15:
            sun_color = [1.0, 0.6, 0.2]
            light_color = [1.0, 0.7, 0.5]
        elif self.sun_elevation < 30:
            sun_color = [1.0, 0.85, 0.5]
            light_color = [1.0, 0.9, 0.7]
        else:
            sun_color = [1.0, 0.95, 0.7]
            light_color = [1.0, 0.95, 0.85]
        
        # Calculate building dimensions
        ground_level = self.building_center[2] - self.building_height/2
        building_top = self.building_center[2] + self.building_height/2
        roof_peak = building_top + self.roof_height
        
        # Calculate sun direction
        sun_dir_h = np.array([
            self.sun_position[0] - self.building_center[0],
            self.sun_position[1] - self.building_center[1],
            0
        ])
        sun_dir_h_norm = sun_dir_h / (np.linalg.norm(sun_dir_h) + 0.001)
        perp_dir = np.array([-sun_dir_h_norm[1], sun_dir_h_norm[0], 0])
        
        # MAIN TARGET - For debug visualization
        height_range = roof_peak - ground_level
        target_height = ground_level + (height_range * TARGET_HEIGHT_RATIO)
        
        roof_target = np.array([
            self.building_center[0] + sun_dir_h_norm[0] * TARGET_HORIZONTAL_OFFSET,
            self.building_center[1] + sun_dir_h_norm[1] * TARGET_HORIZONTAL_OFFSET,
            target_height
        ])
        
        # Store for debug visualization
        self.debug_roof_target = roof_target
        
        # CREATE MULTIPLE STRATEGIC TARGET POINTS FOR COMPLETE ROOF COVERAGE
        roof_targets = []
        
        if USE_MULTI_TARGET_LIGHTING:
            # 1. ROOF PEAK - Most important for eliminating dark line
            peak_target = self.building_center.copy()
            peak_target[2] = roof_peak
            roof_targets.append(('peak', peak_target, 1.0))  # (name, position, intensity_multiplier)
            
            # 2. ROOF CENTER (slightly below peak)
            center_target = self.building_center.copy()
            center_target[2] = building_top + self.roof_height * 0.7
            roof_targets.append(('center', center_target, 0.8))
            
            # 3. FRONT SLOPE (sun-facing side)
            front_target = self.building_center.copy()
            front_target[0] += sun_dir_h_norm[0] * (self.building_width * 0.25)
            front_target[1] += sun_dir_h_norm[1] * (self.building_width * 0.25)
            front_target[2] = building_top + self.roof_height * 0.5
            roof_targets.append(('front', front_target, 0.7))
            
            # 4. BACK SLOPE (opposite side)
            back_target = self.building_center.copy()
            back_target[0] -= sun_dir_h_norm[0] * (self.building_width * 0.25)
            back_target[1] -= sun_dir_h_norm[1] * (self.building_width * 0.25)
            back_target[2] = building_top + self.roof_height * 0.5
            roof_targets.append(('back', back_target, 0.5))
            
            # 5. RIDGE LINE POINTS (along the peak)
            for offset in [-self.building_length/3, 0, self.building_length/3]:
                ridge_target = peak_target.copy()
                ridge_target[0] += perp_dir[0] * offset
                ridge_target[1] += perp_dir[1] * offset
                roof_targets.append((f'ridge_{offset}', ridge_target, 0.6))
        else:
            # Single target mode (fallback)
            roof_targets.append(('main', roof_target, 1.0))
        
        print(f"\n{'='*60}")
        print(f"DEBUG: Multi-Target Lighting Configuration")
        print(f"  Number of targets: {len(roof_targets)}")
        print(f"  Roof peak height: {roof_peak:.2f}")
        print(f"  Building top: {building_top:.2f}")
        for name, pos, intensity_mult in roof_targets[:5]:
            print(f"  {name:10s}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}] (intensity: {intensity_mult:.1f})")
        print(f"{'='*60}\n")
        
        # Calculate base intensity
        base_intensity = 0.8 + 0.4 * np.sin(np.radians(min(90, self.sun_elevation)))
        intensity = base_intensity * self.weather_factor * self.sun_intensity_multiplier
        
        # CREATE LIGHTS FOR EACH TARGET
        light_count = 0
        
        # 1. PRIMARY LIGHTS FOR ROOF COVERAGE
        for i, (name, target, intensity_mult) in enumerate(roof_targets):
            if i == 0 or self.performance_mode != 'performance':
                # Adjust light intensity based on target importance
                light_intensity = intensity * intensity_mult
                
                # Special handling for peak light - make it stronger
                if name == 'peak' and ROOF_PEAK_PRIORITY:
                    light_intensity *= 1.5
                
                target_light = pv.Light(
                    position=tuple(self.sun_position),
                    focal_point=tuple(target),
                    light_type='scene light',
                    intensity=light_intensity,
                    color=light_color,
                    positional=False,
                    show_actor=False
                )
                self.plotter.add_light(target_light)
                self.current_lights.append(target_light)
                light_count += 1
                
                # Add a second light from slightly different angle for peak
                if name == 'peak' and self.performance_mode == 'quality':
                    # Offset sun position slightly for soft shadows
                    offset_sun = self.sun_position.copy()
                    offset_sun[0] += 5
                    offset_sun[1] += 5
                    
                    peak_light2 = pv.Light(
                        position=tuple(offset_sun),
                        focal_point=tuple(target),
                        light_type='scene light',
                        intensity=light_intensity * 0.5,
                        color=light_color,
                        positional=False,
                        show_actor=False
                    )
                    self.plotter.add_light(peak_light2)
                    self.current_lights.append(peak_light2)
                    light_count += 1
        
        print(f"DEBUG: Created {light_count} targeted lights")
        
        # 2. ENHANCED AMBIENT LIGHT (stronger to fill shadows)
        ambient_light = pv.Light(
            light_type='headlight',
            intensity=self.ambient_intensity * 4.0,  # Increased
            color=[0.97, 0.97, 0.99]
        )
        self.plotter.add_light(ambient_light)
        self.current_lights.append(ambient_light)
        
        # 3. TOP-DOWN LIGHT (eliminates roof ridge shadows)
        if self.performance_mode in ['balanced', 'quality']:
            # Direct overhead light
            overhead_pos = self.building_center.copy()
            overhead_pos[2] = roof_peak + 50
            
            overhead_light = pv.Light(
                position=tuple(overhead_pos),
                focal_point=tuple(peak_target if USE_MULTI_TARGET_LIGHTING else roof_target),
                light_type='scene light',
                intensity=intensity * 0.6,
                color=[0.98, 0.98, 1.0],
                positional=False,
                show_actor=False
            )
            self.plotter.add_light(overhead_light)
            self.current_lights.append(overhead_light)
            print(f"DEBUG: Overhead light added to eliminate ridge shadows")
        
        # 4. GRAZING LIGHT (parallel to roof for texture)
        if self.performance_mode == 'quality':
            # Light at same height as roof, from sun direction
            grazing_pos = self.sun_position.copy()
            grazing_pos[2] = roof_peak - self.roof_height * 0.2
            
            grazing_light = pv.Light(
                position=tuple(grazing_pos),
                focal_point=tuple(peak_target if USE_MULTI_TARGET_LIGHTING else roof_target),
                light_type='scene light',
                intensity=intensity * 0.4,
                color=[1.0, 0.98, 0.95],
                positional=False,
                show_actor=False
            )
            self.plotter.add_light(grazing_light)
            self.current_lights.append(grazing_light)
            print(f"DEBUG: Grazing light added for roof texture")
        
        # 5. FILL LIGHT FROM OPPOSITE SIDE
        if self.performance_mode != 'performance':
            fill_position = self.building_center - sun_dir_h_norm * 50
            fill_position[2] = self.sun_position[2]
            
            # Target the peak to ensure it's well lit
            fill_target = peak_target if USE_MULTI_TARGET_LIGHTING else roof_target
            
            fill_light = pv.Light(
                position=tuple(fill_position),
                focal_point=tuple(fill_target),
                light_type='scene light',
                intensity=intensity * 0.6,
                color=[0.92, 0.94, 0.99],
                positional=False,
                show_actor=False
            )
            self.plotter.add_light(fill_light)
            self.current_lights.append(fill_light)
            print(f"DEBUG: Fill light added from opposite side")
        
        # 6. CAMERA LIGHT (additional fill)
        if self.performance_mode == 'quality':
            camera_light = pv.Light(
                light_type='camera light',
                intensity=0.5,
                color=[1.0, 1.0, 1.0]
            )
            self.plotter.add_light(camera_light)
            self.current_lights.append(camera_light)
        
        # 7. SPOT LIGHT FOR ROOF PEAK (Ray tracing mode)
        if self.ray_tracing_enabled and self.performance_mode == 'quality':
            spot_target = peak_target if USE_MULTI_TARGET_LIGHTING else roof_target
            
            spot_light = pv.Light(
                position=tuple(self.sun_position),
                focal_point=tuple(spot_target),
                light_type='scene light',
                intensity=intensity * 0.8,
                color=light_color,
                positional=True,
                cone_angle=80,  # Very wide to cover entire roof
                exponent=0.1,
                show_actor=False
            )
            spot_light.attenuation_values = (1, 0.00001, 0.0000001)
            self.plotter.add_light(spot_light)
            self.current_lights.append(spot_light)
            print(f"DEBUG: Wide spot light added for ray tracing")
        
        print(f"DEBUG: Total lights created: {len(self.current_lights)}")
        
        # Special handling for low sun angles
        if self.sun_elevation < 30:
            print(f"DEBUG: Low sun angle detected ({self.sun_elevation:.1f}°), adding extra roof illumination")
            
            # Add extra light specifically for the roof at low angles
            low_angle_pos = self.sun_position.copy()
            low_angle_pos[2] = max(self.sun_position[2], roof_peak + 10)
            
            low_angle_light = pv.Light(
                position=tuple(low_angle_pos),
                focal_point=tuple(peak_target if USE_MULTI_TARGET_LIGHTING else roof_target),
                light_type='scene light',
                intensity=intensity * 0.5,
                color=[1.0, 0.95, 0.9],
                positional=False,
                show_actor=False
            )
            self.plotter.add_light(low_angle_light)
            self.current_lights.append(low_angle_light)


    def _create_optimized_shadows(self):
        """Create performance-optimized shadows"""
        if self.ray_tracing_enabled:
            self._clear_shadows()
            return
        
        self._clear_shadows()
        
        # Calculate shadow direction from actual sun position
        sun_dir = self.sun_position - self.building_center
        sun_distance = np.linalg.norm(sun_dir)
        if sun_distance <= 0:
            return
        
        sun_dir = sun_dir / sun_distance
        
        # Project to ground plane
        shadow_dir = np.array([sun_dir[0], sun_dir[1], 0])
        shadow_length_2d = np.linalg.norm(shadow_dir)
        
        if shadow_length_2d > 0:
            shadow_dir = shadow_dir / shadow_length_2d
        else:
            shadow_dir = np.array([0.01, 0.01, 0])
        
        # Sort objects by distance
        sorted_objects = sorted(self.environment_objects, 
                              key=lambda x: x.get('lod_distance', 0))
        
        max_shadows = {'performance': 5, 'balanced': 10, 'quality': 20}
        max_count = max_shadows.get(self.performance_mode, 10)
        
        for i, obj in enumerate(sorted_objects[:max_count]):
            self._create_fast_shadow(obj, shadow_dir, i < 5)
        
        if self.building_height > 0:
            self._create_fast_building_shadow(shadow_dir)

    def _create_fast_shadow(self, obj, shadow_dir, high_quality=False):
        """Create optimized shadow for object"""
        pos = obj['position']
        height = obj['height']
        radius = obj['radius']
        is_tree = 'tree' in obj['type']
        
        if is_tree:
            source_height = pos[2] + height * 0.75
            shadow_radius = radius * 1.5
        else:
            source_height = pos[2] + height
            shadow_radius = radius * 2
        
        ground_z = 0.02
        height_above = source_height - ground_z
        
        if height_above <= 0 or self.sun_elevation <= 0:
            return
        
        shadow_length = height_above / np.tan(np.radians(max(1, self.sun_elevation)))
        shadow_length = min(shadow_length, 30)
        
        shadow_center = np.array([
            pos[0] - shadow_dir[0] * shadow_length * 0.5,
            pos[1] - shadow_dir[1] * shadow_length * 0.5,
            ground_z
        ])
        
        if is_tree and high_quality:
            shadow = pv.Disc(
                center=shadow_center,
                inner=0,
                outer=shadow_radius,
                normal=(0, 0, 1),
                r_res=1,
                c_res=8 if self.performance_mode == 'performance' else 12
            )
            
            stretch_factor = 1 + shadow_length / 20
            shadow.points[:, 0] = (shadow.points[:, 0] - shadow_center[0]) * stretch_factor + shadow_center[0]
        else:
            shadow = pv.Plane(
                center=shadow_center,
                direction=(0, 0, 1),
                i_size=shadow_length,
                j_size=shadow_radius * 3,
                i_resolution=1,
                j_resolution=1
            )
        
        distance_factor = min(1.0, obj.get('lod_distance', 0) / self.lod_distance_threshold)
        elevation_factor = self.sun_elevation / 90.0
        opacity = (0.3 + 0.2 * elevation_factor - 0.1 * distance_factor) * self.weather_factor
        opacity = max(0.1, min(0.6, opacity))
        
        actor = self.plotter.add_mesh(
            shadow,
            color=[0.1, 0.1, 0.12],
            opacity=opacity,
            lighting=False,
            pickable=False,
            show_edges=False,
            reset_camera=False
        )
        
        if actor:
            self.shadow_actors.append(actor)

    def _create_fast_building_shadow(self, shadow_dir):
        """Create optimized building shadow"""
        if self.sun_elevation <= 0:
            return
        
        total_height = self.building_height + self.roof_height
        shadow_length = total_height / np.tan(np.radians(max(1, self.sun_elevation)))
        shadow_length = min(shadow_length, 30)
        
        hw = self.building_width / 2
        hl = self.building_length / 2
        angle = np.radians(self.building_rotation)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        corners = [
            [-hw, -hl],
            [hw, -hl],
            [hw, hl],
            [-hw, hl]
        ]
        
        points = []
        for corner in corners:
            x = corner[0] * cos_a - corner[1] * sin_a
            y = corner[0] * sin_a + corner[1] * cos_a
            
            points.append([
                self.building_center[0] + x,
                self.building_center[1] + y,
                0.01
            ])
        
        for p in points[:4]:
            shadow_point = [
                p[0] - shadow_dir[0] * shadow_length,
                p[1] - shadow_dir[1] * shadow_length,
                0.01
            ]
            points.append(shadow_point)
        
        shadow_mesh = pv.PolyData(np.array(points))
        
        faces = np.array([4, 0, 1, 5, 4,
                         4, 1, 2, 6, 5,
                         4, 2, 3, 7, 6,
                         4, 3, 0, 4, 7])
        shadow_mesh.faces = faces
        
        elevation_factor = self.sun_elevation / 90.0
        opacity = (0.3 + 0.2 * elevation_factor) * self.weather_factor
        opacity = max(0.2, min(0.5, opacity))
        
        actor = self.plotter.add_mesh(
            shadow_mesh,
            color=[0.08, 0.08, 0.1],
            opacity=opacity,
            lighting=False,
            pickable=False,
            show_edges=False,
            reset_camera=False
        )
        
        if actor:
            self.shadow_actors.append(actor)

    def _clear_shadows(self):
        """Efficiently clear shadow actors"""
        if not self.shadow_actors:
            return
        
        for actor in self.shadow_actors:
            try:
                self.plotter.remove_actor(actor, reset_camera=False)
            except:
                pass
        self.shadow_actors.clear()

    def _update_shadows(self):
        """Update shadows"""
        if self.shadow_enabled and self.sun_elevation > self.min_shadow_elevation:
            if not self.ray_tracing_enabled:
                self._create_optimized_shadows()
            if hasattr(self.plotter, 'render'):
                self.plotter.render()

    def _deferred_update(self):
        """Deferred update for better performance"""
        self._update_shadows()
        self.scene_dirty = False

    def _update_performance_metrics(self, frame_time):
        """Update performance metrics"""
        self.fps_history.append(1000.0 / max(frame_time, 1))
        
        if len(self.fps_history) > self.max_fps_history:
            self.fps_history.pop(0)
        
        if self.performance_auto_adjust and len(self.fps_history) >= 5:
            avg_fps = self._get_average_fps()
            
            if avg_fps < 30 and self.performance_mode != 'performance':
                self.set_performance_mode('performance')
                print(f"Auto-switching to performance mode (FPS: {avg_fps:.1f})")
            elif avg_fps > 50 and self.performance_mode == 'performance':
                self.set_performance_mode('balanced')
            elif avg_fps > 60 and self.performance_mode == 'balanced':
                self.set_performance_mode('quality')

    def _get_average_fps(self):
        """Get average FPS"""
        if not self.fps_history:
            return 60.0
        return sum(self.fps_history) / len(self.fps_history)

    def update_sun_position(self, sun_position, solar_settings=None):
        """Update sun position with smart caching"""
        # Handle None position (night time)
        if sun_position is None:
            self.create_photorealistic_sun(None, solar_settings)
            return
        
        # Check cache
        cache_key = f"{sun_position[0]:.1f}_{sun_position[1]:.1f}_{sun_position[2]:.1f}"
        
        current_time = time.time()
        if cache_key in self.light_cache:
            cached_time, cached_data = self.light_cache[cache_key]
            if current_time - cached_time < 2.0:
                return
        
        self.create_photorealistic_sun(sun_position, solar_settings)
        self.light_cache[cache_key] = (current_time, True)
        
        if len(self.light_cache) > 100:
            self.light_cache.clear()

    def enable_shadows(self, enabled=True):
        """Enable or disable shadows"""
        self.shadow_enabled = enabled
        if not enabled:
            self._clear_shadows()
        else:
            self.scene_dirty = True
            self.update_timer.start(50)

    def set_shadow_quality(self, quality='medium'):
        """Set shadow rendering quality"""
        self.shadow_resolution = quality
        self.update_timer.start(50)

    def set_interactive_mode(self, interactive):
        """Set interactive mode for camera movement"""
        self.camera_moving = interactive
        
        if interactive:
            old_mode = self.performance_mode
            if old_mode != 'performance':
                self.set_performance_mode('performance')
                self._temp_performance_mode = old_mode
        else:
            if hasattr(self, '_temp_performance_mode'):
                self.set_performance_mode(self._temp_performance_mode)
                delattr(self, '_temp_performance_mode')
            
            if self.shadow_enabled:
                self.update_timer.start(100)

    def set_sun_sphere_visibility(self, visible=True):
        """Toggle sun sphere visibility"""
        self.show_sun_sphere = visible
        self.scene_dirty = True
        self.update_timer.start(50)
        print(f"DEBUG: Sun sphere visibility set to: {visible}")

    def set_hide_sun_with_raytracing(self, hide=True):
        """Set whether to automatically hide sun sphere when ray tracing is enabled"""
        self.hide_sun_sphere_with_raytracing = hide
        self.scene_dirty = True
        self.update_timer.start(50)

    def set_sun_intensity_multiplier(self, multiplier):
        """Adjust the sun intensity multiplier"""
        self.sun_intensity_multiplier = multiplier
        self.scene_dirty = True
        self.update_timer.start(50)
        print(f"DEBUG: Sun intensity multiplier set to: {multiplier}")

    def set_ambient_intensity(self, intensity):
        """Adjust ambient light intensity"""
        self.ambient_intensity = intensity
        self.scene_dirty = True
        self.update_timer.start(50)
        print(f"DEBUG: Ambient intensity set to: {intensity}")

    def toggle_debug_visualization(self, enabled=None):
        """Toggle debug visualization on/off"""
        if enabled is None:
            self.show_debug_visualization = not self.show_debug_visualization
        else:
            self.show_debug_visualization = enabled
        
        if not self.show_debug_visualization:
            self._clear_debug_visualization()
        
        self.scene_dirty = True
        self.update_timer.start(50)
        print(f"DEBUG: Debug visualization {'enabled' if self.show_debug_visualization else 'disabled'}")

    def get_solar_irradiance(self):
        """Calculate solar irradiance in W/m²"""
        if self.sun_elevation <= 0:
            return 0.0
        
        elevation_rad = np.radians(self.sun_elevation)
        
        air_mass = 1 / (np.sin(elevation_rad) + 0.50572 * (6.07995 + self.sun_elevation) ** -1.6364)
        dni = 950 * np.exp(-0.14 * air_mass)
        ghi = dni * np.sin(elevation_rad)
        
        return ghi * self.weather_factor

    def get_shadow_info(self):
        """Get information about current shadows"""
        return {
            'enabled': self.shadow_enabled,
            'ray_tracing': self.ray_tracing_enabled,
            'count': len(self.shadow_actors) if not self.ray_tracing_enabled else 'ray-traced',
            'quality': self.shadow_resolution,
            'sun_elevation': self.sun_elevation,
            'shadow_length_factor': 1.0 / np.tan(np.radians(max(1, self.sun_elevation))) if self.sun_elevation > 0 else 0,
            'sun_sphere_visible': False,  # Always false in debug mode
            'debug_mode': True
        }

    def get_performance_info(self):
        """Get performance information"""
        return {
            'mode': self.performance_mode,
            'fps': self._get_average_fps(),
            'shadows': len(self.shadow_actors),
            'lights': len(self.current_lights),
            'objects': len(self.environment_objects),
            'auto_adjust': self.performance_auto_adjust,
            'ray_tracing': self.ray_tracing_enabled,
            'sun_sphere_visible': False,  # Always false in debug mode
            'debug_visualization': self.show_debug_visualization
        }

    def destroy(self):
        """Clean up resources"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        self._efficient_clear()
        self._clear_shadows()
        self._clear_debug_visualization()
        self.environment_objects.clear()
        self.scene_objects.clear()
        self.shadow_cache.clear()
        self.light_cache.clear()
