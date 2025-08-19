#!/usr/bin/env python3
"""
roofs/base/base_roof.py - COMPLETE FIXED VERSION
Proper sun system integration and texture loading
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

class BaseRoof(ABC):
    """COMPLETE FIXED: Base class with proper sun system integration and texture loading"""
    
    def __init__(self, plotter=None, dimensions=None, theme="light"):
        """Initialize roof with proper sun coordination"""
        print(f"\n🏗️ BaseRoof.__init__ starting for {self.__class__.__name__}")
        
        # Store basic properties
        self.theme = theme
        self.base_height = 3.0
        self.ground_size = 30.0
        self.house_walls = []
        self.ground_mesh = None
        self.environment_obstacles = []
        self.environment_attachment_points = []
        self.tree_type_index = 0
        
        # CRITICAL: Ground level coordination with sun system
        self.grass_ground_level = -0.05  # Must match sun system
        
        # Building rotation tracking
        self.building_rotation_angle = 0
        
        # Setup plotter
        self._setup_plotter(plotter)
        
        # ENHANCED: Find and configure sun system
        self.sun_system = None
        self._find_and_configure_sun_system()
        
        # Clear existing key bindings
        if self.plotter:
            self.clear_key_bindings()
        
        # Initialize common properties
        self.attachment_points = []
        self.attachment_point_actor = None
        self.obstacles = []
        self.obstacle_count = 0
        self.placement_instruction = None
        self.selected_obstacle_type = None
        self.obstacle_dimensions = None
        self.enable_help_system = False
        self.annotator = None
        
        # Setup textures with proper paths
        self._setup_textures()
        
        # Create grass ground with proper coordination
        self._create_coordinated_grass_ground()
        
        # Create environment attachment points
        self._create_environment_attachment_points()
        
        # Store base points for building creation
        self.base_points = None
        
        # Add axes
        try:
            self.plotter.add_axes()
        except Exception as e:
            print(f"⚠️ Could not add axes: {e}")

        print(f"✅ BaseRoof.__init__ completed for {self.__class__.__name__}")
    
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
    
    def _find_and_configure_sun_system(self):
        """ENHANCED: Find and properly configure sun system"""
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
            # Default center if no specific geometry
            default_center = [0, 0, self.base_height / 2]
            
            # Try to get center from current roof class
            if hasattr(self, 'dimensions') and self.dimensions:
                # For roofs with dimensions (like GableRoof)
                if len(self.dimensions) >= 3:
                    length, width, height = self.dimensions[:3]
                    return [0, 0, self.base_height + height / 2]
            
            elif hasattr(self, 'base_points') and self.base_points:
                # For roofs with base points (like FlatRoof)
                points = np.array(self.base_points)
                center_x = np.mean(points[:, 0])
                center_y = np.mean(points[:, 1])
                center_z = self.base_height / 2
                return [center_x, center_y, center_z]
            
            elif hasattr(self, 'apex_height'):
                # For pyramid roofs
                return [0, 0, self.base_height + self.apex_height / 2]
            
            return default_center
            
        except Exception as e:
            print(f"⚠️ Error calculating building center: {e}")
            return [0, 0, self.base_height / 2]
    
    def _calculate_building_dimensions(self):
        """Calculate building dimensions for shadow calculations"""
        try:
            # Default dimensions
            default_dims = (8.0, 10.0, self.base_height, 4.0)
            
            # Try to get dimensions from current roof class
            if hasattr(self, 'dimensions') and self.dimensions and len(self.dimensions) >= 3:
                # For GableRoof and similar
                length, width, height = self.dimensions[:3]
                roof_height = height if len(self.dimensions) < 4 else height
                return (width, length, self.base_height, roof_height)
            
            elif hasattr(self, 'base_points') and self.base_points:
                # Calculate from base points
                points = np.array(self.base_points)
                width = np.max(points[:, 0]) - np.min(points[:, 0])
                length = np.max(points[:, 1]) - np.min(points[:, 1])
                roof_height = 2.0  # Default roof height for flat roofs
                return (width, length, self.base_height, roof_height)
            
            elif hasattr(self, 'apex_height'):
                # For pyramid roofs
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
            
            # Recalculate and update building parameters
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
    
    def _setup_textures(self):
        """FIXED: Setup texture paths with proper fallback locations"""
        # Try multiple possible texture directory locations
        possible_texture_dirs = [
            "PVmizer GEO/textures",
            "textures",
            "_internal/textures",
            os.path.join(os.path.dirname(__file__), "..", "..", "textures"),
            os.path.join(os.path.dirname(__file__), "..", "..", "PVmizer GEO", "textures"),
            os.path.join(os.getcwd(), "textures"),
            os.path.join(os.getcwd(), "PVmizer GEO", "textures")
        ]
        
        texture_dir = None
        for dir_path in possible_texture_dirs:
            full_path = resource_path(dir_path)
            if os.path.exists(full_path):
                texture_dir = full_path
                print(f"✅ Found texture directory: {texture_dir}")
                break
        
        if not texture_dir:
            # Use the first path as default even if it doesn't exist
            texture_dir = resource_path("textures")
            print(f"⚠️ No texture directory found, using default: {texture_dir}")
        
        # House textures
        self.wall_texture_file = os.path.join(texture_dir, "wall.jpg")
        self.brick_texture_file = os.path.join(texture_dir, "brick.jpg")
        self.roof_tile_texture_file = os.path.join(texture_dir, "roof_tiles.jpg")
        
        # Environment textures
        self.grass_texture_file = os.path.join(texture_dir, "grass.png")
        self.concrete_texture_file = os.path.join(texture_dir, "concrete.jpg")
        
        # Tree textures
        self.leaf_texture_file = os.path.join(texture_dir, "leaf.jpg")
        self.pine_texture_file = os.path.join(texture_dir, "pine.jpg")
        self.leaf_bark_texture_file = os.path.join(texture_dir, "leaf_stomp.jpg")
        self.pine_bark_texture_file = os.path.join(texture_dir, "pine_stomp.jpg")
        
        # Default colors (used when textures aren't available)
        self.default_wall_color = "#F5E6D3"      
        self.default_roof_color = "#C08040"      
        self.default_grass_color = "#6BCD6B"     
        self.default_concrete_color = "#D0D0D0"  
        self.default_leaf_color = "#85D685"      
        self.default_pine_color = "#5A9A5A"      
        self.default_bark_color = "#B08060"
        
        print("✅ Texture paths configured")

    def load_texture_safely(self, filename, default_color="#A9A9A9"):
        """ENHANCED: Safely load texture with comprehensive fallback"""
        if not filename:
            print(f"⚠️ No filename provided, using default color")
            return default_color, False
        
        base_filename = os.path.basename(filename)
        
        # Try the direct path first
        if os.path.exists(filename):
            try:
                texture = pv.read_texture(filename)
                print(f"✅ Loaded texture: {base_filename}")
                return texture, True
            except Exception as e:
                print(f"❌ Error loading texture {base_filename}: {e}")
        
        # Try alternative extensions
        name_without_ext = os.path.splitext(base_filename)[0]
        alternative_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        for ext in alternative_extensions:
            alt_filename = os.path.join(os.path.dirname(filename), name_without_ext + ext)
            if os.path.exists(alt_filename):
                try:
                    texture = pv.read_texture(alt_filename)
                    print(f"✅ Loaded alternative texture: {name_without_ext}{ext}")
                    return texture, True
                except Exception as e:
                    print(f"❌ Error loading alternative texture: {e}")
        
        # Try in current working directory
        cwd_path = os.path.join(os.getcwd(), base_filename)
        if os.path.exists(cwd_path):
            try:
                texture = pv.read_texture(cwd_path)
                print(f"✅ Loaded texture from CWD: {base_filename}")
                return texture, True
            except Exception as e:
                print(f"❌ Error loading texture from CWD: {e}")
        
        print(f"⚠️ Texture not found: {base_filename}, using default color: {default_color}")
        return default_color, False

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
            # Optimized for shadow receiving
            kwargs.setdefault('ambient', 0.4)
            kwargs.setdefault('diffuse', 0.95)  # Very high for shadow contrast
            kwargs.setdefault('specular', 0.0)
            kwargs.setdefault('specular_power', 1)
        else:
            kwargs.setdefault('ambient', 0.25)
            kwargs.setdefault('diffuse', 0.8)
            kwargs.setdefault('specular', 0.1)
            kwargs.setdefault('specular_power', 5)
        
        # Add mesh
        actor = self.plotter.add_mesh(mesh, **kwargs)
        
        # Register with sun system if available
        if self.sun_system and hasattr(self.sun_system, 'register_scene_object'):
            name = kwargs.get('name', 'unnamed')
            self.sun_system.register_scene_object(mesh, name, cast_shadow=True)
            print(f"✅ Registered '{name}' with sun system")
        
        return actor

    def _create_coordinated_grass_ground(self):
        """Create grass ground with coordinated level for shadows"""
        try:
            ground_size = self.ground_size
            z_level = self.grass_ground_level
            
            print(f"🌱 Creating coordinated grass at level: {z_level:.3f}")
            
            # Create ground mesh with high resolution for shadows
            resolution = 100
            x = np.linspace(-ground_size/2, ground_size/2, resolution)
            y = np.linspace(-ground_size/2, ground_size/2, resolution)
            x, y = np.meshgrid(x, y)
            
            # Flat ground for proper shadows
            z = np.ones_like(x) * z_level
            
            # Create mesh
            points = np.c_[x.ravel(), y.ravel(), z.ravel()]
            self.ground_mesh = pv.PolyData(points)
            self.ground_mesh = self.ground_mesh.delaunay_2d()
            
            # CRITICAL: Compute normals for proper lighting
            self.ground_mesh.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Generate texture coordinates
            texture_scale = 8.0
            texture_coords = np.zeros((self.ground_mesh.n_points, 2))
            for i in range(self.ground_mesh.n_points):
                point = self.ground_mesh.points[i]
                u = (point[0] + ground_size/2) / ground_size * texture_scale
                v = (point[1] + ground_size/2) / ground_size * texture_scale
                texture_coords[i] = [u, v]
            
            self.ground_mesh.active_t_coords = texture_coords
            
            # Load texture
            grass_texture, texture_loaded = self.load_texture_safely(
                self.grass_texture_file, 
                self.default_grass_color
            )
            
            # Add with shadow-optimized lighting
            if texture_loaded:
                self.add_sun_compatible_mesh(
                    self.ground_mesh,
                    texture=grass_texture,
                    name="ground_plane"
                )
            else:
                self.add_sun_compatible_mesh(
                    self.ground_mesh,
                    color=self.default_grass_color,
                    name="ground_plane"
                )
            
            print(f"✅ Coordinated grass ground created at {z_level:.3f}")
            
        except Exception as e:
            print(f"❌ Error creating grass ground: {e}")
            import traceback
            traceback.print_exc()

    def create_building_walls(self, base_points, height):
        """Create building walls with ENHANCED LIGHTING"""
        try:
            print(f"🏗️ Creating {len(base_points)} walls with height {height}")
            
            # Load wall texture
            wall_texture, wall_loaded = self.load_texture_safely(
                self.brick_texture_file,
                self.default_wall_color
            )
            
            # Clear existing walls
            for wall in self.house_walls:
                try:
                    self.plotter.remove_actor(wall)
                except:
                    pass
            self.house_walls.clear()
            
            # Create each wall with ENHANCED LIGHTING
            for i in range(len(base_points)):
                next_i = (i + 1) % len(base_points)
                
                # Wall vertices (counter-clockwise for outward normals)
                wall_verts = np.array([
                    [base_points[i][0], base_points[i][1], 0],
                    [base_points[next_i][0], base_points[next_i][1], 0],
                    [base_points[next_i][0], base_points[next_i][1], height],
                    [base_points[i][0], base_points[i][1], height]
                ])
                
                # Create wall mesh
                wall = pv.PolyData(wall_verts)
                wall.faces = np.array([4, 0, 1, 2, 3])
                
                # CRITICAL: Compute normals for proper lighting
                wall.compute_normals(inplace=True, auto_orient_normals=True)
                
                # Add texture coordinates for walls
                wall_length = np.linalg.norm(np.array(base_points[next_i]) - np.array(base_points[i]))
                texture_coords = np.array([
                    [0, 0],  # Bottom left
                    [wall_length, 0],  # Bottom right
                    [wall_length, height],  # Top right
                    [0, height]  # Top left
                ])
                wall.active_t_coords = texture_coords
                
                # Add wall with sun-compatible lighting
                if wall_loaded:
                    wall_actor = self.add_sun_compatible_mesh(
                        wall,
                        texture=wall_texture,
                        name=f'building_wall_{i}'
                    )
                else:
                    wall_actor = self.add_sun_compatible_mesh(
                        wall,
                        color=self.default_wall_color,
                        name=f'building_wall_{i}'
                    )
                
                if wall_actor:
                    self.house_walls.append(wall_actor)
            
            # Store base points for later use
            self.base_points = base_points
            
            print(f"✅ Created {len(self.house_walls)} walls with enhanced lighting")
            
        except Exception as e:
            print(f"❌ Error creating walls: {e}")
            import traceback
            traceback.print_exc()

    def _create_environment_attachment_points(self):
        """Create attachment points around the building"""
        try:
            building_buffer = 7.0
            angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
            radius = building_buffer + 3.0
            
            for angle in angles:
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                self.environment_attachment_points.append({
                    'position': [x, y, 0],
                    'occupied': False,
                    'obstacle': None
                })
            
            # Add outer points
            outer_radius = building_buffer + 6.0
            outer_angles = np.linspace(np.pi/8, 2*np.pi, 8, endpoint=False)
            
            for angle in outer_angles:
                x = outer_radius * np.cos(angle)
                y = outer_radius * np.sin(angle)
                self.environment_attachment_points.append({
                    'position': [x, y, 0],
                    'occupied': False,
                    'obstacle': None
                })
            
            print(f"✅ Created {len(self.environment_attachment_points)} attachment points")
            
        except Exception as e:
            print(f"❌ Error creating attachment points: {e}")

    def show_environment_attachment_points(self):
        """Visualize attachment points"""
        try:
            points = []
            for point_data in self.environment_attachment_points:
                if not point_data['occupied']:
                    points.append(point_data['position'])
            
            if points:
                points_array = np.array(points)
                point_cloud = pv.PolyData(points_array)
                
                self.plotter.add_mesh(
                    point_cloud,
                    color='green',
                    point_size=10,
                    render_points_as_spheres=True,
                    name="env_attachment_points"
                )
                
                print(f"✅ Showing {len(points)} available points")
                
        except Exception as e:
            print(f"❌ Error showing points: {e}")

    def hide_environment_attachment_points(self):
        """Hide attachment points"""
        try:
            self.plotter.remove_actor("env_attachment_points")
        except:
            pass

    def add_environment_obstacle_at_point(self, obstacle_type, point_index=None):
        """Add environmental obstacle"""
        try:
            if point_index is None:
                available_points = [i for i, p in enumerate(self.environment_attachment_points) 
                                  if not p['occupied']]
                if not available_points:
                    print("⚠️ No available points")
                    return False
                
                import random
                point_index = random.choice(available_points)
            
            if point_index >= len(self.environment_attachment_points):
                print(f"⚠️ Invalid point index: {point_index}")
                return False
            
            point_data = self.environment_attachment_points[point_index]
            if point_data['occupied']:
                print(f"⚠️ Point {point_index} is occupied")
                return False
            
            position = point_data['position']
            
            if obstacle_type == 'tree':
                tree_types = ['deciduous', 'pine', 'oak']
                tree_type = tree_types[self.tree_type_index % len(tree_types)]
                self.tree_type_index += 1
                obstacle = self._add_clean_tree(position[:2], tree_type)
            elif obstacle_type == 'pole':
                obstacle = self._add_clean_pole(position[:2])
            else:
                print(f"⚠️ Unknown obstacle type: {obstacle_type}")
                return False
            
            point_data['occupied'] = True
            point_data['obstacle'] = obstacle
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding obstacle: {e}")
            return False

    def _generate_sphere_texture_coordinates(self, mesh, center, radius):
        """Generate texture coordinates for spheres"""
        try:
            points = mesh.points
            texture_coords = np.zeros((points.shape[0], 2))
            
            for i, point in enumerate(points):
                dx = point[0] - center[0]
                dy = point[1] - center[1]
                dz = point[2] - center[2]
                
                length = np.sqrt(dx*dx + dy*dy + dz*dz)
                if length > 0:
                    dx /= length
                    dy /= length
                    dz /= length
                
                theta = np.arctan2(dy, dx)
                phi = np.arccos(np.clip(dz, -1.0, 1.0))
                
                u = (theta + np.pi) / (2 * np.pi)
                v = phi / np.pi
                
                texture_coords[i] = [u * 4, v * 4]
            
            return texture_coords
            
        except Exception as e:
            print(f"❌ Error generating texture coordinates: {e}")
            return np.zeros((points.shape[0], 2))

    def _add_clean_tree(self, position, tree_type='deciduous'):
        """Add tree with proper lighting"""
        try:
            x, y = position
            
            # Create trunk
            if tree_type == 'pine':
                trunk_height = 2.5
                trunk_radius = 0.3
            elif tree_type == 'oak':
                trunk_height = 3.0
                trunk_radius = 0.4
            else:  # deciduous
                trunk_height = 3.5
                trunk_radius = 0.35
            
            trunk = pv.Cylinder(
                center=(x, y, trunk_height/2),
                direction=(0, 0, 1),
                radius=trunk_radius,
                height=trunk_height,
                resolution=20
            )
            trunk.compute_normals(inplace=True, auto_orient_normals=True)
            
            bark_texture, bark_loaded = self.load_texture_safely(
                self.leaf_bark_texture_file if tree_type != 'pine' else self.pine_bark_texture_file,
                self.default_bark_color
            )
            
            # Add trunk
            if bark_loaded:
                self.add_sun_compatible_mesh(
                    trunk,
                    texture=bark_texture,
                    name=f"{tree_type}_trunk_{len(self.environment_obstacles)}"
                )
            else:
                self.add_sun_compatible_mesh(
                    trunk,
                    color=self.default_bark_color,
                    name=f"{tree_type}_trunk_{len(self.environment_obstacles)}"
                )
            
            # Create crown
            if tree_type == 'pine':
                # Pine layers
                layers = [
                    (0.5, 2.2, 0.8), (1.2, 1.9, 0.8), (1.9, 1.6, 0.8),
                    (2.6, 1.3, 0.7), (3.2, 1.0, 0.7)
                ]
                
                pine_texture, pine_loaded = self.load_texture_safely(
                    self.pine_texture_file,
                    self.default_pine_color
                )
                
                for layer_idx, (h_offset, radius, thickness) in enumerate(layers):
                    layer = pv.Cylinder(
                        center=(x, y, trunk_height + h_offset),
                        direction=(0, 0, 1),
                        radius=radius,
                        height=thickness,
                        resolution=30,
                        capping=True
                    )
                    layer.compute_normals(inplace=True, auto_orient_normals=True)
                    
                    if pine_loaded:
                        self.add_sun_compatible_mesh(
                            layer,
                            texture=pine_texture,
                            name=f"pine_crown_{len(self.environment_obstacles)}_layer_{layer_idx}"
                        )
                    else:
                        self.add_sun_compatible_mesh(
                            layer,
                            color=self.default_pine_color,
                            name=f"pine_crown_{len(self.environment_obstacles)}_layer_{layer_idx}"
                        )
                
                tree_height = trunk_height + 5
                
            else:  # deciduous or oak
                crown_height = trunk_height + (2 if tree_type == 'oak' else 1.5)
                crown_radius = 3.5 if tree_type == 'oak' else 2.5
                
                crown = pv.Sphere(
                    center=(x, y, crown_height),
                    radius=crown_radius,
                    theta_resolution=35,
                    phi_resolution=35
                )
                
                texture_coords = self._generate_sphere_texture_coordinates(
                    crown, (x, y, crown_height), crown_radius
                )
                crown.active_t_coords = texture_coords
                crown.compute_normals(inplace=True, auto_orient_normals=True)
                
                leaf_texture, leaf_loaded = self.load_texture_safely(
                    self.leaf_texture_file,
                    "#7EA040" if tree_type == 'oak' else self.default_leaf_color
                )
                
                if leaf_loaded:
                    self.add_sun_compatible_mesh(
                        crown,
                        texture=leaf_texture,
                        name=f"{tree_type}_crown_{len(self.environment_obstacles)}",
                        opacity=1.0
                    )
                else:
                    self.add_sun_compatible_mesh(
                        crown,
                        color="#7EA040" if tree_type == 'oak' else self.default_leaf_color,
                        name=f"{tree_type}_crown_{len(self.environment_obstacles)}",
                        opacity=1.0
                    )
                
                tree_height = trunk_height + (5.5 if tree_type == 'oak' else 4)
            
            obstacle_data = {
                'type': f'tree_{tree_type}',
                'position': position,
                'height': tree_height
            }
            
            self.environment_obstacles.append(obstacle_data)
            print(f"✅ Added {tree_type} tree at ({x:.1f}, {y:.1f})")
            return obstacle_data
            
        except Exception as e:
            print(f"❌ Error adding tree: {e}")
            return None

    def _add_clean_pole(self, position):
        """Add utility pole with proper lighting"""
        try:
            x, y = position
            
            # Create pole
            pole_height = 7.0
            pole_radius = 0.15
            pole = pv.Cylinder(
                center=(x, y, pole_height/2),
                direction=(0, 0, 1),
                radius=pole_radius,
                height=pole_height,
                resolution=12
            )
            pole.compute_normals(inplace=True, auto_orient_normals=True)
            
            concrete_texture, concrete_loaded = self.load_texture_safely(
                self.concrete_texture_file,
                self.default_concrete_color
            )
            
            # Add pole
            if concrete_loaded:
                self.add_sun_compatible_mesh(
                    pole,
                    texture=concrete_texture,
                    name=f"pole_{len(self.environment_obstacles)}"
                )
            else:
                self.add_sun_compatible_mesh(
                    pole,
                    color="#A0A0A0",
                    name=f"pole_{len(self.environment_obstacles)}"
                )
            
            # Create crossbeam
            beam_width = 2.0
            beam_thickness = 0.1
            beam = pv.Box(bounds=(
                x - beam_width/2, x + beam_width/2,
                y - beam_thickness/2, y + beam_thickness/2,
                pole_height - 1.0, pole_height - 0.7
            ))
            beam.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Add beam
            self.add_sun_compatible_mesh(
                beam,
                color="#B85432",
                name=f"pole_beam_{len(self.environment_obstacles)}"
            )
            
            obstacle_data = {
                'type': 'pole',
                'position': position,
                'height': pole_height
            }
            
            self.environment_obstacles.append(obstacle_data)
            print(f"✅ Added utility pole at ({x:.1f}, {y:.1f})")
            return obstacle_data
            
        except Exception as e:
            print(f"❌ Error adding pole: {e}")
            return None

    def clear_environment_obstacles(self):
        """Clear all environment obstacles"""
        try:
            for i in range(len(self.environment_obstacles)):
                obstacle = self.environment_obstacles[i]
                if obstacle['type'].startswith('tree'):
                    # Remove tree parts
                    tree_type = obstacle['type'].split('_')[1] if '_' in obstacle['type'] else 'tree'
                    for prefix in ['tree', 'deciduous', 'oak', 'pine']:
                        try:
                            self.plotter.remove_actor(f"{prefix}_trunk_{i}")
                            self.plotter.remove_actor(f"{prefix}_crown_{i}")
                        except:
                            pass
                    
                    # Remove pine layers
                    for layer_idx in range(10):
                        try:
                            self.plotter.remove_actor(f"pine_crown_{i}_layer_{layer_idx}")
                        except:
                            pass
                            
                elif obstacle['type'] == 'pole':
                    try:
                        self.plotter.remove_actor(f"pole_{i}")
                        self.plotter.remove_actor(f"pole_beam_{i}")
                    except:
                        pass
            
            self.environment_obstacles.clear()
            
            for point in self.environment_attachment_points:
                point['occupied'] = False
                point['obstacle'] = None
            
            self.tree_type_index = 0
            print("✅ Cleared all environment obstacles")
            
        except Exception as e:
            print(f"❌ Error clearing obstacles: {e}")

    def set_theme(self, theme):
        """Update the roof's theme"""
        self.theme = theme
        if hasattr(self, 'annotator') and self.annotator:
            self.annotator.set_theme(theme)

    def reset_camera(self):
        """Reset camera to default position"""
        try:
            position, focal_point, up_vector = self.calculate_camera_position()
            
            adjusted_position = [
                position[0] * 1.5,
                position[1] * 1.5,
                position[2] * 1.2
            ]
            
            self.plotter.camera_position = [adjusted_position, focal_point, up_vector]
            
            if hasattr(self, 'roof_mesh') and self.roof_mesh:
                bounds = self.roof_mesh.bounds
                self.plotter.camera.focal_point = [
                    (bounds[0] + bounds[1]) / 2,
                    (bounds[2] + bounds[3]) / 2,
                    self.base_height / 2
                ]
                
                size = max(bounds[1] - bounds[0], bounds[3] - bounds[2], self.base_height)
                self.plotter.camera.distance = size * 3.0
            else:
                self.plotter.reset_camera()
                
        except Exception as e:
            print(f"❌ Camera reset failed: {e}")
            position, focal_point, up_vector = self.calculate_camera_position()
            self.plotter.camera_position = [position, focal_point, up_vector]
    
    def set_default_camera_view(self):
        """Set camera to the default position"""
        self.reset_camera()

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
            print(f"Screenshot saved to {filepath}")
        except Exception as e:
            print(f"Error saving screenshot: {e}")

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

    def update_texts(self):
        """Update all text elements"""
        self.plotter.update()

    def setup_key_bindings(self):
        """Set up key bindings"""
        print(f"🎮 Setting up key bindings...")
        
        self.setup_roof_specific_key_bindings()
        
        self.plotter.add_key_event("r", self.reset_camera)
        self.plotter.add_key_event("R", self.reset_camera)
        self.plotter.add_key_event('o', self.clear_obstacles)
        self.plotter.add_key_event('O', self.clear_obstacles)
        self.plotter.add_key_event("s", self.save_roof_screenshot)
        self.plotter.add_key_event("S", self.save_roof_screenshot)
        
        print("✅ Key bindings setup completed")

    def _setup_environment_key_bindings(self):
        """Setup environment key bindings"""
        def add_tree():
            self.add_environment_obstacle_at_point('tree')
            
        def add_pole():
            self.add_environment_obstacle_at_point('pole')
            
        def toggle_points():
            try:
                self.plotter.remove_actor("env_attachment_points")
            except:
                self.show_environment_attachment_points()
        
        self.plotter.add_key_event("t", add_tree)
        self.plotter.add_key_event("p", add_pole)
        self.plotter.add_key_event("a", toggle_points)
        self.plotter.add_key_event("e", self.clear_environment_obstacles)
        
        print("✅ Environment key bindings: t=tree, p=pole, a=points, e=clear")

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

    def is_point_occupied(self, point):
        """Check if point is occupied"""
        if not hasattr(self, 'obstacles') or not self.obstacles:
            return False
            
        min_distance = 0.2
        
        for obstacle in self.obstacles:
            distance = np.linalg.norm(np.array(obstacle.position) - np.array(point))
            if distance < min_distance:
                return True
                
        return False

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
        
        # Create roof-specific geometry
        self.create_roof_geometry()
        
        # IMPORTANT: Update sun system after geometry is created
        self.update_sun_system_after_changes()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
            self._setup_environment_key_bindings()
        except Exception as e:
            print(f"⚠️ Error setting up key bindings: {e}")
        
        # Set default camera view
        try:
            self.set_default_camera_view()
        except Exception as e:
            print(f"⚠️ Could not set camera view: {e}")

        print(f"🏠 {self.__class__.__name__} initialized with sun system integration")

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