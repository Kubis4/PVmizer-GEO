#!/usr/bin/env python3
"""
roofs/concrete/flat_roof.py
Fixed FlatRoof - annotations properly centered with the building
"""
from roofs.base.base_roof import BaseRoof
from roofs.base.resource_utils import resource_path
from roofs.roof_annotation import RoofAnnotation
from translations import _
import pyvista as pv
import numpy as np
import os

try:
    from roofs.solar_panel_handlers.solar_panel_placement_flat import SolarPanelPlacementFlat
    SOLAR_HANDLER_AVAILABLE = True
    print("✅ Solar panel handler imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import solar panel handler: {e}")
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementFlat = None

class FlatRoof(BaseRoof):
    """Complete flat roof centered on grass plane with proper annotations"""
    
    def __init__(self, plotter=None, dimensions=(10.0, 8.0, 0.5, 0.3), theme="light"):
        """Initialize flat roof with complete building"""
        # Handle dimensions
        if dimensions is None:
            dimensions = (10.0, 8.0, 0.5, 0.3)
        
        # Parse dimensions
        if len(dimensions) >= 2:
            self.length, self.width = dimensions[0], dimensions[1]
        else:
            self.length, self.width = 10.0, 8.0
        
        self.height = 0.5  # For flat roof, height is the parapet height for annotation
        
        if len(dimensions) >= 3:
            self.parapet_height = dimensions[2]
        else:
            self.parapet_height = 0.5
            
        if len(dimensions) >= 4:
            self.parapet_width = dimensions[3]
        else:
            self.parapet_width = 0.3
        
        # Building height - FIXED at 3m
        self.building_height = 3.0
        
        # Set texture paths
        texture_base_path = "PVmizer GEO/textures"
        self.roof_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.wall_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.brick_texture_path = resource_path(os.path.join(texture_base_path, "brick.jpg"))
        self.concrete_texture_path = resource_path(os.path.join(texture_base_path, "concrete.jpg"))
        
        # Colors
        self.roof_color = "#A9A9A9"
        self.wall_color = "#DEB887"
        self.concrete_color = "#808080"
        self.parapet_color = "#696969"
        
        # Call parent constructor (this creates the ground plane)
        super().__init__(plotter, dimensions, theme)
        
        # CRITICAL: Set base_height for panel placement
        self.base_height = self.building_height
        
        # Setup lighting
        self._setup_lighting()
        
        # Initialize roof using template method
        self.initialize_roof(dimensions)
        
        print(f"🏠 FlatRoof initialized with proper annotations")
    
    def initialize_roof(self, dimensions):
        """Initialize roof with building"""
        # Store dimensions
        self.dimensions = dimensions
        
        # Create roof and building geometry
        self.create_roof_geometry()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Create annotations using RoofAnnotation class
        try:
            annotation_params = self._get_annotation_params()
            if annotation_params:
                self.annotator = RoofAnnotation(
                    self.plotter,
                    *annotation_params,
                    theme=self.theme,
                    center_origin=True,  # Important: we're using centered coordinates
                    base_height=self.building_height  # Pass the base height
                )
                self.annotator.add_annotations()
                print("✅ Annotations added using RoofAnnotation")
        except Exception as e:
            print(f"⚠️ Could not add annotations: {e}")
            import traceback
            traceback.print_exc()
            self.annotator = None
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
            if hasattr(self, '_setup_environment_key_bindings'):
                self._setup_environment_key_bindings()
            print("✅ Key bindings configured")
        except Exception as e:
            print(f"⚠️ Error setting up key bindings: {e}")
        
        # Set camera view
        try:
            self.set_default_camera_view()
            print("✅ Camera positioned")
        except Exception as e:
            print(f"⚠️ Could not set camera view: {e}")
    
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
            
            print("✅ Lighting configured")
        except Exception as e:
            print(f"⚠️ Could not setup lighting: {e}")
    
    def create_roof_geometry(self):
        """Create flat roof CENTERED on the grass plane"""
        # Calculate half dimensions for centering
        half_length = self.length / 2
        half_width = self.width / 2
        
        # Roof at building height
        roof_z = self.building_height
        
        # Create roof surface CENTERED at origin
        roof_vertices = np.array([
            [-half_length, -half_width, roof_z],
            [half_length, -half_width, roof_z],
            [half_length, half_width, roof_z],
            [-half_length, half_width, roof_z]
        ])
        
        # Store roof points for solar panel placement (still in 0-based for panel system)
        self.roof_points = {
            'bottom_left': np.array([self.parapet_width, self.parapet_width, roof_z]),
            'bottom_right': np.array([self.length - self.parapet_width, self.parapet_width, roof_z]),
            'top_right': np.array([self.length - self.parapet_width, self.width - self.parapet_width, roof_z]),
            'top_left': np.array([self.parapet_width, self.width - self.parapet_width, roof_z])
        }
        
        # Create roof mesh
        self._create_roof_surface(roof_vertices)
        
        # Create building walls (centered)
        self._create_building_walls_centered()
        
        # Create parapet walls (centered) - FIXED VERSION
        self._create_parapet_walls_centered()
        
        # Add foundation (centered)
        self._add_foundation_centered()
        
    def _create_roof_surface(self, vertices):
        """Create the flat roof surface with wall.jpg texture"""
        roof_faces = np.array([[4, 0, 1, 2, 3]])
        self.roof_mesh = pv.PolyData(vertices, roof_faces)
        
        # Apply texture coordinates
        texture_coords = np.array([
            [0, 0], 
            [3, 0],
            [3, 3], 
            [0, 3]
        ])
        self.roof_mesh.active_texture_coordinates = texture_coords
        
        # Load wall.jpg texture for roof
        roof_texture, texture_loaded = self.load_texture_safely(
            self.roof_texture_path,
            self.roof_color
        )
        
        if texture_loaded:
            self.plotter.add_mesh(
                self.roof_mesh,
                texture=roof_texture,
                name="roof",
                smooth_shading=True,
                ambient=0.3,
                diffuse=0.7,
                specular=0.05
            )
        else:
            self.plotter.add_mesh(
                self.roof_mesh,
                color=self.roof_color,
                name="roof",
                smooth_shading=True
            )
        
        print("✅ Roof surface created with wall.jpg texture")
    
    def _create_building_walls_centered(self):
        """Create building walls CENTERED at origin"""
        half_length = self.length / 2
        half_width = self.width / 2
        
        wall_vertices = []
        wall_faces = []
        
        # Base and top points CENTERED
        base_points = np.array([
            [-half_length, -half_width, 0],
            [half_length, -half_width, 0],
            [half_length, half_width, 0],
            [-half_length, half_width, 0]
        ])
        
        top_points = np.array([
            [-half_length, -half_width, self.building_height],
            [half_length, -half_width, self.building_height],
            [half_length, half_width, self.building_height],
            [-half_length, half_width, self.building_height]
        ])
        
        vertex_offset = 0
        for i in range(4):
            j = (i + 1) % 4
            wall_verts = [
                base_points[i],
                base_points[j],
                top_points[j],
                top_points[i]
            ]
            wall_vertices.extend(wall_verts)
            wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
            vertex_offset += 4
        
        wall_mesh = pv.PolyData(np.array(wall_vertices))
        wall_mesh.faces = np.hstack(wall_faces)
        
        texture_coords = []
        for i in range(4):
            texture_coords.extend([[0, 0], [3, 0], [3, 1], [0, 1]])
        wall_mesh.active_texture_coordinates = np.array(texture_coords)
        
        wall_texture, texture_loaded = self.load_texture_safely(
            self.brick_texture_path,
            self.wall_color
        )
        
        if texture_loaded:
            self.plotter.add_mesh(
                wall_mesh,
                texture=wall_texture,
                name="building_walls",
                smooth_shading=True,
                ambient=0.25,
                diffuse=0.75,
                specular=0.05
            )
        else:
            self.plotter.add_mesh(
                wall_mesh,
                color=self.wall_color,
                name="building_walls",
                smooth_shading=True
            )
        
        print("✅ Building walls created")
    
    def _create_parapet_walls_centered(self):
        """Create parapet walls CENTERED at origin with proper texture coordinates"""
        half_length = self.length / 2
        half_width = self.width / 2
        parapet_top = self.building_height + self.parapet_height
        
        # Load texture once
        parapet_texture, texture_loaded = self.load_texture_safely(
            self.concrete_texture_path,
            self.parapet_color
        )
        
        # Create each parapet wall manually with texture coordinates
        parapets_data = [
            # Front parapet
            {
                'bounds': (-half_length, half_length, -half_width - self.parapet_width/2, -half_width + self.parapet_width/2, self.building_height, parapet_top),
                'name': 'parapet_front'
            },
            # Back parapet  
            {
                'bounds': (-half_length, half_length, half_width - self.parapet_width/2, half_width + self.parapet_width/2, self.building_height, parapet_top),
                'name': 'parapet_back'
            },
            # Left parapet
            {
                'bounds': (-half_length - self.parapet_width/2, -half_length + self.parapet_width/2, -half_width, half_width, self.building_height, parapet_top),
                'name': 'parapet_left'
            },
            # Right parapet
            {
                'bounds': (half_length - self.parapet_width/2, half_length + self.parapet_width/2, -half_width, half_width, self.building_height, parapet_top),
                'name': 'parapet_right'
            }
        ]
        
        for i, parapet_data in enumerate(parapets_data):
            bounds = parapet_data['bounds']
            name = parapet_data['name']
            
            # Create box mesh
            parapet = pv.Box(bounds=bounds)
            
            # Add texture coordinates if we have a texture
            if texture_loaded:
                # Generate texture coordinates for the box
                # This creates a simple UV mapping for all faces
                n_points = parapet.n_points
                texture_coords = np.zeros((n_points, 2))
                
                # Simple UV mapping - you can make this more sophisticated
                for j in range(n_points):
                    point = parapet.points[j]
                    # Map X and Y coordinates to UV space (0-1)
                    u = (point[0] - bounds[0]) / (bounds[1] - bounds[0]) if bounds[1] != bounds[0] else 0
                    v = (point[1] - bounds[2]) / (bounds[3] - bounds[2]) if bounds[3] != bounds[2] else 0
                    texture_coords[j] = [u % 1.0, v % 1.0]  # Ensure 0-1 range
                
                parapet.active_texture_coordinates = texture_coords
                
                # Add mesh with texture
                self.plotter.add_mesh(
                    parapet,
                    texture=parapet_texture,
                    name=name,
                    smooth_shading=True,
                    ambient=0.3,
                    diffuse=0.7,
                    specular=0.05
                )
            else:
                # Add mesh without texture (fallback to color)
                self.plotter.add_mesh(
                    parapet,
                    color=self.parapet_color,
                    name=name,
                    smooth_shading=True
                )
        
        print("✅ Parapet walls created with proper texture coordinates")
    
    def _add_foundation_centered(self):
        """Add foundation CENTERED at origin"""
        foundation_height = 0.2
        foundation_extend = 0.15
        
        half_length = self.length/2 + foundation_extend
        half_width = self.width/2 + foundation_extend
        
        foundation = pv.Box(bounds=(
            -half_length, half_length,
            -half_width, half_width,
            -foundation_height, 0
        ))
        
        self.plotter.add_mesh(
            foundation,
            color=self.concrete_color,
            name="foundation",
            smooth_shading=True,
            ambient=0.3,
            diffuse=0.7,
            specular=0.02
        )
        
        print("✅ Foundation added")
    
    def calculate_camera_position(self):
        """Calculate camera position for centered building"""
        total_height = self.building_height + self.parapet_height
        position = (self.length*1.5, -self.width*1.5, total_height*2.0)
        focal_point = (0, 0, total_height*0.5)  # Focus on center (0,0)
        up_vector = (0, 0, 1)
        return position, focal_point, up_vector
    
    def setup_roof_specific_key_bindings(self):
        """Setup key bindings"""
        if self.solar_panel_handler:
            print("✅ Adding panel placement key bindings")
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("center"))
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("north"))
            self.plotter.add_key_event("3", lambda: self.safe_add_panels("south"))
            self.plotter.add_key_event("4", lambda: self.safe_add_panels("east"))
            self.plotter.add_key_event("5", lambda: self.safe_add_panels("west"))
            self.plotter.add_key_event("c", self.safe_clear_panels)
            self.plotter.add_key_event("C", self.safe_clear_panels)
    
    def get_solar_panel_areas(self):
        """Get valid solar panel areas"""
        return ["center", "north", "south", "east", "west"]
    
    def get_solar_panel_handler_class(self):
        """Get solar panel handler class"""
        return SolarPanelPlacementFlat if SOLAR_HANDLER_AVAILABLE else None
    
    def _get_annotation_params(self):
        """Get annotation parameters for RoofAnnotation class"""
        # Return params: (length, width, height, slope_angle, center_origin)
        # For flat roof, we use parapet_height as the height dimension
        return (self.length, self.width, self.parapet_height, None)
    
    def add_attachment_points(self):
        """Generate attachment points for obstacles on centered building"""
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
            
            # Generate grid points on roof (centered coordinates)
            margin = self.parapet_width + 0.5
            half_length = self.length / 2
            half_width = self.width / 2
            grid_size = 6
            
            point_index = 0
            for i in range(grid_size):
                for j in range(grid_size):
                    x = -half_length + margin + (i/(grid_size-1)) * (self.length - 2*margin)
                    y = -half_width + margin + (j/(grid_size-1)) * (self.width - 2*margin)
                    z = self.building_height + 0.1
                    
                    point = np.array([x, y, z])
                    self.attachment_points.append(point)
                    self.face_normals[point_index] = {
                        'normal': np.array([0, 0, 1]),
                        'face': 'top',
                        'roof_point': np.array([x, y, self.building_height])
                    }
                    point_index += 1
            
            # Initialize tracking
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None,
                    'normal': self.face_normals[i]['normal'],
                    'face': self.face_normals[i]['face'],
                    'roof_point': self.face_normals[i]['roof_point']
                }
            
            # Create visualization
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
            print(f"Error adding attachment points: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Get point data
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
        
        # Mark point as occupied
        if closest_point_idx in self.attachment_points_occupied:
            self.attachment_points_occupied[closest_point_idx]['occupied'] = True
            self.attachment_points_occupied[closest_point_idx]['obstacle'] = obstacle
        
        self.plotter.disable_picking()
        
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.plotter.remove_actor(self.attachment_point_actor)
            self.attachment_point_actor = None
        
        # Update panels if needed
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            active_areas = getattr(self.solar_panel_handler, 'active_areas', [])
            for area in active_areas:
                self.solar_panel_handler.add_panels(area)
        
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
