#!/usr/bin/env python3
"""
Solar Event Handlers - Fixed with original time/date calculations
"""
import numpy as np
from PyQt5.QtCore import QTimer
import math

try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

class SolarEventHandlers:
    """Handles solar simulation with proper time/date calculations"""
    
    def __init__(self, content_tab_widget):
        self.content_tab_widget = content_tab_widget
        self.main_window = content_tab_widget.main_window
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_sun)
        self.is_animating = False
        self.animation_time = 0
        self.animation_speed = 1
        
        # Solar parameters
        self.time_of_day = 12  # Hours (6-18)
        self.day_of_year = 180  # Day (1-365)
        self.latitude = 48.3  # Default latitude (can be updated)
        
    def update_solar_position(self, time_of_day, day_of_year):
        """Update solar position based on time and date"""
        try:
            self.time_of_day = time_of_day
            self.day_of_year = day_of_year
            
            # Calculate sun position
            azimuth, elevation = self._calculate_sun_position(time_of_day, day_of_year, self.latitude)
            
            # Update 3D scene lighting
            self._update_sun_lighting(azimuth, elevation)
            
            print(f"☀️ Solar position updated: time={time_of_day}h, day={day_of_year}, azimuth={azimuth:.1f}°, elevation={elevation:.1f}°")
            return True
            
        except Exception as e:
            print(f"❌ Error updating solar position: {e}")
            return False
    
    def _calculate_sun_position(self, time_of_day, day_of_year, latitude):
        """Calculate sun azimuth and elevation based on time, date, and location"""
        try:
            # Convert inputs
            hour = float(time_of_day)
            day = float(day_of_year)
            lat = math.radians(float(latitude))
            
            # Solar declination angle
            declination = math.radians(23.45 * math.sin(math.radians(360 * (284 + day) / 365)))
            
            # Hour angle (solar time)
            hour_angle = math.radians(15 * (hour - 12))
            
            # Solar elevation angle
            elevation_rad = math.asin(
                math.sin(declination) * math.sin(lat) + 
                math.cos(declination) * math.cos(lat) * math.cos(hour_angle)
            )
            elevation = math.degrees(elevation_rad)
            
            # Solar azimuth angle
            azimuth_rad = math.atan2(
                math.sin(hour_angle),
                math.cos(hour_angle) * math.sin(lat) - math.tan(declination) * math.cos(lat)
            )
            azimuth = (math.degrees(azimuth_rad) + 180) % 360  # Convert to 0-360°
            
            # Ensure sun is above horizon
            elevation = max(0, elevation)
            
            return azimuth, elevation
            
        except Exception as e:
            print(f"❌ Error calculating sun position: {e}")
            return 180, 45  # Default: south, 45° elevation
    
    def _update_sun_lighting(self, azimuth, elevation):
        """Update 3D scene lighting based on sun position"""
        try:
            pyvista_integration = self.content_tab_widget.pyvista_integration
            plotter = pyvista_integration.get_plotter()
            
            if not plotter or not PYVISTA_AVAILABLE:
                return False
            
            # Calculate 3D sun position
            distance = 100  # Distance from origin
            azimuth_rad = math.radians(azimuth)
            elevation_rad = math.radians(elevation)
            
            x = distance * math.cos(elevation_rad) * math.sin(azimuth_rad)
            y = distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
            z = distance * math.sin(elevation_rad)
            
            # Remove existing lights
            try:
                plotter.remove_all_lights()
            except:
                pass
            
            # Calculate sun intensity based on elevation
            sun_intensity = max(0.1, min(1.0, elevation / 90.0))
            
            # Add main sun light
            sun_light = pv.Light(
                position=(x, y, z),
                intensity=sun_intensity,
                light_type='scene light'
            )
            plotter.add_light(sun_light)
            
            # Add ambient lighting (varies with sun elevation)
            ambient_intensity = max(0.2, sun_intensity * 0.4)
            ambient_light = pv.Light(
                position=(-x * 0.3, -y * 0.3, abs(z) * 0.5),
                intensity=ambient_intensity,
                light_type='scene light'
            )
            plotter.add_light(ambient_light)
            
            # Add fill light for better visibility
            fill_light = pv.Light(
                position=(x * 0.5, y * 0.5, abs(z)),
                intensity=0.3,
                light_type='scene light'
            )
            plotter.add_light(fill_light)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating sun lighting: {e}")
            return False
    
    def start_animation(self, speed=1):
        """Start solar animation"""
        try:
            if self.is_animating:
                self.stop_animation()
            
            self.animation_speed = speed
            self.animation_time = 6  # Start at 6 AM
            self.is_animating = True
            
            # Update interval based on speed (faster = shorter interval)
            interval = max(50, 200 // speed)
            self.animation_timer.start(interval)
            
            print(f"▶️ Solar animation started at {speed}x speed")
            return True
            
        except Exception as e:
            print(f"❌ Error starting animation: {e}")
            return False
    
    def stop_animation(self):
        """Stop solar animation"""
        try:
            self.animation_timer.stop()
            self.is_animating = False
            print("⏸️ Solar animation stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping animation: {e}")
            return False
    
    def _animate_sun(self):
        """Animate sun movement throughout the day"""
        try:
            if not self.is_animating:
                return
            
            # Update time
            time_increment = 0.1 * self.animation_speed  # 0.1 hour per step
            self.animation_time += time_increment
            
            # Check if animation should loop or stop
            if self.animation_time > 18:  # 6 PM
                self.animation_time = 6   # Reset to 6 AM
                # Or stop animation:
                # self.stop_animation()
                # return
            
            # Update solar position
            self.update_solar_position(self.animation_time, self.day_of_year)
            
            # Update left panel sliders if available
            self._update_left_panel_sliders()
            
        except Exception as e:
            print(f"❌ Error in solar animation: {e}")
            self.stop_animation()
    
    def _update_left_panel_sliders(self):
        """Update left panel sliders to reflect current animation state"""
        try:
            if hasattr(self.main_window, 'left_panel'):
                left_panel = self.main_window.left_panel
                
                # Update time slider
                if hasattr(left_panel, 'time_slider'):
                    left_panel.time_slider.setValue(int(self.animation_time))
                
                # Update time label
                if hasattr(left_panel, 'time_value'):
                    left_panel.time_value.setText(f"{int(self.animation_time):02d}:00")
                    
        except Exception as e:
            print(f"❌ Error updating left panel sliders: {e}")
    
    def set_latitude(self, latitude):
        """Set latitude for solar calculations"""
        try:
            self.latitude = float(latitude)
            # Recalculate current position
            self.update_solar_position(self.time_of_day, self.day_of_year)
            print(f"🌍 Latitude set to {latitude}°")
            return True
        except Exception as e:
            print(f"❌ Error setting latitude: {e}")
            return False