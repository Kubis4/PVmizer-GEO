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

class SolarPanelPlacementFlat:
    def __init__(self, roof):
        self.roof = roof
        self.plotter = roof.plotter
        
        # Get base height from roof if available
        self.base_height = getattr(roof, 'base_height', 0.0)
        
        # Solar panel dimensions
        self.panel_length = 1700  # Length in millimeters
        self.panel_width = 1000   # Width in millimeters
        self.panel_thickness = 100  # Thickness in millimeters
        
        self.panel_power = 440  # Panel power in watts
        self.panels_count_by_area = {'center': 0, 'north': 0, 'south': 0, 'east': 0, 'west': 0}
        self.current_area = None
        self.installation_width = 0  # in meters
        self.installation_length = 0  # in meters
        self.panels_skipped = 0
        self.panels_skipped_by_area = {'center': 0, 'north': 0, 'south': 0, 'east': 0, 'west': 0}

        # Spacing between panels
        self.panel_spacing = 50  # Spacing in millimeters
        
        # Edge offset (distance from parapet)
        self.edge_offset = 300   # Offset in millimeters
        
        # Panel color (fallback if texture not available)
        self.panel_color = '#1E3F66'  # Dark blue
        
        # Panel tilt angle (default 0 degrees for tilted panels)
        self.panel_tilt = 0.0  # Degrees
        
        # Panel orientation (azimuth angle, 180 = south)
        self.panel_orientation = 180.0  # Degrees
        
        # Row spacing multiplier based on tilt
        self.row_spacing_factor = 1.0  # Will be adjusted based on tilt
        
        # Panel actors (for removal)
        self.panel_actors = []
        
        # Wireframe and grid actors
        self.wireframe_actors = []
        
        # Load the panel texture with robust path handling
        self.panel_texture = None
        self.load_panel_texture()
        
        # Calculate initial row spacing based on default tilt
        self.calculate_row_spacing()
    
    def load_panel_texture(self):
        """Load the solar panel texture using resource_path for robust loading."""
        try:
            # Define texture path using resource_path
            texture_file = resource_path(os.path.join("textures", "solarpanel.png"))
            
            # Try to load the texture
            if os.path.exists(texture_file):
                self.panel_texture = pv.read_texture(texture_file)
                print(f"Loaded panel texture from: {texture_file}")
                return
            
            # If not found, try some alternative paths for backward compatibility
            alternative_paths = [
                os.path.join("PVmizer", "textures", "solarpanel.png"),
                os.path.join("textures", "solarpanel.png")
            ]
            
            for path in alternative_paths:
                if os.path.exists(path):
                    try:
                        self.panel_texture = pv.read_texture(path)
                        print(f"Loaded panel texture from alternative path: {path}")
                        return
                    except Exception as e:
                        print(f"Error loading texture from {path}: {e}")
            
            # If we get here, we couldn't load the texture
            print("Solar panel texture not found, will use solid color instead.")
            
        except Exception as e:
            print(f"Error loading panel texture: {e}")
            import traceback
            traceback.print_exc()
    
    def set_base_height(self, base_height):
        """Set the base height for correct panel placement."""
        self.base_height = base_height
        print(f"Base height set to {self.base_height}m")
    
    def calculate_row_spacing(self):
        """Calculate optimal row spacing to avoid shadowing based on tilt angle."""
        if self.panel_tilt <= 5:  # Almost flat
            self.row_spacing_factor = 1.0
            return

        panel_height = self.panel_width * np.sin(np.radians(self.panel_tilt))
        
        # Adjust spacing factor based on tilt angle
        if self.panel_tilt <= 10:
            self.row_spacing_factor = 1.2
        elif self.panel_tilt <= 20:
            self.row_spacing_factor = 1.5
        elif self.panel_tilt <= 30:
            self.row_spacing_factor = 2.0
        else:
            self.row_spacing_factor = 2.5
    
    def calculate_panel_spacing(self, base_gap_x=0.1, base_gap_y=0.1):
        # Convert orientation to radians
        orientation_rad = np.radians(self.panel_orientation)
        
        # For non-cardinal orientations (NE, SE, SW, NW), adjust spacing
        # Maximum effect at 45°, 135°, 225°, 315°
        diagonal_effect = abs(np.sin(2 * orientation_rad))  # Peaks at 45° angles
        
        # Calculate orientation adjustment factors
        # Increase spacing by up to 40% for diagonal orientations
        orientation_factor = 1.0 + 0.4 * diagonal_effect
        
        # Additional adjustment for tilt
        tilt_factor = 1.0
        if self.panel_tilt > 0.1:
            tilt_rad = np.radians(self.panel_tilt)
            # More tilt requires more spacing to prevent shading
            tilt_factor = 1.0 + 0.5 * np.sin(tilt_rad)  # Up to 50% more at max tilt
        
        # Apply adjustments
        adjusted_gap_x = base_gap_x * orientation_factor * tilt_factor
        adjusted_gap_y = base_gap_y * orientation_factor * tilt_factor
        
        return adjusted_gap_x, adjusted_gap_y

    def place_panels(self, area="center"):
        """Place solar panels on the specified area of the flat roof using efficient instancing."""
        # Calculate appropriate row spacing based on tilt
        self.calculate_row_spacing()
        
        # Clear any existing panels
        self.clear_panels()
        
        # Set current area for performance data
        self.current_area = area
        
        # Get roof dimensions (in meters)
        roof_length = self.roof.length  # X direction (horizontal)
        roof_width = self.roof.width    # Y direction (vertical)
        
        # Convert edge offset from mm to m for calculation
        edge_offset_m = self.edge_offset / 1000.0
        
        # Make sure the edge offset isn't too large for the roof
        max_edge_offset = min(roof_length, roof_width) * 0.2  # Max 20% of smallest dimension
        safe_edge_offset = min(edge_offset_m, max_edge_offset)
        
        # Calculate the usable area with valid edge offsets (in meters)
        usable_length = max(0, roof_length - 2 * safe_edge_offset)
        usable_width = max(0, roof_width - 2 * safe_edge_offset)
        
        # Determine the starting position and dimensions based on the selected area
        if area == "center":
            # Use the full usable area for center placement
            area_start_x = safe_edge_offset
            area_start_y = safe_edge_offset
            area_length = usable_length
            area_width = usable_width
        
        elif area == "south":
            # North area (upper half of the roof)
            area_start_x = safe_edge_offset
            area_start_y = roof_width / 2  # Start halfway up the roof
            area_length = usable_length
            area_width = max(0, roof_width - area_start_y - safe_edge_offset)
        
        elif area == "north":
            # South area (lower half of the roof)
            area_start_x = safe_edge_offset
            area_start_y = safe_edge_offset
            area_length = usable_length
            area_width = max(0, roof_width / 2 - safe_edge_offset)
        
        elif area == "east":
            # East area (right half of the roof)
            area_start_x = roof_length / 2  # Start halfway across the roof
            area_start_y = safe_edge_offset
            area_length = max(0, roof_length - area_start_x - safe_edge_offset)
            area_width = usable_width
        
        elif area == "west":
            # West area (left half of the roof)
            area_start_x = safe_edge_offset
            area_start_y = safe_edge_offset
            area_length = max(0, roof_length / 2 - safe_edge_offset)
            area_width = usable_width
        
        # Validate dimensions - make sure we have enough space
        if area_width <= 0 or area_length <= 0:
            # Reset panels count for this area
            self.panels_count_by_area[area] = 0
            return 0
        
        # Store original panel dimensions (in meters)
        orig_panel_length_m = self.panel_length / 1000.0
        orig_panel_width_m = self.panel_width / 1000.0
        panel_spacing_m = self.panel_spacing / 1000.0
        
        # Detect orientation
        orientation_mod = self.panel_orientation % 360
        is_east_west = (45 <= orientation_mod <= 135) or (225 <= orientation_mod <= 315)
        
        # For East/West orientations, swap dimensions for layout calculation
        if is_east_west:
            # Use swapped dimensions for layout calculation
            panel_length_m = orig_panel_width_m
            panel_width_m = orig_panel_length_m
        else:
            # Use original dimensions for layout calculation
            panel_length_m = orig_panel_length_m
            panel_width_m = orig_panel_width_m
        
        # Initialize base spacing
        spacing_x = panel_spacing_m
        spacing_y = panel_spacing_m
        
        # Improved spacing calculation for tilted panels
        if self.panel_tilt > 5:
            tilt_rad = np.radians(self.panel_tilt)
            protrusion_height = panel_width_m * np.sin(tilt_rad)
            
            # Calculate optimized spacing factor (decreases for higher angles)
            if self.panel_tilt <= 30:
                # For common angles (5-30°): use moderate spacing
                spacing_factor = 1.2
            else:
                # For higher angles: reduce factor to prevent excessive gaps
                # Gradually reduce from 1.2 at 30° to 0.8 at 90°
                spacing_factor = 1.2 - 0.4 * min(1.0, (self.panel_tilt - 30) / 60)
            
            # Apply spacing based on orientation
            if is_east_west:
                # For East/West: increase spacing along X axis (between columns)
                spacing_x = max(spacing_x, protrusion_height * spacing_factor)
            else:
                # For North/South: increase spacing along Y axis (between rows)
                spacing_y = max(spacing_y, protrusion_height * spacing_factor)
        
        # Calculate how many panels can fit in the area
        panels_x = max(1, int(area_length / (panel_length_m + spacing_x)))
        panels_y = max(1, int(area_width / (panel_width_m + spacing_y)))
        
        # Calculate actual space needed by the panels (in meters)
        total_panels_length = panels_x * panel_length_m + (panels_x - 1) * spacing_x
        total_panels_width = panels_y * panel_width_m + (panels_y - 1) * spacing_y
        
        # Ensure we don't exceed the area - verify against roof boundaries
        if total_panels_length > area_length:
            panels_x = max(1, panels_x - 1)
            total_panels_length = panels_x * panel_length_m + (panels_x - 1) * spacing_x
        
        if total_panels_width > area_width:
            panels_y = max(1, panels_y - 1)
            total_panels_width = panels_y * panel_width_m + (panels_y - 1) * spacing_y
        
        # Calculate centering offsets within the area (in meters)
        length_offset = (area_length - total_panels_length) / 2
        width_offset = (area_width - total_panels_width) / 2
        
        # Calculate the final starting position (centered within the area)
        start_x = area_start_x + length_offset
        start_y = area_start_y + width_offset
        
        # Double-check that the boundaries will be within the roof
        # Adjust if necessary to ensure we stay within roof boundaries
        if start_x < safe_edge_offset:
            start_x = safe_edge_offset
        if start_y < safe_edge_offset:
            start_y = safe_edge_offset
        
        end_x = start_x + total_panels_length
        end_y = start_y + total_panels_width
        
        if end_x > roof_length - safe_edge_offset:
            # Shift the starting position to ensure we stay within boundaries
            start_x = roof_length - safe_edge_offset - total_panels_length
        
        if end_y > roof_width - safe_edge_offset:
            # Shift the starting position to ensure we stay within boundaries
            start_y = roof_width - safe_edge_offset - total_panels_width
        
        # Define the installation area boundary points (slightly above the roof surface)
        boundary_z = self.base_height + 0.1  # Base height plus height above roof surface in meters
        
        # Define the four corners of the installation area (in meters)
        bottom_left = [start_x, start_y, boundary_z]
        bottom_right = [start_x + total_panels_length, start_y, boundary_z]
        top_right = [start_x + total_panels_length, start_y + total_panels_width, boundary_z]
        top_left = [start_x, start_y + total_panels_width, boundary_z]
        
        # Create boundary lines
        left_boundary = pv.Line(bottom_left, top_left)
        right_boundary = pv.Line(bottom_right, top_right)
        bottom_boundary = pv.Line(bottom_left, bottom_right)
        top_boundary = pv.Line(top_left, top_right)
        
        # Add boundary lines to the visualization
        wireframe_actors = []
        wireframe_actors.append(self.plotter.add_mesh(left_boundary, color="yellow", line_width=3))
        wireframe_actors.append(self.plotter.add_mesh(right_boundary, color="yellow", line_width=3))
        wireframe_actors.append(self.plotter.add_mesh(bottom_boundary, color="yellow", line_width=3))
        wireframe_actors.append(self.plotter.add_mesh(top_boundary, color="yellow", line_width=3))
        
        # Add markers at corners
        for corner in [bottom_left, bottom_right, top_right, top_left]:
            wireframe_actors.append(
                self.plotter.add_mesh(
                    pv.Sphere(radius=0.08, center=corner),
                    color="yellow", 
                    render_points_as_spheres=True
                )
            )
        
        # Store wireframe actors for later removal
        self.wireframe_actors.extend(wireframe_actors)
        
        # Add grid lines
        grid_z = boundary_z  # Same height as boundary lines

        # Vertical grid lines (along y-axis)
        for j in range(panels_y + 1):
            y = start_y + j * (panel_width_m + spacing_y)
            start_point = [start_x, y, grid_z]
            end_point = [start_x + total_panels_length, y, grid_z]
            
            grid_line = pv.Line(start_point, end_point)
            grid_actor = self.plotter.add_mesh(grid_line, color="orange", line_width=1, opacity=0.7)
            self.wireframe_actors.append(grid_actor)
        
        # Horizontal grid lines (along x-axis)
        for i in range(panels_x + 1):
            x = start_x + i * (panel_length_m + spacing_x)
            start_point = [x, start_y, grid_z]
            end_point = [x, start_y + total_panels_width, grid_z]
            
            grid_line = pv.Line(start_point, end_point)
            grid_actor = self.plotter.add_mesh(grid_line, color="orange", line_width=1, opacity=0.7)
            self.wireframe_actors.append(grid_actor)

        
        # Create a template panel mesh with ORIGINAL dimensions
        template_panel = pv.Plane(
            center=[0, 0, 0],
            direction=[0, 0, 1],
            i_size=orig_panel_length_m, 
            j_size=orig_panel_width_m
        )
        
        # Apply rotations to the template panel
        if self.panel_tilt > 0.1:
            template_panel.rotate_x(self.panel_tilt, inplace=True)
            vertical_adjustment = orig_panel_width_m * np.sin(np.radians(self.panel_tilt)) / 2
        else:
            vertical_adjustment = 0
        
        template_panel.rotate_z(self.panel_orientation, inplace=True)
        
        # Create array of panel center positions
        panel_positions = []
        for i in range(panels_x):
            for j in range(panels_y):
                # Calculate center positions - not corner positions
                x = start_x + i * (panel_length_m + spacing_x) + (panel_length_m / 2)
                y = start_y + j * (panel_width_m + spacing_y) + (panel_width_m / 2)
                z = boundary_z + vertical_adjustment
                panel_positions.append([x, y, z])
        
        # If no panels to place, skip instancing
        panels_count = len(panel_positions)
        if panels_count == 0:
            self.panels_count_by_area[area] = 0
            return 0
        
        # Convert to numpy array and create PolyData points
        points = pv.PolyData(np.array(panel_positions))
        
        # Use glyph filter to create instances of the panel at each point
        panels_glyph = points.glyph(
            geom=template_panel,
            orient=False,  # We already oriented the template
            scale=False,   # No scaling needed
            factor=1.0
        )
        
        # Add the instanced panels to the plotter with a single actor
        if self.panel_texture is not None:
            actor = self.plotter.add_mesh(
                panels_glyph,
                texture=self.panel_texture,
                ambient=0.2,
                diffuse=0.8,
                specular=0.2
            )
        else:
            actor = self.plotter.add_mesh(
                panels_glyph,
                color=self.panel_color,
                ambient=0.2,
                diffuse=0.8,
                specular=0.2
            )
        
        # Store the actor for later removal
        self.panel_actors.append(actor)
        
        
        # Store installation dimensions for performance data
        self.installation_width = total_panels_width
        self.installation_length = total_panels_length
        
        # Store panel count in the current area
        self.panels_count_by_area[area] = panels_count

        if hasattr(self.roof, 'update_panels_debug_info'):
            self.roof.update_panels_debug_info(area)
        
        return panels_count
    
    def add_panel_array(self, base_x, base_y, rows=3, columns=3, base_gap_x=0.1, base_gap_y=0.1):
        """Add an array of panels with realistic spacing based on orientation using instancing."""
        try:
            # Convert panel dimensions from mm to m
            panel_length_m = self.panel_length / 1000.0
            panel_width_m = self.panel_width / 1000.0
            
            # Calculate orientation-appropriate spacing
            adjusted_gap_x, adjusted_gap_y = self.calculate_panel_spacing(base_gap_x, base_gap_y)
            
            # Create template panel
            template_panel = pv.Plane(
                center=[0, 0, 0],
                direction=[0, 0, 1],
                i_size=panel_length_m, 
                j_size=panel_width_m
            )
            
            # Apply rotations to the template panel
            if self.panel_tilt > 0.1:
                template_panel.rotate_x(self.panel_tilt, inplace=True)
                vertical_adjustment = panel_width_m * np.sin(np.radians(self.panel_tilt)) / 2
            else:
                vertical_adjustment = 0
            
            template_panel.rotate_z(self.panel_orientation, inplace=True)
            
            # Create array of panel positions
            panel_positions = []
            for row in range(rows):
                for col in range(columns):
                    # Position with adjusted gaps
                    x = base_x + col * (panel_length_m + adjusted_gap_x)
                    y = base_y + row * (panel_width_m + adjusted_gap_y)
                    z = self.base_height + 0.1 + vertical_adjustment
                    panel_positions.append([x, y, z])
            
            # Convert to numpy array and create PolyData points
            points = pv.PolyData(np.array(panel_positions))
            
            # Use glyph filter to create instances of the panel at each point
            panels_glyph = points.glyph(
                geom=template_panel,
                orient=False,
                scale=False,
                factor=1.0
            )
            
            # Add the instanced panels to the plotter with a single actor
            if self.panel_texture is not None:
                actor = self.plotter.add_mesh(
                    panels_glyph,
                    texture=self.panel_texture,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.2
                )
            else:
                actor = self.plotter.add_mesh(
                    panels_glyph,
                    color=self.panel_color,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.2
                )
            
            # Store the actor for later removal
            self.panel_actors.append(actor)
            
            return True
            
        except Exception as e:
            print(f"Error adding panel array: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def add_panels(self, side=None):
        """Standardized interface for placing panels on the flat roof."""
        # Simply call the place_panels method with the center area
        return self.place_panels(area="center")
    
    def add_panel(self, x, y, z=0.1):
        try:
            # Convert panel dimensions from mm to m for PyVista
            panel_length_m = self.panel_length / 1000.0
            panel_width_m = self.panel_width / 1000.0
            
            # STEP 1: Create a panel at origin, facing upward
            panel = pv.Plane(
                center=[0, 0, 0],
                direction=[0, 0, 1],
                i_size=panel_length_m, 
                j_size=panel_width_m
            )
            
            # STEP 2: First tilt the panel around X-axis
            if self.panel_tilt > 0.1:
                panel.rotate_x(self.panel_tilt, inplace=True)
                
                # Calculate vertical adjustment to prevent clipping
                vertical_adjustment = panel_width_m * np.sin(np.radians(self.panel_tilt)) / 2
            else:
                vertical_adjustment = 0
            
            # STEP 3: Now rotate around Z-axis to face the correct direction
            # FIXED: Changed direction calculation to correct NE/NW swap
            panel.rotate_z(self.panel_orientation, inplace=True)
            
            # STEP 4: Translate to final position with height adjustment
            panel.translate([x, y, z + vertical_adjustment], inplace=True)
            
            # Add panel to plotter with texture or color
            if self.panel_texture is not None:
                actor = self.plotter.add_mesh(
                    panel,
                    texture=self.panel_texture,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.2
                )
            else:
                actor = self.plotter.add_mesh(
                    panel,
                    color=self.panel_color,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.2
                )
            
            # Store actor for later removal
            self.panel_actors.append(actor)
            
        except Exception as e:
            print(f"Error adding panel: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_panels(self):
        """Clear all panels and wireframes from the roof and reset panel counts."""
        # Remove all panel actors
        for actor in self.panel_actors:
            try:
                self.plotter.remove_actor(actor)
            except:
                pass
        self.panel_actors = []
        
        # Remove all wireframe actors
        for actor in self.wireframe_actors:
            try:
                self.plotter.remove_actor(actor)
            except:
                pass
        self.wireframe_actors = []
        
        # Reset panel counts for all areas
        self.reset_performance_data()
        
        # Update the display
        self.plotter.update()
        
        # Update debug info if available
        if hasattr(self.roof, 'update_panels_debug_info') and self.current_area:
            self.roof.update_panels_debug_info(self.current_area)
    
    def reset_performance_data(self, area=None):
        """Reset performance data for a specific area or all areas if area is None."""
        if area is None:
            # Reset data for all areas
            for key in self.panels_count_by_area:
                self.panels_count_by_area[key] = 0
        else:
            # Reset data only for the specified area
            if area in self.panels_count_by_area:
                self.panels_count_by_area[area] = 0
        
        # Clear any panels_skipped data if it exists
        if hasattr(self, 'panels_skipped_by_area'):
            if area is None:
                # Reset all areas
                for key in self.panels_skipped_by_area:
                    self.panels_skipped_by_area[key] = 0
            elif area in self.panels_skipped_by_area:
                # Reset only specified area
                self.panels_skipped_by_area[area] = 0
    
    def remove_panels_from_area(self, area):
        """Remove panels from a specific area."""
        # Store the area before clearing
        self.current_area = area
        
        # Clear visual elements
        self.clear_panels()
        
        # Reset data for this specific area
        self.reset_performance_data(area)
        
        # Update debug info if available
        if hasattr(self.roof, 'update_panels_debug_info'):
            self.roof.update_panels_debug_info(area)
    
    def update_panel_config(self, config):
        """Update the panel configuration with new values from the dialog."""
        if not config:
            print("No configuration provided, skipping update")
            return
            
        # Store original values for comparison
        original_values = {
            'panel_width': self.panel_width,
            'panel_length': self.panel_length,
            'panel_spacing': self.panel_spacing,
            'panel_power': self.panel_power
        }
        
        # Basic panel dimensions
        if 'panel_width' in config:
            self.panel_width = config['panel_width']
        if 'panel_length' in config:
            self.panel_length = config['panel_length']
        if 'panel_gap' in config:
            self.panel_spacing = config['panel_gap']
        if 'panel_power' in config:
            self.panel_power = config['panel_power']
        
        # Edge offset (may be called panel_offset or edge_offset)
        if 'panel_offset' in config:
            self.edge_offset = config['panel_offset']
        elif 'edge_offset' in config:
            self.edge_offset = config['edge_offset']
        
        # Specific offsets for different directions
        if 'horizontal_edge_offset' in config:
            # Handle horizontal edge offset
            pass
        if 'vertical_edge_offset' in config:
            # Handle vertical edge offset
            pass
        
        # Flat roof specific parameters
        if 'panel_tilt' in config:
            self.panel_tilt = config['panel_tilt']
        if 'panel_orientation' in config:
            self.panel_orientation = config['panel_orientation']
        
        # Store model information if provided
        if 'panel_model' in config:
            self.panel_model = config['panel_model']
        
        # After updating config, recalculate row spacing if tilt was changed
        if 'panel_tilt' in config:
            self.calculate_row_spacing()
        
        # Print what was updated (for debugging)
        changes = []
        for key, old_value in original_values.items():
            new_value = getattr(self, key)
            if new_value != old_value:
                changes.append(f"{key}: {old_value} → {new_value}")
        
        if changes:
            print(f"Updated panel configuration: {', '.join(changes)}")
        else:
            print("Panel configuration unchanged")
        
        # Return True to indicate successful update
        return True
    
    def get_performance_data(self):
        """Calculate solar performance data with seasonal variations."""
        try:
            # Get the current area if available
            current_area = getattr(self, 'current_area', None)
            
            # Get panel counts from all areas
            panel_counts = getattr(self, 'panels_count_by_area', {})
            total_panels = sum(panel_counts.values()) if panel_counts else 0
            
            # If no panels placed, return minimal data
            if total_panels == 0:
                return {
                    'panel_count': 0,
                    'current_area': current_area
                }
                
            # Calculate system power based on total panels
            panel_power_w = self.panel_power
            system_power_w = panel_power_w * total_panels
            system_power_kw = system_power_w / 1000
            
            # Get tilt and orientation
            angle_degrees = self.panel_tilt
            orientation_degrees = self.panel_orientation
            
            # Calculate tilt efficiency factor
            angle_factor = self._calculate_angle_factor(angle_degrees)
            
            # Calculate orientation efficiency factor
            orientation_factor = self._calculate_orientation_factor(orientation_degrees)
            
            # Combined efficiency factor
            combined_factor = angle_factor * orientation_factor
            
            # IMPROVED: Monthly solar insolation model (kWh/kWp values by month)
            # These values represent typical monthly production in moderate climate
            monthly_insolation = {
                1: 40,    # January
                2: 60,    # February
                3: 100,   # March
                4: 130,   # April
                5: 160,   # May
                6: 170,   # June
                7: 180,   # July
                8: 160,   # August
                9: 120,   # September
                10: 80,   # October
                11: 50,   # November
                12: 30    # December
            }
            
            # Performance ratio - system efficiency factor
            performance_ratio = 0.8
            
            # Calculate monthly energy production
            monthly_energy = {}
            for month, insolation in monthly_insolation.items():
                # Apply system size, performance ratio, and other factors
                monthly_energy[month] = system_power_kw * insolation * performance_ratio * combined_factor
            
            # Calculate annual and daily averages
            annual_energy_kwh = sum(monthly_energy.values())
            daily_energy_kwh = annual_energy_kwh / 365
            
            # Calculate seasonal production
            seasonal_energy = {
                'winter': monthly_energy[12] + monthly_energy[1] + monthly_energy[2],
                'spring': monthly_energy[3] + monthly_energy[4] + monthly_energy[5],
                'summer': monthly_energy[6] + monthly_energy[7] + monthly_energy[8],
                'fall': monthly_energy[9] + monthly_energy[10] + monthly_energy[11]
            }
            
            # Get installation dimensions and skipped panels data
            installation_width = getattr(self, 'installation_width', 0)
            installation_length = getattr(self, 'installation_length', 0)
            skipped_panels = getattr(self, 'panels_skipped_by_area', {})
            total_skipped = sum(skipped_panels.values()) if skipped_panels else 0
            
            # Create performance data dictionary with all factors
            perf_data = {
                'panel_count': total_panels,
                'panel_power_w': panel_power_w,
                'system_power_w': system_power_w,
                'system_power_kw': system_power_kw,
                'roof_angle_degrees': angle_degrees,
                'panel_orientation': orientation_degrees,
                'angle_factor': angle_factor,
                'orientation_factor': orientation_factor,
                'combined_factor': combined_factor,
                'annual_energy_kwh': annual_energy_kwh,
                'daily_energy_kwh': daily_energy_kwh,
                'monthly_energy': monthly_energy,
                'seasonal_energy': seasonal_energy,
                'current_area': current_area,
                'panels_skipped': total_skipped,
                'area_counts': {area: count for area, count in panel_counts.items() if count > 0},
                'installation_width': installation_width,
                'installation_length': installation_length
            }
            
            # Add obstacle count if available
            if hasattr(self.roof, 'obstacles') and self.roof.obstacles:
                perf_data['obstacle_count'] = len(self.roof.obstacles)
            
            return perf_data
            
        except Exception as e:
            print(f"Error calculating performance data: {e}")
            import traceback
            traceback.print_exc()
            # Return minimal data
            return {'panel_count': 0, 'current_area': current_area}

    def _calculate_angle_factor(self, angle_degrees):
        """Calculate efficiency factor based on panel tilt angle."""
        # For flat roofs (0-5 degrees), efficiency is reduced
        if angle_degrees < 5:
            return 0.85  # 15% reduction compared to optimal tilt
        elif angle_degrees < 10:
            return 0.88
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
        
    def _calculate_orientation_factor(self, orientation_degrees):
        """Calculate efficiency factor based on panel orientation (azimuth)."""
        # Normalize orientation to 0-360°
        orientation_normalized = orientation_degrees % 360
        
        # Northern hemisphere calculations (south is optimal)
        if 157.5 <= orientation_normalized <= 202.5:  # South ±22.5°
            return 1.0  # Optimal - south facing (100%)
        elif 135 <= orientation_normalized < 157.5:  # Southeast quadrant 1
            return 0.94  # Very good - close to south (94%)
        elif 202.5 < orientation_normalized <= 225:  # Southwest quadrant 1
            return 0.94  # Very good - close to south (94%)
        elif 112.5 <= orientation_normalized < 135:  # Southeast quadrant 2
            return 0.88  # Good - further from south (88%)
        elif 225 < orientation_normalized <= 247.5:  # Southwest quadrant 2
            return 0.88  # Good - further from south (88%)
        elif 90 <= orientation_normalized < 112.5:  # East
            return 0.82  # Moderate - east facing (82%)
        elif 247.5 < orientation_normalized <= 270:  # West
            return 0.82  # Moderate - west facing (82%)
        elif 67.5 <= orientation_normalized < 90:  # East-northeast
            return 0.76  # Below average (76%)
        elif 270 < orientation_normalized <= 292.5:  # West-northwest
            return 0.76  # Below average (76%)
        elif 45 <= orientation_normalized < 67.5:  # Northeast
            return 0.70  # Poor (70%)
        elif 292.5 < orientation_normalized <= 315:  # Northwest
            return 0.70  # Poor (70%)
        elif 22.5 <= orientation_normalized < 45:  # North-northeast
            return 0.63  # Very poor (63%)
        elif 315 < orientation_normalized <= 337.5:  # North-northwest
            return 0.63  # Very poor (63%)
        else:  # North ±22.5°
            return 0.55  # Worst - north facing (55%)
    
    def format_performance_text(self, perf_data):
        """Format performance data with seasonal breakdown for display."""
        try:
            from translations import _  # Import translation function
        except ImportError:
            # If translations module not available, create a pass-through function
            _ = lambda x: x
            
        if not perf_data or 'panel_count' not in perf_data or perf_data['panel_count'] == 0:
            return _("no_panels_placed")
        
        # Build performance text
        output = []
        
        # Basic system info
        output.append(f"{_('panels')}: {perf_data['panel_count']}")
        output.append(f"{_('system_size')}: {perf_data['system_power_kw']:.2f} kWp")
        
        # Production estimates
        output.append(f"{_('est_annual_production')}: {perf_data['annual_energy_kwh']:.0f} kWh")
        output.append(f"{_('est_daily_production')}: {perf_data['daily_energy_kwh']:.1f} kWh")
        
        # Add seasonal breakdown
        if 'seasonal_energy' in perf_data:
            output.append(f"\n{_('seasonal_production')}:")
            output.append(f"  {_('winter')}: {perf_data['seasonal_energy']['winter']:.0f} kWh")
            output.append(f"  {_('spring')}: {perf_data['seasonal_energy']['spring']:.0f} kWh")
            output.append(f"  {_('summer')}: {perf_data['seasonal_energy']['summer']:.0f} kWh")
            output.append(f"  {_('fall')}: {perf_data['seasonal_energy']['fall']:.0f} kWh")
        
        # Efficiency factors
        output.append(f"\n{_('tilt_factor')}: {perf_data['angle_factor']:.2f}")
        output.append(f"{_('orientation_factor')}: {perf_data['orientation_factor']:.2f}")
        
        # Return formatted text
        return "\n".join(output)