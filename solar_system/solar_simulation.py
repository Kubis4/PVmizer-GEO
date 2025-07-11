#!/usr/bin/env python3
"""
Complete Solar Simulation Module - OPTIMIZED VERSION - FIXED
Features: Sun positioning, Shadows, Performance Analysis
REMOVED: Particles, Complex effects for better performance
FIXED: All method names to match ModelTab expectations
"""
import numpy as np
import pyvista as pv
import math
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class AdvancedSolarVisualization(QObject):
    """Complete solar visualization - OPTIMIZED for performance - FIXED"""
    
    performance_updated = pyqtSignal(float, float, float)
    
    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        
        # Building and panels
        self.building_mesh = None
        self.solar_panels = []
        self.panel_meshes = []
        
        # Sun and lighting
        self.sun_mesh = None
        self.sun_light = None
        
        # Effects - SIMPLIFIED
        self.shadow_meshes = []
        
        # Parameters
        self.current_hour = 12
        self.current_day = 172
        self.latitude = 40.7128
        self.longitude = -74.0060
        self.panel_efficiency = 20.0
        self.panel_power = 330
        self.weather_factor = 1.0
        
        # Visual settings - OPTIMIZED
        self.shadows_enabled = True
        self.sunshafts_enabled = True
        
        print("✅ Optimized Solar Visualization initialized - FIXED")
    
    def set_building(self, building_mesh):
        """Set building for solar analysis - OPTIMIZED"""
        self.building_mesh = building_mesh
        if building_mesh:
            self.create_advanced_solar_panels()
            self.create_realistic_sun()  # FIXED: Method name matches ModelTab
            if self.shadows_enabled:
                self.update_comprehensive_shadows()  # FIXED: Method name matches ModelTab
    
    def create_advanced_solar_panels(self):
        """Create OPTIMIZED solar panel layout - FIXED METHOD NAME"""
        if not self.building_mesh:
            return
        
        try:
            self.clear_solar_panels()
            
            bounds = self.building_mesh.bounds
            panel_specs = {
                'width': 1.65,
                'height': 1.0,
                'thickness': 0.04,
                'power': self.panel_power,
                'efficiency': self.panel_efficiency / 100
            }
            
            # SIMPLIFIED panel layout
            panel_layout = self._simple_panel_layout(bounds, panel_specs)
            
            for i, panel_pos in enumerate(panel_layout):
                panel = self._create_simple_panel(panel_pos, panel_specs, i)
                if panel:
                    self.panel_meshes.append(panel)
                    self.solar_panels.append({
                        'mesh': panel,
                        'position': panel_pos,
                        'power_rating': panel_specs['power'],
                        'efficiency': panel_specs['efficiency']
                    })
            
            print(f"✅ Created {len(self.solar_panels)} optimized solar panels")
            
        except Exception as e:
            print(f"❌ Error creating optimized solar panels: {e}")
    
    def _simple_panel_layout(self, bounds, panel_specs):
        """SIMPLIFIED panel layout for performance"""
        x_min, x_max, y_min, y_max, z_min, z_max = bounds
        
        roof_width = x_max - x_min
        roof_height = y_max - y_min
        roof_level = z_max
        
        # Simple 2x2 or 3x3 layout
        panels_x = min(3, max(1, int(roof_width / 2)))
        panels_y = min(3, max(1, int(roof_height / 2)))
        
        panel_positions = []
        for i in range(panels_x):
            for j in range(panels_y):
                x = x_min + (i + 0.5) * roof_width / panels_x
                y = y_min + (j + 0.5) * roof_height / panels_y
                z = roof_level + 0.05
                
                panel_positions.append([x, y, z])
        
        return panel_positions
    
    def _create_simple_panel(self, position, specs, panel_id):
        """Create a SIMPLE solar panel for performance"""
        try:
            panel = pv.Cube(
                center=position,
                x_length=specs['width'],
                y_length=specs['height'],
                z_length=specs['thickness']
            )
            
            panel_actor = self.plotter.add_mesh(
                panel,
                color='#1a237e',  # Dark blue
                name=f'solar_panel_{panel_id}'
            )
            
            return panel_actor
            
        except Exception as e:
            print(f"❌ Error creating simple panel {panel_id}: {e}")
            return None
    
    def create_realistic_sun(self):
        """Create OPTIMIZED sun - MORE YELLOW, CLOSER - FIXED METHOD NAME"""
        try:
            if self.sun_mesh:
                try:
                    self.plotter.remove_actor('sun')
                except:
                    pass
            
            sun_pos = self.calculate_precise_sun_position()
            
            # Simple yellow sun
            sun_core = pv.Sphere(radius=2, center=sun_pos)
            
            self.sun_mesh = self.plotter.add_mesh(
                sun_core,
                color='#FFFF00',  # Pure yellow
                name='sun'
            )
            
            self._setup_realistic_lighting(sun_pos)
            
            print(f"✅ Optimized yellow sun created at {sun_pos}")
            
        except Exception as e:
            print(f"❌ Error creating optimized sun: {e}")
    
    def calculate_precise_sun_position(self):
        """Calculate OPTIMIZED sun position - CLOSER - FIXED METHOD NAME"""
        try:
            # Use the optimized solar calculations
            try:
                from solar_system.solar_calculations import SolarCalculations
                return SolarCalculations.calculate_sun_position(
                    self.current_hour,
                    self.current_day,
                    self.latitude
                )
            except ImportError:
                # Fallback calculation
                return self._fallback_sun_position()
        except Exception as e:
            print(f"❌ Error calculating optimized sun position: {e}")
            return [15, 15, 8]  # Closer default position
    
    def _fallback_sun_position(self):
        """Fallback sun position calculation"""
        try:
            # Simple sun position calculation
            hour_angle = 15 * (self.current_hour - 12)
            elevation = 45  # degrees
            azimuth = hour_angle
            
            # Convert to cartesian - CLOSER
            distance = 25
            x = distance * math.cos(math.radians(elevation)) * math.sin(math.radians(azimuth))
            y = distance * math.cos(math.radians(elevation)) * math.cos(math.radians(azimuth))
            z = max(5, distance * math.sin(math.radians(elevation)))
            
            return [x, y, z]
        except Exception:
            return [15, 15, 8]
    
    def _setup_realistic_lighting(self, sun_pos):
        """Setup OPTIMIZED lighting system - FIXED METHOD NAME"""
        try:
            if hasattr(self.plotter, 'remove_all_lights'):
                self.plotter.remove_all_lights()
            
            # Simple lighting setup
            self.plotter.add_light(pv.Light(
                position=sun_pos,
                focal_point=(0, 0, 0),
                color=[1.0, 1.0, 0.0],  # Yellow light
                intensity=1.0
            ))
            
            # Ambient light
            self.plotter.add_light(pv.Light(
                position=(0, 0, 20),
                focal_point=(0, 0, 0),
                color=[0.7, 0.8, 1.0],
                intensity=0.4
            ))
            
        except Exception as e:
            print(f"❌ Error setting up optimized lighting: {e}")
    
    def update_comprehensive_shadows(self):
        """Update SIMPLE shadow system for performance - FIXED METHOD NAME"""
        if not self.shadows_enabled or not self.building_mesh:
            return
        
        try:
            self.clear_shadows()
            
            sun_pos = self.calculate_precise_sun_position()
            
            # Simple building shadow
            building_shadow = self._calculate_building_shadow(sun_pos)
            if building_shadow:
                shadow_actor = self.plotter.add_mesh(
                    building_shadow,
                    color='black',
                    opacity=0.3,
                    name='building_shadow'
                )
                self.shadow_meshes.append(shadow_actor)
            
            print("✅ Simple shadows updated")
            
        except Exception as e:
            print(f"❌ Error updating simple shadows: {e}")
    
    def _calculate_building_shadow(self, sun_pos):
        """Calculate SIMPLE building shadow for performance"""
        try:
            if not self.building_mesh:
                return None
            
            bounds = self.building_mesh.bounds
            x_min, x_max, y_min, y_max, z_min, z_max = bounds
            
            # Simple shadow calculation
            if sun_pos[2] <= 0:
                return None
                
            shadow_length = (z_max - z_min) / max(0.1, sun_pos[2] / 10)
            
            shadow_points = np.array([
                [x_min - shadow_length, y_min - shadow_length, 0.01],
                [x_max - shadow_length, y_min - shadow_length, 0.01],
                [x_max - shadow_length, y_max - shadow_length, 0.01],
                [x_min - shadow_length, y_max - shadow_length, 0.01]
            ])
            
            shadow = pv.PolyData(shadow_points)
            shadow.faces = np.array([4, 0, 1, 2, 3])
            
            return shadow
            
        except Exception as e:
            print(f"❌ Error calculating simple building shadow: {e}")
            return None
    
    def calculate_solar_performance(self):
        """Calculate SIMPLIFIED solar performance"""
        try:
            if not self.solar_panels:
                return 0, 0, 0
            
            # Simplified performance calculation
            base_power_per_panel = 0.33  # kW
            num_panels = len(self.solar_panels)
            
            # Time and weather adjustments
            if 6 <= self.current_hour <= 18:
                time_factor = 1.0
            else:
                time_factor = 0.1
            
            weather_factor = self.weather_factor
            
            total_power = num_panels * base_power_per_panel * time_factor * weather_factor
            daily_energy = total_power * 8  # Simplified daily calculation
            efficiency = min(100, total_power / (num_panels * 0.4) * 100) if num_panels > 0 else 0
            
            self.performance_updated.emit(total_power, daily_energy, efficiency)
            
            return total_power, daily_energy, efficiency
            
        except Exception as e:
            print(f"❌ Error calculating solar performance: {e}")
            return 0, 0, 0
    
    # Control methods - OPTIMIZED with FIXED method names
    def set_time(self, hour):
        """Update time - OPTIMIZED"""
        self.current_hour = hour
        self.create_realistic_sun()
        if self.shadows_enabled:
            self.update_comprehensive_shadows()
    
    def set_day(self, day):
        """Update day - OPTIMIZED"""
        self.current_day = day
        self.create_realistic_sun()
        if self.shadows_enabled:
            self.update_comprehensive_shadows()
    
    def set_location(self, lat, lon):
        """Update location - OPTIMIZED"""
        self.latitude = lat
        self.longitude = lon
        self.create_realistic_sun()
        if self.shadows_enabled:
            self.update_comprehensive_shadows()
    
    def set_weather_factor(self, factor):
        """Set weather factor - OPTIMIZED"""
        self.weather_factor = max(0.0, min(1.0, factor))
        self.create_realistic_sun()
    
    def set_visual_effects(self, shadows=None, sunshafts=None, reflections=None):
        """Toggle visual effects - OPTIMIZED"""
        if shadows is not None:
            self.shadows_enabled = shadows
            if shadows:
                self.update_comprehensive_shadows()
            else:
                self.clear_shadows()
        
        if sunshafts is not None:
            self.sunshafts_enabled = sunshafts
    
    # Cleanup methods - OPTIMIZED
    def clear_solar_panels(self):
        """Clear all solar panels - OPTIMIZED"""
        try:
            for i in range(len(self.panel_meshes)):
                try:
                    self.plotter.remove_actor(f'solar_panel_{i}')
                except:
                    pass
            
            self.solar_panels.clear()
            self.panel_meshes.clear()
            
        except Exception as e:
            print(f"❌ Error clearing solar panels: {e}")
    
    def clear_shadows(self):
        """Clear all shadow meshes - OPTIMIZED"""
        try:
            try:
                self.plotter.remove_actor('building_shadow')
            except:
                pass
            
            self.shadow_meshes.clear()
            
        except Exception as e:
            print(f"❌ Error clearing shadows: {e}")
    
    def clear_all(self):
        """Clear everything - OPTIMIZED"""
        try:
            self.clear_solar_panels()
            self.clear_shadows()
            
            # Clear sun
            if self.sun_mesh:
                try:
                    self.plotter.remove_actor('sun')
                except:
                    pass
            
            print("✅ Optimized solar visualization cleared")
            
        except Exception as e:
            print(f"❌ Error clearing all: {e}")

    # Additional methods that might be called by ModelTab
    def create_volumetric_sunshafts(self, sun_pos):
        """Create simple sunshafts - OPTIMIZED (no particles)"""
        try:
            if not self.sunshafts_enabled:
                return
            
            # Remove existing sunshafts
            try:
                self.plotter.remove_actor('sunshafts')
            except:
                pass
            
            # Create simple cone for sunshafts
            target_point = np.array([0, 0, 0])
            sun_position = np.array(sun_pos)
            
            direction = target_point - sun_position
            direction_length = np.linalg.norm(direction)
            
            if direction_length > 0:
                direction = direction / direction_length
            else:
                direction = np.array([0, 0, -1])
            
            # Create simple sunshaft cone
            cone_height = min(15, direction_length * 0.5)
            cone_radius = cone_height * 0.15
            cone_center = sun_position + direction * 2
            
            sunshaft_cone = pv.Cone(
                center=cone_center,
                direction=direction,
                height=cone_height,
                radius=cone_radius,
                resolution=8  # Low resolution for performance
            )
            
            self.plotter.add_mesh(
                sunshaft_cone,
                color='#FFFF99',  # Yellow sunshafts
                opacity=0.05,  # Very subtle
                name='sunshafts'
            )
            
            print("✅ Simple sunshafts created (no particles)")
            
        except Exception as e:
            print(f"❌ Error creating sunshafts: {e}")
