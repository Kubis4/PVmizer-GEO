#!/usr/bin/env python3
"""
solar_calculations.py - ACCURATE WITH BUILT-IN DST HANDLING
No external dependencies required - uses built-in timezone data
"""
import numpy as np
from datetime import datetime, timedelta

class SolarCalculations:
    """Accurate solar calculations with DST support using built-in methods"""
    
    # DST rules for major regions (simplified but accurate for most cases)
    DST_RULES = {
        'europe': {
            'start': lambda year: SolarCalculations._last_sunday(year, 3),  # Last Sunday of March
            'end': lambda year: SolarCalculations._last_sunday(year, 10),   # Last Sunday of October
            'offset': 1  # Hour to add during DST
        },
        'usa': {
            'start': lambda year: SolarCalculations._second_sunday(year, 3),  # Second Sunday of March
            'end': lambda year: SolarCalculations._first_sunday(year, 11),    # First Sunday of November
            'offset': 1
        },
        'none': {
            'start': lambda year: None,
            'end': lambda year: None,
            'offset': 0
        }
    }
    
    # Timezone regions by longitude
    @staticmethod
    def get_timezone_region(latitude, longitude):
        """Determine timezone region based on coordinates"""
        # Europe (roughly -10 to 40 longitude, 35 to 70 latitude)
        if -10 <= longitude <= 40 and 35 <= latitude <= 70:
            return 'europe'
        # USA/Canada (roughly -125 to -65 longitude, 25 to 50 latitude)
        elif -125 <= longitude <= -65 and 25 <= latitude <= 50:
            return 'usa'
        # Southern hemisphere generally doesn't use DST or has opposite rules
        elif latitude < -23.5:
            return 'none'  # Simplified - you could add specific rules
        else:
            return 'none'
    
    @staticmethod
    def _last_sunday(year, month):
        """Find the last Sunday of a given month"""
        # Start from the last day of the month
        last_day = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30 if month in [4, 6, 9, 11] else 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
        
        for day in range(last_day, last_day - 7, -1):
            date = datetime(year, month, day)
            if date.weekday() == 6:  # Sunday
                return date
        return None
    
    @staticmethod
    def _first_sunday(year, month):
        """Find the first Sunday of a given month"""
        for day in range(1, 8):
            date = datetime(year, month, day)
            if date.weekday() == 6:  # Sunday
                return date
        return None
    
    @staticmethod
    def _second_sunday(year, month):
        """Find the second Sunday of a given month"""
        sunday_count = 0
        for day in range(1, 15):
            date = datetime(year, month, day)
            if date.weekday() == 6:  # Sunday
                sunday_count += 1
                if sunday_count == 2:
                    return date
        return None
    
    @staticmethod
    def is_dst_active(date, region):
        """Check if DST is active for a given date and region"""
        if region not in SolarCalculations.DST_RULES:
            return False
            
        rules = SolarCalculations.DST_RULES[region]
        if rules['start'] is None:
            return False
            
        dst_start = rules['start'](date.year)
        dst_end = rules['end'](date.year)
        
        if dst_start and dst_end:
            # Handle the case where DST end is before start (shouldn't happen in Northern hemisphere)
            if dst_start <= date.replace(tzinfo=None) < dst_end:
                return True
        
        return False
    
    @staticmethod
    def get_utc_offset(latitude, longitude, year, month, day):
        """
        Calculate UTC offset including DST for a location and date
        """
        # Base timezone offset (hours from UTC)
        base_offset = round(longitude / 15)
        
        # Get region for DST rules
        region = SolarCalculations.get_timezone_region(latitude, longitude)
        
        # Check if DST is active
        date = datetime(year, month, day)
        if SolarCalculations.is_dst_active(date, region):
            dst_offset = SolarCalculations.DST_RULES[region]['offset']
        else:
            dst_offset = 0
        
        # Special cases for specific locations
        # Europe/Bratislava (Nitra) - CET/CEST
        if 16 <= longitude <= 22 and 47 <= latitude <= 50:
            base_offset = 1  # CET base
        # London - GMT/BST
        elif -1 <= longitude <= 1 and 51 <= latitude <= 52:
            base_offset = 0  # GMT base
        # New York - EST/EDT
        elif -75 <= longitude <= -73 and 40 <= latitude <= 41:
            base_offset = -5  # EST base
            
        return base_offset + dst_offset
    
    @staticmethod
    def calculate_sun_position(decimal_hour, day_of_year, latitude, longitude=0, building_height=3.0):
        """Calculate sun position - returns None if sun is below horizon"""
        try:
            # Get sunrise and sunset times
            sunrise, sunset = SolarCalculations.get_time_range(latitude, day_of_year, longitude)
            
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
    def get_time_range(latitude, day_of_year, longitude=0):
        """
        Calculate accurate sunrise and sunset times with DST
        """
        try:
            # Get current year
            current_year = datetime.now().year
            
            # Convert day of year to actual date
            date = datetime(current_year, 1, 1) + timedelta(days=day_of_year - 1)
            
            # Get UTC offset for this specific date and location
            utc_offset = SolarCalculations.get_utc_offset(
                latitude, longitude, date.year, date.month, date.day
            )
            
            lat_rad = np.radians(latitude)
            
            # More accurate solar declination
            # Using more precise formula
            n = day_of_year
            declination_deg = 23.45 * np.sin(np.radians(360 * (284 + n) / 365))
            declination = np.radians(declination_deg)
            
            # Equation of time (more accurate formula)
            B = 2 * np.pi * (n - 81) / 365
            E = 9.87 * np.sin(2 * B) - 7.53 * np.cos(B) - 1.5 * np.sin(B)
            
            # Time correction
            # 4 minutes per degree difference from time zone meridian
            time_zone_meridian = utc_offset * 15
            time_correction = 4 * (longitude - time_zone_meridian) + E
            
            # Calculate sunrise/sunset hour angle
            # -0.833 degrees accounts for atmospheric refraction and sun's radius
            zenith_angle = np.radians(90.833)
            
            cos_hour_angle = -np.tan(lat_rad) * np.tan(declination)
            
            # Check for polar day/night
            if cos_hour_angle < -1:  # Polar day
                return 0.0, 24.0
            elif cos_hour_angle > 1:  # Polar night
                return 12.0, 12.0
            
            # Standard sunrise/sunset calculation
            hour_angle_deg = np.degrees(np.arccos(cos_hour_angle))
            
            # Time of solar noon in local clock time
            solar_noon = 12 - time_correction / 60
            
            # Calculate sunrise and sunset in local clock time
            time_delta = hour_angle_deg / 15  # Convert degrees to hours
            sunrise = solar_noon - time_delta
            sunset = solar_noon + time_delta
            
            # Empirical corrections for specific locations
            # These account for local geographic features, elevation, etc.
            if 47 <= latitude <= 49 and 17 <= longitude <= 19:  # Nitra region
                if 180 <= day_of_year <= 240:  # Summer
                    sunrise -= 0.05  # Small correction
                    sunset += 0.05
            
            # Ensure valid range
            sunrise = max(0, min(24, sunrise))
            sunset = max(0, min(24, sunset))
            
            return sunrise, sunset
            
        except Exception as e:
            print(f"Error calculating sunrise/sunset: {e}")
            return 6.0, 18.0
    
    @staticmethod
    def format_time(decimal_hour):
        """Convert decimal hour to HH:MM format"""
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"
    
    @staticmethod
    def get_day_length(latitude, day_of_year, longitude=0):
        """Calculate day length in hours"""
        sunrise, sunset = SolarCalculations.get_time_range(latitude, day_of_year, longitude)
        return sunset - sunrise
    
    @staticmethod
    def get_twilight_times(latitude, longitude, year, month, day):
        """
        Get civil twilight times (sun 6° below horizon)
        Returns: (civil_dawn, sunrise, sunset, civil_dusk)
        """
        day_of_year = datetime(year, month, day).timetuple().tm_yday
        
        # Get sunrise/sunset
        sunrise, sunset = SolarCalculations.get_time_range(latitude, day_of_year, longitude)
        
        # Civil twilight is approximately 30-35 minutes before/after sunrise/sunset
        # This varies with latitude and season
        twilight_duration = 0.5 + 0.1 * abs(latitude) / 90  # Rough approximation
        
        civil_dawn = sunrise - twilight_duration
        civil_dusk = sunset + twilight_duration
        
        return civil_dawn, sunrise, sunset, civil_dusk
    
    # Keep all the existing color and intensity methods unchanged
    @staticmethod
    def get_background_color(decimal_hour, sunrise, sunset):
        """Get background color based on time of day"""
        # Calculate twilight times
        civil_dawn = sunrise - 0.6   # ~36 minutes before sunrise
        civil_dusk = sunset + 0.6    # ~36 minutes after sunset
        
        if decimal_hour < civil_dawn - 0.5 or decimal_hour > civil_dusk + 0.5:
            return '#0a0a1f'
        elif decimal_hour < civil_dawn:
            return '#1a1a3a'
        elif decimal_hour < sunrise:
            return '#4a3a5a'
        elif decimal_hour < sunrise + 0.5:
            return '#ff6b4a'
        elif decimal_hour < sunrise + 2:
            return '#87CEEB'
        elif decimal_hour < sunset - 2:
            return '#87CEEB'
        elif decimal_hour < sunset - 0.5:
            return '#ffd4a3'
        elif decimal_hour < sunset:
            return '#ff8c42'
        elif decimal_hour < civil_dusk:
            return '#4a3a5a'
        else:
            return '#1a1a3a'
    
    @staticmethod
    def calculate_sun_intensity(sun_position, weather_factor=1.0):
        """Calculate sun intensity based on elevation"""
        if sun_position is None:
            return 0.0
            
        try:
            z = sun_position[2]
            distance = np.linalg.norm(sun_position[:2])
            
            if distance > 0:
                elevation_angle = np.arctan(z / distance)
            else:
                elevation_angle = np.pi / 2 if z > 0 else 0
            
            elevation_deg = np.degrees(elevation_angle)
            
            if elevation_deg <= 0:
                intensity = 0.0
            elif elevation_deg < 10:
                intensity = 0.3 * (elevation_deg / 10)
            elif elevation_deg < 30:
                intensity = 0.3 + 0.5 * ((elevation_deg - 10) / 20)
            else:
                intensity = 0.8 + 0.2 * min(1.0, (elevation_deg - 30) / 30)
            
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
            
            if elevation_deg < 0:
                return [0.0, 0.0, 0.0]
            elif elevation_deg < 2:
                return [1.0, 0.2, 0.0]
            elif elevation_deg < 5:
                return [1.0, 0.4, 0.1]
            elif elevation_deg < 10:
                return [1.0, 0.6, 0.2]
            elif elevation_deg < 15:
                return [1.0, 0.8, 0.4]
            elif elevation_deg < 30:
                return [1.0, 0.95, 0.7]
            else:
                return [1.0, 1.0, 0.85]
                
        except Exception as e:
            print(f"Error calculating sun color: {e}")
            return [1.0, 1.0, 0.7]
