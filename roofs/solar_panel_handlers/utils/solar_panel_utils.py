import pyvista as pv
import numpy as np
import os
import sys
from pathlib import Path

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_paths = []
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_paths.append(sys._MEIPASS)
    except Exception:
        pass
    
    # Add the directory of the executable
    base_paths.append(os.path.dirname(sys.executable))
    
    # Add the _internal directory that auto-py-to-exe often creates
    base_paths.append(os.path.join(os.path.dirname(sys.executable), "_internal"))
    
    # Add current directory
    base_paths.append(os.path.abspath("."))
    
    # Try to find the file in each base path
    for base_path in base_paths:
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            print(f"Found resource at: {full_path}")
            return full_path
            
    # If we get here, log what we checked
    print(f"Resource not found: {relative_path}")
    print(f"Searched paths: {[os.path.join(bp, relative_path) for bp in base_paths]}")
    
    # Return the original path in the executable directory
    return os.path.join(os.path.dirname(sys.executable), relative_path)

def load_panel_texture():
    """Load solar panel texture with robust path handling."""
    try:
        # Try to find the texture using resource_path
        texture_paths = [
            os.path.join("textures", "solarpanel.png"),
            os.path.join("textures", "solarpanel.jpg"),
            os.path.join("PVmizer", "textures", "solarpanel.png"),
            os.path.join("PVmizer", "textures", "solarpanel.jpg")
        ]
        
        # Try each texture path
        for texture_path in texture_paths:
            try:
                full_path = resource_path(texture_path)
                if os.path.exists(full_path):
                    panel_texture = pv.read_texture(full_path)
                    print(f"Loaded solar panel texture from: {full_path}")
                    return panel_texture
            except Exception as e:
                print(f"Failed to load texture from {texture_path}: {e}")
        
        # If we get here, try legacy paths as a fallback
        legacy_paths = [
            "PVmizer/textures/solarpanel.png",
            "PVmizer/textures/solarpanel.jpg",
            "textures/solarpanel.png",
            "textures/solarpanel.jpg"
        ]
        
        for path in legacy_paths:
            if os.path.exists(path):
                try:
                    panel_texture = pv.read_texture(path)
                    print(f"Loaded solar panel texture from legacy path: {path}")
                    return panel_texture
                except Exception as e:
                    print(f"Failed to load texture from legacy path {path}: {e}")
        
        # If we reach here, no texture was loaded
        print("No solar panel texture could be loaded. Using solid color instead.")
        return None
        
    except Exception as e:
        print(f"Error in texture loading process: {e}")
        import traceback
        traceback.print_exc()
        return None

class PanelGeometry:
    """Handles panel geometry calculations and transformations"""
    
    @staticmethod
    def create_panel_mesh(panel_length_m, panel_width_m, panel_tilt=0, panel_orientation=0):
        """Create a panel mesh with specified dimensions and transformations"""
        # Create panel at origin
        panel = pv.Plane(
            center=[0, 0, 0],
            direction=[0, 0, 1],
            i_size=panel_length_m, 
            j_size=panel_width_m
        )
        
        # Apply rotations if needed
        if panel_tilt > 0.1:
            panel.rotate_x(panel_tilt, inplace=True)
        
        if panel_orientation != 0:
            panel.rotate_z(panel_orientation, inplace=True)
        
        return panel
    
    @staticmethod
    def calculate_panel_spacing(base_gap_x, base_gap_y, panel_tilt, panel_orientation):
        """Calculate appropriate panel spacing based on tilt and orientation"""
        # Convert orientation to radians
        orientation_rad = np.radians(panel_orientation)
        
        # For non-cardinal orientations, adjust spacing
        diagonal_effect = abs(np.sin(2 * orientation_rad))
        orientation_factor = 1.0 + 0.4 * diagonal_effect
        
        # Additional adjustment for tilt
        tilt_factor = 1.0
        if panel_tilt > 0.1:
            tilt_rad = np.radians(panel_tilt)
            tilt_factor = 1.0 + 0.5 * np.sin(tilt_rad)
        
        # Apply adjustments
        adjusted_gap_x = base_gap_x * orientation_factor * tilt_factor
        adjusted_gap_y = base_gap_y * orientation_factor * tilt_factor
        
        return adjusted_gap_x, adjusted_gap_y
