from .base.base_panel_handler import BasePanelHandler
from .utils.solar_panel_utils import PanelGeometry
from .utils.panel_performance import PerformanceCalculator
import numpy as np
import pyvista as pv
import time

class SolarPanelPlacementPyramid(BasePanelHandler):
    """Handler for placing solar panels on pyramid roofs - COMPLETE FIXED VERSION"""
    
    def __init__(self, pyramid_roof):
        super().__init__(pyramid_roof, "pyramid")
        
        # Pyramid-specific tracking
        self.panels_by_side = {
            "front": [], "right": [], "back": [], "left": []
        }
        self.boundaries_by_side = {
            "front": [], "right": [], "back": [], "left": []
        }
        
        # Panel template for instancing
        self.panel_template = None
        self.panel_meshes_by_side = {
            "front": [], "right": [], "back": [], "left": []
        }
        
        # ✅ COMPLETE CALL PROTECTION SYSTEM
        self._last_call_time = {}
        self._call_stack = []
        self._processing = False
        self._call_counter = 0
        self._blocked_calls = 0
        
        # Create panel template
        self.create_panel_template()
        
        print(f"✅ Pyramid solar panel handler initialized with complete call protection")
        print(f"✅ Handler ID: {id(self)}")
    
    def create_panel_template(self):
        """Create template panel for instancing"""
        try:
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            
            self.panel_template = pv.Plane(
                center=[0, 0, 0],
                direction=[0, 0, 1],
                i_size=panel_width_m,
                j_size=panel_length_m,
                i_resolution=1,
                j_resolution=1
            )
            
            # Set texture coordinates
            self.panel_template.texture_coordinates = np.array([
                [0, 0], [1, 0], [1, 1], [0, 1]
            ])
            
            print("✅ Panel template created successfully")
            
        except Exception as e:
            print(f"❌ Error creating panel template: {e}")
    
    def add_panels(self, side):
        """Add panels to specific side with COMPLETE call protection"""
        
        # ✅ ENHANCED CALL PROTECTION
        current_time = time.time()
        call_id = f"pyramid_add_panels_{side}_{current_time}_{self._call_counter}"
        self._call_counter += 1
        
        print(f"\n🔧 === PYRAMID ADD_PANELS CALLED ===")
        print(f"🔧 Call ID: {call_id}")
        print(f"🔧 Requested side: {side}")
        print(f"🔧 Handler ID: {id(self)}")
        print(f"🔧 Call stack depth: {len(self._call_stack)}")
        print(f"🔧 Currently processing: {self._processing}")
        print(f"🔧 Blocked calls so far: {self._blocked_calls}")
        
        # ✅ PROTECTION 1: Check if already processing
        if self._processing:
            self._blocked_calls += 1
            print(f"🚨 BLOCKED #{self._blocked_calls}: Already processing another call")
            return
        
        # ✅ PROTECTION 2: Check call cooldown (500ms)
        if side in self._last_call_time:
            time_since_last = current_time - self._last_call_time[side]
            if time_since_last < 0.5:  # 500ms cooldown
                self._blocked_calls += 1
                print(f"🚨 BLOCKED #{self._blocked_calls}: Call too soon ({time_since_last:.3f}s < 0.5s)")
                return
        
        # ✅ PROTECTION 3: Check if exact call already in stack
        if call_id in self._call_stack:
            self._blocked_calls += 1
            print(f"🚨 BLOCKED #{self._blocked_calls}: Duplicate call ID in stack")
            return
        
        # ✅ PROTECTION 4: Limit call stack depth
        if len(self._call_stack) >= 3:
            self._blocked_calls += 1
            print(f"🚨 BLOCKED #{self._blocked_calls}: Call stack too deep ({len(self._call_stack)} calls)")
            return
        
        # ✅ PROTECTION 5: Validate side
        if side not in ["front", "right", "back", "left"]:
            print(f"❌ Invalid side: {side}")
            return
        
        # ✅ SET PROTECTION FLAGS
        self._processing = True
        self._call_stack.append(call_id)
        self._last_call_time[side] = current_time
        
        try:
            print(f"🔧 PROCEEDING with call {call_id}")
            print(f"🔧 Current active_sides: {list(self.active_sides)}")
            
            # ✅ TOGGLE FUNCTIONALITY
            is_currently_active = side in self.active_sides
            print(f"🔧 Is {side} currently active? {is_currently_active}")
            
            if is_currently_active:
                print(f"🔧 TOGGLE OFF: Removing panels from {side} side")
                self.remove_panels_from_side(side)
                print(f"🔧 After toggle off, active_sides: {list(self.active_sides)}")
                return
                
            # Max 2 sides limit
            if len(self.active_sides) >= 2:
                oldest_side = next(iter(self.active_sides))
                print(f"🔧 Max 2 sides reached. Removing oldest: {oldest_side}")
                self.remove_panels_from_side(oldest_side)
                print(f"🔧 After removing oldest, active_sides: {list(self.active_sides)}")
            
            # Set current side
            self.current_side = side
            
            # ✅ PLACE PANELS (single call only)
            placement_methods = {
                "front": self.place_front_panels,
                "right": self.place_right_panels,
                "back": self.place_back_panels,
                "left": self.place_left_panels
            }
            
            if side in placement_methods:
                print(f"🔧 Calling placement method for {side}")
                placement_methods[side]()
                
                # Check if panels were placed
                panels_placed = self.panels_count_by_side.get(side, 0)
                if panels_placed > 0:
                    self.active_sides.add(side)
                    print(f"✅ Added {panels_placed} panels to {side} side")
                else:
                    print(f"⚠️ No panels placed on {side} side")
            
            # Single render call
            self.plotter.render()
            print(f"🔧 === PYRAMID ADD_PANELS COMPLETED ===")
            
        except Exception as e:
            print(f"❌ Error in add_panels: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # ✅ ALWAYS CLEAN UP PROTECTION FLAGS
            if call_id in self._call_stack:
                self._call_stack.remove(call_id)
            self._processing = False
            print(f"🔧 Cleaned up call protection for {call_id}")
            print(f"🔧 Final call stack depth: {len(self._call_stack)}")
    
    def remove_panels_from_side(self, side):
        """Remove panels from specific side - ENHANCED VERSION"""
        print(f"\n🗑️ === REMOVE_PANELS_FROM_SIDE ===")
        print(f"🗑️ Removing panels from: {side}")
        print(f"🗑️ Before removal - active_sides: {list(self.active_sides)}")
        
        # Debug: Check what we have to remove
        panel_actors_count = len(self.panels_by_side.get(side, []))
        boundary_actors_count = len(self.boundaries_by_side.get(side, []))
        print(f"🗑️ Panel actors to remove: {panel_actors_count}")
        print(f"🗑️ Boundary actors to remove: {boundary_actors_count}")
        
        # Remove from active sides
        if side in self.active_sides:
            self.active_sides.remove(side)
            print(f"✅ Removed {side} from active_sides")
        else:
            print(f"⚠️ {side} was not in active_sides")
        
        # ✅ ENHANCED: Remove panel actors for this side
        panels_removed = 0
        if side in self.panels_by_side:
            for actor in self.panels_by_side[side]:
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                        panels_removed += 1
                        print(f"✅ Removed panel actor {panels_removed}")
                    except Exception as e:
                        print(f"⚠️ Error removing panel actor: {e}")
            
            # Clear the list
            self.panels_by_side[side] = []
            print(f"✅ Removed {panels_removed} panel actors from {side}")
        
        # ✅ ENHANCED: Remove boundary actors for this side
        boundaries_removed = 0
        if side in self.boundaries_by_side:
            for i, actor in enumerate(self.boundaries_by_side[side]):
                if actor is not None:
                    try:
                        self.plotter.remove_actor(actor)
                        boundaries_removed += 1
                        print(f"✅ Removed boundary actor {boundaries_removed} (was index {i})")
                    except Exception as e:
                        print(f"⚠️ Error removing boundary actor {i}: {e}")
            
            # Clear the list
            self.boundaries_by_side[side] = []
            print(f"✅ Removed {boundaries_removed} boundary actors from {side}")
        
        # Clear pending meshes
        if side in self.panel_meshes_by_side:
            self.panel_meshes_by_side[side] = []
        
        # Reset counts for this side
        old_count = self.panels_count_by_side.get(side, 0)
        self.panels_count_by_side[side] = 0
        self.panels_skipped_by_side[side] = 0
        print(f"✅ Reset panel count for {side} (was {old_count}, now 0)")
        
        # ✅ FORCE RENDER UPDATE
        try:
            self.plotter.render()
            print(f"✅ Forced plotter render after removal")
        except Exception as e:
            print(f"⚠️ Error rendering after removal: {e}")
        
        print(f"🗑️ After removal - active_sides: {list(self.active_sides)}")
        print(f"🗑️ === REMOVE_PANELS_FROM_SIDE COMPLETED ===\n")
    
    def place_front_panels(self):
        """Place panels on front triangular face - PROTECTED"""
        if self._processing and len(self._call_stack) > 1:
            print(f"🚨 BLOCKED: place_front_panels called during processing")
            return
            
        try:
            print(f"🏠 === PLACE_FRONT_PANELS ===")
            points = self.roof.roof_points
            bottom_left = points['front_left']
            bottom_right = points['front_right']
            top = points['peak']
            
            print(f"🏠 Front geometry: left={bottom_left}, right={bottom_right}, peak={top}")
            
            # Use common triangular boundary creation
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=True
            )
            
            # Use common triangle placement
            panel_count = self.place_panels_on_triangle_surface(
                adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal
            )
            
            self.panels_count_by_side["front"] = panel_count
            print(f"✅ Placed {panel_count} panels on FRONT side")
            
        except Exception as e:
            print(f"❌ Error placing front panels: {e}")
            import traceback
            traceback.print_exc()
    
    def place_right_panels(self):
        """Place panels on right triangular face - PROTECTED"""
        if self._processing and len(self._call_stack) > 1:
            print(f"🚨 BLOCKED: place_right_panels called during processing")
            return
            
        try:
            print(f"🏠 === PLACE_RIGHT_PANELS ===")
            points = self.roof.roof_points
            bottom_left = points['front_right']
            bottom_right = points['back_right']
            top = points['peak']
            
            print(f"🏠 Right geometry: left={bottom_left}, right={bottom_right}, peak={top}")
            
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=False
            )
            
            panel_count = self.place_panels_on_triangle_surface(
                adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal
            )
            
            self.panels_count_by_side["right"] = panel_count
            print(f"✅ Placed {panel_count} panels on RIGHT side")
            
        except Exception as e:
            print(f"❌ Error placing right panels: {e}")
            import traceback
            traceback.print_exc()
    
    def place_back_panels(self):
        """Place panels on back triangular face - PROTECTED"""
        if self._processing and len(self._call_stack) > 1:
            print(f"🚨 BLOCKED: place_back_panels called during processing")
            return
            
        try:
            print(f"🏠 === PLACE_BACK_PANELS ===")
            points = self.roof.roof_points
            bottom_left = points['back_right']
            bottom_right = points['back_left']
            top = points['peak']
            
            print(f"🏠 Back geometry: left={bottom_left}, right={bottom_right}, peak={top}")
            
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=False
            )
            
            panel_count = self.place_panels_on_triangle_surface(
                adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal
            )
            
            self.panels_count_by_side["back"] = panel_count
            print(f"✅ Placed {panel_count} panels on BACK side")
            
        except Exception as e:
            print(f"❌ Error placing back panels: {e}")
            import traceback
            traceback.print_exc()
    
    def place_left_panels(self):
        """Place panels on left triangular face - PROTECTED"""
        if self._processing and len(self._call_stack) > 1:
            print(f"🚨 BLOCKED: place_left_panels called during processing")
            return
            
        try:
            print(f"🏠 === PLACE_LEFT_PANELS ===")
            points = self.roof.roof_points
            bottom_left = points['back_left']
            bottom_right = points['front_left']
            top = points['peak']
            
            print(f"🏠 Left geometry: left={bottom_left}, right={bottom_right}, peak={top}")
            
            adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal = self.create_triangular_boundary(
                bottom_left, bottom_right, top, is_front=False
            )
            
            panel_count = self.place_panels_on_triangle_surface(
                adjusted_bottom_left, adjusted_bottom_right, adjusted_top, normal
            )
            
            self.panels_count_by_side["left"] = panel_count
            print(f"✅ Placed {panel_count} panels on LEFT side")
            
        except Exception as e:
            print(f"❌ Error placing left panels: {e}")
            import traceback
            traceback.print_exc()
    
    def create_triangular_boundary(self, eave_left, eave_right, apex, is_front=True, min_offset=300):
        """Override base class method to use per-side boundary tracking"""
        print(f"🔶 === PYRAMID: CREATING TRIANGULAR BOUNDARY FOR {self.current_side.upper()} ===")
        
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
        
        # ✅ PYRAMID-SPECIFIC: Use per-side boundary tracking instead of base class
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
    
    def _create_panel_batch(self, valid_panels):
        """Override base class method to store actors in per-side tracking"""
        if not valid_panels:
            return
        
        print(f"🔧 Creating {len(valid_panels)} panels for {self.current_side} side")
        
        # Create combined mesh (same as base class logic)
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
        
        # ✅ CRITICAL: Store the actor in the correct side (NOT base class)
        if hasattr(self, 'current_side') and self.current_side:
            if self.current_side not in self.panels_by_side:
                self.panels_by_side[self.current_side] = []
            
            self.panels_by_side[self.current_side].append(panel_actor)
            print(f"✅ Stored panel actor for {self.current_side} side")
            print(f"✅ Total actors for {self.current_side}: {len(self.panels_by_side[self.current_side])}")
        else:
            print(f"❌ No current_side set - cannot store panel actors!")
    
    def clear_panels(self):
        """Clear all panels and reset tracking"""
        print("🧹 Clearing all pyramid panels...")
        
        # Clear all sides
        for side in ["front", "right", "back", "left"]:
            if side in self.active_sides:
                self.remove_panels_from_side(side)
        
        # Clear active sides set
        self.active_sides.clear()
        self.current_side = None
        
        # Reset call protection
        self._last_call_time = {}
        self._call_stack = []
        self._processing = False
        self._blocked_calls = 0
        
        # Clear base class actors as well (just in case)
        try:
            super().clear_panels()
        except:
            pass
        
        print("✅ All pyramid panels cleared")
    
    def update_panel_config(self, config):
        """Update panel configuration with re-placement"""
        if config is None:
            return False
        
        try:
            # Store active sides
            active_sides_copy = list(self.active_sides)
            
            # Update configuration using base class
            success = super().update_panel_config(config)
            if not success:
                return False
            
            # Recreate template with new dimensions
            self.create_panel_template()
            
            # Re-place panels on active sides
            if active_sides_copy:
                # Clear all panels
                self.clear_panels()
                
                # Re-add panels to all previously active sides
                for side in active_sides_copy:
                    self.add_panels(side)
            
            return True
            
        except Exception as e:
            print(f"Error updating panel config: {e}")
            return False
    
    def refresh_language(self):
        """Update displayed text when language changes - CLEANED"""
        try:
            # Re-place panels if any are active
            active_sides = list(self.active_sides)
            if active_sides:
                current_side = self.current_side
                self.clear_panels()
                for side in active_sides:
                    self.add_panels(side)
                print(f"Language updated, refreshed panels on {', '.join(active_sides)}")
            else:
                print("Language updated, will apply to next panel placement")
                
        except Exception as e:
            print(f"Error refreshing language: {e}")
    
    def setup_key_bindings(self, *args, **kwargs):
        """Override to prevent duplicate key bindings"""
        print("⚠️ PyramidRoof key binding setup blocked - using Roof Generation Manager bindings")
        pass
    
    def _setup_key_bindings(self, *args, **kwargs):
        """Override to prevent duplicate key bindings"""
        print("⚠️ PyramidRoof _setup_key_bindings blocked")
        pass
