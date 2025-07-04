from translations import _
import pyvista as pv
import numpy as np
import os
import sys
from pathlib import Path

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

class SolarPanelPlacementHip:
    """Handler for placing solar panels on a hip roof."""
    
    def __init__(self, hip_roof):
        """Initialize a solar panel placement handler for a hip roof."""
        self.hip_roof = hip_roof
        self.plotter = hip_roof.plotter
        
        # Panel parameters (all in millimeters)
        self.panel_width = 1000      # Width in millimeters (across the roof)
        self.panel_length = 1600     # Length in millimeters (up the roof)
        self.panel_gap = 50          # Gap between panels in millimeters
        self.edge_offset = 300       # Offset from roof edges in millimeters
        self.panel_height = 50       # Height above roof surface in millimeters
        
        # Performance attributes
        self.panel_power = 400       # Power rating in Watts
        self.panel_model = "Generic 400W"  # Panel model name
        self.performance_actor = None  # Actor for performance text display
        
        # Layout tracking attributes
        self.horizontal_length = 0   # Installation width in mm
        self.vertical_length = 0     # Installation height in mm
        self.num_panels_horizontal = 0  # Number of panels across
        self.num_panels_vertical = 0    # Number of panels up
        
        # Conversion factor from mm to m for rendering
        self.mm_to_m = 0.001
        
        # Track panels and boundaries by side
        self.panels_by_side = {
            "front": [],
            "right": [],
            "back": [],
            "left": []
        }
        self.boundaries_by_side = {
            "front": [],
            "right": [],
            "back": [],
            "left": []
        }
        self.panels_count_by_side = {
            "front": 0,
            "right": 0,
            "back": 0,
            "left": 0
        }
        
        # Track panels skipped due to obstacles
        self.panels_skipped_by_side = {
            "front": 0,
            "right": 0,
            "back": 0,
            "left": 0
        }
        
        # Set of active sides (max 2)
        self.active_sides = set()
        
        # Store debug actors for easy removal
        self.debug_actors = []
        self.text_actor = None
        self.help_text_actor = None
        
        # Add help text
        self.add_help_text()
        
        # Add tracking for current side
        self.current_side = None

        # Load the solar panel texture with improved handling
        self.panel_texture = None
        self.load_panel_texture()
    
    def load_panel_texture(self):
        """Load solar panel texture with robust path handling and error recovery."""
        try:
            # Try to find the texture using resource_path
            texture_paths = [
                os.path.join("textures", "solarpanel.png"),
                os.path.join("textures", "solarpanel.jpg"),
                os.path.join("PVmizer", "textures", "solarpanel.png"),
                os.path.join("PVmizer", "textures", "solarpanel.jpg")
            ]
            
            # Try each texture path
            for texture_path in texture_paths:
                try:
                    full_path = resource_path(texture_path)
                    if os.path.exists(full_path):
                        self.panel_texture = pv.read_texture(full_path)
                        print(f"Loaded solar panel texture from: {full_path}")
                        return
                except Exception as e:
                    print(f"Failed to load texture from {texture_path}: {e}")
            
            # If we get here, try legacy paths as a fallback
            legacy_paths = [
                "PVmizer/textures/solarpanel.png",
                "PVmizer/textures/solarpanel.jpg",
                "textures/solarpanel.png",
                "textures/solarpanel.jpg"
            ]
            
            for path in legacy_paths:
                if os.path.exists(path):
                    try:
                        self.panel_texture = pv.read_texture(path)
                        print(f"Loaded solar panel texture from legacy path: {path}")
                        return
                    except Exception as e:
                        print(f"Failed to load texture from legacy path {path}: {e}")
            
            # If we reach here, no texture was loaded
            print("No solar panel texture could be loaded. Using solid color instead.")
            self.panel_texture = None
            
        except Exception as e:
            print(f"Error in texture loading process: {e}")
            import traceback
            traceback.print_exc()
            self.panel_texture = None

    def add_panels(self, side):
        # Validate side
        if side not in ["front", "right", "back", "left"]:
            print(f"Invalid side: {side}")
            self.update_text(f"Invalid side: {side}\nChoose from front, right, back, left")
            return
        
        # If this side already has panels, remove them (toggle functionality)
        if side in self.active_sides:
            self.remove_panels_from_side(side)
            self.update_debug_display()
            return
            
        # If we're already at max sides, remove the oldest one
        if len(self.active_sides) >= 2:
            oldest_side = next(iter(self.active_sides))
            print(f"Maximum sides reached. Removing panels from {oldest_side} side.")
            self.remove_panels_from_side(oldest_side)
        
        # Set current side for panel placement
        self.current_side = side
        
        # Place panels on the selected slope
        if side == "front":
            self.place_front_panels()
        elif side == "right":
            self.place_right_panels()
        elif side == "back":
            self.place_back_panels()
        elif side == "left":
            self.place_left_panels()
        
        # Add to active sides
        self.active_sides.add(side)
        
        # Update the display
        self.plotter.render()
        self.update_debug_display()
    
    def remove_panels_from_side(self, side):
        """Remove panels from a specific side without affecting other sides."""
        print(f"Removing panels from {side} side")
        
        # Remove from active sides
        if side in self.active_sides:
            self.active_sides.remove(side)
        
        # Remove panel actors for this side
        for actor in self.panels_by_side[side]:
            if actor is not None:
                self.plotter.remove_actor(actor)
        self.panels_by_side[side] = []
        
        # Remove boundary actors for this side
        for actor in self.boundaries_by_side[side]:
            if actor is not None:
                self.plotter.remove_actor(actor)
        self.boundaries_by_side[side] = []
        
        # Reset panel count and skipped count
        self.panels_count_by_side[side] = 0
        self.panels_skipped_by_side[side] = 0

        self.update_debug_display()
    
    def place_front_panels(self):
        """Place solar panels on the front slope."""
        try:
            # Get roof coordinates
            points = self.hip_roof.roof_points
            eave_left = points['front_left']
            eave_right = points['front_right']
            ridge = points['ridge_front']
            
            # Create installation area with offsets
            bottom_left, bottom_right, top = self.create_triangular_boundary(
                eave_left, eave_right, ridge, is_front=True
            )
            
            # Place panels
            panel_count = self.place_panels_on_triangle(bottom_left, bottom_right, top)
            
            # Store the panel count
            self.panels_count_by_side["front"] = panel_count
            
        except Exception as e:
            print(f"Error placing front panels: {e}")
            import traceback
            traceback.print_exc()

    def place_right_panels(self):
        """Place solar panels on the right slope."""
        try:
            # Get roof coordinates
            points = self.hip_roof.roof_points
            eave_front = points['front_right']
            eave_back = points['back_right']
            ridge_front = points['ridge_front']
            ridge_back = points['ridge_back']
            
            # Create installation area with offsets
            bottom_front, bottom_back, top_back, top_front = self.create_trapezoidal_boundary(
                eave_front, eave_back, ridge_front, ridge_back, is_right=True
            )
            
            # Place panels
            panel_count = self.place_panels_on_trapezoid(bottom_front, bottom_back, top_back, top_front)
            
            # Store the panel count
            self.panels_count_by_side["right"] = panel_count
            
        except Exception as e:
            print(f"Error placing right panels: {e}")
            import traceback
            traceback.print_exc()

    def place_back_panels(self):
        """Place solar panels on the back slope."""
        try:
            # Get roof coordinates
            points = self.hip_roof.roof_points
            eave_left = points['back_left']
            eave_right = points['back_right']
            ridge = points['ridge_back']
            
            # Create installation area with offsets
            bottom_left, bottom_right, top = self.create_triangular_boundary(
                eave_left, eave_right, ridge, is_front=False
            )
            
            # Place panels
            panel_count = self.place_panels_on_triangle(bottom_left, bottom_right, top)
            
            # Store the panel count
            self.panels_count_by_side["back"] = panel_count
            
        except Exception as e:
            print(f"Error placing back panels: {e}")
            import traceback
            traceback.print_exc()

    def place_left_panels(self):
        """Place solar panels on the left slope."""
        try:
            # Get roof coordinates
            points = self.hip_roof.roof_points
            eave_front = points['front_left']
            eave_back = points['back_left']
            ridge_front = points['ridge_front']
            ridge_back = points['ridge_back']
            
            # Create installation area with offsets
            bottom_front, bottom_back, top_back, top_front = self.create_trapezoidal_boundary(
                eave_front, eave_back, ridge_front, ridge_back, is_right=False
            )
            
            # Place panels
            panel_count = self.place_panels_on_trapezoid(bottom_front, bottom_back, top_back, top_front)
            
            # Store the panel count
            self.panels_count_by_side["left"] = panel_count
            
        except Exception as e:
            print(f"Error placing left panels: {e}")
            import traceback
            traceback.print_exc()

    def create_triangular_boundary(self, eave_left, eave_right, ridge, is_front, min_offset=500):
        # Calculate vectors
        base_vector = eave_right - eave_left
        base_length = np.linalg.norm(base_vector)  # This is in meters
        base_dir = base_vector / base_length
        
        base_mid = (eave_left + eave_right) / 2
        height_vector = ridge - base_mid
        height_length = np.linalg.norm(height_vector)  # This is in meters
        height_dir = height_vector / height_length
        
        # Calculate normal vector (pointing outward)
        if is_front:
            normal = np.cross(base_dir, height_dir)
        else:
            normal = np.cross(height_dir, base_dir)
        normal = normal / np.linalg.norm(normal)
        
        # Ensure normal points outward
        if normal[2] < 0:
            normal = -normal
        
        # Convert roof dimensions to millimeters for calculations
        base_length_mm = base_length * 1000
        height_length_mm = height_length * 1000
        
        # Calculate dynamic offsets based on roof dimensions (in mm)
        horizontal_offset_mm = max(min_offset, base_length_mm * 0.20)  # 20% of width or min_offset
        vertical_offset_mm = max(min_offset, height_length_mm * 0.15)  # 15% of height or min_offset
        
        # Check available space (in mm)
        available_width_mm = base_length_mm - 2 * horizontal_offset_mm
        available_height_mm = height_length_mm - vertical_offset_mm - self.edge_offset
        
        # Adjust offsets if panels won't fit (in mm)
        if available_width_mm < self.panel_width + 2 * self.panel_gap:
            horizontal_offset_mm = max(200, (base_length_mm - self.panel_width - 2 * self.panel_gap) / 2)
            print(f"Reducing horizontal offset to {horizontal_offset_mm:.0f}mm to fit panels")
        
        if available_height_mm < self.panel_length + 2 * self.panel_gap:
            vertical_offset_mm = max(200, (height_length_mm - self.panel_length - 2 * self.panel_gap))
            print(f"Reducing vertical offset to {vertical_offset_mm:.0f}mm to fit panels")
        
        # Convert offsets back to meters for positioning
        horizontal_offset = horizontal_offset_mm * self.mm_to_m
        vertical_offset = vertical_offset_mm * self.mm_to_m
        edge_offset = self.edge_offset * self.mm_to_m
        panel_height = self.panel_height * self.mm_to_m
        
        # Calculate boundary points (in meters for PyVista)
        bottom_left = eave_left + base_dir * horizontal_offset + height_dir * edge_offset
        bottom_right = eave_right - base_dir * horizontal_offset + height_dir * edge_offset
        top = ridge - height_dir * vertical_offset
        
        # Elevate above roof surface (in meters)
        bottom_left = bottom_left + normal * panel_height
        bottom_right = bottom_right + normal * panel_height
        top = top + normal * panel_height
        
        # Create boundary visualization
        self.create_boundary([bottom_left, bottom_right, top])
        
        return bottom_left, bottom_right, top

    def create_trapezoidal_boundary(self, eave_front, eave_back, ridge_front, ridge_back, is_right, min_offset=300):
        # Calculate the side edges
        eave_vector = eave_back - eave_front
        eave_length = np.linalg.norm(eave_vector)  # meters
        eave_dir = eave_vector / eave_length
        
        ridge_vector = ridge_back - ridge_front
        ridge_length = np.linalg.norm(ridge_vector)  # meters
        ridge_dir = ridge_vector / ridge_length
        
        # Calculate height vectors
        front_height_vector = ridge_front - eave_front
        front_height_length = np.linalg.norm(front_height_vector)  # meters
        front_height_dir = front_height_vector / front_height_length
        
        back_height_vector = ridge_back - eave_back
        back_height_length = np.linalg.norm(back_height_vector)  # meters
        back_height_dir = back_height_vector / back_height_length
        
        # Calculate normal vector (pointing outward)
        if is_right:
            normal = np.cross(eave_dir, front_height_dir)
        else:
            normal = np.cross(front_height_dir, eave_dir)
        normal = normal / np.linalg.norm(normal)
        
        # Ensure normal points outward
        if normal[2] < 0:
            normal = -normal
        
        # Convert dimensions to millimeters for calculations
        eave_length_mm = eave_length * 1000
        ridge_length_mm = ridge_length * 1000
        front_height_mm = front_height_length * 1000
        back_height_mm = back_height_length * 1000
        
        # Calculate dynamic offsets based on roof dimensions (in mm)
        eave_offset_mm = max(min_offset, eave_length_mm * 0.10)  # 15% of width or min_offset
        ridge_offset_mm = max(min_offset, ridge_length_mm * 0.10)  # 15% of width or min_offset
        vertical_offset_mm = max(min_offset, min(front_height_mm, back_height_mm) * 0.10)  # 10% of height or min_offset
        
        # Convert offsets back to meters for positioning
        eave_offset = eave_offset_mm * self.mm_to_m
        ridge_offset = ridge_offset_mm * self.mm_to_m
        vertical_offset = vertical_offset_mm * self.mm_to_m
        edge_offset = self.edge_offset * self.mm_to_m
        panel_height = self.panel_height * self.mm_to_m
        
        # Calculate boundary points (in meters for PyVista)
        bottom_front = eave_front + eave_dir * eave_offset + front_height_dir * edge_offset
        bottom_back = eave_back - eave_dir * eave_offset + back_height_dir * edge_offset
        top_back = ridge_back - ridge_dir * ridge_offset - back_height_dir * vertical_offset
        top_front = ridge_front + ridge_dir * ridge_offset - front_height_dir * vertical_offset
        
        # Elevate above roof surface (in meters)
        bottom_front = bottom_front + normal * panel_height
        bottom_back = bottom_back + normal * panel_height
        top_back = top_back + normal * panel_height
        top_front = top_front + normal * panel_height
        
        # Create boundary visualization
        self.create_boundary([bottom_front, bottom_back, top_back, top_front])
        
        return bottom_front, bottom_back, top_back, top_front

    def create_boundary(self, points):
        """Create a highlighted boundary visualization."""
        # Clear any existing boundary actors for the current side
        if self.current_side:
            for actor in self.boundaries_by_side[self.current_side]:
                self.plotter.remove_actor(actor)
            self.boundaries_by_side[self.current_side] = []
        
        # Create boundary lines
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            line = pv.Line(start, end)
            actor = self.plotter.add_mesh(line, color="yellow", line_width=4)
            
            if self.current_side:
                # Add to the boundary list for the current side
                self.boundaries_by_side[self.current_side].append(actor)
        
        # Add corner markers
        for point in points:
            marker = pv.Sphere(radius=0.1, center=point)
            actor = self.plotter.add_mesh(marker, color="yellow", render_points_as_spheres=True)
            
            if self.current_side:
                # Add to the boundary list for the current side
                self.boundaries_by_side[self.current_side].append(actor)

    def create_instanced_panels(self, side, panel_positions):
        """Create a single instanced mesh from all panel positions for a given side."""
        if not panel_positions or len(panel_positions) == 0:
            return None
        
        # Create template panel
        panel_width_m = self.panel_width * self.mm_to_m
        panel_length_m = self.panel_length * self.mm_to_m
        
        template = pv.Plane(
            center=[0, 0, 0],
            direction=[0, 0, 1],
            i_size=panel_width_m,
            j_size=panel_length_m,
            i_resolution=1,
            j_resolution=1
        )
        
        # Set texture coordinates
        template.texture_coordinates = np.array([
            [0, 0], [1, 0], [1, 1], [0, 1]  # bottom-left, bottom-right, top-right, top-left
        ])
        
        # Create list for transformed panel meshes
        panel_meshes = []
        
        # Apply all transforms from panel positions
        for pos_data in panel_positions:
            center, width_dir, length_dir, normal = pos_data
            
            # Normalize vectors
            width_dir = width_dir / np.linalg.norm(width_dir)
            length_dir = length_dir / np.linalg.norm(length_dir)
            normal = normal / np.linalg.norm(normal)
            
            # Create coordinate system
            x_axis = width_dir
            z_axis = normal
            y_axis = np.cross(z_axis, x_axis)
            
            # Create transform matrix
            transform = np.eye(4)
            transform[0:3, 0] = x_axis
            transform[0:3, 1] = y_axis
            transform[0:3, 2] = z_axis
            transform[0:3, 3] = center
            
            # Copy and transform panel
            panel_copy = template.copy()
            panel_copy.transform(transform)
            panel_meshes.append(panel_copy)
        
        # Combine all panels into a single mesh
        if panel_meshes:
            blocks = pv.MultiBlock(panel_meshes)
            combined_mesh = blocks.combine()
            return combined_mesh
        
        return None

    def place_panels_on_triangle(self, bottom_left, bottom_right, top):
        """Place solar panels on a triangular surface with instancing optimization."""
        try:
            # Calculate main directions
            bottom_edge_vector = bottom_right - bottom_left
            bottom_edge_length = np.linalg.norm(bottom_edge_vector)  # meters
            bottom_edge_dir = bottom_edge_vector / bottom_edge_length

            # Vector from bottom edge midpoint to top
            bottom_mid = (bottom_left + bottom_right) / 2
            height_vector = top - bottom_mid
            height_length = np.linalg.norm(height_vector)  # meters
            height_dir = height_vector / height_length

            # Calculate normal vector for panel orientation
            normal = np.cross(bottom_edge_dir, height_dir)
            normal /= np.linalg.norm(normal)

            # Panel spacing (convert from mm to meters for placement)
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            panel_gap_m = self.panel_gap * self.mm_to_m
            
            vertical_spacing_m = panel_length_m + panel_gap_m
            horizontal_spacing_m = panel_width_m + panel_gap_m
            
            # Calculate how many rows will fit
            num_rows = max(1, int((height_length + panel_gap_m/2) / vertical_spacing_m))
            
            # Small offset to avoid boundary overlap
            vertical_start_offset_m = panel_gap_m/2

            # Track total panels placed and skipped
            count = 0
            skipped_panels = 0
            
            # Store panel positions for instancing
            panel_positions = []
            
            # Place panels row by row from bottom to top
            for row in range(num_rows):
                # Calculate position of this row from the bottom
                row_height_m = vertical_start_offset_m + row * vertical_spacing_m

                # Calculate center of this row
                row_center = bottom_mid + height_dir * row_height_m

                # Row width shrinks as we go up the triangle
                scale_factor = 1.0 - (row_height_m / height_length)
                row_width_m = bottom_edge_length * scale_factor
                
                # Apply edge inset (larger near the top)
                side_inset_m = panel_gap_m * (1 + row / max(1, num_rows - 1))
                usable_row_width_m = max(0, row_width_m - 2 * side_inset_m)

                # Calculate panels for this row
                num_panels_in_row = int((usable_row_width_m + panel_gap_m/2) / horizontal_spacing_m)

                # Skip rows too narrow for panels
                if num_panels_in_row < 1:
                    continue

                # Center panels in the row
                actual_width_used_m = num_panels_in_row * horizontal_spacing_m - panel_gap_m
                horizontal_start_offset_m = (usable_row_width_m - actual_width_used_m) / 2 + side_inset_m

                # Calculate left edge of row
                row_left_edge = row_center - bottom_edge_dir * (row_width_m / 2)
                row_start = row_left_edge + bottom_edge_dir * horizontal_start_offset_m

                # Place panels in this row
                for col in range(num_panels_in_row):
                    # Calculate panel center position
                    panel_center = (row_start +
                                bottom_edge_dir * (col * horizontal_spacing_m + panel_width_m / 2) +
                                height_dir * (panel_length_m / 2))

                    # Check if panel intersects with any obstacles
                    skip_panel = False
                    if hasattr(self.hip_roof, 'obstacles') and self.hip_roof.obstacles:
                        for obstacle in self.hip_roof.obstacles:
                            if self.check_panel_obstacle_intersection(
                                panel_center, 
                                bottom_edge_dir, 
                                height_dir, 
                                normal,
                                panel_width_m, 
                                panel_length_m, 
                                obstacle
                            ):
                                skip_panel = True
                                skipped_panels += 1
                                break
                    
                    # Skip this panel if it intersects with an obstacle
                    if skip_panel:
                        continue

                    # Store panel position for instancing
                    panel_positions.append((panel_center, bottom_edge_dir, height_dir, normal))
                    count += 1

            # Create instanced mesh from collected positions
            if panel_positions:
                combined_mesh = self.create_instanced_panels(self.current_side, panel_positions)
                
                # Remove any existing panels for this side
                if self.current_side in self.panels_by_side:
                    for actor in self.panels_by_side[self.current_side]:
                        if actor is not None:
                            self.plotter.remove_actor(actor)
                    self.panels_by_side[self.current_side] = []
                    
                # Add the combined mesh as a single actor
                if combined_mesh:
                    if self.panel_texture is not None:
                        try:
                            actor = self.plotter.add_mesh(
                                combined_mesh, 
                                texture=self.panel_texture, 
                                show_edges=True,
                                ambient=0.2,
                                diffuse=0.8,
                                specular=0.1
                            )
                        except Exception as e:
                            print(f"Error adding instanced panels with texture: {e}, using solid color")
                            actor = self.plotter.add_mesh(
                                combined_mesh, 
                                color="#1a1a2e", 
                                opacity=0.9, 
                                show_edges=True,
                                ambient=0.2,
                                diffuse=0.8,
                                specular=0.1
                            )
                    else:
                        actor = self.plotter.add_mesh(
                            combined_mesh, 
                            color="#1a1a2e", 
                            opacity=0.9, 
                            show_edges=True,
                            ambient=0.2,
                            diffuse=0.8,
                            specular=0.1
                        )
                    
                    # Store the actor for this side
                    self.panels_by_side[self.current_side] = [actor]
            
            # Store panel and skipped counts
            if self.current_side:
                self.panels_count_by_side[self.current_side] = count
                self.panels_skipped_by_side[self.current_side] = skipped_panels
            
            return count

        except Exception as e:
            print(f"Error placing panels on triangle: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def place_panels_on_trapezoid(self, bottom_front, bottom_back, top_back, top_front):
        """Place solar panels on a trapezoidal surface with instancing optimization."""
        try:
            # Calculate bottom edge
            bottom_edge = bottom_back - bottom_front
            bottom_length = np.linalg.norm(bottom_edge)
            bottom_dir = bottom_edge / bottom_length
            
            # Calculate top edge
            top_edge = top_back - top_front
            top_length = np.linalg.norm(top_edge)
            top_dir = top_edge / top_length
            
            # Calculate the midpoints and height direction
            bottom_mid = (bottom_front + bottom_back) / 2
            top_mid = (top_front + top_back) / 2
            
            # Height vector from bottom mid to top mid
            height_vector = top_mid - bottom_mid
            height_length = np.linalg.norm(height_vector)
            height_dir = height_vector / height_length
            
            # Calculate normal
            normal = np.cross(bottom_dir, height_dir)
            normal /= np.linalg.norm(normal)
            
            # Convert dimensions to meters
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            panel_gap_m = self.panel_gap * self.mm_to_m
            
            # Calculate spacing
            vertical_spacing_m = panel_length_m + panel_gap_m
            horizontal_spacing_m = panel_width_m + panel_gap_m
            
            # Calculate how many rows can fit
            num_rows = max(1, int((height_length - panel_gap_m) / vertical_spacing_m))
            
            # Small offset to start with
            vertical_start_offset_m = panel_gap_m
            
            # Track total panels placed and skipped
            count = 0
            skipped_panels = 0
            
            # Store panel positions for instancing
            panel_positions = []
            
            # Place panels row by row from bottom to top
            for row in range(num_rows):
                # Calculate height position of this row with proper spacing
                row_height_m = vertical_start_offset_m + row * vertical_spacing_m
                
                # Ensure we don't go beyond the top edge
                if row_height_m + panel_length_m > height_length:
                    break
                
                # Height ratio for interpolation (0 at bottom, 1 at top)
                height_ratio = row_height_m / height_length
                
                # Calculate row width by interpolating between bottom and top widths
                row_width_m = bottom_length * (1 - height_ratio) + top_length * height_ratio
                
                # Calculate row center position
                row_center = bottom_mid + height_dir * row_height_m
                
                # Calculate row direction (interpolate between bottom and top directions)
                row_dir = bottom_dir * (1 - height_ratio) + top_dir * height_ratio
                row_dir = row_dir / np.linalg.norm(row_dir)
                
                # Calculate edge inset
                side_inset_m = panel_gap_m * 1.5
                usable_row_width_m = max(0, row_width_m - 2 * side_inset_m)
                
                # Calculate how many panels fit in this row
                num_panels_in_row = int((usable_row_width_m + panel_gap_m/2) / horizontal_spacing_m)
                
                # Skip rows too narrow for panels
                if num_panels_in_row < 1:
                    continue
                
                # Center panels in the row
                actual_width_used_m = num_panels_in_row * horizontal_spacing_m - panel_gap_m
                horizontal_start_offset_m = (usable_row_width_m - actual_width_used_m) / 2 + side_inset_m
                
                # Calculate left edge of row
                row_left_edge = row_center - row_dir * (row_width_m / 2)
                row_start = row_left_edge + row_dir * horizontal_start_offset_m
                
                # Place panels in this row
                for col in range(num_panels_in_row):
                    # Calculate panel center position
                    panel_center = (row_start +
                                row_dir * (col * horizontal_spacing_m + panel_width_m / 2) +
                                height_dir * (panel_length_m / 2))
                    
                    # Check if panel intersects with any obstacles
                    skip_panel = False
                    if hasattr(self.hip_roof, 'obstacles') and self.hip_roof.obstacles:
                        for obstacle in self.hip_roof.obstacles:
                            if self.check_panel_obstacle_intersection(
                                panel_center, 
                                row_dir, 
                                height_dir, 
                                normal,
                                panel_width_m, 
                                panel_length_m, 
                                obstacle
                            ):
                                skip_panel = True
                                skipped_panels += 1
                                break
                    
                    # Skip this panel if it intersects with an obstacle
                    if skip_panel:
                        continue
                    
                    # Store panel position for instancing
                    panel_positions.append((panel_center, row_dir, height_dir, normal))
                    count += 1
            
            # Create instanced mesh from collected positions
            if panel_positions:
                combined_mesh = self.create_instanced_panels(self.current_side, panel_positions)
                
                # Remove any existing panels for this side
                if self.current_side in self.panels_by_side:
                    for actor in self.panels_by_side[self.current_side]:
                        if actor is not None:
                            self.plotter.remove_actor(actor)
                    self.panels_by_side[self.current_side] = []
                
                # Add the combined mesh as a single actor
                if combined_mesh:
                    if self.panel_texture is not None:
                        try:
                            actor = self.plotter.add_mesh(
                                combined_mesh, 
                                texture=self.panel_texture, 
                                show_edges=True,
                                ambient=0.2,
                                diffuse=0.8,
                                specular=0.1
                            )
                        except Exception as e:
                            print(f"Error adding instanced panels with texture: {e}, using solid color")
                            actor = self.plotter.add_mesh(
                                combined_mesh, 
                                color="#1a1a2e", 
                                opacity=0.9, 
                                show_edges=True,
                                ambient=0.2,
                                diffuse=0.8,
                                specular=0.1
                            )
                    else:
                        actor = self.plotter.add_mesh(
                            combined_mesh, 
                            color="#1a1a2e", 
                            opacity=0.9, 
                            show_edges=True,
                            ambient=0.2,
                            diffuse=0.8,
                            specular=0.1
                        )
                    
                    # Store the actor for this side
                    self.panels_by_side[self.current_side] = [actor]
            
            # Store panel and skipped counts
            if self.current_side:
                self.panels_count_by_side[self.current_side] = count
                self.panels_skipped_by_side[self.current_side] = skipped_panels
            
            return count
            
        except Exception as e:
            print(f"Error placing panels on trapezoid: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def add_panel(self, center, width_dir, length_dir, normal):
        """Add a solar panel at the specified location with texture."""
        try:
            # Normalize direction vectors
            width_dir = width_dir / np.linalg.norm(width_dir)
            length_dir = length_dir / np.linalg.norm(length_dir)
            normal = normal / np.linalg.norm(normal)
            
            # Convert panel dimensions from mm to meters for PyVista
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            
            # Create a rectangular panel
            panel = pv.Plane(
                center=[0, 0, 0],
                direction=[0, 0, 1],
                i_size=panel_width_m,
                j_size=panel_length_m,
                i_resolution=1,
                j_resolution=1
            )
            
            # Set texture coordinates
            tcoords = np.array([
                [0, 0],  # bottom-left
                [1, 0],  # bottom-right
                [1, 1],  # top-right
                [0, 1]   # top-left
            ])
            panel.texture_coordinates = tcoords
            
            # Create coordinate system for panel
            x_axis = width_dir
            z_axis = normal
            y_axis = np.cross(z_axis, x_axis)  # Ensure right-hand rule
            
            # Create transformation matrix
            transform = np.eye(4)
            transform[0:3, 0] = x_axis
            transform[0:3, 1] = y_axis
            transform[0:3, 2] = z_axis
            transform[0:3, 3] = center
            
            # Apply transformation
            panel.transform(transform)
            
            # Add panel to scene with texture or color
            if self.panel_texture is not None:
                try:
                    actor = self.plotter.add_mesh(
                        panel, 
                        texture=self.panel_texture, 
                        show_edges=True,
                        ambient=0.2,
                        diffuse=0.8,
                        specular=0.1
                    )
                except Exception as e:
                    print(f"Error adding panel with texture: {e}, using solid color")
                    actor = self.plotter.add_mesh(
                        panel, 
                        color="#1a1a2e", 
                        opacity=0.9, 
                        show_edges=True,
                        ambient=0.2,
                        diffuse=0.8,
                        specular=0.1
                    )
            else:
                actor = self.plotter.add_mesh(
                    panel, 
                    color="#1a1a2e", 
                    opacity=0.9, 
                    show_edges=True,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.1
                )
            
            # Store the actor for the current side
            if self.current_side:
                self.panels_by_side[self.current_side].append(actor)
            
        except Exception as e:
            print(f"Error in add_panel: {e}")
            import traceback
            traceback.print_exc()

    def clear_panels(self):
        """Remove all panels and boundary visualizations from all sides."""
        try:
            # Clear each side
            for side in self.panels_by_side:
                # Remove panel actors
                for actor in self.panels_by_side[side]:
                    if actor is not None:
                        self.plotter.remove_actor(actor)
                self.panels_by_side[side] = []
                
                # Remove boundary actors
                for actor in self.boundaries_by_side[side]:
                    if actor is not None:
                        self.plotter.remove_actor(actor)
                self.boundaries_by_side[side] = []
                
                # Reset panel count
                self.panels_count_by_side[side] = 0
            
            # Clear active sides set
            self.active_sides.clear()
            self.current_side = None
            
            # Remove debug actors
            for actor in self.debug_actors:
                if actor is not None:
                    self.plotter.remove_actor(actor)
            self.debug_actors = []
            
            # Remove text actor if it exists
            if self.text_actor:
                self.plotter.remove_actor(self.text_actor)
                self.text_actor = None
            
            # Update text
            self.update_debug_display()
            
            # Update display
            self.plotter.render()
        except Exception as e:
            print(f"Error clearing panels: {e}")
            import traceback
            traceback.print_exc()
    
    def update_text(self, message):
        """Update or create status text."""
        try:
            # Remove existing text actor if it exists
            if self.text_actor:
                self.plotter.remove_actor(self.text_actor)
                self.text_actor = None
            
            # Create new text
            self.text_actor = self.plotter.add_text(
                message, 
                position="lower_right",
                font_size=12, 
                color="black"
            )
            
            # Ensure the update is visible
            self.plotter.render()
        except Exception as e:
            print(f"Error updating text: {e}")
    
    def add_help_text(self):
        """Add comprehensive help text for hip roof visualization."""
        # First, remove any existing help text
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            self.plotter.remove_actor(self.help_text_actor)
            self.help_text_actor = None
        
        # Also remove any help text from the HipRoof if it exists
        if hasattr(self.hip_roof, 'help_text_actor') and self.hip_roof.help_text_actor:
            self.plotter.remove_actor(self.hip_roof.help_text_actor)
            self.hip_roof.help_text_actor = None
        
        # Create comprehensive help text for hip roof
        help_text = (
             f"{_('help_hip_roof_title')}\n"
            f"{_('help_place_front_panels')}\n"
            f"{_('help_place_right_panels')}\n"
            f"{_('help_place_back_panels')}\n"
            f"{_('help_place_left_panels')}\n"
            f"{_('help_max_two_sides')}\n"
            f"{_('help_clear_panels')}\n"
            f"\n"
            f"{_('roof_obstacles')}:\n"
            f"{_('click_on_black_dot')}\n"
            f"{_('help_remove_obstacles')}\n"
            f"\n"
            f"{_('help_view_controls_title')}\n"
            f"{_('help_reset_camera')}\n"
            f"{_('help_save_screenshot')}\n"
            f"{_('help_toggle_menu')}"
        )
        
        self.help_text_actor = self.plotter.add_text(
            help_text,
            position="upper_right",
            font_size=12,
            color="black"
        )
        self.help_visible = True
        
        # Update the HipRoof's help visibility state to match
        self.hip_roof.help_visible = True
        
    def toggle_help(self):
        """Toggle visibility of help text."""
        if self.help_visible:
            if self.help_text_actor:
                self.plotter.remove_actor(self.help_text_actor)
                self.help_text_actor = None
            self.help_visible = False
        else:
            self.add_help_text()
            self.help_visible = True
        
        self.plotter.render()
    
    def update_panel_config(self, config):
        """Update panel configuration without toggling panels."""
        try:
            print(f"SolarPanelPlacementHip: Updating panel config")
            
            # Store which sides currently have panels 
            active_sides_before = list(self.active_sides)
            print(f"Current active sides: {active_sides_before}")
            
            # Save camera position
            camera_pos = self.plotter.camera_position

            # Update configuration values
            if 'panel_length' in config:
                self.panel_length = float(config['panel_length'])
            if 'panel_width' in config:
                self.panel_width = float(config['panel_width'])
            if 'panel_gap' in config:
                self.panel_gap = float(config['panel_gap'])
            if 'panel_power' in config:
                self.panel_power = float(config['panel_power'])
            if 'panel_model' in config:
                self.panel_model = config['panel_model']
                
            # Only proceed if we have active panels
            if not active_sides_before:
                print("No active sides to update")
                return True
                
            # For each active side, manually remove all panel actors
            for side in active_sides_before:
                # Remove panel actors from scene
                for actor in self.panels_by_side[side]:
                    if actor is not None:
                        self.plotter.remove_actor(actor)
                self.panels_by_side[side] = []
                
                # Remove boundary actors from scene
                for actor in self.boundaries_by_side[side]:
                    if actor is not None:
                        self.plotter.remove_actor(actor)
                self.boundaries_by_side[side] = []
            
            # Directly rebuild panels on each side
            for side in active_sides_before:
                # Reset this side's collection
                self.panels_by_side[side] = []
                self.boundaries_by_side[side] = []
                
                # Set current side
                self.current_side = side
                
                # Call direct placement method, ensuring we store a valid count
                panel_count = 0
                if side == "front":
                    result = self.place_front_panels()
                    panel_count = result if isinstance(result, int) else 0
                elif side == "right":
                    result = self.place_right_panels()
                    panel_count = result if isinstance(result, int) else 0
                elif side == "back":
                    result = self.place_back_panels()
                    panel_count = result if isinstance(result, int) else 0
                elif side == "left":
                    result = self.place_left_panels()
                    panel_count = result if isinstance(result, int) else 0
                    
                # Store the valid panel count
                self.panels_count_by_side[side] = panel_count
                
                # Only add to active sides if panels were placed
                if panel_count > 0:
                    self.active_sides.add(side)
                else:
                    # If no panels were placed, remove from active sides
                    if side in self.active_sides:
                        self.active_sides.remove(side)
                
            # Restore camera and update display
            self.plotter.camera_position = camera_pos
            self.update_debug_display()
            self.plotter.render()
            
            print(f"Panel config updated. Active sides: {self.active_sides}")
            return True
            
        except Exception as e:
            print(f"Error updating panel config: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def calculate_performance(self):
        """Calculate solar system performance metrics."""
        # Get the total number of panels
        panel_count = sum(self.panels_count_by_side.values())
        
        # Can't calculate if no panels placed or no power rating
        if panel_count == 0 or not hasattr(self, 'panel_power') or self.panel_power <= 0:
            return None
        
        # Calculate total capacity in kW
        system_capacity_kw = (panel_count * self.panel_power) / 1000  # Convert W to kW
        total_power_w = panel_count * self.panel_power
        
        # Get the slope angle from the roof
        # For hip roofs, try to get the angle from the roof object
        roof_angle_rad = 30  # Default angle in degrees
        
        # Try to get the actual angle if available
        if hasattr(self.hip_roof, 'slope_angle'):
            roof_angle_rad = self.hip_roof.slope_angle
        
        # Convert to degrees if in radians
        roof_angle_deg = roof_angle_rad
        if roof_angle_rad < 1.6:  # Probably in radians
            roof_angle_deg = np.degrees(roof_angle_rad)
        
        # Calculate angle factor (efficiency based on roof angle)
        angle_factor = self._calculate_angle_factor(roof_angle_deg)
        
        # Calculate chimney impact factor (new)
        chimney_factor = self._calculate_chimney_impact_factor()
        
        # Basic insolation model - annual kWh per kW installed capacity
        base_annual_yield = 1200  # kWh per kWp per year (moderate climate)
        performance_ratio = 0.8
        
        # Apply both factors to energy production calculation
        annual_energy_kwh = system_capacity_kw * base_annual_yield * performance_ratio * angle_factor * chimney_factor
        daily_energy_kwh = annual_energy_kwh / 365
        
        # Return performance data
        perf_data = {
            'panel_count': panel_count,
            'panel_power_w': self.panel_power,
            'system_power_kw': system_capacity_kw,
            'system_power_w': total_power_w,
            'annual_energy_kwh': annual_energy_kwh,
            'daily_energy_kwh': daily_energy_kwh,
            'roof_angle_degrees': roof_angle_deg,
            'angle_factor': angle_factor,
            'chimney_factor': chimney_factor,  # Add chimney factor to data dict
            'side_counts': {side: count for side, count in self.panels_count_by_side.items() if count > 0}
        }
        
        return perf_data

    def _calculate_angle_factor(self, angle_degrees):
        """Calculate efficiency factor based on roof angle."""
        # Simplified model - optimal angle is around 35 degrees
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

    def update_debug_display(self):
        """Update the debug display with current panel information in the current language."""
        try:
            # Remove existing text actors except help_text_actor
            if self.text_actor:
                self.plotter.remove_actor(self.text_actor)
                self.text_actor = None
            
            if hasattr(self, 'performance_actor') and self.performance_actor:
                self.plotter.remove_actor(self.performance_actor)
                self.performance_actor = None
            
            # Calculate performance
            perf_data = self.calculate_performance()
            
            # Only display debug information if panels exist
            if perf_data and perf_data.get('panel_count', 0) > 0:
                # Get side counts and skipped counts with translations
                side_info = []
                total_skipped = 0
                
                for side, count in perf_data['side_counts'].items():
                    skipped = self.panels_skipped_by_side.get(side, 0)
                    total_skipped += skipped
                    
                    # Translate side name
                    if side.lower() == "front":
                        side_name = _('front_side')
                    elif side.lower() == "back":
                        side_name = _('back_side')
                    elif side.lower() == "left":
                        side_name = _('left_side')
                    elif side.lower() == "right":
                        side_name = _('right_side')
                    else:
                        side_name = side.upper()
                    
                    if skipped > 0:
                        side_info.append(f"{side_name}: {count} ({_('skipped')} {skipped})")
                    else:
                        side_info.append(f"{side_name}: {count}")
                
                debug_msg = f"{_('selected_slope')}: {', '.join(side_info)}\n"
                debug_msg += f"{_('panels')}: {perf_data['panel_count']}"
                
                if total_skipped > 0:
                    debug_msg += f" ({_('skipped')} {total_skipped} {_('due_to_obstacles')})\n"
                else:
                    debug_msg += "\n"
                    
                debug_msg += f"{_('panel_dimensions')}: {self.panel_width}mm x {self.panel_length}mm\n"
                debug_msg += f"{_('panel_gap')}: {self.panel_gap}mm\n"
                debug_msg += f"{_('slope_angle')}: {perf_data['roof_angle_degrees']:.1f}°\n\n"
                
                # Add power calculations to debug message
                debug_msg += f"{_('panel_power')}: {perf_data['panel_power_w']}W\n"
                debug_msg += f"{_('system_size')}: {perf_data['system_power_kw']:.2f}kWp ({perf_data['system_power_w']:.0f}W)\n"
                debug_msg += f"{_('est_annual_production')}: {perf_data['annual_energy_kwh']:.0f}kWh\n" 
                debug_msg += f"{_('est_daily_production')}: {perf_data['daily_energy_kwh']:.1f}kWh\n"
                debug_msg += f"{_('performance_factor')}: {perf_data['angle_factor']:.2f}\n"
                

                # Add obstacle info
                if hasattr(self.hip_roof, 'obstacles') and self.hip_roof.obstacles:
                    obstacle_count = len(self.hip_roof.obstacles)
                    debug_msg += f"\n{_('obstacles_on_roof')}: {obstacle_count}"
                    
                    
                    if total_skipped > 0:
                        debug_msg += f"\n{_('panels_skipped')}: {total_skipped}"

                # Add chimney impact if available and relevant
                if 'chimney_factor' in perf_data and perf_data['chimney_factor'] < 1.0:
                    chimney_impact = (1.0 - perf_data['chimney_factor']) * 100
                    debug_msg += f"\n{_('chimney_impact')}: {chimney_impact:.1f}%\n"
                
                # Add the debug message as text at upper left with black color
                self.performance_actor = self.plotter.add_text(
                    debug_msg,
                    position="upper_left",
                    font_size=12,
                    color="black"
                )
            
            # Force an update
            self.plotter.render()
            
        except Exception as e:
            print(f"Error updating debug display: {e}")
            import traceback
            traceback.print_exc()
            
    def check_panel_obstacle_intersection(self, center, width_dir, length_dir, normal, panel_width_m, panel_length_m, obstacle):
        """Check if a panel intersects with an obstacle with improved side detection."""
        try:
            # === STEP 1: DETERMINE SIDES (CURRENT PANEL SIDE AND OBSTACLE SIDE) ===
            panel_side = self.current_side  # This should be set when placing panels
            obstacle_side = None
            
            # Get obstacle side if directly available
            if hasattr(obstacle, 'side'):
                obstacle_side = obstacle.side
                
            # If obstacle side is unknown, determine it from position
            if obstacle_side is None and hasattr(obstacle, 'position'):
                # Get roof center coordinates
                center_x = 0
                center_y = 0
                center_count = 0
                
                # Use hip roof points if available
                if hasattr(self, 'hip_roof') and hasattr(self.hip_roof, 'roof_points'):
                    points = self.hip_roof.roof_points
                    
                    # Calculate center from all available points
                    for point_key, point_val in points.items():
                        if isinstance(point_val, (list, tuple, np.ndarray)) and len(point_val) >= 2:
                            center_x += point_val[0]
                            center_y += point_val[1]
                            center_count += 1
                    
                    if center_count > 0:
                        center_x /= center_count
                        center_y /= center_count
                
                # Determine side based on obstacle position relative to center
                pos = obstacle.position
                
                # Calculate distance from center in each direction
                dx = abs(pos[0] - center_x)  # Distance from center in X direction
                dy = abs(pos[1] - center_y)  # Distance from center in Y direction
                
                # Determine primary side based on which axis has greater distance
                if dx > dy:
                    # Primarily on east/west sides
                    if pos[0] < center_x:
                        obstacle_side = "left"  # West
                    else:
                        obstacle_side = "right"  # East
                else:
                    # Primarily on north/south sides
                    if pos[1] < center_y:
                        obstacle_side = "front"  # North/Front
                    else:
                        obstacle_side = "back"  # South/Back
                
                # Debug print (can be removed after verification)
                print(f"Obstacle at {pos} detected on {obstacle_side} side (center: {center_x}, {center_y})")
            
            # === STEP 2: SIMPLE SIDE-BASED FILTERING ===
            # Only consider obstacles on the same side as the panels
            if panel_side and obstacle_side and panel_side != obstacle_side:
                print(f"Skipping obstacle check: panel on {panel_side}, obstacle on {obstacle_side}")
                return False  # Different sides, no intersection
            
            # === STEP 3: STANDARD COLLISION DETECTION FOR OBSTACLES ON THE SAME SIDE ===
            # Get obstacle bounds if available
            if hasattr(obstacle, 'get_bounds'):
                obstacle_bounds = obstacle.get_bounds()
            elif hasattr(obstacle, 'mesh') and hasattr(obstacle.mesh, 'bounds'):
                obstacle_bounds = obstacle.mesh.bounds
            else:
                # If bounds not available, be conservative and say there's an intersection
                return True
            
            # Panel thickness - used for the bounds check
            panel_thickness = 0.04  # 4cm
            
            # Calculate half dimensions
            half_width = panel_width_m / 2
            half_length = panel_length_m / 2
            
            # Normalize direction vectors
            width_dir = width_dir / np.linalg.norm(width_dir)
            length_dir = length_dir / np.linalg.norm(length_dir)
            normal = normal / np.linalg.norm(normal)
            
            # Calculate corners of the panel
            corners = [
                # Bottom face
                center - width_dir * half_width - length_dir * half_length,
                center + width_dir * half_width - length_dir * half_length,
                center + width_dir * half_width + length_dir * half_length,
                center - width_dir * half_width + length_dir * half_length,
                # Top face (elevated by panel thickness)
                center - width_dir * half_width - length_dir * half_length + normal * panel_thickness,
                center + width_dir * half_width - length_dir * half_length + normal * panel_thickness,
                center + width_dir * half_width + length_dir * half_length + normal * panel_thickness,
                center - width_dir * half_width + length_dir * half_length + normal * panel_thickness
            ]
            
            # Calculate panel bounds
            panel_bounds = [
                min(corner[0] for corner in corners),  # min_x
                max(corner[0] for corner in corners),  # max_x
                min(corner[1] for corner in corners),  # min_y
                max(corner[1] for corner in corners),  # max_y
                min(corner[2] for corner in corners),  # min_z
                max(corner[2] for corner in corners)   # max_z
            ]
            
            # First do a quick axis-aligned bounding box (AABB) check
            if (panel_bounds[1] < obstacle_bounds[0] or  # panel max_x < obstacle min_x
                panel_bounds[0] > obstacle_bounds[1] or  # panel min_x > obstacle max_x
                panel_bounds[3] < obstacle_bounds[2] or  # panel max_y < obstacle min_y
                panel_bounds[2] > obstacle_bounds[3] or  # panel min_y > obstacle max_y
                panel_bounds[5] < obstacle_bounds[4] or  # panel max_z < obstacle min_z
                panel_bounds[4] > obstacle_bounds[5]):   # panel min_z > obstacle max_z
                # No intersection
                return False
            
            # For roof windows, add a safety margin
            if hasattr(obstacle, 'type') and obstacle.type == "Roof Window":
                safety_margin = 0.05  # 5cm safety margin
                expanded_bounds = [
                    obstacle_bounds[0] - safety_margin,
                    obstacle_bounds[1] + safety_margin,
                    obstacle_bounds[2] - safety_margin,
                    obstacle_bounds[3] + safety_margin,
                    obstacle_bounds[4] - safety_margin,
                    obstacle_bounds[5] + safety_margin
                ]
                
                # Check against expanded bounds
                if (panel_bounds[1] < expanded_bounds[0] or
                    panel_bounds[0] > expanded_bounds[1] or
                    panel_bounds[3] < expanded_bounds[2] or
                    panel_bounds[2] > expanded_bounds[3] or
                    panel_bounds[5] < expanded_bounds[4] or
                    panel_bounds[4] > expanded_bounds[5]):
                    # No intersection with expanded bounds
                    return False
                
                # If it passed the expanded bounds check, consider it an intersection
                return True
            
            # Use PyVista's collision detection if available
            if hasattr(obstacle, 'mesh'):
                try:
                    # Create a panel mesh
                    panel_mesh = pv.Cube(
                        center=(0, 0, 0), 
                        x_length=panel_width_m, 
                        y_length=panel_length_m,
                        z_length=panel_thickness
                    )
                    
                    # Create transformation matrix (4x4)
                    transform = np.eye(4)
                    transform[:3, 0] = width_dir
                    transform[:3, 1] = length_dir
                    transform[:3, 2] = normal
                    transform[:3, 3] = center
                    
                    # Apply transformation
                    panel_mesh.transform(transform)
                    
                    collision = panel_mesh.collision(obstacle.mesh)
                    return collision
                except Exception as e:
                    print(f"Error in collision detection: {e}")
                    # Fall back to bounding box intersection
                    return True
                    
            # If we can't do a proper collision check, be conservative
            return True
            
        except Exception as e:
            print(f"Error checking panel-obstacle intersection: {e}")
            import traceback
            traceback.print_exc()
            return True  # Be conservative in case of errors
        
    def _calculate_chimney_impact_factor(self):
        """Calculate the performance impact factor from chimneys."""
        # Default impact factor (1.0 = no impact)
        impact_factor = 1.0
        
        # Check if the hip roof has obstacles
        if not hasattr(self.hip_roof, 'obstacles') or not self.hip_roof.obstacles:
            return impact_factor
        
        # Count chimneys
        chimney_count = 0
        total_chimney_size = 0
        
        # Track which sides have panels
        active_sides = self.active_sides
        
        # Analyze each chimney
        for obstacle in self.hip_roof.obstacles:
            # Skip if not a chimney
            if not hasattr(obstacle, 'type') or obstacle.type != "Chimney":
                continue
                
            # Skip if not on one of the active sides
            if hasattr(obstacle, 'side') and obstacle.side not in active_sides:
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
        
        # No chimneys found on active sides
        if chimney_count == 0:
            return impact_factor
        
        # Calculate impact - each chimney reduces efficiency by its relative footprint plus a shading factor
        
        # Estimate roof area for active sides
        if hasattr(self.hip_roof, 'length') and hasattr(self.hip_roof, 'width'):
            single_side_area = self.hip_roof.length * self.hip_roof.width / 4  # Quarter of total for one side
            roof_area = single_side_area * len(active_sides)  # Area of active sides
        else:
            # Default area if dimensions not available
            roof_area = 50.0  # Default to 50 sq meters
        
        # Base impact: 1-3% per chimney for general impact
        base_impact = 0.01 * chimney_count
        
        # Size impact: reduction based on relative size to roof area with shading factor
        shading_multiplier = 2.5  # Chimney affects 2.5x its area due to shading
        size_impact = (total_chimney_size * shading_multiplier) / roof_area
        
        # Combine impacts, ensuring we don't reduce by more than 25% from chimneys
        total_impact = min(0.25, base_impact + size_impact)
        
        # Final factor (reduces performance)
        impact_factor = 1.0 - total_impact
        
        return impact_factor