from translations import _
import pyvista as pv
import numpy as np
import os
import sys
from pathlib import Path
from solar_panel_handlers.solar_panel_gable import SolarPanelPlacementGable
import tkinter as tk
from tkinter import messagebox
from roofs.roof_annotation import RoofAnnotation
from roofs.roof_obstacle import RoofObstacle
from ui.dialogs.obstacle_dialogs import RoofObstacleDialogs

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
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

class GableRoof:
    def __init__(self, plotter=None, dimensions=(10.0, 7.0, 4.0), theme="light"):
        # If dimensions are provided, use them; otherwise, show dialog to get them
        if dimensions is None:
            dimensions = self.show_input_dialog()
            if dimensions is None: 
                return
                
        # Unpack dimensions (all in meters)
        self.length, self.width, self.height = dimensions
        self.theme = theme  # Store theme as instance variable
        
        # If a plotter is provided, use it; otherwise create a new one
        if plotter:
            self.plotter = plotter
            self.external_plotter = True
        else:
            self.plotter = pv.Plotter()
            self.external_plotter = False
            
        # Set theme-appropriate background
        self.set_plotter_background()
            
        # Calculate slope properties
        self.slope_width = np.sqrt((self.width / 2) ** 2 + self.height ** 2)
        self.slope_angle = np.arctan(self.height / (self.width / 2))  # Angle in radians
        
        # Store reference points
        self.roof_points = {}
        
        # Debug text actor for status messages
        self.debug_text = None
        
        # Define roof colors (fallback if texture not available)
        self.roof_color = "#610B0B"  # Dark red color for the roof
        self.wall_color = "#404040"  # Dark gray color for the walls
        
        # Initialize texture paths directly - don't use Path objects
        self.roof_texture_file = "PVmizer/textures/rooftile.jpg"
        self.wall_texture_file = "PVmizer/textures/woodwall.jpg"
        self.concrete_texture_file = "PVmizer/textures/wall.jpg"
        
        # Add axes to the plotter
        self.plotter.add_axes()
        
        # Create the roof
        self.create_gable_roof()

        # Create annotations using the RoofAnnotation helper
        self.annotator = RoofAnnotation(
            self.plotter,
            self.length,
            self.width,
            self.height,
            self.slope_angle,
            self.theme
        )
        self.annotator.add_annotations()
        
        # Add help text
        self.add_help_text()
        
        # Initialize solar panel handler
        try:
            # Create solar panel handler
            self.solar_panel_handler = SolarPanelPlacementGable(self)
        except Exception as e:
            self.solar_panel_handler = None
        
        # Initialize obstacle-related properties
        self.attachment_points = []
        self.attachment_point_actor = None
        self.obstacles = []
        self.obstacle_count = 0
        self.placement_instruction = None
        
        # Set up key bindings
        self.setup_key_bindings()
        
        # Set default camera view
        self.set_default_camera_view()
                
        # Only show the plotter if we created it internally
        if not self.external_plotter:
            self.plotter.show()
            
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
            
    def set_theme(self, theme):
        """Update the roof's theme and refresh visuals"""
        self.theme = theme
        self.set_plotter_background()
        
        # Update annotator's theme if it exists
        if hasattr(self, 'annotator'):
            self.annotator.set_theme(theme)
        
    def set_plotter_background(self):
        """Set the plotter background based on current theme"""
        if hasattr(self, 'theme') and self.theme == "dark":
            self.plotter.set_background("darkgrey")
        else:
            self.plotter.set_background("lightgrey")
    
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
    
    def setup_key_bindings(self):
        """Set up key bindings for user interaction."""
        # Panel placement keys
        if self.solar_panel_handler:
            self.plotter.add_key_event("1", lambda: self.solar_panel_handler.add_panels("left"))
            self.plotter.add_key_event("2", lambda: self.solar_panel_handler.add_panels("right"))
            self.plotter.add_key_event("c", self.solar_panel_handler.clear_panels)
            self.plotter.add_key_event("C", self.solar_panel_handler.clear_panels)
            self.plotter.add_key_event("Left", lambda: self.solar_panel_handler.add_panels("left"))
            self.plotter.add_key_event("Right", lambda: self.solar_panel_handler.add_panels("right"))
            self.plotter.add_key_event("r", self.reset_camera)
            self.plotter.add_key_event("R", self.reset_camera)
            self.plotter.add_key_event("h", self.toggle_help)
            self.plotter.add_key_event("H", self.toggle_help)
            self.plotter.add_key_event("s", self.save_roof_screenshot)
            self.plotter.add_key_event("S", self.save_roof_screenshot)
            self.plotter.add_key_event('o', self.clear_obstacles)
            self.plotter.add_key_event('O', self.clear_obstacles)
          
    def create_gable_roof(self):
        """Creates a gable roof with concrete base and wooden walls"""
        # Define key points for the roof
        ridge_front = np.array([self.width/2, 0, self.height])
        ridge_back = np.array([self.width/2, self.length, self.height])
        
        # Eave points (top of building walls)
        eave_left_front = np.array([0, 0, 0])
        eave_right_front = np.array([self.width, 0, 0])
        eave_left_back = np.array([0, self.length, 0])
        eave_right_back = np.array([self.width, self.length, 0])
        
        # Define building height - reduced to 1 meter
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
        
        # ===== ROOF COMPONENTS =====
        # Create roof slopes (only the sloped parts)
        left_slope_points = np.array([eave_left_front, eave_left_back, ridge_back, ridge_front])
        left_faces = np.array([[4, 0, 1, 2, 3]])
        self.left_slope = pv.PolyData(left_slope_points, left_faces)
        
        right_slope_points = np.array([eave_right_front, eave_right_back, ridge_back, ridge_front])
        right_faces = np.array([[4, 0, 1, 2, 3]])
        self.right_slope = pv.PolyData(right_slope_points, right_faces)
        
        # ===== WALL COMPONENTS =====
        # Create front gable (triangular part at the front)
        front_gable_points = np.array([eave_left_front, eave_right_front, ridge_front])
        front_gable_faces = np.array([[3, 0, 1, 2]])
        front_gable = pv.PolyData(front_gable_points, front_gable_faces)
        
        # Create back gable (triangular part at the back)
        back_gable_points = np.array([eave_left_back, eave_right_back, ridge_back])
        back_gable_faces = np.array([[3, 0, 1, 2]])
        back_gable = pv.PolyData(back_gable_points, back_gable_faces)
        
        # ===== CONCRETE BASE COMPONENTS =====
        # Floor (foundation)
        floor_points = np.array([
            base_left_front, base_right_front, 
            base_right_back, base_left_back
        ])
        floor_faces = np.array([[4, 0, 1, 2, 3]])
        floor = pv.PolyData(floor_points, floor_faces)
        
        # Front concrete base wall
        front_base_points = np.array([
            base_left_front, base_right_front, 
            base_right_front + np.array([0, 0, building_height]), 
            base_left_front + np.array([0, 0, building_height])
        ])
        front_base_faces = np.array([[4, 0, 1, 2, 3]])
        front_base = pv.PolyData(front_base_points, front_base_faces)
        
        # Back concrete base wall
        back_base_points = np.array([
            base_left_back, base_right_back, 
            base_right_back + np.array([0, 0, building_height]), 
            base_left_back + np.array([0, 0, building_height])
        ])
        back_base_faces = np.array([[4, 0, 1, 2, 3]])
        back_base = pv.PolyData(back_base_points, back_base_faces)
        
        # Left concrete base wall
        left_base_points = np.array([
            base_left_front, base_left_back, 
            base_left_back + np.array([0, 0, building_height]), 
            base_left_front + np.array([0, 0, building_height])
        ])
        left_base_faces = np.array([[4, 0, 1, 2, 3]])
        left_base = pv.PolyData(left_base_points, left_base_faces)
        
        # Right concrete base wall
        right_base_points = np.array([
            base_right_front, base_right_back, 
            base_right_back + np.array([0, 0, building_height]), 
            base_right_front + np.array([0, 0, building_height])
        ])
        right_base_faces = np.array([[4, 0, 1, 2, 3]])
        right_base = pv.PolyData(right_base_points, right_base_faces)
        
        # Create texture coordinates
        # For roof slopes - stretch texture across surface
        left_tcoords = np.array([
            [0, 0], [3, 0], [3, 1], [0, 1]
        ])
        
        right_tcoords = np.array([
            [0, 0], [3, 0], [3, 1], [0, 1]
        ])
        
        # For gable triangles
        front_gable_tcoords = np.array([
            [0, 0], [1, 0], [0.5, 1]
        ])
        
        back_gable_tcoords = np.array([
            [0, 0], [1, 0], [0.5, 1]
        ])
        
        # For walls - using appropriate repeat to avoid stretching
        std_wall_tcoords = np.array([
            [0, 0], [2, 0], [2, 1], [0, 1]
        ])
        
        # For concrete foundation - increase tiling for more detail
        concrete_tcoords = np.array([
            [0, 0], [3, 0], [3, 1], [0, 1]
        ])
        
        # For floor with more tiling
        floor_tcoords = np.array([
            [0, 0], [3, 0], [3, 3], [0, 3]
        ])
        
        # Apply texture coordinates
        self.left_slope.active_texture_coordinates = left_tcoords
        self.right_slope.active_texture_coordinates = right_tcoords
        front_gable.active_texture_coordinates = front_gable_tcoords
        back_gable.active_texture_coordinates = back_gable_tcoords
        
        # Apply concrete texture coordinates
        floor.active_texture_coordinates = floor_tcoords
        front_base.active_texture_coordinates = concrete_tcoords
        back_base.active_texture_coordinates = concrete_tcoords
        left_base.active_texture_coordinates = concrete_tcoords
        right_base.active_texture_coordinates = concrete_tcoords
        
        # Load textures with the safe method
        roof_texture, roof_texture_exists = self.load_texture_safely(self.roof_texture_file, self.roof_color)
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file, self.wall_color)
        concrete_texture, concrete_texture_exists = self.load_texture_safely(self.concrete_texture_file, "#AAAAAA")
        
        # ===== APPLY TEXTURES TO COMPONENTS =====
        
        # 1\. Apply roof texture ONLY to roof slopes
        if roof_texture_exists:
            self.plotter.add_mesh(self.left_slope, texture=roof_texture, show_edges=True)
            self.plotter.add_mesh(self.right_slope, texture=roof_texture, show_edges=True)
        else:
            self.plotter.add_mesh(self.left_slope, color=roof_texture, show_edges=True)
            self.plotter.add_mesh(self.right_slope, color=roof_texture, show_edges=True)
        
        # 2\. Apply WALL texture to ONLY gable triangles (upper parts)
        if wall_texture_exists:
            # Apply to triangular gables
            self.plotter.add_mesh(front_gable, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_gable, texture=wall_texture, show_edges=True)
        else:
            # Fallback to solid color
            self.plotter.add_mesh(front_gable, color=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_gable, color=wall_texture, show_edges=True)
        
        # 3\. Apply CONCRETE texture to floor and base walls
        if concrete_texture_exists:
            # Apply to floor and all base walls
            self.plotter.add_mesh(floor, texture=concrete_texture, show_edges=True)
            self.plotter.add_mesh(front_base, texture=concrete_texture, show_edges=True)
            self.plotter.add_mesh(back_base, texture=concrete_texture, show_edges=True)
            self.plotter.add_mesh(left_base, texture=concrete_texture, show_edges=True)
            self.plotter.add_mesh(right_base, texture=concrete_texture, show_edges=True)
        else:
            # Fallback to solid color
            self.plotter.add_mesh(floor, color=concrete_texture, show_edges=True)
            self.plotter.add_mesh(front_base, color=concrete_texture, show_edges=True)
            self.plotter.add_mesh(back_base, color=concrete_texture, show_edges=True)
            self.plotter.add_mesh(left_base, color=concrete_texture, show_edges=True)
            self.plotter.add_mesh(right_base, color=concrete_texture, show_edges=True)
    
    def add_help_text(self):
        """Add comprehensive help text for gable roof visualization."""
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            self.plotter.remove_actor(self.help_text_actor)
            self.help_text_actor = None
        
        # Create comprehensive help text for gable roof
        help_text = (
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

        self.help_text_actor = self.plotter.add_text(
            help_text,
            position="upper_right",
            font_size=12,
            color="black"
        )
        self.help_visible = True
    
    def toggle_help(self):
        """Toggle visibility of help text."""
        if self.help_visible:
            self.plotter.remove_actor(self.help_text_actor)
            self.help_visible = False
        else:
            self.add_help_text()
            self.help_visible = True
    
    def update_debug_text(self, text):
        """Update the debug text in the visualization."""
        if self.debug_text:
            self.plotter.remove_actor(self.debug_text)
        
        self.debug_text = self.plotter.add_text(
            text, 
            position="upper_left", 
            font_size=12, 
            color="black"
        )
    
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
        
    def update_panel_config(self, panel_config):           
        try:
            # Log input configuration (already in millimeters)
            if panel_config:
                for key, value in panel_config.items():
                    print(f"  {key}: {value}")
            
            # Clear existing panels
            self.solar_panel_handler.clear_panels()
            
            # Update panel configuration in the handler
            # (The SolarPanelPlacementGable class should handle dimensions in millimeters)
            result = self.solar_panel_handler.update_panel_config(panel_config)
            return result
                        
        except Exception as e:
            print(f"Error updating panel configuration: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_texts(self):
        """Update all text elements with current language"""
        # Update help text if it exists
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            # First remove the old help text
            self.plotter.remove_actor(self.help_text_actor)
            # Then regenerate it with the current language
            self.add_help_text()
        
        # Refresh the solar panel handler if it exists
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            self.solar_panel_handler.refresh_language()
                    
        # Update the plotter
        self.plotter.update()

    def refresh_language(self):
        """Update all displayed text with current language when the application language changes."""
        try:
            # Update help text if it's visible
            if hasattr(self, 'help_visible') and self.help_visible:
                self.add_help_text()
            
            # Update performance/debug display
            self.update_debug_text()
            
            # Update status text
            self.update_texts()
            
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
            
    def add_obstacle(self, obstacle_type, dimensions=None):
        try:
            # Map localized names to internal names if needed
            if obstacle_type == _('chimney'):
                internal_type = "Chimney"
            elif obstacle_type == _('roof_window'):
                internal_type = "Roof Window" 
            elif obstacle_type == _('ventilation'):
                internal_type = "Ventilation"
            else:
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
                # Get translated display name using helper function
                display_name = self.get_translated_obstacle_name(internal_type)
                    
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
            print(f"Error in add_obstacle: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_translated_obstacle_name(self, obstacle_type):
        """Get the translated name for display based on internal type"""
        if obstacle_type == "Chimney":
            return _('chimney')
        elif obstacle_type == "Roof Window":
            return _('roof_window')
        elif obstacle_type == "Ventilation":
            return _('ventilation')
        else:
            return obstacle_type
        
    def add_attachment_points(self):
        """Generate attachment points and enable placing ONE obstacle"""
        try:
            # Check if we've reached the maximum limit
            if hasattr(self, 'obstacle_count') and self.obstacle_count >= 6:
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
            
            # Define a minimum distance to keep from existing obstacles (in meters)
            min_obstacle_distance = 1
            
            # Reduced number of points - 6x6 grid per face (instead of 12x12)
            face_u_steps = 6
            face_v_steps = 6
            
            # Function to check if a point is valid (away from obstacles)
            def is_valid_point(point):
                # Check distance from existing obstacles
                if hasattr(self, 'obstacles') and self.obstacles:
                    for obstacle in self.obstacles:
                        dist = np.linalg.norm(np.array(obstacle.position) - np.array(point))
                        if dist < min_obstacle_distance:
                            return False
                return True
            
            # Generate points on left face
            for u in np.linspace(0.1, 0.9, face_u_steps):
                for v in np.linspace(0.1, 0.9, face_v_steps):
                    p1 = left_face_points[0] * (1-u) * (1-v)
                    p2 = left_face_points[1] * u * (1-v)
                    p3 = left_face_points[2] * u * v
                    p4 = left_face_points[3] * (1-u) * v
                    point = p1 + p2 + p3 + p4
                    
                    # Only add valid points
                    if is_valid_point(point):
                        self.attachment_points.append(point)
            
            # Generate points on right face
            for u in np.linspace(0.1, 0.9, face_u_steps):
                for v in np.linspace(0.1, 0.9, face_v_steps):
                    p1 = right_face_points[0] * (1-u) * (1-v)
                    p2 = right_face_points[1] * u * (1-v)
                    p3 = right_face_points[2] * u * v
                    p4 = right_face_points[3] * (1-u) * v
                    point = p1 + p2 + p3 + p4
                    
                    # Only add valid points
                    if is_valid_point(point):
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
                    point_size=10,  # Increased from 6
                    render_points_as_spheres=True,
                    pickable=True
                )
                
                # Enable point picking - only for ONE obstacle
                self.plotter.enable_point_picking(
                    callback=self.attachment_point_clicked,
                    show_message=False,
                    pickable_window=False,
                    tolerance=0.05
                )
                
                # Update instruction if not already set
                if not hasattr(self, 'placement_instruction') or not self.placement_instruction:
                    remaining = 6 - self.obstacle_count
                    self.update_instruction(
                        _('click_to_place') + f" {self.selected_obstacle_type} " +
                        f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")"
                    )
                            
            return True
        
        except Exception as e:
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
        
        # Convert to numpy array once for efficiency
        click_point_array = np.array(click_point)
        
        for idx, point_data in self.attachment_points_occupied.items():
            point = point_data['position']
            # Use numpy for efficient distance calculation
            distance = np.linalg.norm(np.array(point) - click_point_array)
            
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
        
        # Place the obstacle
        obstacle = self.place_obstacle_at_point(closest_point, self.selected_obstacle_type)
        
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
        
        # ADDED: If we have solar panels, update their placement to account for the new obstacle
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            # Get current side (for gable roof there's typically only one active side at a time)
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
            self.update_instruction(
                _('obstacle_max_reached') + " (6/6)"
            )
    def place_obstacle_at_point(self, point, obstacle_type):
        """Place an obstacle at the specified point with the stored dimensions"""
        # Check if we have custom dimensions
        dimensions = None
        if hasattr(self, 'obstacle_dimensions'):
            dimensions = self.obstacle_dimensions
        
        # Calculate the normal vector at this point
        normal_vector = self.calculate_normal_at_point(point)
        
        # Create the obstacle with the normal vector
        obstacle = RoofObstacle(obstacle_type, point, self, dimensions=dimensions, normal_vector=normal_vector)
        
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

    def calculate_normal_at_point(self, point):
        """Calculate the normal vector at a specific point on the gable roof"""
        # For gable roof, we only need to check if we're on the left or right side
        center_x = self.width / 2
        
        # Get roof angle in radians
        slope_angle = self.slope_angle
        
        # Create normal vector based on which side the point is on
        if point[0] < center_x:
            # Left side (sloping from left to right)
            # Normal points up and to the right
            normal = np.array([-np.sin(slope_angle), 0, np.cos(slope_angle)])
        else:
            # Right side (sloping from right to left)
            # Normal points up and to the left
            normal = np.array([np.sin(slope_angle), 0, np.cos(slope_angle)])
        
        # Make sure normal is normalized
        normal = normal / np.linalg.norm(normal)
        
        return normal
