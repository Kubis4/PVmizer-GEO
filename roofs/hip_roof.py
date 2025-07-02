from obstacle_dialogs import RoofObstacleDialogs
from roof_obstacle import RoofObstacle
from translations import _
import pyvista as pv
import numpy as np
import os
import sys
from pathlib import Path
from roof_annotation import RoofAnnotation

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # Try to find the file
    full_path = os.path.join(base_path, relative_path)
    if os.path.exists(full_path):
        return full_path
        
    # Try alternate paths if the first one doesn't exist
    alt_paths = [
        os.path.join(os.path.dirname(sys.executable), relative_path),
        os.path.join(os.path.dirname(sys.executable), "_internal", relative_path),
        os.path.join(os.path.dirname(__file__), relative_path)
    ]
    
    for path in alt_paths:
        if os.path.exists(path):
            return path
            
    # Return the original path even if it doesn't exist
    return full_path

class HipRoof:
    def __init__(self, plotter=None, dimensions=(10.0, 8.0, 5.0), theme="light"):
        """Initialize a hip roof with the specified dimensions (in meters)."""
        # If dimensions are provided, use them; otherwise, show dialog to get them
        if dimensions is None:
            dimensions = self.show_input_dialog()
            if dimensions is None:  # User cancelled the dialog
                return
            
        self.length, self.width, self.height = dimensions
        self.theme = theme  # Store theme as instance variable
        
        # Calculate slope angle for solar panel performance calculations
        self.slope_angle = np.arctan(self.height / (self.width / 2))
        
        # Store the plotter
        self.plotter = plotter if plotter else pv.Plotter()
        
        # Set theme-appropriate background
        self.set_plotter_background()
        
        # Initialize texture paths directly - don't use Path objects
        self.roof_texture_file = "PVmizer/textures/rooftile.jpg"
        self.wall_texture_file = "PVmizer/textures/wall.jpg"
        
        # Create the roof
        self.create_hip_roof()
        
        # Initialize obstacle-related properties
        self.attachment_points = []
        self.attachment_point_actor = None
        self.obstacles = []
        self.obstacle_count = 0
        self.placement_instruction = None
        
        # Initialize solar panel handler
        try:
            from solar_panel_hip import SolarPanelPlacementHip
            self.solar_panel_handler = SolarPanelPlacementHip(self)
            
            # Add key bindings for solar panel placement
            self.add_key_bindings()
        except Exception as e:
            print(f"Error initializing solar panel handler: {e}")
            import traceback
            traceback.print_exc()
            self.solar_panel_handler = None
                
    def set_theme(self, theme):
        """Update the roof's theme and refresh visuals"""
        self.theme = theme
        self.set_plotter_background()
        
        # Update annotations if they exist
        if hasattr(self, 'annotator'):
            self.annotator.set_theme(theme)
        
    def set_plotter_background(self):
        """Set the plotter background based on current theme"""
        if hasattr(self, 'theme') and self.theme == "dark":
            self.plotter.set_background("darkgrey")
        else:
            self.plotter.set_background("lightgrey")
    
    def load_texture_safely(self, filename, default_color="#A9A9A9"):
        """Safely load a texture with fallback to color if loading fails"""
        # Extract just the filename without path
        base_filename = os.path.basename(filename)
        
        # Try multiple possible locations
        possible_paths = [
            filename,  # Original path
            resource_path(filename),  # Original with resource_path
            resource_path(f"PVmizer/textures/{base_filename}"),  # Try in PVmizer/textures
            resource_path(f"textures/{base_filename}"),  # Try in textures dir
            resource_path(f"_internal/textures/{base_filename}")  # Try in _internal/textures
        ]
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    print(f"Loading texture from: {path}")
                    texture = pv.read_texture(path)
                    return texture, True
                except Exception as e:
                    print(f"Error loading texture from {path}: {e}")
        
        # If we get here, no texture was loaded
        print(f"Could not load texture {filename}, using default color: {default_color}")
        return default_color, False
    
    def create_hip_roof(self):
        """Create the hip roof with properly mapped textures on all sides."""
        # Clear the plotter
        self.plotter.clear()
        
        # Define the corners of the roof base
        front_left = np.array([0, 0, 0])
        front_right = np.array([self.width, 0, 0])
        back_left = np.array([0, self.length, 0])
        back_right = np.array([self.width, self.length, 0])
        
        # Define the ridge points
        ridge_front = np.array([self.width/2, self.length*0.25, self.height])
        ridge_back = np.array([self.width/2, self.length*0.75, self.height])
        
        # Store all key points for later use
        self.roof_points = {
            'front_left': front_left,
            'front_right': front_right,
            'back_left': back_left,
            'back_right': back_right,
            'ridge_front': ridge_front,
            'ridge_back': ridge_back,
            'peak': ridge_front  # For compatibility with solar panel placement
        }
        
        # Roof color for fallback
        roof_color = '#8B4513'
        
        # Texture scaling factor (higher = smaller texture)
        texture_scale = 1.5
        
        # Load textures with the safe method
        roof_texture, roof_texture_exists = self.load_texture_safely(self.roof_texture_file, roof_color)
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file, "#E8DCC9")
        
        # === FRONT TRIANGULAR FACE ===
        front_points = np.array([front_left, front_right, ridge_front])
        front_faces = np.array([3, 0, 1, 2])
        front_triangle = pv.PolyData(front_points, front_faces)
        
        # Scale texture coordinates to make texture smaller
        front_tcoords = np.array([
            [0.0, 0.0],                # bottom left
            [texture_scale, 0.0],      # bottom right
            [texture_scale/2, texture_scale]  # top center
        ])
        front_triangle.active_texture_coordinates = front_tcoords
        
        if roof_texture_exists:
            self.plotter.add_mesh(front_triangle, texture=roof_texture, show_edges=False)
        else:
            self.plotter.add_mesh(front_triangle, color=roof_texture, show_edges=True)
        
        # === BACK TRIANGULAR FACE ===
        back_points = np.array([back_left, back_right, ridge_back])
        back_faces = np.array([3, 0, 1, 2])
        back_triangle = pv.PolyData(back_points, back_faces)
        
        # Scale texture coordinates to make texture smaller
        back_tcoords = np.array([
            [0.0, 0.0],                # bottom left
            [texture_scale, 0.0],      # bottom right
            [texture_scale/2, texture_scale]  # top center
        ])
        back_triangle.active_texture_coordinates = back_tcoords
        
        if roof_texture_exists:
            self.plotter.add_mesh(back_triangle, texture=roof_texture, show_edges=False)
        else:
            self.plotter.add_mesh(back_triangle, color=roof_texture, show_edges=True)
        
        # === RIGHT SIDE ===
        right_points1 = np.array([front_right, back_right, ridge_front])
        right_faces1 = np.array([3, 0, 1, 2])
        right_triangle1 = pv.PolyData(right_points1, right_faces1)
        
        # Scale texture coordinates to make texture smaller
        right_tcoords1 = np.array([
            [0.0, 0.0],                    # front bottom corner
            [texture_scale, 0.0],          # back bottom corner
            [texture_scale*0.25, texture_scale]  # ridge front
        ])
        right_triangle1.active_texture_coordinates = right_tcoords1
        
        right_points2 = np.array([back_right, ridge_back, ridge_front])
        right_faces2 = np.array([3, 0, 1, 2])
        right_triangle2 = pv.PolyData(right_points2, right_faces2)
        
        # Scale texture coordinates to make texture smaller, maintaining alignment
        right_tcoords2 = np.array([
            [texture_scale, 0.0],            # back bottom corner
            [texture_scale*0.75, texture_scale],  # ridge back
            [texture_scale*0.25, texture_scale]   # ridge front - must match right_tcoords1[2]
        ])
        right_triangle2.active_texture_coordinates = right_tcoords2
        
        if roof_texture_exists:
            self.plotter.add_mesh(right_triangle1, texture=roof_texture, show_edges=False, 
                                smooth_shading=True)
            self.plotter.add_mesh(right_triangle2, texture=roof_texture, show_edges=False, 
                                smooth_shading=True)
        else:
            self.plotter.add_mesh(right_triangle1, color=roof_texture, show_edges=True)
            self.plotter.add_mesh(right_triangle2, color=roof_texture, show_edges=True)
        
        # === LEFT SIDE ===
        left_points1 = np.array([front_left, ridge_front, back_left])
        left_faces1 = np.array([3, 0, 1, 2])
        left_triangle1 = pv.PolyData(left_points1, left_faces1)
        
        # Scale texture coordinates to make texture smaller
        left_tcoords1 = np.array([
            [0.0, 0.0],                    # front bottom corner
            [texture_scale*0.25, texture_scale],  # ridge front
            [texture_scale, 0.0]           # back bottom corner
        ])
        left_triangle1.active_texture_coordinates = left_tcoords1
        
        left_points2 = np.array([back_left, ridge_back, ridge_front])
        left_faces2 = np.array([3, 0, 1, 2])
        left_triangle2 = pv.PolyData(left_points2, left_faces2)
        
        # Scale texture coordinates to make texture smaller, maintaining alignment
        left_tcoords2 = np.array([
            [texture_scale, 0.0],            # back bottom corner
            [texture_scale*0.75, texture_scale],  # ridge back
            [texture_scale*0.25, texture_scale]   # ridge front - must match left_tcoords1[1]
        ])
        left_triangle2.active_texture_coordinates = left_tcoords2
        
        if roof_texture_exists:
            self.plotter.add_mesh(left_triangle1, texture=roof_texture, show_edges=False, 
                                smooth_shading=True)
            self.plotter.add_mesh(left_triangle2, texture=roof_texture, show_edges=False, 
                                smooth_shading=True)
        else:
            self.plotter.add_mesh(left_triangle1, color=roof_texture, show_edges=True)
            self.plotter.add_mesh(left_triangle2, color=roof_texture, show_edges=True)
        
        # Add the remaining elements
        self.add_roof_edges()
        self.add_base(height=1.0, wall_texture=wall_texture, wall_texture_exists=wall_texture_exists)
        
        # Create annotations
        self.annotator = RoofAnnotation(
            self.plotter,
            self.length,
            self.width,
            self.height,
            self.slope_angle,
            self.theme
        )
        self.annotator.add_annotations()
        
        self.plotter.add_axes()
        self.reset_camera()
        self.plotter.update()

    def add_base(self, height=1.0, wall_texture=None, wall_texture_exists=False):
        """Add a rectangular base (walls) under the hip roof."""
        # Get the roof eave points
        points = self.roof_points
        eave_front_left = points['front_left'].copy()
        eave_front_right = points['front_right'].copy()
        eave_back_left = points['back_left'].copy()
        eave_back_right = points['back_right'].copy()
        
        # Create base points (floor level)
        base_front_left = eave_front_left.copy()
        base_front_right = eave_front_right.copy()
        base_back_left = eave_back_left.copy()
        base_back_right = eave_back_right.copy()
        
        # Adjust z-coordinate for floor level (1 meter below roof)
        base_front_left[2] -= height
        base_front_right[2] -= height
        base_back_left[2] -= height
        base_back_right[2] -= height
        
        # Store base points
        self.base_points = {
            'front_left': base_front_left,
            'front_right': base_front_right,
            'back_left': base_back_left,
            'back_right': base_back_right
        }
        
        # Create wall meshes
        # Front wall
        front_wall_points = np.array([
            base_front_left,
            base_front_right,
            eave_front_right,
            eave_front_left
        ])
        front_wall_faces = np.array([4, 0, 1, 2, 3])
        front_wall = pv.PolyData(front_wall_points, faces=[front_wall_faces])
        
        # Back wall
        back_wall_points = np.array([
            base_back_left,
            base_back_right,
            eave_back_right,
            eave_back_left
        ])
        back_wall_faces = np.array([4, 0, 1, 2, 3])
        back_wall = pv.PolyData(back_wall_points, faces=[back_wall_faces])
        
        # Left wall
        left_wall_points = np.array([
            base_front_left,
            base_back_left,
            eave_back_left,
            eave_front_left
        ])
        left_wall_faces = np.array([4, 0, 1, 2, 3])
        left_wall = pv.PolyData(left_wall_points, faces=[left_wall_faces])
        
        # Right wall
        right_wall_points = np.array([
            base_front_right,
            base_back_right,
            eave_back_right,
            eave_front_right
        ])
        right_wall_faces = np.array([4, 0, 1, 2, 3])
        right_wall = pv.PolyData(right_wall_points, faces=[right_wall_faces])
        
        # Floor (bottom of the house)
        floor_points = np.array([
            base_front_left,
            base_front_right,
            base_back_right,
            base_back_left
        ])
        floor_faces = np.array([4, 0, 1, 2, 3])
        floor = pv.PolyData(floor_points, faces=[floor_faces])
        
        # Set texture coordinates for walls - repeating horizontally
        # For front wall
        front_wall.texture_map_to_plane(inplace=True)
        front_wall.active_texture_coordinates *= np.array([2, 1])  # Repeat texture 2x horizontally
        
        # For back wall
        back_wall.texture_map_to_plane(inplace=True)
        back_wall.active_texture_coordinates *= np.array([2, 1])
        
        # For side walls
        left_wall.texture_map_to_plane(inplace=True)
        left_wall.active_texture_coordinates *= np.array([2, 1])
        
        right_wall.texture_map_to_plane(inplace=True)
        right_wall.active_texture_coordinates *= np.array([2, 1])
        
        # Wall color for fallback
        wall_color = "#E8DCC9"  # Cream/tan color as fallback
        
        if wall_texture_exists:
            # Add walls with texture
            self.plotter.add_mesh(front_wall, texture=wall_texture, show_edges=False)
            self.plotter.add_mesh(back_wall, texture=wall_texture, show_edges=False)
            self.plotter.add_mesh(left_wall, texture=wall_texture, show_edges=False)
            self.plotter.add_mesh(right_wall, texture=wall_texture, show_edges=False)
        else:
            # Add walls with solid color
            self.plotter.add_mesh(front_wall, color=wall_color, show_edges=False)
            self.plotter.add_mesh(back_wall, color=wall_color, show_edges=False)
            self.plotter.add_mesh(left_wall, color=wall_color, show_edges=False)
            self.plotter.add_mesh(right_wall, color=wall_color, show_edges=False)
        
        # Add floor with concrete-like color
        self.plotter.add_mesh(floor, color="#8B7D6B", show_edges=False)
        
        # Add building outline edges for better visibility
        edges = [
            (base_front_left, base_front_right),   # Front base 
            (base_front_right, base_back_right),   # Right base
            (base_back_right, base_back_left),     # Back base
            (base_back_left, base_front_left),     # Left base
            (base_front_left, eave_front_left),    # Front-left vertical
            (base_front_right, eave_front_right),  # Front-right vertical
            (base_back_right, eave_back_right),    # Back-right vertical
            (base_back_left, eave_back_left)       # Back-left vertical
        ]
        
        for start, end in edges:
            edge = pv.Line(start, end)
            self.plotter.add_mesh(edge, color='black', line_width=1)
    
    def add_roof_edges(self):
        """Add edges to outline the roof structure."""
        # Define the corners of the roof base
        front_left = self.roof_points['front_left']
        front_right = self.roof_points['front_right']
        back_left = self.roof_points['back_left']
        back_right = self.roof_points['back_right']
        ridge_front = self.roof_points['ridge_front']
        ridge_back = self.roof_points['ridge_back']
        
        # Add ridge line
        ridge_line = pv.Line(ridge_front, ridge_back)
        self.plotter.add_mesh(ridge_line, color='black', line_width=3)
        
        # Add edges for better visualization
        edges = [
            (front_left, front_right),  # Front eave
            (front_right, back_right),  # Right eave
            (back_right, back_left),    # Back eave
            (back_left, front_left),    # Left eave
            (front_left, ridge_front),  # Front left hip
            (front_right, ridge_front), # Front right hip
            (back_right, ridge_back),   # Back right hip
            (back_left, ridge_back)     # Back left hip
        ]
        
        for start, end in edges:
            edge = pv.Line(start, end)
            self.plotter.add_mesh(edge, color='black', line_width=2)

    def reset_camera(self):
        """Reset camera to default position viewing the front of the roof."""
        self.plotter.camera_position = [
            (self.width*2.0, -self.length*1.2, self.height*2.0),  
            (self.width/2, self.length/2, self.height/2),  
            (0, 0, 1)  
        ]
        self.plotter.reset_camera()
    
    def set_default_camera_view(self):
        """Set camera to the default position viewing the front of the roof."""
        self.plotter.camera_position = [
            (self.width*2.0, -self.length*1.2, self.height*2.0),  
            (self.width/2, self.length/2, self.height/2), 
            (0, 0, 1)  
        ]
        self.plotter.reset_camera()
    
    def add_key_bindings(self):
        """Set up key bindings for solar panel placement."""
        self.plotter.add_key_event("1", lambda: self.add_solar_panels("front"))
        self.plotter.add_key_event("2", lambda: self.add_solar_panels("right"))
        self.plotter.add_key_event("3", lambda: self.add_solar_panels("back"))
        self.plotter.add_key_event("4", lambda: self.add_solar_panels("left"))
        self.plotter.add_key_event("c", self.solar_panel_handler.clear_panels)
        self.plotter.add_key_event("C", self.solar_panel_handler.clear_panels)
        self.plotter.add_key_event("h", self.solar_panel_handler.toggle_help)
        self.plotter.add_key_event("H", self.solar_panel_handler.toggle_help) 
        self.plotter.add_key_event("r", self.reset_camera)
        self.plotter.add_key_event("R", self.reset_camera) 
        self.plotter.add_key_event("s", self.save_roof_screenshot)
        self.plotter.add_key_event("S", self.save_roof_screenshot)
        self.plotter.add_key_event('o', self.clear_obstacles)
        self.plotter.add_key_event('O', self.clear_obstacles)
    
    def add_solar_panels(self, side="front"):
        """Add solar panels to the specified side of the roof."""
        if self.solar_panel_handler:
            print(f"Adding solar panels to {side} side")
            # Use the add_panels method from SolarPanelPlacementHip
            self.solar_panel_handler.add_panels(side)
        else:
            print("Solar panel handler not initialized")
    
    def clear_panels(self):
        """Clear all solar panels from the roof."""
        if self.solar_panel_handler:
            print("Clearing all solar panels")
            self.solar_panel_handler.clear_panels()
            # Restore help text if needed
            if hasattr(self, 'help_visible') and not self.help_visible:
                self.add_help_text()
                self.help_visible = True
        else:
            print("Solar panel handler not initialized")

    def update_panel_config(self, config):
        """Update the solar panel configuration without toggling panels."""
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            # Ensure panel dimensions are in mm as expected by the handler
            result = self.solar_panel_handler.update_panel_config(config)
            print(f"Hip roof: Updated panel config: {result}")
            return result
        else:
            print("Hip roof: No solar panel handler available")
            return False

    def set_screenshot_directory(self, directory):
        """Set the directory where screenshots will be saved."""
        self.screenshot_directory = directory

    def save_roof_screenshot(self):
        """Save current roof view."""
        import os
        import datetime
        from pathlib import Path
        from PyQt5.QtCore import QTimer
        
        # Use the configured screenshot directory or default
        if hasattr(self, 'screenshot_directory') and self.screenshot_directory:
            snaps_dir = Path(self.screenshot_directory)
        else:
            # Default to RoofSnaps if no directory was provided
            snaps_dir = Path("RoofSnaps")
        
        # Ensure the directory exists
        snaps_dir.mkdir(exist_ok=True)
        
        # Generate a unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get the roof type from class name
        roof_type = self.__class__.__name__.lower()
        
        # Create filename
        filename = f"{roof_type}_{timestamp}.png"
        filepath = snaps_dir / filename
        
        # Save the screenshot
        try:
            self.plotter.screenshot(str(filepath))
            
            # Display a temporary success message using translation system
            message_actor = self.plotter.add_text(
                _('screenshot_saved').format(filename=filename),  # Use translation key with format
                position="lower_right",
                font_size=12,
                color="green",
                shadow=True
            )
            
            # Remove the message after 3 seconds
            def remove_message():
                try:
                    self.plotter.remove_actor(message_actor)
                    self.plotter.render()
                except:
                    pass  # Silently ignore if actor doesn't exist
            
            QTimer.singleShot(3000, remove_message)
            
            print(f"Screenshot saved to {filepath}")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            
            # Display error message with translation
            error_actor = self.plotter.add_text(
                _('screenshot_error'),  # Use translation key for error message
                position="lower_right",
                font_size=12,
                color="red",
                shadow=True
            )
            
            # Remove error message after 3 seconds
            def remove_error():
                try:
                    self.plotter.remove_actor(error_actor)
                    self.plotter.render()
                except:
                    pass
            
            QTimer.singleShot(3000, remove_error)

    def update_texts(self):
        """Update all text elements with current language"""
        # Update help text if it exists
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            # First remove the old help text
            self.plotter.remove_actor(self.help_text_actor)
            # Then regenerate it with the current language
            self.add_help_text()
                       
        # Update the plotter
        self.plotter.update()

    def add_help_text(self):
        """Add comprehensive help text for hip roof visualization."""
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            self.plotter.remove_actor(self.help_text_actor)
            self.help_text_actor = None
        
        # Create comprehensive help text for hip roof
        help_text = (
            f"{_('help_hip_roof_title')}\n"
            f"{_('help_place_front_face')} (1)\n"
            f"{_('help_place_right_face')} (2)\n"
            f"{_('help_place_back_face')} (3)\n"
            f"{_('help_place_left_face')} (4)\n"
            f"{_('help_clear_panels')} (C)\n"
            f"\n"
            f"{_('roof_obstacles')}:\n"
            f"{_('click_on_black_dot')}\n"
            f"{_('help_remove_obstacles')} (O)\n"
            f"\n"
            f"{_('help_view_controls_title')}\n"
            f"{_('help_reset_camera')} (R)\n"
            f"{_('help_save_screenshot')} (S)\n"
            f"{_('help_toggle_menu')} (H)"
        )
        
        self.help_text_actor = self.plotter.add_text(
            help_text,
            position="upper_right",
            font_size=12,
            color="black"
        )
        self.help_visible = True
    
    def toggle_help(self):
        """Toggle visibility of help text."""
        if hasattr(self, 'help_visible') and self.help_visible:
            self.plotter.remove_actor(self.help_text_actor)
            self.help_visible = False
        else:
            self.add_help_text()
            self.help_visible = True

    def add_obstacle(self, obstacle_type, dimensions=None):
        """Add a roof obstacle of the specified type with optional dimensions"""
        try:
            # Directly check against translated strings at runtime
            # This way translations are evaluated when the method is called
            if obstacle_type == _('chimney'):
                internal_type = "Chimney"
            elif obstacle_type == _('roof_window'):
                internal_type = "Roof Window" 
            elif obstacle_type == _('ventilation'):
                internal_type = "Ventilation"
            else:
                # If it doesn't match any translated string, use as-is
                internal_type = obstacle_type
            
            # Store the selected obstacle type and dimensions
            self.selected_obstacle_type = internal_type
            self.obstacle_dimensions = dimensions
            
            # If dimensions were not provided, we'll show the obstacle dialog
            if dimensions is None:
                return self.add_obstacle_button_clicked()
            else:
                # Show instruction to the user
                if hasattr(self, 'placement_instruction') and self.placement_instruction:
                    self.plotter.remove_actor(self.placement_instruction)
                    
                # For display, use appropriate translated name based on internal type
                if internal_type == "Chimney":
                    display_name = _('chimney')
                elif internal_type == "Roof Window":
                    display_name = _('roof_window')
                elif internal_type == "Ventilation":
                    display_name = _('ventilation')
                else:
                    display_name = internal_type
                    
                remaining = 6 - self.obstacle_count
                self.placement_instruction = self.plotter.add_text(
                    _('click_to_place') + f" {display_name} " +
                    f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")",
                    position="lower_left",
                    font_size=12,
                    color="black"
                )
                
                # Add attachment points to enable placement
                return self.add_attachment_points()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False 
        
    def add_attachment_points(self):
        """Generate attachment points for the hip roof with explicit face normal calculations"""
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
            self.face_normals = {}  # Store normals for each attachment point
            
            # Flag to track if we've placed an obstacle in this session
            self.obstacle_placed_this_session = False
            
            # Use a moderate offset for attachment points
            offset_distance = 0.15  # 15cm offset
            
            # Get roof points from stored geometry
            points = self.roof_points
            
            # Extract key points from the roof
            front_left = points['front_left']
            front_right = points['front_right']
            back_left = points['back_left']
            back_right = points['back_right']
            ridge_front = points['ridge_front']
            ridge_back = points['ridge_back']
            
            # Calculate actual face normals based on geometry
            # Front face normal (triangular face)
            v1_front = front_right - front_left
            v2_front = ridge_front - front_left
            front_normal = np.cross(v1_front, v2_front)
            # Ensure it points outward (check z-component)
            if front_normal[2] < 0:
                front_normal = -front_normal
            front_normal = front_normal / np.linalg.norm(front_normal)
            
            # Right face normal (quadrilateral face)
            v1_right = ridge_front - front_right
            v2_right = back_right - front_right
            right_normal = np.cross(v1_right, v2_right)
            if right_normal[2] < 0:
                right_normal = -right_normal
            right_normal = right_normal / np.linalg.norm(right_normal)
            
            # Back face normal (triangular face)
            v1_back = back_left - back_right
            v2_back = ridge_back - back_right
            back_normal = np.cross(v1_back, v2_back)
            if back_normal[2] < 0:
                back_normal = -back_normal
            back_normal = back_normal / np.linalg.norm(back_normal)
            
            # Left face normal (quadrilateral face)
            v1_left = ridge_back - back_left
            v2_left = front_left - back_left
            left_normal = np.cross(v1_left, v2_left)
            if left_normal[2] < 0:
                left_normal = -left_normal
            left_normal = left_normal / np.linalg.norm(left_normal)
            
            # Store face info for later reference when placing obstacles
            self.roof_face_info = {
                'front': {
                    'normal': front_normal,
                    'points': [front_left, front_right, ridge_front]
                },
                'right': {
                    'normal': right_normal,
                    'points': [front_right, back_right, ridge_back, ridge_front]
                },
                'back': {
                    'normal': back_normal,
                    'points': [back_right, back_left, ridge_back]
                },
                'left': {
                    'normal': left_normal,
                    'points': [back_left, front_left, ridge_front, ridge_back]
                }
            }
            
            # Now generate attachment points for each face
            point_index = 0
            
            # 1\. Front face (triangular)
            for u in np.linspace(0.1, 0.9, 5):
                for v in np.linspace(0.1, 0.9, 5):
                    if u + v <= 1:  # Stay within triangle
                        # Barycentric coordinates for triangle
                        point = (1-u-v)*front_left + u*front_right + v*ridge_front
                        # Add offset in normal direction
                        offset_point = point + front_normal * offset_distance
                        # Safety check - ensure point is above the roof
                        if offset_point[2] < point[2]:
                            offset_point[2] = point[2] + 0.1
                        self.attachment_points.append(offset_point)
                        # Store the normal and face info for this point
                        self.face_normals[point_index] = {'normal': front_normal, 'face': 'front', 'roof_point': point}
                        point_index += 1
                        
            # 2\. Right face (quad)
            for u in np.linspace(0.1, 0.9, 5):
                for v in np.linspace(0.1, 0.9, 5):
                    # Bilinear interpolation for quad
                    point = (1-u)*(1-v)*front_right + u*(1-v)*back_right + \
                            (1-u)*v*ridge_front + u*v*ridge_back
                    # Add offset in normal direction
                    offset_point = point + right_normal * offset_distance
                    # Safety check
                    if offset_point[2] < point[2]:
                        offset_point[2] = point[2] + 0.1
                    self.attachment_points.append(offset_point)
                    # Store the normal and face info for this point
                    self.face_normals[point_index] = {'normal': right_normal, 'face': 'right', 'roof_point': point}
                    point_index += 1
                    
            # 3\. Back face (triangular)
            for u in np.linspace(0.1, 0.9, 5):
                for v in np.linspace(0.1, 0.9, 5):
                    if u + v <= 1:  # Stay within triangle
                        # Barycentric coordinates for triangle
                        point = (1-u-v)*back_right + u*back_left + v*ridge_back
                        # Add offset in normal direction
                        offset_point = point + back_normal * offset_distance
                        # Safety check
                        if offset_point[2] < point[2]:
                            offset_point[2] = point[2] + 0.1
                        self.attachment_points.append(offset_point)
                        # Store the normal and face info for this point
                        self.face_normals[point_index] = {'normal': back_normal, 'face': 'back', 'roof_point': point}
                        point_index += 1
                        
            # 4\. Left face (quad)
            for u in np.linspace(0.1, 0.9, 5):
                for v in np.linspace(0.1, 0.9, 5):
                    # Bilinear interpolation for quad
                    point = (1-u)*(1-v)*back_left + u*(1-v)*front_left + \
                            (1-u)*v*ridge_back + u*v*ridge_front
                    # Add offset in normal direction
                    offset_point = point + left_normal * offset_distance
                    # Safety check
                    if offset_point[2] < point[2]:
                        offset_point[2] = point[2] + 0.1
                    self.attachment_points.append(offset_point)
                    # Store the normal and face info for this point
                    self.face_normals[point_index] = {'normal': left_normal, 'face': 'left', 'roof_point': point}
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
                    self.update_instruction(
                        _('click_to_place') + f" {self.selected_obstacle_type} " +
                        f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")"
                    )
            
            
            return True
        
        except Exception as e:
            print(f"Error adding attachment points: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def clear_attachment_points(self):
        """Remove all attachment points from the visualization"""
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.plotter.remove_actor(self.attachment_point_actor)
            self.attachment_point_actor = None
        
        # Disable picking when clearing attachment points
        try:
            self.plotter.disable_picking()
        except:
            pass
        
        if hasattr(self, 'attachment_points'):
            self.attachment_points = []
        
    def toggle_attachment_points(self):
        """Toggle visibility of attachment points"""
        if hasattr(self, 'attachment_point_actor') and self.attachment_point_actor:
            self.clear_attachment_points()
        else:
            self.add_attachment_points()

    def find_closest_attachment_point(self, click_point):
        """Find the closest attachment point to the clicked position"""
        if not hasattr(self, 'attachment_points') or not self.attachment_points:
            return None, None
            
        min_distance = float('inf')
        closest_idx = None
        closest_point = None
        
        for idx, point_data in self.attachment_points_occupied.items():
            point = point_data['position']
            distance = np.linalg.norm(np.array(point) - np.array(click_point))
            
            if distance < min_distance:
                min_distance = distance
                closest_idx = idx
                closest_point = point
        
        return closest_idx, closest_point

    def attachment_point_clicked(self, point, *args):
        """Handle click on attachment point - place ONE obstacle only"""
        # Check if we already placed an obstacle this session
        if hasattr(self, 'obstacle_placed_this_session') and self.obstacle_placed_this_session:
            self.update_instruction(
                _('obstacle_already_placed')
            )
            return
        
        # Check if obstacle type is selected
        if not hasattr(self, 'selected_obstacle_type') or not self.selected_obstacle_type:
            # No obstacle type selected
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
        
        # If we have solar panels, update their placement to account for the new obstacle
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            # For Hip roof, we might have multiple active sides
            if hasattr(self.solar_panel_handler, 'active_sides'):
                active_sides = list(self.solar_panel_handler.active_sides)
                # Refresh panels on all active sides to account for the new obstacle
                for side in active_sides:
                    self.solar_panel_handler.remove_panels_from_side(side)
                    self.solar_panel_handler.add_panels(side)
        
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
            self.update_instruction(
                _('obstacle_max_reached') + " (6/6)"
            )
    def place_obstacle_at_point(self, point, obstacle_type, normal_vector=None, roof_point=None, face=None):
        """Place an obstacle at the specified point with the stored dimensions"""
        # Check if we have custom dimensions
        dimensions = None
        if hasattr(self, 'obstacle_dimensions'):
            dimensions = self.obstacle_dimensions
        
        # Create the obstacle with orientation information
        obstacle = RoofObstacle(
            obstacle_type, 
            point, 
            self, 
            dimensions=dimensions,
            normal_vector=normal_vector,
            roof_point=roof_point,
            face=face
        )
        
        # Add to plotter
        obstacle.add_to_plotter(self.plotter)
        
        return obstacle

    def clear_obstacles(self):
        """Remove all obstacles from the roof"""
        if hasattr(self, 'obstacles') and self.obstacles:
            for obstacle in self.obstacles:
                if hasattr(obstacle, 'actor') and obstacle.actor:
                    self.plotter.remove_actor(obstacle.actor)
            
            # Clear the list
            self.obstacles = []
            
            # Reset obstacle count
            self.obstacle_count = 0
            
            # Reset occupation status
            if hasattr(self, 'attachment_points_occupied'):
                for idx in self.attachment_points_occupied:
                    self.attachment_points_occupied[idx]['occupied'] = False
                    self.attachment_points_occupied[idx]['obstacle'] = None
            
            # Update instruction
            self.update_instruction(_('obstacle_removed') + " (0/6)")

    def update_instruction(self, message):
        """Update the instruction text in the plotter"""
        if hasattr(self, 'placement_instruction') and self.placement_instruction:
            self.plotter.remove_actor(self.placement_instruction)
        
        self.placement_instruction = self.plotter.add_text(
            message,
            position="lower_left",
            font_size=12,
            color="black"
        )

    def is_point_occupied(self, point):
        """Check if a point is already occupied by an obstacle"""
        if not hasattr(self, 'obstacles') or not self.obstacles:
            return False
            
        # Check if any existing obstacle is too close to this point
        min_distance = 0.2  # Minimum distance in meters
        
        for obstacle in self.obstacles:
            distance = np.linalg.norm(np.array(obstacle.position) - np.array(point))
            if distance < min_distance:
                return True
                
        return False

    def add_obstacle_button_clicked(self):
        """Handle 'Add Obstacle' button click"""
        # Check if we've reached the maximum limit
        if hasattr(self, 'obstacle_count') and self.obstacle_count >= 6:
            self.update_instruction(_('obstacle_max_reached'))
            return False
            
        # Create dialogs instance
        dialogs = RoofObstacleDialogs()
        
        # Show the selection dialog, which will also show the properties dialog
        # and then call our callback when done
        dialogs.show_selection_dialog(self.on_obstacle_selected)
        return True

    def on_obstacle_selected(self, obstacle_type, dimensions):
        """Callback when obstacle type and dimensions are selected"""
        if obstacle_type is None or dimensions is None:
            # User canceled
            return
            
        # Store the selected values for use when placing
        self.selected_obstacle_type = obstacle_type
        self.obstacle_dimensions = dimensions
        
        # Continue with placement
        self.add_attachment_points()

    def get_translated_obstacle_name(self, internal_type):
        """Get translated name for an obstacle based on internal type"""
        if internal_type == "Chimney":
            return _('chimney')
        elif internal_type == "Roof Window":
            return _('roof_window')
        elif internal_type == "Ventilation":
            return _('ventilation')
        else:
            return internal_type
