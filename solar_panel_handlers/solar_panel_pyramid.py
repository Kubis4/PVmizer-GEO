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

# Common texture loading function to avoid duplication
def load_panel_texture():
    """Load solar panel texture with robust path handling."""
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
                    panel_texture = pv.read_texture(full_path)
                    print(f"Loaded solar panel texture from: {full_path}")
                    return panel_texture
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
                    panel_texture = pv.read_texture(path)
                    print(f"Loaded solar panel texture from legacy path: {path}")
                    return panel_texture
                except Exception as e:
                    print(f"Failed to load texture from legacy path {path}: {e}")
        
        # If we reach here, no texture was loaded
        print("No solar panel texture could be loaded. Using solid color instead.")
        return None
        
    except Exception as e:
        print(f"Error in texture loading process: {e}")
        import traceback
        traceback.print_exc()
        return None

class SolarPanelPlacementPyramid:
    """Handler for placing solar panels on a pyramid roof with efficient instancing."""
    
    def __init__(self, pyramid_roof):
        """Initialize a solar panel placement handler for a pyramid roof."""
        self.pyramid_roof = pyramid_roof
        self.plotter = pyramid_roof.plotter
        
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
        self.panel_offset = 300      # Default panel offset in mm
        
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
        
        # Add template mesh for instancing and batch rendering
        self.panel_template = None
        self.panel_meshes_by_side = {
            "front": [],
            "right": [],
            "back": [],
            "left": []
        }
        self.panel_batch_size = 20  # Number of panels per batch for rendering
        
        # Add help text
        self.add_help_text()
        
        # Add tracking for current side
        self.current_side = None

        # Load the solar panel texture with improved handling
        self.panel_texture = load_panel_texture()
        
        # Create panel template for instancing
        self.create_panel_template()
    
    def create_panel_template(self):
        """Create a template panel mesh for instancing."""
        # Convert panel dimensions from mm to meters
        panel_width_m = self.panel_width * self.mm_to_m
        panel_length_m = self.panel_length * self.mm_to_m
        
        # Create a rectangular panel
        self.panel_template = pv.Plane(
            center=[0, 0, 0],
            direction=[0, 0, 1],
            i_size=panel_width_m,
            j_size=panel_length_m,
            i_resolution=1,
            j_resolution=1
        )
        
        # Set texture coordinates for proper mapping
        tcoords = np.array([
            [0, 0],  # bottom-left
            [1, 0],  # bottom-right
            [1, 1],  # top-right
            [0, 1]   # top-left
        ])
        self.panel_template.texture_coordinates = tcoords
    
    def check_panel_obstacle_intersection(self, panel_center, panel_length, panel_width, h_unit, v_unit, normal, obstacle):
        """Check if a panel at the given position intersects with an obstacle."""
        try:
            # First, check if this is a roof window on a pyramid/hip roof
            is_roof_window = False
            is_special_roof = False
            
            # Check obstacle type
            if hasattr(obstacle, 'type') and obstacle.type == "Roof Window":
                is_roof_window = True
                
                # Check if we're on a pyramid or hip roof
                if hasattr(obstacle, 'roof'):
                    roof_type = type(obstacle.roof).__name__
                    is_special_roof = roof_type in ["HipRoof", "PyramidRoof"]
            
            # Special handling for roof windows on pyramid/hip roofs
            if is_roof_window and is_special_roof:
                # Get window properties
                window_pos = obstacle.position
                
                if hasattr(obstacle, 'dimensions'):
                    window_width, window_length, window_height = obstacle.dimensions
                else:
                    window_width, window_length = 1.0, 1.2  # Default size
                
                # Get window normal vector
                window_normal = obstacle.normal_vector if hasattr(obstacle, 'normal_vector') else None
                if window_normal is None and hasattr(obstacle, 'get_roof_normal_at_position'):
                    window_normal = obstacle.get_roof_normal_at_position()
                if window_normal is None or np.linalg.norm(window_normal) < 0.001:
                    window_normal = np.array([0, 0, 1])  # Default to vertical
                
                # Use absolute minimal safety margins
                side_margin = 0.10    # 10cm side margin (was 15cm)
                top_margin = 0.05     # 5cm top margin (was 10cm) 
                bottom_margin = 0.25   # 25cm bottom margin (was 50cm)
                
                # Create window coordinate system for directional checks
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
                
                # Calculate shadow based on roof slope - much shorter now
                roof_slope = np.arccos(abs(np.dot(z_axis, [0, 0, 1])))
                
                # Much smaller shadow length
                shadow_length = 0.3  # Base shadow length 30cm (was 50cm)
                
                if roof_slope > 0.001:
                    # Calculate shadow based on window height and slope (with reduced factor)
                    slope_shadow = np.tan(roof_slope) * window_height * 0.7  # Only 70% of theoretical shadow
                    shadow_length = max(shadow_length, slope_shadow)
                    
                    # Only add extra for very steep roofs
                    if roof_slope > np.radians(45):  # Only for extremely steep roofs (>45°)
                        shadow_length += 0.15  # Add 15cm (was 20cm)
                
                # Check if panel is downslope from window (negative y in local coords)
                if panel_local[1] < 0:
                    # Narrower shadow zone
                    shadow_width = window_width/2 + side_margin * 0.7  # Reduce width by 30%
                    
                    if (abs(panel_local[0]) <= shadow_width + panel_width/2 and
                        abs(panel_local[1]) <= shadow_length + panel_length/2):
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
                    # Check lower zone - with smaller margin than before
                    if (abs(panel_local[0]) <= half_width + panel_width/2 and
                        panel_local[1] >= -half_length_bottom - panel_length/2):
                        return True
                
                # If we get here, panel doesn't intersect the minimized window zone
            
            # Standard collision detection for all other obstacles or windows on standard roofs
            
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
            half_width = panel_width / 2
            half_length = panel_length / 2
            
            # Normalize direction vectors
            h_unit = h_unit / np.linalg.norm(h_unit)
            v_unit = v_unit / np.linalg.norm(v_unit)
            normal = normal / np.linalg.norm(normal)
            
            # Calculate corners of the panel
            corners = [
                # Bottom face
                panel_center - h_unit * half_width - v_unit * half_length,
                panel_center + h_unit * half_width - v_unit * half_length,
                panel_center + h_unit * half_width + v_unit * half_length,
                panel_center - h_unit * half_width + v_unit * half_length,
                # Top face (elevated by panel thickness)
                panel_center - h_unit * half_width - v_unit * half_length + normal * panel_thickness,
                panel_center + h_unit * half_width - v_unit * half_length + normal * panel_thickness,
                panel_center + h_unit * half_width + v_unit * half_length + normal * panel_thickness,
                panel_center - h_unit * half_width + v_unit * half_length + normal * panel_thickness
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
            
            # For windows, add a minimal safety margin around the bounding box
            if is_roof_window:
                safety_margin = 0.05  # 5cm safety margin (was 10cm)
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
                # This provides a small safety margin without full mesh collision
                return True
            
            # For non-window obstacles, use PyVista's collision detection if available
            if hasattr(obstacle, 'mesh'):
                try:
                    # Create a panel mesh
                    panel_mesh = pv.Cube(
                        center=(0, 0, 0), 
                        x_length=panel_width, 
                        y_length=panel_length,
                        z_length=panel_thickness
                    )
                    
                    # Create transformation matrix (4x4)
                    transform = np.eye(4)
                    
                    # Set orientation vectors
                    transform[:3, 0] = h_unit
                    transform[:3, 1] = v_unit
                    transform[:3, 2] = normal
                    
                    # Set position
                    transform[:3, 3] = panel_center
                    
                    # Apply transformation
                    panel_mesh.transform(transform)
                    
                    collision = panel_mesh.collision(obstacle.mesh)
                    return collision
                except Exception as e:
                    print(f"Error in collision detection: {e}")
                    # Fall back to bounding box intersection (already checked and passed)
                    return True
                    
            # If we can't do a proper collision check, be conservative
            return True
            
        except Exception as e:
            print(f"Error checking panel-obstacle intersection: {e}")
            # In case of error, be conservative and say there's an intersection
            return True

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
        # Update status text with all active sides
    
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
        
        # Clear pending panel meshes
        self.panel_meshes_by_side[side] = []
        
        # Remove boundary actors for this side
        for actor in self.boundaries_by_side[side]:
            if actor is not None:
                self.plotter.remove_actor(actor)
        self.boundaries_by_side[side] = []
        
        # Reset panel count and skipped count
        self.panels_count_by_side[side] = 0
        self.panels_skipped_by_side[side] = 0

        self.update_debug_display()
    
    def update_status_text(self):
        """Update status text with information about active sides."""
        if not self.active_sides:
            message = "No panels placed\nUse keys 1-4 to add panels to different sides"
        else:
            active_sides_text = ", ".join(sorted(self.active_sides))
            
            # Build info about each active side
            side_info = []
            total_panels = 0
            total_skipped = 0
            
            for side in sorted(self.active_sides):
                count = self.panels_count_by_side[side]
                skipped = self.panels_skipped_by_side[side]
                total_panels += count
                total_skipped += skipped
                
                if skipped > 0:
                    side_info.append(f"{side} ({count}, skipped {skipped})")
                else:
                    side_info.append(f"{side} ({count})")
            
            sides_text = ", ".join(side_info)
            
            message = (
                f"Panels on: {sides_text}\n"
                f"Total panels: {total_panels}"
            )
            
            if total_skipped > 0:
                message += f" (skipped {total_skipped} total)\n"
            else:
                message += "\n"
                
            message += (
                f"Panel size: {self.panel_width}mm × {self.panel_length}mm\n"
                f"Gap: {self.panel_gap}mm\n"
                f"Press 'C' to clear all panels"
            )
        
        self.update_text(message)

    def place_front_panels(self):
        """Place solar panels on the front face of the pyramid."""
        try:
            # Get points for the front face
            points = self.pyramid_roof.roof_points
            bottom_left = points['front_left']
            bottom_right = points['front_right']
            top = points['peak']
            
            # Create installation area with offsets
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=True
            )
            
            # Place panels
            panel_count = self.place_panels_on_triangle(adjusted_bottom_left, adjusted_bottom_right, adjusted_top)
            
            # Store the panel count
            self.panels_count_by_side["front"] = panel_count
            
        except Exception as e:
            print(f"Error placing front panels: {e}")
            import traceback
            traceback.print_exc()

    def place_right_panels(self):
        """Place solar panels on the right face of the pyramid."""
        try:
            # Get points for the right face
            points = self.pyramid_roof.roof_points
            bottom_left = points['front_right']
            bottom_right = points['back_right']
            top = points['peak']
            
            # Create installation area with offsets
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=False
            )
            
            # Place panels
            panel_count = self.place_panels_on_triangle(adjusted_bottom_left, adjusted_bottom_right, adjusted_top)
            
            # Store the panel count
            self.panels_count_by_side["right"] = panel_count
            
        except Exception as e:
            print(f"Error placing right panels: {e}")
            import traceback
            traceback.print_exc()

    def place_back_panels(self):
        """Place solar panels on the back face of the pyramid."""
        try:
            # Get points for the back face
            points = self.pyramid_roof.roof_points
            bottom_left = points['back_right']
            bottom_right = points['back_left']
            top = points['peak']
            
            # Create installation area with offsets
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=False
            )
            
            # Place panels
            panel_count = self.place_panels_on_triangle(adjusted_bottom_left, adjusted_bottom_right, adjusted_top)
            
            # Store the panel count
            self.panels_count_by_side["back"] = panel_count
            
        except Exception as e:
            print(f"Error placing back panels: {e}")
            import traceback
            traceback.print_exc()

    def place_left_panels(self):
        """Place solar panels on the left face of the pyramid."""
        try:
            # Get points for the left face
            points = self.pyramid_roof.roof_points
            bottom_left = points['back_left']
            bottom_right = points['front_left']
            top = points['peak']
            
            # Create installation area with offsets
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=False
            )
            
            # Place panels
            panel_count = self.place_panels_on_triangle(adjusted_bottom_left, adjusted_bottom_right, adjusted_top)
            
            # Store the panel count
            self.panels_count_by_side["left"] = panel_count
            
        except Exception as e:
            print(f"Error placing left panels: {e}")
            import traceback
            traceback.print_exc()

    def create_triangular_boundary(self, eave_left, eave_right, apex, is_front, min_offset=300):
        """Create a triangular boundary with appropriate offsets for panel placement.
        
        Note: min_offset is in millimeters (default 300mm)
        """
        # Calculate vectors
        base_vector = eave_right - eave_left
        base_length = np.linalg.norm(base_vector)  # This is in meters
        base_dir = base_vector / base_length
        
        base_mid = (eave_left + eave_right) / 2
        height_vector = apex - base_mid
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
        horizontal_offset_mm = max(min_offset, base_length_mm * 0.15)  # 15% of width or min_offset
        vertical_offset_mm = max(min_offset, height_length_mm * 0.20)  # 20% of height or min_offset
        
        # Check available space (in mm)
        available_width_mm = base_length_mm - 2 * horizontal_offset_mm
        available_height_mm = height_length_mm - vertical_offset_mm - self.edge_offset
        
        # Adjust offsets if panels won't fit (in mm)
        if available_width_mm < self.panel_width + 2 * self.panel_gap:
            horizontal_offset_mm = max(100, (base_length_mm - self.panel_width - 2 * self.panel_gap) / 2)
            print(f"Reducing horizontal offset to {horizontal_offset_mm:.0f}mm to fit panels")
        
        if available_height_mm < self.panel_length + 2 * self.panel_gap:
            vertical_offset_mm = max(100, (height_length_mm - self.panel_length - 2 * self.panel_gap))
            print(f"Reducing vertical offset to {vertical_offset_mm:.0f}mm to fit panels")
        
        # Convert offsets back to meters for positioning
        horizontal_offset = horizontal_offset_mm * self.mm_to_m
        vertical_offset = vertical_offset_mm * self.mm_to_m
        edge_offset = self.edge_offset * self.mm_to_m
        panel_height = self.panel_height * self.mm_to_m
        
        # Calculate boundary points (in meters for PyVista)
        bottom_left = eave_left + base_dir * horizontal_offset + height_dir * edge_offset
        bottom_right = eave_right - base_dir * horizontal_offset + height_dir * edge_offset
        top = apex - height_dir * vertical_offset
        
        # Calculate effective top width (in meters)
        top_width = np.linalg.norm(np.cross(height_dir, normal)) * height_length
        
        # Adjust top point if needed for narrow peaks (in meters)
        if top_width * 1000 < self.panel_width + 2 * self.panel_gap:
            panel_gap_m = self.panel_gap * self.mm_to_m
            top = top - height_dir * (panel_gap_m * 2)
        
        # Elevate above roof surface (in meters)
        bottom_left = bottom_left + normal * panel_height
        bottom_right = bottom_right + normal * panel_height
        top = top + normal * panel_height
        
        # Create boundary visualization
        self.create_enhanced_boundary([bottom_left, bottom_right, top], normal,
                                     labels={
                                         "horizontal_offset": f"{horizontal_offset_mm:.0f}mm",
                                         "vertical_offset": f"{vertical_offset_mm:.0f}mm",
                                         "available_width": f"{available_width_mm:.0f}mm",
                                         "available_height": f"{available_height_mm:.0f}mm"
                                     })
        
        return bottom_left, bottom_right, top

    def create_enhanced_boundary(self, points, normal, labels=None):
        """Create a highlighted boundary visualization with dimension labels."""
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

    def place_panels_on_triangle(self, bottom_left, bottom_right, top):
        """Place solar panels optimally on a triangular surface with batched rendering.
        
        Returns the number of panels placed.
        """
        try:
            # Calculate main directions
            bottom_edge_vector = bottom_right - bottom_left
            bottom_edge_length = np.linalg.norm(bottom_edge_vector)  # meters
            bottom_edge_dir = bottom_edge_vector / bottom_edge_length

            # Vector from bottom edge midpoint to top
            bottom_mid = (bottom_left + bottom_right) / 2
            apex_vector = top - bottom_mid
            apex_length = np.linalg.norm(apex_vector)  # meters
            apex_dir = apex_vector / apex_length

            # Calculate normal vector for panel orientation
            normal = np.cross(bottom_edge_dir, apex_dir)
            normal /= np.linalg.norm(normal)

            # Panel spacing (convert from mm to meters for placement)
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            panel_gap_m = self.panel_gap * self.mm_to_m
            
            vertical_spacing_m = panel_length_m + panel_gap_m
            horizontal_spacing_m = panel_width_m + panel_gap_m
            
            # Calculate how many rows will fit
            num_rows = max(1, int((apex_length + panel_gap_m/2) / vertical_spacing_m))
            
            # Small offset to avoid boundary overlap
            vertical_start_offset_m = panel_gap_m/2

            # Track total panels placed and skipped
            count = 0
            skipped_panels = 0
            
            # Clear pending panels for this side
            if self.current_side:
                self.panel_meshes_by_side[self.current_side] = []
            
            # Collect all valid panel positions and transformations
            valid_panels = []
            
            # Place panels row by row from bottom to top
            for row in range(num_rows):
                # Calculate position of this row from the bottom
                row_height_m = vertical_start_offset_m + row * vertical_spacing_m

                # Calculate center of this row
                row_center = bottom_mid + apex_dir * row_height_m

                # Row width shrinks as we go up the triangle
                scale_factor = 1.0 - (row_height_m / apex_length)
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
                                apex_dir * (panel_length_m / 2))

                    # Check if panel intersects with any obstacles
                    skip_panel = False
                    if hasattr(self.pyramid_roof, 'obstacles') and self.pyramid_roof.obstacles:
                        for obstacle in self.pyramid_roof.obstacles:
                            if self.check_panel_obstacle_intersection(
                                panel_center, 
                                panel_length_m, 
                                panel_width_m, 
                                bottom_edge_dir, 
                                apex_dir, 
                                normal,
                                obstacle
                            ):
                                skip_panel = True
                                skipped_panels += 1
                                break
                    
                    # Skip this panel if it intersects with an obstacle
                    if skip_panel:
                        continue

                    # Store this valid panel position and orientation
                    valid_panels.append({
                        'center': panel_center,
                        'width_dir': bottom_edge_dir,
                        'length_dir': apex_dir,
                        'normal': normal
                    })
                    count += 1

            # Create batched mesh with all valid panels
            if valid_panels:
                self._create_panel_batch(valid_panels)
            
            # Store skipped panel count for the current side
            if self.current_side:
                self.panels_skipped_by_side[self.current_side] = skipped_panels

            return count

        except Exception as e:
            print(f"Error placing panels on triangle: {e}")
            import traceback
            traceback.print_exc()
            return 0  # Return 0 panels on error

    def _create_panel_batch(self, valid_panels):
        """Create a batched mesh with all valid panels for efficient rendering."""
        try:
            # For empty list, return early
            if not valid_panels:
                return
                
            # Convert panel dimensions from mm to meters
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            
            # Create a list to hold all transformed panel meshes
            transformed_panels = []
            
            # For each valid panel, create and transform a copy of the template
            for panel_data in valid_panels:
                # Create a copy of the template
                panel = self.panel_template.copy()
                
                # Get parameters from panel data
                center = panel_data['center']
                width_dir = panel_data['width_dir']
                length_dir = panel_data['length_dir']
                normal = panel_data['normal']
                
                # Create transformation matrix (4x4)
                transform = np.eye(4)
                
                # Set orientation vectors (properly normalized)
                width_dir = width_dir / np.linalg.norm(width_dir)
                length_dir = length_dir / np.linalg.norm(length_dir)
                normal = normal / np.linalg.norm(normal)
                
                transform[:3, 0] = width_dir
                transform[:3, 1] = length_dir
                transform[:3, 2] = normal
                
                # Set position
                transform[:3, 3] = center
                
                # Apply transformation
                panel.transform(transform)
                
                # Add to the list of transformed panels
                transformed_panels.append(panel)
            
            # Now merge all panels into a single mesh for efficient rendering
            # First handle the case of a single panel
            if len(transformed_panels) == 1:
                combined_mesh = transformed_panels[0]
            else:
                # Try to efficiently combine multiple panels
                try:
                    # Use PyVista's MultiBlock to handle multiple meshes
                    multi_block = pv.MultiBlock(transformed_panels)
                    
                    # If combine method is available, use it
                    if hasattr(multi_block, 'combine'):
                        combined_mesh = multi_block.combine()
                    else:
                        # Fall back to manual combination
                        combined_mesh = transformed_panels[0].copy()
                        for i in range(1, len(transformed_panels)):
                            combined_mesh = combined_mesh.merge(transformed_panels[i])
                except Exception as e:
                    print(f"Error combining panels: {e}, falling back to individual rendering")
                    # Fall back to adding each panel individually
                    for panel in transformed_panels:
                        self._add_mesh_with_texture(panel)
                    return
            
            # Add the combined mesh to the scene
            self._add_mesh_with_texture(combined_mesh)
            
        except Exception as e:
            print(f"Error creating panel batch: {e}")
            import traceback
            traceback.print_exc()

    def _add_mesh_with_texture(self, mesh):
        """Add a mesh to the scene with proper texturing."""
        try:
            # Add to scene with texture or color
            if hasattr(self, 'panel_texture') and self.panel_texture is not None:
                try:
                    actor = self.plotter.add_mesh(
                        mesh, 
                        texture=self.panel_texture, 
                        show_edges=True,
                        ambient=0.2,
                        diffuse=0.8,
                        specular=0.1
                    )
                except Exception as e:
                    print(f"Error adding panel with texture: {e}, using solid color")
                    actor = self.plotter.add_mesh(
                        mesh, 
                        color="#1a1a2e", 
                        opacity=0.9, 
                        show_edges=True,
                        ambient=0.2,
                        diffuse=0.8,
                        specular=0.1
                    )
            else:
                actor = self.plotter.add_mesh(
                    mesh, 
                    color="#1a1a2e", 
                    opacity=0.9, 
                    show_edges=True,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.1
                )
            
            # Store the actor for this side
            if self.current_side:
                self.panels_by_side[self.current_side].append(actor)
            
        except Exception as e:
            print(f"Error adding mesh with texture: {e}")
            import traceback
            traceback.print_exc()

    def add_panel(self, center, width_dir, length_dir, normal):
        """Legacy method for adding a single panel - now uses batching."""
        try:
            # Create transformed panel mesh
            panel = self.create_transformed_panel(center, width_dir, length_dir, normal)
            
            # Add to batch for the current side
            if self.current_side:
                self.panel_meshes_by_side[self.current_side].append(panel)
                
        except Exception as e:
            print(f"Error in add_panel: {e}")
            import traceback
            traceback.print_exc()

    def create_transformed_panel(self, center, width_dir, length_dir, normal):
        """Create a panel mesh with the specified transformation."""
        # Normalize direction vectors
        width_dir = width_dir / np.linalg.norm(width_dir)
        length_dir = length_dir / np.linalg.norm(length_dir)
        normal = normal / np.linalg.norm(normal)
        
        # Create a copy of the template
        panel = self.panel_template.copy()
        
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
        
        return panel

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
                
                # Clear pending panel meshes
                self.panel_meshes_by_side[side] = []
                
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
        """Add comprehensive help text for pyramid roof visualization."""
        # First, remove any existing help text
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            self.plotter.remove_actor(self.help_text_actor)
            self.help_text_actor = None
        
        # Also remove any help text from the PyramidRoof if it exists
        if hasattr(self.pyramid_roof, 'help_text_actor') and self.pyramid_roof.help_text_actor:
            self.plotter.remove_actor(self.pyramid_roof.help_text_actor)
            self.pyramid_roof.help_text_actor = None
    
        # Create comprehensive help text for pyramid roof
        help_text = (
            f"{_('help_pyramid_roof_title')}\n"
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
        
        # Update the PyramidRoof's help visibility state to match
        self.pyramid_roof.help_visible = True

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
        """Update panel configuration parameters. All input values are in millimeters."""
        if config is None:
            return False
            
        try:
            if 'panel_width' in config:
                self.panel_width = float(config['panel_width'])
                
            if 'panel_length' in config:
                self.panel_length = float(config['panel_length'])
                
            if 'panel_gap' in config:
                self.panel_gap = float(config['panel_gap'])
                
            if 'panel_offset' in config:
                self.panel_offset = float(config['panel_offset'])
                
            if 'edge_offset' in config:
                self.edge_offset = float(config['edge_offset'])
                
            if 'panel_power' in config:
                self.panel_power = float(config['panel_power'])
                
            if 'panel_model' in config:
                self.panel_model = config['panel_model']
            
            # Recreate panel template with new dimensions
            self.create_panel_template()
            
            # Refresh all active sides
            active_sides_copy = list(self.active_sides)
            if active_sides_copy:
                # Clear all panels
                self.clear_panels()
                
                # Re-add panels to all previously active sides
                for side in active_sides_copy:
                    self.add_panels(side)
                    
            return True
                
        except Exception as e:
            # Use print instead of _log
            print(f"Error updating panel config: {e}")
            return False
            
    def calculate_performance(self):
        """Calculate performance data for currently placed panels."""
        # Get total panel count
        total_panels = sum(self.panels_count_by_side.values())
        
        if total_panels == 0:
            return None
        
        # Calculate power values
        panel_power_w = self.panel_power  # Individual panel power in watts
        system_power_w = panel_power_w * total_panels  # Total power in watts
        system_power_kw = system_power_w / 1000  # Convert to kilowatts
        
        # Get the roof angle - for pyramid roofs, try to get it from the pyramid_roof object
        try:
            # For pyramid roofs, try to get the angle from the roof object
            roof_angle_rad = 30  # Default angle in degrees
            
            # Try to get the actual angle if available
            if hasattr(self.pyramid_roof, 'slope_angle'):
                roof_angle_rad = self.pyramid_roof.slope_angle
            
            # Convert to degrees if in radians
            angle_degrees = roof_angle_rad
            if roof_angle_rad < 1.6:  # Probably in radians
                angle_degrees = np.degrees(roof_angle_rad)
        except:
            angle_degrees = 30  # Default fallback
        
        # Calculate angle factor (efficiency based on roof angle)
        angle_factor = self._calculate_angle_factor(angle_degrees)
        
        # Calculate chimney impact factor (new)
        chimney_factor = self._calculate_chimney_impact_factor()
        
        # Estimate annual energy production
        annual_yield_base = 1200  # kWh per kWp per year (moderate climate)
        performance_ratio = 0.8   # System efficiency factor
        
        # Apply both factors to energy production calculation
        annual_energy_kwh = system_power_kw * annual_yield_base * performance_ratio * angle_factor * chimney_factor
        daily_energy_kwh = annual_energy_kwh / 365
        
        # Estimate panel layout dimensions
        import math
        panel_count = total_panels
        ratio = self.panel_length / self.panel_width
        
        # Estimate a reasonable layout based on panel count and aspect ratio
        num_panels_vertical = max(1, round(math.sqrt(panel_count / ratio)))
        num_panels_horizontal = math.ceil(panel_count / num_panels_vertical)
        
        # Calculate installation area dimensions in mm
        installation_width = num_panels_horizontal * self.panel_width + (num_panels_horizontal-1) * self.panel_gap
        installation_height = num_panels_vertical * self.panel_length + (num_panels_vertical-1) * self.panel_gap
        
        return {
            'panel_count': total_panels,
            'panel_power_w': panel_power_w,
            'system_power_w': system_power_w,
            'system_power_kw': system_power_kw,
            'roof_angle_degrees': angle_degrees,
            'angle_factor': angle_factor,
            'chimney_factor': chimney_factor,  # Add chimney factor to data dict
            'annual_energy_kwh': annual_energy_kwh,
            'daily_energy_kwh': daily_energy_kwh,
            'installation_width': installation_width,
            'installation_height': installation_height,
            'side_counts': {side: count for side, count in self.panels_count_by_side.items() if count > 0}
        }


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
            perf_data = self.calculate_performance() or {}
            
            # Only display debug information if panels exist
            if perf_data and perf_data.get('panel_count', 0) > 0:
                # Get side information
                side_info = []
                total_skipped = 0
                
                # First attempt: Get from perf_data side_counts
                if 'side_counts' in perf_data and perf_data['side_counts']:
                    for side, count in perf_data['side_counts'].items():
                        skipped = getattr(self, 'panels_skipped_by_side', {}).get(side, 0)
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
                
                # Second attempt: Get from active_sides and panels_count_by_side
                elif hasattr(self, 'active_sides') and self.active_sides and hasattr(self, 'panels_count_by_side'):
                    for side in self.active_sides:
                        count = self.panels_count_by_side.get(side, 0)
                        skipped = getattr(self, 'panels_skipped_by_side', {}).get(side, 0)
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
                
                # Build debug message
                if side_info:
                    debug_msg = f"{_('selected_slope')}: {', '.join(side_info)}\n"
                else:
                    current_side = self.current_side or "UNKNOWN"
                    # Translate current side name
                    if current_side.lower() == "front":
                        side_name = _('front_side')
                    elif current_side.lower() == "back":
                        side_name = _('back_side')
                    elif current_side.lower() == "left":
                        side_name = _('left_side')
                    elif current_side.lower() == "right":
                        side_name = _('right_side')
                    else:
                        side_name = current_side.upper()
                        
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
                if hasattr(self.pyramid_roof, 'obstacles') and self.pyramid_roof.obstacles:
                    obstacle_count = len(self.pyramid_roof.obstacles)
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

    def refresh_language(self):
        """Update all displayed text with current language when the application language changes."""
        try:
            # Update help text if it's visible
            if hasattr(self, 'help_visible') and self.help_visible:
                self.add_help_text()
            
            # Update performance/debug display
            self.update_debug_display()
            
            # Update status text
            self.update_status_text()
            
            # If there are active sides, refresh them to update any side-specific text
            active_sides = list(self.active_sides)
            if active_sides:
                # Store current configuration
                current_side = self.current_side
                
                # Clear and re-add panels for all active sides
                self.clear_panels()
                for side in active_sides:
                    self.add_panels(side)
                
                print(f"Language updated, refreshed panels on {', '.join(active_sides)}")
            else:
                print("Language updated, will apply to next panel placement")
                
        except Exception as e:
            print(f"Error refreshing language: {e}")
            import traceback
            traceback.print_exc()

    def _calculate_chimney_impact_factor(self):
        """Calculate impact factor from chimneys on system performance."""
        # Default impact factor (1.0 = no impact)
        impact_factor = 1.0
        
        # Check if the pyramid roof has obstacles
        roof_obj = None
        if hasattr(self, 'obstacles'):
            roof_obj = self
        elif hasattr(self, 'pyramid_roof') and hasattr(self.pyramid_roof, 'obstacles'):
            roof_obj = self.pyramid_roof
        elif hasattr(self, 'roof') and hasattr(self.roof, 'obstacles'):
            roof_obj = self.roof
            
        if not roof_obj or not hasattr(roof_obj, 'obstacles') or not roof_obj.obstacles:
            return impact_factor
        
        # Count chimneys
        chimney_count = 0
        total_chimney_size = 0
        
        # Get active sides for pyramid roof
        active_sides = getattr(self, 'active_sides', [])
        if not active_sides:
            # If active_sides not explicitly defined, use sides with panels
            active_sides = [side for side, count in getattr(self, 'panels_count_by_side', {}).items() if count > 0]
        
        # Analyze each chimney
        for obstacle in roof_obj.obstacles:
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
        roof_area = 25.0  # Default area per side for calculation
        
        # Try to get the actual dimensions if available
        if hasattr(self, 'pyramid_roof'):
            if hasattr(self.pyramid_roof, 'length') and hasattr(self.pyramid_roof, 'width'):
                # Pyramid typically has 4 sides - each side is approximately length*width/4
                single_side_area = self.pyramid_roof.length * self.pyramid_roof.width / 4
                roof_area = single_side_area * len(active_sides)  # Area of active sides
        
        # Base impact: 2% per chimney for general impact
        base_impact = 0.02 * chimney_count
        
        # Size impact: reduction based on relative size to roof area with shading factor
        shading_multiplier = 2.0  # Chimney affects 2x its area due to shading
        size_impact = (total_chimney_size * shading_multiplier) / roof_area
        
        # Combine impacts, ensuring we don't reduce by more than 25% from chimneys
        total_impact = min(0.25, base_impact + size_impact)
        
        # Final factor (reduces performance)
        impact_factor = 1.0 - total_impact
        
        return impact_factor
