#!/usr/bin/env python3
"""
solar_lighting_system.py - OPTIMIZED VERSION
Solar lighting and atmosphere system - BETTER PERFORMANCE
"""
import pyvista as pv
from solar_system.solar_calculations import SolarCalculations

class SolarLightingSystem:
    """Handle solar lighting - OPTIMIZED for performance"""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.sun_light = None
        self.ambient_light = None
    
    def setup_solar_lighting(self, sun_pos, solar_settings):
        """Setup OPTIMIZED solar lighting system"""
        try:
            if not self.plotter:
                return
            
            # Remove existing lights
            if hasattr(self.plotter, 'remove_all_lights'):
                self.plotter.remove_all_lights()
            
            # If sun position is None, it's night
            if sun_pos is None:
                self.setup_night_lighting()
                return
            
            # Calculate lighting parameters
            sun_intensity = SolarCalculations.calculate_sun_intensity(
                sun_pos, solar_settings.get('weather_factor', 1.0)
            )
            sun_color = SolarCalculations.calculate_sun_color(sun_pos)
            
            # Get current hour for intensity adjustment
            current_hour = solar_settings.get('current_hour', 12)
            
            # 1. Main sun light - BRIGHTER AT NOON
            self.sun_light = pv.Light(
                position=sun_pos,
                focal_point=(0, 0, 0),
                color=sun_color,
                intensity=2.0 * sun_intensity  # Increased base intensity
            )
            self.plotter.add_light(self.sun_light)
            
            # 2. Ambient sky light - BRIGHTER FOR DAY
            ambient_intensity = 0.3 if 6 <= current_hour <= 18 else 0.1
            self.ambient_light = pv.Light(
                position=(0, 0, 30),
                focal_point=(0, 0, 0),
                color=[0.8, 0.9, 1.0],  # Sky blue tint
                intensity=ambient_intensity
            )
            self.plotter.add_light(self.ambient_light)
            
            # 3. Fill light for better visibility
            if 9 <= current_hour <= 15:  # Midday hours
                fill_light = pv.Light(
                    position=(-sun_pos[0], -sun_pos[1], sun_pos[2]),
                    focal_point=(0, 0, 0),
                    color=[0.9, 0.9, 1.0],
                    intensity=0.3
                )
                self.plotter.add_light(fill_light)
            
            print(f"✅ Solar lighting set: intensity={sun_intensity:.2f}, hour={current_hour:.1f}")
            
        except Exception as e:
            print(f"❌ Error setting up solar lighting: {e}")

    
    def update_background_color(self, solar_settings):
        """Update background color - FIXED FOR NOON"""
        try:
            current_hour = solar_settings.get('current_hour', 12)
            
            # FORCE BRIGHT COLORS DURING DAY
            if 6 <= current_hour <= 8:
                self.plotter.background_color = '#FFE4B5'  # Morning
            elif 8 < current_hour <= 16:  # Extended bright period
                self.plotter.background_color = '#87CEEB'  # Bright sky blue
            elif 16 < current_hour <= 18:
                self.plotter.background_color = '#FFD4A3'  # Afternoon
            elif 18 < current_hour <= 20:
                self.plotter.background_color = '#FF8C42'  # Sunset
            else:
                self.plotter.background_color = '#191970'  # Night
                
        except Exception as e:
            print(f"❌ Error updating background color: {e}")

    
    def setup_night_lighting(self):
        """Setup minimal night lighting - OPTIMIZED"""
        try:
            if hasattr(self.plotter, 'remove_all_lights'):
                self.plotter.remove_all_lights()
            
            night_light = pv.Light(
                position=(0, 0, 15),  # Closer
                focal_point=(0, 0, 0),
                color=[0.3, 0.3, 0.5],
                intensity=0.15  # Reduced for performance
            )
            
            self.plotter.add_light(night_light)
            
        except Exception as e:
            print(f"❌ Error setting up night lighting: {e}")
