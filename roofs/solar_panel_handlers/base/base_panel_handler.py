import pyvista as pv
import numpy as np
from ..utils.solar_panel_utils import load_panel_texture, PanelGeometry
from ..utils.panel_performance import PerformanceCalculator
from ..utils.obstacle_detection import ObstacleDetector

class BasePanelHandler:
    """Base class for all solar panel placement handlers"""
    
    def __init__(self, roof, roof_type="generic"):
        self.roof = roof
        self.plotter = roof.plotter
        self.roof_type = roof_type
        
        # Common panel parameters (in millimeters)
        self.panel_width = 1000
        self.panel_length = 1600
        self.panel_gap = 50
        self.panel_power = 400
        self.edge_offset = 300
        self.panel_height = 50
        self.panel_offset = 100  # Alternative name for panel_height
        
        # Roof-specific offsets
        self.horizontal_edge_offset = 300
        self.vertical_edge_offset = 300
        
        # Conversion factor
        self.mm_to_m = 0.001
        
        # Common tracking
        self.panels_count_by_side = {}
        self.panels_skipped_by_side = {}
        self.panel_actors = []
        self.boundary_actors = []
        self.wireframe_actors = []
        self.text_actor = None
        self.help_text_actor = None
        self.performance_actor = None
        self.current_side = None
        self.active_sides = set()
        self.enable_debug_display = False
        self.show_debug = False
        self.panel_positions_by_side = {}  # {side_name: [np.array([x,y,z]), ...]}
        
        # Load texture
        self.panel_texture = load_panel_texture()
        
        # Initialize specific tracking based on roof type
        self._initialize_tracking()
    
    def _initialize_tracking(self):
        """Initialize tracking dictionaries based on roof type"""
        if self.roof_type == "flat":
            sides = ['center', 'north', 'south', 'east', 'west']
        else:
            sides = ['front', 'right', 'back', 'left']
        
        for side in sides:
            self.panels_count_by_side[side] = 0
            self.panels_skipped_by_side[side] = 0
    
    def create_boundary_lines(self, points, color="yellow", line_width=3):
        """Create boundary visualization with lines and markers"""
        boundary_actors = []
        
        # Create boundary lines
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            line = pv.Line(start, end)
            actor = self.plotter.add_mesh(line, color=color, line_width=line_width)
            boundary_actors.append(actor)
        
        # Add corner markers
        for point in points:
            marker = pv.Sphere(radius=0.08, center=point)
            actor = self.plotter.add_mesh(marker, color=color, render_points_as_spheres=True)
            boundary_actors.append(actor)
        
        return boundary_actors
    
    def create_triangular_boundary(self, eave_left, eave_right, apex, is_front=True, min_offset=300):
        """Common triangular boundary creation for pyramid/gable roofs"""
        # Calculate vectors
        base_vector = eave_right - eave_left
        base_length = np.linalg.norm(base_vector)
        base_dir = base_vector / base_length
        
        base_mid = (eave_left + eave_right) / 2
        height_vector = apex - base_mid
        height_length = np.linalg.norm(height_vector)
        height_dir = height_vector / height_length
        
        # Calculate normal vector
        if is_front:
            normal = np.cross(base_dir, height_dir)
        else:
            normal = np.cross(height_dir, base_dir)
        normal = normal / np.linalg.norm(normal)
        
        if normal[2] < 0:
            normal = -normal
        
        # Convert to mm for calculations
        base_length_mm = base_length * 1000
        height_length_mm = height_length * 1000
        
        # Calculate offsets
        horizontal_offset_mm = max(min_offset, base_length_mm * 0.15)
        vertical_offset_mm = max(min_offset, height_length_mm * 0.20)
        
        # Check available space
        available_width_mm = base_length_mm - 2 * horizontal_offset_mm
        available_height_mm = height_length_mm - vertical_offset_mm - self.edge_offset
        
        # Adjust if needed
        if available_width_mm < self.panel_width + 2 * self.panel_gap:
            horizontal_offset_mm = max(100, (base_length_mm - self.panel_width - 2 * self.panel_gap) / 2)
        
        if available_height_mm < self.panel_length + 2 * self.panel_gap:
            vertical_offset_mm = max(100, (height_length_mm - self.panel_length - 2 * self.panel_gap))
        
        # Convert back to meters
        horizontal_offset = horizontal_offset_mm * self.mm_to_m
        vertical_offset = vertical_offset_mm * self.mm_to_m
        edge_offset = self.edge_offset * self.mm_to_m
        panel_height = self.panel_height * self.mm_to_m
        
        # Calculate boundary points
        bottom_left = eave_left + base_dir * horizontal_offset + height_dir * edge_offset
        bottom_right = eave_right - base_dir * horizontal_offset + height_dir * edge_offset
        top = apex - height_dir * vertical_offset
        
        # Elevate above roof
        bottom_left = bottom_left + normal * panel_height
        bottom_right = bottom_right + normal * panel_height
        top = top + normal * panel_height
        
        # Create boundary visualization
        boundary_actors = self.create_boundary_lines([bottom_left, bottom_right, top])
        self.boundary_actors.extend(boundary_actors)
        
        return bottom_left, bottom_right, top, normal
    
    def place_panels_on_triangle_surface(self, bottom_left, bottom_right, top, normal):
        """Common triangle panel placement logic"""
        try:
            # Calculate directions
            bottom_edge_vector = bottom_right - bottom_left
            bottom_edge_length = np.linalg.norm(bottom_edge_vector)
            bottom_edge_dir = bottom_edge_vector / bottom_edge_length

            bottom_mid = (bottom_left + bottom_right) / 2
            height_vector = top - bottom_mid
            height_length = np.linalg.norm(height_vector)
            height_dir = height_vector / height_length

            # Panel spacing
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            panel_gap_m = self.panel_gap * self.mm_to_m
            
            vertical_spacing_m = panel_length_m + panel_gap_m
            horizontal_spacing_m = panel_width_m + panel_gap_m
            
            # Calculate rows
            num_rows = max(1, int((height_length + panel_gap_m/2) / vertical_spacing_m))
            vertical_start_offset_m = panel_gap_m/2

            count = 0
            skipped_panels = 0
            valid_panels = []
            
            # Place panels row by row
            for row in range(num_rows):
                row_height_m = vertical_start_offset_m + row * vertical_spacing_m
                row_center = bottom_mid + height_dir * row_height_m

                # Row width shrinks as we go up
                scale_factor = 1.0 - (row_height_m / height_length)
                row_width_m = bottom_edge_length * scale_factor
                
                side_inset_m = panel_gap_m * (1 + row / max(1, num_rows - 1))
                usable_row_width_m = max(0, row_width_m - 2 * side_inset_m)

                num_panels_in_row = int((usable_row_width_m + panel_gap_m/2) / horizontal_spacing_m)

                if num_panels_in_row < 1:
                    continue

                actual_width_used_m = num_panels_in_row * horizontal_spacing_m - panel_gap_m
                horizontal_start_offset_m = (usable_row_width_m - actual_width_used_m) / 2 + side_inset_m

                row_left_edge = row_center - bottom_edge_dir * (row_width_m / 2)
                row_start = row_left_edge + bottom_edge_dir * horizontal_start_offset_m

                for col in range(num_panels_in_row):
                    panel_center = (row_start +
                                bottom_edge_dir * (col * horizontal_spacing_m + panel_width_m / 2) +
                                height_dir * (panel_length_m / 2))

                    # Check obstacles
                    skip_panel = False
                    if hasattr(self.roof, 'obstacles') and self.roof.obstacles:
                        for obstacle in self.roof.obstacles:
                            if self.check_obstacle_intersection(
                                panel_center, panel_width_m, panel_length_m, 
                                (bottom_edge_dir, height_dir, normal), obstacle
                            ):
                                skip_panel = True
                                skipped_panels += 1
                                break
                    
                    if skip_panel:
                        continue

                    valid_panels.append({
                        'center': panel_center,
                        'width_dir': bottom_edge_dir,
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
            print(f"Error placing panels on triangle: {e}")
            return 0
    
    def _create_panel_batch(self, valid_panels):
        """Create batched mesh for efficient rendering"""
        try:
            if not valid_panels:
                return

            # Store panel center positions for shadow ray-casting
            if self.current_side:
                self.panel_positions_by_side[self.current_side] = [
                    np.array(p['center'], dtype=float) for p in valid_panels
                ]
                
            panel_width_m = self.panel_width * self.mm_to_m
            panel_length_m = self.panel_length * self.mm_to_m
            
            transformed_panels = []
            
            for panel_data in valid_panels:
                panel = pv.Plane(
                    center=[0, 0, 0],
                    direction=[0, 0, 1],
                    i_size=panel_width_m,
                    j_size=panel_length_m
                )
                
                panel.texture_coordinates = np.array([
                    [0, 0], [1, 0], [1, 1], [0, 1]
                ])
                
                # Create transformation
                center = panel_data['center']
                width_dir = panel_data['width_dir'] / np.linalg.norm(panel_data['width_dir'])
                length_dir = panel_data['length_dir'] / np.linalg.norm(panel_data['length_dir'])
                normal = panel_data['normal'] / np.linalg.norm(panel_data['normal'])
                
                transform = np.eye(4)
                transform[:3, 0] = width_dir
                transform[:3, 1] = length_dir
                transform[:3, 2] = normal
                transform[:3, 3] = center
                
                panel.transform(transform)
                transformed_panels.append(panel)
            
            # Combine panels
            if len(transformed_panels) == 1:
                combined_mesh = transformed_panels[0]
            else:
                try:
                    multi_block = pv.MultiBlock(transformed_panels)
                    combined_mesh = multi_block.combine()
                except:
                    # Fallback
                    combined_mesh = transformed_panels[0].copy()
                    for i in range(1, len(transformed_panels)):
                        combined_mesh = combined_mesh.merge(transformed_panels[i])
            
            # Add to scene
            self.add_mesh_with_texture(combined_mesh)
            
        except Exception as e:
            print(f"Error creating panel batch: {e}")
    
    def update_debug_display_common(self, roof_type_specific_text=""):
        """Clean view — no debug overlay in 3D view"""
        try:
            if self.text_actor:
                self.plotter.remove_actor(self.text_actor)
                self.text_actor = None
            if self.performance_actor:
                self.plotter.remove_actor(self.performance_actor)
                self.performance_actor = None
        except Exception:
            pass
    
    def _build_debug_message(self, perf_data, _):
        """Build common debug message"""
        # Get side info
        side_info = []
        total_skipped = 0
        
        for side, count in perf_data.get('side_counts', {}).items():
            skipped = self.panels_skipped_by_side.get(side, 0)
            total_skipped += skipped
            
            # Translate side name
            side_translations = {
                'front': _('front_side'),
                'back': _('back_side'),
                'left': _('left_side'),
                'right': _('right_side'),
                'center': _('center'),
                'north': _('north'),
                'south': _('south'),
                'east': _('east'),
                'west': _('west')
            }
            
            side_name = side_translations.get(side.lower(), side.upper())
            
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
        debug_msg += f"{_('slope_angle')}: {perf_data.get('roof_angle_degrees', 0):.1f}°\n\n"
        
        debug_msg += f"{_('panel_power')}: {perf_data['panel_power_w']}W\n"
        debug_msg += f"{_('system_size')}: {perf_data['system_power_kw']:.2f}kWp ({perf_data['system_power_w']:.0f}W)\n"
        debug_msg += f"{_('est_annual_production')}: {perf_data['annual_energy_kwh']:.0f}kWh\n"
        debug_msg += f"{_('est_daily_production')}: {perf_data['daily_energy_kwh']:.1f}kWh\n"
        debug_msg += f"{_('performance_factor')}: {perf_data.get('angle_factor', 1.0):.2f}\n"
        
        # Add obstacle info
        if hasattr(self.roof, 'obstacles') and self.roof.obstacles:
            obstacle_count = len(self.roof.obstacles)
            debug_msg += f"\n{_('obstacles_on_roof')}: {obstacle_count}"
            
            if total_skipped > 0:
                debug_msg += f"\n{_('panels_skipped')}: {total_skipped}"

            if 'chimney_factor' in perf_data and perf_data['chimney_factor'] < 1.0:
                chimney_impact = (1.0 - perf_data['chimney_factor']) * 100
                debug_msg += f"\n{_('chimney_impact')}: {chimney_impact:.1f}%"
        
        return debug_msg
    
    # Common interface methods
    def create_panel_mesh(self, center, width_dir, length_dir, normal):
        """Create a single panel mesh at specified location"""
        panel_width_m = self.panel_width * self.mm_to_m
        panel_length_m = self.panel_length * self.mm_to_m
        
        panel = pv.Plane(
            center=[0, 0, 0],
            direction=[0, 0, 1],
            i_size=panel_width_m,
            j_size=panel_length_m
        )
        
        panel.texture_coordinates = np.array([
            [0, 0], [1, 0], [1, 1], [0, 1]
        ])
        
        # Create transformation matrix
        transform = np.eye(4)
        transform[:3, 0] = width_dir / np.linalg.norm(width_dir)
        transform[:3, 1] = length_dir / np.linalg.norm(length_dir)
        transform[:3, 2] = normal / np.linalg.norm(normal)
        transform[:3, 3] = center
        
        panel.transform(transform)
        return panel
    
    def add_mesh_with_texture(self, mesh):
        """Add mesh to scene with texture or fallback color"""
        try:
            if self.panel_texture is not None:
                actor = self.plotter.add_mesh(
                    mesh,
                    texture=self.panel_texture,
                    show_edges=True,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.1
                )
            else:
                actor = self.plotter.add_mesh(
                    mesh,
                    color="#1E3F66",
                    show_edges=True,
                    ambient=0.2,
                    diffuse=0.8,
                    specular=0.1
                )
            
            self.panel_actors.append(actor)
            return actor
            
        except Exception as e:
            print(f"Error adding mesh: {e}")
            return None
    
    def check_obstacle_intersection(self, panel_center, panel_width, panel_length, 
                                  orientation_vectors, obstacle):
        """Check if panel intersects with obstacle"""
        return ObstacleDetector.check_panel_obstacle_intersection(
            panel_center, panel_width, panel_length, orientation_vectors, obstacle
        )
    
    def calculate_performance(self, **kwargs):
        """Calculate performance data"""
        total_panels = sum(self.panels_count_by_side.values())
        
        return PerformanceCalculator.calculate_performance_data(
            panel_count=total_panels,
            panel_power=self.panel_power,
            roof_obj=self.roof,
            active_sides=list(self.active_sides) if hasattr(self, 'active_sides') else None,
            **kwargs
        )
    
    def clear_panels(self):
        """Clear all panels and reset tracking"""
        # Remove all actors
        for actor_list in [self.panel_actors, self.boundary_actors, self.wireframe_actors]:
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
        for side in self.panels_count_by_side:
            self.panels_count_by_side[side] = 0
            self.panels_skipped_by_side[side] = 0
        
        if hasattr(self, 'active_sides'):
            self.active_sides.clear()
        
        self.current_side = None
        self.plotter.update()
    
    def update_panel_config(self, config):
        """Update panel configuration"""
        if not config:
            return True
        
        try:
            # Update parameters
            param_mapping = {
                'panel_width': 'panel_width',
                'panel_length': 'panel_length', 
                'panel_gap': 'panel_gap',
                'panel_power': 'panel_power',
                'edge_offset': 'edge_offset',
                'panel_offset': 'panel_offset',
                'horizontal_edge_offset': 'horizontal_edge_offset',
                'vertical_edge_offset': 'vertical_edge_offset'
            }
            
            for config_key, attr_name in param_mapping.items():
                if config_key in config:
                    setattr(self, attr_name, float(config[config_key]))
            
            if 'panel_model' in config:
                self.panel_model = config['panel_model']
            
            return True
            
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def update_text(self, message):
        """Clean view — no status text overlay"""
        try:
            if self.text_actor:
                self.plotter.remove_actor(self.text_actor)
                self.text_actor = None
        except Exception as e:
            print(f"Error updating text: {e}")
    
    # Abstract methods
    def add_panels(self, side):
        """Add panels to specified side - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement add_panels method")
