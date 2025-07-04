import pyvista as pv
import numpy as np

class RoofObstacle:   
    def __init__(self, obstacle_type, position, roof, dimensions=None, normal_vector=None, roof_point=None, face=None):
        self.type = obstacle_type
        self.position = np.array(position) if not isinstance(position, np.ndarray) else position
        self.roof = roof
        
        # Store orientation information
        self.normal_vector = normal_vector
        self.roof_point = roof_point
        self.face = face
        
        # Default dimensions based on obstacle type
        default_dimensions = {
            "Chimney": (0.6, 0.6, 1.2),        # width, length, height
            "Roof Window": (1.0, 1.8, 0.15),   # width, length, height
            "Ventilation": (0.4, 0.4, 0.5)     # diameter, diameter, height
        }
        
        # Use provided dimensions or defaults
        self.dimensions = dimensions if dimensions else default_dimensions.get(obstacle_type, (0.5, 0.5, 0.5))
        
        # Actor reference
        self.actor = None
        
        # Initialize actors list for tracking
        self.actors = []
        
        # Initialize an invisible collision shape for consistent bounds detection
        self.collision_shape = self.create_collision_shape()
        
        # Create the 3D mesh for this obstacle
        self.mesh = self.create_mesh()
    
    def create_collision_shape(self):
        """Create a collision shape that matches the visual orientation"""
        if self.type == "Ventilation":
         
            return {
                "type": "cylinder",
                "radius": self.dimensions[0]/2,
                "height": self.dimensions[2],
                "position": np.array(self.position)
            }
        elif self.type == "Roof Window":

            normal = self.normal_vector
            if normal is None:
                normal = self.get_roof_normal_at_position()
            
            if normal is not None and not np.allclose(normal, [0, 0, 1]):
                # We have a non-vertical normal - use it for orientation
                return {
                    "type": "oriented_box",
                    "width": self.dimensions[0],
                    "length": self.dimensions[1],
                    "height": self.dimensions[2],
                    "position": np.array(self.position),
                    "normal": normal
                }
            else:
                # Fallback - horizontal box
                return {
                    "type": "box",
                    "width": self.dimensions[0],
                    "length": self.dimensions[1],
                    "height": self.dimensions[2],
                    "position": np.array(self.position)
                }
        else:
            # Chimney is always vertical
            return {
                "type": "box",
                "width": self.dimensions[0],
                "length": self.dimensions[1],
                "height": self.dimensions[2],
                "position": np.array(self.position)
            }
    
    def create_mesh(self):
        """Create a 3D mesh representation for this obstacle with proper orientation"""
        if self.type == "Chimney":
            return self.create_chimney_mesh()
        elif self.type == "Roof Window":
            return self.create_roof_window_mesh()
        elif self.type == "Ventilation":
            return self.create_ventilation_mesh()
        else:
            # Default - simple box
            return pv.Cube(
                center=self.position,
                x_length=self.dimensions[0],
                y_length=self.dimensions[1],
                z_length=self.dimensions[2]
            )
        
    def create_chimney_mesh(self):
        """Create just the main chimney body without lines"""
        # Get dimensions
        width = self.dimensions[0]
        length = self.dimensions[1]
        height = self.dimensions[2]
        
        # Create main body at exact position for accurate bounds
        main_body = pv.Cube(
            center=self.position,
            x_length=width,
            y_length=length,
            z_length=height
        )
        return main_body
        
    def create_roof_window_mesh(self):
        """Create a simplified roof window with just a glass panel"""
        # Get dimensions
        width = self.dimensions[0]
        length = self.dimensions[1]
        height = self.dimensions[2]
        center = self.position
        
        # Try to get a normal vector if not already provided
        normal = self.normal_vector if hasattr(self, 'normal_vector') else None
        if normal is None:
            # Try to get normal from the roof
            normal = self.get_roof_normal_at_position()
        
        # Check if we have a valid normal for orientation
        if normal is not None and np.linalg.norm(normal) > 0.001:
            # Create basis vectors for the window
            z_axis = normal / np.linalg.norm(normal)
            
            # For consistent orientation, use world up as reference
            world_up = np.array([0, 0, 1])
            
            # X-axis is perpendicular to normal and parallel to roof surface
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            
            # Y-axis completes the orthogonal basis
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            
            # Create rotation matrix
            rot_matrix = np.column_stack((x_axis, y_axis, z_axis))
            
            # Create 4x4 transformation matrix
            transform_matrix = np.eye(4)
            transform_matrix[:3, :3] = rot_matrix
            transform_matrix[:3, 3] = center
            
            # Create single glass panel
            glass = pv.Cube(
                center=(0, 0, 0),
                x_length=width,
                y_length=length,
                z_length=height * 0.3  # Make it thinner
            )
            
            # Apply transformation
            glass.transform(transform_matrix, inplace=True)
            
            return glass
        else:
            # Fallback: non-oriented window
            glass = pv.Cube(
                center=center,
                x_length=width,
                y_length=length,
                z_length=height * 0.3
            )
            
            return glass
        
    def create_ventilation_mesh(self):

        # Get dimensions
        diameter = self.dimensions[0]
        height = self.dimensions[2]
        center = self.position
        
        # Create a simple cylinder for ventilation
        ventilation = pv.Cylinder(
            center=center,
            direction=(0, 0, 1),  # Always vertical for simplicity
            radius=diameter/2,
            height=height
        )
        
        return ventilation
        
    def get_roof_normal_at_position(self):

        try:
            # If we already have a stored normal vector, use it
            if hasattr(self, 'normal_vector') and self.normal_vector is not None:
                return self.normal_vector
            
            # If face is provided, try to get normal from roof's face_normals
            if hasattr(self, 'face') and self.face and hasattr(self.roof, 'face_normals'):
                if self.face in self.roof.face_normals:
                    return self.roof.face_normals[self.face]
            
            # Determine roof type and use appropriate method to get normal
            roof_type = type(self.roof).__name__
            
            if roof_type == "HipRoof":
                # Hip roof handling
                try:
                    position = self.position
                    width = self.roof.width
                    length = self.roof.length
                    
                    # Determine which face this point is on
                    is_front_half = position[1] < length/2
                    is_left_half = position[0] < width/2
                    
                    if is_front_half:
                        if is_left_half:
                            face = "front"
                        else:
                            face = "right"
                    else:
                        if is_left_half:
                            face = "left"
                        else:
                            face = "back"
                    
                    # If the roof has face normals, use them
                    if hasattr(self.roof, 'roof_face_info') and face in self.roof.roof_face_info:
                        return self.roof.roof_face_info[face]['normal']
                except Exception as e:
                    print(f"Error determining hip roof face: {e}")
            
            elif roof_type == "GableRoof":
                # Gable roof handling
                try:
                    position = self.position
                    on_left_side = position[0] < self.roof.width / 2
                    
                    # Default 45 degree normals
                    left_normal = np.array([-1, 0, 1]) / np.sqrt(2)
                    right_normal = np.array([1, 0, 1]) / np.sqrt(2)
                    
                    # Try to get actual roof angle if available
                    roof_angle = None
                    if hasattr(self.roof, 'roof_angle'):
                        roof_angle = self.roof.roof_angle
                    elif hasattr(self.roof, 'angle'):
                        roof_angle = self.roof.angle
                        
                    # If we have a specific angle and it's not 45°, recalculate the normals
                    if roof_angle is not None and abs(roof_angle - 45.0) > 0.1:
                        angle_rad = np.radians(roof_angle)
                        # Create normals based on angle
                        left_normal = np.array([-np.sin(angle_rad), 0, np.cos(angle_rad)])
                        right_normal = np.array([np.sin(angle_rad), 0, np.cos(angle_rad)])
                    
                    # Return appropriate normal
                    if on_left_side:
                        return left_normal
                    else:
                        return right_normal
                except Exception as e:
                    print(f"Error determining gable roof normal: {e}")
            
            elif roof_type == "PyramidRoof":
                # Pyramid roof handling
                try:
                    # Get center of roof
                    if hasattr(self.roof, 'center'):
                        center = self.roof.center
                    else:
                        # Estimate center
                        center = np.array([self.roof.width/2, self.roof.length/2, 0])
                    
                    # Vector from center to position (horizontal only)
                    position = self.position
                    direction = np.array([position[0] - center[0], position[1] - center[1], 0])
                    
                    # Normalize
                    if np.linalg.norm(direction) > 0:
                        direction = direction / np.linalg.norm(direction)
                    else:
                        # If at center, use upward normal
                        return np.array([0, 0, 1])
                    
                    # Create normal that points outward and upward
                    normal = np.array([direction[0], direction[1], 1])
                    
                    # Normalize
                    normal = normal / np.linalg.norm(normal)
                    
                    return normal
                except Exception as e:
                    print(f"Error determining pyramid roof normal: {e}")
            
            # Default fallback - upward normal
            return np.array([0, 0, 1])
        
        except Exception as e:
            print(f"Error in get_roof_normal_at_position: {e}")
            # Always return a valid normal
            return np.array([0, 0, 1])
    
    def add_to_plotter(self, plotter):

        # Clear any existing actors to prevent duplicates
        self.remove_from_plotter(plotter)
        
        # Initialize actors list
        self.actors = []
        
        if self.type == "Chimney":
            if isinstance(self.mesh, pv.MultiBlock) and len(self.mesh) > 0:
                # Add main body with brick red color
                main_body = self.mesh[0]
                main_body_actor = plotter.add_mesh(
                    main_body,
                    color="#B22222",  # Firebrick red - classic brick color
                    opacity=1.0,
                    show_edges=True,   # Show edges for visual detail
                    edge_color="black" # Black edges
                )
                self.actors.append(main_body_actor)
                
                # Add brick lines with darker color
                for i in range(1, len(self.mesh)):
                    if self.mesh[i] is not None:
                        component_actor = plotter.add_mesh(
                            self.mesh[i],
                            color="#383838",  # Dark gray for mortar lines
                            opacity=1.0,
                            show_edges=False
                        )
                        self.actors.append(component_actor)
                
                # Store the main body actor as primary reference
                self.actor = main_body_actor
                print(f"Added chimney with {len(self.actors)} components")
            else:
                # Fallback for simple mesh
                self.actor = plotter.add_mesh(
                    self.mesh,
                    color="#B22222",  # Firebrick red
                    opacity=1.0,
                    show_edges=True
                )
                self.actors.append(self.actor)
        
        elif self.type == "Roof Window":
            # Add a single glass panel with nice styling
            glass_actor = plotter.add_mesh(
                self.mesh,
                color="#4682B4",  # SteelBlue - nice blue color for glass
                opacity=0.4,      # Translucent
                specular=1.0,
                specular_power=50,
                show_edges=True,
                edge_color="white"  # White edges for visibility
            )
            self.actors.append(glass_actor)
            self.actor = glass_actor
                
        elif self.type == "Ventilation":
            # Single mesh for ventilation
            vent_actor = plotter.add_mesh(
                self.mesh,
                color="#708090",  # Slate gray
                opacity=1.0,
                show_edges=True
            )
            self.actors.append(vent_actor)
            self.actor = vent_actor
        else:
            # Default
            self.actor = plotter.add_mesh(
                self.mesh,
                color="#A9A9A9",  # Dark gray
                opacity=0.9,
                show_edges=True
            )
            self.actors.append(self.actor)
            
        return self.actor
    
    def remove_from_plotter(self, plotter):
        """Remove all associated actors from the plotter with thorough cleanup"""
        actors_removed = 0
        
        # Remove all actors in our tracked list
        if hasattr(self, 'actors') and self.actors:
            for actor in self.actors:
                if actor is not None:
                    try:
                        plotter.remove_actor(actor)
                        actors_removed += 1
                    except Exception as e:
                        print(f"Warning: Failed to remove actor: {e}")
            
            # Clear the list
            self.actors = []
        
        # Also try removing main actor for backward compatibility
        if hasattr(self, 'actor') and self.actor is not None and (not hasattr(self, 'actors') or not self.actor in self.actors):
            # Only if not already removed in the actors list
            try:
                plotter.remove_actor(self.actor)
                actors_removed += 1
            except Exception:
                pass  # May have been removed already
            self.actor = None
        
        if actors_removed > 0:
            print(f"Removed {actors_removed} actors for {self.type}")
        
        # Force a render update
        plotter.render()
        
        return actors_removed
    
    def update_position(self, new_position):
        """Update the position of this obstacle"""
        # Calculate displacement vector
        displacement = np.array(new_position) - self.position
        
        # Update stored position
        self.position = np.array(new_position)
        
        # Update collision shape position
        self.collision_shape["position"] = np.array(new_position)
        
        # Move the mesh
        if hasattr(self.mesh, 'translate'):
            self.mesh.translate(displacement)
        elif isinstance(self.mesh, pv.MultiBlock):
            for i in range(len(self.mesh)):
                self.mesh[i].translate(displacement)
    
    def get_bounds(self):
        # Use collision shape for consistent bounds calculation
        shape = self.collision_shape
        pos = shape["position"]
        
        if shape["type"] == "cylinder":
            # For cylinder (ventilation)
            radius = shape["radius"]
            height = shape["height"]
            half_height = height / 2
            
            return (
                pos[0] - radius, pos[0] + radius,  # x min/max
                pos[1] - radius, pos[1] + radius,  # y min/max
                pos[2] - half_height, pos[2] + half_height  # z min/max
            )
        else:
            # For box shapes (chimney, window)
            width = shape["width"]
            length = shape["length"]
            height = shape["height"]
            
            half_width = width / 2
            half_length = length / 2
            half_height = height / 2
            
            return (
                pos[0] - half_width, pos[0] + half_width,  # x min/max
                pos[1] - half_length, pos[1] + half_length,  # y min/max
                pos[2] - half_height, pos[2] + half_height  # z min/max
            )
    
    def intersects_panel(self, panel_position, panel_width, panel_length, panel_normal):
        # Special handling for chimneys to avoid excessive blocking
        if self.type == "Chimney":
            return self._check_chimney_panel_intersection(panel_position, panel_width, panel_length, panel_normal)
        
         # Special handling for roof windows
        elif self.type == "Roof Window":
            return self._check_window_panel_intersection(panel_position, panel_width, panel_length, panel_normal)
        # Original collision logic for other obstacle types
        SAFETY_MARGIN = 0.05
        
        # Get shape info
        shape = self.collision_shape
        shape_type = shape["type"]
        pos = shape["position"]
        
        # Simple distance check for first filtering
        dx = panel_position[0] - pos[0]
        dy = panel_position[1] - pos[1]
        dz = panel_position[2] - pos[2]
        
        # Quick distance check - if centers are very far, no need for detailed check
        dist_sq = dx*dx + dy*dy + dz*dz
        max_panel_dim = max(panel_width, panel_length) / 2
        max_obj_dim = max(self.dimensions) / 2
        
        if dist_sq > (max_panel_dim + max_obj_dim + SAFETY_MARGIN) ** 2:
            return False  # Objects are far apart - quick reject
        
        # For vertical objects (ventilation), use simple checks
        if shape_type == "cylinder":
            # For ventilation - cylinder check
            radius = shape["radius"] + SAFETY_MARGIN
            height = shape["height"]
            
            # Simple distance check in horizontal plane
            if dx*dx + dy*dy > (radius + max_panel_dim) ** 2:
                return False  # Too far horizontally
            
            # Vertical distance check
            half_height = height / 2
            top_z = pos[2] + half_height
            bottom_z = pos[2] - half_height
            
            if panel_position[2] - max_panel_dim > top_z or panel_position[2] + max_panel_dim < bottom_z:
                return False  # Above or below cylinder
                
            return True  # Collision
            
        elif shape_type == "box":
            # For vertical box objects
            width = shape["width"] + SAFETY_MARGIN*2
            length = shape["length"] + SAFETY_MARGIN*2
            height = shape["height"]
            
            # Simple box check
            half_w = width/2
            half_l = length/2
            half_h = height/2
            
            if (abs(dx) > half_w + max_panel_dim or 
                abs(dy) > half_l + max_panel_dim or
                abs(dz) > half_h + max_panel_dim):
                return False  # Outside box bounds
                
            return True  # Potential collision
            
        elif shape_type == "oriented_box":
            # For oriented boxes (windows) - need to check in local space
            width = shape["width"] + SAFETY_MARGIN*2
            length = shape["length"] + SAFETY_MARGIN*2
            height = shape["height"] + SAFETY_MARGIN*2
            normal = shape["normal"]
            
            # Create local coordinate system based on normal
            z_axis = normal / np.linalg.norm(normal)
            
            # x-axis is perpendicular to normal and parallel to roof surface
            world_up = np.array([0, 0, 1])
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            
            # y-axis completes the orthogonal basis
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            
            # Transform panel position to local space of window
            local_pos = np.array([
                np.dot(panel_position - pos, x_axis),
                np.dot(panel_position - pos, y_axis),
                np.dot(panel_position - pos, z_axis)
            ])
            
            # Check if panel is inside the oriented box bounds
            if (abs(local_pos[0]) > width/2 + max_panel_dim or
                abs(local_pos[1]) > length/2 + max_panel_dim or
                abs(local_pos[2]) > height/2 + max_panel_dim):
                return False  
                
            return True  
            
        return False  
    
    def _check_chimney_panel_intersection(self, panel_position, panel_width, panel_length, panel_normal):
        # Get chimney position and dimensions
        chimney_pos = self.position
        
        if hasattr(self, 'dimensions'):
            chim_width, chim_length, chim_height = self.dimensions
        else:
            # Default dimensions if not available
            chim_width = chim_length = 0.6  # 60cm default size
        
        # Vector from panel center to chimney
        panel_to_chimney = chimney_pos - panel_position
        
        # Project this vector onto the panel's plane (remove normal component)
        dot_with_normal = np.dot(panel_to_chimney, panel_normal)
        projected_vector = panel_to_chimney - dot_with_normal * panel_normal
        
        # Horizontal distance in panel plane
        in_plane_distance = np.linalg.norm(projected_vector)
        
        # Initial quick check using distance
        panel_diagonal = np.sqrt(panel_width**2 + panel_length**2) / 2.0
        chimney_diagonal = np.sqrt(chim_width**2 + chim_length**2) / 2.0
        
        # Use a significantly smaller safety margin for chimneys (10cm)
        safety_margin = 0.10
        
        # Quick reject if clearly too far
        if in_plane_distance > panel_diagonal + chimney_diagonal + safety_margin:
            return False
                
        # If we have a panel normal, use it to create a local coordinate system
        if np.linalg.norm(panel_normal) > 0.001:
            # Create panel coordinate system
            z_axis = panel_normal / np.linalg.norm(panel_normal)
            
            # Get an x-axis perpendicular to the normal
            world_up = np.array([0, 0, 1])
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                # If normal is vertical, use world x-axis
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            
            # Get y-axis to complete the basis
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            
            # Project chimney-panel vector onto these axes
            x_dist = abs(np.dot(panel_to_chimney, x_axis))
            y_dist = abs(np.dot(panel_to_chimney, y_axis))
            
            # Check against dimensions plus safety margin
            x_overlap = x_dist < (panel_width/2 + chim_width/2 + safety_margin)
            y_overlap = y_dist < (panel_length/2 + chim_length/2 + safety_margin)
            
            return x_overlap and y_overlap
        
        # Fallback to simpler distance-based check if no normal is available
        return in_plane_distance < (panel_diagonal + chimney_diagonal + safety_margin)
    
    def _check_window_panel_intersection(self, panel_position, panel_width, panel_length, panel_normal):
        # Get window position and dimensions
        window_pos = self.position
        
        if hasattr(self, 'dimensions'):
            window_width, window_length, window_height = self.dimensions
        else:
            # Default dimensions if not available
            window_width, window_length = 1.0, 1.2  # 1.0m x 1.2m default size
        
        # Get window normal - crucial since windows follow roof slope
        window_normal = self.normal_vector
        if window_normal is None or np.linalg.norm(window_normal) < 0.001:
            window_normal = self.get_roof_normal_at_position()
            if window_normal is None or np.linalg.norm(window_normal) < 0.001:
                # Fallback to vertical if we can't determine the normal
                window_normal = np.array([0, 0, 1])
        
        # Check if panel and window are on the same plane (same roof face)
        normals_aligned = np.dot(window_normal, panel_normal) > 0.95  # cos(18°) ≈ 0.95
        
        # Vector from panel center to window
        panel_to_window = window_pos - panel_position
        
        # Use a smaller safety margin for windows (8cm)
        safety_margin = 0.08
        
        if normals_aligned:
            # Panel and window are on same plane - use precise 2D check
            
            # Project vector onto panel plane (remove normal component)
            dot_with_normal = np.dot(panel_to_window, panel_normal)
            projected_vector = panel_to_window - dot_with_normal * panel_normal
            
            # In-plane distance
            in_plane_distance = np.linalg.norm(projected_vector)
            
            # Initial quick check using distance
            panel_diagonal = np.sqrt(panel_width**2 + panel_length**2) / 2.0
            window_diagonal = np.sqrt(window_width**2 + window_length**2) / 2.0
            
            # Quick reject if clearly too far
            if in_plane_distance > panel_diagonal + window_diagonal + safety_margin:
                return False
            
            # For closer objects, create a coordinate system in the panel plane
            z_axis = panel_normal / np.linalg.norm(panel_normal)
            
            # Get an x-axis perpendicular to the normal
            world_up = np.array([0, 0, 1])
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                # If normal is vertical, use world x-axis
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            
            # Get y-axis to complete the basis
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            
            # Project window-panel vector onto these axes
            x_dist = abs(np.dot(panel_to_window, x_axis))
            y_dist = abs(np.dot(panel_to_window, y_axis))
            
            # Check against dimensions plus safety margin
            x_overlap = x_dist < (panel_width/2 + window_width/2 + safety_margin)
            y_overlap = y_dist < (panel_length/2 + window_length/2 + safety_margin)
            
            return x_overlap and y_overlap
        
        else:
            # Panel and window are on different planes
            # Create window's local coordinate system
            z_axis = window_normal / np.linalg.norm(window_normal)
            
            # Get an x-axis perpendicular to the normal
            world_up = np.array([0, 0, 1])
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                # If normal is vertical, use world x-axis
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            
            # Get y-axis to complete the basis
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            
            # Transform panel position to window's local coordinate system
            panel_local = np.array([
                np.dot(panel_position - window_pos, x_axis),
                np.dot(panel_position - window_pos, y_axis),
                np.dot(panel_position - window_pos, z_axis)
            ])
            
            # Check if panel is above the window in local z (perpendicular distance)
            # Windows are thin, so use a smaller check distance
            window_thickness = window_height + safety_margin
            
            # If panel is too far above window surface, no intersection
            if panel_local[2] > window_thickness + panel_width/2:
                return False
                
            # Check x-y distance in window plane
            local_xy_dist = np.sqrt(panel_local[0]**2 + panel_local[1]**2)
            max_dimension = max(window_width, window_length)/2 + max(panel_width, panel_length)/2 + safety_margin
            
            return local_xy_dist < max_dimension