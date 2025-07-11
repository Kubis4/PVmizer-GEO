from .base.base_panel_handler import BasePanelHandler
from .utils.solar_panel_utils import PanelGeometry
from .utils.panel_performance import PerformanceCalculator
import numpy as np
import pyvista as pv

class SolarPanelPlacementGable(BasePanelHandler):
    """Handler for placing solar panels on gable roofs"""
    
    def __init__(self, gable_roof):
        super().__init__(gable_roof, "gable")
        
        # Gable-specific tracking
        self.panels_by_side = {'left': [], 'right': []}
        self.boundaries_by_side = {'left': [], 'right': []}
    
    def add_panels(self, side):
        """Add panels to gable roof side with clean placement (no flickering)"""
        print(f"\n🔧 === GABLE ADD_PANELS CALLED ===")
        print(f"🔧 Requested side: {side}")
        print(f"🔧 Current active_sides: {list(self.active_sides)}")
        
        # Validate side
        if side not in ["left", "right"]:
            print(f"❌ Invalid side for gable roof: {side}")
            return
        
        # Check if this side is already active (TOGGLE functionality)
        is_currently_active = side in self.active_sides
        print(f"🔧 Is {side} currently active? {is_currently_active}")
        
        if is_currently_active:
            print(f"🔧 TOGGLE OFF: Removing panels from {side} side")
            self.remove_panels_from_side(side)
            print(f"🔧 After toggle off, active_sides: {list(self.active_sides)}")
            return
        
        # ✅ GABLE SPECIFIC: Only allow one side at a time (or modify as needed)
        if len(self.active_sides) >= 1:  # Adjust this number based on your requirements
            oldest_side = next(iter(self.active_sides))
            print(f"🔧 Max sides reached. Removing oldest: {oldest_side}")
            self.remove_panels_from_side(oldest_side)
            print(f"🔧 After removing oldest, active_sides: {list(self.active_sides)}")
        
        # Place panels on the requested side ONLY
        print(f"🔧 Placing panels on {side} side...")
        self.current_side = side
        
        # ✅ CLEAN PLACEMENT: Don't clear existing panels, just place new ones
        try:
            panel_count = self.place_solar_panels(side)
            print(f"🔧 Placement completed. Panels placed: {panel_count}")
            
            if panel_count > 0:
                # Add to active sides
                self.active_sides.add(side)
                print(f"✅ Added {side} to active_sides")
                print(f"✅ Final active_sides: {list(self.active_sides)}")
            else:
                print(f"⚠️ No panels placed on {side} - not adding to active_sides")
            
        except Exception as e:
            print(f"❌ Error in placement method: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Update display
        self.plotter.render()
        print(f"🔧 === GABLE ADD_PANELS COMPLETED ===\n")
    
    def place_solar_panels(self, side):
        """Place solar panels on the selected roof slope - CLEAN VERSION"""
        try:
            print(f"🏠 === PLACE_SOLAR_PANELS ON {side.upper()} ===")
            
            # ✅ NO CLEARING: Don't call self.clear_panels() here
            # The clearing is handled in add_panels() method for toggle functionality
            
            # Convert mm to meters
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
                    self.roof.roof_points['eave_left_front'],
                    self.roof.roof_points['eave_left_back'],
                    self.roof.roof_points['ridge_back'],
                    self.roof.roof_points['ridge_front']
                ]
            else:  # right side
                corners = [
                    self.roof.roof_points['eave_right_front'],
                    self.roof.roof_points['eave_right_back'],
                    self.roof.roof_points['ridge_back'],
                    self.roof.roof_points['ridge_front']
                ]
            
            # Create vectors for the installation area
            horizontal_vector = corners[1] - corners[0]
            vertical_vector = corners[3] - corners[0]
            
            h_length = np.linalg.norm(horizontal_vector)
            v_length = np.linalg.norm(vertical_vector)
            
            h_unit = horizontal_vector / h_length
            v_unit = vertical_vector / v_length
            
            # Calculate normal vector
            normal = np.cross(h_unit, v_unit)
            normal = normal / np.linalg.norm(normal)
            
            if normal[2] < 0:
                normal = -normal
            
            # ✅ CLEAN BOUNDARY CREATION: Clear only this side's boundaries
            self._clear_boundaries_for_side(side)
            
            # Show installation boundaries
            boundary_corners = self.show_installation_area(
                corners[0], h_unit, v_unit, h_length, v_length, normal,
                h_edge_offset_m, v_edge_offset_m, panel_offset_m
            )
            
            # Calculate available area
            available_width = h_length - 2 * h_edge_offset_m
            available_height = v_length - 2 * v_edge_offset_m
            
            # Calculate panel layout
            panels_horizontal = int((available_width + panel_gap_m) / (panel_width_m + panel_gap_m))
            panels_vertical = int((available_height + panel_gap_m) / (panel_length_m + panel_gap_m))
            
            # Center alignment
            total_h_space_needed = panels_horizontal * panel_width_m + (panels_horizontal - 1) * panel_gap_m
            total_v_space_needed = panels_vertical * panel_length_m + (panels_vertical - 1) * panel_gap_m
            
            h_offset = (available_width - total_h_space_needed) / 2
            v_offset = (available_height - total_v_space_needed) / 2
            
            start_point = boundary_corners[0] + h_unit * h_offset + v_unit * v_offset
            
            # ✅ CLEAN PANEL PLACEMENT: Clear only this side's panels before placing new ones
            self._clear_panels_for_side(side)
            
            # Place panels
            panels_placed = self.place_panels_on_trapezoid(
                start_point, h_unit, v_unit, normal,
                panels_horizontal, panels_vertical,
                panel_length_m, panel_width_m, panel_gap_m, panel_offset_m
            )
            
            # Store count
            self.panels_count_by_side[side] = panels_placed
            
            print(f"✅ Placed {panels_placed} panels on {side.upper()} side")
            return panels_placed
            
        except Exception as e:
            print(f"❌ Error placing solar panels: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def show_installation_area(self, start_point, h_unit, v_unit, h_length, v_length, 
                            normal, h_edge_offset, v_edge_offset, panel_offset):
        """Visualize the installation area boundary"""
        # Clear existing boundary actors
        for actor in self.boundary_actors:
            self.plotter.remove_actor(actor)
        self.boundary_actors = []
        
        # Calculate corners WITHOUT panel_offset for boundaries
        # Boundaries should be on the roof surface, not offset from it
        adjusted_start = start_point + h_unit * h_edge_offset + v_unit * v_edge_offset
        adjusted_bottom_right = start_point + h_unit * (h_length - h_edge_offset) + v_unit * v_edge_offset
        adjusted_top_right = start_point + h_unit * (h_length - h_edge_offset) + v_unit * (v_length - v_edge_offset)
        adjusted_top_left = start_point + h_unit * h_edge_offset + v_unit * (v_length - v_edge_offset)
        
        corners = [adjusted_start, adjusted_bottom_right, adjusted_top_right, adjusted_top_left]
        
        # Create boundary visualization (still on roof surface)
        boundary_actors = self.create_boundary_lines(corners)
        self.boundary_actors.extend(boundary_actors)
        
        return corners

    def place_panels_on_trapezoid(self, start_point, h_unit, v_unit, normal,
                                panels_h, panels_v, panel_length, panel_width,
                                panel_gap, panel_offset):
        """Place panel meshes with proper offset from roof surface"""
        # Clear existing panel actors
        for actor in self.panel_actors:
            self.plotter.remove_actor(actor)
        self.panel_actors = []
        
        # Apply the configured offset
        offset_vector = normal * panel_offset
        
        panels_placed = 0
        panels_skipped = 0
        valid_panels = []
        
        # Calculate panel positions
        for h in range(panels_h):
            for v in range(panels_v):
                h_pos = h * (panel_width + panel_gap)
                v_pos = v * (panel_length + panel_gap)
                
                # Place on roof surface, then add the configured offset
                panel_base = start_point + h_unit * h_pos + v_unit * v_pos
                panel_start = panel_base + offset_vector
                panel_center = panel_start + h_unit * (panel_width/2) + v_unit * (panel_length/2)
                
                # Check obstacles
                skip_panel = False
                if hasattr(self.roof, 'obstacles') and self.roof.obstacles:
                    for obstacle in self.roof.obstacles:
                        if self.check_obstacle_intersection(
                            panel_center, panel_width, panel_length,
                            (h_unit, v_unit, normal), obstacle
                        ):
                            skip_panel = True
                            panels_skipped += 1
                            break
                
                if skip_panel:
                    continue
                
                # Store valid panel with proper offset
                valid_panels.append({
                    'center': panel_center,
                    'width_dir': h_unit,
                    'length_dir': v_unit,
                    'normal': normal
                })
                panels_placed += 1
        
        # Store skipped panels data
        self.panels_skipped_by_side[self.current_side] = panels_skipped
        
        # Create batched mesh
        if valid_panels:
            self._create_panel_batch(valid_panels)
        
        return panels_placed

    def calculate_performance_data(self, panel_count, side):
        """Calculate solar performance data for gable roof"""
        # Update the panels_count_by_side dictionary
        self.panels_count_by_side[side] = panel_count
        
        # Get roof angle
        angle_rad = self.roof.slope_angle
        angle_degrees = np.degrees(angle_rad)
        
        # Use base class performance calculation
        perf_data = self.calculate_performance(
            angle_degrees=angle_degrees,
            active_sides=[side]
        )
        
        # Add gable-specific data
        perf_data.update({
            'side': side,
            'panels_skipped': sum(self.panels_skipped_by_side.values()),
            'side_counts': {s: count for s, count in self.panels_count_by_side.items() if count > 0}
        })
        
        return perf_data
    
    def _clear_panels_for_side(self, side):
        """Clear panels for specific side only"""
        if side in self.panels_by_side:
            for actor in self.panels_by_side[side]:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                    except:
                        pass
            self.panels_by_side[side] = []
            print(f"🧹 Cleared existing panels for {side} side")

    def _clear_boundaries_for_side(self, side):
        """Clear boundaries for specific side only"""
        if side in self.boundaries_by_side:
            for actor in self.boundaries_by_side[side]:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                    except:
                        pass
            self.boundaries_by_side[side] = []
            print(f"🧹 Cleared existing boundaries for {side} side")

    def remove_panels_from_side(self, side):
        """Remove panels from specific side ONLY - Enhanced version"""
        print(f"\n🗑️ === REMOVE_PANELS_FROM_SIDE ===")
        print(f"🗑️ Removing panels from: {side}")
        
        # Remove from active sides
        if side in self.active_sides:
            self.active_sides.remove(side)
            print(f"✅ Removed {side} from active_sides")
        
        # Clear panels for this side
        self._clear_panels_for_side(side)
        
        # Clear boundaries for this side
        self._clear_boundaries_for_side(side)
        
        # Reset counts for this side
        self.panels_count_by_side[side] = 0
        self.panels_skipped_by_side[side] = 0
        
        print(f"✅ Reset panel count for {side}")
        print(f"🗑️ After removal - active_sides: {list(self.active_sides)}")
        print(f"🗑️ === REMOVE_PANELS_FROM_SIDE COMPLETED ===\n")
        