import pyvista as pv
import numpy as np
import os
import sys
from pathlib import Path
from translations import _ 

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_paths = []
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_paths.append(sys._MEIPASS)
    except Exception:
        pass
    
    # Add the directory of the executable
    base_paths.append(os.path.dirname(sys.executable))
    
    # Add the _internal directory that auto-py-to-exe often creates
    base_paths.append(os.path.join(os.path.dirname(sys.executable), "_internal"))
    
    # Add current directory
    base_paths.append(os.path.abspath("."))
    
    # Try to find the file in each base path
    for base_path in base_paths:
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            print(f"Found resource at: {full_path}")
            return full_path
            
    # If we get here, log what we checked
    print(f"Resource not found: {relative_path}")
    print(f"Searched paths: {[os.path.join(bp, relative_path) for bp in base_paths]}")
    
    # Return the original path in the executable directory
    return os.path.join(os.path.dirname(sys.executable), relative_path)

class SolarPanelPlacementGable:
    """Handler for placing solar panels on a gable roof with language support."""
    
    def __init__(self, gable_roof):
        """Initialize solar panel placement handler for a gable roof."""
        self.gable_roof = gable_roof
        self.plotter = gable_roof.plotter
        
        # Panel parameters (all in millimeters)
        self.panel_width = 1000      # Width in mm (across the roof)
        self.panel_length = 1600     # Length in mm (up the roof)
        self.panel_gap = 50          # Gap between panels in mm
        self.panel_offset = 50       # Height above roof surface in mm
        self.horizontal_edge_offset = 300  # Offset from side edges in mm
        self.vertical_edge_offset = 300    # Offset from top/bottom edges in mm
        
        # Power-related parameters
        self.panel_power = 440       # Power rating of each panel in watts
        
        # Store all actors for easy removal
        self.panel_actors = []
        self.boundary_actors = []
        self.text_actor = None
        
        # Track current side for updates
        self.current_side = None
        self.panels_count_by_side = {
            'left': 0, 
            'right': 0
        }
        self.panels_skipped_by_side = {
            'left': 0, 
            'right': 0
        }
        
        # Initialize texture variables
        self.panel_texture = None
        self.panel_texture_file = None
        self.load_panel_texture()
            
        # Initialize debug variables
        self._debug_obstacle_actors = []
        self._debug_panel_actors = []
    
    def load_panel_texture(self):
        """Load the solar panel texture using resource_path for robust loading."""
        try:
            # Try first with PNG format
            texture_path = resource_path(os.path.join("textures", "solarpanel.png"))
            
            # If PNG not found, try JPG format
            if not os.path.exists(texture_path):
                texture_path = resource_path(os.path.join("textures", "solarpanel.jpg"))
            
            # Try to load the texture
            if os.path.exists(texture_path):
                self.panel_texture = pv.read_texture(texture_path)
                self.panel_texture_file = Path(texture_path)
                print(f"Loaded panel texture from: {texture_path}")
                return
            
            # If not found, try some alternative paths for backward compatibility
            alternative_paths = [
                os.path.join("PVmizer", "textures", "solarpanel.png"),
                os.path.join("PVmizer", "textures", "solarpanel.jpg"),
                os.path.join("textures", "solarpanel.png"),
                os.path.join("textures", "solarpanel.jpg")
            ]
            
            for path in alternative_paths:
                if os.path.exists(path):
                    try:
                        self.panel_texture = pv.read_texture(path)
                        self.panel_texture_file = Path(path)
                        print(f"Loaded panel texture from alternative path: {path}")
                        return
                    except Exception as e:
                        print(f"Error loading texture from {path}: {e}")
            
            # If we get here, we couldn't load the texture
            print("Solar panel texture not found, will use solid color instead.")
            self.panel_texture = None
            self.panel_texture_file = None
            
        except Exception as e:
            print(f"Error loading panel texture: {e}")
            import traceback
            traceback.print_exc()
            self.panel_texture = None
            self.panel_texture_file = None
            
    def add_panels(self, side):
        # Store current side for language updates
        self.current_side = side
        
        # Clear any existing panels
        self.clear_panels()
        
        # Reset panel counts for non-selected sides
        for s in self.panels_count_by_side:
            if s != side:
                self.panels_count_by_side[s] = 0
                self.panels_skipped_by_side[s] = 0
        
        # Place solar panels
        self.place_solar_panels(side)
    
    def place_solar_panels(self, side):
        """Place solar panels on the selected roof slope."""
        try:
            # Convert mm to meters for calculations
            mm_to_m = 0.001
            panel_width_m = self.panel_width * mm_to_m
            panel_length_m = self.panel_length * mm_to_m
            panel_gap_m = self.panel_gap * mm_to_m
            panel_offset_m = self.panel_offset * mm_to_m
            h_edge_offset_m = self.horizontal_edge_offset * mm_to_m
            v_edge_offset_m = self.vertical_edge_offset * mm_to_m
            
            # Get roof points based on side
            if side == "left":
                corners = [
                    self.gable_roof.roof_points['eave_left_front'],    # Bottom front
                    self.gable_roof.roof_points['eave_left_back'],     # Bottom back
                    self.gable_roof.roof_points['ridge_back'],         # Top back
                    self.gable_roof.roof_points['ridge_front']         # Top front
                ]
            else:  # right side
                corners = [
                    self.gable_roof.roof_points['eave_right_front'],   # Bottom front
                    self.gable_roof.roof_points['eave_right_back'],    # Bottom back
                    self.gable_roof.roof_points['ridge_back'],         # Top back
                    self.gable_roof.roof_points['ridge_front']         # Top front
                ]
            
            # Create vectors for the installation area
            horizontal_vector = corners[1] - corners[0]  # Along the bottom edge
            vertical_vector = corners[3] - corners[0]    # From bottom front to top front
            
            # Calculate unit vectors and lengths
            h_length = np.linalg.norm(horizontal_vector)
            v_length = np.linalg.norm(vertical_vector)
            
            h_unit = horizontal_vector / h_length
            v_unit = vertical_vector / v_length
            
            # Calculate normal vector for this face
            normal = np.cross(h_unit, v_unit)
            normal = normal / np.linalg.norm(normal)
            
            # Ensure normal points outward
            if normal[2] < 0:
                normal = -normal
            
            # Show installation boundaries
            boundary_corners = self.show_installation_area(
                corners[0], h_unit, v_unit, 
                h_length, v_length, normal, 
                h_edge_offset_m, v_edge_offset_m, panel_offset_m
            )
            
            # Calculate available area dimensions
            available_width = h_length - 2 * h_edge_offset_m
            available_height = v_length - 2 * v_edge_offset_m
            
            # FIXED: Calculate how many panels can fit - use width for horizontal dimension
            panels_horizontal = int((available_width + panel_gap_m) / (panel_width_m + panel_gap_m))
            panels_vertical = int((available_height + panel_gap_m) / (panel_length_m + panel_gap_m))
            
            # Center alignment
            total_h_space_needed = panels_horizontal * panel_width_m + (panels_horizontal - 1) * panel_gap_m
            total_v_space_needed = panels_vertical * panel_length_m + (panels_vertical - 1) * panel_gap_m
            
            h_offset = (available_width - total_h_space_needed) / 2
            v_offset = (available_height - total_v_space_needed) / 2
            
            # Updated start point for centered panels
            start_point = boundary_corners[0] + h_unit * h_offset + v_unit * v_offset
            
            # Place the panels
            panels_placed = self.place_panels(
                start_point, h_unit, v_unit, normal, 
                panels_horizontal, panels_vertical,
                panel_length_m, panel_width_m, panel_gap_m, panel_offset_m
            )
            
            # Calculate performance data
            perf_data = self.calculate_performance_data(panels_placed, side)
            
            # Update debug text
            self.update_debug_text(perf_data)
            
            return panels_placed
            
        except Exception as e:
            print(f"Error placing panels: {e}")
            import traceback
            traceback.print_exc()
    
    def show_installation_area(self, start_point, h_unit, v_unit, 
                              h_length, v_length, normal, 
                              h_edge_offset, v_edge_offset, panel_offset):
        """Visualize the installation area boundary with yellow markers."""
        # Clear existing boundary actors
        for actor in self.boundary_actors:
            self.plotter.remove_actor(actor)
        self.boundary_actors = []
        
        # Calculate the four corners with offsets
        offset_vector = normal * panel_offset
        
        # The four corners of the installation area
        adjusted_start = start_point + h_unit * h_edge_offset + v_unit * v_edge_offset + offset_vector
        adjusted_bottom_right = start_point + h_unit * (h_length - h_edge_offset) + v_unit * v_edge_offset + offset_vector
        adjusted_top_right = start_point + h_unit * (h_length - h_edge_offset) + v_unit * (v_length - v_edge_offset) + offset_vector
        adjusted_top_left = start_point + h_unit * h_edge_offset + v_unit * (v_length - v_edge_offset) + offset_vector
        
        corners = [adjusted_start, adjusted_bottom_right, adjusted_top_right, adjusted_top_left]
        
        # Create boundary lines with yellow color
        for i in range(4):
            line = pv.Line(corners[i], corners[(i+1)%4])
            actor = self.plotter.add_mesh(line, color="yellow", line_width=2)
            self.boundary_actors.append(actor)
        
        # Add marker spheres at each corner
        for point in corners:
            marker = pv.Sphere(radius=0.08, center=point)
            actor = self.plotter.add_mesh(marker, color="yellow", render_points_as_spheres=True)
            self.boundary_actors.append(actor)
        
        return corners
    
    def place_panels(self, start_point, h_unit, v_unit, normal, 
                 panels_h, panels_v, panel_length, panel_width, 
                 panel_gap, panel_offset):
        """Place panel meshes in the installation area using efficient instancing."""
        # Clear existing panel actors
        for actor in self.panel_actors:
            self.plotter.remove_actor(actor)
        self.panel_actors = []
        
        # Calculate offset vector for panel height above roof
        offset_vector = normal * panel_offset
        
        # Counter for panels actually placed and skipped
        panels_placed = 0
        panels_skipped = 0
        
        # Create a list to store valid panel positions and corners
        valid_panels = []
        
        # First, determine all valid panel positions
        for h in range(panels_h):
            for v in range(panels_v):
                # Use panel_width for horizontal dimension, panel_length for vertical
                h_pos = h * (panel_width + panel_gap)
                v_pos = v * (panel_length + panel_gap)
                
                # Panel corners with offset from roof
                panel_start = start_point + h_unit * h_pos + v_unit * v_pos + offset_vector
                
                # Calculate all four corners with correct dimensions
                top_left = panel_start
                top_right = panel_start + h_unit * panel_width
                bottom_left = panel_start + v_unit * panel_length
                bottom_right = bottom_left + h_unit * panel_width
                
                # Calculate panel center for obstacle check
                panel_center = panel_start + h_unit * (panel_width/2) + v_unit * (panel_length/2)
                
                # Check if panel intersects with any obstacles
                skip_panel = False
                if hasattr(self.gable_roof, 'obstacles') and self.gable_roof.obstacles:
                    for obstacle in self.gable_roof.obstacles:
                        if self.check_panel_obstacle_intersection(
                            panel_center, panel_width, panel_length, 
                            normal, h_unit, v_unit, obstacle
                        ):
                            skip_panel = True
                            panels_skipped += 1
                            break
                
                # Skip this panel if it intersects with an obstacle
                if skip_panel:
                    continue
                
                # Store valid panel corners
                valid_panels.append([top_left, top_right, bottom_right, bottom_left])
                panels_placed += 1
        
        # Store skipped panels data
        self.panels_skipped_by_side[self.current_side] = panels_skipped
        
        # If no valid panels, return
        if not valid_panels:
            print(f"No valid panel positions found on {self.current_side} side")
            return 0
        
        # ===== Create a single mesh with all panels =====
        
        # Create points array for all panel corners
        num_panels = len(valid_panels)
        points = np.vstack(valid_panels)
        
        # Create faces array (quad faces)
        faces = np.zeros((num_panels, 5), dtype=np.int64)
        for i in range(num_panels):
            idx = i * 4  # Each panel has 4 points
            faces[i] = np.array([4, idx, idx+1, idx+2, idx+3])
        
        # Flatten faces array for PolyData format
        faces_flat = np.hstack(faces)
        
        # Create polydata with all panels
        panels_mesh = pv.PolyData(points, faces=faces_flat)
        
        # Create texture coordinates
        tcoords = np.zeros((len(points), 2))
        for i in range(num_panels):
            idx = i * 4  # Each panel has 4 points
            tcoords[idx] = [0, 0]
            tcoords[idx+1] = [1, 0]
            tcoords[idx+2] = [1, 1]
            tcoords[idx+3] = [0, 1]
        
        panels_mesh.active_texture_coordinates = tcoords
        
        # Add the combined mesh to the scene
        if self.panel_texture is not None:
            actor = self.plotter.add_mesh(
                panels_mesh, 
                texture=self.panel_texture,
                show_edges=True,
                ambient=0.2,
                diffuse=0.8,
                specular=0.1
            )
        else:
            actor = self.plotter.add_mesh(
                panels_mesh, 
                color="#1F77B4", 
                show_edges=True,
                ambient=0.2,
                diffuse=0.8,
                specular=0.1
            )
        
        # Add to actor list for later removal
        self.panel_actors.append(actor)
        
        print(f"Placed {panels_placed} panels on {self.current_side} side, skipped {panels_skipped} due to obstacles")
        return panels_placed
    
    def check_panel_obstacle_intersection(self, panel_center, panel_width, panel_length, 
                                    normal, h_unit, v_unit, obstacle):
        """Check if a panel intersects with an obstacle with improved obstacle handling."""
        # First check if the obstacle is on the same roof face as the panel
        if hasattr(self, 'current_side') and hasattr(obstacle, 'side'):
            # If both have side information, we can directly compare
            if self.current_side != obstacle.side:
                # Obstacle is on a different side, no intersection
                return False
        
        # Special handling for chimneys to reduce blocking area
        if obstacle.type == "Chimney":
            intersects = self._check_chimney_intersection(
                panel_center, panel_width, panel_length, 
                normal, h_unit, v_unit, obstacle
            )
        # Special handling for roof windows
        elif obstacle.type == "Roof Window":
            intersects = self._check_window_intersection(
                panel_center, panel_width, panel_length, 
                normal, h_unit, v_unit, obstacle
            )
        else:
            # Standard distance-based check for other obstacles
            obstacle_pos = np.array(obstacle.position)
            distance = np.linalg.norm(panel_center - obstacle_pos)
            
            # Panel size 
            panel_radius = np.sqrt(panel_width**2 + panel_length**2) / 2
            
            # Obstacle size
            if hasattr(obstacle, 'dimensions'):
                obstacle_size = max(obstacle.dimensions) / 2
            else:
                obstacle_size = 0.5  # Default
            
            # Safety margin
            margin = 0.3  # 30cm
            
            intersects = distance < (panel_radius + obstacle_size + margin)
        
        # Track skipped panels if there's an intersection
        if intersects:
            # Make sure the panels_skipped_by_side dictionary exists
            if not hasattr(self, 'panels_skipped_by_side'):
                self.panels_skipped_by_side = {'left': 0, 'right': 0}
            
            # Get the current side
            current_side = getattr(self, 'current_side', 'left')  # Default to left if not set
            
            # Increment the skipped counter for this side
            self.panels_skipped_by_side[current_side] = self.panels_skipped_by_side.get(current_side, 0) + 1
        
        return intersects

    def _check_window_intersection(self, panel_center, panel_width, panel_length, 
                                normal, h_unit, v_unit, obstacle):
        """Check if a panel intersects with a roof window with narrower side boundaries."""
        try:
            # Get window properties
            window_pos = obstacle.position
            
            # Get window dimensions
            if hasattr(obstacle, 'dimensions'):
                window_width, window_length, window_height = obstacle.dimensions
            else:
                window_width, window_length = 1.0, 1.2  # Default
            
            # Check if this window is on the same face as the panel
            if hasattr(self, 'current_side') and hasattr(obstacle, 'side'):
                if self.current_side != obstacle.side:
                    # Obstacle is on a different side, no intersection
                    return False
            else:
                # No side information, try using normals
                if hasattr(obstacle, 'normal_vector'):
                    obstacle_normal = obstacle.normal_vector
                    # Calculate dot product (will be close to 1 if normals are parallel - same face)
                    panel_normal = normal / np.linalg.norm(normal)
                    obstacle_normal = obstacle_normal / np.linalg.norm(obstacle_normal)
                    dot_product = np.dot(panel_normal, obstacle_normal)
                    
                    # If dot product is less than 0.7 (~45 degrees), they're on different faces
                    if dot_product < 0.7:
                        # Not on the same face, skip this obstacle
                        return False
            
            # *** REDUCED MARGINS ***
            side_margin = 0.05       # Reduced from 10cm to 5cm
            top_margin = 0.05        # Keep at 5cm
            bottom_margin = 0.15     # Reduced from 20cm to 15cm
            
            # Calculate minimal shadow based on roof slope
            roof_slope = 0
            if hasattr(self.gable_roof, 'slope_angle'):
                roof_slope = self.gable_roof.slope_angle
                # Convert to radians if in degrees (roughly checking if value is large)
                if roof_slope > 1.6:  # Probably in degrees
                    roof_slope = np.radians(roof_slope)
            
            # Create local coordinate system around the window
            window_normal = normal  # Use panel normal as approximation
            if hasattr(obstacle, 'normal_vector'):
                window_normal = obstacle.normal_vector
                
            z_axis = window_normal / np.linalg.norm(window_normal)
            world_up = np.array([0, 0, 1])
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            y_axis = np.cross(z_axis, x_axis)
            y_axis = y_axis / np.linalg.norm(y_axis)
            
            # Transform panel center to window's local space
            panel_local = np.array([
                np.dot(panel_center - window_pos, x_axis),
                np.dot(panel_center - window_pos, y_axis),
                np.dot(panel_center - window_pos, z_axis)
            ])
            
            # *** REDUCED SHADOW LENGTH ***
            shadow_length = 0.20  # Reduced from 25cm to 20cm
            
            if roof_slope > 0.001:
                # Calculate shadow based on window height and slope (with more reduced factor)
                slope_shadow = np.tan(roof_slope) * window_height * 0.5  # Reduced from 60% to 50%
                shadow_length = max(shadow_length, slope_shadow)
                
                # Only add extra for very steep roofs
                if roof_slope > np.radians(45):  # Only for extremely steep roofs (>45°)
                    shadow_length += 0.05  # Reduced from 10cm to 5cm
            
            # *** DYNAMIC SIDE MARGIN BASED ON DISTANCE ***
            # Further reduce side margin for panels that are farther away
            distance_from_window = abs(panel_local[1])
            
            # Narrow the side margin for panels far from the window center
            if distance_from_window > window_length:
                # Reduce side margin proportionally to distance
                side_margin_factor = max(0.4, 1.0 - (distance_from_window - window_length) / window_length)
                side_margin *= side_margin_factor
            
            # Check if panel is downslope from window (negative y in local coords)
            if panel_local[1] < 0:
                # Narrower shadow zone with distance-based adjustment
                shadow_width = window_width/2 + side_margin * 0.5  # Further reduce width by 50%
                
                # Calculate shadow length based on distance (shorter shadow for farther panels)
                effective_shadow = shadow_length
                if distance_from_window > window_length:
                    # Reduce shadow length for distant panels
                    distance_factor = max(0.5, 1.0 - (distance_from_window - window_length) / (2*window_length))
                    effective_shadow *= distance_factor
                
                if (abs(panel_local[0]) <= shadow_width + panel_width/2 and
                    abs(panel_local[1]) <= effective_shadow + panel_length/2):
                    return True  # In shadow zone
            
            # Check if panel is in any direction but close to window
            half_width = window_width/2 + side_margin
            half_length_top = window_length/2 + top_margin
            half_length_bottom = window_length/2 + bottom_margin
            
            # Different checks depending on direction from window
            if panel_local[1] >= 0:  # Panel is above window in local coords
                # Check upper zone - smaller margin
                if (abs(panel_local[0]) <= half_width + panel_width/2 and
                    panel_local[1] <= half_length_top + panel_length/2):
                    return True
            else:  # Panel is below window in local coords
                # Check lower zone with distance-based margin
                effective_bottom_margin = bottom_margin
                if distance_from_window > window_length:
                    # Reduce bottom margin for distant panels
                    distance_factor = max(0.6, 1.0 - (distance_from_window - window_length) / (1.5*window_length))
                    effective_bottom_margin *= distance_factor
                
                half_length_bottom_effective = window_length/2 + effective_bottom_margin
                
                if (abs(panel_local[0]) <= half_width + panel_width/2 and
                    panel_local[1] >= -half_length_bottom_effective - panel_length/2):
                    return True
                    
            # No intersection detected
            return False
        
        except Exception as e:
            print(f"Error in _check_window_intersection: {e}")
            import traceback
            traceback.print_exc()
            # Be conservative on error
            return True 

    def _check_chimney_intersection(self, panel_center, panel_width, panel_length, 
                                normal, h_unit, v_unit, obstacle):
        """Check if a panel intersects with a chimney with improved face detection."""
        try:
            # First check if the chimney is on the same side as the panel
            if hasattr(self, 'current_side') and hasattr(obstacle, 'side'):
                if self.current_side != obstacle.side:
                    # Obstacle is on a different side, no intersection
                    return False
            else:
                # No side information, try using normals
                if hasattr(obstacle, 'normal_vector'):
                    obstacle_normal = obstacle.normal_vector
                    # Calculate dot product (will be close to 1 if normals are parallel - same face)
                    panel_normal = normal / np.linalg.norm(normal)
                    obstacle_normal = obstacle_normal / np.linalg.norm(obstacle_normal)
                    dot_product = np.dot(panel_normal, obstacle_normal)
                    
                    # If dot product is less than 0.7 (~45 degrees), they're on different faces
                    if dot_product < 0.7:
                        # Not on the same face, skip this obstacle
                        return False
            
            # Get chimney properties
            chimney_pos = obstacle.position
            
            # Get dimensions
            if hasattr(obstacle, 'dimensions'):
                chimney_width, chimney_length, chimney_height = obstacle.dimensions
            else:
                chimney_width = chimney_length = 0.6  # Default
                
            # Calculate margins - smaller for chimneys than windows
            safety_margin = 0.15  # 15cm
            
            # Get panel corners
            panel_half_width = panel_width / 2
            panel_half_length = panel_length / 2
            
            # Transform to 2D coordinates on the roof surface
            chimney_2d = np.array([
                np.dot(chimney_pos - panel_center, h_unit),
                np.dot(chimney_pos - panel_center, v_unit)
            ])
            
            # Calculate chimney bounds in 2D
            chimney_half_width = chimney_width / 2 + safety_margin
            chimney_half_length = chimney_length / 2 + safety_margin
            
            # Check for overlap in 2D
            if (abs(chimney_2d[0]) < panel_half_width + chimney_half_width and
                abs(chimney_2d[1]) < panel_half_length + chimney_half_length):
                return True
                
            # No overlap detected
            return False
            
        except Exception as e:
            print(f"Error in _check_chimney_intersection: {e}")
            import traceback
            traceback.print_exc()
            # Be conservative on error
            return True 
    def _calculate_angle_factor(self, angle_degrees):
        """Calculate efficiency factor based on roof angle."""
        if angle_degrees < 10:
            return 0.88  # Very shallow angle
        elif angle_degrees < 20:
            return 0.94
        elif angle_degrees < 30:
            return 0.98
        elif angle_degrees < 40:
            return 1.0   # Optimal range
        elif angle_degrees < 50:
            return 0.97
        elif angle_degrees < 60:
            return 0.91
        else:
            return 0.84  # Very steep angle
        
    def calculate_performance_data(self, panel_count, side):
        """Calculate solar performance data."""
        try:
            # Update the panels_count_by_side dictionary
            self.panels_count_by_side[side] = panel_count
            
            # Calculate system power based on total panels
            total_panels = sum(self.panels_count_by_side.values())
            panel_power_w = self.panel_power
            system_power_w = panel_power_w * total_panels
            system_power_kw = system_power_w / 1000
            
            # Get roof angle in degrees
            angle_rad = self.gable_roof.slope_angle
            angle_degrees = np.degrees(angle_rad)
            
            # Calculate angle efficiency factor
            angle_factor = self._calculate_angle_factor(angle_degrees)
            
            # Calculate chimney impact factor
            chimney_factor = self._calculate_chimney_impact_factor()
            
            # Estimate annual energy production with chimney impact
            annual_yield_base = 1200  # kWh per kWp per year (moderate climate)
            performance_ratio = 0.8   # System efficiency factor
            
            # Apply both factors to energy production calculation
            annual_energy_kwh = system_power_kw * annual_yield_base * performance_ratio * angle_factor * chimney_factor
            print(f"""
            Annual Energy Production Calculation:
            ------------------------------------
            System Size: {system_power_kw:.2f} kWp (kilowatt peak)
            Base Yield: {annual_yield_base} kWh/kWp/year (standard solar insolation)
            Performance Ratio: {performance_ratio:.2f} (system efficiency factor)
            Angle Factor: {angle_factor:.2f} (roof orientation efficiency)
            Chimney Factor: {chimney_factor:.2f} (shading impact)

            Calculation: {system_power_kw:.2f} kWp × {annual_yield_base} kWh/kWp × {performance_ratio:.2f} × {angle_factor:.2f} × {chimney_factor:.2f}
                    = {annual_energy_kwh:.1f} kWh/year

            Daily Average: {annual_energy_kwh/365:.1f} kWh/day

            Note: This calculation assumes standard solar insolation patterns that account for 
            day/night cycles and seasonal variations throughout the year.
            """)
            daily_energy_kwh = annual_energy_kwh / 365
            
            # Get total skipped panels
            total_skipped = sum(self.panels_skipped_by_side.values())
            
            # Create a data dictionary with all performance data
            perf_data = {
                'panel_count': total_panels,
                'panel_power_w': self.panel_power,
                'system_power_w': system_power_w,
                'system_power_kw': system_power_kw,
                'roof_angle_degrees': angle_degrees,
                'angle_factor': angle_factor,
                'chimney_factor': chimney_factor, 
                'annual_energy_kwh': annual_energy_kwh,
                'daily_energy_kwh': daily_energy_kwh,
                'side': side,
                'panels_skipped': total_skipped,
                'side_counts': {s: count for s, count in self.panels_count_by_side.items() if count > 0}
            }
            
            return perf_data
        except Exception as e:
            print(f"Error calculating performance data: {e}")
            # Return minimal data with side
            return {'panel_count': 0, 'side': side}
    
    def update_debug_text(self, perf_data):
        """Update the debug text with current panel information."""
        if self.text_actor:
            self.plotter.remove_actor(self.text_actor)
        
        # Guard against None
        if not perf_data:
            self.text_actor = self.plotter.add_text(
                "No panel data available",
                position="upper_left",
                font_size=12,
                color="black"
            )
            self.plotter.update()
            return
        
        # Format the text with translated strings
        side = perf_data.get('side', 'unknown')
        if side == "left":
            side_name = _('left_side')
        else:
            side_name = _('right_side')

        # Get skipped panel count
        skipped_panels = perf_data.get('panels_skipped', 0)

        
        # Build debug message with proper translations
        debug_msg = f"{_('selected_slope')}: {side_name}\n"
        debug_msg += f"{_('panels')}: {perf_data.get('panel_count', 0)}"

        # Add skipped panels info if any were skipped
        if skipped_panels > 0:
            debug_msg += f" ({_('skipped')} {skipped_panels} {_('due_to_obstacles')})\n"
        else:
            debug_msg += "\n"

        debug_msg += f"{_('panel_dimensions')}: {self.panel_width}mm x {self.panel_length}mm\n"
        debug_msg += f"{_('panel_gap')}: {self.panel_gap}mm\n"
        debug_msg += f"{_('slope_angle')}: {perf_data.get('roof_angle_degrees', 0):.1f}°\n\n"
        
        # Add power calculations
        debug_msg += f"{_('panel_power')}: {perf_data.get('panel_power_w', 0)}W\n"
        debug_msg += f"{_('system_size')}: {perf_data.get('system_power_kw', 0):.2f}kWp ({perf_data.get('system_power_w', 0):.0f}W)\n"
        debug_msg += f"{_('est_annual_production')}: {perf_data.get('annual_energy_kwh', 0):.0f}kWh\n"
        debug_msg += f"{_('est_daily_production')}: {perf_data.get('daily_energy_kwh', 0):.1f}kWh\n"
        debug_msg += f"{_('performance_factor')}: {perf_data.get('angle_factor', 0):.2f}\n"
        
        # Add info about obstacles if any were skipped
        if hasattr(self.gable_roof, 'obstacles') and self.gable_roof.obstacles:
            obstacle_count = len(self.gable_roof.obstacles)
            debug_msg += f"\n{_('obstacles_on_roof')}: {obstacle_count}"
            
            # Get skipped panel count from either source
            skipped_panels = perf_data.get('panels_skipped', 0)
            debug_msg += f"\n{_('panels_skipped')}: {skipped_panels}"
            
            # Add chimney impact factor if available
            if 'chimney_factor' in perf_data:
                chimney_impact = (1.0 - perf_data['chimney_factor']) * 100
                debug_msg += f"\n{_('chimney_impact')}: {chimney_impact:.1f}%"
        
        # Add the text to the plotter
        self.text_actor = self.plotter.add_text(
            debug_msg,
            position="upper_left",
            font_size=12,
            color="black"
        )
        
        # Make sure the changes are visible
        self.plotter.update()
    
    def clear_panels(self):
        """Remove all solar panels from the visualization."""
        # Remove all panel actors
        for actor in self.panel_actors:
            self.plotter.remove_actor(actor)
        self.panel_actors = []
        
        # Remove boundary visualization
        for actor in self.boundary_actors:
            self.plotter.remove_actor(actor)
        self.boundary_actors = []
        
        # Remove text display
        if self.text_actor:
            self.plotter.remove_actor(self.text_actor)
            self.text_actor = None
        
        # Update display
        self.plotter.update()
        print(_("all_panels_cleared"))
    
    def update_panel_config(self, panel_config):
        """Update panel configuration with new values."""
        if not panel_config:
            return True
            
        try:
            # Update panel dimensions (all in millimeters)
            if 'panel_width' in panel_config:
                self.panel_width = panel_config['panel_width']
            
            if 'panel_length' in panel_config:
                self.panel_length = panel_config['panel_length']
            
            if 'panel_gap' in panel_config:
                self.panel_gap = panel_config['panel_gap']
            
            if 'panel_offset' in panel_config:
                self.panel_offset = panel_config['panel_offset']
            
            if 'horizontal_edge_offset' in panel_config:
                self.horizontal_edge_offset = panel_config['horizontal_edge_offset']
            
            if 'vertical_edge_offset' in panel_config:
                self.vertical_edge_offset = panel_config['vertical_edge_offset']
            
            # Update panel power if provided
            if 'panel_power' in panel_config:
                self.panel_power = panel_config['panel_power']
            
            if self.current_side:
                self.add_panels(self.current_side)
            
            return True
            
        except Exception as e:
            print(f"Error updating panel configuration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _calculate_chimney_impact_factor(self):
        """Calculate impact factor from chimneys on system performance."""
        # Default impact factor (1.0 = no impact)
        impact_factor = 1.0
        
        # Check if the gable roof has obstacles
        if not hasattr(self.gable_roof, 'obstacles') or not self.gable_roof.obstacles:
            return impact_factor
        
        # Count chimneys
        chimney_count = 0
        total_chimney_size = 0
        
        # Current side being calculated
        current_side = self.current_side
        
        # Analyze each chimney
        for obstacle in self.gable_roof.obstacles:
            # Skip if not a chimney
            if obstacle.type != "Chimney":
                continue
                
            # Skip if not on the current side
            if hasattr(obstacle, 'side') and obstacle.side != current_side:
                continue
                
            # Count this chimney
            chimney_count += 1
            
            # Get chimney dimensions
            if hasattr(obstacle, 'dimensions'):
                chimney_width, chimney_length, chimney_height = obstacle.dimensions
                chimney_size = chimney_width * chimney_length
                
                # Consider height factor (taller chimneys create more shading)
                height_factor = min(1.5, max(1.0, chimney_height / 1.0))  # 1.0m is reference height
            else:
                # Default size estimate
                chimney_size = 0.36  # 0.6m × 0.6m
                height_factor = 1.0
                
            # Accumulate total size with height adjustment
            total_chimney_size += chimney_size * height_factor
        
        # No chimneys found on this side
        if chimney_count == 0:
            return impact_factor
        
        # Calculate impact - each chimney reduces efficiency by its relative footprint plus a shading factor
        
        # Estimate roof area
        roof_area = self.gable_roof.width * self.gable_roof.length / 2  # Half of total for one side
        
        # Base impact: 1-3% per chimney for general impact
        base_impact = 0.02 * chimney_count
        
        # Size impact: reduction based on relative size to roof area with shading factor
        shading_multiplier = 2.0  # Chimney affects 2x its area due to shading
        size_impact = (total_chimney_size * shading_multiplier) / roof_area
        
        # Combine impacts, ensuring we don't reduce by more than 25% from chimneys
        total_impact = min(0.25, base_impact + size_impact)
        
        # Final factor (reduces performance)
        impact_factor = 1.0 - total_impact
        
        return impact_factor
