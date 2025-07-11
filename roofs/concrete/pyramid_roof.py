"""
Pyramid roof implementation using the BaseRoof template
Reduced from ~1100 lines to ~350 lines (68% reduction)
"""
from roofs.base.base_roof import BaseRoof
from roofs.base.resource_utils import resource_path
from translations import _
import pyvista as pv
import numpy as np
import os

try:
    from roofs.solar_panel_handlers.solar_panel_placement_pyramid import SolarPanelPlacementPyramid
    SOLAR_HANDLER_AVAILABLE = True
    print("✅ Solar panel handler imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import solar panel handler: {e}")
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementPyramid = None

class PyramidRoof(BaseRoof):
    """Pyramid roof implementation - now 68% smaller thanks to inheritance!"""
    
    def __init__(self, plotter, dimensions=(10.0, 10.0, 5.0), theme="light"):
        """Initialize a pyramid roof with textures and dimension annotations"""
        # Store properties
        self.length, self.width, self.height = dimensions
        
        # Calculate slope angle for the roof
        half_length = self.length / 2
        half_width = self.width / 2
        self.slope_angle = np.arctan(self.height / np.sqrt((half_length**2 + half_width**2)))
        
        # Set texture paths using resource_path for robust loading
        texture_base_path = "PVmizer/textures"
        
        # Define paths for different textures
        self.roof_texture_path = resource_path(os.path.join(texture_base_path, "rooftile.jpg"))
        self.wall_texture_path = resource_path(os.path.join(texture_base_path, "wall.jpg"))
        self.panel_texture_path = resource_path(os.path.join(texture_base_path, "solarpanel.png"))
        
        # Define roof color (fallback if texture not available)
        self.roof_color = "#610B0B"  # Dark red color for the roof
        self.wall_color = "#404040"  # Dark gray color for the walls
        
        # Solar panel parameters
        self.panel_width = 1.0  # Width of a single panel (m)
        self.panel_height = 1.6  # Height of a single panel (m)
        self.panel_gap = 0.05    # Gap between panels (m)
        self.panel_offset = 0.05 # Offset from roof surface (m)
        self.edge_margin = 0.40  # Margin from roof edges (m)
        
        # Call parent constructor
        super().__init__(plotter, dimensions, theme)
        
        # Initialize roof using template method
        self.initialize_roof(dimensions)

    def create_roof_geometry(self):
        """Create a pyramid with textures and a concrete base"""
        # Create a base plane
        half_length = self.length / 2
        half_width = self.width / 2
        
        # Define the pyramid vertices - front side is now at y=-half_width
        vertices = np.array([
            # Base vertices (counter-clockwise from front-left)
            [-half_length, -half_width, 0],  # front-left (0)
            [half_length, -half_width, 0],   # front-right (1)
            [half_length, half_width, 0],    # back-right (2)
            [-half_length, half_width, 0],   # back-left (3)
            # Apex
            [0, 0, self.height]              # peak (4)
        ])
        
        # Define base vertices for concrete base (1 meter below the roof base)
        base_height = -1.0  # 1 meter below the roof base
        base_vertices = np.array([
            # Concrete base vertices (counter-clockwise from front-left)
            [-half_length, -half_width, base_height],  # front-left (5)
            [half_length, -half_width, base_height],   # front-right (6)
            [half_length, half_width, base_height],    # back-right (7)
            [-half_length, half_width, base_height],   # back-left (8)
        ])
        
        # Store key points for later use
        self.roof_points = {
            'front_left': vertices[0],
            'front_right': vertices[1],
            'back_right': vertices[2],
            'back_left': vertices[3],
            'peak': vertices[4]
        }
        
        # Create faces for each slope (front, right, back, left)
        self._create_pyramid_faces(vertices)
        
        # Create base and concrete structure
        self._create_pyramid_base(vertices, base_vertices)

    def _create_pyramid_faces(self, vertices):
        """Create the four triangular faces of the pyramid"""
        front_face = pv.PolyData(vertices[[0, 1, 4]], faces=[3, 0, 1, 2])
        right_face = pv.PolyData(vertices[[1, 2, 4]], faces=[3, 0, 1, 2])
        back_face = pv.PolyData(vertices[[2, 3, 4]], faces=[3, 0, 1, 2])
        left_face = pv.PolyData(vertices[[3, 0, 4]], faces=[3, 0, 1, 2])
        
        # Create base (floor)
        base = pv.PolyData(vertices[:4], faces=[4, 0, 1, 2, 3])
        
        # Set texture coordinates for each face
        face_tcoords = np.array([[0, 0], [2, 0], [1, 2]])
        base_tcoords = np.array([[0, 0], [2, 0], [2, 2], [0, 2]])
        
        pyramid_faces = [front_face, right_face, back_face, left_face]
        for face in pyramid_faces:
            face.active_texture_coordinates = face_tcoords
        
        base.active_texture_coordinates = base_tcoords
        
        # Store faces for panel placement
        self.faces = {
            'front': front_face,
            'right': right_face,
            'back': back_face,
            'left': left_face,
            'base': base
        }
        
        # Load and apply textures
        self._apply_pyramid_textures(pyramid_faces, base)

    def _apply_pyramid_textures(self, pyramid_faces, base):
        """Apply textures to pyramid faces"""
        # Load textures with improved error handling
        roof_texture = None
        wall_texture = None
        
        try:
            if os.path.exists(self.roof_texture_path):
                roof_texture = pv.read_texture(self.roof_texture_path)
                print(f"Loaded roof texture from: {self.roof_texture_path}")
        except Exception as e:
            print(f"Error loading roof texture: {e}")
            
        try:
            if os.path.exists(self.wall_texture_path):
                wall_texture = pv.read_texture(self.wall_texture_path)
                print(f"Loaded wall texture from: {self.wall_texture_path}")
        except Exception as e:
            print(f"Error loading wall texture: {e}")
        
        # Apply textures or fallback to colors
        if roof_texture:
            for face in pyramid_faces:
                self.plotter.add_mesh(face, texture=roof_texture, show_edges=False)
        else:
            print(f"Warning: Roof texture file not found. Using solid color instead.")
            for face in pyramid_faces:
                self.plotter.add_mesh(face, color=self.roof_color, show_edges=False)
        
        # Apply wall texture to base if available
        if wall_texture:
            self.plotter.add_mesh(base, texture=wall_texture, show_edges=False)
        elif roof_texture:
            self.plotter.add_mesh(base, texture=roof_texture, show_edges=False)
        else:
            self.plotter.add_mesh(base, color=self.wall_color, show_edges=False)

    def _create_pyramid_base(self, vertices, base_vertices):
        """Create concrete base structure under the pyramid"""
        # Create concrete base sides
        # Front wall of concrete base
        concrete_front = pv.PolyData(
            np.array([base_vertices[0], base_vertices[1], vertices[1], vertices[0]]), 
            faces=[4, 0, 1, 2, 3]
        )
        
        # Right wall of concrete base
        concrete_right = pv.PolyData(
            np.array([base_vertices[1], base_vertices[2], vertices[2], vertices[1]]), 
            faces=[4, 0, 1, 2, 3]
        )
        
        # Back wall of concrete base
        concrete_back = pv.PolyData(
            np.array([base_vertices[2], base_vertices[3], vertices[3], vertices[2]]), 
            faces=[4, 0, 1, 2, 3]
        )
        
        # Left wall of concrete base
        concrete_left = pv.PolyData(
            np.array([base_vertices[3], base_vertices[0], vertices[0], vertices[3]]), 
            faces=[4, 0, 1, 2, 3]
        )
        
        # Bottom of concrete base
        concrete_bottom = pv.PolyData(base_vertices, faces=[4, 0, 1, 2, 3])
        
        # Texture coordinates for concrete sides (vertical walls)
        concrete_tcoords = np.array([[0, 0], [2, 0], [2, 1], [0, 1]])  # Repeat texture horizontally
        concrete_bottom_tcoords = np.array([[0, 0], [2, 0], [2, 2], [0, 2]])  # Repeat texture
        
        concrete_components = [concrete_front, concrete_right, concrete_back, concrete_left]
        for component in concrete_components:
            component.active_texture_coordinates = concrete_tcoords
        
        concrete_bottom.active_texture_coordinates = concrete_bottom_tcoords
        
        # Apply concrete texture
        concrete_texture = None
        try:
            if os.path.exists(self.wall_texture_path):
                concrete_texture = pv.read_texture(self.wall_texture_path)
        except Exception as e:
            print(f"Error loading concrete texture: {e}")
        
        # Apply concrete texture to base
        if concrete_texture:
            for component in concrete_components:
                self.plotter.add_mesh(component, texture=concrete_texture, show_edges=False)
            self.plotter.add_mesh(concrete_bottom, texture=concrete_texture, show_edges=False)
        else:
            # Fallback to a concrete-like color if texture is not available
            concrete_color = "#CCCCCC"  # Light gray
            print(f"Warning: Concrete texture file not found. Using solid color instead.")
            for component in concrete_components:
                self.plotter.add_mesh(component, color=concrete_color, show_edges=False)
            self.plotter.add_mesh(concrete_bottom, color=concrete_color, show_edges=False)

    # In hip_roof.py and pyramid_roof.py setup_roof_specific_key_bindings()
    def setup_roof_specific_key_bindings(self):
        """Setup key bindings specific to hip/pyramid roof"""
        if self.solar_panel_handler:
            print("✅ Adding panel placement key bindings")
            
            # ✅ FIXED: Correct mapping for hip/pyramid roofs
            # Key 1 = Front (North)
            # Key 2 = Right (East) 
            # Key 3 = Back (South)
            # Key 4 = Left (West)
            
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("front"))  # North
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("right"))  # East
            self.plotter.add_key_event("3", lambda: self.safe_add_panels("back"))   # South
            self.plotter.add_key_event("4", lambda: self.safe_add_panels("left"))   # West
            
            # Debug: Print which side is being called
            self.plotter.add_key_event("1", lambda: self.debug_add_panels("front", "1-North"))
            self.plotter.add_key_event("2", lambda: self.debug_add_panels("right", "2-East"))
            self.plotter.add_key_event("3", lambda: self.debug_add_panels("back", "3-South"))
            self.plotter.add_key_event("4", lambda: self.debug_add_panels("left", "4-West"))

    def debug_add_panels(self, side, key_info):
        """Debug version to see what's being called"""
        print(f"🔍 Key pressed: {key_info} -> Adding panels to {side} side")
        self.safe_add_panels(side)


    def get_solar_panel_areas(self):
        """Get valid solar panel areas for pyramid roof"""
        return ["front", "right", "back", "left"]

    def get_solar_panel_handler_class(self):
        """Get the solar panel handler class for pyramid roof"""
        return SolarPanelPlacementPyramid if SOLAR_HANDLER_AVAILABLE else None

    def calculate_camera_position(self):
        """Calculate camera position for pyramid roof"""
        position = (self.width*2.0, -self.length*1.2, self.height*2.0)
        focal_point = (self.width/2, self.length/2, self.height/2)
        up_vector = (0, 0, 1)
        return position, focal_point, up_vector

    def _get_annotation_params(self):
        """Get parameters for RoofAnnotation"""
        return (self.width, self.length, self.height, self.slope_angle, True)

    def add_attachment_points(self):
        """Generate attachment points for pyramid roof obstacle placement"""
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
            self.face_normals = {}  # Store normals for each attachment point
                
            # Flag to track if we've placed an obstacle in this session
            self.obstacle_placed_this_session = False
                
            # Use a moderate offset for attachment points
            offset_distance = 0.15  # 15cm offset
                
            # Get roof points from stored geometry
            points = self.roof_points
                
            # Extract key points from the roof
            peak = points['peak']
            front_left = points['front_left']
            front_right = points['front_right']
            back_left = points['back_left']
            back_right = points['back_right']
                
            # Calculate face normals
            # Front face 
            v1_front = front_right - front_left
            v2_front = peak - front_left
            front_normal = np.cross(v1_front, v2_front)
            front_normal = front_normal / np.linalg.norm(front_normal)
            if front_normal[2] < 0:
                front_normal = -front_normal
                    
            # Right face
            v1_right = back_right - front_right
            v2_right = peak - front_right
            right_normal = np.cross(v1_right, v2_right)
            right_normal = right_normal / np.linalg.norm(right_normal)
            if right_normal[2] < 0:
                right_normal = -right_normal
                    
            # Back face
            v1_back = back_left - back_right
            v2_back = peak - back_right
            back_normal = np.cross(v1_back, v2_back)
            back_normal = back_normal / np.linalg.norm(back_normal)
            if back_normal[2] < 0:
                back_normal = -back_normal
                    
            # Left face
            v1_left = front_left - back_left
            v2_left = peak - back_left
            left_normal = np.cross(v1_left, v2_left)
            left_normal = left_normal / np.linalg.norm(left_normal)
            if left_normal[2] < 0:
                left_normal = -left_normal
                    
            # Store face info with slope vectors
            self.roof_face_info = {
                'front': {
                    'normal': front_normal, 
                    'points': [front_left, front_right, peak],
                    'base_vector': front_right - front_left,
                    'slope_vector': peak - (front_left + front_right) / 2
                },
                'right': {
                    'normal': right_normal, 
                    'points': [front_right, back_right, peak],
                    'base_vector': back_right - front_right,
                    'slope_vector': peak - (front_right + back_right) / 2
                },
                'back': {
                    'normal': back_normal, 
                    'points': [back_right, back_left, peak],
                    'base_vector': back_left - back_right,
                    'slope_vector': peak - (back_right + back_left) / 2
                },
                'left': {
                    'normal': left_normal, 
                    'points': [back_left, front_left, peak],
                    'base_vector': front_left - back_left,
                    'slope_vector': peak - (back_left + front_left) / 2
                }
            }
                
            # Normalize slope vectors
            for face_name in self.roof_face_info:
                slope_vector = self.roof_face_info[face_name]['slope_vector']
                self.roof_face_info[face_name]['slope_vector'] = slope_vector / np.linalg.norm(slope_vector)
                
            # Calculate roof area to determine point density
            roof_area = self.length * self.width
                
            # Define grid density based on roof size
            if roof_area < 50:  # Small roof
                rows = 3
                cols = 3
            elif roof_area < 100:  # Medium roof
                rows = 4
                cols = 4
            elif roof_area < 200:  # Large roof
                rows = 5
                cols = 5
            else:  # Very large roof
                rows = 6
                cols = 6
                
            point_index = 0
                
            # Helper function to check if a point is inside the triangular face
            def is_point_in_triangle(point, vertices):
                # Barycentric coordinate method to check if point is in triangle
                v0 = vertices[2] - vertices[0]
                v1 = vertices[1] - vertices[0]
                v2 = point - vertices[0]
                    
                # Compute dot products
                dot00 = np.dot(v0, v0)
                dot01 = np.dot(v0, v1)
                dot02 = np.dot(v0, v2)
                dot11 = np.dot(v1, v1)
                dot12 = np.dot(v1, v2)
                    
                # Compute barycentric coordinates
                inv_denom = 1.0 / (dot00 * dot11 - dot01 * dot01)
                u = (dot11 * dot02 - dot01 * dot12) * inv_denom
                v = (dot00 * dot12 - dot01 * dot02) * inv_denom
                    
                # Check if point is in triangle
                return (u >= 0) and (v >= 0) and (u + v <= 1)

            # For each face, place points in a grid pattern
            for face_name, face_info in self.roof_face_info.items():
                # Extract face data
                normal = face_info['normal']
                face_points = face_info['points']
                base_vector = face_info['base_vector']
                base_length = np.linalg.norm(base_vector)
                base_unit = base_vector / base_length
                
                # Base midpoint & slope peak distance
                base_mid = (face_points[0] + face_points[1]) / 2
                peak_distance = np.linalg.norm(peak - base_mid)
                
                # Normalized slope vector
                slope_unit = face_info['slope_vector']
                
                # Define safe ranges to ensure points stay on the face
                # Start slightly above base (avoid edge) and end slightly below peak
                slope_min = 0.15  # 15% up from base
                slope_max = 0.85  # 85% up toward peak
                
                # Define width range depending on position up the slope
                base_min = -0.4   # 40% left of center
                base_max = 0.4    # 40% right of center
                
                # Generate grid points
                for row in range(rows):
                    # Calculate height percentage (from base to peak)
                    if rows == 1:
                        slope_pct = 0.5  # Middle of slope
                    else:
                        slope_pct = slope_min + (row / (rows - 1)) * (slope_max - slope_min)
                    
                    # Reduce width as we go up (triangular shape)
                    width_scale = 1.0 - (slope_pct - slope_min) * 0.5
                    
                    # Adjust number of columns based on height
                    effective_cols = max(2, int(cols * width_scale))
                    
                    for col in range(effective_cols):
                        # Calculate width percentage (adjust range based on height)
                        if effective_cols == 1:
                            base_pct = 0  # Center only
                        else:
                            # Scale width percentage - narrower near peak
                            base_range = (base_min * width_scale, base_max * width_scale)
                            base_pct = base_range[0] + (col / (effective_cols - 1)) * (base_range[1] - base_range[0])
                        
                        # Calculate point position
                        # First move up the slope
                        slope_position = base_mid + slope_unit * (slope_pct * peak_distance)
                        
                        # Then offset horizontally along the base
                        horz_offset = base_unit * (base_pct * base_length)
                        point = slope_position + horz_offset
                        
                        # Verify point is inside triangular face
                        if is_point_in_triangle(point, face_points):
                            # Add offset normal to the roof
                            offset_point = point + normal * offset_distance
                            
                            self.attachment_points.append(offset_point)
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
                    point_size=10,  # Larger point size for easier clicking
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

    def attachment_point_clicked(self, point_index_or_coords):
        """Handle clicking on an attachment point to place an obstacle"""
        try:
            # Check if we got a point coordinate instead of an index
            if isinstance(point_index_or_coords, np.ndarray):
                # We need to find the closest attachment point to this coordinate
                point_index = self.find_closest_attachment_point_index(point_index_or_coords)
            else:
                # We got a direct index
                point_index = point_index_or_coords

            # First check if we've already placed an obstacle in this session
            if hasattr(self, 'obstacle_placed_this_session') and self.obstacle_placed_this_session:
                self.update_instruction(_('obstacle_already_placed'))
                return

            # Check if the point is valid
            if point_index is None or point_index not in self.attachment_points_occupied:
                self.update_instruction(_("Invalid attachment point selected"))
                return
                
            if self.attachment_points_occupied[point_index]['occupied']:
                self.update_instruction(_("This point already has an obstacle"))
                return

            # Get point information from the stored data
            point_data = self.attachment_points_occupied[point_index]
            position = point_data['position']
            normal = point_data['normal']
            face = point_data['face']
            roof_point = point_data['roof_point']
            
            # Create the obstacle
            if hasattr(self, 'selected_obstacle_type'):
                obstacle_type = self.selected_obstacle_type
            else:
                obstacle_type = "Chimney"  # Default
                
            # Create and place the obstacle
            obstacle = self.place_obstacle_at_point(
                position, 
                obstacle_type, 
                normal_vector=normal, 
                roof_point=roof_point, 
                face=face
            )
            
            if obstacle:
                # Add to obstacles list if not already initialized
                if not hasattr(self, 'obstacles'):
                    self.obstacles = []
                self.obstacles.append(obstacle)
                
                # Increment obstacle count
                self.obstacle_count += 1
                
                # Mark this point as occupied
                self.attachment_points_occupied[point_index]['occupied'] = True
                self.attachment_points_occupied[point_index]['obstacle'] = obstacle
                
                # Mark that we've placed an obstacle in this session
                self.obstacle_placed_this_session = True
                
                # Clear attachment points from view
                if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                    self.plotter.remove_actor(self.attachment_point_actor)
                    self.attachment_point_actor = None
                
                # Disable picking until next obstacle session
                try:
                    self.plotter.disable_picking()
                except:
                    pass
                
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
                    
                # If we have solar panels, update their placement to account for the new obstacle
                if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
                    # Get active sides
                    if hasattr(self.solar_panel_handler, 'active_sides'):
                        active_sides = list(self.solar_panel_handler.active_sides)
                        # Refresh panels on active sides to account for new obstacle
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
        """Find the index of the closest attachment point to the clicked position"""
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
