#!/usr/bin/env python3
"""
roofs/concrete/hip_roof.py
Complete HipRoof with building structure, textures, and environment like PyramidRoof
"""
from roofs.base.base_roof import BaseRoof
from roofs.base.resource_utils import resource_path
from roofs.roof_annotation import RoofAnnotation
from translations import _
import pyvista as pv
import numpy as np
import os

try:
    from roofs.solar_panel_handlers.solar_panel_placement_hip import SolarPanelPlacementHip
    SOLAR_HANDLER_AVAILABLE = True
    print("✅ Solar panel handler imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import solar panel handler: {e}")
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementHip = None

class HipRoof(BaseRoof):
    """Complete hip roof with building structure and environment"""
    
    def __init__(self, plotter=None, dimensions=(10.0, 8.0, 5.0), theme="light"):
        """Initialize hip roof with complete building"""
        # Store properties
        self.length, self.width, self.height = dimensions
        
        # Building height (walls from ground to roof)
        self.building_height = 3.0  # 3 meters tall building
        
        # Calculate slope angle for solar panel performance
        self.slope_angle = np.arctan(self.height / (self.width / 2))
        
        # Set texture paths using resource_path for robust loading
        texture_base_path = "PVmizer GEO/textures"
        
        # Define paths for different textures
        self.roof_texture_path = resource_path(os.path.join(texture_base_path, "rooftile.jpg"))
        self.wall_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.brick_texture_path = resource_path(os.path.join(texture_base_path, "brick.jpg"))
        self.concrete_texture_path = resource_path(os.path.join(texture_base_path, "concrete.jpg"))
        self.panel_texture_path = resource_path(os.path.join(texture_base_path, "solarpanel.png"))
        
        # Realistic colors
        self.roof_color = "#D2691E"  # Chocolate brown for tiles
        self.wall_color = "#DEB887"  # Burlywood for walls
        self.concrete_color = "#808080"  # Gray for foundation
        
        # Solar panel parameters
        self.panel_width = 1.0
        self.panel_height = 1.6
        self.panel_gap = 0.05
        self.panel_offset = 0.05
        self.edge_margin = 0.40
        
        # Call parent constructor
        super().__init__(plotter, dimensions, theme)
        
        # Setup lighting
        self._setup_lighting()
        
        # Initialize roof using template method
        self.initialize_roof(dimensions)
    
    def _setup_lighting(self):
        """Setup realistic lighting"""
        try:
            # Clear existing lights
            self.plotter.remove_all_lights()
            
            # Main sunlight
            sun = pv.Light()
            sun.position = (20, -20, 30)
            sun.focal_point = (0, 0, self.building_height/2)
            sun.intensity = 0.7
            sun.color = [1.0, 0.95, 0.8]
            self.plotter.add_light(sun)
            
            # Ambient light
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
        """Create hip roof at the top of the building"""
        half_length = self.length / 2
        half_width = self.width / 2
        
        # Roof sits on top of building
        roof_base_z = self.building_height
        
        # Define vertices with overhang
        overhang = 0.3  # 30cm roof overhang
        
        # Define the corners of the roof base with overhang
        vertices = np.array([
            [-half_width - overhang, -half_length - overhang, roof_base_z],  # front-left
            [half_width + overhang, -half_length - overhang, roof_base_z],   # front-right
            [half_width + overhang, half_length + overhang, roof_base_z],    # back-right
            [-half_width - overhang, half_length + overhang, roof_base_z],   # back-left
            [0, -half_length*0.25, roof_base_z + self.height],              # ridge-front
            [0, half_length*0.25, roof_base_z + self.height]                # ridge-back
        ])
        
        # Store key points
        self.roof_points = {
            'front_left': vertices[0],
            'front_right': vertices[1],
            'back_right': vertices[2],
            'back_left': vertices[3],
            'ridge_front': vertices[4],
            'ridge_back': vertices[5],
            'peak': vertices[4]  # For compatibility
        }
        
        # Store base points for building walls
        self.building_base_points = np.array([
            [-half_width, -half_length, 0],
            [half_width, -half_length, 0],
            [half_width, half_length, 0],
            [-half_width, half_length, 0]
        ])
        
        # Create hip roof faces
        self._create_hip_roof_faces(vertices)
        
        # Create building walls
        self._create_building_walls()
    
    def _create_hip_roof_faces(self, vertices):
        """Create the hip roof faces with proper texture"""
        # Create each face of the hip roof
        faces = []
        
        # Front triangular face
        front_face = pv.PolyData(vertices[[0, 1, 4]], faces=[3, 0, 1, 2])
        faces.append(front_face)
        
        # Back triangular face
        back_face = pv.PolyData(vertices[[2, 3, 5]], faces=[3, 0, 1, 2])
        faces.append(back_face)
        
        # Right side (two triangles)
        right_face1 = pv.PolyData(vertices[[1, 2, 4]], faces=[3, 0, 1, 2])
        right_face2 = pv.PolyData(vertices[[2, 5, 4]], faces=[3, 0, 1, 2])
        faces.extend([right_face1, right_face2])
        
        # Left side (two triangles)
        left_face1 = pv.PolyData(vertices[[0, 4, 3]], faces=[3, 0, 1, 2])
        left_face2 = pv.PolyData(vertices[[3, 4, 5]], faces=[3, 0, 1, 2])
        faces.extend([left_face1, left_face2])
        
        # Combine all faces into one mesh
        self.roof_mesh = faces[0]
        for face in faces[1:]:
            self.roof_mesh = self.roof_mesh.merge(face)
        
        # Apply roof texture
        self._apply_roof_texture()
        
        # Add ridge line
        ridge_line = pv.Line(self.roof_points['ridge_front'], self.roof_points['ridge_back'])
        self.plotter.add_mesh(ridge_line, color='black', line_width=3)
    
    def _apply_roof_texture(self):
        """Apply texture to the roof"""
        try:
            # Generate texture coordinates
            if self.roof_mesh.n_points > 0:
                bounds = self.roof_mesh.bounds
                texture_coords = np.zeros((self.roof_mesh.n_points, 2))
                
                for i in range(self.roof_mesh.n_points):
                    point = self.roof_mesh.points[i]
                    # Create tile pattern
                    u = (point[0] - bounds[0]) / (bounds[1] - bounds[0]) * 10
                    v = (point[1] - bounds[2]) / (bounds[3] - bounds[2]) * 10
                    texture_coords[i] = [u, v]
                
                self.roof_mesh.active_t_coords = texture_coords
            
            # Try to load texture
            roof_texture, texture_loaded = self.load_texture_safely(
                self.roof_texture_path,
                self.roof_color
            )
            
            # Add roof to scene
            if texture_loaded:
                self.plotter.add_mesh(
                    self.roof_mesh,
                    texture=roof_texture,
                    name="roof",
                    smooth_shading=True,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.1
                )
            else:
                self.plotter.add_mesh(
                    self.roof_mesh,
                    color=self.roof_color,
                    name="roof",
                    smooth_shading=True,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.1
                )
            
            print("✅ Roof created with texture")
            
        except Exception as e:
            print(f"⚠️ Error applying roof texture: {e}")
            # Fallback to color
            self.plotter.add_mesh(
                self.roof_mesh,
                color=self.roof_color,
                name="roof",
                smooth_shading=True
            )
    
    def _create_building_walls(self):
        """Create the building walls beneath the roof"""
        try:
            # Create walls from ground to roof
            wall_vertices = []
            wall_faces = []
            
            # Get base and top points
            base_points = self.building_base_points
            top_points = np.array([
                [-self.width/2, -self.length/2, self.building_height],
                [self.width/2, -self.length/2, self.building_height],
                [self.width/2, self.length/2, self.building_height],
                [-self.width/2, self.length/2, self.building_height]
            ])
            
            # Create each wall
            vertex_offset = 0
            for i in range(4):
                j = (i + 1) % 4
                
                # Wall vertices
                wall_verts = [
                    base_points[i],
                    base_points[j],
                    top_points[j],
                    top_points[i]
                ]
                wall_vertices.extend(wall_verts)
                
                # Wall face
                wall_faces.append([4, vertex_offset, vertex_offset+1, vertex_offset+2, vertex_offset+3])
                vertex_offset += 4
            
            # Create wall mesh
            wall_mesh = pv.PolyData(np.array(wall_vertices))
            wall_mesh.faces = np.hstack(wall_faces)
            
            # Generate texture coordinates
            texture_coords = []
            for i in range(4):  # For each wall
                texture_coords.extend([
                    [0, 0],
                    [3, 0],
                    [3, 1],
                    [0, 1]
                ])
            wall_mesh.active_t_coords = np.array(texture_coords)
            
            # Load wall texture
            wall_texture, texture_loaded = self.load_texture_safely(
                self.brick_texture_path if os.path.exists(resource_path(os.path.join("PVmizer GEO/textures", "brick.jpg"))) else self.wall_texture_path,
                self.wall_color
            )
            
            # Add walls
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
                    smooth_shading=True,
                    ambient=0.25,
                    diffuse=0.75,
                    specular=0.05
                )
            
            # Add foundation
            self._add_foundation()
            
            print("✅ Building base created")
            
        except Exception as e:
            print(f"❌ Error creating building base: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_foundation(self):
        """Add concrete foundation"""
        try:
            foundation_height = 0.2
            foundation_extend = 0.15
            
            half_length = self.length/2 + foundation_extend
            half_width = self.width/2 + foundation_extend
            
            foundation = pv.Box(bounds=(
                -half_width, half_width,
                -half_length, half_length,
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
            
        except Exception as e:
            print(f"⚠️ Could not add foundation: {e}")
    
    def initialize_roof(self, dimensions):
        """Initialize roof with building and environment"""
        # Store dimensions
        self.dimensions = dimensions
        
        # Create roof and building geometry
        self.create_roof_geometry()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Create annotations
        try:
            annotation_params = self._get_annotation_params()
            self.annotator = RoofAnnotation(
                self.plotter,
                *annotation_params,
                self.theme
            )
            self.annotator.add_annotations()
            print("✅ Annotations added")
        except Exception as e:
            print(f"⚠️ Could not add annotations: {e}")
            self.annotator = None
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
            self._setup_environment_key_bindings()
            print("✅ Key bindings configured (t=tree, p=pole, a=points, e=clear)")
        except Exception as e:
            print(f"⚠️ Error setting up key bindings: {e}")
        
        # Set camera view
        try:
            self.set_default_camera_view()
            print("✅ Camera positioned")
        except Exception as e:
            print(f"⚠️ Could not set camera view: {e}")
        
        print(f"🏠 {self.__class__.__name__} complete with building and environment")
    
    def calculate_camera_position(self):
        """Calculate optimal camera position"""
        total_height = self.building_height + self.height
        position = (self.width*2.0, -self.length*2.0, total_height*1.3)
        focal_point = (0, 0, total_height*0.4)
        up_vector = (0, 0, 1)
        return position, focal_point, up_vector
    
    def setup_roof_specific_key_bindings(self):
        """Setup hip roof key bindings"""
        if self.solar_panel_handler:
            print("✅ Adding panel key bindings (1-4 for sides)")
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("front"))
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("right"))
            self.plotter.add_key_event("3", lambda: self.safe_add_panels("back"))
            self.plotter.add_key_event("4", lambda: self.safe_add_panels("left"))
    
    def safe_add_panels(self, side):
        """Safely add panels"""
        try:
            if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                self.solar_panel_handler.add_panels(side)
        except Exception as e:
            print(f"Error adding panels to {side}: {e}")
    
    def get_solar_panel_areas(self):
        """Get valid panel areas"""
        return ["front", "right", "back", "left"]
    
    def get_solar_panel_handler_class(self):
        """Get panel handler class"""
        return SolarPanelPlacementHip if SOLAR_HANDLER_AVAILABLE else None
    
    def _get_annotation_params(self):
        """Get annotation parameters"""
        return (self.width, self.length, self.height, self.slope_angle, False)  # False for non-pyramid
    
    def add_attachment_points(self):
        """Generate attachment points for obstacles on roof"""
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
            points = self.roof_points
            
            ridge_front = points['ridge_front']
            ridge_back = points['ridge_back']
            front_left = points['front_left']
            front_right = points['front_right']
            back_left = points['back_left']
            back_right = points['back_right']
            
            # Calculate face normals for hip roof
            # Front face
            v1_front = front_right - front_left
            v2_front = ridge_front - front_left
            front_normal = np.cross(v1_front, v2_front)
            front_normal = front_normal / np.linalg.norm(front_normal)
            if front_normal[2] < 0:
                front_normal = -front_normal
            
            # Back face
            v1_back = back_left - back_right
            v2_back = ridge_back - back_right
            back_normal = np.cross(v1_back, v2_back)
            back_normal = back_normal / np.linalg.norm(back_normal)
            if back_normal[2] < 0:
                back_normal = -back_normal
            
            # Right faces
            v1_right = ridge_front - front_right
            v2_right = back_right - front_right
            right_normal = np.cross(v1_right, v2_right)
            right_normal = right_normal / np.linalg.norm(right_normal)
            if right_normal[2] < 0:
                right_normal = -right_normal
            
            # Left faces
            v1_left = ridge_back - back_left
            v2_left = front_left - back_left
            left_normal = np.cross(v1_left, v2_left)
            left_normal = left_normal / np.linalg.norm(left_normal)
            if left_normal[2] < 0:
                left_normal = -left_normal
            
            self.roof_face_info = {
                'front': {
                    'normal': front_normal,
                    'points': [front_left, front_right, ridge_front]
                },
                'back': {
                    'normal': back_normal,
                    'points': [back_right, back_left, ridge_back]
                },
                'right': {
                    'normal': right_normal,
                    'points': [front_right, back_right, ridge_back, ridge_front]
                },
                'left': {
                    'normal': left_normal,
                    'points': [back_left, front_left, ridge_front, ridge_back]
                }
            }
            
            point_index = 0
            
            # Generate points for each face
            for face_name, face_info in self.roof_face_info.items():
                normal = face_info['normal']
                face_points = face_info['points']
                
                if len(face_points) == 3:  # Triangular face
                    for u in np.linspace(0.2, 0.8, 4):
                        for v in np.linspace(0.2, 0.8, 4):
                            if u + v <= 0.9:
                                point = (1-u-v)*face_points[0] + u*face_points[1] + v*face_points[2]
                                offset_point = point + normal * offset_distance
                                self.attachment_points.append(offset_point)
                                self.face_normals[point_index] = {
                                    'normal': normal,
                                    'face': face_name,
                                    'roof_point': point
                                }
                                point_index += 1
                else:  # Quadrilateral face
                    for u in np.linspace(0.2, 0.8, 4):
                        for v in np.linspace(0.2, 0.8, 4):
                            point = (1-u)*(1-v)*face_points[0] + u*(1-v)*face_points[1] + \
                                   u*v*face_points[2] + (1-u)*v*face_points[3]
                            offset_point = point + normal * offset_distance
                            self.attachment_points.append(offset_point)
                            self.face_normals[point_index] = {
                                'normal': normal,
                                'face': face_name,
                                'roof_point': point
                            }
                            point_index += 1
            
            # Initialize tracking dictionary
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None,
                    'normal': self.face_normals[i]['normal'] if i in self.face_normals else None,
                    'face': self.face_normals[i]['face'] if i in self.face_normals else None,
                    'roof_point': self.face_normals[i]['roof_point'] if i in self.face_normals else None
                }
            
            # Create point cloud for visualization
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
                
                if not hasattr(self, 'placement_instruction') or not self.placement_instruction:
                    remaining = 6 - self.obstacle_count
                    display_name = self.get_translated_obstacle_name(self.selected_obstacle_type)
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
    
    def attachment_point_clicked(self, point_index_or_coords):
        """Handle clicking on attachment point"""
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
            
            if hasattr(self, 'selected_obstacle_type'):
                obstacle_type = self.selected_obstacle_type
            else:
                obstacle_type = "Chimney"
            
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
                
                try:
                    self.plotter.disable_picking()
                except:
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
                
                if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                    if hasattr(self.solar_panel_handler, 'active_sides'):
                        active_sides = list(self.solar_panel_handler.active_sides)
                        for side in active_sides:
                            self.solar_panel_handler.remove_panels_from_side(side)
                            self.solar_panel_handler.add_panels(side)
            else:
                self.update_instruction(_("Failed to add obstacle. Try a different location."))
                
        except Exception as e:
            print(f"Error in attachment point callback: {e}")
            import traceback
            traceback.print_exc()
    
    def find_closest_attachment_point_index(self, clicked_position):
        """Find closest attachment point"""
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
            print(f"Error finding closest attachment point: {e}")
            return None
