from .base.base_panel_handler import BasePanelHandler
from .utils.solar_panel_utils import PanelGeometry
from .utils.panel_performance import PerformanceCalculator
import numpy as np
import pyvista as pv
import time

class SolarPanelPlacementHip(BasePanelHandler):
    """Handler for placing solar panels on hip roofs - FIXED VERSION"""
    
    def __init__(self, hip_roof):
        super().__init__(hip_roof, "hip")
        
        # Hip-specific tracking
        self.panels_by_side = {
            "front": [], "right": [], "back": [], "left": []
        }
        self.boundaries_by_side = {
            "front": [], "right": [], "back": [], "left": []
        }
        
        # Add cooldown tracking to prevent rapid calls
        self._last_call_time = {}
        
        print(f"✅ Hip solar panel handler initialized")
        print(f"✅ Initial active_sides: {list(self.active_sides)}")
    
    def add_panels(self, side):
        """Add panels to hip roof side with proper single-side handling"""
        print(f"\n🔧 === HIP ADD_PANELS CALLED ===")
        print(f"🔧 Requested side: {side}")
        print(f"🔧 Current active_sides: {list(self.active_sides)}")
        
        # Validate side
        if side not in ["front", "right", "back", "left"]:
            print(f"❌ Invalid side: {side}")
            return
        
        # Cooldown check to prevent rapid calls
        current_time = time.time()
        if side in self._last_call_time:
            if current_time - self._last_call_time[side] < 0.5:  # 500ms cooldown
                print(f"⏰ Cooldown active for {side}, ignoring call")
                return
        self._last_call_time[side] = current_time
        
        # Check if this side is already active (TOGGLE functionality)
        is_currently_active = side in self.active_sides
        print(f"🔧 Is {side} currently active? {is_currently_active}")
        
        if is_currently_active:
            print(f"🔧 TOGGLE OFF: Removing panels from {side} side")
            self.remove_panels_from_side(side)
            print(f"🔧 After toggle off, active_sides: {list(self.active_sides)}")
            return
        
        # Check 2-side limit
        if len(self.active_sides) >= 2:
            oldest_side = next(iter(self.active_sides))
            print(f"🔧 Max 2 sides reached. Removing oldest: {oldest_side}")
            self.remove_panels_from_side(oldest_side)
            print(f"🔧 After removing oldest, active_sides: {list(self.active_sides)}")
        
        # Place panels on the requested side ONLY
        print(f"🔧 Placing panels on {side} side...")
        self.current_side = side
        
        # Call the specific placement method
        placement_success = False
        try:
            if side == "front":
                placement_success = self.place_front_panels()
            elif side == "right":
                placement_success = self.place_right_panels()
            elif side == "back":
                placement_success = self.place_back_panels()
            elif side == "left":
                placement_success = self.place_left_panels()
            
            print(f"🔧 Placement method completed. Success: {placement_success}")
            
        except Exception as e:
            print(f"❌ Error in placement method: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Check if panels were actually placed
        panels_placed = self.panels_count_by_side.get(side, 0)
        print(f"🔧 Panels placed on {side}: {panels_placed}")
        
        if panels_placed > 0:
            # Add to active sides
            self.active_sides.add(side)
            print(f"✅ Added {side} to active_sides")
            print(f"✅ Final active_sides: {list(self.active_sides)}")
        else:
            print(f"⚠️ No panels placed on {side} - not adding to active_sides")
        
        # Update display
        self.plotter.render()
        print(f"🔧 === HIP ADD_PANELS COMPLETED ===\n")
    
    def remove_panels_from_side(self, side):
        """Remove panels from specific side ONLY"""
        print(f"\n🗑️ === REMOVE_PANELS_FROM_SIDE ===")
        print(f"🗑️ Removing panels from: {side}")
        print(f"🗑️ Before removal - active_sides: {list(self.active_sides)}")
        print(f"🗑️ Panel actors to remove: {len(self.panels_by_side.get(side, []))}")
        print(f"🗑️ Boundary actors to remove: {len(self.boundaries_by_side.get(side, []))}")
        
        # Remove from active sides
        if side in self.active_sides:
            self.active_sides.remove(side)
            print(f"✅ Removed {side} from active_sides")
        else:
            print(f"⚠️ {side} was not in active_sides")
        
        # Remove panel actors for this side
        panels_removed = 0
        if side in self.panels_by_side:
            for actor in self.panels_by_side[side]:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                        panels_removed += 1
                    except Exception as e:
                        print(f"⚠️ Error removing panel actor: {e}")
            
            # Clear the list
            self.panels_by_side[side] = []
            print(f"✅ Removed {panels_removed} panel actors from {side}")
        
        # Remove boundary actors for this side
        boundaries_removed = 0
        if side in self.boundaries_by_side:
            for actor in self.boundaries_by_side[side]:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                        boundaries_removed += 1
                    except Exception as e:
                        print(f"⚠️ Error removing boundary actor: {e}")
            
            # Clear the list
            self.boundaries_by_side[side] = []
            print(f"✅ Removed {boundaries_removed} boundary actors from {side}")
        
        # Reset counts and stored positions for this side
        old_count = self.panels_count_by_side.get(side, 0)
        self.panels_count_by_side[side] = 0
        self.panels_skipped_by_side[side] = 0
        self.panel_positions_by_side.pop(side, None)
        print(f"✅ Reset panel count for {side} (was {old_count}, now 0)")

        print(f"🗑️ After removal - active_sides: {list(self.active_sides)}")
        print(f"🗑️ === REMOVE_PANELS_FROM_SIDE COMPLETED ===\n")
    
    # Keep all your original methods but add debug calls
    def place_front_panels(self):
        """Place panels ONLY on front triangular slope"""
        print(f"🏠 === PLACE_FRONT_PANELS ===")
        self.debug_call_origin()  # ✅ ADD THIS
        
        try:
            # Clear existing panels/boundaries for front side only
            self.remove_panels_from_side("front")
            
            points = self.roof.roof_points
            eave_left = points['front_left']
            eave_right = points['front_right']
            ridge = points['ridge_front']
            
            print(f"🏠 Front geometry: left={eave_left}, right={eave_right}, ridge={ridge}")
            
            # Create boundary and place panels
            bottom_left, bottom_right, top, normal = self.create_triangular_boundary(
                eave_left, eave_right, ridge, is_front=True
            )
            
            panel_count = self.place_panels_on_triangle_surface(
                bottom_left, bottom_right, top, normal
            )
            
            self.panels_count_by_side["front"] = panel_count
            print(f"✅ Placed {panel_count} panels on FRONT side")
            return True
            
        except Exception as e:
            print(f"❌ Error in place_front_panels: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ✅ ADD THE SAME DEBUG TO OTHER PLACEMENT METHODS
    def place_left_panels(self):
        """Place panels ONLY on left trapezoidal slope"""
        print(f"🏠 === PLACE_LEFT_PANELS ===")
        self.debug_call_origin()  # ✅ ADD THIS
        
        try:
            # Clear existing panels/boundaries for left side only
            self.remove_panels_from_side("left")
            
            points = self.roof.roof_points
            eave_front = points['front_left']
            eave_back = points['back_left']
            ridge_front = points['ridge_front']
            ridge_back = points['ridge_back']
            
            print(f"🏠 Left geometry: eave_front={eave_front}, eave_back={eave_back}")
            
            # Create trapezoidal boundary
            bottom_front, bottom_back, top_back, top_front = self.create_trapezoidal_boundary(
                eave_front, eave_back, ridge_front, ridge_back, is_right=False
            )
            
            # Place panels on trapezoid
            panel_count = self.place_panels_on_trapezoid_surface(
                bottom_front, bottom_back, top_back, top_front
            )
            
            self.panels_count_by_side["left"] = panel_count
            print(f"✅ Placed {panel_count} panels on LEFT side")
            return True
            
        except Exception as e:
            print(f"❌ Error in place_left_panels: {e}")
            import traceback
            traceback.print_exc()
            return False
    

    def place_right_panels(self):
        """Place panels ONLY on right trapezoidal slope"""
        print(f"🏠 === PLACE_RIGHT_PANELS ===")
        try:
            # ❌ REMOVE THIS LINE:
            # self.remove_panels_from_side("right")
            
            points = self.roof.roof_points
            eave_front = points['front_right']
            eave_back = points['back_right']
            ridge_front = points['ridge_front']
            ridge_back = points['ridge_back']
            
            print(f"🏠 Right geometry: eave_front={eave_front}, eave_back={eave_back}")
            
            # Create trapezoidal boundary
            bottom_front, bottom_back, top_back, top_front = self.create_trapezoidal_boundary(
                eave_front, eave_back, ridge_front, ridge_back, is_right=True
            )
            
            # Place panels on trapezoid
            panel_count = self.place_panels_on_trapezoid_surface(
                bottom_front, bottom_back, top_back, top_front
            )
            
            self.panels_count_by_side["right"] = panel_count
            print(f"✅ Placed {panel_count} panels on RIGHT side")
            return True
            
        except Exception as e:
            print(f"❌ Error in place_right_panels: {e}")
            import traceback
            traceback.print_exc()
            return False

    def place_back_panels(self):
        """Place panels ONLY on back triangular slope"""
        print(f"🏠 === PLACE_BACK_PANELS ===")
        try:
            # ❌ REMOVE THIS LINE:
            # self.remove_panels_from_side("back")
            
            points = self.roof.roof_points
            eave_left = points['back_left']
            eave_right = points['back_right']
            ridge = points['ridge_back']
            
            print(f"🏠 Back geometry: left={eave_left}, right={eave_right}, ridge={ridge}")
            
            # Create boundary and place panels
            bottom_left, bottom_right, top, normal = self.create_triangular_boundary(
                eave_left, eave_right, ridge, is_front=False
            )
            
            panel_count = self.place_panels_on_triangle_surface(
                bottom_left, bottom_right, top, normal
            )
            
            self.panels_count_by_side["back"] = panel_count
            print(f"✅ Placed {panel_count} panels on BACK side")
            return True
            
        except Exception as e:
            print(f"❌ Error in place_back_panels: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def debug_call_origin(self):
        """Debug where the call is coming from"""
        import traceback
        import inspect
        
        print(f"\n🔍 === CALL ORIGIN DEBUG ===")
        
        # Get current stack
        stack = inspect.stack()
        
        print(f"🔍 Call stack ({len(stack)} frames):")
        for i, frame in enumerate(stack[:10]):  # Show first 10 frames
            filename = frame.filename.split('/')[-1]  # Just filename
            print(f"  {i}: {filename}:{frame.lineno} in {frame.function}")
        
        print(f"🔍 === CALL ORIGIN DEBUG END ===\n")

    def _create_panel_batch(self, valid_panels):
        """Create batched mesh and STORE ACTORS properly"""
        if not valid_panels:
            return
        
        print(f"🔧 Creating {len(valid_panels)} panels for {self.current_side} side")
        
        # Create combined mesh (your existing panel creation logic)
        combined_points = []
        combined_faces = []
        combined_tcoords = []
        
        panel_width_m = self.panel_width * self.mm_to_m
        panel_length_m = self.panel_length * self.mm_to_m
        
        face_offset = 0
        
        for panel_data in valid_panels:
            center = panel_data['center']
            width_dir = panel_data['width_dir']
            length_dir = panel_data['length_dir']
            normal = panel_data['normal']
            
            # Create panel corners
            half_width = panel_width_m / 2
            half_length = panel_length_m / 2
            
            corners = [
                center - width_dir * half_width - length_dir * half_length,
                center + width_dir * half_width - length_dir * half_length,
                center + width_dir * half_width + length_dir * half_length,
                center - width_dir * half_width + length_dir * half_length
            ]
            
            combined_points.extend(corners)
            combined_faces.extend([
                4, face_offset, face_offset + 1, face_offset + 2, face_offset + 3
            ])
            combined_tcoords.extend([[0, 0], [1, 0], [1, 1], [0, 1]])
            face_offset += 4
        
        # Create mesh
        combined_mesh = pv.PolyData(np.array(combined_points), faces=combined_faces)
        combined_mesh.active_texture_coordinates = np.array(combined_tcoords)
        
        # Load panel texture
        try:
            panel_texture = pv.read_texture("PVmizer/textures/solarpanel.png")
            panel_actor = self.plotter.add_mesh(combined_mesh, texture=panel_texture, show_edges=False)
        except:
            panel_actor = self.plotter.add_mesh(combined_mesh, color="navy", show_edges=False)
        
        # ✅ CRITICAL: Store the actor in the correct side
        if hasattr(self, 'current_side') and self.current_side:
            if self.current_side not in self.panels_by_side:
                self.panels_by_side[self.current_side] = []
            
            self.panels_by_side[self.current_side].append(panel_actor)
            print(f"✅ Stored panel actor for {self.current_side} side")
            print(f"✅ Total actors for {self.current_side}: {len(self.panels_by_side[self.current_side])}")
        else:
            print(f"❌ No current_side set - cannot store panel actors!")

    def create_trapezoidal_boundary(self, eave_front, eave_back, ridge_front, ridge_back, is_right):
        """Create trapezoidal boundary for hip roof sides"""
        # Calculate edge vectors
        eave_vector = eave_back - eave_front
        eave_length = np.linalg.norm(eave_vector)
        eave_dir = eave_vector / eave_length
        
        ridge_vector = ridge_back - ridge_front
        ridge_length = np.linalg.norm(ridge_vector)
        ridge_dir = ridge_vector / ridge_length
        
        # Calculate height vectors
        front_height_vector = ridge_front - eave_front
        front_height_length = np.linalg.norm(front_height_vector)
        front_height_dir = front_height_vector / front_height_length
        
        # Calculate normal
        if is_right:
            normal = np.cross(eave_dir, front_height_dir)
        else:
            normal = np.cross(front_height_dir, eave_dir)
        normal = normal / np.linalg.norm(normal)
        
        if normal[2] < 0:
            normal = -normal
        
        # Calculate offsets (in mm, then convert)
        min_offset = 300
        eave_length_mm = eave_length * 1000
        ridge_length_mm = ridge_length * 1000
        front_height_mm = front_height_length * 1000
        
        eave_offset_mm = max(min_offset, eave_length_mm * 0.10)
        ridge_offset_mm = max(min_offset, ridge_length_mm * 0.10)
        vertical_offset_mm = max(min_offset, front_height_mm * 0.10)
        
        # Convert to meters
        eave_offset = eave_offset_mm * self.mm_to_m
        ridge_offset = ridge_offset_mm * self.mm_to_m
        vertical_offset = vertical_offset_mm * self.mm_to_m
        edge_offset = self.edge_offset * self.mm_to_m
        panel_height = self.panel_height * self.mm_to_m
        
        # Calculate boundary points
        bottom_front = eave_front + eave_dir * eave_offset + front_height_dir * edge_offset
        bottom_back = eave_back - eave_dir * eave_offset + front_height_dir * edge_offset
        top_back = ridge_back - ridge_dir * ridge_offset - front_height_dir * vertical_offset
        top_front = ridge_front + ridge_dir * ridge_offset - front_height_dir * vertical_offset
        
        # Elevate above roof
        bottom_front = bottom_front + normal * panel_height
        bottom_back = bottom_back + normal * panel_height
        top_back = top_back + normal * panel_height
        top_front = top_front + normal * panel_height
        
        # ✅ Store boundary actors for THIS SIDE ONLY
        boundary_actors = self.create_boundary_lines([bottom_front, bottom_back, top_back, top_front])
        
        if self.current_side not in self.boundaries_by_side:
            self.boundaries_by_side[self.current_side] = []
        self.boundaries_by_side[self.current_side].extend(boundary_actors)
        
        return bottom_front, bottom_back, top_back, top_front
    
    def place_panels_on_trapezoid_surface(self, bottom_front, bottom_back, top_back, top_front):
        """Place panels on trapezoidal surface"""
        try:
            # Calculate directions
            bottom_edge = bottom_back - bottom_front
            bottom_length = np.linalg.norm(bottom_edge)
            bottom_dir = bottom_edge / bottom_length
            
            top_edge = top_back - top_front
            top_length = np.linalg.norm(top_edge)
            top_dir = top_edge / top_length
            
            # Height direction
            bottom_mid = (bottom_front + bottom_back) / 2
            top_mid = (top_front + top_back) / 2
            height_vector = top_mid - bottom_mid
            height_length = np.linalg.norm(height_vector)
            height_dir = height_vector / height_length
            
            # Normal
            normal = np.cross(bottom_dir, height_dir)
            normal /= np.linalg.norm(normal)
            
            # Panel dimensions
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            panel_gap_m = self.panel_gap * self.mm_to_m
            
            # Calculate spacing
            vertical_spacing_m = panel_length_m + panel_gap_m
            horizontal_spacing_m = panel_width_m + panel_gap_m
            
            # Calculate rows
            num_rows = max(1, int((height_length - panel_gap_m) / vertical_spacing_m))
            vertical_start_offset_m = panel_gap_m
            
            count = 0
            skipped_panels = 0
            valid_panels = []
            
            # Place panels row by row
            for row in range(num_rows):
                row_height_m = vertical_start_offset_m + row * vertical_spacing_m
                
                if row_height_m + panel_length_m > height_length:
                    break
                
                # Height ratio for interpolation
                height_ratio = row_height_m / height_length
                
                # Interpolate row width and direction
                row_width_m = bottom_length * (1 - height_ratio) + top_length * height_ratio
                row_center = bottom_mid + height_dir * row_height_m
                row_dir = bottom_dir * (1 - height_ratio) + top_dir * height_ratio
                row_dir = row_dir / np.linalg.norm(row_dir)
                
                # Calculate inset and panels in row
                side_inset_m = panel_gap_m * 1.5
                usable_row_width_m = max(0, row_width_m - 2 * side_inset_m)
                num_panels_in_row = int((usable_row_width_m + panel_gap_m/2) / horizontal_spacing_m)
                
                if num_panels_in_row < 1:
                    continue
                
                # Center panels
                actual_width_used_m = num_panels_in_row * horizontal_spacing_m - panel_gap_m
                horizontal_start_offset_m = (usable_row_width_m - actual_width_used_m) / 2 + side_inset_m
                
                row_left_edge = row_center - row_dir * (row_width_m / 2)
                row_start = row_left_edge + row_dir * horizontal_start_offset_m
                
                # Place panels in row
                for col in range(num_panels_in_row):
                    panel_center = (row_start +
                                row_dir * (col * horizontal_spacing_m + panel_width_m / 2) +
                                height_dir * (panel_length_m / 2))
                    
                    # Check obstacles
                    skip_panel = False
                    if hasattr(self.roof, 'obstacles') and self.roof.obstacles:
                        for obstacle in self.roof.obstacles:
                            if self.check_obstacle_intersection(
                                panel_center, panel_width_m, panel_length_m,
                                (row_dir, height_dir, normal), obstacle
                            ):
                                skip_panel = True
                                skipped_panels += 1
                                break
                    
                    if skip_panel:
                        continue
                    
                    # Store valid panel
                    valid_panels.append({
                        'center': panel_center,
                        'width_dir': row_dir,
                        'length_dir': height_dir,
                        'normal': normal
                    })
                    count += 1
            
            # Create batched mesh
            if valid_panels:
                self._create_panel_batch(valid_panels)
            
            # Store skipped count
            if self.current_side:
                self.panels_skipped_by_side[self.current_side] = skipped_panels
            
            return count
            
        except Exception as e:
            print(f"Error placing panels on trapezoid: {e}")
            return 0
    
    def update_panel_config(self, config):
        """Update panel configuration with re-placement"""
        try:
            # Store active sides
            active_sides_before = list(self.active_sides)
            
            # Save camera position
            camera_pos = self.plotter.camera_position
            
            # Update configuration using base class
            success = super().update_panel_config(config)
            if not success:
                return False
            
            # Re-place panels on active sides
            if active_sides_before:
                # Clear all panels first
                for side in active_sides_before:
                    self.remove_panels_from_side(side)
                
                # Re-place on each side
                for side in active_sides_before:
                    self.add_panels(side)
                
                # Restore camera position
                self.plotter.camera_position = camera_pos
                self.plotter.render()
            
            return True
            
        except Exception as e:
            print(f"Error updating panel config: {e}")
            return False

    def create_triangular_boundary(self, eave_left, eave_right, apex, is_front=True, min_offset=300):
        """Override base class method to use per-side boundary tracking"""
        print(f"🔶 === HIP: CREATING TRIANGULAR BOUNDARY FOR {self.current_side.upper()} ===")
        
        # Calculate vectors (same as base class)
        base_vector = eave_right - eave_left
        base_length = np.linalg.norm(base_vector)
        base_dir = base_vector / base_length
        
        base_mid = (eave_left + eave_right) / 2
        height_vector = apex - base_mid
        height_length = np.linalg.norm(height_vector)
        height_dir = height_vector / height_length
        
        # Calculate normal vector (same as base class)
        if is_front:
            normal = np.cross(base_dir, height_dir)
        else:
            normal = np.cross(height_dir, base_dir)
        normal = normal / np.linalg.norm(normal)
        
        if normal[2] < 0:
            normal = -normal
        
        # Convert to mm for calculations (same as base class)
        base_length_mm = base_length * 1000
        height_length_mm = height_length * 1000
        
        # Calculate offsets (same as base class)
        horizontal_offset_mm = max(min_offset, base_length_mm * 0.15)
        vertical_offset_mm = max(min_offset, height_length_mm * 0.20)
        
        # Check available space (same as base class)
        available_width_mm = base_length_mm - 2 * horizontal_offset_mm
        available_height_mm = height_length_mm - vertical_offset_mm - self.edge_offset
        
        # Adjust if needed (same as base class)
        if available_width_mm < self.panel_width + 2 * self.panel_gap:
            horizontal_offset_mm = max(100, (base_length_mm - self.panel_width - 2 * self.panel_gap) / 2)
        
        if available_height_mm < self.panel_length + 2 * self.panel_gap:
            vertical_offset_mm = max(100, (height_length_mm - self.panel_length - 2 * self.panel_gap))
        
        # Convert back to meters (same as base class)
        horizontal_offset = horizontal_offset_mm * self.mm_to_m
        vertical_offset = vertical_offset_mm * self.mm_to_m
        edge_offset = self.edge_offset * self.mm_to_m
        panel_height = self.panel_height * self.mm_to_m
        
        # Calculate boundary points (same as base class)
        bottom_left = eave_left + base_dir * horizontal_offset + height_dir * edge_offset
        bottom_right = eave_right - base_dir * horizontal_offset + height_dir * edge_offset
        top = apex - height_dir * vertical_offset
        
        # Elevate above roof (same as base class)
        bottom_left = bottom_left + normal * panel_height
        bottom_right = bottom_right + normal * panel_height
        top = top + normal * panel_height
        
        # ✅ HIP-SPECIFIC: Use per-side boundary tracking instead of base class
        boundary_actors = self.create_boundary_lines([bottom_left, bottom_right, top])
        
        # ✅ Store in per-side tracking (NOT base class boundary_actors list)
        if self.current_side not in self.boundaries_by_side:
            self.boundaries_by_side[self.current_side] = []
        self.boundaries_by_side[self.current_side].extend(boundary_actors)
        
        print(f"🔶 Stored {len(boundary_actors)} boundary actors for {self.current_side}")
        print(f"🔶 Total boundary actors for {self.current_side}: {len(self.boundaries_by_side[self.current_side])}")
        
        return bottom_left, bottom_right, top, normal
    
    def create_boundary_lines(self, points, color="yellow", line_width=3):
        """Override base class method to ensure proper tracking"""
        boundary_actors = []
        
        # Create boundary lines (same as base class)
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            line = pv.Line(start, end)
            actor = self.plotter.add_mesh(line, color=color, line_width=line_width)
            boundary_actors.append(actor)
            print(f"🔶 Created boundary line {i+1} for {self.current_side}")
        
        # Add corner markers (same as base class)
        for i, point in enumerate(points):
            marker = pv.Sphere(radius=0.08, center=point)
            actor = self.plotter.add_mesh(marker, color=color, render_points_as_spheres=True)
            boundary_actors.append(actor)
            print(f"🔶 Created boundary marker {i+1} for {self.current_side}")
        
        # ✅ DON'T add to base class tracking - return for caller to handle
        print(f"🔶 Created {len(boundary_actors)} boundary actors (returning for per-side tracking)")
        
        return boundary_actors