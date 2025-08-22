#!/usr/bin/env python3
"""
roofs/base/base_roof.py
Main base roof class with core functionality
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
from .resource_utils import resource_path
from .environment_manager import EnvironmentManager
from .texture_manager import TextureManager
from .sun_system_manager import SunSystemManager
from .camera_manager import CameraManager

class BaseRoof(ABC):
    """Base class for all roof types with modular components"""
    
    def __init__(self, plotter=None, dimensions=None, theme="light"):
        """Initialize roof with modular managers"""
        print(f"\n🏗️ BaseRoof.__init__ starting for {self.__class__.__name__}")
        
        # Store basic properties
        self.theme = theme
        self.base_height = 3.0
        self.dimensions = dimensions
        self.house_walls = []
        self.base_points = None
        self.building_rotation_angle = 0
        
        # CRITICAL: Ground level coordination
        self.grass_ground_level = -0.05  # Must match sun system
        
        # Setup plotter
        self._setup_plotter(plotter)
        
        # CRITICAL: Find sun system FIRST
        self.sun_system = None
        self._find_and_configure_sun_system()
        
        # Initialize managers
        self.texture_manager = TextureManager(self)
        self.sun_system_manager = SunSystemManager(self)
        
        # Pass already-found sun system to manager
        if self.sun_system:
            self.sun_system_manager.sun_system = self.sun_system
        
        self.environment_manager = EnvironmentManager(self)
        self.camera_manager = CameraManager(self)
        
        # Make environment attributes accessible at root level for compatibility
        self.environment_obstacles = self.environment_manager.environment_obstacles
        self.environment_attachment_points = self.environment_manager.environment_attachment_points
        self.tree_type_index = 0
        
        # Environment interaction state
        self.selected_tree_type = None
        self.selected_pole_type = None
        self.tree_size_multiplier = 1.0
        self.pole_height_multiplier = 1.0
        self.environment_placement_mode = None
        self.attachment_points_visible = False
        self.attachment_points_actor = None
        self._environment_click_callback_id = None
        
        # Clear existing key bindings
        if self.plotter:
            self.clear_key_bindings()
        
        # Initialize roof-specific properties
        self.attachment_points = []
        self.attachment_point_actor = None
        self.obstacles = []
        self.obstacle_count = 0
        self.placement_instruction = None
        self.selected_obstacle_type = None
        self.obstacle_dimensions = None
        self.enable_help_system = False
        self.annotator = None
        
        # Create ground and environment
        self.environment_manager.initialize_environment()
        
        # Update references after environment initialization
        self.ground_mesh = self.environment_manager.ground_mesh
        self.ground_actor = self.environment_manager.ground_actor
        
        # CRITICAL: Tell sun system about ground level
        if self.sun_system and hasattr(self.sun_system, 'set_shadow_height'):
            self.sun_system.set_shadow_height(self.grass_ground_level + 0.02)
        
        # Add axes
        try:
            self.plotter.add_axes()
        except Exception as e:
            print(f"⚠️ Could not add axes: {e}")

        print(f"✅ BaseRoof.__init__ completed for {self.__class__.__name__}")
    
    def _find_and_configure_sun_system(self):
        """Find and properly configure sun system"""
        try:
            print("🔍 Searching for sun system...")
            
            # Method 1: Check if plotter has parent with enhanced_sun_system
            if hasattr(self.plotter, 'parent'):
                parent = self.plotter.parent()
                for _ in range(5):  # Check up hierarchy
                    if parent and hasattr(parent, 'enhanced_sun_system'):
                        self.sun_system = parent.enhanced_sun_system
                        print("✅ Found sun system via plotter parent")
                        break
                    if parent and hasattr(parent, 'parent'):
                        parent = parent.parent()
                    else:
                        break
            
            # Method 2: Check global module reference
            if not self.sun_system:
                try:
                    import sys
                    import ui.tabs.model_tab as model_tab_module
                    if hasattr(model_tab_module, '_global_sun_system'):
                        self.sun_system = model_tab_module._global_sun_system
                        print("✅ Found sun system via global reference")
                except:
                    pass
            
            # Method 3: Check if plotter has model_tab reference
            if not self.sun_system and hasattr(self.plotter, 'model_tab'):
                if hasattr(self.plotter.model_tab, 'enhanced_sun_system'):
                    self.sun_system = self.plotter.model_tab.enhanced_sun_system
                    print("✅ Found sun system via plotter.model_tab")
            
            # Configure sun system if found
            if self.sun_system:
                self._configure_sun_system()
                return True
            else:
                print("⚠️ No sun system found - shadows may not work")
                return False
                
        except Exception as e:
            print(f"❌ Error finding sun system: {e}")
            self.sun_system = None
            return False
    
    def _configure_sun_system(self):
        """Configure sun system with building parameters"""
        try:
            if not self.sun_system:
                return
            
            print("⚙️ Configuring sun system...")
            
            # Calculate building center and dimensions
            building_center = self._calculate_building_center()
            building_dims = self._calculate_building_dimensions()
            
            # Set building center for shadow calculations
            if building_center:
                self.sun_system.set_building_center(building_center)
                print(f"✅ Set building center: {building_center}")
            
            # Set building dimensions
            if building_dims:
                width, length, height, roof_height = building_dims
                self.sun_system.set_building_dimensions(width, length, height, roof_height)
                print(f"✅ Set building dimensions: {width}x{length}x{height} (roof: {roof_height})")
            
            # Set shadow level to match grass
            if hasattr(self.sun_system, 'shadow_level'):
                self.sun_system.shadow_level = self.grass_ground_level + 0.01
                print(f"✅ Set shadow level: {self.sun_system.shadow_level}")
            
            print("✅ Sun system configured successfully")
            
        except Exception as e:
            print(f"❌ Error configuring sun system: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_building_center(self):
        """Calculate building center from roof geometry"""
        try:
            default_center = [0, 0, self.base_height / 2]
            
            if hasattr(self, 'dimensions') and self.dimensions:
                if len(self.dimensions) >= 3:
                    length, width, height = self.dimensions[:3]
                    return [0, 0, self.base_height + height / 2]
            
            elif hasattr(self, 'base_points') and self.base_points:
                points = np.array(self.base_points)
                center_x = np.mean(points[:, 0])
                center_y = np.mean(points[:, 1])
                center_z = self.base_height / 2
                return [center_x, center_y, center_z]
            
            elif hasattr(self, 'apex_height'):
                return [0, 0, self.base_height + self.apex_height / 2]
            
            return default_center
            
        except Exception as e:
            print(f"⚠️ Error calculating building center: {e}")
            return [0, 0, self.base_height / 2]
    
    def _calculate_building_dimensions(self):
        """Calculate building dimensions for shadow calculations"""
        try:
            default_dims = (8.0, 10.0, self.base_height, 4.0)
            
            if hasattr(self, 'dimensions') and self.dimensions and len(self.dimensions) >= 3:
                length, width, height = self.dimensions[:3]
                roof_height = height if len(self.dimensions) < 4 else height
                return (width, length, self.base_height, roof_height)
            
            elif hasattr(self, 'base_points') and self.base_points:
                points = np.array(self.base_points)
                width = np.max(points[:, 0]) - np.min(points[:, 0])
                length = np.max(points[:, 1]) - np.min(points[:, 1])
                roof_height = 2.0
                return (width, length, self.base_height, roof_height)
            
            elif hasattr(self, 'apex_height'):
                return (8.0, 8.0, self.base_height, self.apex_height)
            
            return default_dims
            
        except Exception as e:
            print(f"⚠️ Error calculating building dimensions: {e}")
            return (8.0, 10.0, self.base_height, 4.0)
    
    def update_sun_system_after_changes(self):
        """Update sun system after roof geometry changes"""
        try:
            if not self.sun_system:
                return
            
            print("🔄 Updating sun system after roof changes...")
            
            building_center = self._calculate_building_center()
            building_dims = self._calculate_building_dimensions()
            
            if building_center:
                self.sun_system.set_building_center(building_center)
            
            if building_dims:
                width, length, height, roof_height = building_dims
                self.sun_system.set_building_dimensions(width, length, height, roof_height)
            
            print("✅ Sun system updated after roof changes")
            
        except Exception as e:
            print(f"❌ Error updating sun system: {e}")
    
    def _setup_plotter(self, plotter):
        """Setup plotter with validation"""
        if plotter:
            if hasattr(plotter, 'plotter') and hasattr(plotter.plotter, 'add_mesh'):
                self.plotter = plotter.plotter
                self.external_plotter = True
                print(f"✅ Using QtInteractor.plotter")
            elif hasattr(plotter, 'add_mesh'):
                self.plotter = plotter
                self.external_plotter = True
                print(f"✅ Using PyVista plotter directly")
            else:
                print(f"⚠️ Unknown plotter type, creating new one")
                self.plotter = pv.Plotter()
                self.external_plotter = False
        else:
            self.plotter = pv.Plotter()
            self.external_plotter = False
        
        # Validate required methods
        required_methods = ['add_mesh', 'clear', 'render', 'add_key_event']
        plotter_valid = True
        for method in required_methods:
            if not hasattr(self.plotter, method):
                print(f"❌ Plotter missing method: {method}")
                plotter_valid = False
                break
        
        if not plotter_valid:
            print(f"❌ Creating new plotter due to validation failure")
            self.plotter = pv.Plotter()
            self.external_plotter = False
        
        print(f"✅ Plotter initialized: {type(self.plotter)}")
    
    def load_texture_safely(self, filename, default_color="#A9A9A9"):
        """Load texture safely - delegate to texture manager"""
        return self.texture_manager.load_texture_safely(filename, default_color)
    
    def add_sun_compatible_mesh(self, mesh, **kwargs):
        """Add mesh with proper material properties for sun system"""
        # Force proper lighting parameters
        kwargs['lighting'] = True
        kwargs['smooth_shading'] = True
        
        # Enhanced material properties based on surface type
        mesh_name = kwargs.get('name', '').lower()
        
        if 'foundation' in mesh_name:
            kwargs.setdefault('ambient', 0.3)
            kwargs.setdefault('diffuse', 0.8)
            kwargs.setdefault('specular', 0.05)
            kwargs.setdefault('specular_power', 3)
        elif 'wall' in mesh_name:
            kwargs.setdefault('ambient', 0.35)
            kwargs.setdefault('diffuse', 0.85)
            kwargs.setdefault('specular', 0.05)
            kwargs.setdefault('specular_power', 2)
        elif 'roof' in mesh_name or 'slope' in mesh_name:
            kwargs.setdefault('ambient', 0.3)
            kwargs.setdefault('diffuse', 0.9)
            kwargs.setdefault('specular', 0.1)
            kwargs.setdefault('specular_power', 8)
        elif 'gable' in mesh_name:
            kwargs.setdefault('ambient', 0.4)
            kwargs.setdefault('diffuse', 0.85)
            kwargs.setdefault('specular', 0.05)
            kwargs.setdefault('specular_power', 2)
        elif 'ground' in mesh_name:
            # CRITICAL: Ground should NOT cast shadows - only receive them
            kwargs.setdefault('ambient', 0.4)
            kwargs.setdefault('diffuse', 0.95)  # Very high for shadow contrast
            kwargs.setdefault('specular', 0.0)
            kwargs.setdefault('specular_power', 1)
            kwargs['pickable'] = False  # Not pickable for performance
        else:
            kwargs.setdefault('ambient', 0.25)
            kwargs.setdefault('diffuse', 0.8)
            kwargs.setdefault('specular', 0.1)
            kwargs.setdefault('specular_power', 5)
        
        # Add mesh
        actor = self.plotter.add_mesh(mesh, **kwargs)
        
        # Register with sun system if available (but NOT ground)
        if self.sun_system and hasattr(self.sun_system, 'register_scene_object'):
            name = kwargs.get('name', 'unnamed')
            # CRITICAL: Don't register ground plane for shadow casting
            if 'ground' not in name.lower():
                self.sun_system.register_scene_object(mesh, name, cast_shadow=True)
                print(f"✅ Registered '{name}' with sun system")
        
        return actor
    
    def create_building_walls(self, base_points, height):
        """Create building walls with textures"""
        try:
            print(f"🏗️ Creating {len(base_points)} walls with height {height}")
            
            # Calculate texture scaling
            texture_scale_factor = self.texture_manager.calculate_texture_scale()
            
            # Load wall texture
            wall_texture, wall_loaded = self.texture_manager.load_texture_safely(
                self.texture_manager.brick_texture_file,
                self.texture_manager.default_wall_color
            )
            
            # Clear existing walls
            for wall in self.house_walls:
                try:
                    self.plotter.remove_actor(wall)
                except:
                    pass
            self.house_walls.clear()
            
            # Create each wall
            for i in range(len(base_points)):
                next_i = (i + 1) % len(base_points)
                
                # Wall vertices
                wall_verts = np.array([
                    [base_points[i][0], base_points[i][1], 0],
                    [base_points[next_i][0], base_points[next_i][1], 0],
                    [base_points[next_i][0], base_points[next_i][1], height],
                    [base_points[i][0], base_points[i][1], height]
                ])
                
                # Create wall mesh
                wall = pv.PolyData(wall_verts)
                wall.faces = np.array([4, 0, 1, 2, 3])
                wall.compute_normals(inplace=True, auto_orient_normals=True)
                
                # Add texture coordinates
                wall_length = np.linalg.norm(np.array(base_points[next_i]) - np.array(base_points[i]))
                u_scale = wall_length * texture_scale_factor / 2.0
                v_scale = height * texture_scale_factor / 2.0
                
                texture_coords = np.array([
                    [0, 0], [u_scale, 0], [u_scale, v_scale], [0, v_scale]
                ])
                wall.active_t_coords = texture_coords
                
                # Add wall
                if wall_loaded:
                    wall_actor = self.add_sun_compatible_mesh(
                        wall, texture=wall_texture, name=f'building_wall_{i}'
                    )
                else:
                    wall_actor = self.add_sun_compatible_mesh(
                        wall, color=self.texture_manager.default_wall_color,
                        name=f'building_wall_{i}'
                    )
                
                if wall_actor:
                    self.house_walls.append(wall_actor)
            
            self.base_points = base_points
            print(f"✅ Created {len(self.house_walls)} walls")
            
        except Exception as e:
            print(f"❌ Error creating walls: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== ENVIRONMENT TAB CONNECTION ====================
    
    def handle_environment_action(self, action_type, parameters):
        """Main handler for environment actions from EnvironmentTab - routes to environment manager"""
        try:
            print(f"🎯 BaseRoof handling environment action: {action_type}")
            
            # Route all environment actions to the environment manager
            self.environment_manager.handle_environment_action(action_type, parameters)
            
            # Update root level references after action
            self.environment_obstacles = self.environment_manager.environment_obstacles
            self.environment_attachment_points = self.environment_manager.environment_attachment_points
            
            # Force render after any environment action
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                
        except Exception as e:
            print(f"❌ Error handling environment action {action_type}: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== ENVIRONMENT METHODS ====================
    
    def add_environment_obstacle_at_point(self, obstacle_type, point_index=None):
        """Add environmental obstacle - SINGLE OBJECT ONLY"""
        result = self.environment_manager.add_environment_obstacle_at_point(obstacle_type, point_index)
        # Update root level references
        self.environment_obstacles = self.environment_manager.environment_obstacles
        return result
    
    def clear_environment_obstacles(self):
        """Clear all environment obstacles"""
        self.environment_manager.clear_environment_obstacles()
        # Update root level references
        self.environment_obstacles = self.environment_manager.environment_obstacles
        
        # CLEAR ENVIRONMENT OBJECTS FROM SUN SYSTEM
        if self.sun_system and hasattr(self.sun_system, 'clear_environment_objects'):
            self.sun_system.clear_environment_objects()
            # Force shadow update
            if hasattr(self.sun_system, '_update_shadows_only'):
                self.sun_system._update_shadows_only()
    
    def show_environment_attachment_points(self):
        """Show environment attachment points"""
        self.environment_manager.show_environment_attachment_points()
        self.attachment_points_visible = True
    
    def hide_environment_attachment_points(self):
        """Hide environment attachment points"""
        self.environment_manager.hide_environment_attachment_points()
        self.attachment_points_visible = False
    
    # ==================== CAMERA METHODS ====================
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.camera_manager.reset_camera()
    
    def set_default_camera_view(self):
        """Set camera to the default position"""
        self.camera_manager.set_default_camera_view()
    
    def set_screenshot_directory(self, directory):
        """Set screenshot directory"""
        self.camera_manager.set_screenshot_directory(directory)
    
    def save_roof_screenshot(self):
        """Save current roof view"""
        self.camera_manager.save_roof_screenshot()
    
    # ==================== KEY BINDINGS ====================
    
    def setup_key_bindings(self):
        """Set up key bindings INCLUDING 7, 8, 9 for environment objects"""
        print(f"🎮 Setting up key bindings...")
        
        # Roof-specific bindings
        self.setup_roof_specific_key_bindings()
        
        # Standard key bindings
        self.plotter.add_key_event("r", self.reset_camera)
        self.plotter.add_key_event("R", self.reset_camera)
        self.plotter.add_key_event('o', self.clear_obstacles)
        self.plotter.add_key_event('O', self.clear_obstacles)
        self.plotter.add_key_event("s", self.save_roof_screenshot)
        self.plotter.add_key_event("S", self.save_roof_screenshot)
        
        # NEW: Number keys for environment objects - SINGLE SPAWNS ONLY
        def add_pine_tree():
            """Key 7: Add ONE pine tree"""
            self.tree_type_index = 1  # Set to pine
            self.add_environment_obstacle_at_point('tree')
        
        def add_deciduous_tree():
            """Key 8: Add ONE deciduous/leaf tree"""
            self.tree_type_index = 0  # Set to deciduous
            self.add_environment_obstacle_at_point('tree')
        
        def add_pole():
            """Key 9: Add ONE pole"""
            self.add_environment_obstacle_at_point('pole')
        
        # Bind number keys
        self.plotter.add_key_event("7", add_pine_tree)
        self.plotter.add_key_event("8", add_deciduous_tree)
        self.plotter.add_key_event("9", add_pole)
        
        # Clear environment
        self.plotter.add_key_event("e", self.clear_environment_obstacles)
        self.plotter.add_key_event("E", self.clear_environment_obstacles)
        
        print("✅ Key bindings setup completed")
        print("   7: Add pine tree")
        print("   8: Add deciduous tree")
        print("   9: Add pole")
        print("   e/E: Clear environment")
        print("   r/R: Reset camera")
        print("   o/O: Clear obstacles")
        print("   s/S: Save screenshot")
    
    def clear_key_bindings(self):
        """Clear all existing key bindings"""
        try:
            cleared_count = 0
            
            if hasattr(self.plotter, 'clear_events'):
                self.plotter.clear_events()
                cleared_count += 1
            
            if hasattr(self.plotter, '_key_press_event_callbacks'):
                self.plotter._key_press_event_callbacks.clear()
                cleared_count += 1
            
            if hasattr(self.plotter, 'iren'):
                if hasattr(self.plotter.iren, '_key_press_event_callbacks'):
                    self.plotter.iren._key_press_event_callbacks.clear()
                    cleared_count += 1
                
                if hasattr(self.plotter.iren, 'RemoveObservers'):
                    self.plotter.iren.RemoveObservers('KeyPressEvent')
                    cleared_count += 1
            
            print(f"✅ Key bindings cleared using {cleared_count} methods")
            
        except Exception as e:
            print(f"⚠️ Error clearing key bindings: {e}")
    
    # ==================== OBSTACLE MANAGEMENT ====================
    
    def add_obstacle(self, obstacle_type, dimensions=None):
        """Add a roof obstacle"""
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
    
    def clear_obstacles(self):
        """Remove all obstacles"""
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
    
    def get_translated_obstacle_name(self, obstacle_type):
        """Get translated name"""
        if obstacle_type == "Chimney":
            return _('chimney')
        elif obstacle_type == "Roof Window":
            return _('roof_window')
        elif obstacle_type == "Ventilation":
            return _('ventilation')
        else:
            return obstacle_type
    
    def update_instruction(self, message):
        """Update instruction text"""
        if hasattr(self, 'placement_instruction') and self.placement_instruction:
            self.plotter.remove_actor(self.placement_instruction)
        
        self.placement_instruction = self.plotter.add_text(
            message,
            position="lower_left",
            font_size=12,
            color="black"
        )
    
    def add_obstacle_button_clicked(self):
        """Handle obstacle button click"""
        if hasattr(self, 'obstacle_count') and self.obstacle_count >= 6:
            self.update_instruction(_('obstacle_max_reached'))
            return False
            
        dialogs = RoofObstacleDialogs()
        dialogs.show_selection_dialog(self.on_obstacle_selected)
        return True
    
    def on_obstacle_selected(self, obstacle_type, dimensions):
        """Callback when obstacle selected"""
        if obstacle_type is None or dimensions is None:
            return
            
        self.selected_obstacle_type = obstacle_type
        self.obstacle_dimensions = dimensions
        self.add_attachment_points()
    
    def place_obstacle_at_point(self, point, obstacle_type, normal_vector=None, roof_point=None, face=None):
        """Place obstacle at point"""
        dimensions = None
        if hasattr(self, 'obstacle_dimensions'):
            dimensions = self.obstacle_dimensions
        
        obstacle = RoofObstacle(
            obstacle_type, 
            point, 
            self, 
            dimensions=dimensions,
            normal_vector=normal_vector,
            roof_point=roof_point,
            face=face
        )
        
        obstacle.add_to_plotter(self.plotter)
        return obstacle
    
    def is_point_occupied(self, point):
        """Check if point is occupied"""
        if not hasattr(self, 'obstacles') or not self.obstacles:
            return False
            
        min_distance = 0.2
        
        for obstacle in self.obstacles:
            if hasattr(obstacle, 'position'):
                distance = np.linalg.norm(np.array(obstacle.position) - np.array(point))
                if distance < min_distance:
                    return True
                    
        return False
    
    def find_closest_attachment_point(self, click_point):
        """Find closest attachment point"""
        if not hasattr(self, 'attachment_points_occupied') or not self.attachment_points_occupied:
            return None, None
            
        min_distance = float('inf')
        closest_idx = None
        closest_point = None
        
        click_point_array = np.array(click_point)
        
        for idx, point_data in self.attachment_points_occupied.items():
            point = point_data['position']
            distance = np.linalg.norm(np.array(point) - click_point_array)
            
            if distance < min_distance:
                min_distance = distance
                closest_idx = idx
                closest_point = point
        
        return closest_idx, closest_point
    
    # ==================== SOLAR PANEL METHODS ====================
    
    def _initialize_solar_panel_handler(self):
        """Initialize the solar panel handler"""
        try:
            handler_class = self.get_solar_panel_handler_class()
            if handler_class:
                self.solar_panel_handler = handler_class(self)
                print(f"✅ Solar panel handler initialized")
            else:
                print(f"⚠️ Solar panel handler class not available")
                self.solar_panel_handler = None
        except Exception as e:
            print(f"❌ Failed to initialize solar panel handler: {e}")
            self.solar_panel_handler = None
    
    def safe_add_panels(self, area):
        """Safely add panels"""
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            try:
                self.solar_panel_handler.add_panels(area)
                print(f"✅ Added panels to {area} area")
            except Exception as e:
                print(f"❌ Error adding panels to {area}: {e}")
        else:
            print(f"⚠️ Cannot add {area} panels - handler not available")
    
    def safe_clear_panels(self):
        """Safely clear panels"""
        if hasattr(self, 'solar_panel_handler') and self.solar_panel_handler:
            try:
                self.solar_panel_handler.clear_panels()
                print("✅ Panels cleared")
            except Exception as e:
                print(f"❌ Error clearing panels: {e}")
        else:
            print("⚠️ Cannot clear panels - handler not available")
    
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
                return False
        return False
    
    # ==================== UTILITY METHODS ====================
    
    def set_theme(self, theme):
        """Update the roof's theme"""
        self.theme = theme
        if hasattr(self, 'annotator') and self.annotator:
            self.annotator.set_theme(theme)
    
    def update_texts(self):
        """Update all text elements"""
        self.plotter.update()
    
    def update_lighting_for_building_rotation(self, rotation_angle):
        """Update for building rotation"""
        self.building_rotation_angle = rotation_angle
        print(f"🔄 Building rotation updated to: {rotation_angle}°")
        
        # Update sun system after rotation
        self.update_sun_system_after_changes()
        
        if hasattr(self.plotter, 'render'):
            self.plotter.render()
    
    def cleanup(self):
        """Cleanup method"""
        try:
            self.clear_key_bindings()
            
            # Cleanup managers
            self.environment_manager.cleanup()
            self.sun_system_manager.cleanup()
            
            if hasattr(self, 'solar_panel_handler'):
                self.solar_panel_handler = None
            
            # Don't cleanup sun system here as it's shared
            self.sun_system = None
            
            print(f"✅ {self.__class__.__name__} cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def initialize_roof(self, dimensions):
        """Initialize roof with proper sun system integration"""
        # Store dimensions
        self.dimensions = dimensions
        
        # Reinitialize environment with new dimensions
        self.environment_manager.reinitialize_for_dimensions(dimensions)
        
        # Update root level references
        self.ground_mesh = self.environment_manager.ground_mesh
        self.ground_actor = self.environment_manager.ground_actor
        
        # Create roof-specific geometry
        self.create_roof_geometry()
        
        # IMPORTANT: Update sun system after geometry is created
        self.update_sun_system_after_changes()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
        except Exception as e:
            print(f"⚠️ Error setting up key bindings: {e}")
        
        # Set default camera view
        try:
            self.set_default_camera_view()
        except Exception as e:
            print(f"⚠️ Could not set camera view: {e}")

        print(f"🏠 {self.__class__.__name__} initialized with environment and shadows")
    
    # ==================== ABSTRACT METHODS ====================
    @abstractmethod
    def create_roof_geometry(self):
        """Create the specific roof geometry"""
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
        """Get parameters for RoofAnnotation"""
        pass

    @abstractmethod
    def add_attachment_points(self):
        """Generate attachment points for obstacle placement"""
        pass
