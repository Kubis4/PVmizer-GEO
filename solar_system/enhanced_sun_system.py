#!/usr/bin/env python3
"""
enhanced_sun_system.py - Complete working sun system with rotation support
"""
import numpy as np
import pyvista as pv
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time

class EnhancedRealisticSunSystem(QObject):
    """Sun system with dynamic shadows and rotation support"""
    
    sun_updated = pyqtSignal(dict)
    
    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        
        self.sun_actor = None
        self.shadow_actor = None
        self.current_lights = []
        self.all_shadow_actors = []
        
        self.sun_position = np.array([50, 0, 50])
        self.sun_elevation = 45.0
        self.sun_azimuth = 180.0
        self.time_of_day = 12.0
        self.weather_factor = 1.0
        
        self.building_height = 3.0
        self.roof_height = 4.0
        self.building_width = 8.0
        self.building_length = 10.0
        self.building_center = np.array([0, 0, 1.5])
        self.building_rotation = 0
        
        self.scene_objects = {}
        self.environment_objects = []
        
        self.shadow_enabled = True
        self.min_shadow_elevation = 10.0
        self.shadow_height_offset = 0.05
        
        self.update_cooldown = 0.3
        self.last_update_time = 0
        self.updating = False
        
        self.rotation_timer = QTimer()
        self.rotation_timer.setSingleShot(True)
        self.rotation_timer.timeout.connect(self._perform_shadow_update)
        self.pending_rotation = None

    def set_building_center(self, center):
        self.building_center = np.array(center)

    def set_building_dimensions(self, width, length, height, roof_height=0):
        self.building_width = width
        self.building_length = length
        self.building_height = height
        self.roof_height = roof_height

    def set_building_rotation(self, rotation_angle):
        """Set building rotation and schedule shadow update"""
        self.building_rotation = rotation_angle
        self.pending_rotation = rotation_angle
        
        self.rotation_timer.stop()
        self.rotation_timer.start(100)

    def update_for_building_rotation(self, rotation_angle):
        """Alternative method for rotation update"""
        self.building_rotation = rotation_angle
        self._update_shadows_only()

    def register_scene_object(self, mesh, name, cast_shadow=True):
        if cast_shadow and mesh:
            self.scene_objects[name] = {
                'mesh': mesh,
                'cast_shadow': cast_shadow
            }

    def register_environment_object(self, obj_type, position, height, radius=None):
        """Register trees and poles for shadow casting"""
        env_obj = {
            'type': obj_type,
            'position': np.array(position),
            'height': height,
            'radius': radius if radius else 0.5
        }
        self.environment_objects.append(env_obj)
        
        if self.shadow_enabled:
            self._update_shadows_only()

    def clear_environment_objects(self):
        """Clear all registered environment objects"""
        self.environment_objects.clear()

    def _perform_shadow_update(self):
        """Perform shadow update after debounce"""
        if self.pending_rotation is not None:
            self.building_rotation = self.pending_rotation
            self.pending_rotation = None
            self._update_shadows_only()

    def _update_shadows_only(self):
        """Update only shadows without touching lights"""
        if not self.shadow_enabled or self.sun_elevation < self.min_shadow_elevation:
            return
        
        try:
            if self.shadow_actor:
                try:
                    self.plotter.remove_actor('dynamic_shadow')
                except:
                    pass
                self.shadow_actor = None
            
            for actor in self.all_shadow_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.all_shadow_actors.clear()
            
            for i in range(20):
                try:
                    self.plotter.remove_actor(f'shadow_part_{i}')
                    self.plotter.remove_actor(f'env_shadow_{i}')
                except:
                    pass
            
            self._create_dynamic_building_shadow()
            self._create_environment_shadows()
            
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
        except:
            pass

    def create_photorealistic_sun(self, sun_position, solar_settings=None):
        current_time = time.time()
        
        if current_time - self.last_update_time < self.update_cooldown:
            return
        
        if self.updating:
            return
            
        self.updating = True
        self.last_update_time = current_time
        
        try:
            self.sun_position = np.array(sun_position)
            
            if solar_settings:
                self.sun_elevation = solar_settings.get('sun_elevation', 45.0)
                self.sun_azimuth = solar_settings.get('sun_azimuth', 180.0)
                self.time_of_day = solar_settings.get('current_hour', 12.0)
                self.weather_factor = solar_settings.get('weather_factor', 1.0)
            else:
                self._calculate_sun_angles_from_position()
            
            self._clear_all_elements()
            
            is_night = self.sun_elevation < -10 or (self.time_of_day < 4 or self.time_of_day > 22)
            
            if is_night:
                self._create_night_scene()
            else:
                if self.sun_elevation > -5:
                    self._create_sun_sphere()
                
                self._create_balanced_lighting()
                
                if self.shadow_enabled and self.sun_elevation >= self.min_shadow_elevation:
                    self._create_dynamic_building_shadow()
                    self._create_environment_shadows()
            
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
        except:
            pass
        finally:
            self.updating = False

    def _calculate_sun_angles_from_position(self):
        horizontal_dist = np.sqrt(self.sun_position[0]**2 + self.sun_position[1]**2)
        
        if horizontal_dist > 0:
            self.sun_elevation = np.degrees(np.arctan2(self.sun_position[2], horizontal_dist))
        else:
            self.sun_elevation = 90.0 if self.sun_position[2] > 0 else -90.0
        
        self.sun_azimuth = np.degrees(np.arctan2(self.sun_position[1], self.sun_position[0]))

    def _clear_all_elements(self):
        if self.sun_actor:
            try:
                self.plotter.remove_actor('sun_sphere')
            except:
                pass
            self.sun_actor = None
        
        if self.shadow_actor:
            try:
                self.plotter.remove_actor('dynamic_shadow')
            except:
                pass
            self.shadow_actor = None
        
        for actor in self.all_shadow_actors:
            try:
                self.plotter.remove_actor(actor)
            except:
                pass
        self.all_shadow_actors.clear()
        
        for i in range(20):
            try:
                self.plotter.remove_actor(f'shadow_part_{i}')
                self.plotter.remove_actor(f'env_shadow_{i}')
            except:
                pass
        
        self.plotter.remove_all_lights()
        self.current_lights.clear()

    def _create_night_scene(self):
        night_light = pv.Light(
            light_type='cameralight',
            intensity=0.08,
            color=[0.2, 0.25, 0.4]
        )
        self.plotter.add_light(night_light)
        self.current_lights.append(night_light)

    def _create_sun_sphere(self):
        sun_sphere = pv.Sphere(
            radius=2.5,
            center=self.sun_position,
            phi_resolution=16,
            theta_resolution=16
        )
        
        if self.sun_elevation < 15:
            sun_color = [1.0, 0.6, 0.3]
        elif self.sun_elevation < 30:
            sun_color = [1.0, 0.8, 0.5]
        else:
            sun_color = [1.0, 0.95, 0.7]
        
        self.sun_actor = self.plotter.add_mesh(
            sun_sphere,
            color=sun_color,
            opacity=0.9,
            lighting=False,
            name='sun_sphere'
        )

    def _create_balanced_lighting(self):
        if self.sun_elevation <= 0:
            base_intensity = 0.15
        elif self.sun_elevation < 15:
            base_intensity = 0.4
        elif self.sun_elevation < 30:
            base_intensity = 0.6
        else:
            elevation_factor = np.sin(np.radians(min(90, self.sun_elevation)))
            base_intensity = 0.8 + elevation_factor * 0.4
        
        base_intensity *= self.weather_factor
        
        primary_sun = pv.Light(
            position=tuple(self.sun_position),
            focal_point=tuple(self.building_center),
            light_type='scenelight',
            intensity=base_intensity * 1.5,
            color=[1.0, 0.95, 0.85] if self.sun_elevation > 20 else [1.0, 0.75, 0.5],
            positional=True,
            cone_angle=90,
            show_actor=False,
            attenuation_values=(1, 0, 0)
        )
        self.plotter.add_light(primary_sun)
        self.current_lights.append(primary_sun)
        
        wide_light = pv.Light(
            position=tuple(self.sun_position * 0.8),
            focal_point=(0, 0, 0),
            light_type='scenelight',
            intensity=base_intensity * 0.5,
            color=[0.95, 0.95, 0.9],
            positional=True,
            cone_angle=140,
            show_actor=False
        )
        self.plotter.add_light(wide_light)
        self.current_lights.append(wide_light)
        
        ambient_light = pv.Light(
            light_type='cameralight',
            intensity=0.25 + 0.1 * self.weather_factor,
            color=[0.85, 0.88, 0.92]
        )
        self.plotter.add_light(ambient_light)
        self.current_lights.append(ambient_light)

    def _create_dynamic_building_shadow(self):
        try:
            building_outline = self._extract_building_outline()
            
            if not building_outline:
                self._create_parametric_shadow()
                return
            
            sun_ray = (self.sun_position - self.building_center)
            sun_ray_normalized = sun_ray / np.linalg.norm(sun_ray)
            
            shadow_mesh = self._project_outline_shadow(building_outline, sun_ray_normalized)
            
            if shadow_mesh:
                shadow_color = self._get_realistic_shadow_color()
                shadow_opacity = self._get_shadow_opacity()
                
                self.shadow_actor = self.plotter.add_mesh(
                    shadow_mesh,
                    color=shadow_color,
                    opacity=shadow_opacity,
                    lighting=False,
                    name='dynamic_shadow',
                    pickable=False,
                    show_edges=False,
                    render=True
                )
                
                if self.shadow_actor:
                    self.all_shadow_actors.append(self.shadow_actor)
                    self._add_soft_shadow_edges(shadow_mesh, shadow_color, shadow_opacity)
            
        except:
            self._create_parametric_shadow()

    def _create_environment_shadows(self):
        """Create shadows for trees and poles"""
        try:
            for idx, env_obj in enumerate(self.environment_objects):
                obj_type = env_obj['type']
                position = env_obj['position']
                height = env_obj['height']
                radius = env_obj.get('radius', 0.5)
                
                sun_dir_h = np.array([self.sun_position[0], self.sun_position[1]])
                if np.linalg.norm(sun_dir_h) > 0:
                    shadow_dir = -sun_dir_h / np.linalg.norm(sun_dir_h)
                else:
                    shadow_dir = np.array([1, 0])
                
                elevation_rad = np.radians(max(10, self.sun_elevation))
                shadow_length = height / np.tan(elevation_rad)
                shadow_length = min(shadow_length, 15.0)
                
                shadow_center = np.array([
                    position[0] + shadow_dir[0] * shadow_length * 0.5,
                    position[1] + shadow_dir[1] * shadow_length * 0.5,
                    self.shadow_height_offset
                ])
                
                if 'tree' in obj_type:
                    shadow_radius = radius * (1 + shadow_length / 10)
                    shadow_mesh = pv.Disc(
                        center=shadow_center,
                        inner=0,
                        outer=shadow_radius,
                        normal=(0, 0, 1),
                        r_res=1,
                        c_res=20
                    )
                else:
                    shadow_plane = pv.Plane(
                        center=shadow_center,
                        direction=(0, 0, 1),
                        i_size=shadow_length,
                        j_size=radius * 4,
                        i_resolution=10,
                        j_resolution=5
                    )
                    angle = np.degrees(np.arctan2(shadow_dir[1], shadow_dir[0]))
                    shadow_plane.rotate_z(angle, point=shadow_center, inplace=True)
                    shadow_mesh = shadow_plane
                
                shadow_opacity = self._get_shadow_opacity() * 0.6
                actor = self.plotter.add_mesh(
                    shadow_mesh,
                    color=[0.1, 0.1, 0.12],
                    opacity=shadow_opacity,
                    lighting=False,
                    name=f'env_shadow_{idx}',
                    pickable=False,
                    show_edges=False
                )
                
                if actor:
                    self.all_shadow_actors.append(actor)
        except:
            pass

    def _extract_building_outline(self):
        try:
            outline_points = []
            
            building_meshes = []
            for name, obj_data in self.scene_objects.items():
                if any(key in name.lower() for key in ['wall', 'roof', 'slope', 'gable']):
                    if obj_data['mesh']:
                        building_meshes.append(obj_data['mesh'])
            
            if not building_meshes:
                return None
            
            for mesh in building_meshes:
                if hasattr(mesh, 'points'):
                    points = mesh.points
                    
                    z_levels = [0, self.building_height, self.building_height + self.roof_height]
                    
                    for z_level in z_levels:
                        height_points = points[np.abs(points[:, 2] - z_level) < 0.5]
                        
                        if len(height_points) > 0:
                            if len(height_points) >= 3:
                                xy_points = height_points[:, :2]
                                
                                min_x, max_x = np.min(xy_points[:, 0]), np.max(xy_points[:, 0])
                                min_y, max_y = np.min(xy_points[:, 1]), np.max(xy_points[:, 1])
                                
                                outline_points.append({
                                    'height': z_level,
                                    'bounds': [(min_x, min_y), (max_x, min_y), 
                                              (max_x, max_y), (min_x, max_y)]
                                })
            
            return outline_points if outline_points else None
            
        except:
            return None

    def _project_outline_shadow(self, outline, sun_ray):
        try:
            elevation_rad = np.radians(max(5, self.sun_elevation))
            
            shadow_vertices = []
            
            for level_data in outline:
                height = level_data['height']
                bounds = level_data['bounds']
                
                if height > 0:
                    shadow_distance = height / np.tan(elevation_rad)
                    shadow_distance = min(shadow_distance, 30.0)
                    
                    for point in bounds:
                        ground_point = [point[0], point[1], self.shadow_height_offset]
                        shadow_vertices.append(ground_point)
                        
                        projected_x = point[0] - sun_ray[0] * shadow_distance
                        projected_y = point[1] - sun_ray[1] * shadow_distance
                        projected_point = [projected_x, projected_y, self.shadow_height_offset]
                        shadow_vertices.append(projected_point)
            
            if not shadow_vertices:
                return None
            
            vertices = np.array(shadow_vertices)
            shadow_mesh = pv.PolyData(vertices)
            shadow_mesh = shadow_mesh.delaunay_2d()
            
            return shadow_mesh
            
        except:
            return None

    def _create_parametric_shadow(self):
        try:
            sun_dir_h = np.array([self.sun_position[0], self.sun_position[1]])
            if np.linalg.norm(sun_dir_h) > 0:
                shadow_dir = -sun_dir_h / np.linalg.norm(sun_dir_h)
            else:
                shadow_dir = np.array([1, 0])
            
            elevation_rad = np.radians(max(10, self.sun_elevation))
            total_height = self.building_height + self.roof_height
            shadow_length = total_height / np.tan(elevation_rad)
            shadow_length = min(shadow_length, 25.0)
            
            rotation_rad = np.radians(self.building_rotation)
            cos_r = np.cos(rotation_rad)
            sin_r = np.sin(rotation_rad)
            
            half_width = self.building_width / 2
            half_length = self.building_length / 2
            
            corners = [
                [-half_width, -half_length],
                [half_width, -half_length],
                [half_width, half_length],
                [-half_width, half_length]
            ]
            
            rotated_corners = []
            for corner in corners:
                rot_x = corner[0] * cos_r - corner[1] * sin_r
                rot_y = corner[0] * sin_r + corner[1] * cos_r
                rotated_corners.append([
                    self.building_center[0] + rot_x,
                    self.building_center[1] + rot_y,
                    self.shadow_height_offset
                ])
            
            shadow_points = []
            shadow_points.extend(rotated_corners)
            
            for corner in rotated_corners:
                projected = [
                    corner[0] + shadow_dir[0] * shadow_length,
                    corner[1] + shadow_dir[1] * shadow_length,
                    self.shadow_height_offset
                ]
                shadow_points.append(projected)
            
            vertices = np.array(shadow_points)
            shadow_mesh = pv.PolyData(vertices[:4])
            shadow_mesh.faces = np.array([4, 0, 1, 2, 3])
            
            extended_mesh = pv.PolyData(vertices[4:8])
            extended_mesh.faces = np.array([4, 0, 1, 2, 3])
            
            combined_shadow = shadow_mesh + extended_mesh
            
            shadow_color = self._get_realistic_shadow_color()
            shadow_opacity = self._get_shadow_opacity()
            
            self.shadow_actor = self.plotter.add_mesh(
                combined_shadow,
                color=shadow_color,
                opacity=shadow_opacity,
                lighting=False,
                name='dynamic_shadow',
                pickable=False,
                show_edges=False
            )
            
            if self.shadow_actor:
                self.all_shadow_actors.append(self.shadow_actor)
            
        except:
            pass

    def _get_realistic_shadow_color(self):
        if self.time_of_day < 7:
            return [0.08, 0.08, 0.12]
        elif self.time_of_day < 10:
            return [0.09, 0.08, 0.11]
        elif self.time_of_day < 16:
            return [0.10, 0.10, 0.11]
        elif self.time_of_day < 19:
            return [0.11, 0.09, 0.08]
        else:
            return [0.07, 0.07, 0.10]

    def _get_shadow_opacity(self):
        if self.sun_elevation > 60:
            return 0.25
        elif self.sun_elevation > 45:
            return 0.35
        elif self.sun_elevation > 30:
            return 0.45
        else:
            return 0.55

    def _add_soft_shadow_edges(self, base_mesh, color, base_opacity):
        try:
            soft_params = [
                {'scale': 1.05, 'opacity': base_opacity * 0.3, 'offset': 0.04},
                {'scale': 1.1, 'opacity': base_opacity * 0.15, 'offset': 0.03}
            ]
            
            for i, params in enumerate(soft_params):
                soft_mesh = base_mesh.copy()
                center = soft_mesh.center
                soft_mesh.points = (soft_mesh.points - center) * params['scale'] + center
                soft_mesh.points[:, 2] = params['offset']
                
                actor = self.plotter.add_mesh(
                    soft_mesh,
                    color=[c * 1.2 for c in color],
                    opacity=params['opacity'],
                    lighting=False,
                    name=f'shadow_part_{i+1}',
                    pickable=False,
                    show_edges=False
                )
                
                if actor:
                    self.all_shadow_actors.append(actor)
        except:
            pass

    def update_sun_position(self, sun_position, solar_settings=None):
        self.create_photorealistic_sun(sun_position, solar_settings)

    def enable_shadows(self, enabled=True):
        self.shadow_enabled = enabled
        if not enabled:
            for actor in self.all_shadow_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.all_shadow_actors.clear()

    def get_solar_irradiance(self):
        if self.sun_elevation <= 0:
            return 0.0
        
        solar_constant = 1000.0
        elevation_factor = np.sin(np.radians(self.sun_elevation))
        return solar_constant * elevation_factor * self.weather_factor

    def set_shadow_height(self, height):
        self.shadow_height_offset = height

    def set_interactive_mode(self, interactive):
        """Set interactive mode for smoother updates"""
        self.update_cooldown = 0.5 if interactive else 0.3

    def destroy(self):
        if hasattr(self, 'rotation_timer'):
            self.rotation_timer.stop()
        self._clear_all_elements()
        self.scene_objects.clear()
        self.environment_objects.clear()
