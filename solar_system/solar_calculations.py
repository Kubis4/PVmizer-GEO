#!/usr/bin/env python3
"""
solar_calculations.py - FIXED DAYLIGHT
Realistic sun position calculations with proper noon brightness
"""
import numpy as np
from datetime import datetime

class SolarCalculations:
    """Accurate solar position calculations with proper daylight"""
    
    @staticmethod
    def calculate_sun_position(decimal_hour, day_of_year, latitude, building_height=3.0):
        """
        Calculate sun position - returns None if sun is below horizon
        """
        try:
            # Get sunrise and sunset times
            sunrise, sunset = SolarCalculations.get_time_range(latitude, day_of_year)
            
            # Check if it's night time
            if decimal_hour < sunrise or decimal_hour > sunset:
                return None  # Sun is below horizon
            
            # Convert inputs to radians
            lat_rad = np.radians(latitude)
            
            # Calculate solar declination angle
            declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
            decl_rad = np.radians(declination)
            
            # Calculate hour angle
            hour_angle = (decimal_hour - 12) * 15  # 15 degrees per hour
            hour_angle_rad = np.radians(hour_angle)
            
            # Calculate sun elevation (altitude) angle
            elevation_rad = np.arcsin(
                np.sin(decl_rad) * np.sin(lat_rad) + 
                np.cos(decl_rad) * np.cos(lat_rad) * np.cos(hour_angle_rad)
            )
            
            # If sun is below horizon, return None
            if elevation_rad < 0:
                return None
            
            elevation = np.degrees(elevation_rad)
            
            # Calculate sun azimuth angle
            azimuth_rad = np.arccos(
                (np.sin(decl_rad) - np.sin(elevation_rad) * np.sin(lat_rad)) /
                (np.cos(elevation_rad) * np.cos(lat_rad))
            )
            
            # Correct azimuth for afternoon
            if hour_angle > 0:
                azimuth_rad = 2 * np.pi - azimuth_rad
                
            # Convert to 3D position
            distance = 30  # Distance from origin
            
            x = distance * np.cos(elevation_rad) * np.sin(azimuth_rad)  # East
            y = distance * np.cos(elevation_rad) * np.cos(azimuth_rad)  # North
            z = distance * np.sin(elevation_rad)  # Up
            
            # Adjust height relative to building
            z = max(z, building_height + 2)
            
            return [x, y, z]
            
        except Exception as e:
            print(f"Error in sun calculation: {e}")
            return None
    
    @staticmethod
    def get_time_range(latitude, day_of_year):
        """Calculate sunrise and sunset times"""
        try:
            lat_rad = np.radians(latitude)
            
            # Solar declination
            declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
            decl_rad = np.radians(declination)
            
            # Hour angle at sunrise/sunset
            cos_hour_angle = -np.tan(lat_rad) * np.tan(decl_rad)
            
            # Check for polar conditions
            if cos_hour_angle < -1:  # Polar day
                return 0.0, 24.0
            elif cos_hour_angle > 1:  # Polar night  
                return 12.0, 12.0
            
            hour_angle = np.arccos(cos_hour_angle)
            hours = np.degrees(hour_angle) / 15
            
            sunrise = 12 - hours
            sunset = 12 + hours
            
            return max(0, sunrise), min(24, sunset)
            
        except Exception:
            return 6.0, 18.0  # Default
    
    @staticmethod
    def get_background_color(decimal_hour, sunrise, sunset):
        """Get background color based on time of day - FIXED FOR BRIGHT NOON"""
        # Night time
        if decimal_hour < sunrise - 1 or decimal_hour > sunset + 1:
            return '#0a0a1f'  # Very dark blue
        
        # Pre-dawn (1 hour before sunrise)
        elif decimal_hour < sunrise - 0.5:
            return '#1a1a3a'  # Dark blue
        
        # Dawn (30 min before sunrise)
        elif decimal_hour < sunrise:
            return '#4a3a5a'  # Purple dawn
        
        # Sunrise (30 min after sunrise)
        elif decimal_hour < sunrise + 0.5:
            return '#ff6b4a'  # Orange sunrise
        
        # Early morning
        elif decimal_hour < sunrise + 2:
            return '#87CEEB'  # Sky blue
        
        # Mid-morning to mid-afternoon (BRIGHT DAYLIGHT)
        elif decimal_hour < sunset - 2:
            return '#87CEEB'  # Bright sky blue
        
        # Late afternoon
        elif decimal_hour < sunset - 0.5:
            return '#ffd4a3'  # Warm afternoon
        
        # Sunset
        elif decimal_hour < sunset:
            return '#ff8c42'  # Orange sunset
        
        # Twilight (30 min after sunset)
        elif decimal_hour < sunset + 0.5:
            return '#4a3a5a'  # Purple twilight
        
        # Dusk (1 hour after sunset)
        else:
            return '#1a1a3a'  # Dark blue
    
    @staticmethod
    def calculate_sun_intensity(sun_position, weather_factor=1.0):
        """Calculate sun intensity based on elevation"""
        if sun_position is None:
            return 0.0
            
        try:
            # Extract elevation from position
            z = sun_position[2]
            distance = np.linalg.norm(sun_position[:2])  # Horizontal distance
            
            if distance > 0:
                elevation_angle = np.arctan(z / distance)
            else:
                elevation_angle = np.pi / 2 if z > 0 else 0
            
            # Convert to degrees
            elevation_deg = np.degrees(elevation_angle)
            
            # More realistic intensity curve
            if elevation_deg <= 0:
                intensity = 0.0
            elif elevation_deg < 10:
                intensity = 0.3 * (elevation_deg / 10)
            elif elevation_deg < 30:
                intensity = 0.3 + 0.5 * ((elevation_deg - 10) / 20)
            else:
                # Full intensity for high sun
                intensity = 0.8 + 0.2 * min(1.0, (elevation_deg - 30) / 30)
            
            # Apply weather factor
            intensity *= weather_factor
            
            return max(0.0, min(1.0, intensity))
            
        except Exception as e:
            print(f"Error calculating sun intensity: {e}")
            return 0.8
    
    @staticmethod
    def calculate_sun_color(sun_position):
        """Calculate sun color based on elevation"""
        if sun_position is None:
            return [0.0, 0.0, 0.0]
            
        try:
            z = sun_position[2]
            distance = np.linalg.norm(sun_position[:2])
            
            if distance > 0:
                elevation_angle = np.arctan(z / distance)
                elevation_deg = np.degrees(elevation_angle)
            else:
                elevation_deg = 90 if z > 0 else 0
            
            # Realistic sun colors based on elevation
            if elevation_deg < 0:
                return [0.0, 0.0, 0.0]  # Below horizon
            elif elevation_deg < 2:
                return [1.0, 0.2, 0.0]  # Deep red
            elif elevation_deg < 5:
                return [1.0, 0.4, 0.1]  # Red-orange
            elif elevation_deg < 10:
                return [1.0, 0.6, 0.2]  # Orange
            elif elevation_deg < 15:
                return [1.0, 0.8, 0.4]  # Yellow-orange
            elif elevation_deg < 30:
                return [1.0, 0.95, 0.7]  # Warm yellow
            else:
                return [1.0, 1.0, 0.85]  # Bright yellow-white for noon
                
        except Exception as e:
            print(f"Error calculating sun color: {e}")
            return [1.0, 1.0, 0.7]
    
    @staticmethod
    def format_time(decimal_hour):
        """Convert decimal hour to HH:MM format"""
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"
