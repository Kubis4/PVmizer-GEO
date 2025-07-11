import numpy as np

class PerformanceCalculator:
    """Handles solar panel performance calculations"""
    
    @staticmethod
    def calculate_angle_factor(angle_degrees):
        """Calculate efficiency factor based on panel tilt angle."""
        if angle_degrees < 5:
            return 0.85  # 15% reduction compared to optimal tilt
        elif angle_degrees < 10:
            return 0.88
        elif angle_degrees < 20:
            return 0.94
        elif angle_degrees < 30:
            return 0.98
        elif angle_degrees < 40:
            return 1.0   # Optimal range
        elif angle_degrees < 50:
            return 0.97
        elif angle_degrees < 60:
            return 0.91
        else:
            return 0.84  # Very steep angle
    
    @staticmethod
    def calculate_orientation_factor(orientation_degrees):
        """Calculate efficiency factor based on panel orientation (azimuth)."""
        # Normalize orientation to 0-360°
        orientation_normalized = orientation_degrees % 360
        
        # Northern hemisphere calculations (south is optimal)
        if 157.5 <= orientation_normalized <= 202.5:  # South ±22.5°
            return 1.0  # Optimal - south facing (100%)
        elif 135 <= orientation_normalized < 157.5:  # Southeast quadrant 1
            return 0.94  # Very good - close to south (94%)
        elif 202.5 < orientation_normalized <= 225:  # Southwest quadrant 1
            return 0.94  # Very good - close to south (94%)
        elif 112.5 <= orientation_normalized < 135:  # Southeast quadrant 2
            return 0.88  # Good - further from south (88%)
        elif 225 < orientation_normalized <= 247.5:  # Southwest quadrant 2
            return 0.88  # Good - further from south (88%)
        elif 90 <= orientation_normalized < 112.5:  # East
            return 0.82  # Moderate - east facing (82%)
        elif 247.5 < orientation_normalized <= 270:  # West
            return 0.82  # Moderate - west facing (82%)
        elif 67.5 <= orientation_normalized < 90:  # East-northeast
            return 0.76  # Below average (76%)
        elif 270 < orientation_normalized <= 292.5:  # West-northwest
            return 0.76  # Below average (76%)
        elif 45 <= orientation_normalized < 67.5:  # Northeast
            return 0.70  # Poor (70%)
        elif 292.5 < orientation_normalized <= 315:  # Northwest
            return 0.70  # Poor (70%)
        elif 22.5 <= orientation_normalized < 45:  # North-northeast
            return 0.63  # Very poor (63%)
        elif 315 < orientation_normalized <= 337.5:  # North-northwest
            return 0.63  # Very poor (63%)
        else:  # North ±22.5°
            return 0.55  # Worst - north facing (55%)
    
    @staticmethod
    def calculate_chimney_impact_factor(roof_obj, active_sides=None):
        """Calculate impact factor from chimneys on system performance."""
        impact_factor = 1.0
        
        if not hasattr(roof_obj, 'obstacles') or not roof_obj.obstacles:
            return impact_factor
        
        chimney_count = 0
        total_chimney_size = 0
        
        # Analyze each chimney
        for obstacle in roof_obj.obstacles:
            if not hasattr(obstacle, 'type') or obstacle.type != "Chimney":
                continue
                
            # Skip if not on active sides
            if active_sides and hasattr(obstacle, 'side') and obstacle.side not in active_sides:
                continue
                
            chimney_count += 1
            
            # Get chimney dimensions
            if hasattr(obstacle, 'dimensions'):
                chimney_width, chimney_length, chimney_height = obstacle.dimensions
                chimney_size = chimney_width * chimney_length
                height_factor = min(1.5, max(1.0, chimney_height / 1.0))
            else:
                chimney_size = 0.36  # Default size
                height_factor = 1.0
                
            total_chimney_size += chimney_size * height_factor
        
        if chimney_count == 0:
            return impact_factor
        
        # Estimate roof area
        roof_area = 25.0  # Default
        if hasattr(roof_obj, 'length') and hasattr(roof_obj, 'width'):
            if active_sides:
                single_side_area = roof_obj.length * roof_obj.width / 4
                roof_area = single_side_area * len(active_sides)
            else:
                roof_area = roof_obj.length * roof_obj.width
        
        # Calculate impact
        base_impact = 0.02 * chimney_count
        shading_multiplier = 2.0
        size_impact = (total_chimney_size * shading_multiplier) / roof_area
        total_impact = min(0.25, base_impact + size_impact)
        
        return 1.0 - total_impact
    
    @staticmethod
    def calculate_performance_data(panel_count, panel_power, angle_degrees=None, 
                                 orientation_degrees=None, roof_obj=None, active_sides=None):
        """Calculate comprehensive performance data"""
        if panel_count == 0:
            return {'panel_count': 0}
        
        # Basic calculations
        system_power_w = panel_power * panel_count
        system_power_kw = system_power_w / 1000
        
        # Efficiency factors
        angle_factor = 1.0
        if angle_degrees is not None:
            angle_factor = PerformanceCalculator.calculate_angle_factor(angle_degrees)
        
        orientation_factor = 1.0
        if orientation_degrees is not None:
            orientation_factor = PerformanceCalculator.calculate_orientation_factor(orientation_degrees)
        
        chimney_factor = 1.0
        if roof_obj:
            chimney_factor = PerformanceCalculator.calculate_chimney_impact_factor(roof_obj, active_sides)
        
        # Energy production
        combined_factor = angle_factor * orientation_factor * chimney_factor
        annual_yield_base = 1200  # kWh per kWp per year
        performance_ratio = 0.8
        
        annual_energy_kwh = system_power_kw * annual_yield_base * performance_ratio * combined_factor
        daily_energy_kwh = annual_energy_kwh / 365
        
        return {
            'panel_count': panel_count,
            'panel_power_w': panel_power,
            'system_power_w': system_power_w,
            'system_power_kw': system_power_kw,
            'roof_angle_degrees': angle_degrees or 0,
            'angle_factor': angle_factor,
            'orientation_factor': orientation_factor,
            'chimney_factor': chimney_factor,
            'combined_factor': combined_factor,
            'annual_energy_kwh': annual_energy_kwh,
            'daily_energy_kwh': daily_energy_kwh
        }
