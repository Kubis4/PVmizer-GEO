#!/usr/bin/env python3
"""
roofs/base/base_roof.py
Complete BaseRoof without automatic annotation creation
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
    """
    Base class for all roof types - annotations handled by subclasses
    """
    
    def __init__(self, plotter=None, dimensions=None, theme="light"):
        """
        Template method for roof initialization without annotations
        """
        print("\nDEBUG: BaseRoof.__init__ starting")
        print(f"DEBUG: Called from: {self.__class__.__name__}")
        # Store basic properties FIRST
        self.theme = theme
        self.base_height = 3.0  # Standard house height (3 meters)
        self.ground_size = 30.0  # Larger ground plane (30x30 meters)
        self.house_walls = []
        self.ground_mesh = None
        self.environment_obstacles = []  # Trees, poles, etc.
        self.environment_attachment_points = []  # Points for placing trees/poles
        self.tree_type_index = 0  # Track which tree type to spawn next
        
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
        self.annotator = None  # Will be set by subclasses if needed
        
        # Setup textures
        self._setup_textures()
        
        # Create ground with grass.png texture
        self._create_grass_ground()
        
        # Create environment attachment points
        self._create_environment_attachment_points()
        
        # Store base points for building creation
        self.base_points = None  # Will be set by concrete roof classes
        
        # Add axes to the plotter
        try:
            self.plotter.add_axes()
            print(f"✅ {self.__class__.__name__}: Axes added successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Could not add axes: {e}")

        print("DEBUG: BaseRoof.__init__ completed")
        print(f"DEBUG: Has initialize_roof been called? {hasattr(self, 'dimensions')}")
    def set_plotter_background(self):
        """Set the plotter background based on current theme"""
        if hasattr(self, 'theme') and self.theme == "dark":
            self.plotter.set_background("darkgrey")
        else:
            self.plotter.set_background("lightgrey")

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
        """Setup texture paths for realistic rendering - UPDATED PATH"""
        texture_dir = resource_path("PVmizer GEO/textures")  # Updated path
        
        # House textures
        self.wall_texture_file = os.path.join(texture_dir, "wall.jpg")
        self.brick_texture_file = os.path.join(texture_dir, "brick.jpg")
        self.roof_tile_texture_file = os.path.join(texture_dir, "roof_tiles.jpg")
        
        # Environment textures
        self.grass_texture_file = os.path.join(texture_dir, "grass.png")  # STAYS .png
        self.concrete_texture_file = os.path.join(texture_dir, "concrete.jpg")
        
        # Tree textures - .jpg format
        self.leaf_texture_file = os.path.join(texture_dir, "leaf.jpg")
        self.pine_texture_file = os.path.join(texture_dir, "pine.jpg")
        self.leaf_bark_texture_file = os.path.join(texture_dir, "leaf_stomp.jpg")
        self.pine_bark_texture_file = os.path.join(texture_dir, "pine_stomp.jpg")
        
        # Default colors if textures not found
        self.default_wall_color = "#D4A373"
        self.default_roof_color = "#8B4513"
        self.default_grass_color = "#228B22"
        self.default_concrete_color = "#808080"
        self.default_leaf_color = "#388E3C"
        self.default_pine_color = "#0F4F2F"
        self.default_bark_color = "#5D4037"

    def _create_grass_ground(self):
        """Create grass ground plane using grass.png texture (512x512)"""
        try:
            # Create a larger ground plane BELOW everything
            ground_size = self.ground_size
            z_level = -0.1  # Place ground slightly below z=0
            
            # Create ground mesh with more detail for better texture mapping
            resolution = 50  # Higher resolution for better texture appearance
            x = np.linspace(-ground_size/2, ground_size/2, resolution)
            y = np.linspace(-ground_size/2, ground_size/2, resolution)
            x, y = np.meshgrid(x, y)
            
            # Add very subtle terrain variation
            z = np.ones_like(x) * z_level
            z += np.random.normal(0, 0.005, z.shape)  # Very subtle variation
            
            # Create the mesh
            points = np.c_[x.ravel(), y.ravel(), z.ravel()]
            self.ground_mesh = pv.PolyData(points)
            self.ground_mesh = self.ground_mesh.delaunay_2d()
            
            # Generate texture coordinates for grass.png (512x512)
            # Scale texture to repeat appropriately for ground size
            texture_scale = 8.0  # Each texture covers about 3.75m x 3.75m
            texture_coords = np.zeros((self.ground_mesh.n_points, 2))
            for i in range(self.ground_mesh.n_points):
                point = self.ground_mesh.points[i]
                # Map to UV coordinates with proper scaling
                u = (point[0] + ground_size/2) / ground_size * texture_scale
                v = (point[1] + ground_size/2) / ground_size * texture_scale
                texture_coords[i] = [u, v]
            
            self.ground_mesh.active_t_coords = texture_coords
            
            # Load and apply grass.png texture
            grass_texture, texture_loaded = self.load_texture_safely(
                self.grass_texture_file, 
                self.default_grass_color
            )
            
            if texture_loaded:
                self.plotter.add_mesh(
                    self.ground_mesh,
                    texture=grass_texture,
                    name="ground_plane",
                    smooth_shading=True,
                    ambient=0.3,
                    diffuse=0.7,
                    specular=0.05
                )
                print(f"✅ Ground plane created with grass.png texture")
            else:
                self.plotter.add_mesh(
                    self.ground_mesh,
                    color=self.default_grass_color,
                    name="ground_plane",
                    smooth_shading=True,
                    ambient=0.3,
                    diffuse=0.7,
                    specular=0.05
                )
                print(f"✅ Ground plane created with default color (grass.png not found)")
            
        except Exception as e:
            print(f"❌ Error creating ground plane: {e}")

    def _create_environment_attachment_points(self):
        """Create attachment points around the building for trees and poles"""
        try:
            # Create a grid of points around the building
            building_buffer = 7.0  # Keep obstacles at least 7m from building center
            
            # Create points in a ring around the building
            angles = np.linspace(0, 2*np.pi, 12, endpoint=False)  # 12 points in a circle
            radius = building_buffer + 3.0  # Place 3m outside building buffer
            
            for angle in angles:
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                self.environment_attachment_points.append({
                    'position': [x, y, 0],
                    'occupied': False,
                    'obstacle': None
                })
            
            # Add some points further out
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
            
            print(f"✅ Created {len(self.environment_attachment_points)} environment attachment points")
            
        except Exception as e:
            print(f"❌ Error creating environment attachment points: {e}")

    def show_environment_attachment_points(self):
        """Visualize the environment attachment points"""
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
                
                print(f"✅ Showing {len(points)} available attachment points")
                
        except Exception as e:
            print(f"❌ Error showing attachment points: {e}")

    def hide_environment_attachment_points(self):
        """Hide the environment attachment points"""
        try:
            self.plotter.remove_actor("env_attachment_points")
        except:
            pass

    def add_environment_obstacle_at_point(self, obstacle_type, point_index=None):
        """
        Add environmental obstacle at specific attachment point
        
        Args:
            obstacle_type: 'tree' or 'pole'
            point_index: Index of attachment point, or None for random available point
        """
        try:
            # Find available point
            if point_index is None:
                # Find random available point
                available_points = [i for i, p in enumerate(self.environment_attachment_points) 
                                  if not p['occupied']]
                if not available_points:
                    print("⚠️ No available attachment points")
                    return False
                
                import random
                point_index = random.choice(available_points)
            
            if point_index >= len(self.environment_attachment_points):
                print(f"⚠️ Invalid point index: {point_index}")
                return False
            
            point_data = self.environment_attachment_points[point_index]
            if point_data['occupied']:
                print(f"⚠️ Point {point_index} is already occupied")
                return False
            
            position = point_data['position']
            
            if obstacle_type == 'tree':
                # Cycle through different tree types
                tree_types = ['deciduous', 'pine', 'oak']
                tree_type = tree_types[self.tree_type_index % len(tree_types)]
                self.tree_type_index += 1
                obstacle = self._add_realistic_tree(position[:2], tree_type)
            elif obstacle_type == 'pole':
                obstacle = self._add_pole(position[:2])
            else:
                print(f"⚠️ Unknown obstacle type: {obstacle_type}")
                return False
            
            # Mark point as occupied
            point_data['occupied'] = True
            point_data['obstacle'] = obstacle
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding environment obstacle: {e}")
            return False

    def _add_realistic_tree(self, position, tree_type='deciduous'):
        """Add a realistic tree with textures"""
        try:
            x, y = position
            
            if tree_type == 'pine':
                # Create pine tree
                trunk_height = 2.5
                trunk_radius = 0.3
                
                trunk = pv.Cylinder(
                    center=(x, y, trunk_height/2),
                    direction=(0, 0, 1),
                    radius=trunk_radius,
                    height=trunk_height,
                    resolution=20
                )
                
                # Texture coordinates for trunk
                trunk_texture_coords = np.zeros((trunk.n_points, 2))
                for i in range(trunk.n_points):
                    point = trunk.points[i]
                    angle = np.arctan2(point[1] - y, point[0] - x)
                    u = (angle + np.pi) / (2 * np.pi)
                    v = (point[2] / trunk_height)
                    trunk_texture_coords[i] = [u * 2, v * 3]
                
                trunk.active_t_coords = trunk_texture_coords
                
                bark_texture, bark_loaded = self.load_texture_safely(
                    self.pine_bark_texture_file,
                    "#4A3C28"
                )
                
                # Create layered pine crown
                crown_parts = []
                layers = [
                    (0.5, 2.2, 0.8),
                    (1.2, 1.9, 0.8),
                    (1.9, 1.6, 0.8),
                    (2.6, 1.3, 0.7),
                    (3.2, 1.0, 0.7),
                    (3.8, 0.7, 0.6),
                    (4.3, 0.4, 0.5),
                ]
                
                for layer_idx, (h_offset, radius, thickness) in enumerate(layers):
                    layer = pv.Cylinder(
                        center=(x, y, trunk_height + h_offset),
                        direction=(0, 0, 1),
                        radius=radius,
                        height=thickness,
                        resolution=30,
                        capping=True
                    )
                    crown_parts.append(layer)
                
                crown = crown_parts[0]
                for part in crown_parts[1:]:
                    crown = crown + part
                
                crown_texture_coords = np.zeros((crown.n_points, 2))
                for i in range(crown.n_points):
                    point = crown.points[i]
                    dx = point[0] - x
                    dy = point[1] - y
                    dist = np.sqrt(dx*dx + dy*dy)
                    angle = np.arctan2(dy, dx)
                    height = point[2] - trunk_height
                    
                    u = (angle + np.pi) / (2 * np.pi) * 3
                    v = height / 5.0
                    
                    crown_texture_coords[i] = [u, v]
                
                crown.active_t_coords = crown_texture_coords
                
                pine_texture, pine_loaded = self.load_texture_safely(
                    self.pine_texture_file,
                    self.default_pine_color
                )
                
                # Add trunk
                if bark_loaded:
                    self.plotter.add_mesh(
                        trunk,
                        texture=bark_texture,
                        name=f"pine_trunk_{len(self.environment_obstacles)}",
                        smooth_shading=True,
                        ambient=0.3,
                        diffuse=0.7,
                        specular=0.05
                    )
                else:
                    self.plotter.add_mesh(
                        trunk,
                        color="#4A3C28",
                        name=f"pine_trunk_{len(self.environment_obstacles)}",
                        smooth_shading=True
                    )
                
                # Add crown
                if pine_loaded:
                    self.plotter.add_mesh(
                        crown,
                        texture=pine_texture,
                        name=f"pine_crown_{len(self.environment_obstacles)}",
                        smooth_shading=True,
                        ambient=0.25,
                        diffuse=0.75,
                        specular=0.1
                    )
                else:
                    self.plotter.add_mesh(
                        crown,
                        color=self.default_pine_color,
                        name=f"pine_crown_{len(self.environment_obstacles)}",
                        smooth_shading=True
                    )
                
                tree_height = trunk_height + 5
                
            elif tree_type == 'oak':
                # Oak tree
                trunk_height = 3.0
                trunk_radius = 0.4
                
                trunk = pv.Cylinder(
                    center=(x, y, trunk_height/2),
                    direction=(0, 0, 1),
                    radius=trunk_radius,
                    height=trunk_height,
                    resolution=20
                )
                
                trunk_texture_coords = np.zeros((trunk.n_points, 2))
                for i in range(trunk.n_points):
                    point = trunk.points[i]
                    angle = np.arctan2(point[1] - y, point[0] - x)
                    u = (angle + np.pi) / (2 * np.pi)
                    v = point[2] / trunk_height
                    trunk_texture_coords[i] = [u * 3, v * 4]
                
                trunk.active_t_coords = trunk_texture_coords
                
                bark_texture, bark_loaded = self.load_texture_safely(
                    self.leaf_bark_texture_file,
                    "#3E2723"
                )
                
                crown = pv.Sphere(
                    center=(x, y, trunk_height + 2),
                    radius=3.5,
                    theta_resolution=30,
                    phi_resolution=30
                )
                
                crown_texture_coords = np.zeros((crown.n_points, 2))
                for i in range(crown.n_points):
                    point = crown.points[i]
                    theta = np.arctan2(point[1] - y, point[0] - x)
                    phi = np.arccos(np.clip((point[2] - trunk_height - 2) / 3.5, -1, 1))
                    u = (theta + np.pi) / (2 * np.pi)
                    v = phi / np.pi
                    crown_texture_coords[i] = [u * 8, v * 8]
                
                crown.active_t_coords = crown_texture_coords
                
                leaf_texture, leaf_loaded = self.load_texture_safely(
                    self.leaf_texture_file,
                    "#2E7D32"
                )
                
                if bark_loaded:
                    self.plotter.add_mesh(
                        trunk,
                        texture=bark_texture,
                        name=f"oak_trunk_{len(self.environment_obstacles)}",
                        smooth_shading=True
                    )
                else:
                    self.plotter.add_mesh(
                        trunk,
                        color="#3E2723",
                        name=f"oak_trunk_{len(self.environment_obstacles)}",
                        smooth_shading=True
                    )
                
                if leaf_loaded:
                    self.plotter.add_mesh(
                        crown,
                        texture=leaf_texture,
                        name=f"oak_crown_{len(self.environment_obstacles)}",
                        smooth_shading=True,
                        opacity=0.95
                    )
                else:
                    self.plotter.add_mesh(
                        crown,
                        color="#2E7D32",
                        name=f"oak_crown_{len(self.environment_obstacles)}",
                        smooth_shading=True,
                        opacity=0.95
                    )
                
                tree_height = trunk_height + 5.5
                
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
                
                trunk_texture_coords = np.zeros((trunk.n_points, 2))
                for i in range(trunk.n_points):
                    point = trunk.points[i]
                    angle = np.arctan2(point[1] - y, point[0] - x)
                    u = (angle + np.pi) / (2 * np.pi)
                    v = point[2] / trunk_height
                    trunk_texture_coords[i] = [u * 2, v * 3]
                
                trunk.active_t_coords = trunk_texture_coords
                
                bark_texture, bark_loaded = self.load_texture_safely(
                    self.leaf_bark_texture_file,
                    "#5D4037"
                )
                
                crown = pv.Sphere(
                    center=(x, y, trunk_height + 1.5),
                    radius=2.5,
                    theta_resolution=25,
                    phi_resolution=25
                )
                
                crown_texture_coords = np.zeros((crown.n_points, 2))
                for i in range(crown.n_points):
                    point = crown.points[i]
                    theta = np.arctan2(point[1] - y, point[0] - x)
                    phi = np.arccos(np.clip((point[2] - trunk_height - 1.5) / 2.5, -1, 1))
                    u = (theta + np.pi) / (2 * np.pi)
                    v = phi / np.pi
                    crown_texture_coords[i] = [u * 6, v * 6]
                
                crown.active_t_coords = crown_texture_coords
                
                leaf_texture, leaf_loaded = self.load_texture_safely(
                    self.leaf_texture_file,
                    self.default_leaf_color
                )
                
                if bark_loaded:
                    self.plotter.add_mesh(
                        trunk,
                        texture=bark_texture,
                        name=f"tree_trunk_{len(self.environment_obstacles)}",
                        smooth_shading=True
                    )
                else:
                    self.plotter.add_mesh(
                        trunk,
                        color="#5D4037",
                        name=f"tree_trunk_{len(self.environment_obstacles)}",
                        smooth_shading=True
                    )
                
                if leaf_loaded:
                    self.plotter.add_mesh(
                        crown,
                        texture=leaf_texture,
                        name=f"tree_crown_{len(self.environment_obstacles)}",
                        smooth_shading=True,
                        opacity=0.92
                    )
                else:
                    self.plotter.add_mesh(
                        crown,
                        color=self.default_leaf_color,
                        name=f"tree_crown_{len(self.environment_obstacles)}",
                        smooth_shading=True,
                        opacity=0.92
                    )
                
                tree_height = trunk_height + 4
            
            obstacle_data = {
                'type': f'tree_{tree_type}',
                'position': position,
                'height': tree_height
            }
            
            self.environment_obstacles.append(obstacle_data)
            
            print(f"✅ Added {tree_type} tree at position ({x:.1f}, {y:.1f})")
            return obstacle_data
            
        except Exception as e:
            print(f"❌ Error adding tree: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_pole(self, position):
        """Add a utility pole with concrete texture"""
        try:
            x, y = position
            
            pole_height = 7.0
            pole_radius = 0.15
            pole = pv.Cylinder(
                center=(x, y, pole_height/2),
                direction=(0, 0, 1),
                radius=pole_radius,
                height=pole_height,
                resolution=12
            )
            
            pole_texture_coords = np.zeros((pole.n_points, 2))
            for i in range(pole.n_points):
                point = pole.points[i]
                angle = np.arctan2(point[1] - y, point[0] - x)
                u = (angle + np.pi) / (2 * np.pi)
                v = point[2] / pole_height
                pole_texture_coords[i] = [u, v * 5]
            
            pole.active_t_coords = pole_texture_coords
            
            concrete_texture, concrete_loaded = self.load_texture_safely(
                self.concrete_texture_file,
                self.default_concrete_color
            )
            
            beam_width = 2.0
            beam_thickness = 0.1
            beam = pv.Box(bounds=(
                x - beam_width/2, x + beam_width/2,
                y - beam_thickness/2, y + beam_thickness/2,
                pole_height - 1.0, pole_height - 0.7
            ))
            
            if concrete_loaded:
                self.plotter.add_mesh(
                    pole,
                    texture=concrete_texture,
                    name=f"pole_{len(self.environment_obstacles)}",
                    metallic=0.3,
                    roughness=0.8
                )
            else:
                self.plotter.add_mesh(
                    pole,
                    color="#4B4B4B",
                    name=f"pole_{len(self.environment_obstacles)}",
                    metallic=0.8,
                    roughness=0.3
                )
            
            self.plotter.add_mesh(
                beam,
                color="#654321",
                name=f"pole_beam_{len(self.environment_obstacles)}",
                metallic=0.1,
                roughness=0.9
            )
            
            obstacle_data = {
                'type': 'pole',
                'position': position,
                'height': pole_height
            }
            
            self.environment_obstacles.append(obstacle_data)
            
            print(f"✅ Added utility pole at position ({x:.1f}, {y:.1f})")
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
                    tree_type = obstacle['type'].split('_')[1] if '_' in obstacle['type'] else 'tree'
                    try:
                        self.plotter.remove_actor(f"{tree_type}_trunk_{i}")
                        self.plotter.remove_actor(f"{tree_type}_crown_{i}")
                        self.plotter.remove_actor(f"tree_trunk_{i}")
                        self.plotter.remove_actor(f"tree_crown_{i}")
                        self.plotter.remove_actor(f"oak_trunk_{i}")
                        self.plotter.remove_actor(f"oak_crown_{i}")
                        self.plotter.remove_actor(f"pine_trunk_{i}")
                        self.plotter.remove_actor(f"pine_crown_{i}")
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
            print(f"❌ Error clearing environment obstacles: {e}")

    # ==================== TEXTURE METHODS ====================
    def load_texture_safely(self, filename, default_color="#A9A9A9"):
        """Safely load a texture with fallback to color if loading fails"""
        base_filename = os.path.basename(filename)
        
        possible_paths = [
            filename,
            resource_path(filename),
            resource_path(f"PVmizer GEO/textures/{base_filename}"),
            resource_path(f"textures/{base_filename}"),
            resource_path(f"_internal/textures/{base_filename}")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    texture = pv.read_texture(path)
                    print(f"✅ Loaded texture: {base_filename}")
                    return texture, True
                except Exception as e:
                    print(f"Error loading texture from {path}: {e}")
        
        print(f"⚠️ Texture not found: {base_filename}, using default color")
        return default_color, False

    # ==================== THEME METHODS ====================
    def set_theme(self, theme):
        """Update the roof's theme and refresh visuals"""
        self.theme = theme
        self.set_plotter_background()
        
        if hasattr(self, 'annotator') and self.annotator:
            self.annotator.set_theme(theme)

    # ==================== CAMERA METHODS ====================
    def reset_camera(self):
        """Reset camera to default position focusing on roof and house"""
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
        self.plotter.update()

    # ==================== KEY BINDING METHODS ====================
    def setup_key_bindings(self):
        """Set up key bindings for roof visualization"""
        print(f"🎮 Setting up key bindings. Solar handler available: {self.solar_panel_handler is not None}")
        
        self.setup_roof_specific_key_bindings()
        
        self.plotter.add_key_event("r", self.reset_camera)
        self.plotter.add_key_event("R", self.reset_camera)
        self.plotter.add_key_event('o', self.clear_obstacles)
        self.plotter.add_key_event('O', self.clear_obstacles)
        self.plotter.add_key_event("s", self.save_roof_screenshot)
        self.plotter.add_key_event("S", self.save_roof_screenshot)
        
        print("✅ Key bindings setup completed")

    def _setup_environment_key_bindings(self):
        """Setup key bindings for environment obstacles"""
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
            
        min_distance = 0.2
        
        for obstacle in self.obstacles:
            distance = np.linalg.norm(np.array(obstacle.position) - np.array(point))
            if distance < min_distance:
                return True
                
        return False

    def place_obstacle_at_point(self, point, obstacle_type, normal_vector=None, roof_point=None, face=None):
        """Place an obstacle at the specified point with the stored dimensions"""
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
        """Find the closest attachment point to the clicked position"""
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

    # ==================== TEMPLATE METHOD ====================
    def initialize_roof(self, dimensions):
        """
        Template method that orchestrates roof creation WITHOUT annotations
        Subclasses handle their own annotations
        """
        # Store dimensions
        self.dimensions = dimensions
        
        # Create roof-specific geometry FIRST (this sets roof_points)
        self.create_roof_geometry()
        
        # Initialize solar panel handler
        self._initialize_solar_panel_handler()
        
        # NOTE: Annotations are NOT created here
        # Each roof subclass should create its own annotations as needed
        
        # Setup key bindings
        try:
            self.setup_key_bindings()
            self._setup_environment_key_bindings()
            print(f"✅ {self.__class__.__name__}: Key bindings set up successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Error setting up key bindings: {e}")
        
        # Set default camera view
        try:
            self.set_default_camera_view()
            print(f"✅ {self.__class__.__name__}: Camera view set successfully")
        except Exception as e:
            print(f"⚠️ {self.__class__.__name__}: Could not set camera view: {e}")

        print(f"🏠 {self.__class__.__name__} initialized (annotations handled by subclass)")
