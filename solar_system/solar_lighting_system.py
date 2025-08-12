#!/usr/bin/env python3
"""
solar_lighting_system.py - SIMPLIFIED WORKING VERSION
Based on the successful working example
"""
import pyvista as pv
import numpy as np

class SolarLightingSystem:
    """Simplified solar lighting that works like the example"""

    def __init__(self, plotter):
        self.plotter = plotter
        self.sun_light = None
        self.ambient_light = None
        self.fill_light = None

    def setup_solar_lighting(self, sun_pos, solar_settings=None):
        """Setup lighting exactly like working example"""
        try:
            # Clear existing lights
            self.plotter.remove_all_lights()
            
            if sun_pos is None or (len(sun_pos) > 2 and sun_pos[2] <= 0):
                # Night lighting
                self.setup_night_lighting()
                return
            
            # Main sun light (strong directional)
            self.sun_light = pv.Light(
                position=sun_pos,
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=1.8
            )
            self.sun_light.color = [1.0, 0.95, 0.8]
            self.plotter.add_light(self.sun_light)
            
            # Ambient light for overall illumination
            self.ambient_light = pv.Light(
                position=(0, 0, 30),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.4
            )
            self.ambient_light.color = [0.9, 0.9, 1.0]
            self.plotter.add_light(self.ambient_light)
            
            # Fill light from opposite side
            if len(sun_pos) >= 3:
                fill_pos = (-sun_pos[0]*0.3, -sun_pos[1]*0.3, sun_pos[2]*0.5)
            else:
                fill_pos = (-sun_pos[0]*0.3, -sun_pos[1]*0.3, 10)
                
            self.fill_light = pv.Light(
                position=fill_pos,
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.3
            )
            self.fill_light.color = [0.85, 0.9, 1.0]
            self.plotter.add_light(self.fill_light)
            
            print("💡 Solar lighting configured")
            
        except Exception as e:
            print(f"Error in solar lighting: {e}")
            self.setup_fallback_lighting()

    def setup_night_lighting(self):
        """Simple night lighting"""
        try:
            moon = pv.Light(
                position=(10, 10, 20),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=0.3
            )
            moon.color = [0.7, 0.7, 0.9]
            self.plotter.add_light(moon)
            
            print("🌙 Night lighting active")
            
        except Exception as e:
            print(f"Error in night lighting: {e}")

    def setup_fallback_lighting(self):
        """Fallback lighting"""
        try:
            light = pv.Light(
                position=(15, 15, 20),
                focal_point=(0, 0, 0),
                light_type='scenelight',
                intensity=1.0
            )
            self.plotter.add_light(light)
            
        except:
            pass

    def update_sun_position(self, sun_pos):
        """Update sun light position"""
        if self.sun_light and sun_pos:
            self.sun_light.position = sun_pos
            print(f"☀️ Sun light updated to position {sun_pos}")

    def update_background_color(self, solar_settings):
        """Update background based on time"""
        try:
            hour = solar_settings.get('current_hour', 12)
            
            if hour < 6 or hour > 20:
                self.plotter.set_background('#1a1a3a', top='#0a0a1f')
            elif hour < 8:
                self.plotter.set_background('#ff6b4a', top='#ffa366')
            elif hour < 18:
                self.plotter.set_background('skyblue', top='white')
            else:
                self.plotter.set_background('#ff8c42', top='#ff6b4a')
                
        except:
            self.plotter.set_background('skyblue', top='white')
