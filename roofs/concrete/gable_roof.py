#!/usr/bin/env python3
"""
roofs/concrete/gable_roof.py - COMPLETE FIXED VERSION
Eliminated roof lines and proper sun integration
"""
from roofs.base.base_roof import BaseRoof
from roofs.base.resource_utils import resource_path
import pyvista as pv
import numpy as np
import os
from translations import _

try:
    from roofs.solar_panel_handlers.solar_panel_placement_gable import SolarPanelPlacementGable
    SOLAR_HANDLER_AVAILABLE = True
except ImportError as e:
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementGable = None

class GableRoof(BaseRoof):
    """COMPLETE FIXED: Smooth gable roof without lighting lines"""

    def __init__(self, plotter=None, dimensions=(10.0, 8.0, 4.0), theme="light", rotation_angle=0):
        if dimensions is None:
            dimensions = (10.0, 8.0, 4.0)
        
        self.length, self.width, self.height = dimensions
        self.rotation_angle = rotation_angle % 360
        self.rotation_rad = np.radians(self.rotation_angle)
        self.building_height = 3.0
        
        # Store original orientation vectors
        self.original_north_vector = np.array([0, 1, 0])
        self.original_up_vector = np.array([0, 0, 1])
        
        self.slope_width = np.sqrt((self.width / 2) ** 2 + self.height ** 2)
        self.slope_angle = np.arctan(self.height / (self.width / 2))
        
        texture_base_path = "PVmizer GEO/textures"
        self.roof_texture_path = resource_path(os.path.join(texture_base_path, "rooftile.jpg"))
        self.wall_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.brick_texture_path = resource_path(os.path.join(texture_base_path, "brick.jpg"))
        self.concrete_texture_path = resource_path(os.path.join(texture_base_path, "concrete.jpg"))
        
        # Default colors
        self.roof_color = "#A0622D"
        self.wall_color = "#E6C7A0"
        self.concrete_color = "#B0B0B0"
        
        self.building_actors = {}
        self.compass_actors = []
        self.mesh_cache = {}
        self.surface_normals_cache = {}
        self.model_tab = None
        self.solar_visualization = None
        self.solar_simulation = None
        
        # Solar panel tracking
        self.solar_panels_state = {}
        
        # Call parent init
        super().__init__(plotter, dimensions, theme)
        
        self.base_height = self.building_height
        self._find_references()
        
        # Set building center for sun system
        self._set_building_center_for_sun_system()
        
        self.initialize_roof(dimensions)
    
    def _set_building_center_for_sun_system(self):
        """Set building center in sun system for proper sun positioning"""
        try:
            building_center = [0, 0, self.building_height / 2 + self.height / 2]
            if self.sun_system and hasattr(self.sun_system, 'set_building_center'):
                self.sun_system.set_building_center(building_center)
                print(f"✅ Building center set in sun system: {building_center}")
        except Exception as e:
            print(f"⚠️ Could not set building center: {e}")
    
    def _find_references(self):
        """Find references to solar systems"""
        try:
            if hasattr(self.plotter, 'app'):
                app = self.plotter.app
                if hasattr(app, 'main_window'):
                    main_window = app.main_window
                    if hasattr(main_window, 'model_tab'):
                        self.model_tab = main_window.model_tab
                        if hasattr(self.model_tab, 'solar_visualization'):
                            self.solar_visualization = self.model_tab.solar_visualization
                        if hasattr(self.model_tab, 'solar_simulation'):
                            self.solar_simulation = self.model_tab.solar_simulation
        except:
            pass
    
    def set_solar_simulation(self, solar_sim):
        """Set reference to solar simulation"""
        self.solar_simulation = solar_sim
        if solar_sim:
            solar_sim.set_building_reference(self)
    
    def _rotate_point(self, point):
        """Rotate a point around the Z-axis"""
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
        """Rotate a vector around the Z-axis"""
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
        """Rotate multiple points around the Z-axis"""
        if self.rotation_angle == 0:
            return points
        
        rotated = []
        for point in points:
            rotated.append(self._rotate_point(point))
        return np.array(rotated)
    
    def get_current_north_vector(self):
        """Get the current north direction after rotation"""
        return self._rotate_vector(self.original_north_vector)
    
    def create_roof_geometry(self):
        """Create gable roof geometry"""
        half_length = self.length / 2
        half_width = self.width / 2
        
        roof_base_z = self.building_height
        roof_peak_z = self.building_height + self.height
        
        self.original_points = {
            'ridge_front': np.array([0, -half_length, roof_peak_z]),
            'ridge_back': np.array([0, half_length, roof_peak_z]),
            'eave_left_front': np.array([-half_width, -half_length, roof_base_z]),
            'eave_right_front': np.array([half_width, -half_length, roof_base_z]),
            'eave_left_back': np.array([-half_width, half_length, roof_base_z]),
            'eave_right_back': np.array([half_width, half_length, roof_base_z]),
            'base_left_front': np.array([-half_width, -half_length, 0]),
            'base_right_front': np.array([half_width, -half_length, 0]),
            'base_right_back': np.array([half_width, half_length, 0]),
            'base_left_back': np.array([-half_width, half_length, 0])
        }
        
        self._calculate_original_surface_normals()
        self._update_rotated_points()
        
        # Create all meshes
        self._create_all_meshes()
    
    def _calculate_original_surface_normals(self):
        """Calculate surface normals in the original coordinate system"""
        # Left slope normal
        v1 = self.original_points['eave_left_back'] - self.original_points['eave_left_front']
        v2 = self.original_points['ridge_front'] - self.original_points['eave_left_front']
        left_normal = np.cross(v1, v2)
        left_normal = left_normal / np.linalg.norm(left_normal)
        if left_normal[2] < 0:
            left_normal = -left_normal
        
        # Right slope normal  
        v1 = self.original_points['eave_right_back'] - self.original_points['eave_right_front']
        v2 = self.original_points['ridge_front'] - self.original_points['eave_right_front']
        right_normal = np.cross(v1, v2)
        right_normal = right_normal / np.linalg.norm(right_normal)
        if right_normal[2] < 0:
            right_normal = -right_normal
        
        self.original_surface_normals = {
            'left_slope': left_normal,
            'right_slope': right_normal,
            'front_wall': np.array([0, -1, 0]),
            'back_wall': np.array([0, 1, 0]),
            'left_wall': np.array([-1, 0, 0]),
            'right_wall': np.array([1, 0, 0]),
            'foundation': np.array([0, 0, 1])
        }
    
    def _update_rotated_surface_normals(self):
        """Update surface normals after rotation"""
        self.surface_normals_cache = {}
        for surface_name, original_normal in self.original_surface_normals.items():
            self.surface_normals_cache[surface_name] = self._rotate_vector(original_normal)
    
    def _update_rotated_points(self):
        """Update rotated points based on current rotation angle"""
        self.roof_points = {}
        for key in ['ridge_front', 'ridge_back', 'eave_left_front', 
                    'eave_right_front', 'eave_left_back', 'eave_right_back']:
            self.roof_points[key] = self._rotate_point(self.original_points[key])
        
        self.base_points = {}
        for key in ['base_left_front', 'base_right_front', 
                    'base_right_back', 'base_left_back']:
            self.base_points[key] = self._rotate_point(self.original_points[key])
        
        self._update_rotated_surface_normals()
    
    def _create_all_meshes(self):
        """Create all meshes and add them to the scene"""
        self._create_smooth_roof_slopes()
        self._create_walls()
        self._create_gable_triangles()
        self._add_foundation()
    
    def _safe_compute_normals(self, mesh):
        """Safely compute normals with PyVista version compatibility"""
        try:
            mesh.compute_normals(inplace=True, auto_orient_normals=True)
        except TypeError:
            try:
                mesh.compute_normals(inplace=True)
            except:
                pass
        except Exception as e:
            print(f"⚠️ Normal computation failed: {e}")
    
    def _create_smooth_roof_slopes(self):
        """FIXED: Create smooth roof slopes without grid lines"""
        # FIXED: Use simple quad faces instead of subdivision to eliminate lines
        
        # Left slope - single smooth quad
        left_slope_points = np.array([
            self.roof_points['eave_left_front'],
            self.roof_points['eave_left_back'], 
            self.roof_points['ridge_back'],
            self.roof_points['ridge_front']
        ])
        left_faces = np.array([[4, 0, 1, 2, 3]])
        self.left_slope = pv.PolyData(left_slope_points, left_faces)
        self._safe_compute_normals(self.left_slope)
        
        # Right slope - single smooth quad
        right_slope_points = np.array([
            self.roof_points['eave_right_front'],
            self.roof_points['eave_right_back'],
            self.roof_points['ridge_back'],
            self.roof_points['ridge_front']
        ])
        right_faces = np.array([[4, 0, 1, 2, 3]])
        self.right_slope = pv.PolyData(right_slope_points, right_faces)
        self._safe_compute_normals(self.right_slope)
        
        self.mesh_cache['left_slope'] = self.left_slope
        self.mesh_cache['right_slope'] = self.right_slope
        
        # Simple texture coordinates for smooth surfaces
        simple_tcoords = np.array([[0, 0], [3, 0], [3, 2], [0, 2]])
        self.left_slope.active_t_coords = simple_tcoords
        self.right_slope.active_t_coords = simple_tcoords
        
        # Load texture
        roof_texture, texture_loaded = self.load_texture_safely(
            self.roof_texture_path,
            self.roof_color
        )
        
        # Add meshes with smooth shading
        if texture_loaded:
            self.building_actors['left_slope'] = self.add_sun_compatible_mesh(
                self.left_slope,
                texture=roof_texture,
                name="left_slope",
                smooth_shading=True  # Force smooth shading
            )
            self.building_actors['right_slope'] = self.add_sun_compatible_mesh(
                self.right_slope,
                texture=roof_texture,
                name="right_slope",
                smooth_shading=True  # Force smooth shading
            )
        else:
            self.building_actors['left_slope'] = self.add_sun_compatible_mesh(
                self.left_slope,
                color=self.roof_color,
                name="left_slope",
                smooth_shading=True
            )
            self.building_actors['right_slope'] = self.add_sun_compatible_mesh(
                self.right_slope,
                color=self.roof_color,
                name="right_slope",
                smooth_shading=True
            )
        
        print("✅ Smooth roof slopes created without grid lines")
    
    def _create_walls(self):
        """Create walls with proper normals"""
        wall_vertices = []
        wall_faces = []
        vertex_offset = 0
        
        # Front wall (counter-clockwise from outside)
        wall_vertices.extend([
            self.base_points['base_left_front'],
            self.roof_points['eave_left_front'],
            self.roof_points['eave_right_front'],
            self.base_points['base_right_front']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        # Right wall
        wall_vertices.extend([
            self.base_points['base_right_front'],
            self.roof_points['eave_right_front'],
            self.roof_points['eave_right_back'],
            self.base_points['base_right_back']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        # Back wall
        wall_vertices.extend([
            self.base_points['base_right_back'],
            self.roof_points['eave_right_back'],
            self.roof_points['eave_left_back'],
            self.base_points['base_left_back']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        # Left wall
        wall_vertices.extend([
            self.base_points['base_left_back'],
            self.roof_points['eave_left_back'],
            self.roof_points['eave_left_front'],
            self.base_points['base_left_front']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        
        wall_mesh = pv.PolyData(np.array(wall_vertices))
        wall_mesh.faces = np.hstack(wall_faces)
        self._safe_compute_normals(wall_mesh)
        
        self.mesh_cache['walls'] = wall_mesh
        
        # Texture coordinates
        texture_coords = []
        for _ in range(4):  # 4 walls
            texture_coords.extend([[0, 0], [0, 1], [1, 1], [1, 0]])
        
        wall_mesh.active_t_coords = np.array(texture_coords)
        
        wall_texture, texture_loaded = self.load_texture_safely(
            self.brick_texture_path,
            self.wall_color
        )
        
        if texture_loaded:
            self.building_actors['building_walls'] = self.add_sun_compatible_mesh(
                wall_mesh,
                texture=wall_texture,
                name="building_walls"
            )
        else:
            self.building_actors['building_walls'] = self.add_sun_compatible_mesh(
                wall_mesh,
                color=self.wall_color,
                name="building_walls"
            )
    
    def _create_gable_triangles(self):
        """Create gable triangles"""
        # Front gable triangle
        front_tri_verts = np.array([
            self.roof_points['eave_left_front'],
            self.roof_points['eave_right_front'],
            self.roof_points['ridge_front']
        ])
        front_tri_faces = np.array([[3, 0, 1, 2]])
        front_gable = pv.PolyData(front_tri_verts, front_tri_faces)
        self._safe_compute_normals(front_gable)
        
        # Back gable triangle
        back_tri_verts = np.array([
            self.roof_points['eave_right_back'],
            self.roof_points['eave_left_back'],
            self.roof_points['ridge_back']
        ])
        back_tri_faces = np.array([[3, 0, 1, 2]])
        back_gable = pv.PolyData(back_tri_verts, back_tri_faces)
        self._safe_compute_normals(back_gable)
        
        self.mesh_cache['front_gable'] = front_gable
        self.mesh_cache['back_gable'] = back_gable
        
        triangle_tcoords = np.array([[0, 0], [1, 0], [0.5, 1]])
        front_gable.active_t_coords = triangle_tcoords
        back_gable.active_t_coords = triangle_tcoords
        
        wall_texture, texture_loaded = self.load_texture_safely(
            self.wall_texture_path,
            self.wall_color
        )
        
        if texture_loaded:
            self.building_actors['front_gable_triangle'] = self.add_sun_compatible_mesh(
                front_gable,
                texture=wall_texture,
                name="front_gable_triangle"
            )
            self.building_actors['back_gable_triangle'] = self.add_sun_compatible_mesh(
                back_gable,
                texture=wall_texture,
                name="back_gable_triangle"
            )
        else:
            self.building_actors['front_gable_triangle'] = self.add_sun_compatible_mesh(
                front_gable,
                color=self.wall_color,
                name="front_gable_triangle"
            )
            self.building_actors['back_gable_triangle'] = self.add_sun_compatible_mesh(
                back_gable,
                color=self.wall_color,
                name="back_gable_triangle"
            )
    
    def _add_foundation(self):
        """Add foundation"""
        foundation_height = 0.15
        foundation_extend = 0.15
        
        half_length = self.length/2 + foundation_extend
        half_width = self.width/2 + foundation_extend
        
        # Create foundation vertices
        foundation_verts_local = np.array([
            # Bottom face
            [-half_width, -half_length, -foundation_height],  # 0
            [half_width, -half_length, -foundation_height],   # 1
            [half_width, half_length, -foundation_height],    # 2
            [-half_width, half_length, -foundation_height],   # 3
            # Top face
            [-half_width, -half_length, 0.01],                # 4
            [half_width, -half_length, 0.01],                 # 5
            [half_width, half_length, 0.01],                  # 6
            [-half_width, half_length, 0.01]                  # 7
        ])
        
        # Rotate foundation vertices
        foundation_verts = self._rotate_points(foundation_verts_local)
        
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
        self._safe_compute_normals(foundation)
        
        # Texture coordinates
        n_points = len(foundation_verts)
        texture_coords = np.zeros((n_points, 2))
        
        for i in range(n_points):
            x_norm = (foundation_verts[i][0] + half_width) / (2 * half_width)
            y_norm = (foundation_verts[i][1] + half_length) / (2 * half_length)
            texture_coords[i] = [x_norm * 2, y_norm * 2]
        
        foundation.active_t_coords = texture_coords
        
        self.mesh_cache['foundation'] = foundation
        
        # Load texture and add
        concrete_texture, texture_loaded = self.load_texture_safely(
            self.concrete_texture_path,
            self.concrete_color
        )
        
        if texture_loaded:
            self.building_actors['foundation'] = self.add_sun_compatible_mesh(
                foundation,
                texture=concrete_texture,
                name="foundation"
            )
        else:
            self.building_actors['foundation'] = self.add_sun_compatible_mesh(
                foundation,
                color=self.concrete_color,
                name="foundation"
            )
        
        print("✅ Foundation created")
    
    def add_sun_compatible_mesh(self, mesh, **kwargs):
        """ENHANCED: Add mesh with better low-sun visibility"""
        kwargs['lighting'] = True
        kwargs.setdefault('smooth_shading', True)
        
        # ENHANCED material properties for better visibility at low sun
        mesh_name = kwargs.get('name', '').lower()
        
        if 'wall' in mesh_name or 'gable' in mesh_name:
            kwargs.setdefault('ambient', 0.3)   # INCREASED for low sun visibility
            kwargs.setdefault('diffuse', 0.9)   # HIGH for sun response
            kwargs.setdefault('specular', 0.1)
        elif 'roof' in mesh_name or 'slope' in mesh_name:
            kwargs.setdefault('ambient', 0.25)  # INCREASED for low sun visibility
            kwargs.setdefault('diffuse', 0.9)   # HIGH for sun response
            kwargs.setdefault('specular', 0.1)
        else:
            kwargs.setdefault('ambient', 0.3)   # INCREASED overall
            kwargs.setdefault('diffuse', 0.8)
            kwargs.setdefault('specular', 0.1)
        
        # Add mesh
        actor = self.plotter.add_mesh(mesh, **kwargs)
        
        # Register with sun system
        if self.sun_system and hasattr(self.sun_system, 'register_scene_object'):
            name = kwargs.get('name', 'unnamed')
            self.sun_system.register_scene_object(mesh, name, cast_shadow=True)
        
        return actor

    def rotate_building(self, angle_delta):
        """Rotate building and update sun system"""
        print(f"🔄 Rotating building by {angle_delta}° (current: {self.rotation_angle}°)")
        
        # Store solar panel state
        self._store_solar_panels_state()
        
        # Update rotation
        self.rotation_angle = (self.rotation_angle + angle_delta) % 360
        self.rotation_rad = np.radians(self.rotation_angle)
        
        # Update geometry points
        self._update_rotated_points()
        
        # Remove all actors
        for name in ['left_slope', 'right_slope', 'building_walls', 
                     'front_gable_triangle', 'back_gable_triangle', 'foundation']:
            try:
                self.plotter.remove_actor(name)
            except:
                pass
        
        self.building_actors.clear()
        
        # Recreate meshes
        self._create_all_meshes()
        
        # Update sun system building center
        self._set_building_center_for_sun_system()
        
        # Update solar system
        if self.solar_simulation:
            self.solar_simulation.update_for_building_rotation(self.rotation_angle)
        
        # Restore solar panels
        self._restore_solar_panels_state()
        
        # Force render
        self.plotter.render()
        
        print(f"✅ Building rotated to {self.rotation_angle}°")
    
    def _store_solar_panels_state(self):
        """Store solar panel state"""
        self.solar_panels_state = {}
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            if hasattr(self.solar_panel_handler, 'active_sides'):
                self.solar_panels_state = {
                    'active_sides': set(self.solar_panel_handler.active_sides),
                    'panel_config': getattr(self.solar_panel_handler, 'panel_config', None)
                }
    
    def _restore_solar_panels_state(self):
        """Restore solar panels"""
        if self.solar_panels_state and hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            try:
                active_sides = self.solar_panels_state.get('active_sides', set())
                self.solar_panel_handler.clear_panels()
                for side in active_sides:
                    self.solar_panel_handler.add_panels(side)
            except Exception as e:
                print(f"❌ Error restoring solar panels: {e}")
    
    def initialize_roof(self, dimensions):
        """Initialize the gable roof"""
        self.dimensions = dimensions
        
        # Create geometry
        self.create_roof_geometry()
        
        # Add rotation controls
        try:
            self._add_rotation_circle()
        except Exception as e:
            print(f"⚠️ Could not add rotation controls: {e}")
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
        except Exception as e:
            print(f"⚠️ Error setting up key bindings: {e}")
        
        # Set default camera view
        try:
            self.set_default_camera_view()
        except Exception as e:
            print(f"⚠️ Could not set camera view: {e}")
    
    def setup_roof_specific_key_bindings(self):
        """Setup key bindings"""
        # Solar panels
        if self.solar_panel_handler:
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("left"))
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("right"))
            self.plotter.add_key_event("c", self.safe_clear_panels)
            self.plotter.add_key_event("C", self.safe_clear_panels)
        
        # Rotation controls
        self.plotter.add_key_event("plus", lambda: self.rotate_building(15))
        self.plotter.add_key_event("minus", lambda: self.rotate_building(-15))
        self.plotter.add_key_event("bracketright", lambda: self.rotate_building(5))
        self.plotter.add_key_event("bracketleft", lambda: self.rotate_building(-5))
    
    def _add_rotation_circle(self):
        """Add rotation control circle"""
        radius = max(self.length, self.width) * 0.7
        
        theta = np.linspace(0, 2*np.pi, 100)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = np.zeros_like(x) + 0.01
        
        circle_points = np.column_stack([x, y, z])
        
        circle = pv.PolyData(circle_points)
        n_points = len(circle_points)
        lines = np.zeros((n_points, 3), dtype=int)
        lines[:, 0] = 2
        lines[:, 1] = np.arange(n_points)
        lines[:, 2] = np.arange(1, n_points + 1)
        lines[-1, 2] = 0
        circle.lines = lines.flatten()
        
        self.rotation_circle_actor = self.plotter.add_mesh(
            circle,
            color='orange',
            line_width=3,
            name='rotation_circle',
            opacity=0.7
        )
        
        # Add rotation handle
        handle_angle = np.radians(self.rotation_angle)
        handle_x = radius * np.sin(handle_angle)
        handle_y = -radius * np.cos(handle_angle)
        handle_z = 0.1
        
        handle = pv.Sphere(radius=0.3, center=[handle_x, handle_y, handle_z])
        self.rotation_handle_actor = self.plotter.add_mesh(
            handle,
            color='red',
            name='rotation_handle',
            pickable=True
        )
        
        self._add_compass_markers(radius)
    
    def _add_compass_markers(self, radius):
        """Add compass direction markers"""
        for actor in self.compass_actors:
            try:
                self.plotter.remove_actor(actor)
            except:
                pass
        self.compass_actors.clear()
        
        marker_offset = 1.3
        positions = {
            'N': (0, -radius * marker_offset),
            'S': (0, radius * marker_offset),
            'E': (radius * marker_offset, 0),
            'W': (-radius * marker_offset, 0)
        }
        
        for direction, (x, y) in positions.items():
            point = pv.PolyData([[x, y, 0.1]])
            actor = self.plotter.add_point_labels(
                point,
                [direction],
                font_size=20,
                text_color='black',
                show_points=False,
                name=f'compass_{direction}'
            )
            self.compass_actors.append(actor)
    
    def calculate_camera_position(self):
        """Calculate optimal camera position"""
        total_height = self.building_height + self.height
        
        base_position = np.array([self.width*1.8, -self.length*1.5, total_height*1.5])
        rotated_position = self._rotate_point(base_position)
        
        focal_point = (0, 0, total_height*0.4)
        up_vector = (0, 0, 1)
        
        return tuple(rotated_position), focal_point, up_vector
    
    def get_solar_panel_areas(self):
        """Get available solar panel areas"""
        return ["left", "right"]
    
    def get_solar_panel_handler_class(self):
        """Get solar panel handler class"""
        return SolarPanelPlacementGable if SOLAR_HANDLER_AVAILABLE else None
    
    def _get_annotation_params(self):
        """Get annotation parameters"""
        return None

    def add_attachment_points(self):
        """Add attachment points for obstacle placement"""
        try:
            if not hasattr(self, 'obstacle_count'):
                self.obstacle_count = 0
                self.obstacles = []
            
            if self.obstacle_count >= 6:
                self.update_instruction(_('maximum_obstacles_reached'))
                return False
            
            # Clear existing attachment points
            if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                self.plotter.remove_actor(self.attachment_point_actor)
                self.attachment_point_actor = None
            
            self.attachment_points = []
            self.attachment_points_occupied = {}
            self.face_normals = {}
            self.obstacle_placed_this_session = False
            
            offset_distance = 0.15
            
            roof_points = self.roof_points
            
            # Calculate normals for each roof slope
            v1_left = roof_points['eave_left_back'] - roof_points['eave_left_front']
            v2_left = roof_points['ridge_front'] - roof_points['eave_left_front']
            left_normal = np.cross(v1_left, v2_left)
            left_normal = left_normal / np.linalg.norm(left_normal)
            if left_normal[2] < 0:
                left_normal = -left_normal
            
            v1_right = roof_points['eave_right_back'] - roof_points['eave_right_front']
            v2_right = roof_points['ridge_front'] - roof_points['eave_right_front']
            right_normal = np.cross(v1_right, v2_right)
            right_normal = right_normal / np.linalg.norm(right_normal)
            if right_normal[2] < 0:
                right_normal = -right_normal
            
            grid_size = 5
            point_index = 0
            
            # Add points on left slope
            for i in range(grid_size):
                for j in range(grid_size):
                    u = 0.15 + (i / (grid_size - 1)) * 0.7
                    v = 0.15 + (j / (grid_size - 1)) * 0.7
                    
                    # Bilinear interpolation on left slope
                    p1 = roof_points['eave_left_front'] * (1-u) * (1-v)
                    p2 = roof_points['eave_left_back'] * u * (1-v)
                    p3 = roof_points['ridge_back'] * u * v
                    p4 = roof_points['ridge_front'] * (1-u) * v
                    point = p1 + p2 + p3 + p4
                    
                    offset_point = point + left_normal * offset_distance
                    self.attachment_points.append(offset_point)
                    self.face_normals[point_index] = {
                        'normal': left_normal,
                        'face': 'left',
                        'roof_point': point
                    }
                    point_index += 1
            
            # Add points on right slope
            for i in range(grid_size):
                for j in range(grid_size):
                    u = 0.15 + (i / (grid_size - 1)) * 0.7
                    v = 0.15 + (j / (grid_size - 1)) * 0.7
                    
                    # Bilinear interpolation on right slope
                    p1 = roof_points['eave_right_front'] * (1-u) * (1-v)
                    p2 = roof_points['eave_right_back'] * u * (1-v)
                    p3 = roof_points['ridge_back'] * u * v
                    p4 = roof_points['ridge_front'] * (1-u) * v
                    point = p1 + p2 + p3 + p4
                    
                    offset_point = point + right_normal * offset_distance
                    self.attachment_points.append(offset_point)
                    self.face_normals[point_index] = {
                        'normal': right_normal,
                        'face': 'right',
                        'roof_point': point
                    }
                    point_index += 1
            
            # Create occupied points dictionary
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None,
                    'normal': self.face_normals[i]['normal'],
                    'face': self.face_normals[i]['face'],
                    'roof_point': self.face_normals[i]['roof_point']
                }
            
            # Visualize attachment points
            if self.attachment_points:
                points = pv.PolyData(np.array(self.attachment_points))
                
                self.attachment_point_actor = self.plotter.add_points(
                    points,
                    color='black',
                    point_size=10,
                    render_points_as_spheres=True,
                    pickable=True
                )
                
                # Enable point picking
                self.plotter.enable_point_picking(
                    callback=self.attachment_point_clicked,
                    show_message=False,
                    pickable_window=False,
                    tolerance=0.05
                )
                
                # Update instruction
                remaining = 6 - self.obstacle_count
                display_name = self.get_translated_obstacle_name(
                    getattr(self, 'selected_obstacle_type', 'Chimney')
                )
                self.update_instruction(
                    _('click_to_place') + f" {display_name} " +
                    f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")"
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding attachment points: {e}")
            return False
    
    def attachment_point_clicked(self, point, *args):
        """Handle attachment point click for obstacle placement"""
        if hasattr(self, 'obstacle_placed_this_session') and self.obstacle_placed_this_session:
            self.update_instruction(_('obstacle_already_placed'))
            return
        
        if not hasattr(self, 'selected_obstacle_type') or not self.selected_obstacle_type:
            self.update_instruction(_('select_obstacle_type'))
            return
        
        closest_point_idx, closest_point = self.find_closest_attachment_point(point)
        
        if closest_point_idx is None:
            return
        
        if self.is_point_occupied(closest_point):
            self.update_instruction(_('point_occupied'))
            return
        
        # Get point data
        point_data = self.attachment_points_occupied.get(closest_point_idx, {})
        normal_vector = point_data.get('normal', np.array([0, 0, 1]))
        roof_point = point_data.get('roof_point')
        face = point_data.get('face')
        
        # Place obstacle
        obstacle = self.place_obstacle_at_point(
            closest_point,
            self.selected_obstacle_type,
            normal_vector=normal_vector,
            roof_point=roof_point,
            face=face
        )
        
        self.obstacles.append(obstacle)
        self.obstacle_count += 1
        self.obstacle_placed_this_session = True
        
        # Mark point as occupied
        if closest_point_idx in self.attachment_points_occupied:
            self.attachment_points_occupied[closest_point_idx]['occupied'] = True
            self.attachment_points_occupied[closest_point_idx]['obstacle'] = obstacle
        
        # Disable picking and remove points
        self.plotter.disable_picking()
        
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.plotter.remove_actor(self.attachment_point_actor)
            self.attachment_point_actor = None
        
        # Update instruction
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
