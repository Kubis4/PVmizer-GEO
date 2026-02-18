#!/usr/bin/env python3
"""
roofs/concrete/pyramid_roof.py
Complete PyramidRoof matching GableRoof structure and functionality
"""
from roofs.base.base_roof import BaseRoof
from roofs.base.resource_utils import resource_path
from roofs.roof_annotation import RoofAnnotation
from translations import _
import pyvista as pv
import numpy as np
import os

try:
    from roofs.solar_panel_handlers.solar_panel_placement_pyramid import SolarPanelPlacementPyramid
    SOLAR_HANDLER_AVAILABLE = True
except ImportError as e:
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementPyramid = None

class PyramidRoof(BaseRoof):
    """Pyramid roof with automatic shadow updates on rotation - MATCHES GABLE ROOF"""

    def __init__(self, plotter=None, dimensions=(10.0, 10.0, 5.0), theme="light", rotation_angle=0):
        if dimensions is None:
            dimensions = (10.0, 10.0, 5.0)
        
        self.length, self.width, self.height = dimensions
        self.rotation_angle = rotation_angle % 360
        self.rotation_rad = np.radians(self.rotation_angle)
        self.building_height = 3.0
        
        # Store original orientation vectors
        self.original_north_vector = np.array([0, 1, 0])
        self.original_up_vector = np.array([0, 0, 1])
        
        # Calculate slope angle
        half_diagonal = np.sqrt((self.length/2)**2 + (self.width/2)**2)
        self.slope_angle = np.arctan(self.height / half_diagonal)
        
        # Texture paths - MATCH GABLE ROOF
        texture_base_path = "textures"
        self.roof_texture_path = resource_path(os.path.join(texture_base_path, "rooftile.jpg"))
        self.wall_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.brick_texture_path = resource_path(os.path.join(texture_base_path, "brick.jpg"))
        self.concrete_texture_path = resource_path(os.path.join(texture_base_path, "concrete.jpg"))
        
        # Default colors - MATCH GABLE ROOF
        self.roof_color = "#A0622D"
        self.wall_color = "#E6C7A0"
        self.concrete_color = "#B0B0B0"
        
        # MATCH GABLE ROOF: Building actors and mesh tracking
        self.building_actors = {}
        self.compass_actors = []
        self.mesh_cache = {}
        self.surface_normals_cache = {}
        self.model_tab = None
        self.solar_visualization = None
        self.solar_simulation = None
        
        # Solar panel tracking - MATCH GABLE ROOF
        self.solar_panels_state = {}
        
        # Call parent init
        super().__init__(plotter, dimensions, theme)
        
        self.base_height = self.building_height
        self._find_references()
        
        # Set building center for sun system - MATCH GABLE ROOF
        self._set_building_center_for_sun_system()
        
        # Initialize with current rotation - MATCH GABLE ROOF
        if self.sun_system:
            self.sun_system.set_building_rotation(self.rotation_angle)
        
        self.initialize_roof(dimensions)
    
    def _set_building_center_for_sun_system(self):
        """Set building center in sun system for proper sun positioning - MATCH GABLE ROOF"""
        try:
            building_center = [0, 0, self.building_height / 2 + self.height / 2]
            if self.sun_system and hasattr(self.sun_system, 'set_building_center'):
                self.sun_system.set_building_center(building_center)
                
            # Also set initial rotation
            if self.sun_system and hasattr(self.sun_system, 'set_building_rotation'):
                self.sun_system.set_building_rotation(self.rotation_angle)
        except Exception as e:
            pass
    
    def _find_references(self):
        """Find references to solar systems - MATCH GABLE ROOF"""
        try:
            if hasattr(self.plotter, 'app'):
                app = self.plotter.app
                if hasattr(app, 'main_window') and hasattr(app.main_window, 'model_tab'):
                    self.model_tab = app.main_window.model_tab
                    if hasattr(self.model_tab, 'solar_visualization'):
                        self.solar_visualization = self.model_tab.solar_visualization
                    if hasattr(self.model_tab, 'solar_simulation'):
                        self.solar_simulation = self.model_tab.solar_simulation
        except:
            pass
    
    def set_solar_simulation(self, solar_sim):
        """Set reference to solar simulation - MATCH GABLE ROOF"""
        self.solar_simulation = solar_sim
        if solar_sim:
            solar_sim.set_building_reference(self)
    
    def _rotate_point(self, point):
        """Rotate a point around the Z-axis - MATCH GABLE ROOF"""
        if self.rotation_angle == 0:
            return point
        
        cos_angle = np.cos(self.rotation_rad)
        sin_angle = np.sin(self.rotation_rad)
        
        rotation_matrix = np.array([
            [cos_angle, -sin_angle, 0],
            [sin_angle, cos_angle, 0],
            [0, 0, 1]
        ])
        
        return np.dot(rotation_matrix, point)
    
    def _rotate_vector(self, vector):
        """Rotate a vector around the Z-axis - MATCH GABLE ROOF"""
        if self.rotation_angle == 0:
            return vector
        
        cos_angle = np.cos(self.rotation_rad)
        sin_angle = np.sin(self.rotation_rad)
        
        rotation_matrix = np.array([
            [cos_angle, -sin_angle, 0],
            [sin_angle, cos_angle, 0],
            [0, 0, 1]
        ])
        
        return np.dot(rotation_matrix, vector)
    
    def _rotate_points(self, points):
        """Rotate multiple points around the Z-axis - MATCH GABLE ROOF"""
        if self.rotation_angle == 0:
            return points
        
        rotated = []
        for point in points:
            rotated.append(self._rotate_point(point))
        return np.array(rotated)
    
    def get_current_north_vector(self):
        """Get the current north direction after rotation - MATCH GABLE ROOF"""
        return self._rotate_vector(self.original_north_vector)
    
    def create_roof_geometry(self):
        """Create pyramid roof with building base - MATCH GABLE ROOF STRUCTURE"""
        half_length = self.length / 2
        half_width = self.width / 2
        
        # Roof sits on top of building
        roof_base_z = self.building_height
        roof_peak_z = self.building_height + self.height
        
        # MATCH GABLE ROOF: Define original points structure
        overhang = 0.3  # 30cm roof overhang
        self.original_points = {
            # Roof points with overhang
            'front_left': np.array([-half_length - overhang, -half_width - overhang, roof_base_z]),
            'front_right': np.array([half_length + overhang, -half_width - overhang, roof_base_z]),
            'back_right': np.array([half_length + overhang, half_width + overhang, roof_base_z]),
            'back_left': np.array([-half_length - overhang, half_width + overhang, roof_base_z]),
            'peak': np.array([0, 0, roof_peak_z]),
            # Base points (building walls)
            'base_front_left': np.array([-half_length, -half_width, 0]),
            'base_front_right': np.array([half_length, -half_width, 0]),
            'base_back_right': np.array([half_length, half_width, 0]),
            'base_back_left': np.array([-half_length, half_width, 0])
        }
        
        self._calculate_original_surface_normals()
        self._update_rotated_points()
        
        # Create all meshes
        self._create_all_meshes()
        
        # MATCH GABLE ROOF: Register meshes with sun system for shadow casting
        self._register_meshes_with_sun_system()
        
        # Register roof faces as shadow receivers
        self._register_shadow_receivers()
    
    def _calculate_original_surface_normals(self):
        """Calculate surface normals in original orientation - MATCH GABLE ROOF"""
        # Calculate normals for pyramid faces in original orientation
        front_left = self.original_points['front_left']
        front_right = self.original_points['front_right']
        back_right = self.original_points['back_right']
        back_left = self.original_points['back_left']
        peak = self.original_points['peak']
        
        # Front face normal
        v1_front = front_right - front_left
        v2_front = peak - front_left
        front_normal = np.cross(v1_front, v2_front)
        front_normal = front_normal / np.linalg.norm(front_normal)
        
        # Right face normal
        v1_right = back_right - front_right
        v2_right = peak - front_right
        right_normal = np.cross(v1_right, v2_right)
        right_normal = right_normal / np.linalg.norm(right_normal)
        
        # Back face normal
        v1_back = back_left - back_right
        v2_back = peak - back_right
        back_normal = np.cross(v1_back, v2_back)
        back_normal = back_normal / np.linalg.norm(back_normal)
        
        # Left face normal
        v1_left = front_left - back_left
        v2_left = peak - back_left
        left_normal = np.cross(v1_left, v2_left)
        left_normal = left_normal / np.linalg.norm(left_normal)
        
        self.original_surface_normals = {
            'front_face': front_normal,
            'right_face': right_normal,
            'back_face': back_normal,
            'left_face': left_normal,
            'front_wall': np.array([0, -1, 0]),
            'right_wall': np.array([1, 0, 0]),
            'back_wall': np.array([0, 1, 0]),
            'left_wall': np.array([-1, 0, 0]),
            'foundation': np.array([0, 0, 1])
        }
    
    def _update_rotated_points(self):
        """Update points with current rotation - MATCH GABLE ROOF"""
        self.rotated_points = {}
        for name, point in self.original_points.items():
            self.rotated_points[name] = self._rotate_point(point)
        
        # Update surface normals with rotation
        self.surface_normals_cache = {}
        for name, normal in self.original_surface_normals.items():
            self.surface_normals_cache[name] = self._rotate_vector(normal)
    
    def _create_all_meshes(self):
        """Create all building meshes - MATCH GABLE ROOF"""
        # Create pyramid roof faces
        self._create_pyramid_faces()
        
        # Create building walls
        self._create_building_walls()
        
        # Create foundation
        self._create_foundation()
    
    def _create_pyramid_faces(self):
        """Create pyramid roof faces - MATCH GABLE ROOF PATTERN"""
        points = self.rotated_points
        
        # Define pyramid faces
        faces = {
            'front_face': [points['front_left'], points['front_right'], points['peak']],
            'right_face': [points['front_right'], points['back_right'], points['peak']],
            'back_face': [points['back_right'], points['back_left'], points['peak']],
            'left_face': [points['back_left'], points['front_left'], points['peak']]
        }
        
        # Load roof texture
        roof_texture, texture_loaded = self.load_texture_safely(
            self.roof_texture_path,
            self.roof_color
        )
        
        for face_name, face_vertices in faces.items():
            # Create face mesh
            face_verts = np.array(face_vertices)
            face_mesh = pv.PolyData(face_verts)
            face_mesh.faces = np.array([3, 0, 1, 2])
            
            # Set normals
            normal = self.surface_normals_cache[face_name]
            normals = np.array([normal, normal, normal])
            face_mesh.point_data['Normals'] = normals
            
            # Texture coordinates
            face_mesh.active_texture_coordinates = np.array([[0, 0], [1, 0], [0.5, 1]])
            
            # Store in cache
            self.mesh_cache[face_name] = face_mesh
            
            # Add to scene
            if texture_loaded:
                actor = self.add_sun_compatible_mesh(
                    face_mesh,
                    texture=roof_texture,
                    name=face_name,
                    smooth_shading=True
                )
            else:
                actor = self.add_sun_compatible_mesh(
                    face_mesh,
                    color=self.roof_color,
                    name=face_name,
                    smooth_shading=True
                )
            
            self.building_actors[face_name] = actor
    
    def _create_building_walls(self):
        """Create building walls - MATCH GABLE ROOF PATTERN"""
        points = self.rotated_points
        
        # Wall definitions
        wall_vertices = []
        wall_faces = []
        vertex_offset = 0
        
        walls = [
            ('front', points['base_front_left'], points['base_front_right'], 
             points['front_right'], points['front_left']),
            ('right', points['base_front_right'], points['base_back_right'], 
             points['back_right'], points['front_right']),
            ('back', points['base_back_right'], points['base_back_left'], 
             points['back_left'], points['back_right']),
            ('left', points['base_back_left'], points['base_front_left'], 
             points['front_left'], points['back_left'])
        ]
        
        for wall_name, bottom_left, bottom_right, top_right, top_left in walls:
            wall_verts = [bottom_left, bottom_right, top_right, top_left]
            wall_vertices.extend(wall_verts)
            wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
            vertex_offset += 4
        
        # Create wall mesh
        wall_mesh = pv.PolyData(np.array(wall_vertices))
        wall_mesh.faces = np.hstack(wall_faces)
        wall_mesh.compute_normals(inplace=True, auto_orient_normals=True)
        
        # Store in cache
        self.mesh_cache['building_walls'] = wall_mesh
        
        # Texture coordinates
        n_walls = len(walls)
        texture_coords = []
        for i in range(n_walls):
            texture_coords.extend([[0, 0], [3, 0], [3, 1], [0, 1]])
        wall_mesh.active_texture_coordinates = np.array(texture_coords)

        # Load texture and add
        wall_texture, texture_loaded = self.load_texture_safely(
            self.brick_texture_path,
            self.wall_color
        )
        
        if texture_loaded:
            actor = self.add_sun_compatible_mesh(
                wall_mesh,
                texture=wall_texture,
                name="building_walls"
            )
        else:
            actor = self.add_sun_compatible_mesh(
                wall_mesh,
                color=self.wall_color,
                name="building_walls"
            )
        
        self.building_actors['building_walls'] = actor
    
    def _create_foundation(self):
        """Create foundation - MATCH GABLE ROOF PATTERN"""
        foundation_height = 0.15
        foundation_extend = 0.15
        
        half_length = self.length/2 + foundation_extend
        half_width = self.width/2 + foundation_extend
        
        # Foundation vertices in original orientation
        original_verts = np.array([
            # Bottom face
            [-half_length, -half_width, -foundation_height],
            [half_length, -half_width, -foundation_height],
            [half_length, half_width, -foundation_height],
            [-half_length, half_width, -foundation_height],
            # Top face
            [-half_length, -half_width, 0.01],
            [half_length, -half_width, 0.01],
            [half_length, half_width, 0.01],
            [-half_length, half_width, 0.01]
        ])
        
        # Apply rotation
        foundation_verts = self._rotate_points(original_verts)
        
        # Create faces
        foundation_faces = np.array([
            [4, 0, 3, 2, 1],  # Bottom
            [4, 4, 5, 6, 7],  # Top
            [4, 0, 1, 5, 4],  # Front
            [4, 1, 2, 6, 5],  # Right
            [4, 2, 3, 7, 6],  # Back
            [4, 3, 0, 4, 7]   # Left
        ]).flatten()
        
        foundation = pv.PolyData(foundation_verts)
        foundation.faces = foundation_faces
        foundation.compute_normals(inplace=True, auto_orient_normals=True)
        
        # Store in cache
        self.mesh_cache['foundation'] = foundation
        
        # Texture coordinates
        n_points = len(foundation_verts)
        texture_coords = np.zeros((n_points, 2))
        for i in range(n_points):
            x_norm = (foundation_verts[i][0] + half_length) / (2 * half_length)
            y_norm = (foundation_verts[i][1] + half_width) / (2 * half_width)
            texture_coords[i] = [x_norm * 2, y_norm * 2]
        foundation.active_texture_coordinates = texture_coords

        # Load texture and add
        concrete_texture, texture_loaded = self.load_texture_safely(
            self.concrete_texture_path,
            self.concrete_color
        )
        
        if texture_loaded:
            actor = self.add_sun_compatible_mesh(
                foundation,
                texture=concrete_texture,
                name="foundation"
            )
        else:
            actor = self.add_sun_compatible_mesh(
                foundation,
                color=self.concrete_color,
                name="foundation"
            )
        
        self.building_actors['foundation'] = actor
    
    def _register_meshes_with_sun_system(self):
        """Register meshes with sun system - MATCH GABLE ROOF"""
        if not self.sun_system:
            return
        
        try:
            for name, mesh in self.mesh_cache.items():
                if mesh and hasattr(self.sun_system, 'register_scene_object'):
                    cast_shadow = 'foundation' not in name.lower()
                    self.sun_system.register_scene_object(mesh, name, cast_shadow)
        except Exception as e:
            pass
    
    def _register_shadow_receivers(self):
        """Register shadow receivers - MATCH GABLE ROOF"""
        if not self.sun_system:
            return
        
        try:
            # Register roof faces as shadow receivers
            for face_name in ['front_face', 'right_face', 'back_face', 'left_face']:
                if face_name in self.mesh_cache:
                    mesh = self.mesh_cache[face_name]
                    if hasattr(self.sun_system, 'register_shadow_receiver'):
                        self.sun_system.register_shadow_receiver(mesh, face_name)
        except Exception as e:
            pass
    
    def rotate_building(self, angle_delta):
        """Rotate building with automatic shadow updates - MATCH GABLE ROOF"""
        try:
            # Store solar panel state
            self._store_solar_panels_state()
            
            # Update rotation
            self.rotation_angle = (self.rotation_angle + angle_delta) % 360
            self.rotation_rad = np.radians(self.rotation_angle)
            
            # Remove existing actors
            for name in list(self.building_actors.keys()):
                try:
                    self.plotter.remove_actor(self.building_actors[name])
                    del self.building_actors[name]
                except:
                    pass
            
            # Clear caches
            self.mesh_cache.clear()
            
            # Recreate geometry
            self.create_roof_geometry()
            
            # Update sun system
            if self.sun_system:
                self.sun_system.set_building_rotation(self.rotation_angle)
            
            # Update sun system after changes
            self.update_sun_system_after_changes()
            
            # Restore solar panels
            self._restore_solar_panels_state()
            
            # Force render
            self.plotter.render()
            
            
        except Exception as e:
            pass
    
    def _store_solar_panels_state(self):
        """Store solar panel state - MATCH GABLE ROOF"""
        self.solar_panels_state = {}
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            if hasattr(self.solar_panel_handler, 'active_sides'):
                self.solar_panels_state = {
                    'active_sides': set(self.solar_panel_handler.active_sides),
                    'panel_config': getattr(self.solar_panel_handler, 'panel_config', None)
                }
    
    def _restore_solar_panels_state(self):
        """Restore solar panels - MATCH GABLE ROOF"""
        if hasattr(self, 'solar_panels_state') and self.solar_panels_state:
            if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                try:
                    active_sides = self.solar_panels_state.get('active_sides', set())
                    self.solar_panel_handler.clear_panels()
                    for side in active_sides:
                        self.solar_panel_handler.add_panels(side)
                except Exception as e:
                    pass
    
    def initialize_roof(self, dimensions):
        """Initialize roof - MATCH GABLE ROOF"""
        # Store dimensions
        self.dimensions = dimensions
        
        # Create roof and building geometry
        self.create_roof_geometry()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Create annotations
        try:
            annotation_params = self._get_annotation_params()
            if annotation_params:
                self.annotator = RoofAnnotation(
                    self.plotter,
                    *annotation_params,
                    self.theme
                )
                self.annotator.add_annotations()
        except Exception as e:
            self.annotator = None
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
        except Exception as e:
            pass
        
        # Set camera view
        try:
            self.set_default_camera_view()
        except Exception as e:
            pass
        
    
    def calculate_camera_position(self):
        """Calculate camera position - MATCH GABLE ROOF"""
        total_height = self.building_height + self.height
        
        # Base camera position
        base_position = np.array([self.width*2.0, -self.length*2.0, total_height*1.3])
        
        # Rotate with building
        rotated_position = self._rotate_point(base_position)
        
        focal_point = (0, 0, total_height*0.4)
        up_vector = (0, 0, 1)
        
        return tuple(rotated_position), focal_point, up_vector
    
    def setup_roof_specific_key_bindings(self):
        """Setup key bindings - MATCH GABLE ROOF"""
        try:
            # Solar panel controls
            if self.solar_panel_handler:
                self.plotter.add_key_event("1", lambda: self.safe_add_panels("front"))
                self.plotter.add_key_event("2", lambda: self.safe_add_panels("right"))
                self.plotter.add_key_event("3", lambda: self.safe_add_panels("back"))
                self.plotter.add_key_event("4", lambda: self.safe_add_panels("left"))
                self.plotter.add_key_event("c", self.safe_clear_panels)
                self.plotter.add_key_event("C", self.safe_clear_panels)
            
            # Rotation controls
            self.plotter.add_key_event("plus", lambda: self.rotate_building(15))
            self.plotter.add_key_event("minus", lambda: self.rotate_building(-15))
            self.plotter.add_key_event("bracketright", lambda: self.rotate_building(5))
            self.plotter.add_key_event("bracketleft", lambda: self.rotate_building(-5))
            
            # Arrow keys
            self.plotter.add_key_event("Left", lambda: self.rotate_building(-15))
            self.plotter.add_key_event("Right", lambda: self.rotate_building(15))
            
            
        except Exception as e:
            pass
    
    def safe_add_panels(self, side):
        """Safely add panels"""
        try:
            if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                self.solar_panel_handler.add_panels(side)
        except Exception as e:
            pass
    
    def safe_clear_panels(self):
        """Safely clear panels"""
        try:
            if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                self.solar_panel_handler.clear_panels()
        except Exception as e:
            pass
    
    def get_solar_panel_areas(self):
        """Get panel areas"""
        return ["front", "right", "back", "left"]
    
    def get_solar_panel_handler_class(self):
        """Get handler class"""
        return SolarPanelPlacementPyramid if SOLAR_HANDLER_AVAILABLE else None
    
    def _get_annotation_params(self):
        """Get annotation parameters"""
        return (self.width, self.length, self.height, self.slope_angle, True)
    
    def add_attachment_points(self):
        """Generate attachment points - MATCH GABLE ROOF PATTERN"""
        try:
            if not hasattr(self, 'obstacle_count'):
                self.obstacle_count = 0
                self.obstacles = []
            
            if not hasattr(self, 'selected_obstacle_type'):
                self.selected_obstacle_type = "Chimney"
            
            if self.obstacle_count >= 6:
                self.update_instruction(_('obstacle_max_reached'))
                return False
            
            if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                self.plotter.remove_actor(self.attachment_point_actor)
                self.attachment_point_actor = None
            
            self.attachment_points = []
            self.attachment_points_occupied = {}
            self.face_normals = {}
            self.obstacle_placed_this_session = False
            
            offset_distance = 0.15
            points = self.rotated_points
            
            peak = points['peak']
            front_left = points['front_left']
            front_right = points['front_right']
            back_left = points['back_left']
            back_right = points['back_right']
            
            # Define roof faces with normals
            self.roof_face_info = {
                'front': {
                    'normal': self.surface_normals_cache.get('front_face', np.array([0, -1, 1])),
                    'points': [front_left, front_right, peak],
                    'base_vector': front_right - front_left,
                    'slope_vector': peak - (front_left + front_right) / 2
                },
                'right': {
                    'normal': self.surface_normals_cache.get('right_face', np.array([1, 0, 1])),
                    'points': [front_right, back_right, peak],
                    'base_vector': back_right - front_right,
                    'slope_vector': peak - (front_right + back_right) / 2
                },
                'back': {
                    'normal': self.surface_normals_cache.get('back_face', np.array([0, 1, 1])),
                    'points': [back_right, back_left, peak],
                    'base_vector': back_left - back_right,
                    'slope_vector': peak - (back_right + back_left) / 2
                },
                'left': {
                    'normal': self.surface_normals_cache.get('left_face', np.array([-1, 0, 1])),
                    'points': [back_left, front_left, peak],
                    'base_vector': front_left - back_left,
                    'slope_vector': peak - (back_left + front_left) / 2
                }
            }
            
            # Normalize slope vectors
            for face_name in self.roof_face_info:
                slope_vector = self.roof_face_info[face_name]['slope_vector']
                if np.linalg.norm(slope_vector) > 0:
                    self.roof_face_info[face_name]['slope_vector'] = slope_vector / np.linalg.norm(slope_vector)
            
            # Generate points on each face
            roof_area = self.length * self.width
            
            if roof_area < 50:
                rows, cols = 3, 3
            elif roof_area < 100:
                rows, cols = 4, 4
            elif roof_area < 200:
                rows, cols = 5, 5
            else:
                rows, cols = 6, 6
            
            point_index = 0
            
            def is_point_in_triangle(point, vertices):
                v0 = vertices[2] - vertices[0]
                v1 = vertices[1] - vertices[0]
                v2 = point - vertices[0]
                
                dot00 = np.dot(v0, v0)
                dot01 = np.dot(v0, v1)
                dot02 = np.dot(v0, v2)
                dot11 = np.dot(v1, v1)
                dot12 = np.dot(v1, v2)
                
                inv_denom = 1.0 / (dot00 * dot11 - dot01 * dot01)
                u = (dot11 * dot02 - dot01 * dot12) * inv_denom
                v = (dot00 * dot12 - dot01 * dot02) * inv_denom
                
                return (u >= 0) and (v >= 0) and (u + v <= 1)
            
            for face_name, face_info in self.roof_face_info.items():
                normal = face_info['normal']
                face_points = face_info['points']
                base_vector = face_info['base_vector']
                base_length = np.linalg.norm(base_vector)
                base_unit = base_vector / base_length if base_length > 0 else np.array([1, 0, 0])
                
                base_mid = (face_points[0] + face_points[1]) / 2
                peak_distance = np.linalg.norm(peak - base_mid)
                
                slope_unit = face_info['slope_vector']
                
                slope_min, slope_max = 0.15, 0.85
                base_min, base_max = -0.4, 0.4
                
                for row in range(rows):
                    slope_pct = slope_min + (row / (rows - 1)) * (slope_max - slope_min) if rows > 1 else 0.5
                    
                    width_scale = 1.0 - (slope_pct - slope_min) * 0.5
                    effective_cols = max(2, int(cols * width_scale))
                    
                    for col in range(effective_cols):
                        if effective_cols == 1:
                            base_pct = 0
                        else:
                            base_range = (base_min * width_scale, base_max * width_scale)
                            base_pct = base_range[0] + (col / (effective_cols - 1)) * (base_range[1] - base_range[0])
                        
                        slope_position = base_mid + slope_unit * (slope_pct * peak_distance)
                        horz_offset = base_unit * (base_pct * base_length)
                        point = slope_position + horz_offset
                        
                        if is_point_in_triangle(point, face_points):
                            offset_point = point + normal * offset_distance
                            
                            self.attachment_points.append(offset_point)
                            self.face_normals[point_index] = {
                                'normal': normal,
                                'face': face_name,
                                'roof_point': point
                            }
                            point_index += 1
            
            # Create occupied points dict
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None,
                    'normal': self.face_normals[i]['normal'] if i in self.face_normals else None,
                    'face': self.face_normals[i]['face'] if i in self.face_normals else None,
                    'roof_point': self.face_normals[i]['roof_point'] if i in self.face_normals else None
                }
            
            # Add points to scene
            if self.attachment_points:
                points_mesh = pv.PolyData(np.array(self.attachment_points))
                
                self.attachment_point_actor = self.plotter.add_points(
                    points_mesh,
                    color='black',
                    point_size=10,
                    render_points_as_spheres=True,
                    pickable=False,
                    lighting=False  # No lighting = no shadow casting
                )
                
                self._setup_roof_obstacle_click()
                
                if not hasattr(self, 'placement_instruction') or not self.placement_instruction:
                    remaining = 6 - self.obstacle_count
                    display_name = self.get_translated_obstacle_name(self.selected_obstacle_type)
                    self.update_instruction(
                        _('click_to_place') + f" {display_name} " +
                        f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")"
                    )
            
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def attachment_point_clicked(self, point_index_or_coords):
        """Handle attachment point clicks - MATCH GABLE ROOF"""
        try:
            if isinstance(point_index_or_coords, np.ndarray):
                point_index = self.find_closest_attachment_point_index(point_index_or_coords)
            else:
                point_index = point_index_or_coords
            
            if hasattr(self, 'obstacle_placed_this_session') and self.obstacle_placed_this_session:
                self.update_instruction(_('obstacle_already_placed'))
                return
            
            if point_index is None or point_index not in self.attachment_points_occupied:
                self.update_instruction(_("Invalid attachment point selected"))
                return
            
            if self.attachment_points_occupied[point_index]['occupied']:
                self.update_instruction(_("This point already has an obstacle"))
                return
            
            point_data = self.attachment_points_occupied[point_index]
            position = point_data['position']
            normal = point_data['normal']
            face = point_data['face']
            roof_point = point_data['roof_point']
            
            obstacle_type = getattr(self, 'selected_obstacle_type', "Chimney")
            
            obstacle = self.place_obstacle_at_point(
                position,
                obstacle_type,
                normal_vector=normal,
                roof_point=roof_point,
                face=face
            )
            
            if obstacle:
                if not hasattr(self, 'obstacles'):
                    self.obstacles = []
                self.obstacles.append(obstacle)
                
                self.obstacle_count += 1
                
                self.attachment_points_occupied[point_index]['occupied'] = True
                self.attachment_points_occupied[point_index]['obstacle'] = obstacle
                
                self.obstacle_placed_this_session = True
                
                if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                    self.plotter.remove_actor(self.attachment_point_actor)
                    self.attachment_point_actor = None
                
                self._remove_roof_obstacle_click()
                try:
                    self.plotter.disable_picking()
                except Exception:
                    pass

                remaining = 6 - self.obstacle_count
                if remaining > 0:
                    display_name = self.get_translated_obstacle_name(self.selected_obstacle_type)
                    self.update_instruction(
                        f"{display_name} " + _('placed') +
                        f" ({self.obstacle_count}/6, {remaining} " + _('remaining') + "). " +
                        _('press_add_obstacle')
                    )
                else:
                    self.update_instruction(_('obstacle_max_reached') + " (6/6)")
                
                # Update solar panels
                if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                    if hasattr(self.solar_panel_handler, 'active_sides'):
                        active_sides = list(self.solar_panel_handler.active_sides)
                        for side in active_sides:
                            self.solar_panel_handler.remove_panels_from_side(side)
                            self.solar_panel_handler.add_panels(side)
            else:
                self.update_instruction(_("Failed to add obstacle. Try a different location."))
                
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def find_closest_attachment_point_index(self, clicked_position):
        """Find closest attachment point - MATCH GABLE ROOF"""
        try:
            if not hasattr(self, 'attachment_points_occupied') or not self.attachment_points_occupied:
                return None
            
            min_distance = float('inf')
            closest_index = None
            
            for idx, point_data in self.attachment_points_occupied.items():
                point = point_data['position']
                distance = np.linalg.norm(point - clicked_position)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_index = idx
            
            return closest_index
        except Exception as e:
            return None
