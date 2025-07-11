"""
Hip roof implementation using the BaseRoof template
Reduced from ~1000 lines to ~300 lines (70% reduction)
"""
from roofs.base.base_roof import BaseRoof
from translations import _
import pyvista as pv
import numpy as np

try:
    from roofs.solar_panel_handlers.solar_panel_placement_hip import SolarPanelPlacementHip
    SOLAR_HANDLER_AVAILABLE = True
    print("✅ Solar panel handler imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import solar panel handler: {e}")
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementHip = None

class HipRoof(BaseRoof):
    """Hip roof implementation - now 70% smaller thanks to inheritance!"""
    
    def __init__(self, plotter=None, dimensions=(10.0, 8.0, 5.0), theme="light"):
        # If dimensions are provided, use them; otherwise, show dialog to get them
        if dimensions is None:
            dimensions = self.show_input_dialog()
            if dimensions is None:
                return
            
        self.length, self.width, self.height = dimensions
        
        # Calculate slope angle for solar panel performance calculations
        self.slope_angle = np.arctan(self.height / (self.width / 2))
        
        # Initialize texture paths
        self.roof_texture_file = "PVmizer/textures/rooftile.jpg"
        self.wall_texture_file = "PVmizer/textures/wall.jpg"
        
        # Call parent constructor
        super().__init__(plotter, dimensions, theme)
        
        # Initialize roof using template method
        self.initialize_roof(dimensions)

    def create_roof_geometry(self):
        """Create the hip roof with properly mapped textures on all sides"""
        # Clear the plotter
        self.plotter.clear()
        
        # Define the corners of the roof base
        front_left = np.array([0, 0, 0])
        front_right = np.array([self.width, 0, 0])
        back_left = np.array([0, self.length, 0])
        back_right = np.array([self.width, self.length, 0])
        
        # Define the ridge points
        ridge_front = np.array([self.width/2, self.length*0.25, self.height])
        ridge_back = np.array([self.width/2, self.length*0.75, self.height])
        
        # Store all key points for later use
        self.roof_points = {
            'front_left': front_left,
            'front_right': front_right,
            'back_left': back_left,
            'back_right': back_right,
            'ridge_front': ridge_front,
            'ridge_back': ridge_back,
            'peak': ridge_front  # For compatibility with solar panel placement
        }
        
        # Create roof faces
        self._create_hip_roof_faces()
        
        # Add base and edges
        self.add_base(height=1.0)
        self.add_roof_edges()

    def _create_hip_roof_faces(self):
        """Create the four faces of the hip roof"""
        # Roof color for fallback
        roof_color = '#8B4513'
        texture_scale = 1.5
        
        # Load textures
        roof_texture, roof_texture_exists = self.load_texture_safely(self.roof_texture_file, roof_color)
        
        # Front triangular face
        front_points = np.array([
            self.roof_points['front_left'], 
            self.roof_points['front_right'], 
            self.roof_points['ridge_front']
        ])
        front_faces = np.array([3, 0, 1, 2])
        front_triangle = pv.PolyData(front_points, front_faces)
        
        front_tcoords = np.array([
            [0.0, 0.0],
            [texture_scale, 0.0],
            [texture_scale/2, texture_scale]
        ])
        front_triangle.active_texture_coordinates = front_tcoords
        
        # Back triangular face
        back_points = np.array([
            self.roof_points['back_left'], 
            self.roof_points['back_right'], 
            self.roof_points['ridge_back']
        ])
        back_faces = np.array([3, 0, 1, 2])
        back_triangle = pv.PolyData(back_points, back_faces)
        
        back_tcoords = np.array([
            [0.0, 0.0],
            [texture_scale, 0.0],
            [texture_scale/2, texture_scale]
        ])
        back_triangle.active_texture_coordinates = back_tcoords
        
        # Right side (two triangular faces)
        right_points1 = np.array([
            self.roof_points['front_right'], 
            self.roof_points['back_right'], 
            self.roof_points['ridge_front']
        ])
        right_faces1 = np.array([3, 0, 1, 2])
        right_triangle1 = pv.PolyData(right_points1, right_faces1)
        
        right_tcoords1 = np.array([
            [0.0, 0.0],
            [texture_scale, 0.0],
            [texture_scale*0.25, texture_scale]
        ])
        right_triangle1.active_texture_coordinates = right_tcoords1
        
        right_points2 = np.array([
            self.roof_points['back_right'], 
            self.roof_points['ridge_back'], 
            self.roof_points['ridge_front']
        ])
        right_faces2 = np.array([3, 0, 1, 2])
        right_triangle2 = pv.PolyData(right_points2, right_faces2)
        
        right_tcoords2 = np.array([
            [texture_scale, 0.0],
            [texture_scale*0.75, texture_scale],
            [texture_scale*0.25, texture_scale]
        ])
        right_triangle2.active_texture_coordinates = right_tcoords2
        
        # Left side (two triangular faces)
        left_points1 = np.array([
            self.roof_points['front_left'], 
            self.roof_points['ridge_front'], 
            self.roof_points['back_left']
        ])
        left_faces1 = np.array([3, 0, 1, 2])
        left_triangle1 = pv.PolyData(left_points1, left_faces1)
        
        left_tcoords1 = np.array([
            [0.0, 0.0],
            [texture_scale*0.25, texture_scale],
            [texture_scale, 0.0]
        ])
        left_triangle1.active_texture_coordinates = left_tcoords1
        
        left_points2 = np.array([
            self.roof_points['back_left'], 
            self.roof_points['ridge_back'], 
            self.roof_points['ridge_front']
        ])
        left_faces2 = np.array([3, 0, 1, 2])
        left_triangle2 = pv.PolyData(left_points2, left_faces2)
        
        left_tcoords2 = np.array([
            [texture_scale, 0.0],
            [texture_scale*0.75, texture_scale],
            [texture_scale*0.25, texture_scale]
        ])
        left_triangle2.active_texture_coordinates = left_tcoords2
        
        # Apply textures to all faces
        roof_meshes = [
            front_triangle, back_triangle,
            right_triangle1, right_triangle2,
            left_triangle1, left_triangle2
        ]
        
        for mesh in roof_meshes:
            if roof_texture_exists:
                self.plotter.add_mesh(mesh, texture=roof_texture, show_edges=False, smooth_shading=True)
            else:
                self.plotter.add_mesh(mesh, color=roof_texture, show_edges=True)

    def add_base(self, height=1.0):
        """Add a rectangular base (walls) under the hip roof"""
        # Get the roof eave points
        points = self.roof_points
        eave_front_left = points['front_left'].copy()
        eave_front_right = points['front_right'].copy()
        eave_back_left = points['back_left'].copy()
        eave_back_right = points['back_right'].copy()
        
        # Create base points (floor level)
        base_front_left = eave_front_left.copy()
        base_front_right = eave_front_right.copy()
        base_back_left = eave_back_left.copy()
        base_back_right = eave_back_right.copy()
        
        # Adjust z-coordinate for floor level
        base_front_left[2] -= height
        base_front_right[2] -= height
        base_back_left[2] -= height
        base_back_right[2] -= height
        
        # Store base points
        self.base_points = {
            'front_left': base_front_left,
            'front_right': base_front_right,
            'back_left': base_back_left,
            'back_right': base_back_right
        }
        
        # Create and add wall meshes
        self._create_base_walls(eave_front_left, eave_front_right, eave_back_left, eave_back_right,
                               base_front_left, base_front_right, base_back_left, base_back_right)

    def _create_base_walls(self, eave_fl, eave_fr, eave_bl, eave_br, base_fl, base_fr, base_bl, base_br):
        """Create the base walls of the building"""
        # Load wall texture
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file, "#E8DCC9")
        
        # Create wall meshes
        walls = [
            # Front wall
            pv.PolyData(np.array([base_fl, base_fr, eave_fr, eave_fl]), faces=[4, 0, 1, 2, 3]),
            # Back wall  
            pv.PolyData(np.array([base_bl, base_br, eave_br, eave_bl]), faces=[4, 0, 1, 2, 3]),
            # Left wall
            pv.PolyData(np.array([base_fl, base_bl, eave_bl, eave_fl]), faces=[4, 0, 1, 2, 3]),
            # Right wall
            pv.PolyData(np.array([base_fr, base_br, eave_br, eave_fr]), faces=[4, 0, 1, 2, 3])
        ]
        
        # Floor
        floor = pv.PolyData(np.array([base_fl, base_fr, base_br, base_bl]), faces=[4, 0, 1, 2, 3])
        
        # Apply textures
        wall_color = "#E8DCC9"
        for wall in walls:
            wall.texture_map_to_plane(inplace=True)
            wall.active_texture_coordinates *= np.array([2, 1])
            
            if wall_texture_exists:
                self.plotter.add_mesh(wall, texture=wall_texture, show_edges=False)
            else:
                self.plotter.add_mesh(wall, color=wall_color, show_edges=False)
        
        # Add floor
        self.plotter.add_mesh(floor, color="#8B7D6B", show_edges=False)

    def add_roof_edges(self):
        """Add edges to outline the roof structure"""
        # Define the corners of the roof base
        front_left = self.roof_points['front_left']
        front_right = self.roof_points['front_right']
        back_left = self.roof_points['back_left']
        back_right = self.roof_points['back_right']
        ridge_front = self.roof_points['ridge_front']
        ridge_back = self.roof_points['ridge_back']
        
        # Add ridge line
        ridge_line = pv.Line(ridge_front, ridge_back)
        self.plotter.add_mesh(ridge_line, color='black', line_width=3)
        
        # Add edges for better visualization
        edges = [
            (front_left, front_right),  # Front eave
            (front_right, back_right),  # Right eave
            (back_right, back_left),    # Back eave
            (back_left, front_left),    # Left eave
            (front_left, ridge_front),  # Front left hip
            (front_right, ridge_front), # Front right hip
            (back_right, ridge_back),   # Back right hip
            (back_left, ridge_back)     # Back left hip
        ]
        
        for start, end in edges:
            edge = pv.Line(start, end)
            self.plotter.add_mesh(edge, color='black', line_width=2)

    def setup_roof_specific_key_bindings(self):
        """Setup key bindings specific to hip/pyramid roof"""
        if self.solar_panel_handler:
            print("✅ Adding panel placement key bindings")
            
            # ✅ FIXED: Clear key bindings and add specific ones
            self.plotter.clear_events_for_key("1")
            self.plotter.clear_events_for_key("2") 
            self.plotter.clear_events_for_key("3")
            self.plotter.clear_events_for_key("4")
            
            # Add single key event per key
            self.plotter.add_key_event("1", lambda: self.debug_add_panels("front", "1-North"))
            self.plotter.add_key_event("2", lambda: self.debug_add_panels("right", "2-East"))
            self.plotter.add_key_event("3", lambda: self.debug_add_panels("back", "3-South"))
            self.plotter.add_key_event("4", lambda: self.debug_add_panels("left", "4-West"))
            
            self.plotter.add_key_event("c", self.safe_clear_panels)
            self.plotter.add_key_event("C", self.safe_clear_panels)

    def debug_add_panels(self, side, key_info):
        """Debug version to see what's being called"""
        print(f"🔍 Key pressed: {key_info} -> Adding panels to {side} side ONLY")
        self.safe_add_panels(side)


    def get_solar_panel_areas(self):
        """Get valid solar panel areas for hip roof"""
        return ["front", "right", "back", "left"]

    def get_solar_panel_handler_class(self):
        """Get the solar panel handler class for hip roof"""
        return SolarPanelPlacementHip if SOLAR_HANDLER_AVAILABLE else None

    def calculate_camera_position(self):
        """Calculate camera position for hip roof"""
        position = (self.width*2.0, -self.length*1.2, self.height*2.0)
        focal_point = (self.width/2, self.length/2, self.height/2)
        up_vector = (0, 0, 1)
        return position, focal_point, up_vector

    def _get_annotation_params(self):
        """Get parameters for RoofAnnotation"""
        return (self.length, self.width, self.height, self.slope_angle)

    def add_attachment_points(self):
        """Generate attachment points for hip roof obstacle placement"""
        try:
            # Initialize obstacle properties if not already done
            if not hasattr(self, 'obstacle_count'):
                self.obstacle_count = 0
                self.obstacles = []
                
            # Initialize selected_obstacle_type if not defined
            if not hasattr(self, 'selected_obstacle_type'):
                self.selected_obstacle_type = "Chimney"
                
            # Check if we've reached the maximum limit
            if self.obstacle_count >= 6:
                self.update_instruction(_('obstacle_max_reached'))
                return False
                
            # Clear existing attachment points if any
            if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                self.plotter.remove_actor(self.attachment_point_actor)
                self.attachment_point_actor = None
                
            # Reset attachment points data for this session
            self.attachment_points = []
            self.attachment_points_occupied = {}
            self.face_normals = {}
                
            # Flag to track if we've placed an obstacle in this session
            self.obstacle_placed_this_session = False
                
            # Use a moderate offset for attachment points
            offset_distance = 0.15  # 15cm offset
                
            # Get roof points from stored geometry
            points = self.roof_points
                
            # Extract key points from the roof
            peak = points['ridge_front']  # Use ridge_front as peak
            front_left = points['front_left']
            front_right = points['front_right']
            back_left = points['back_left']
            back_right = points['back_right']
            ridge_back = points['ridge_back']
                
            # Calculate face normals for each face of the hip roof
            # Front face normal (triangular face)
            v1_front = front_right - front_left
            v2_front = peak - front_left
            front_normal = np.cross(v1_front, v2_front)
            front_normal = front_normal / np.linalg.norm(front_normal)
            if front_normal[2] < 0:
                front_normal = -front_normal
                    
            # Right face normal (quadrilateral face)
            v1_right = peak - front_right
            v2_right = back_right - front_right
            right_normal = np.cross(v1_right, v2_right)
            right_normal = right_normal / np.linalg.norm(right_normal)
            if right_normal[2] < 0:
                right_normal = -right_normal
                    
            # Back face normal (triangular face)
            v1_back = back_left - back_right
            v2_back = ridge_back - back_right
            back_normal = np.cross(v1_back, v2_back)
            back_normal = back_normal / np.linalg.norm(back_normal)
            if back_normal[2] < 0:
                back_normal = -back_normal
                    
            # Left face normal (quadrilateral face)
            v1_left = ridge_back - back_left
            v2_left = front_left - back_left
            left_normal = np.cross(v1_left, v2_left)
            left_normal = left_normal / np.linalg.norm(left_normal)
            if left_normal[2] < 0:
                left_normal = -left_normal
                    
            # Store face info for later reference when placing obstacles
            self.roof_face_info = {
                'front': {
                    'normal': front_normal,
                    'points': [front_left, front_right, peak]
                },
                'right': {
                    'normal': right_normal,
                    'points': [front_right, back_right, ridge_back, peak]
                },
                'back': {
                    'normal': back_normal,
                    'points': [back_right, back_left, ridge_back]
                },
                'left': {
                    'normal': left_normal,
                    'points': [back_left, front_left, peak, ridge_back]
                }
            }
                
            point_index = 0
                
            # Helper function to check if a point is inside a triangular face
            def is_point_in_triangle(point, vertices):
                # Barycentric coordinate method
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

            # Generate points for each face
            for face_name, face_info in self.roof_face_info.items():
                normal = face_info['normal']
                face_points = face_info['points']
                
                if len(face_points) == 3:  # Triangular face
                    for u in np.linspace(0.1, 0.9, 5):
                        for v in np.linspace(0.1, 0.9, 5):
                            if u + v <= 1:  # Stay within triangle
                                # Barycentric coordinates for triangle
                                point = (1-u-v)*face_points[0] + u*face_points[1] + v*face_points[2]
                                # Add offset in normal direction
                                offset_point = point + normal * offset_distance
                                # Safety check
                                if offset_point[2] < point[2]:
                                    offset_point[2] = point[2] + 0.1
                                self.attachment_points.append(offset_point)
                                # Store the normal and face info for this point
                                self.face_normals[point_index] = {
                                    'normal': normal, 
                                    'face': face_name, 
                                    'roof_point': point
                                }
                                point_index += 1
                                
                else:  # Quadrilateral face
                    for u in np.linspace(0.1, 0.9, 5):
                        for v in np.linspace(0.1, 0.9, 5):
                            # Bilinear interpolation for quad
                            point = (1-u)*(1-v)*face_points[0] + u*(1-v)*face_points[1] + \
                                    (1-u)*v*face_points[3] + u*v*face_points[2]
                            # Add offset in normal direction
                            offset_point = point + normal * offset_distance
                            # Safety check
                            if offset_point[2] < point[2]:
                                offset_point[2] = point[2] + 0.1
                            self.attachment_points.append(offset_point)
                            # Store the normal and face info for this point
                            self.face_normals[point_index] = {
                                'normal': normal, 
                                'face': face_name, 
                                'roof_point': point
                            }
                            point_index += 1
            
            # Initialize tracking dictionary for attachment points
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
                
                # Add points to plotter
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

    def attachment_point_clicked(self, point, *args):
        """Handle click on attachment point - place ONE obstacle only"""
        # Check if we already placed an obstacle this session
        if hasattr(self, 'obstacle_placed_this_session') and self.obstacle_placed_this_session:
            self.update_instruction(_('obstacle_already_placed'))
            return
        
        # Check if obstacle type is selected
        if not hasattr(self, 'selected_obstacle_type') or not self.selected_obstacle_type:
            self.update_instruction(_('select_obstacle_type'))
            return
        
        # Find the closest attachment point
        closest_point_idx, closest_point = self.find_closest_attachment_point(point)
        
        # Safety check for valid point index
        if closest_point_idx is None:
            return
        
        # Check if this point is already occupied by a previous obstacle
        if self.is_point_occupied(closest_point):
            self.update_instruction(_('point_occupied'))
            return
        
        # Get the normal vector and roof point for this attachment point
        normal_vector = None
        roof_point = None
        face = None
        
        if closest_point_idx in self.attachment_points_occupied:
            normal_vector = self.attachment_points_occupied[closest_point_idx].get('normal')
            roof_point = self.attachment_points_occupied[closest_point_idx].get('roof_point')
            face = self.attachment_points_occupied[closest_point_idx].get('face')
        
        # Place the obstacle with orientation info
        obstacle = self.place_obstacle_at_point(
            closest_point, 
            self.selected_obstacle_type,
            normal_vector=normal_vector,
            roof_point=roof_point,
            face=face
        )
        
        # Add to obstacles list
        self.obstacles.append(obstacle)
        
        # Increment obstacle count
        self.obstacle_count += 1
        
        # Mark that we've placed an obstacle this session
        self.obstacle_placed_this_session = True
        
        # Disable further picking until "Add Obstacle" is pressed again
        self.plotter.disable_picking()
        
        # Remove attachment points
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.plotter.remove_actor(self.attachment_point_actor)
            self.attachment_point_actor = None
        
        # Update solar panels if they exist
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            # For Hip roof, we might have multiple active sides
            if hasattr(self.solar_panel_handler, 'active_sides'):
                active_sides = list(self.solar_panel_handler.active_sides)
                # Refresh panels on all active sides to account for the new obstacle
                for side in active_sides:
                    self.solar_panel_handler.remove_panels_from_side(side)
                    self.solar_panel_handler.add_panels(side)
        
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
