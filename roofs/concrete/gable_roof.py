"""
Gable roof implementation using the BaseRoof template
Reduced from ~900 lines to ~250 lines (72% reduction)
"""
from roofs.base.base_roof import BaseRoof
from translations import _
import pyvista as pv
import numpy as np
import tkinter as tk
from tkinter import messagebox

try:
    from roofs.solar_panel_handlers.solar_panel_placement_gable import SolarPanelPlacementGable
    SOLAR_HANDLER_AVAILABLE = True
    print("✅ Solar panel handler imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import solar panel handler: {e}")
    SOLAR_HANDLER_AVAILABLE = False
    SolarPanelPlacementGable = None

class GableRoof(BaseRoof):
    """Gable roof implementation - now 72% smaller thanks to inheritance!"""
    
    def __init__(self, plotter=None, dimensions=(10.0, 7.0, 4.0), theme="light"):
        # If dimensions are provided, use them; otherwise, show dialog to get them
        if dimensions is None:
            dimensions = self.show_input_dialog()
            if dimensions is None: 
                return
                
        # Unpack dimensions (all in meters)
        self.length, self.width, self.height = dimensions
        
        # Calculate slope properties
        self.slope_width = np.sqrt((self.width / 2) ** 2 + self.height ** 2)
        self.slope_angle = np.arctan(self.height / (self.width / 2))  # Angle in radians
        
        # Define roof colors (fallback if texture not available)
        self.roof_color = "#610B0B"  # Dark red color for the roof
        self.wall_color = "#404040"  # Dark gray color for the walls
        
        # Initialize texture paths
        self.roof_texture_file = "PVmizer/textures/rooftile.jpg"
        self.wall_texture_file = "PVmizer/textures/woodwall.jpg"
        self.concrete_texture_file = "PVmizer/textures/wall.jpg"
        
        # Call parent constructor
        super().__init__(plotter, dimensions, theme)
        
        # Initialize roof using template method
        self.initialize_roof(dimensions)

    def show_input_dialog(self):
        """Show a dialog to get roof dimensions from the user (in meters)"""
        # Create a root window but hide it
        root = tk.Tk()
        root.withdraw()
        
        # Create a custom dialog window
        dialog = tk.Toplevel(root)
        dialog.title('Gable Roof Dimensions')
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (root.winfo_screenwidth()/2 - 150, 
                                    root.winfo_screenheight()/2 - 100))
        
        # Add input fields
        tk.Label(dialog, text='Enter roof dimensions:').grid(row=0, column=0, columnspan=2, pady=10)
        
        tk.Label(dialog, text='Length (m):').grid(row=1, column=0, sticky="e", padx=5, pady=5)
        length_var = tk.StringVar(value="12")
        length_entry = tk.Entry(dialog, textvariable=length_var, width=10)
        length_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(dialog, text="Width (m):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        width_var = tk.StringVar(value="8")
        width_entry = tk.Entry(dialog, textvariable=width_var, width=10)
        width_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(dialog, text="Height (m):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        height_var = tk.StringVar(value="4")
        height_entry = tk.Entry(dialog, textvariable=height_var, width=10)
        height_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Variables to store the result
        result = [None]
        
        def on_ok():
            try:
                length = float(length_var.get())
                width = float(width_var.get())
                height = float(height_var.get())
                
                # Validate inputs
                if length <= 0 or width <= 0 or height <= 0:
                    messagebox.showerror("Error", "All dimensions must be positive numbers")
                    return
                
                result[0] = (length, width, height)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for all dimensions")
        
        def on_cancel():
            dialog.destroy()
        
        # Add buttons
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ok_button = tk.Button(button_frame, text="OK", command=on_ok, width=10)
        ok_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Set focus to the first entry
        length_entry.focus_set()
        
        # Make dialog modal
        dialog.transient(root)
        dialog.grab_set()
        root.wait_window(dialog)
        
        # Destroy the hidden root window
        root.destroy()
        
        return result[0]

    def create_roof_geometry(self):
        """Creates a gable roof with concrete base and wooden walls"""
        # Define key points for the roof
        ridge_front = np.array([self.width/2, 0, self.height])
        ridge_back = np.array([self.width/2, self.length, self.height])
        
        # Eave points (top of building walls)
        eave_left_front = np.array([0, 0, 0])
        eave_right_front = np.array([self.width, 0, 0])
        eave_left_back = np.array([0, self.length, 0])
        eave_right_back = np.array([self.width, self.length, 0])
        
        # Define building height
        building_height = 1.0  # 1 meter building height
        
        # Define base points (ground level)
        base_left_front = np.array([0, 0, -building_height])
        base_right_front = np.array([self.width, 0, -building_height])
        base_left_back = np.array([0, self.length, -building_height])
        base_right_back = np.array([self.width, self.length, -building_height])
        
        # Store reference points in dictionary
        self.roof_points = {
            'ridge_front': ridge_front,
            'ridge_back': ridge_back,
            'eave_left_front': eave_left_front,
            'eave_right_front': eave_right_front,
            'eave_left_back': eave_left_back,
            'eave_right_back': eave_right_back,
            'base_left_front': base_left_front,
            'base_right_front': base_right_front,
            'base_left_back': base_left_back,
            'base_right_back': base_right_back
        }
        
        # Create roof slopes
        self._create_roof_slopes()
        
        # Create walls and base
        self._create_walls_and_base(building_height)

    def _create_roof_slopes(self):
        """Create the two sloped surfaces of the gable roof"""
        # Left slope
        left_slope_points = np.array([
            self.roof_points['eave_left_front'], 
            self.roof_points['eave_left_back'], 
            self.roof_points['ridge_back'], 
            self.roof_points['ridge_front']
        ])
        left_faces = np.array([[4, 0, 1, 2, 3]])
        self.left_slope = pv.PolyData(left_slope_points, left_faces)
        
        # Right slope
        right_slope_points = np.array([
            self.roof_points['eave_right_front'], 
            self.roof_points['eave_right_back'], 
            self.roof_points['ridge_back'], 
            self.roof_points['ridge_front']
        ])
        right_faces = np.array([[4, 0, 1, 2, 3]])
        self.right_slope = pv.PolyData(right_slope_points, right_faces)
        
        # Apply textures
        self._apply_roof_textures()

    def _create_walls_and_base(self, building_height):
        """Create gable walls and concrete base"""
        # Create front gable (triangular part at the front)
        front_gable_points = np.array([
            self.roof_points['eave_left_front'], 
            self.roof_points['eave_right_front'], 
            self.roof_points['ridge_front']
        ])
        front_gable_faces = np.array([[3, 0, 1, 2]])
        front_gable = pv.PolyData(front_gable_points, front_gable_faces)
        
        # Create back gable (triangular part at the back)
        back_gable_points = np.array([
            self.roof_points['eave_left_back'], 
            self.roof_points['eave_right_back'], 
            self.roof_points['ridge_back']
        ])
        back_gable_faces = np.array([[3, 0, 1, 2]])
        back_gable = pv.PolyData(back_gable_points, back_gable_faces)
        
        # Create base components
        self._create_base_components(building_height)
        
        # Apply textures to walls
        self._apply_wall_textures(front_gable, back_gable)

    def _apply_roof_textures(self):
        """Apply textures to roof slopes"""
        # Load roof texture
        roof_texture, roof_texture_exists = self.load_texture_safely(self.roof_texture_file, self.roof_color)
        
        # Set texture coordinates
        left_tcoords = np.array([[0, 0], [3, 0], [3, 1], [0, 1]])
        right_tcoords = np.array([[0, 0], [3, 0], [3, 1], [0, 1]])
        
        self.left_slope.active_texture_coordinates = left_tcoords
        self.right_slope.active_texture_coordinates = right_tcoords
        
        # Apply textures or colors
        if roof_texture_exists:
            self.plotter.add_mesh(self.left_slope, texture=roof_texture, show_edges=True)
            self.plotter.add_mesh(self.right_slope, texture=roof_texture, show_edges=True)
        else:
            self.plotter.add_mesh(self.left_slope, color=roof_texture, show_edges=True)
            self.plotter.add_mesh(self.right_slope, color=roof_texture, show_edges=True)

    def _apply_wall_textures(self, front_gable, back_gable):
        """Apply textures to gable walls"""
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file, self.wall_color)
        
        # Set texture coordinates for gable triangles
        front_gable_tcoords = np.array([[0, 0], [1, 0], [0.5, 1]])
        back_gable_tcoords = np.array([[0, 0], [1, 0], [0.5, 1]])
        
        front_gable.active_texture_coordinates = front_gable_tcoords
        back_gable.active_texture_coordinates = back_gable_tcoords
        
        if wall_texture_exists:
            self.plotter.add_mesh(front_gable, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_gable, texture=wall_texture, show_edges=True)
        else:
            self.plotter.add_mesh(front_gable, color=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_gable, color=wall_texture, show_edges=True)

    def _create_base_components(self, building_height):
        """Create concrete base walls and floor"""
        # Floor (foundation)
        floor_points = np.array([
            self.roof_points['base_left_front'], 
            self.roof_points['base_right_front'], 
            self.roof_points['base_right_back'], 
            self.roof_points['base_left_back']
        ])
        floor_faces = np.array([[4, 0, 1, 2, 3]])
        floor = pv.PolyData(floor_points, floor_faces)
        
        # Front concrete base wall
        front_base_points = np.array([
            self.roof_points['base_left_front'], 
            self.roof_points['base_right_front'], 
            self.roof_points['base_right_front'] + np.array([0, 0, building_height]), 
            self.roof_points['base_left_front'] + np.array([0, 0, building_height])
        ])
        front_base_faces = np.array([[4, 0, 1, 2, 3]])
        front_base = pv.PolyData(front_base_points, front_base_faces)
        
        # Back concrete base wall
        back_base_points = np.array([
            self.roof_points['base_left_back'], 
            self.roof_points['base_right_back'], 
            self.roof_points['base_right_back'] + np.array([0, 0, building_height]), 
            self.roof_points['base_left_back'] + np.array([0, 0, building_height])
        ])
        back_base_faces = np.array([[4, 0, 1, 2, 3]])
        back_base = pv.PolyData(back_base_points, back_base_faces)
        
        # Left concrete base wall
        left_base_points = np.array([
            self.roof_points['base_left_front'], 
            self.roof_points['base_left_back'], 
            self.roof_points['base_left_back'] + np.array([0, 0, building_height]), 
            self.roof_points['base_left_front'] + np.array([0, 0, building_height])
        ])
        left_base_faces = np.array([[4, 0, 1, 2, 3]])
        left_base = pv.PolyData(left_base_points, left_base_faces)
        
        # Right concrete base wall
        right_base_points = np.array([
            self.roof_points['base_right_front'], 
            self.roof_points['base_right_back'], 
            self.roof_points['base_right_back'] + np.array([0, 0, building_height]), 
            self.roof_points['base_right_front'] + np.array([0, 0, building_height])
        ])
        right_base_faces = np.array([[4, 0, 1, 2, 3]])
        right_base = pv.PolyData(right_base_points, right_base_faces)
        
        # Apply concrete texture
        concrete_texture, concrete_texture_exists = self.load_texture_safely(self.concrete_texture_file, "#AAAAAA")
        
        concrete_tcoords = np.array([
            [0, 0], [3, 0], [3, 1], [0, 1]
        ])
        
        floor_tcoords = np.array([
            [0, 0], [3, 0], [3, 3], [0, 3]
        ])
        
        # Apply texture coordinates
        floor.active_texture_coordinates = floor_tcoords
        front_base.active_texture_coordinates = concrete_tcoords
        back_base.active_texture_coordinates = concrete_tcoords
        left_base.active_texture_coordinates = concrete_tcoords
        right_base.active_texture_coordinates = concrete_tcoords
        
        base_components = [floor, front_base, back_base, left_base, right_base]
        
        for component in base_components:
            if concrete_texture_exists:
                self.plotter.add_mesh(component, texture=concrete_texture, show_edges=True)
            else:
                self.plotter.add_mesh(component, color=concrete_texture, show_edges=True)

    def get_roof_specific_help_text(self):
        """Get help text specific to gable roofs"""
        return (
            f"{_('help_gable_roof_title')}\n"
            f"{_('help_place_left_face')}\n"
            f"{_('help_place_right_face')}\n"
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
        """Setup key bindings specific to gable roof"""
        if self.solar_panel_handler:
            print("✅ Adding panel placement key bindings")
            self.plotter.add_key_event("1", lambda: self.safe_add_panels("left"))
            self.plotter.add_key_event("2", lambda: self.safe_add_panels("right"))
            self.plotter.add_key_event("c", self.safe_clear_panels)
            self.plotter.add_key_event("C", self.safe_clear_panels)
            self.plotter.add_key_event("Left", lambda: self.safe_add_panels("left"))
            self.plotter.add_key_event("Right", lambda: self.safe_add_panels("right"))
        else:
            print("⚠️ Solar panel handler not available, adding fallback key bindings")
            self.plotter.add_key_event("1", lambda: print("⚠️ Cannot add left panels - solar panel handler not available"))
            self.plotter.add_key_event("2", lambda: print("⚠️ Cannot add right panels - solar panel handler not available"))
            self.plotter.add_key_event("c", lambda: print("⚠️ Cannot clear panels - solar panel handler not available"))
            self.plotter.add_key_event("C", lambda: print("⚠️ Cannot clear panels - solar panel handler not available"))
            self.plotter.add_key_event("Left", lambda: print("⚠️ Cannot add left panels - solar panel handler not available"))
            self.plotter.add_key_event("Right", lambda: print("⚠️ Cannot add right panels - solar panel handler not available"))

    def get_solar_panel_areas(self):
        """Get valid solar panel areas for gable roof"""
        return ["left", "right"]

    def get_solar_panel_handler_class(self):
        """Get the solar panel handler class for gable roof"""
        return SolarPanelPlacementGable if SOLAR_HANDLER_AVAILABLE else None

    def calculate_camera_position(self):
        """Calculate camera position for gable roof"""
        position = (self.width*2.0, -self.length*1.2, self.height*2.0)
        focal_point = (self.width/2, self.length/2, self.height/2)
        up_vector = (0, 0, 1)
        return position, focal_point, up_vector

    def _get_annotation_params(self):
        """Get parameters for RoofAnnotation"""
        return (self.length, self.width, self.height, self.slope_angle)

    def add_attachment_points(self):
        """Generate attachment points for gable roof obstacle placement"""
        try:
            # Initialize obstacle properties if not already done
            if not hasattr(self, 'obstacle_count'):
                self.obstacle_count = 0
                self.obstacles = []
                
            # Initialize selected_obstacle_type if not defined
            if not hasattr(self, 'selected_obstacle_type'):
                self.selected_obstacle_type = "Chimney"
                
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
            self.face_normals = {}
            
            # Flag to track if we've placed an obstacle in this session
            self.obstacle_placed_this_session = False
            
            # Use a moderate offset for attachment points
            offset_distance = 0.15  # 15cm offset
            
            # Get roof points
            roof_points = self.roof_points
            
            # For gable roof - two faces
            left_face_points = [
                roof_points['eave_left_front'],
                roof_points['eave_left_back'],
                roof_points['ridge_back'],
                roof_points['ridge_front']
            ]
            
            right_face_points = [
                roof_points['eave_right_front'],
                roof_points['eave_right_back'],
                roof_points['ridge_back'],
                roof_points['ridge_front']
            ]
            
            # Calculate face normals
            # Left face normal
            v1_left = left_face_points[1] - left_face_points[0]
            v2_left = left_face_points[3] - left_face_points[0]
            left_normal = np.cross(v1_left, v2_left)
            left_normal = left_normal / np.linalg.norm(left_normal)
            if left_normal[2] < 0:
                left_normal = -left_normal
            
            # Right face normal
            v1_right = right_face_points[1] - right_face_points[0]
            v2_right = right_face_points[3] - right_face_points[0]
            right_normal = np.cross(v1_right, v2_right)
            right_normal = right_normal / np.linalg.norm(right_normal)
            if right_normal[2] < 0:
                right_normal = -right_normal
            
            # Generate points on left face
            face_u_steps = 6
            face_v_steps = 6
            point_index = 0
            
            for u in np.linspace(0.1, 0.9, face_u_steps):
                for v in np.linspace(0.1, 0.9, face_v_steps):
                    p1 = left_face_points[0] * (1-u) * (1-v)
                    p2 = left_face_points[1] * u * (1-v)
                    p3 = left_face_points[2] * u * v
                    p4 = left_face_points[3] * (1-u) * v
                    point = p1 + p2 + p3 + p4
                    
                    # Only add valid points
                    if self._is_valid_attachment_point(point, 1.0):
                        offset_point = point + left_normal * offset_distance
                        self.attachment_points.append(offset_point)
                        self.face_normals[point_index] = {
                            'normal': left_normal, 
                            'face': 'left', 
                            'roof_point': point
                        }
                        point_index += 1
            
            # Generate points on right face
            for u in np.linspace(0.1, 0.9, face_u_steps):
                for v in np.linspace(0.1, 0.9, face_v_steps):
                    p1 = right_face_points[0] * (1-u) * (1-v)
                    p2 = right_face_points[1] * u * (1-v)
                    p3 = right_face_points[2] * u * v
                    p4 = right_face_points[3] * (1-u) * v
                    point = p1 + p2 + p3 + p4
                    
                    # Only add valid points
                    if self._is_valid_attachment_point(point, 1.0):
                        offset_point = point + right_normal * offset_distance
                        self.attachment_points.append(offset_point)
                        self.face_normals[point_index] = {
                            'normal': right_normal, 
                            'face': 'right', 
                            'roof_point': point
                        }
                        point_index += 1
            
            # Initialize tracking dictionary for attachment points
            for i, point in enumerate(self.attachment_points):
                self.attachment_points_occupied[i] = {
                    'position': point,
                    'occupied': False,
                    'obstacle': None,
                    'normal': self.face_normals[i]['normal'] if i in self.face_normals else None,
                    'face': self.face_normals[i]['face'] if i in self.face_normals else None,
                    'roof_point': self.face_normals[i]['roof_point'] if i in self.face_normals else None
                }
            
            # Create point cloud for visualization
            if self.attachment_points:
                points = pv.PolyData(np.array(self.attachment_points))
                
                # Add points to plotter
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
                
                # Update instruction
                if not hasattr(self, 'placement_instruction') or not self.placement_instruction:
                    remaining = 6 - self.obstacle_count
                    display_name = self.get_translated_obstacle_name(self.selected_obstacle_type)
                    self.update_instruction(
                        _('click_to_place') + f" {display_name} " +
                        f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")"
                    )

            return True
        
        except Exception as e:
            print(f"Error adding attachment points: {e}")
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
        
        # Get the normal vector and roof point for this attachment point
        normal_vector = None
        roof_point = None
        face = None
        
        if closest_point_idx in self.attachment_points_occupied:
            normal_vector = self.attachment_points_occupied[closest_point_idx].get('normal')
            roof_point = self.attachment_points_occupied[closest_point_idx].get('roof_point')
            face = self.attachment_points_occupied[closest_point_idx].get('face')
        
        # Place the obstacle with orientation info
        obstacle = self.place_obstacle_at_point(
            closest_point, 
            self.selected_obstacle_type,
            normal_vector=normal_vector,
            roof_point=roof_point,
            face=face
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
            # Get current side
            if hasattr(self.solar_panel_handler, 'current_side'):
                current_side = self.solar_panel_handler.current_side
                if current_side:
                    # Refresh panels on the active side to account for the new obstacle
                    self.solar_panel_handler.add_panels(current_side)
        
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

    def calculate_normal_at_point(self, point):
        """Calculate the normal vector at a specific point on the gable roof"""
        # For gable roof, we only need to check if we're on the left or right side
        center_x = self.width / 2
        
        # Get roof angle in radians
        slope_angle = self.slope_angle
        
        # Create normal vector based on which side the point is on
        if point[0] < center_x:
            # Left side (sloping from left to right)
            normal = np.array([-np.sin(slope_angle), 0, np.cos(slope_angle)])
        else:
            # Right side (sloping from right to left)
            normal = np.array([np.sin(slope_angle), 0, np.cos(slope_angle)])
        
        # Make sure normal is normalized
        normal = normal / np.linalg.norm(normal)
        
        return normal