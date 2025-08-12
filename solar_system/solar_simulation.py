#!/usr/bin/env python3
"""
Complete Solar Simulation Module - ENHANCED VERSION
Improved solar visualization with proper lighting integration
"""
import numpy as np
import pyvista as pv
import math
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class AdvancedSolarVisualization(QObject):
    """Enhanced solar visualization with lighting integration"""

    performance_updated = pyqtSignal(float, float, float)

    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        
        # Building and panels
        self.building_mesh = None
        self.building_actor = None
        self.original_building_colors = None
        self.solar_panels = []
        self.panel_meshes = []
        self.panel_actors = []
        
        # Sun visual and position
        self.sun_sphere = None
        self.sun_actor = None
        self.sun_position = None
        
        # Shadow overlay
        self.shadow_overlay = None
        self.shadow_actor = None
        
        # Solar calculation data
        self.face_normals = None
        self.face_centers = None
        self.panel_irradiance = []
        
        # Parameters
        self.current_hour = 12
        self.current_day = 172
        self.latitude = 48.3061  # Nitra
        self.longitude = 18.0764
        self.panel_efficiency = 20.0
        self.panel_power = 330
        self.weather_factor = 1.0
        
        # Visual settings
        self.shadows_enabled = True
        self.show_irradiance = True
        
        # Lighting system integration
        self.lighting_system = None
        
        print("✅ Enhanced Solar Visualization initialized")

    def set_lighting_system(self, lighting_system):
        """Set the lighting system for integration"""
        self.lighting_system = lighting_system
        print("🔗 Lighting system integrated")

    def set_building(self, building_mesh):
        """Set building and prepare for solar simulation"""
        self.building_mesh = building_mesh
        if building_mesh:
            self._prepare_building_for_simulation()
            self.create_advanced_solar_panels()
            self.update_solar_simulation()

    def _prepare_building_for_simulation(self):
        """Prepare building mesh for color-based shading"""
        try:
            if not self.building_mesh:
                return
            
            # Compute normals for each face
            self.building_mesh.compute_normals(
                cell_normals=True,
                point_normals=True,
                split_vertices=True
            )
            
            # Store face normals and centers
            self.face_normals = self.building_mesh.cell_normals
            self.face_centers = self.building_mesh.cell_centers().points
            
            # Store original colors
            if 'colors' in self.building_mesh.cell_data:
                self.original_building_colors = self.building_mesh.cell_data['colors'].copy()
            else:
                n_cells = self.building_mesh.n_cells
                self.original_building_colors = np.ones((n_cells, 3)) * 0.7
            
            print(f"✅ Building prepared: {self.building_mesh.n_cells} faces")
            
        except Exception as e:
            print(f"❌ Error preparing building: {e}")

    def update_solar_simulation(self):
        """Main update method with lighting integration"""
        try:
            # Calculate sun position
            self.sun_position = self.calculate_precise_sun_position()
            
            # Update sun visual
            self._update_sun_visual()
            
            # Update lighting system if available
            if self.lighting_system and self.sun_position:
                solar_settings = self._get_solar_settings()
                self.lighting_system.setup_solar_lighting(self.sun_position, solar_settings)
                self.lighting_system.update_background_color(solar_settings)
            
            # Calculate solar effects
            if self.building_mesh and self.sun_position and self.sun_position[2] > 0:
                self._apply_solar_shading(self.sun_position)
            
            # Calculate panel performance
            if self.solar_panels:
                self._calculate_panel_irradiance(self.sun_position)
            
            # Update shadows
            if self.shadows_enabled:
                self._update_shadow_overlay(self.sun_position)
            
            # Calculate performance metrics
            self.calculate_solar_performance()
            
        except Exception as e:
            print(f"❌ Error updating solar simulation: {e}")

    def _get_solar_settings(self):
        """Get current solar settings for lighting system"""
        try:
            from solar_system.solar_calculations import SolarCalculations
            sunrise, sunset = SolarCalculations.get_time_range(
                self.latitude, self.current_day, self.longitude
            )
        except:
            sunrise, sunset = 6.0, 18.0
        
        return {
            'current_hour': self.current_hour,
            'current_day': self.current_day,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'weather_factor': self.weather_factor,
            'sunrise': sunrise,
            'sunset': sunset
        }

    def _update_sun_visual(self):
        """Update sun visual indicator"""
        try:
            # Remove old sun
            try:
                self.plotter.remove_actor('sun_indicator')
            except:
                pass
            
            if not self.sun_position or self.sun_position[2] <= 0:
                return  # Sun below horizon
            
            # Create sun sphere
            self.sun_sphere = pv.Sphere(
                radius=2,
                center=self.sun_position,
                theta_resolution=16,
                phi_resolution=16
            )
            
            # Sun color based on elevation
            sun_color = self._get_sun_display_color()
            
            # Add sun as bright visual
            self.sun_actor = self.plotter.add_mesh(
                self.sun_sphere,
                color=sun_color,
                name='sun_indicator',
                ambient=1.0,  # Self-illuminated
                diffuse=0,
                specular=0,
                opacity=0.9
            )
            
        except Exception as e:
            print(f"❌ Error updating sun visual: {e}")

    def _get_sun_display_color(self):
        """Get sun color for display"""
        if not self.sun_position:
            return '#FFD700'
        
        elevation = self._calculate_elevation(self.sun_position)
        
        if elevation < 5:
            return '#FF4500'  # Red-orange at horizon
        elif elevation < 15:
            return '#FFA500'  # Orange
        elif elevation < 30:
            return '#FFD700'  # Gold
        else:
            return '#FFFF99'  # Bright yellow

    def _apply_solar_shading(self, sun_pos):
        """Apply realistic shading based on sun position"""
        try:
            if not self.face_normals.any():
                return
            
            # This method can be used for advanced color-based shading
            # For now, we let the lighting system handle the actual lighting
            # This could be expanded for specialized material rendering
            
            pass  # Lighting system handles this now
            
        except Exception as e:
            print(f"❌ Error applying solar shading: {e}")

    def _calculate_panel_irradiance(self, sun_pos):
        """Calculate realistic irradiance for each solar panel"""
        try:
            if not sun_pos or sun_pos[2] <= 0:
                self.panel_irradiance = [0] * len(self.solar_panels)
                return
            
            self.panel_irradiance = []
            
            # Sun direction
            sun_dir = np.array(sun_pos) / np.linalg.norm(sun_pos)
            
            # Solar parameters
            solar_constant = 1000  # W/m²
            elevation = self._calculate_elevation(sun_pos)
            
            if elevation > 0:
                air_mass = 1 / np.sin(np.radians(max(elevation, 1)))
                atmospheric_transmission = 0.75 ** air_mass
            else:
                atmospheric_transmission = 0
            
            for i, panel in enumerate(self.solar_panels):
                # Panel normal (flat on roof)
                panel_normal = np.array(panel.get('normal', [0, 0, 1]))
                
                # Angle of incidence
                cos_theta = np.dot(panel_normal, sun_dir)
                cos_theta = max(0, cos_theta)
                
                # Calculate irradiance
                direct_irradiance = (
                    solar_constant * 
                    atmospheric_transmission * 
                    cos_theta * 
                    self.weather_factor
                )
                
                diffuse_irradiance = 100 * atmospheric_transmission * self.weather_factor
                total_irradiance = direct_irradiance + diffuse_irradiance
                
                self.panel_irradiance.append(total_irradiance)
                
                # Update panel color
                if self.show_irradiance and i < len(self.panel_actors):
                    self._update_panel_color(i, total_irradiance)
            
        except Exception as e:
            print(f"❌ Error calculating panel irradiance: {e}")

    def _update_panel_color(self, panel_index, irradiance):
        """Update panel color based on irradiance"""
        try:
            normalized = min(1.0, irradiance / 1000)
            
            # Color gradient: blue (low) to yellow (high)
            if normalized < 0.5:
                r = 0
                g = normalized * 2 * 0.5
                b = 0.5 + normalized * 0.5
            else:
                r = (normalized - 0.5) * 2
                g = 0.5 + (normalized - 0.5)
                b = 1.0 - (normalized - 0.5) * 2
            
            color = [r, g, b]
            
            if panel_index < len(self.panel_meshes):
                actor = self.panel_meshes[panel_index]
                if actor and hasattr(actor, 'GetProperty'):
                    actor.GetProperty().SetColor(color)
            
        except Exception as e:
            print(f"❌ Error updating panel color: {e}")

    def _update_shadow_overlay(self, sun_pos):
        """Create shadow overlay effect"""
        try:
            if not self.building_mesh or not sun_pos or sun_pos[2] <= 0:
                if self.shadow_actor:
                    self.shadow_actor.SetVisibility(False)
                return
            
            # Remove old shadow
            try:
                self.plotter.remove_actor('shadow_overlay')
            except:
                pass
            
            # Create shadow plane
            bounds = self.building_mesh.bounds
            x_min, x_max, y_min, y_max = bounds[:4]
            
            # Shadow projection
            shadow_length = 8 / max(0.1, sun_pos[2] / 8)
            offset_x = -sun_pos[0] / 15 * shadow_length
            offset_y = -sun_pos[1] / 15 * shadow_length
            
            shadow_points = np.array([
                [x_min + offset_x, y_min + offset_y, 0.01],
                [x_max + offset_x, y_min + offset_y, 0.01],
                [x_max + offset_x, y_max + offset_y, 0.01],
                [x_min + offset_x, y_max + offset_y, 0.01]
            ])
            
            shadow_mesh = pv.PolyData(shadow_points)
            shadow_mesh.faces = np.array([4, 0, 1, 2, 3])
            
            # Shadow opacity
            elevation = self._calculate_elevation(sun_pos)
            opacity = 0.4 * (1 - elevation / 90) if elevation > 0 else 0
            
            self.shadow_actor = self.plotter.add_mesh(
                shadow_mesh,
                color='black',
                opacity=opacity,
                name='shadow_overlay'
            )
            
        except Exception as e:
            print(f"❌ Error updating shadow: {e}")

    def calculate_precise_sun_position(self):
        """Calculate accurate sun position"""
        try:
            from solar_system.solar_calculations import SolarCalculations
            return SolarCalculations.calculate_sun_position(
                self.current_hour,
                self.current_day,
                self.latitude,
                self.longitude
            )
        except Exception as e:
            print(f"Error calculating sun position: {e}")
            # Fallback calculation
            hour_angle = 15 * (self.current_hour - 12)
            elevation = max(0, 45 - abs(hour_angle) / 3)
            
            if elevation <= 0:
                return None
            
            distance = 25
            azimuth_rad = math.radians(hour_angle + 180)
            elevation_rad = math.radians(elevation)
            
            x = distance * math.cos(elevation_rad) * math.sin(azimuth_rad)
            y = distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
            z = distance * math.sin(elevation_rad)
            
            return [x, y, max(0, z)]

    def _calculate_elevation(self, sun_pos):
        """Calculate sun elevation angle"""
        if not sun_pos:
            return 0
        horizontal_dist = np.sqrt(sun_pos[0]**2 + sun_pos[1]**2)
        if horizontal_dist > 0:
            return np.degrees(np.arctan(sun_pos[2] / horizontal_dist))
        return 90 if sun_pos[2] > 0 else 0

    def create_advanced_solar_panels(self):
        """Create solar panels with performance visualization"""
        if not self.building_mesh:
            return
        
        try:
            self.clear_solar_panels()
            
            bounds = self.building_mesh.bounds
            x_min, x_max, y_min, y_max, z_min, z_max = bounds
            
            # Panel specifications
            panel_width = 1.65
            panel_height = 1.0
            panel_thickness = 0.04
            
            roof_level = z_max + 0.05
            margin = 0.5
            spacing = 0.2
            
            panels_x = 3
            panels_y = 2
            
            for i in range(panels_x):
                for j in range(panels_y):
                    x = x_min + margin + i * (panel_width + spacing) + panel_width/2
                    y = y_min + margin + j * (panel_height + spacing) + panel_height/2
                    z = roof_level
                    
                    if x + panel_width/2 > x_max - margin or y + panel_height/2 > y_max - margin:
                        continue
                    
                    # Create panel mesh
                    panel = pv.Cube(
                        center=[x, y, z],
                        x_length=panel_width,
                        y_length=panel_height,
                        z_length=panel_thickness
                    )
                    
                    # Add panel
                    actor = self.plotter.add_mesh(
                        panel,
                        color='#1a237e',
                        name=f'solar_panel_{i}_{j}',
                        opacity=0.9,
                        ambient=0.8,
                        diffuse=0.2,
                        specular=0.1,
                        specular_power=10
                    )
                    
                    self.panel_actors.append(actor)
                    self.panel_meshes.append(actor)
                    self.solar_panels.append({
                        'position': [x, y, z],
                        'normal': [0, 0, 1],
                        'area': panel_width * panel_height,
                        'power_rating': self.panel_power,
                        'efficiency': self.panel_efficiency / 100
                    })
            
            print(f"✅ Created {len(self.solar_panels)} solar panels")
            
        except Exception as e:
            print(f"❌ Error creating panels: {e}")

    def calculate_solar_performance(self):
        """Calculate system performance"""
        try:
            if not self.panel_irradiance:
                return 0, 0, 0
            
            total_power = 0
            for i, panel in enumerate(self.solar_panels):
                if i < len(self.panel_irradiance):
                    irradiance = self.panel_irradiance[i] / 1000  # kW/m²
                    area = panel['area']
                    efficiency = panel['efficiency']
                    
                    panel_power = irradiance * area * efficiency
                    total_power += panel_power
            
            # Daily energy estimate
            daylight_hours = 10
            daily_energy = total_power * daylight_hours * 0.7
            
            # System efficiency
            max_possible = len(self.solar_panels) * 0.33
            efficiency = (total_power / max_possible * 100) if max_possible > 0 else 0
            
            self.performance_updated.emit(total_power, daily_energy, efficiency)
            
            return total_power, daily_energy, efficiency
            
        except Exception as e:
            print(f"❌ Error calculating performance: {e}")
            return 0, 0, 0

    # Control methods
    def set_time(self, hour):
        """Update time and recalculate"""
        self.current_hour = hour
        self.update_solar_simulation()

    def set_day(self, day):
        """Update day and recalculate"""
        self.current_day = day
        self.update_solar_simulation()

    def set_location(self, lat, lon):
        """Update location"""
        self.latitude = lat
        self.longitude = lon
        self.update_solar_simulation()

    def set_weather_factor(self, factor):
        """Set weather factor"""
        self.weather_factor = max(0.0, min(1.0, factor))
        self.update_solar_simulation()
        # Also update lighting system
        if self.lighting_system:
            self.lighting_system.update_weather_lighting(factor)

    def set_visual_effects(self, shadows=None, sunshafts=None, reflections=None):
        """Toggle visual effects"""
        if shadows is not None:
            self.shadows_enabled = shadows
            self.update_solar_simulation()

    # Compatibility methods
    def create_realistic_sun(self):
        """Compatibility method"""
        self.update_solar_simulation()

    def update_comprehensive_shadows(self):
        """Compatibility method"""
        if self.sun_position:
            self._update_shadow_overlay(self.sun_position)

    def update_sun_position(self):
        """Force sun position update"""
        self.update_solar_simulation()

    # Cleanup methods
    def clear_solar_panels(self):
        """Clear all panels"""
        for i in range(10):
            for j in range(10):
                try:
                    self.plotter.remove_actor(f'solar_panel_{i}_{j}')
                except:
                    pass
        
        self.solar_panels.clear()
        self.panel_meshes.clear()
        self.panel_actors.clear()
        self.panel_irradiance.clear()

    def clear_shadows(self):
        """Clear shadows"""
        try:
            self.plotter.remove_actor('shadow_overlay')
        except:
            pass
        self.shadow_actor = None

    def clear_all(self):
        """Clear everything"""
        self.clear_solar_panels()
        self.clear_shadows()
        try:
            self.plotter.remove_actor('sun_indicator')
            self.plotter.remove_actor('building')
        except:
            pass
        print("✅ Visualization cleared")
