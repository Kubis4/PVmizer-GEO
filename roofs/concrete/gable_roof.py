#!/usr/bin/env python3
"""
roofs/concrete/gable_roof.py
Optimized GableRoof with proper shadow system integration
"""
from roofs.base.base_roof import BaseRoof
from roofs.base.resource_utils import resource_path
from translations import _
import pyvista as pv
import numpy as np
import os

try:
    from roofs.solar_panel_handlers.solar_panel_placement_gable import SolarPanelPlacementGable
    SOLAR_HANDLER_AVAILABLE = True
except ImportError as e:
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementGable = None

class GableRoof(BaseRoof):
    """Optimized gable roof with shadow system integration"""
    
    def __init__(self, plotter=None, dimensions=(10.0, 8.0, 4.0), theme="light", rotation_angle=0):
        """Initialize gable roof with complete building"""
        if dimensions is None:
            dimensions = (10.0, 8.0, 4.0)
        
        self.length, self.width, self.height = dimensions
        self.rotation_angle = rotation_angle % 360
        self.rotation_rad = np.radians(self.rotation_angle)
        self.building_height = 3.0
        
        self.slope_width = np.sqrt((self.width / 2) ** 2 + self.height ** 2)
        self.slope_angle = np.arctan(self.height / (self.width / 2))
        
        texture_base_path = "PVmizer GEO/textures"
        self.roof_texture_path = resource_path(os.path.join(texture_base_path, "rooftile.jpg"))
        self.wall_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.brick_texture_path = resource_path(os.path.join(texture_base_path, "brick.jpg"))
        self.concrete_texture_path = resource_path(os.path.join(texture_base_path, "concrete.jpg"))
        
        self.roof_color = "#8B4513"
        self.wall_color = "#DEB887"
        self.concrete_color = "#808080"
        
        self.building_actors = {}
        self.compass_actors = []
        self.mesh_cache = {}
        self.model_tab = None  # Reference to model tab for solar system updates
        self.solar_visualization = None  # Direct reference to solar visualization
        
        super().__init__(plotter, dimensions, theme)
        
        self.base_height = self.building_height
        self._setup_lighting()
        self._find_references()  # Find references to model tab and solar visualization
        self.initialize_roof(dimensions)
    
    def _find_references(self):
        """Find references to model tab and solar visualization through plotter"""
        try:
            if hasattr(self.plotter, 'app'):
                app = self.plotter.app
                if hasattr(app, 'main_window'):
                    main_window = app.main_window
                    if hasattr(main_window, 'model_tab'):
                        self.model_tab = main_window.model_tab
                        # Try to get direct reference to solar visualization
                        if hasattr(self.model_tab, 'solar_visualization'):
                            self.solar_visualization = self.model_tab.solar_visualization
        except:
            self.model_tab = None
            self.solar_visualization = None
    
    def _rotate_point(self, point):
        """Rotate a point around the Z-axis by the building's rotation angle"""
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
    
    def _rotate_points(self, points):
        """Rotate multiple points around the Z-axis"""
        if self.rotation_angle == 0:
            return points
        
        rotated = []
        for point in points:
            rotated.append(self._rotate_point(point))
        return np.array(rotated)
    
    def _setup_lighting(self):
        """Setup realistic lighting"""
        try:
            self.plotter.remove_all_lights()
            
            sun = pv.Light()
            sun.position = (20, -20, 30)
            sun.focal_point = (0, 0, self.building_height/2)
            sun.intensity = 0.7
            sun.color = [1.0, 0.95, 0.8]
            self.plotter.add_light(sun)
            
            ambient = pv.Light()
            ambient.position = (-10, 10, 20)
            ambient.focal_point = (0, 0, self.building_height/2)
            ambient.intensity = 0.3
            ambient.color = [0.9, 0.9, 1.0]
            self.plotter.add_light(ambient)
        except Exception as e:
            pass
    
    def create_roof_geometry(self):
        """Create gable roof CENTERED with rotation for real-world orientation"""
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
        
        self._update_rotated_points()
        
        self._create_roof_slopes()
        self._create_walls()
        self._create_gable_triangles()
        self._add_foundation()
    
    def _update_rotated_points(self):
        """Update all rotated points based on current rotation angle"""
        self.roof_points = {}
        for key in ['ridge_front', 'ridge_back', 'eave_left_front', 
                    'eave_right_front', 'eave_left_back', 'eave_right_back']:
            self.roof_points[key] = self._rotate_point(self.original_points[key])
        
        self.base_points = {}
        for key in ['base_left_front', 'base_right_front', 
                    'base_right_back', 'base_left_back']:
            self.base_points[key] = self._rotate_point(self.original_points[key])
    
    def _create_roof_slopes(self):
        """Create the two sloped surfaces of the gable roof"""
        left_slope_points = np.array([
            self.roof_points['eave_left_front'],
            self.roof_points['eave_left_back'],
            self.roof_points['ridge_back'],
            self.roof_points['ridge_front']
        ])
        left_faces = np.array([[4, 0, 1, 2, 3]])
        self.left_slope = pv.PolyData(left_slope_points, left_faces)
        
        right_slope_points = np.array([
            self.roof_points['eave_right_front'],
            self.roof_points['eave_right_back'],
            self.roof_points['ridge_back'],
            self.roof_points['ridge_front']
        ])
        right_faces = np.array([[4, 0, 1, 2, 3]])
        self.right_slope = pv.PolyData(right_slope_points, right_faces)
        
        self.mesh_cache['left_slope'] = self.left_slope
        self.mesh_cache['right_slope'] = self.right_slope
        
        self._apply_roof_textures()
    
    def _apply_roof_textures(self):
        """Apply textures to roof slopes"""
        left_tcoords = np.array([[0, 0], [5, 0], [5, 3], [0, 3]])
        right_tcoords = np.array([[0, 0], [5, 0], [5, 3], [0, 3]])
        
        self.left_slope.active_t_coords = left_tcoords
        self.right_slope.active_t_coords = right_tcoords
        
        roof_texture, texture_loaded = self.load_texture_safely(
            self.roof_texture_path,
            self.roof_color
        )
        
        if texture_loaded:
            self.building_actors['left_slope'] = self.plotter.add_mesh(
                self.left_slope,
                texture=roof_texture,
                name="left_slope",
                smooth_shading=True,
                ambient=0.2,
                diffuse=0.8,
                specular=0.1
            )
            self.building_actors['right_slope'] = self.plotter.add_mesh(
                self.right_slope,
                texture=roof_texture,
                name="right_slope",
                smooth_shading=True,
                ambient=0.2,
                diffuse=0.8,
                specular=0.1
            )
        else:
            self.building_actors['left_slope'] = self.plotter.add_mesh(
                self.left_slope,
                color=self.roof_color,
                name="left_slope",
                smooth_shading=True
            )
            self.building_actors['right_slope'] = self.plotter.add_mesh(
                self.right_slope,
                color=self.roof_color,
                name="right_slope",
                smooth_shading=True
            )
    
    def _create_walls(self):
        """Create all four walls of the building (rotated)"""
        wall_vertices = []
        wall_faces = []
        vertex_offset = 0
        
        # Front wall
        wall_vertices.extend([
            self.base_points['base_left_front'],
            self.base_points['base_right_front'],
            self.roof_points['eave_right_front'],
            self.roof_points['eave_left_front']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        # Right wall
        wall_vertices.extend([
            self.base_points['base_right_front'],
            self.base_points['base_right_back'],
            self.roof_points['eave_right_back'],
            self.roof_points['eave_right_front']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        # Back wall
        wall_vertices.extend([
            self.base_points['base_right_back'],
            self.base_points['base_left_back'],
            self.roof_points['eave_left_back'],
            self.roof_points['eave_right_back']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        # Left wall
        wall_vertices.extend([
            self.base_points['base_left_back'],
            self.base_points['base_left_front'],
            self.roof_points['eave_left_front'],
            self.roof_points['eave_left_back']
        ])
        wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
        vertex_offset += 4
        
        wall_mesh = pv.PolyData(np.array(wall_vertices))
        wall_mesh.faces = np.hstack(wall_faces)
        
        self.mesh_cache['walls'] = wall_mesh
        
        texture_coords = []
        texture_coords.extend([[0, 0], [3, 0], [3, 1], [0, 1]])
        texture_coords.extend([[0, 0], [4, 0], [4, 1], [0, 1]])
        texture_coords.extend([[0, 0], [3, 0], [3, 1], [0, 1]])
        texture_coords.extend([[0, 0], [4, 0], [4, 1], [0, 1]])
        
        wall_mesh.active_t_coords = np.array(texture_coords)
        
        wall_texture, texture_loaded = self.load_texture_safely(
            self.brick_texture_path,
            self.wall_color
        )
        
        if texture_loaded:
            self.building_actors['building_walls'] = self.plotter.add_mesh(
                wall_mesh,
                texture=wall_texture,
                name="building_walls",
                smooth_shading=True,
                ambient=0.25,
                diffuse=0.75,
                specular=0.05
            )
        else:
            self.building_actors['building_walls'] = self.plotter.add_mesh(
                wall_mesh,
                color=self.wall_color,
                name="building_walls",
                smooth_shading=True
            )
    
    def _create_gable_triangles(self):
        """Create triangular gable ends (rotated)"""
        front_tri_verts = np.array([
            self.roof_points['eave_left_front'],
            self.roof_points['eave_right_front'],
            self.roof_points['ridge_front']
        ])
        front_tri_faces = np.array([[3, 0, 1, 2]])
        front_gable = pv.PolyData(front_tri_verts, front_tri_faces)
        
        back_tri_verts = np.array([
            self.roof_points['eave_left_back'],
            self.roof_points['eave_right_back'],
            self.roof_points['ridge_back']
        ])
        back_tri_faces = np.array([[3, 0, 1, 2]])
        back_gable = pv.PolyData(back_tri_verts, back_tri_faces)
        
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
            self.building_actors['front_gable_triangle'] = self.plotter.add_mesh(
                front_gable,
                texture=wall_texture,
                name="front_gable_triangle",
                smooth_shading=True,
                ambient=0.25,
                diffuse=0.75,
                specular=0.05
            )
            self.building_actors['back_gable_triangle'] = self.plotter.add_mesh(
                back_gable,
                texture=wall_texture,
                name="back_gable_triangle",
                smooth_shading=True,
                ambient=0.25,
                diffuse=0.75,
                specular=0.05
            )
        else:
            self.building_actors['front_gable_triangle'] = self.plotter.add_mesh(
                front_gable,
                color=self.wall_color,
                name="front_gable_triangle",
                smooth_shading=True
            )
            self.building_actors['back_gable_triangle'] = self.plotter.add_mesh(
                back_gable,
                color=self.wall_color,
                name="back_gable_triangle",
                smooth_shading=True
            )
    
    def _add_foundation(self):
        """Add concrete foundation (also rotated)"""
        foundation_height = 0.2
        foundation_extend = 0.15
        
        half_length = self.length/2 + foundation_extend
        half_width = self.width/2 + foundation_extend
        
        foundation_verts_local = np.array([
            [-half_width, -half_length, -foundation_height],
            [half_width, -half_length, -foundation_height],
            [half_width, half_length, -foundation_height],
            [-half_width, half_length, -foundation_height],
            [-half_width, -half_length, 0],
            [half_width, -half_length, 0],
            [half_width, half_length, 0],
            [-half_width, half_length, 0]
        ])
        
        foundation_verts = self._rotate_points(foundation_verts_local)
        
        foundation = pv.PolyData(foundation_verts)
        foundation.faces = np.array([
            [4, 0, 1, 2, 3],
            [4, 4, 5, 6, 7],
            [4, 0, 1, 5, 4],
            [4, 1, 2, 6, 5],
            [4, 2, 3, 7, 6],
            [4, 3, 0, 4, 7]
        ]).flatten()
        
        self.mesh_cache['foundation'] = foundation
        
        self.building_actors['foundation'] = self.plotter.add_mesh(
            foundation,
            color=self.concrete_color,
            name="foundation",
            smooth_shading=True,
            ambient=0.3,
            diffuse=0.7,
            specular=0.02
        )
    
    def _add_rotation_circle(self):
        """Add rotation circle with cardinal markers"""
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
        """Add N, S, E, W markers around the rotation circle"""
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
    
    def _update_rotation_circle(self):
        """Update the rotation handle position"""
        if hasattr(self, 'rotation_handle_actor'):
            try:
                self.plotter.remove_actor('rotation_handle')
            except:
                pass
            
            radius = max(self.length, self.width) * 0.7
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
    
    def get_current_building_mesh(self):
        """Get the current combined building mesh for solar simulation - WITH CURRENT ROTATION"""
        try:
            # Create fresh meshes with current rotation applied
            meshes_to_combine = []
            
            # Create fresh copies of meshes with current vertices
            if 'left_slope' in self.mesh_cache:
                mesh = self.mesh_cache['left_slope'].copy(deep=True)
                meshes_to_combine.append(mesh)
            
            if 'right_slope' in self.mesh_cache:
                mesh = self.mesh_cache['right_slope'].copy(deep=True)
                meshes_to_combine.append(mesh)
            
            if 'walls' in self.mesh_cache:
                mesh = self.mesh_cache['walls'].copy(deep=True)
                meshes_to_combine.append(mesh)
            
            if 'front_gable' in self.mesh_cache:
                mesh = self.mesh_cache['front_gable'].copy(deep=True)
                meshes_to_combine.append(mesh)
            
            if 'back_gable' in self.mesh_cache:
                mesh = self.mesh_cache['back_gable'].copy(deep=True)
                meshes_to_combine.append(mesh)
            
            if 'foundation' in self.mesh_cache:
                mesh = self.mesh_cache['foundation'].copy(deep=True)
                meshes_to_combine.append(mesh)
            
            # Combine meshes
            if meshes_to_combine:
                combined_mesh = meshes_to_combine[0]
                for mesh in meshes_to_combine[1:]:
                    combined_mesh = combined_mesh + mesh
                
                # Ensure the mesh knows it's been updated
                combined_mesh.Modified()
                return combined_mesh
            
            return None
            
        except Exception as e:
            print(f"Error getting building mesh: {e}")
            return None
    
    def rotate_building(self, angle_delta):
        """Efficiently rotate the building by updating existing meshes"""
        old_angle = self.rotation_angle
        self.rotation_angle = (self.rotation_angle + angle_delta) % 360
        self.rotation_rad = np.radians(self.rotation_angle)
        
        # Update rotated points
        self._update_rotated_points()
        
        # Update mesh vertices efficiently
        self._update_mesh_vertices()
        
        # Force complete solar system update with new building configuration
        self._force_solar_system_update()
        
        # Update rotation indicator
        if hasattr(self, 'rotation_text_actor'):
            self._update_rotation_indicator()
        
        # Update rotation circle
        if hasattr(self, 'rotation_handle_actor'):
            self._update_rotation_circle()
        
        # Recreate solar panels with new positions
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            active_sides = list(self.solar_panel_handler.active_sides)
            for side in active_sides:
                self.solar_panel_handler.active_sides.discard(side)
                self.solar_panel_handler.add_panels(side)
        
        # Single render call for performance
        self.plotter.render()
    
    def _force_solar_system_update(self):
        """Force complete update of solar visualization system with rotated building"""
        try:
            # Get fresh building mesh with current rotation
            building_mesh = self.get_current_building_mesh()
            if not building_mesh:
                return
            
            # Update through model tab
            if self.model_tab:
                # Force update the roof reference in model tab
                if hasattr(self.model_tab, 'current_roof'):
                    self.model_tab.current_roof = self
                
                # Update solar visualization if it exists
                if hasattr(self.model_tab, 'solar_visualization') and self.model_tab.solar_visualization:
                    solar_viz = self.model_tab.solar_visualization
                    
                    # Update building mesh reference
                    solar_viz.building_mesh = building_mesh
                    
                    # Clear all caches
                    if hasattr(solar_viz, '_shadow_cache'):
                        solar_viz._shadow_cache = {}
                    if hasattr(solar_viz, 'shadow_mesh'):
                        solar_viz.shadow_mesh = None
                    
                    # Remove old shadow actors
                    if hasattr(solar_viz, 'shadow_actor') and solar_viz.shadow_actor:
                        try:
                            self.plotter.remove_actor(solar_viz.shadow_actor)
                            solar_viz.shadow_actor = None
                        except:
                            pass
                    
                    # Force recalculation of shadows
                    if hasattr(solar_viz, 'sun_position'):
                        sun_pos = solar_viz.sun_position
                        if sun_pos and sun_pos[2] > 0:  # Sun is above horizon
                            # Recreate shadow from scratch
                            if hasattr(solar_viz, '_create_shadow'):
                                solar_viz._create_shadow(sun_pos)
                            elif hasattr(solar_viz, '_update_shadow'):
                                solar_viz._update_shadow(sun_pos)
                    
                    # Update comprehensive shadows if available
                    if hasattr(solar_viz, 'update_comprehensive_shadows'):
                        solar_viz.update_comprehensive_shadows()
                    
                    # Force update sun position to recalculate everything
                    if hasattr(solar_viz, 'update_sun_position'):
                        solar_viz.update_sun_position()
                
                # Trigger roof update for solar
                if hasattr(self.model_tab, 'update_roof_for_solar'):
                    self.model_tab.update_roof_for_solar(self)
            
            # Direct update if we have solar visualization reference
            if self.solar_visualization:
                self.solar_visualization.building_mesh = building_mesh
                if hasattr(self.solar_visualization, 'update_sun_position'):
                    self.solar_visualization.update_sun_position()
            
            # Update solar event handlers
            self._update_solar_event_handlers_with_new_mesh(building_mesh)
            
        except Exception as e:
            print(f"Error updating solar system: {e}")
    
    def _update_solar_event_handlers_with_new_mesh(self, building_mesh):
        """Update solar event handlers with new building mesh"""
        try:
            if hasattr(self.plotter, 'app'):
                app = self.plotter.app
                if hasattr(app, 'main_window'):
                    main_window = app.main_window
                    
                    # Update through content tabs if available
                    if hasattr(main_window, 'content_tabs'):
                        content_tabs = main_window.content_tabs
                        if hasattr(content_tabs, 'solar_event_handlers'):
                            solar_handlers = content_tabs.solar_event_handlers
                            solar_handlers.update_building_for_shadows(building_mesh=building_mesh)
                    
                    # Also update through solar controls if available
                    if hasattr(main_window, 'solar_controls'):
                        solar_controls = main_window.solar_controls
                        if hasattr(solar_controls, 'update_building_mesh'):
                            solar_controls.update_building_mesh(building_mesh)
                            
        except Exception as e:
            print(f"Error updating solar event handlers: {e}")
    
    def _update_mesh_vertices(self):
        """Update mesh vertices without recreating actors - OPTIMIZED"""
        # Update left slope
        if 'left_slope' in self.mesh_cache:
            new_points = np.array([
                self.roof_points['eave_left_front'],
                self.roof_points['eave_left_back'],
                self.roof_points['ridge_back'],
                self.roof_points['ridge_front']
            ])
            self.mesh_cache['left_slope'].points = new_points
            self.mesh_cache['left_slope'].Modified()
        
        # Update right slope
        if 'right_slope' in self.mesh_cache:
            new_points = np.array([
                self.roof_points['eave_right_front'],
                self.roof_points['eave_right_back'],
                self.roof_points['ridge_back'],
                self.roof_points['ridge_front']
            ])
            self.mesh_cache['right_slope'].points = new_points
            self.mesh_cache['right_slope'].Modified()
        
        # Update walls
        if 'walls' in self.mesh_cache:
            wall_vertices = []
            wall_vertices.extend([
                self.base_points['base_left_front'],
                self.base_points['base_right_front'],
                self.roof_points['eave_right_front'],
                self.roof_points['eave_left_front']
            ])
            wall_vertices.extend([
                self.base_points['base_right_front'],
                self.base_points['base_right_back'],
                self.roof_points['eave_right_back'],
                self.roof_points['eave_right_front']
            ])
            wall_vertices.extend([
                self.base_points['base_right_back'],
                self.base_points['base_left_back'],
                self.roof_points['eave_left_back'],
                self.roof_points['eave_right_back']
            ])
            wall_vertices.extend([
                self.base_points['base_left_back'],
                self.base_points['base_left_front'],
                self.roof_points['eave_left_front'],
                self.roof_points['eave_left_back']
            ])
            self.mesh_cache['walls'].points = np.array(wall_vertices)
            self.mesh_cache['walls'].Modified()
        
        # Update gable triangles
        if 'front_gable' in self.mesh_cache:
            new_points = np.array([
                self.roof_points['eave_left_front'],
                self.roof_points['eave_right_front'],
                self.roof_points['ridge_front']
            ])
            self.mesh_cache['front_gable'].points = new_points
            self.mesh_cache['front_gable'].Modified()
        
        if 'back_gable' in self.mesh_cache:
            new_points = np.array([
                self.roof_points['eave_left_back'],
                self.roof_points['eave_right_back'],
                self.roof_points['ridge_back']
            ])
            self.mesh_cache['back_gable'].points = new_points
            self.mesh_cache['back_gable'].Modified()
        
        # Update foundation
        if 'foundation' in self.mesh_cache:
            foundation_height = 0.2
            foundation_extend = 0.15
            half_length = self.length/2 + foundation_extend
            half_width = self.width/2 + foundation_extend
            
            foundation_verts_local = np.array([
                [-half_width, -half_length, -foundation_height],
                [half_width, -half_length, -foundation_height],
                [half_width, half_length, -foundation_height],
                [-half_width, half_length, -foundation_height],
                [-half_width, -half_length, 0],
                [half_width, -half_length, 0],
                [half_width, half_length, 0],
                [-half_width, half_length, 0]
            ])
            new_points = self._rotate_points(foundation_verts_local)
            self.mesh_cache['foundation'].points = new_points
            self.mesh_cache['foundation'].Modified()
    
    def _update_rotation_indicator(self):
        """Update the rotation indicator text"""
        if hasattr(self, 'rotation_text_actor'):
            try:
                self.plotter.remove_actor('rotation_text')
            except:
                pass
        
        text = f"Rotation: {self.rotation_angle:.1f}°"
        self.rotation_text_actor = self.plotter.add_text(
            text,
            position='upper_right',
            font_size=10,
            color='orange',
            name='rotation_text'
        )
    
    def _add_rotation_indicator(self):
        """Add visual indicator showing building rotation"""
        text = f"Rotation: {self.rotation_angle:.1f}°"
        self.rotation_text_actor = self.plotter.add_text(
            text,
            position='upper_right',
            font_size=10,
            color='orange',
            name='rotation_text'
        )
    
    def initialize_roof(self, dimensions):
        """Initialize roof with building - NO ANNOTATIONS"""
        self.dimensions = dimensions
        
        self.create_roof_geometry()
        
        # Add rotation circle with cardinals
        try:
            self._add_rotation_circle()
        except Exception as e:
            pass
        
        self._initialize_solar_panel_handler()
        
        if self.rotation_angle != 0:
            self._add_rotation_indicator()
        
        try:
            self.setup_key_bindings()
            if hasattr(self, '_setup_environment_key_bindings'):
                self._setup_environment_key_bindings()
        except Exception as e:
            pass
        
        try:
            self.set_default_camera_view()
        except Exception as e:
            pass
        
        # Initial solar system update
        self._force_solar_system_update()
    
    def calculate_camera_position(self):
        """Calculate optimal camera position for centered building"""
        total_height = self.building_height + self.height
        
        base_position = np.array([self.width*1.8, -self.length*1.5, total_height*1.5])
        rotated_position = self._rotate_point(base_position)
        
        focal_point = (0, 0, total_height*0.4)
        up_vector = (0, 0, 1)
        
        return tuple(rotated_position), focal_point, up_vector
    
    def setup_roof_specific_key_bindings(self):
        """Setup key bindings specific to gable roof"""
        if self.solar_panel_handler:
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("left"))
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("right"))
            self.plotter.add_key_event("c", self.safe_clear_panels)
            self.plotter.add_key_event("C", self.safe_clear_panels)
        
        self.plotter.add_key_event("plus", lambda: self.rotate_building(15))
        self.plotter.add_key_event("minus", lambda: self.rotate_building(-15))
    
    def get_solar_panel_areas(self):
        """Get valid solar panel areas for gable roof"""
        return ["left", "right"]
    
    def get_solar_panel_handler_class(self):
        """Get the solar panel handler class for gable roof"""
        return SolarPanelPlacementGable if SOLAR_HANDLER_AVAILABLE else None
    
    def _get_annotation_params(self):
        """Get parameters for RoofAnnotation - NOT USED"""
        return None  # No annotations
    
    def add_attachment_points(self):
        """Generate attachment points for gable roof obstacle placement"""
        try:
            if not hasattr(self, 'obstacle_count'):
                self.obstacle_count = 0
                self.obstacles = []
            
            if self.obstacle_count >= 6:
                self.update_instruction(_('maximum_obstacles_reached'))
                return False
            
            if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                self.plotter.remove_actor(self.attachment_point_actor)
                self.attachment_point_actor = None
            
            self.attachment_points = []
            self.attachment_points_occupied = {}
            self.face_normals = {}
            self.obstacle_placed_this_session = False
            
            offset_distance = 0.15
            
            roof_points = self.roof_points
            
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
            
            for i in range(grid_size):
                for j in range(grid_size):
                    u = 0.15 + (i / (grid_size - 1)) * 0.7
                    v = 0.15 + (j / (grid_size - 1)) * 0.7
                    
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
            
            for i in range(grid_size):
                for j in range(grid_size):
                    u = 0.15 + (i / (grid_size - 1)) * 0.7
                    v = 0.15 + (j / (grid_size - 1)) * 0.7
                    
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
            
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None,
                    'normal': self.face_normals[i]['normal'],
                    'face': self.face_normals[i]['face'],
                    'roof_point': self.face_normals[i]['roof_point']
                }
            
            if self.attachment_points:
                points = pv.PolyData(np.array(self.attachment_points))
                
                self.attachment_point_actor = self.plotter.add_points(
                    points,
                    color='black',
                    point_size=10,
                    render_points_as_spheres=True,
                    pickable=True
                )
                
                self.plotter.enable_point_picking(
                    callback=self.attachment_point_clicked,
                    show_message=False,
                    pickable_window=False,
                    tolerance=0.05
                )
                
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
            return False
    
    def attachment_point_clicked(self, point, *args):
        """Handle attachment point click"""
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
        
        point_data = self.attachment_points_occupied.get(closest_point_idx, {})
        normal_vector = point_data.get('normal', np.array([0, 0, 1]))
        roof_point = point_data.get('roof_point')
        face = point_data.get('face')
        
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
        
        if closest_point_idx in self.attachment_points_occupied:
            self.attachment_points_occupied[closest_point_idx]['occupied'] = True
            self.attachment_points_occupied[closest_point_idx]['obstacle'] = obstacle
        
        self.plotter.disable_picking()
        
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.plotter.remove_actor(self.attachment_point_actor)
            self.attachment_point_actor = None
        
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            active_sides = list(self.solar_panel_handler.active_sides)
            for side in active_sides:
                self.solar_panel_handler.add_panels(side)
        
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
