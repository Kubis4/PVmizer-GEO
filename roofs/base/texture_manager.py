#!/usr/bin/env python3
"""
roofs/base/texture_manager.py
Manages textures and materials for the roof system
"""
import os
import pyvista as pv
import numpy as np
from .resource_utils import resource_path

class TextureManager:
    """Manages all texture loading and material properties"""
    
    def __init__(self, base_roof):
        """Initialize texture manager"""
        self.roof = base_roof
        self._setup_textures()
        print("✅ TextureManager initialized")
    
    def _setup_textures(self):
        """Setup texture paths with fallback locations"""
        # Find texture directory
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
        """Safely load texture with comprehensive fallback"""
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
    
    def calculate_texture_scale(self):
        """Calculate texture scaling based on building size"""
        if self.roof.dimensions and len(self.roof.dimensions) >= 2:
            building_size = max(self.roof.dimensions[0], self.roof.dimensions[1])
            return building_size / 10.0  # Base scale on 10m building
        return 1.0
    
    def generate_sphere_texture_coordinates(self, mesh, center, radius):
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
                
                texture_coords[i] = [u * 4, v * 4]  # Scale texture
            
            return texture_coords
            
        except Exception as e:
            print(f"❌ Error generating texture coordinates: {e}")
            return np.zeros((mesh.points.shape[0], 2))
