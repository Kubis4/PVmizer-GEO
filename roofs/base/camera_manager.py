#!/usr/bin/env python3
"""
roofs/base/camera_manager.py
Manages camera positioning and screenshots
"""
import datetime
from pathlib import Path

class CameraManager:
    """Manages camera operations and screenshots"""
    
    def __init__(self, base_roof):
        """Initialize camera manager"""
        self.roof = base_roof
        self.plotter = base_roof.plotter
        self.screenshot_directory = None
        print("✅ CameraManager initialized")
    
    def reset_camera(self):
        """Reset camera to default position"""
        try:
            position, focal_point, up_vector = self.roof.calculate_camera_position()
            
            # Adjust position for better view
            adjusted_position = [
                position[0] * 1.5,
                position[1] * 1.5,
                position[2] * 1.2
            ]
            
            self.plotter.camera_position = [adjusted_position, focal_point, up_vector]
            
            # If roof mesh exists, focus on it
            if hasattr(self.roof, 'roof_mesh') and self.roof.roof_mesh:
                bounds = self.roof.roof_mesh.bounds
                self.plotter.camera.focal_point = [
                    (bounds[0] + bounds[1]) / 2,
                    (bounds[2] + bounds[3]) / 2,
                    self.roof.base_height / 2
                ]
                
                size = max(bounds[1] - bounds[0], bounds[3] - bounds[2], self.roof.base_height)
                self.plotter.camera.distance = size * 3.0
            else:
                self.plotter.reset_camera()
                
        except Exception as e:
            print(f"❌ Camera reset failed: {e}")
            self.plotter.reset_camera()
    
    def set_default_camera_view(self):
        """Set camera to default position"""
        self.reset_camera()
    
    def set_screenshot_directory(self, directory):
        """Set screenshot directory"""
        self.screenshot_directory = directory
    
    def save_roof_screenshot(self):
        """Save current view screenshot"""
        if self.screenshot_directory:
            snaps_dir = Path(self.screenshot_directory)
        else:
            snaps_dir = Path("RoofSnaps")
        
        snaps_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        roof_type = self.roof.__class__.__name__.lower()
        filename = f"{roof_type}_{timestamp}.png"
        filepath = snaps_dir / filename
        
        try:
            self.plotter.screenshot(str(filepath))
            print(f"✅ Screenshot saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving screenshot: {e}")
