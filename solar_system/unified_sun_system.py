#!/usr/bin/env python3
"""
unified_sun_system.py - FIXED FOR PYVISTA COMPATIBILITY
Sun system that works with standard PyVista lighting
"""
import numpy as np
import pyvista as pv
from solar_system.solar_calculations import SolarCalculations

class UnifiedSunSystem:
    """Sun system compatible with PyVista's light types"""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.sun_mesh = None
        self.sun_light = None
        self.current_sun_position = [15, 15, 8]
        self.solar_settings = {
            'sunshafts_enabled': True,
            'weather_factor': 1.0
        }
    
    def create_unified_sun(self, sun_pos, solar_settings):
        """Create sun with proper PyVista lighting"""
        try:
            self.current_sun_position = sun_pos
            self.solar_settings.update(solar_settings)
            
            # Check if sun is above horizon
            if sun_pos[2] <= 0:
                self.create_night_scene()
                return
            
            # Clear existing sun elements
            self.clear_all_sun_elements()
            
            # Create visual sun
            self.create_sun_visual(sun_pos, solar_settings)
            
            # Add sunshafts if enabled
            if self.solar_settings.get('sunshafts_enabled', True):
                self.create_simple_sunshafts(sun_pos)
            
            print(f"☀️ Sun created at {sun_pos}")
            
        except Exception as e:
            print(f"❌ Error creating sun: {e}")
    
    def clear_all_sun_elements(self):
        """Clear all sun-related elements"""
        try:
            sun_elements = [
                'sun_core', 'sun_inner', 'sun_glow', 
                'sun_outer', 'sunshafts'
            ]
            
            for element in sun_elements:
                try:
                    self.plotter.remove_actor(element)
                except:
                    pass
            
            # Remove sun light
            if self.sun_light:
                try:
                    self.plotter.remove_light(self.sun_light)
                    self.sun_light = None
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error clearing sun elements: {e}")
    
    def create_sun_visual(self, sun_pos, solar_settings):
        """Create visual sun with integrated lighting"""
        try:
            # Calculate sun properties
            sun_elevation = self._calculate_sun_elevation(sun_pos)
            sun_intensity = SolarCalculations.calculate_sun_intensity(
                sun_pos, solar_settings.get('weather_factor', 1.0)
            )
            sun_color_values = SolarCalculations.calculate_sun_color(sun_pos)
            
            # 1. Sun core - bright center
            sun_core = pv.Sphere(radius=1.2, center=sun_pos)
            
            # Get color based on elevation
            if sun_elevation < 10:
                core_color = '#FF6347'  # Tomato red
            elif sun_elevation < 30:
                core_color = '#FFD700'  # Gold
            else:
                core_color = '#FFFFE0'  # Light yellow
            
            self.sun_mesh = self.plotter.add_mesh(
                sun_core,
                color=core_color,
                name='sun_core',
                smooth_shading=True,
                opacity=1.0,
                ambient=0.8,  # Make it glow
                diffuse=1.0,
                show_edges=False
            )
            
            # 2. Inner glow
            sun_inner = pv.Sphere(radius=1.8, center=sun_pos)
            self.plotter.add_mesh(
                sun_inner,
                color='#FFFF99',
                name='sun_inner',
                opacity=0.5,
                ambient=0.4,
                show_edges=False
            )
            
            # 3. Outer glow
            sun_glow = pv.Sphere(radius=2.5, center=sun_pos)
            self.plotter.add_mesh(
                sun_glow,
                color='#FFFFCC',
                name='sun_glow',
                opacity=0.2,
                ambient=0.2,
                show_edges=False
            )
            
            # 4. Add light at sun position (standard PyVista light)
            self.sun_light = pv.Light()
            self.sun_light.position = sun_pos
            self.sun_light.focal_point = (0, 0, 0)
            self.sun_light.intensity = max(0.8, min(2.0, sun_intensity * 2.0))
            self.sun_light.color = sun_color_values
            self.sun_light.positional = True  # Point light from sun
            self.sun_light.cone_angle = 90
            self.sun_light.show_actor = False
            
            self.plotter.add_light(self.sun_light)
            
            print(f"✅ Sun visual created: elevation={sun_elevation:.1f}°")
            
        except Exception as e:
            print(f"❌ Error creating sun visual: {e}")
    
    def create_simple_sunshafts(self, sun_pos):
        """Create simple sunshaft effect"""
        try:
            # Simple cone for sunshafts
            target = np.array([0, 0, 0])
            sun = np.array(sun_pos)
            direction = target - sun
            
            dist = np.linalg.norm(direction)
            if dist > 0:
                direction = direction / dist
            else:
                return
            
            # Create subtle sunshaft cone
            cone_height = min(20, dist * 0.6)
            cone_radius = cone_height * 0.15
            cone_center = sun + direction * 3
            
            sunshaft = pv.Cone(
                center=cone_center,
                direction=direction,
                height=cone_height,
                radius=cone_radius,
                resolution=8
            )
            
            self.plotter.add_mesh(
                sunshaft,
                color='#FFFFAA',
                opacity=0.05,
                name='sunshafts',
                show_edges=False
            )
            
        except Exception as e:
            print(f"❌ Error creating sunshafts: {e}")
    
    def _calculate_sun_elevation(self, sun_pos):
        """Calculate sun elevation angle"""
        if sun_pos is None:
            return 0
        horizontal_dist = np.sqrt(sun_pos[0]**2 + sun_pos[1]**2)
        if horizontal_dist > 0:
            return np.degrees(np.arctan(sun_pos[2] / horizontal_dist))
        return 90 if sun_pos[2] > 0 else 0
    
    def create_night_scene(self):
        """Create night scene"""
        try:
            self.clear_all_sun_elements()
            self.plotter.background_color = '#0a0a1f'
            print("✅ Night scene created")
        except Exception as e:
            print(f"❌ Error creating night scene: {e}")
    
    def update_position(self, new_sun_pos, solar_settings):
        """Update sun position"""
        try:
            self.create_unified_sun(new_sun_pos, solar_settings)
        except Exception as e:
            print(f"❌ Error updating sun: {e}")
