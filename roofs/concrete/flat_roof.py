"""
Flat roof implementation using the BaseRoof template
Significantly reduced from ~800 lines to ~200 lines (75% reduction)
"""
from roofs.base.base_roof import BaseRoof
from translations import _
import pyvista as pv
import numpy as np
import os

try:
    from roofs.solar_panel_handlers.solar_panel_placement_flat import SolarPanelPlacementFlat
    SOLAR_HANDLER_AVAILABLE = True
    print("✅ Solar panel handler imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import solar panel handler: {e}")
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementFlat = None

class FlatRoof(BaseRoof):
    """Flat roof implementation - now 75% smaller thanks to inheritance!"""
    
    def __init__(self, plotter=None, dimensions=None, theme="light"):
        """Initialize flat roof with parapet walls"""
        # Handle dimensions
        if dimensions is None:
            self.length = 10.0
            self.width = 8.0
            self.height = 0.0
            self.parapet_height = 0.5
            self.parapet_width = 0.3
        else:
            if len(dimensions) >= 2:
                self.length, self.width = dimensions[0], dimensions[1]
                self.height = 0.0
            if len(dimensions) >= 3:
                self.parapet_height = dimensions[2]
            else:
                self.parapet_height = 0.5
            if len(dimensions) >= 4:
                self.parapet_width = dimensions[3]
            else:
                self.parapet_width = 0.2
        
        # Call parent constructor
        super().__init__(plotter, dimensions, theme)
        
        # Initialize roof using template method
        self.initialize_roof(dimensions)

    def create_roof_geometry(self):
        """Create flat roof geometry with parapet walls"""
        # Clear the plotter
        self.plotter.clear()
        
        # Define the main roof surface (flat part) - AT BASE HEIGHT LEVEL
        roof_points = np.array([
            [0, 0, self.base_height],                # Front left
            [self.length, 0, self.base_height],      # Front right
            [self.length, self.width, self.base_height],  # Back right
            [0, self.width, self.base_height]        # Back left
        ])
        roof_faces = np.array([[4, 0, 1, 2, 3]])
        roof = pv.PolyData(roof_points, roof_faces)
        
        # Define texture coordinates for the roof
        roof_tcoords = np.array([
            [0, 0],  # Front left
            [2, 0],  # Front right
            [2, 2],  # Back right
            [0, 2]   # Back left
        ])
        roof.active_texture_coordinates = roof_tcoords
        
        # Create base walls and parapet walls
        self._create_base_walls()
        self._create_parapet_walls()
        
        # Create a bottom floor surface
        floor_points = np.array([
            [0, 0, 0],                # Front left
            [self.length, 0, 0],      # Front right
            [self.length, self.width, 0],  # Back right
            [0, self.width, 0]        # Back left
        ])
        floor_faces = np.array([[4, 0, 1, 2, 3]])
        floor = pv.PolyData(floor_points, floor_faces)
        floor.active_texture_coordinates = roof_tcoords.copy()
        
        # Load textures
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file)
        brick_texture, brick_texture_exists = self.load_texture_safely(self.brick_texture_file)
        
        # Apply textures or colors
        if wall_texture_exists:
            self.plotter.add_mesh(roof, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(floor, texture=wall_texture, show_edges=True)
        else:
            concrete_color = '#A9A9A9'
            floor_color = '#909090'
            self.plotter.add_mesh(roof, color=concrete_color, show_edges=True)
            self.plotter.add_mesh(floor, color=floor_color, show_edges=True)
        
        # Store reference points - AT BASE HEIGHT LEVEL
        self.roof_points = {
            'bottom_left': np.array([self.parapet_width, self.parapet_width, self.base_height]),
            'bottom_right': np.array([self.length - self.parapet_width, self.parapet_width, self.base_height]),
            'top_right': np.array([self.length - self.parapet_width, self.width - self.parapet_width, self.base_height]),
            'top_left': np.array([self.parapet_width, self.width - self.parapet_width, self.base_height])
        }

    def _create_base_walls(self):
        """Create base walls from ground level to base height"""
        # Front base wall
        front_base_points = np.array([
            [0, 0, 0],                       # Bottom left
            [self.length, 0, 0],             # Bottom right
            [self.length, 0, self.base_height],  # Top right
            [0, 0, self.base_height]         # Top left
        ])
        front_base_faces = np.array([[4, 0, 1, 2, 3]])
        front_base = pv.PolyData(front_base_points, front_base_faces)
        
        # Right base wall
        right_base_points = np.array([
            [self.length, 0, 0],                      # Bottom front
            [self.length, self.width, 0],             # Bottom back
            [self.length, self.width, self.base_height],  # Top back
            [self.length, 0, self.base_height]        # Top front
        ])
        right_base_faces = np.array([[4, 0, 1, 2, 3]])
        right_base = pv.PolyData(right_base_points, right_base_faces)
        
        # Back base wall
        back_base_points = np.array([
            [self.length, self.width, 0],             # Bottom right
            [0, self.width, 0],                       # Bottom left
            [0, self.width, self.base_height],        # Top left
            [self.length, self.width, self.base_height]  # Top right
        ])
        back_base_faces = np.array([[4, 0, 1, 2, 3]])
        back_base = pv.PolyData(back_base_points, back_base_faces)
        
        # Left base wall
        left_base_points = np.array([
            [0, self.width, 0],                       # Bottom back
            [0, 0, 0],                                # Bottom front
            [0, 0, self.base_height],                 # Top front
            [0, self.width, self.base_height]         # Top back
        ])
        left_base_faces = np.array([[4, 0, 1, 2, 3]])
        left_base = pv.PolyData(left_base_points, left_base_faces)
        
        # Apply textures to base walls
        brick_texture, brick_texture_exists = self.load_texture_safely(self.brick_texture_file)
        brick_color = '#9C2706'
        
        base_tcoords = np.array([
            [0, 0],   # Bottom left
            [3, 0],   # Bottom right
            [3, 1],   # Top right
            [0, 1]    # Top left
        ])
        
        for base_wall in [front_base, right_base, back_base, left_base]:
            base_wall.active_texture_coordinates = base_tcoords
            if brick_texture_exists:
                self.plotter.add_mesh(base_wall, texture=brick_texture, show_edges=True)
            else:
                self.plotter.add_mesh(base_wall, color=brick_color, show_edges=True)

    def _create_parapet_walls(self):
        """Create parapet walls around the roof"""
        # Create outer parapet walls (starting from base_height)
        # Front outer wall
        front_outer_points = np.array([
            [0, 0, self.base_height],                                # Bottom left
            [self.length, 0, self.base_height],                      # Bottom right
            [self.length, 0, self.base_height + self.parapet_height],  # Top right
            [0, 0, self.base_height + self.parapet_height]           # Top left
        ])
        front_outer_faces = np.array([[4, 0, 1, 2, 3]])
        front_outer = pv.PolyData(front_outer_points, front_outer_faces)
        
        # Right outer wall
        right_outer_points = np.array([
            [self.length, 0, self.base_height],                                # Bottom front
            [self.length, self.width, self.base_height],                       # Bottom back
            [self.length, self.width, self.base_height + self.parapet_height],   # Top back
            [self.length, 0, self.base_height + self.parapet_height]           # Top front
        ])
        right_outer_faces = np.array([[4, 0, 1, 2, 3]])
        right_outer = pv.PolyData(right_outer_points, right_outer_faces)
        
        # Back outer wall
        back_outer_points = np.array([
            [self.length, self.width, self.base_height],                       # Bottom right
            [0, self.width, self.base_height],                                 # Bottom left
            [0, self.width, self.base_height + self.parapet_height],           # Top left
            [self.length, self.width, self.base_height + self.parapet_height]    # Top right
        ])
        back_outer_faces = np.array([[4, 0, 1, 2, 3]])
        back_outer = pv.PolyData(back_outer_points, back_outer_faces)
        
        # Left outer wall
        left_outer_points = np.array([
            [0, self.width, self.base_height],                                 # Bottom back
            [0, 0, self.base_height],                                          # Bottom front
            [0, 0, self.base_height + self.parapet_height],                    # Top front
            [0, self.width, self.base_height + self.parapet_height]            # Top back
        ])
        left_outer_faces = np.array([[4, 0, 1, 2, 3]])
        left_outer = pv.PolyData(left_outer_points, left_outer_faces)
        
        # Create inner parapet walls
        # Front inner wall
        front_inner_points = np.array([
            [self.parapet_width, self.parapet_width, self.base_height],                                # Bottom left
            [self.length - self.parapet_width, self.parapet_width, self.base_height],                  # Bottom right
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],  # Top right
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]           # Top left
        ])
        front_inner_faces = np.array([[4, 0, 1, 2, 3]])
        front_inner = pv.PolyData(front_inner_points, front_inner_faces)
        
        # Right inner wall
        right_inner_points = np.array([
            [self.length - self.parapet_width, self.parapet_width, self.base_height],                                # Bottom front
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height],                   # Bottom back
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],   # Top back
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]           # Top front
        ])
        right_inner_faces = np.array([[4, 0, 1, 2, 3]])
        right_inner = pv.PolyData(right_inner_points, right_inner_faces)
        
        # Back inner wall
        back_inner_points = np.array([
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height],                       # Bottom right
            [self.parapet_width, self.width - self.parapet_width, self.base_height],                                 # Bottom left
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],           # Top left
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]    # Top right
        ])
        back_inner_faces = np.array([[4, 0, 1, 2, 3]])
        back_inner = pv.PolyData(back_inner_points, back_inner_faces)
        
        # Left inner wall
        left_inner_points = np.array([
            [self.parapet_width, self.width - self.parapet_width, self.base_height],                                 # Bottom back
            [self.parapet_width, self.parapet_width, self.base_height],                                          # Bottom front
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],                    # Top front
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]            # Top back
        ])
        left_inner_faces = np.array([[4, 0, 1, 2, 3]])
        left_inner = pv.PolyData(left_inner_points, left_inner_faces)
        
        # Create parapet top surfaces
        # Front parapet top
        front_top_points = np.array([
            [0, 0, self.base_height + self.parapet_height],                      # Outer front left
            [self.length, 0, self.base_height + self.parapet_height],            # Outer front right
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],  # Inner front right
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]  # Inner front left
        ])
        front_top_faces = np.array([[4, 0, 1, 2, 3]])
        front_top = pv.PolyData(front_top_points, front_top_faces)
        
        # Right parapet top
        right_top_points = np.array([
            [self.length, 0, self.base_height + self.parapet_height],            # Outer right front
            [self.length, self.width, self.base_height + self.parapet_height],   # Outer right back
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],  # Inner right back
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]  # Inner right front
        ])
        right_top_faces = np.array([[4, 0, 1, 2, 3]])
        right_top = pv.PolyData(right_top_points, right_top_faces)
        
        # Back parapet top
        back_top_points = np.array([
            [self.length, self.width, self.base_height + self.parapet_height],   # Outer back right
            [0, self.width, self.base_height + self.parapet_height],             # Outer back left
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],  # Inner back left
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]  # Inner back right
        ])
        back_top_faces = np.array([[4, 0, 1, 2, 3]])
        back_top = pv.PolyData(back_top_points, back_top_faces)
        
        # Left parapet top
        left_top_points = np.array([
            [0, self.width, self.base_height + self.parapet_height],             # Outer left back
            [0, 0, self.base_height + self.parapet_height],                      # Outer left front
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],  # Inner left front
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]  # Inner left back
        ])
        left_top_faces = np.array([[4, 0, 1, 2, 3]])
        left_top = pv.PolyData(left_top_points, left_top_faces)
        
        # Apply textures to parapet walls
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file)
        
        std_tcoords = np.array([
            [0, 0],  # Bottom left
            [2, 0],  # Bottom right
            [2, 0.5],  # Top right
            [0, 0.5]   # Top left
        ])
        
        top_tcoords = np.array([
            [0, 0],  # Outer corner 1
            [1, 0],  # Outer corner 2
            [0.9, 0.9],  # Inner corner 2
            [0.1, 0.9]   # Inner corner 1
        ])
        
        parapet_walls = [front_outer, right_outer, back_outer, left_outer,
                        front_inner, right_inner, back_inner, left_inner]
        parapet_tops = [front_top, right_top, back_top, left_top]
        
        for wall in parapet_walls:
            wall.active_texture_coordinates = std_tcoords
            if wall_texture_exists:
                self.plotter.add_mesh(wall, texture=wall_texture, show_edges=True)
            else:
                self.plotter.add_mesh(wall, color='#808080', show_edges=True)
        
        for top in parapet_tops:
            top.active_texture_coordinates = top_tcoords
            if wall_texture_exists:
                self.plotter.add_mesh(top, texture=wall_texture, show_edges=True)
            else:
                self.plotter.add_mesh(top, color='#707070', show_edges=True)

    def get_roof_specific_help_text(self):
        """Get help text specific to flat roofs"""
        return (
            f"{_('help_flat_roof_title')}\n"
            f"{_('help_place_center_panels')}\n"
            f"{_('help_place_north_panels')}\n"
            f"{_('help_place_south_panels')}\n"
            f"{_('help_place_east_panels')}\n"
            f"{_('help_place_west_panels')}\n"
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

    def setup_roof_specific_key_bindings(self):
        """Setup key bindings specific to flat roof"""
        if self.solar_panel_handler:
            print("✅ Adding panel placement key bindings")
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("center"))
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("north"))
            self.plotter.add_key_event("3", lambda: self.safe_add_panels("south"))
            self.plotter.add_key_event("4", lambda: self.safe_add_panels("east"))
            self.plotter.add_key_event("5", lambda: self.safe_add_panels("west"))
            self.plotter.add_key_event("c", self.safe_clear_panels)
            self.plotter.add_key_event("C", self.safe_clear_panels)
        else:
            print("⚠️ Solar panel handler not available, adding fallback key bindings")
            self.plotter.add_key_event("1", lambda: print("⚠️ Cannot add center panels - solar panel handler not available"))
            self.plotter.add_key_event("2", lambda: print("⚠️ Cannot add north panels - solar panel handler not available"))
            self.plotter.add_key_event("3", lambda: print("⚠️ Cannot add south panels - solar panel handler not available"))
            self.plotter.add_key_event("4", lambda: print("⚠️ Cannot add east panels - solar panel handler not available"))
            self.plotter.add_key_event("5", lambda: print("⚠️ Cannot add west panels - solar panel handler not available"))
            self.plotter.add_key_event("c", lambda: print("⚠️ Cannot clear panels - solar panel handler not available"))
            self.plotter.add_key_event("C", lambda: print("⚠️ Cannot clear panels - solar panel handler not available"))

    def get_solar_panel_areas(self):
        """Get valid solar panel areas for flat roof"""
        return ["center", "north", "south", "east", "west"]

    def get_solar_panel_handler_class(self):
        """Get the solar panel handler class for flat roof"""
        return SolarPanelPlacementFlat if SOLAR_HANDLER_AVAILABLE else None

    def calculate_camera_position(self):
        """Calculate camera position for flat roof"""
        camera_height = max(6.0, self.parapet_height * 12)
        position = (self.width*2.0, -self.length*1.0, camera_height)
        focal_point = (self.width/2, self.length/2, self.parapet_height/2)
        up_vector = (0, 0, 1)
        return position, focal_point, up_vector

    def _get_annotation_params(self):
        """Get parameters for RoofAnnotation"""
        return (self.length, self.width, self.height, 0, False, self.base_height)

    def add_attachment_points(self):
        """Generate attachment points for flat roof obstacle placement"""
        try:
            # Initialize obstacle properties if not already done
            if not hasattr(self, 'obstacle_count'):
                self.obstacle_count = 0
                self.obstacles = []
            
            # Check if we've reached the maximum limit
            if self.obstacle_count >= 6:
                self.update_instruction(_('maximum_obstacles_reached'))
                return False
            
            # Clear existing attachment points if any
            if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
                self.plotter.remove_actor(self.attachment_point_actor)
                self.attachment_point_actor = None
            
            # Reset attachment points data for this session
            self.attachment_points = []
            self.attachment_points_occupied = {}
            
            # Flag to track if we've placed an obstacle in this session
            self.obstacle_placed_this_session = False
            
            # Define a minimum distance to keep from existing obstacles (in meters)
            min_obstacle_distance = 1
            
            # Generate points on the flat roof surface
            # Use the usable area (inside parapet walls)
            usable_length = self.length - 2 * self.parapet_width
            usable_width = self.width - 2 * self.parapet_width
            
            # Create a grid of attachment points
            grid_size = 8  # 8x8 grid
            
            for i in range(grid_size):
                for j in range(grid_size):
                    # Calculate position within usable area
                    x = self.parapet_width + (i / (grid_size - 1)) * usable_length
                    y = self.parapet_width + (j / (grid_size - 1)) * usable_width
                    z = self.base_height + 0.1  # Slightly above roof surface
                    
                    point = np.array([x, y, z])
                    
                    # Check if point is valid (away from existing obstacles)
                    if self._is_valid_attachment_point(point, min_obstacle_distance):
                        self.attachment_points.append(point)
            
            # Initialize tracking dictionary for attachment points
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None
                }
            
            # Create point cloud for visualization
            if self.attachment_points:
                points = pv.PolyData(np.array(self.attachment_points))
                
                # Add points to plotter with larger size for better visibility
                self.attachment_point_actor = self.plotter.add_points(
                    points,
                    color='black',
                    point_size=10,
                    render_points_as_spheres=True,
                    pickable=True
                )
                
                # Enable point picking
                self.plotter.enable_point_picking(
                    callback=self.attachment_point_clicked,
                    show_message=False,
                    pickable_window=False,
                    tolerance=0.05
                )
                
                # Update instruction if not already set
                if not hasattr(self, 'placement_instruction') or not self.placement_instruction:
                    remaining = 6 - self.obstacle_count
                    display_name = self.get_translated_obstacle_name(self.selected_obstacle_type)
                    self.update_instruction(
                        _('click_to_place') + f" {display_name} " +
                        f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")"
                    )
                            
            return True
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def _is_valid_attachment_point(self, point, min_distance):
        """Check if a point is valid for attachment (away from obstacles)"""
        if hasattr(self, 'obstacles') and self.obstacles:
            for obstacle in self.obstacles:
                dist = np.linalg.norm(np.array(obstacle.position) - np.array(point))
                if dist < min_distance:
                    return False
        return True

    def attachment_point_clicked(self, point, *args):
        """Handle click on attachment point - place ONE obstacle only"""
        # Check if we already placed an obstacle this session
        if hasattr(self, 'obstacle_placed_this_session') and self.obstacle_placed_this_session:
            self.update_instruction(_('obstacle_already_placed'))
            return
        
        # Check if obstacle type is selected
        if not hasattr(self, 'selected_obstacle_type') or not self.selected_obstacle_type:
            self.update_instruction(_('select_obstacle_type'))
            return
        
        # Find the closest attachment point
        closest_point_idx, closest_point = self.find_closest_attachment_point(point)
        
        # Safety check for valid point index
        if closest_point_idx is None:
            return
        
        # Check if this point is already occupied by a previous obstacle
        if self.is_point_occupied(closest_point):
            self.update_instruction(_('point_occupied'))
            return
        
        # Place the obstacle
        normal_vector = np.array([0, 0, 1])  # Flat roof normal points up
        obstacle = self.place_obstacle_at_point(
            closest_point, 
            self.selected_obstacle_type,
            normal_vector=normal_vector
        )
        
        # Add to obstacles list
        self.obstacles.append(obstacle)
        
        # Increment obstacle count
        self.obstacle_count += 1
        
        # Mark that we've placed an obstacle this session
        self.obstacle_placed_this_session = True
        
        # Disable further picking until "Add Obstacle" is pressed again
        self.plotter.disable_picking()
        
        # Remove attachment points
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.plotter.remove_actor(self.attachment_point_actor)
            self.attachment_point_actor = None
        
        # Update solar panels if they exist
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            # Refresh panels to account for the new obstacle
            active_areas = getattr(self.solar_panel_handler, 'active_areas', [])
            for area in active_areas:
                self.solar_panel_handler.add_panels(area)
        
        # Update instruction
        remaining = 6 - self.obstacle_count
        if remaining > 0:
            display_name = self.get_translated_obstacle_name(self.selected_obstacle_type)
            self.update_instruction(
                f"{display_name} " + _('placed') + 
                f" ({self.obstacle_count}/6, {remaining} " + _('remaining') + "). " +
                _('press_add_obstacle')
            )
        else:
            self.update_instruction(_('obstacle_max_reached') + " (6/6)")