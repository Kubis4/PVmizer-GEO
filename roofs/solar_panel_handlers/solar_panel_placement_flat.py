from .base.base_panel_handler import BasePanelHandler
from .utils.solar_panel_utils import PanelGeometry
from .utils.panel_performance import PerformanceCalculator
import numpy as np
import pyvista as pv

class SolarPanelPlacementFlat(BasePanelHandler):
    """Handler for placing solar panels on flat roofs - FIXED FOR CENTERED COORDINATES"""
    
    def __init__(self, roof):
        super().__init__(roof, "flat")
        
        # Flat roof specific parameters
        self.panel_tilt = 0.0
        self.panel_orientation = 180.0
        self.row_spacing_factor = 1.0
        
        # Get base height from roof
        self.base_height = getattr(roof, 'base_height', 0.0)
        
        # Calculate initial row spacing
        self.calculate_row_spacing()
        
        print(f"✅ Flat roof solar panel handler initialized with centered coordinates")
    
    def calculate_row_spacing(self):
        """Calculate optimal row spacing based on tilt angle"""
        if self.panel_tilt <= 5:
            self.row_spacing_factor = 1.0
            return

        if self.panel_tilt <= 10:
            self.row_spacing_factor = 1.2
        elif self.panel_tilt <= 20:
            self.row_spacing_factor = 1.5
        elif self.panel_tilt <= 30:
            self.row_spacing_factor = 2.0
        else:
            self.row_spacing_factor = 2.5
    
    def add_panels(self, area="center"):
        """Place panels on flat roof area"""
        return self.place_panels(area)
    
    def place_panels(self, area="center"):
        """Main panel placement logic for flat roofs - FIXED FOR CENTERED COORDINATES"""
        # Calculate row spacing
        self.calculate_row_spacing()
        
        # Only clear if we're switching to a different area or this is the first placement
        if not hasattr(self, '_last_area') or self._last_area != area:
            # Clean boundary clearing: Only clear boundaries, not panels
            self._clear_boundaries_only()
            self._last_area = area
        
        # Set current area
        self.current_area = area
        
        # Get roof dimensions
        roof_length = self.roof.length
        roof_width = self.roof.width
        
        # Calculate usable area with edge offsets
        edge_offset_m = self.edge_offset / 1000.0
        safe_edge_offset = min(edge_offset_m, min(roof_length, roof_width) * 0.2)
        
        # Determine area boundaries based on selection
        area_bounds = self._get_area_bounds(area, roof_length, roof_width, safe_edge_offset)
        
        if not area_bounds:
            return 0
        
        # Clear only panels (not boundaries yet)
        self._clear_panels_only()
        
        # Place panels in the defined area
        panels_placed = self._place_panels_in_bounds(area_bounds)
        
        # Store count and update display
        self.panels_count_by_side[area] = panels_placed
        
        # Update roof info (not annotations)
        self._update_roof_info(area, panels_placed)
        
        return panels_placed

    def _clear_panels_only(self):
        """Clear only panel actors, leave boundaries intact"""
        try:
            # Remove only panel actors
            for actor in self.panel_actors:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                    except:
                        pass
            self.panel_actors.clear()
            print("🧹 Cleared panel actors only")
        except Exception as e:
            print(f"⚠️ Error clearing panels only: {e}")

    def _clear_boundaries_only(self):
        """Clear only boundary actors, leave panels intact"""
        try:
            # Remove only boundary actors
            for actor in self.boundary_actors:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                    except:
                        pass
            self.boundary_actors.clear()
            print("🧹 Cleared boundary actors only")
        except Exception as e:
            print(f"⚠️ Error clearing boundaries only: {e}")

    def _create_boundary_visualization(self, start_x, start_y, length, width):
        """Create boundary lines with smart updates - ULTRA SMOOTH"""
        boundary_z = self.base_height + 0.1
        
        new_corners = [
            [start_x, start_y, boundary_z],
            [start_x + length, start_y, boundary_z],
            [start_x + length, start_y + width, boundary_z],
            [start_x, start_y + width, boundary_z]
        ]
        
        # Smart update: Only update boundaries if they've actually changed
        if hasattr(self, '_last_boundary_corners'):
            # Check if corners are the same (within tolerance)
            corners_changed = False
            if len(self._last_boundary_corners) != len(new_corners):
                corners_changed = True
            else:
                for old_corner, new_corner in zip(self._last_boundary_corners, new_corners):
                    if np.linalg.norm(np.array(old_corner) - np.array(new_corner)) > 0.01:
                        corners_changed = True
                        break
            
            if not corners_changed:
                print(f"🔶 Boundary unchanged for {self.current_area}, keeping existing")
                return
        
        # Clear existing boundaries only if we need to update
        self._clear_boundaries_only()
        
        # Create new boundary lines
        boundary_actors_created = 0
        
        # Create boundary lines
        for i in range(4):
            start_point = new_corners[i]
            end_point = new_corners[(i + 1) % 4]
            
            line = pv.Line(start_point, end_point)
            actor = self.plotter.add_mesh(line, color="yellow", line_width=3)
            self.boundary_actors.append(actor)
            boundary_actors_created += 1
        
        # Add corner markers
        for corner in new_corners:
            marker = pv.Sphere(radius=0.08, center=corner)
            actor = self.plotter.add_mesh(marker, color="yellow", render_points_as_spheres=True)
            self.boundary_actors.append(actor)
            boundary_actors_created += 1
        
        # Store corners for next comparison
        self._last_boundary_corners = new_corners
        
        print(f"🔶 Updated {boundary_actors_created} boundary actors for {self.current_area}")

    def clear_panels(self):
        """Clear all panels and reset tracking - ENHANCED"""
        print("🧹 Clearing all flat roof panels...")
        
        # Clear panel actors
        self._clear_panels_only()
        
        # Clear boundary actors  
        self._clear_boundaries_only()
        
        # Clear other base class actors
        for actor_list in [self.wireframe_actors]:
            for actor in actor_list:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            actor_list.clear()
        
        # Remove text actors
        for text_actor in [self.text_actor, self.performance_actor]:
            if text_actor:
                try:
                    self.plotter.remove_actor(text_actor)
                except:
                    pass
        
        self.text_actor = None
        self.performance_actor = None
        
        # Reset tracking
        for area in self.panels_count_by_side:
            self.panels_count_by_side[area] = 0
            self.panels_skipped_by_side[area] = 0
        self.panel_positions_by_side = {}
        
        # Reset area tracking
        if hasattr(self, '_last_area'):
            del self._last_area
        
        self.current_area = None
        self.plotter.update()
        
        print("✅ All flat roof panels and boundaries cleared")
    
    def _get_area_bounds(self, area, roof_length, roof_width, safe_edge_offset):
        """Calculate area boundaries based on selection - 0-BASED COORDINATES FOR CALCULATION"""
        # These bounds are in 0-based coordinates for calculation purposes
        # They will be converted to centered coordinates in _place_panels_in_bounds
        
        if area == "center":
            return {
                'start_x': safe_edge_offset,
                'start_y': safe_edge_offset,
                'length': roof_length - 2 * safe_edge_offset,
                'width': roof_width - 2 * safe_edge_offset
            }
        elif area == "south":
            return {
                'start_x': safe_edge_offset,
                'start_y': roof_width / 2,
                'length': roof_length - 2 * safe_edge_offset,
                'width': roof_width / 2 - safe_edge_offset
            }
        elif area == "north":
            return {
                'start_x': safe_edge_offset,
                'start_y': safe_edge_offset,
                'length': roof_length - 2 * safe_edge_offset,
                'width': roof_width / 2 - safe_edge_offset
            }
        elif area == "east":
            return {
                'start_x': roof_length / 2,
                'start_y': safe_edge_offset,
                'length': roof_length / 2 - safe_edge_offset,
                'width': roof_width - 2 * safe_edge_offset
            }
        elif area == "west":
            return {
                'start_x': safe_edge_offset,
                'start_y': safe_edge_offset,
                'length': roof_length / 2 - safe_edge_offset,
                'width': roof_width - 2 * safe_edge_offset
            }
        
        return None
    
    def _place_panels_in_bounds(self, bounds):
        """Place panels within specified bounds - FIXED FOR CENTERED COORDINATES"""
        if bounds['width'] <= 0 or bounds['length'] <= 0:
            return 0
        
        # Convert panel dimensions
        panel_length_m = self.panel_length / 1000.0
        panel_width_m = self.panel_width / 1000.0
        panel_spacing_m = self.panel_gap / 1000.0
        
        # Calculate panel layout
        panels_x = max(1, int(bounds['length'] / (panel_length_m + panel_spacing_m)))
        panels_y = max(1, int(bounds['width'] / (panel_width_m + panel_spacing_m)))
        
        # Calculate actual space needed
        total_length = panels_x * panel_length_m + (panels_x - 1) * panel_spacing_m
        total_width = panels_y * panel_width_m + (panels_y - 1) * panel_spacing_m
        
        # Center panels in area (0-based coordinates)
        start_x_0based = bounds['start_x'] + (bounds['length'] - total_length) / 2
        start_y_0based = bounds['start_y'] + (bounds['width'] - total_width) / 2
        
        # 🔥 CRITICAL FIX: Convert to centered coordinates
        roof_half_length = self.roof.length / 2
        roof_half_width = self.roof.width / 2
        
        start_x_centered = start_x_0based - roof_half_length
        start_y_centered = start_y_0based - roof_half_width
        
        # Create boundary visualization (using centered coordinates)
        self._create_boundary_visualization(start_x_centered, start_y_centered, total_length, total_width)
        
        # Create panel positions (using centered coordinates)
        panel_positions = []
        panels_placed = 0
        
        for i in range(panels_x):
            for j in range(panels_y):
                # Calculate in centered coordinates
                x = start_x_centered + i * (panel_length_m + panel_spacing_m) + panel_length_m / 2
                y = start_y_centered + j * (panel_width_m + panel_spacing_m) + panel_width_m / 2
                z = self.base_height + 0.1
                
                panel_center = np.array([x, y, z])
                
                # Check obstacles
                skip_panel = False
                if hasattr(self.roof, 'obstacles') and self.roof.obstacles:
                    for obstacle in self.roof.obstacles:
                        if self.check_obstacle_intersection(
                            panel_center, panel_width_m, panel_length_m, None, obstacle
                        ):
                            skip_panel = True
                            break
                
                if not skip_panel:
                    panel_positions.append([x, y, z])
                    panels_placed += 1
        
        # Store panel center positions for shadow ray-casting
        if hasattr(self, 'current_area') and self.current_area:
            self.panel_positions_by_side[self.current_area] = [
                np.array(pos, dtype=float) for pos in panel_positions
            ]

        # Create instanced panels
        if panel_positions:
            self._create_instanced_panels(panel_positions)

        print(f"✅ Placed {panels_placed} panels in {self.current_area} area using centered coordinates")
        return panels_placed
    
    def _create_instanced_panels(self, positions):
        """Create instanced panels at all positions"""
        # Create template panel
        panel_length_m = self.panel_length / 1000.0
        panel_width_m = self.panel_width / 1000.0
        
        template_panel = pv.Plane(
            center=[0, 0, 0],
            direction=[0, 0, 1],
            i_size=panel_length_m,
            j_size=panel_width_m
        )
        
        # Apply rotations
        if self.panel_tilt > 0.1:
            template_panel.rotate_x(self.panel_tilt, inplace=True)
        
        template_panel.rotate_z(self.panel_orientation, inplace=True)
        
        # Create points for instancing
        points = pv.PolyData(np.array(positions))
        
        # Create instanced panels
        panels_glyph = points.glyph(
            geom=template_panel,
            orient=False,
            scale=False,
            factor=1.0
        )
        
        # Add to scene
        actor = self.add_mesh_with_texture(panels_glyph)
        self.panel_actors.append(actor)
        return actor
    
    def _update_roof_info(self, area, panel_count):
        """Update roof information without creating new annotations"""
        try:
            # If the roof has a specific update method, call it
            if hasattr(self.roof, 'update_panels_debug_info'):
                self.roof.update_panels_debug_info(area)
            
            print(f"✅ Updated roof info for {area} area with {panel_count} panels")
            
        except Exception as e:
            print(f"⚠️ Error updating roof info: {e}")
    
    def update_panel_config(self, config):
        """Update panel configuration with re-placement"""
        try:
            # Store current area
            current_area = getattr(self, 'current_area', 'center')
            
            # Save camera position
            camera_pos = self.plotter.camera_position
            
            # Update configuration using base class
            success = super().update_panel_config(config)
            if not success:
                return False
            
            # Re-place panels on current area
            if hasattr(self, '_last_area'):
                # Clear the last area tracking to force re-placement
                del self._last_area
                self.place_panels(current_area)
                
                # Restore camera position
                self.plotter.camera_position = camera_pos
                self.plotter.render()
            
            return True
            
        except Exception as e:
            print(f"Error updating panel config: {e}")
            return False
