"""
Abstract base class for all roof types
Implements the Template Method pattern to eliminate code duplication
Provides common functionality for roof visualization, solar panels, and obstacles
(Help system and debug system removed)
"""
from abc import ABC, abstractmethod
import pyvista as pv
import numpy as np
import os
import sys
import datetime
from pathlib import Path
from PyQt5.QtCore import QTimer
from translations import _
from ui.dialogs.obstacle_dialogs import RoofObstacleDialogs
from roofs.roof_obstacle import RoofObstacle
from roofs.roof_annotation import RoofAnnotation
from .resource_utils import resource_path

class BaseRoof(ABC):
    """
    Abstract base class for all roof types
    
    This class implements the Template Method pattern where:
    - Common functionality is implemented in concrete methods
    - Roof-specific behavior is defined as abstract methods
    - The initialization process is orchestrated by the template method
    """
    
    def __init__(self, plotter=None, dimensions=None, theme="light"):
        """
        Template method for roof initialization
        
        Args:
            plotter: PyVista plotter instance or QtInteractor
            dimensions: Roof dimensions (varies by roof type)
            theme: Visual theme ("light" or "dark")
        """
        # Store basic properties
        self.theme = theme
        self.base_height = 1.0
        
        # Setup plotter with validation
        self._setup_plotter(plotter)
        
        # Clear existing key bindings
        if self.plotter:
            self.clear_key_bindings()
            print("✅ Cleared existing key bindings before setup")

        # Set theme-appropriate background
        self.set_plotter_background()
        
        # Initialize common properties
        self.attachment_points = []
        self.attachment_point_actor = None
        self.obstacles = []
        self.obstacle_count = 0
        self.placement_instruction = None
        self.selected_obstacle_type = None
        self.obstacle_dimensions = None
        self.enable_help_system = False
        # Setup textures
        self._setup_textures()
        
        # Add axes to the plotter
        try:
            self.plotter.add_axes()
            print(f"✅ {self.__class__.__name__}: Axes added successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Could not add axes: {e}")

    def _setup_plotter(self, plotter):
        """Setup plotter with proper type checking and validation"""
        if plotter:
            # Check if it's a QtInteractor
            if hasattr(plotter, 'plotter') and hasattr(plotter.plotter, 'add_mesh'):
                self.plotter = plotter.plotter
                self.external_plotter = True
                print(f"✅ {self.__class__.__name__}: Using QtInteractor.plotter")
            # Check if it's already a PyVista plotter
            elif hasattr(plotter, 'add_mesh'):
                self.plotter = plotter
                self.external_plotter = True
                print(f"✅ {self.__class__.__name__}: Using PyVista plotter directly")
            else:
                print(f"⚠️ {self.__class__.__name__}: Unknown plotter type: {type(plotter)}, creating new one")
                self.plotter = pv.Plotter()
                self.external_plotter = False
        else:
            self.plotter = pv.Plotter()
            self.external_plotter = False
        
        # Validate the plotter has required methods
        required_methods = ['add_mesh', 'clear', 'render', 'add_key_event']
        plotter_valid = True
        for method in required_methods:
            if not hasattr(self.plotter, method):
                print(f"❌ {self.__class__.__name__}: Plotter missing method: {method}")
                plotter_valid = False
                break
        
        if not plotter_valid:
            print(f"❌ {self.__class__.__name__}: Creating new plotter due to validation failure")
            self.plotter = pv.Plotter()
            self.external_plotter = False
        
        print(f"✅ {self.__class__.__name__} plotter initialized: {type(self.plotter)}")

    def _setup_textures(self):
        """Setup texture paths - can be overridden by subclasses"""
        texture_dir = resource_path("PVmizer/textures")
        self.wall_texture_file = os.path.join(texture_dir, "wall.jpg")
        self.brick_texture_file = os.path.join(texture_dir, "brick.jpg")

    # ==================== ABSTRACT METHODS ====================
    @abstractmethod
    def create_roof_geometry(self):
        """Create the specific roof geometry - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def setup_roof_specific_key_bindings(self):
        """Setup key bindings specific to this roof type"""
        pass
        
    @abstractmethod
    def get_solar_panel_areas(self):
        """Get valid solar panel areas for this roof type"""
        pass

    @abstractmethod
    def get_solar_panel_handler_class(self):
        """Get the solar panel handler class for this roof type"""
        pass

    @abstractmethod
    def calculate_camera_position(self):
        """Calculate roof-specific camera position"""
        pass

    @abstractmethod
    def _get_annotation_params(self):
        """Get parameters for RoofAnnotation - roof specific"""
        pass

    @abstractmethod
    def add_attachment_points(self):
        """Generate attachment points for obstacle placement - roof specific"""
        pass

    # ==================== TEXTURE METHODS ====================
    def load_texture_safely(self, filename, default_color="#A9A9A9"):
        """Safely load a texture with fallback to color if loading fails"""
        base_filename = os.path.basename(filename)
        
        possible_paths = [
            filename,  # Original path
            resource_path(filename),  # Original with resource_path
            resource_path(f"PVmizer/textures/{base_filename}"),
            resource_path(f"textures/{base_filename}"),
            resource_path(f"_internal/textures/{base_filename}")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    texture = pv.read_texture(path)
                    return texture, True
                except Exception as e:
                    print(f"Error loading texture from {path}: {e}")
        
        return default_color, False

    # ==================== THEME METHODS ====================
    def set_theme(self, theme):
        """Update the roof's theme and refresh visuals"""
        self.theme = theme
        self.set_plotter_background()
        
        if hasattr(self, 'annotator') and self.annotator:
            self.annotator.set_theme(theme)
        
    def set_plotter_background(self):
        """Set the plotter background based on current theme"""
        if hasattr(self, 'theme') and self.theme == "dark":
            self.plotter.set_background("darkgrey")
        else:
            self.plotter.set_background("lightgrey")

    # ==================== CAMERA METHODS ====================
    def reset_camera(self):
        """Reset camera to default position focusing on roof only"""
        try:
            # Get roof-specific camera position
            position, focal_point, up_vector = self.calculate_camera_position()
            
            # Set camera position
            self.plotter.camera_position = [position, focal_point, up_vector]
            
            # Instead of reset_camera(), manually set the view
            # This prevents including all actors (like sun) in the view calculation
            if hasattr(self, 'roof_mesh') and self.roof_mesh:
                # Focus on roof mesh bounds only
                bounds = self.roof_mesh.bounds
                self.plotter.camera.focal_point = [
                    (bounds[0] + bounds[1]) / 2,
                    (bounds[2] + bounds[3]) / 2,
                    (bounds[4] + bounds[5]) / 2
                ]
                
                # Set appropriate zoom
                size = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
                self.plotter.camera.distance = size * 2.5
            else:
                # Fallback to standard reset but with limited bounds
                self.plotter.reset_camera()
                
        except Exception as e:
            print(f"❌ Camera reset failed: {e}")
            # Fallback
            position, focal_point, up_vector = self.calculate_camera_position()
            self.plotter.camera_position = [position, focal_point, up_vector]

        
    def set_default_camera_view(self):
        """Set camera to the default position"""
        self.reset_camera()

    # ==================== SCREENSHOT METHODS ====================
    def set_screenshot_directory(self, directory):
        """Set the directory where screenshots will be saved"""
        self.screenshot_directory = directory

    def save_roof_screenshot(self):
        """Save current roof view"""
        if hasattr(self, 'screenshot_directory') and self.screenshot_directory:
            snaps_dir = Path(self.screenshot_directory)
        else:
            snaps_dir = Path("RoofSnaps")
        
        snaps_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        roof_type = self.__class__.__name__.lower()
        filename = f"{roof_type}_{timestamp}.png"
        filepath = snaps_dir / filename
        
        try:
            self.plotter.screenshot(str(filepath))
            
            message_actor = self.plotter.add_text(
                _('screenshot_saved').format(filename=filename), 
                position="lower_right",
                font_size=12,
                color="green",
                shadow=True
            )
            
            def remove_message():
                try:
                    self.plotter.remove_actor(message_actor)
                    self.plotter.render()
                except:
                    pass  
            
            QTimer.singleShot(3000, remove_message)
            print(f"Screenshot saved to {filepath}")
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            
            error_actor = self.plotter.add_text(
                _('screenshot_error'),  
                position="lower_right",
                font_size=12,
                color="red",
                shadow=True
            )
            
            def remove_error():
                try:
                    self.plotter.remove_actor(error_actor)
                    self.plotter.render()
                except:
                    pass
            
            QTimer.singleShot(3000, remove_error)

    # ==================== SOLAR PANEL METHODS ====================
    def _initialize_solar_panel_handler(self):
        """Initialize the solar panel handler for this roof type"""
        try:
            handler_class = self.get_solar_panel_handler_class()
            if handler_class:
                self.solar_panel_handler = handler_class(self)
                print(f"✅ {self.__class__.__name__}: Solar panel handler initialized successfully")
            else:
                print(f"⚠️ {self.__class__.__name__}: Solar panel handler class not available")
                self.solar_panel_handler = None
        except Exception as e:
            print(f"❌ {self.__class__.__name__}: Failed to initialize solar panel handler: {e}")
            import traceback
            traceback.print_exc()
            self.solar_panel_handler = None

    def safe_add_panels(self, area):
        """Safely add panels with error checking"""
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            try:
                self.solar_panel_handler.add_panels(area)
                print(f"✅ Added panels to {area} area")
            except Exception as e:
                print(f"❌ Error adding panels to {area}: {e}")
        else:
            print(f"⚠️ Cannot add {area} panels - solar panel handler not available")

    def safe_clear_panels(self):
        """Safely clear panels with error checking"""
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            try:
                self.solar_panel_handler.clear_panels()
                print("✅ Panels cleared")
            except Exception as e:
                print(f"❌ Error clearing panels: {e}")
        else:
            print("⚠️ Cannot clear panels - solar panel handler not available")

    def update_panel_config(self, panel_config):
        """Update solar panel configuration"""
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            try:
                if panel_config:
                    for key, value in panel_config.items():
                        print(f"  {key}: {value}")
                
                self.solar_panel_handler.clear_panels()
                result = self.solar_panel_handler.update_panel_config(panel_config)
                return result
                            
            except Exception as e:
                print(f"Error updating panel configuration: {e}")
                import traceback
                traceback.print_exc()
                return False
        return False

    def update_texts(self):
        """Update all text elements with current language"""
        # Update the plotter
        self.plotter.update()

    # ==================== KEY BINDING METHODS ====================
    def setup_key_bindings(self):
        """Set up key bindings for roof visualization"""
        print(f"🎮 Setting up key bindings. Solar handler available: {self.solar_panel_handler is not None}")
        
        # Setup roof-specific panel placement keys
        self.setup_roof_specific_key_bindings()
        
        # Common key bindings for all roof types
        self.plotter.add_key_event("r", self.reset_camera)
        self.plotter.add_key_event("R", self.reset_camera)
        self.plotter.add_key_event('o', self.clear_obstacles)
        self.plotter.add_key_event('O', self.clear_obstacles)
        self.plotter.add_key_event("s", self.save_roof_screenshot)
        self.plotter.add_key_event("S", self.save_roof_screenshot)
        
        print("✅ Key bindings setup completed")

    def clear_key_bindings(self):
        """Clear all existing key bindings from the plotter"""
        try:
            cleared_count = 0
            
            if hasattr(self.plotter, 'clear_events'):
                self.plotter.clear_events()
                cleared_count += 1
                print("✅ Cleared via clear_events()")
            
            if hasattr(self.plotter, '_key_press_event_callbacks'):
                callback_count = len(self.plotter._key_press_event_callbacks)
                self.plotter._key_press_event_callbacks.clear()
                cleared_count += 1
                print(f"✅ Cleared {callback_count} callbacks from _key_press_event_callbacks")
            
            if hasattr(self.plotter, 'iren'):
                if hasattr(self.plotter.iren, '_key_press_event_callbacks'):
                    callback_count = len(self.plotter.iren._key_press_event_callbacks)
                    self.plotter.iren._key_press_event_callbacks.clear()
                    cleared_count += 1
                    print(f"✅ Cleared {callback_count} callbacks from iren._key_press_event_callbacks")
                
                if hasattr(self.plotter.iren, 'RemoveObservers'):
                    self.plotter.iren.RemoveObservers('KeyPressEvent')
                    cleared_count += 1
                    print("✅ Removed VTK KeyPressEvent observers")
            
            if hasattr(self.plotter, 'renderer'):
                if hasattr(self.plotter.renderer, '_key_press_event_callbacks'):
                    callback_count = len(self.plotter.renderer._key_press_event_callbacks)
                    self.plotter.renderer._key_press_event_callbacks.clear()
                    cleared_count += 1
                    print(f"✅ Cleared {callback_count} callbacks from renderer")
            
            print(f"✅ Key bindings cleared using {cleared_count} methods")
            
        except Exception as e:
            print(f"⚠️ Error clearing key bindings: {e}")
            import traceback
            traceback.print_exc()

    # ==================== OBSTACLE METHODS ====================
    def add_obstacle(self, obstacle_type, dimensions=None):
        """Add a roof obstacle of the specified type with optional dimensions"""
        try:
            if obstacle_type == _('chimney'):
                internal_type = "Chimney"
            elif obstacle_type == _('roof_window'):
                internal_type = "Roof Window" 
            elif obstacle_type == _('ventilation'):
                internal_type = "Ventilation"
            else:
                internal_type = obstacle_type
            
            self.selected_obstacle_type = internal_type
            self.obstacle_dimensions = dimensions
            
            if dimensions is None:
                return self.add_obstacle_button_clicked()
            else:
                if hasattr(self, 'placement_instruction') and self.placement_instruction:
                    self.plotter.remove_actor(self.placement_instruction)
                
                display_name = self.get_translated_obstacle_name(internal_type)
                remaining = 6 - self.obstacle_count
                
                self.placement_instruction = self.plotter.add_text(
                    _('click_to_place') + f" {display_name} " +
                    f"({self.obstacle_count}/6, {remaining} " + _('remaining') + ")",
                    position="lower_left",
                    font_size=12,
                    color="black"
                )
                
                return self.add_attachment_points()
                
        except Exception as e:
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

    def clear_obstacles(self):
        """Remove all obstacles from the roof"""
        if hasattr(self, 'obstacles') and self.obstacles:
            for obstacle in self.obstacles:
                if hasattr(obstacle, 'actor') and obstacle.actor:
                    self.plotter.remove_actor(obstacle.actor)
            
            self.obstacles = []
            self.obstacle_count = 0
            
            if hasattr(self, 'attachment_points_occupied'):
                for idx in self.attachment_points_occupied:
                    self.attachment_points_occupied[idx]['occupied'] = False
                    self.attachment_points_occupied[idx]['obstacle'] = None
            
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

    def add_obstacle_button_clicked(self):
        """Handle 'Add Obstacle' button click"""
        if hasattr(self, 'obstacle_count') and self.obstacle_count >= 6:
            self.update_instruction(_('obstacle_max_reached'))
            return False
            
        dialogs = RoofObstacleDialogs()
        dialogs.show_selection_dialog(self.on_obstacle_selected)
        return True

    def on_obstacle_selected(self, obstacle_type, dimensions):
        """Callback when obstacle type and dimensions are selected"""
        if obstacle_type is None or dimensions is None:
            return
            
        self.selected_obstacle_type = obstacle_type
        self.obstacle_dimensions = dimensions
        self.add_attachment_points()

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

    def find_closest_attachment_point(self, click_point):
        """Find the closest attachment point to the clicked position"""
        if not hasattr(self, 'attachment_points_occupied') or not self.attachment_points_occupied:
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

    # ==================== CLEANUP METHODS ====================
    def cleanup(self):
        """Cleanup method to be called when roof is being replaced"""
        try:
            self.clear_key_bindings()
            
            if hasattr(self, 'solar_panel_handler'):
                self.solar_panel_handler = None
            
            print(f"✅ {self.__class__.__name__} cleanup completed")
        except Exception as e:
            print(f"❌ Error during {self.__class__.__name__} cleanup: {e}")

    # ==================== TEMPLATE METHOD ====================
    def initialize_roof(self, dimensions):
        """
        Template method that orchestrates roof creation
        
        This is the main template method that defines the algorithm
        for initializing any roof type. Subclasses customize behavior
        by implementing the abstract methods.
        """
        # Store dimensions
        self.dimensions = dimensions
        
        # Create roof-specific geometry
        self.create_roof_geometry()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Create annotations
        try:
            annotation_params = self._get_annotation_params()
            self.annotator = RoofAnnotation(
                self.plotter,
                *annotation_params,
                self.theme
            )
            self.annotator.add_annotations()
            print(f"✅ {self.__class__.__name__}: Annotations added successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Could not add annotations: {e}")
            self.annotator = None
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
            print(f"✅ {self.__class__.__name__}: Key bindings set up successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Error setting up key bindings: {e}")
        
        # Set default camera view
        try:
            self.set_default_camera_view()
            print(f"✅ {self.__class__.__name__}: Camera view set successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Could not set camera view: {e}")

        print(f"🏠 {self.__class__.__name__} initialization completed")
