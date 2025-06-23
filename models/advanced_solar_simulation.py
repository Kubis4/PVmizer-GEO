#!/usr/bin/env python3
"""
Advanced Solar Simulation with PyVista - FIXED VERSION
Features: Shadows, Sunshafts, Performance Analysis, Weather Integration
"""
import numpy as np
import pyvista as pv
import math
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class AdvancedSolarVisualization(QObject):
    """Advanced solar visualization with realistic lighting and performance analysis - FIXED"""
    
    performance_updated = pyqtSignal(float, float, float)  # power, energy, efficiency
    
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
        self.ambient_light = None
        
        # Effects
        self.shadow_meshes = []
        self.sunshaft_mesh = None
        self.cloud_meshes = []
        
        # Parameters
        self.current_hour = 12
        self.current_day = 172
        self.latitude = 40.7128
        self.longitude = -74.0060
        self.panel_efficiency = 20.0
        self.panel_power = 330
        self.weather_factor = 1.0
        
        # Visual settings
        self.shadows_enabled = True
        self.sunshafts_enabled = True
        self.reflections_enabled = True
        self.volumetric_lighting = True
        
        print("✅ Advanced Solar Visualization initialized - FIXED")
    
    def set_building(self, building_mesh):
        """Set building for comprehensive solar analysis"""
        self.building_mesh = building_mesh
        if building_mesh:
            self.create_advanced_solar_panels()
            self.create_realistic_sun()
            self.update_comprehensive_shadows()
            self.create_atmospheric_effects()
    
    def create_advanced_solar_panels(self):
        """Create optimized solar panel layout with realistic specifications"""
        if not self.building_mesh:
            return
        
        try:
            # Clear existing panels
            self.clear_solar_panels()
            
            # Get roof surface
            bounds = self.building_mesh.bounds
            roof_area = self._calculate_roof_area(bounds)
            
            # Standard solar panel dimensions (in meters)
            panel_specs = {
                'width': 1.65,
                'height': 1.0,
                'thickness': 0.04,
                'power': self.panel_power,  # Watts
                'efficiency': self.panel_efficiency / 100
            }
            
            # Calculate optimal panel layout
            panel_layout = self._optimize_panel_layout(bounds, panel_specs)
            
            # Create panel meshes
            for i, panel_pos in enumerate(panel_layout):
                panel = self._create_single_panel(panel_pos, panel_specs, i)
                if panel:
                    self.panel_meshes.append(panel)
                    self.solar_panels.append({
                        'mesh': panel,
                        'position': panel_pos,
                        'normal': [0, 0, 1],  # Facing up
                        'tilt': 0,  # Degrees
                        'azimuth': 180,  # South-facing
                        'power_rating': panel_specs['power'],
                        'efficiency': panel_specs['efficiency']
                    })
            
            print(f"✅ Created {len(self.solar_panels)} optimized solar panels")
            print(f"   Total capacity: {len(self.solar_panels) * panel_specs['power'] / 1000:.1f} kW")
            
        except Exception as e:
            print(f"Error creating advanced solar panels: {e}")
    
    def _calculate_roof_area(self, bounds):
        """Calculate available roof area"""
        x_min, x_max, y_min, y_max, z_min, z_max = bounds
        return (x_max - x_min) * (y_max - y_min)
    
    def _optimize_panel_layout(self, bounds, panel_specs):
        """Optimize panel layout for maximum efficiency"""
        x_min, x_max, y_min, y_max, z_min, z_max = bounds
        
        # Available roof dimensions
        roof_width = x_max - x_min
        roof_height = y_max - y_min
        roof_level = z_max
        
        # Panel dimensions
        panel_w = panel_specs['width']
        panel_h = panel_specs['height']
        
        # Spacing between panels (for maintenance and shadows)
        spacing_factor = 0.1  # 10cm spacing
        
        # Calculate grid
        effective_width = roof_width * 0.9  # 90% roof coverage
        effective_height = roof_height * 0.9
        
        panels_x = max(1, int(effective_width / (panel_w + spacing_factor)))
        panels_y = max(1, int(effective_height / (panel_h + spacing_factor)))
        
        # Calculate starting position (center the array)
        start_x = x_min + (roof_width - panels_x * (panel_w + spacing_factor)) / 2
        start_y = y_min + (roof_height - panels_y * (panel_h + spacing_factor)) / 2
        
        # Generate panel positions
        panel_positions = []
        for i in range(panels_x):
            for j in range(panels_y):
                x = start_x + i * (panel_w + spacing_factor) + panel_w / 2
                y = start_y + j * (panel_h + spacing_factor) + panel_h / 2
                z = roof_level + panel_specs['thickness'] / 2
                
                panel_positions.append([x, y, z])
        
        return panel_positions
    
    def _create_single_panel(self, position, specs, panel_id):
        """Create a single solar panel with realistic materials"""
        try:
            # Create panel geometry
            panel = pv.Cube(
                center=position,
                x_length=specs['width'],
                y_length=specs['height'],
                z_length=specs['thickness']
            )
            
            # Add to scene with realistic material properties - FIXED: Removed incompatible parameters
            panel_actor = self.plotter.add_mesh(
                panel,
                color='#1a237e',  # Dark blue solar panel color
                name=f'solar_panel_{panel_id}',
                smooth_shading=True
            )
            
            # Add panel frame (aluminum) - FIXED: Removed incompatible parameters
            frame_thickness = 0.02
            frame = pv.Cube(
                center=position,
                x_length=specs['width'] + frame_thickness,
                y_length=specs['height'] + frame_thickness,
                z_length=frame_thickness
            )
            frame.translate([0, 0, -specs['thickness'] / 2])
            
            self.plotter.add_mesh(
                frame,
                color='silver',
                name=f'panel_frame_{panel_id}'
            )
            
            return panel_actor
            
        except Exception as e:
            print(f"Error creating panel {panel_id}: {e}")
            return None
    
    def create_realistic_sun(self):
        """Create realistic sun with proper lighting and atmospheric effects - FIXED"""
        try:
            # Remove existing sun
            if self.sun_mesh:
                try:
                    self.plotter.remove_actor('sun')
                    self.plotter.remove_actor('sun_corona')
                except:
                    pass
            
            # Calculate accurate sun position
            sun_pos = self.calculate_precise_sun_position()
            sun_distance = np.linalg.norm(sun_pos)
            
            # Create sun sphere with corona effect
            sun_core = pv.Sphere(radius=3, center=sun_pos)
            sun_corona = pv.Sphere(radius=6, center=sun_pos)
            
            # Add sun core - FIXED: Removed incompatible parameters
            self.sun_mesh = self.plotter.add_mesh(
                sun_core,
                color='#FFF700',  # Bright yellow
                name='sun',
                smooth_shading=True
            )
            
            # Add sun corona (halo effect)
            self.plotter.add_mesh(
                sun_corona,
                color='#FFFF80',  # Light yellow
                opacity=0.3,
                name='sun_corona'
            )
            
            # Create realistic directional lighting
            self._setup_realistic_lighting(sun_pos)
            
            # Create sunshafts if enabled
            if self.sunshafts_enabled:
                self.create_volumetric_sunshafts(sun_pos)
            
            print(f"✅ Realistic sun created at {sun_pos}")
            
        except Exception as e:
            print(f"Error creating realistic sun: {e}")
    
    def calculate_precise_sun_position(self):
        """Calculate precise sun position using solar algorithms"""
        try:
            # Solar declination (accurate formula)
            declination = 23.45 * np.sin(np.radians(360 * (284 + self.current_day) / 365.25))
            
            # Hour angle
            hour_angle = 15 * (self.current_hour - 12)
            
            # Convert to radians
            lat_rad = np.radians(self.latitude)
            decl_rad = np.radians(declination)
            hour_rad = np.radians(hour_angle)
            
            # Solar elevation angle
            elevation = np.arcsin(
                np.sin(lat_rad) * np.sin(decl_rad) +
                np.cos(lat_rad) * np.cos(decl_rad) * np.cos(hour_rad)
            )
            
            # Solar azimuth angle
            azimuth = np.arctan2(
                np.sin(hour_rad),
                np.cos(hour_rad) * np.sin(lat_rad) - np.tan(decl_rad) * np.cos(lat_rad)
            )
            
            # Convert to cartesian coordinates
            distance = 150  # Visualization distance
            
            x = distance * np.cos(elevation) * np.sin(azimuth)
            y = distance * np.cos(elevation) * np.cos(azimuth)
            z = distance * np.sin(elevation)
            
            # Ensure sun is above horizon
            if z < 1:
                z = 1
            
            return [x, y, z]
            
        except Exception as e:
            print(f"Error calculating sun position: {e}")
            return [100, 100, 50]  # Default fallback
    
    def _setup_realistic_lighting(self, sun_pos):
        """Setup realistic lighting system with valid PyVista light types - FIXED"""
        try:
            # Remove existing lights
            self.plotter.remove_all_lights()
            
            # Calculate lighting parameters
            ambient_color = self._calculate_sky_color()
            sun_intensity = self._calculate_sun_intensity()
            sun_color = self._calculate_sun_color()
            
            # FIXED: Use valid light types for newer PyVista versions
            # Scene light (replaces ambient light)
            self.plotter.add_light(pv.Light(
                position=(0, 0, 100),  # High above scene
                focal_point=(0, 0, 0),
                color=ambient_color,
                intensity=0.3,
                light_type='scenelight'  # FIXED: Valid PyVista light type
            ))
            
            # Direct sunlight
            self.plotter.add_light(pv.Light(
                position=sun_pos,
                focal_point=(0, 0, 0),
                color=sun_color,
                intensity=sun_intensity,
                light_type='scenelight'  # FIXED: Valid PyVista light type
            ))
            
            # Fill light (scattered light from atmosphere)
            opposite_pos = [-sun_pos[0] * 0.3, -sun_pos[1] * 0.3, sun_pos[2] * 0.5]
            self.plotter.add_light(pv.Light(
                position=opposite_pos,
                focal_point=(0, 0, 0),
                color=[0.7, 0.8, 1.0],  # Cooler fill light
                intensity=0.2,
                light_type='scenelight'
            ))
            
            print("✅ Realistic lighting setup complete - FIXED")
            
        except Exception as e:
            print(f"Error setting up lighting: {e}")
    
    def _calculate_sky_color(self):
        """Calculate sky color based on time and weather"""
        # Simplified sky color calculation
        sun_elevation = self.current_hour / 24 * np.pi  # Rough approximation
        
        # Dawn/dusk colors
        if self.current_hour < 6 or self.current_hour > 18:
            return [0.1, 0.1, 0.2]  # Night blue
        elif self.current_hour < 8 or self.current_hour > 16:
            return [0.8, 0.5, 0.3]  # Golden hour
        else:
            return [0.5, 0.7, 1.0]  # Day blue
    
    def _calculate_sun_intensity(self):
        """Calculate sun intensity based on atmospheric conditions"""
        sun_pos = self.calculate_precise_sun_position()
        elevation_angle = np.arcsin(sun_pos[2] / np.linalg.norm(sun_pos))
        
        # Atmospheric attenuation (simplified Beer's law)
        atmosphere_thickness = 1 / np.sin(max(elevation_angle, 0.1))
        attenuation = np.exp(-0.1 * atmosphere_thickness)
        
        # Weather factor
        base_intensity = 1.0 * attenuation * self.weather_factor
        
        return max(0.1, min(1.0, base_intensity))
    
    def _calculate_sun_color(self):
        """Calculate sun color based on atmospheric scattering"""
        sun_pos = self.calculate_precise_sun_position()
        elevation_angle = np.arcsin(sun_pos[2] / np.linalg.norm(sun_pos))
        
        # Rayleigh scattering effect
        if elevation_angle < np.radians(10):  # Low sun
            return [1.0, 0.7, 0.4]  # Orange/red
        elif elevation_angle < np.radians(30):  # Medium sun
            return [1.0, 0.9, 0.7]  # Warm white
        else:  # High sun
            return [1.0, 1.0, 0.95]  # Cool white
    
    def create_volumetric_sunshafts(self, sun_pos):
        """Create realistic volumetric sunshafts"""
        try:
            if self.sunshaft_mesh:
                try:
                    self.plotter.remove_actor('sunshafts')
                    self.plotter.remove_actor('sunshaft_particles')
                except:
                    pass
            
            # Create volumetric cone
            sun_distance = np.linalg.norm(sun_pos)
            direction = -np.array(sun_pos) / sun_distance
            
            # Main sunshaft cone
            cone = pv.Cone(
                center=sun_pos,
                direction=direction,
                height=sun_distance * 0.8,
                radius=15,
                resolution=32
            )
            
            # Add volumetric effect
            self.sunshaft_mesh = self.plotter.add_mesh(
                cone,
                color='yellow',
                opacity=0.05,
                name='sunshafts'
            )
            
            # Add particle effects for dust motes
            self.create_dust_particles(sun_pos, direction)
            
            print("✅ Volumetric sunshafts created")
            
        except Exception as e:
            print(f"Error creating sunshafts: {e}")
    
    def create_dust_particles(self, sun_pos, direction):
        """Create dust particle effects in sunshafts"""
        try:
            # Generate random particle positions
            num_particles = 200
            particles = []
            
            for i in range(num_particles):
                # Random position in sunshaft cone
                t = np.random.random() * 0.8  # Along the cone
                r = np.random.random() * 15 * t  # Radius increases with distance
                angle = np.random.random() * 2 * np.pi
                
                # Position in cone
                pos = np.array(sun_pos) + t * np.array(direction) * np.linalg.norm(sun_pos)
                pos[0] += r * np.cos(angle)
                pos[1] += r * np.sin(angle)
                
                particles.append(pos)
            
            # Create particle cloud
            if particles:
                particles_array = np.array(particles)
                particle_cloud = pv.PolyData(particles_array)
                
                self.plotter.add_mesh(
                    particle_cloud,
                    color='white',
                    point_size=2,
                    opacity=0.3,
                    render_points_as_spheres=True,
                    name='sunshaft_particles'
                )
            
            print(f"✅ Created {num_particles} dust particles")
            
        except Exception as e:
            print(f"Error creating dust particles: {e}")
    
    def update_comprehensive_shadows(self):
        """Update comprehensive shadow system"""
        if not self.shadows_enabled:
            return
        
        try:
            # Clear existing shadows
            self.clear_shadows()
            
            if not self.building_mesh:
                return
            
            sun_pos = self.calculate_precise_sun_position()
            
            # Calculate building shadows
            building_shadow = self._calculate_building_shadow(sun_pos)
            if building_shadow:
                shadow_actor = self.plotter.add_mesh(
                    building_shadow,
                    color='black',
                    opacity=0.4,
                    name='building_shadow'
                )
                self.shadow_meshes.append(shadow_actor)
            
            # Calculate panel shadows on panels (inter-panel shading)
            panel_shadows = self._calculate_panel_shadows(sun_pos)
            for i, shadow in enumerate(panel_shadows):
                shadow_actor = self.plotter.add_mesh(
                    shadow,
                    color='darkblue',
                    opacity=0.6,
                    name=f'panel_shadow_{i}'
                )
                self.shadow_meshes.append(shadow_actor)
            
            print("✅ Comprehensive shadows updated")
            
        except Exception as e:
            print(f"Error updating shadows: {e}")
    
    def _calculate_building_shadow(self, sun_pos):
        """Calculate accurate building shadow projection - FIXED"""
        try:
            if not self.building_mesh:
                return None
            
            bounds = self.building_mesh.bounds
            x_min, x_max, y_min, y_max, z_min, z_max = bounds
            
            # Sun direction
            sun_direction = np.array(sun_pos) / np.linalg.norm(sun_pos)
            
            # Calculate shadow projection on ground
            building_height = z_max - z_min
            sun_elevation = np.arcsin(sun_direction[2])
            
            if sun_elevation <= 0:
                return None
                
            shadow_length = building_height / np.tan(sun_elevation)
            
            # Shadow direction (opposite to sun, projected on ground)
            shadow_dir = -np.array([sun_direction[0], sun_direction[1], 0])
            if np.linalg.norm(shadow_dir) > 0:
                shadow_dir = shadow_dir / np.linalg.norm(shadow_dir) * shadow_length
            
            # Create shadow polygon
            shadow_points = np.array([
                [x_min + shadow_dir[0], y_min + shadow_dir[1], 0.01],
                [x_max + shadow_dir[0], y_min + shadow_dir[1], 0.01],
                [x_max + shadow_dir[0], y_max + shadow_dir[1], 0.01],
                [x_min + shadow_dir[0], y_max + shadow_dir[1], 0.01]
            ])
            
            # Create shadow mesh
            shadow = pv.PolyData(shadow_points)
            shadow.faces = np.array([4, 0, 1, 2, 3])
            
            return shadow
            
        except Exception as e:
            print(f"Error calculating building shadow: {e}")
            return None
    
    def _calculate_panel_shadows(self, sun_pos):
        """Calculate shadows between solar panels"""
        panel_shadows = []
        
        try:
            if len(self.solar_panels) < 2:
                return panel_shadows
            
            sun_direction = np.array(sun_pos) / np.linalg.norm(sun_pos)
            
            for i, panel in enumerate(self.solar_panels):
                panel_pos = panel['position']
                
                # Check if this panel casts shadow on other panels
                for j, other_panel in enumerate(self.solar_panels):
                    if i == j:
                        continue
                    
                    other_pos = other_panel['position']
                    
                    # Simple shadow calculation
                    if self._panel_casts_shadow_on_panel(panel_pos, other_pos, sun_direction):
                        shadow = self._create_panel_shadow(panel_pos, other_pos, sun_direction)
                        if shadow:
                            panel_shadows.append(shadow)
            
            return panel_shadows
            
        except Exception as e:
            print(f"Error calculating panel shadows: {e}")
            return panel_shadows
    
    def _panel_casts_shadow_on_panel(self, caster_pos, receiver_pos, sun_direction):
        """Check if one panel casts shadow on another"""
        # Simplified shadow casting check
        to_receiver = np.array(receiver_pos) - np.array(caster_pos)
        to_receiver_norm = to_receiver / np.linalg.norm(to_receiver)
        
        # Check if receiver is in shadow direction from caster
        dot_product = np.dot(-sun_direction[:2], to_receiver_norm[:2])
        return dot_product > 0.7  # Threshold for shadow casting
    
    def _create_panel_shadow(self, caster_pos, receiver_pos, sun_direction):
        """Create shadow mesh from one panel to another"""
        try:
            # Create simple shadow rectangle
            shadow_size = 0.5  # Partial shading
            
            shadow_points = np.array([
                [receiver_pos[0] - shadow_size, receiver_pos[1] - shadow_size, receiver_pos[2] + 0.001],
                [receiver_pos[0] + shadow_size, receiver_pos[1] - shadow_size, receiver_pos[2] + 0.001],
                [receiver_pos[0] + shadow_size, receiver_pos[1] + shadow_size, receiver_pos[2] + 0.001],
                [receiver_pos[0] - shadow_size, receiver_pos[1] + shadow_size, receiver_pos[2] + 0.001]
            ])
            
            shadow = pv.PolyData(shadow_points)
            shadow.faces = np.array([4, 0, 1, 2, 3])
            
            return shadow
            
        except Exception as e:
            print(f"Error creating panel shadow: {e}")
            return None
    
    # ADDED: Missing calculate_solar_performance method
    def calculate_solar_performance(self):
        """Calculate solar performance - FIXED MISSING METHOD"""
        try:
            if not self.solar_panels:
                return 0, 0, 0
            
            # Environmental factors
            sun_pos = self.calculate_precise_sun_position()
            sun_elevation = np.arcsin(sun_pos[2] / np.linalg.norm(sun_pos))
            
            # Direct Normal Irradiance (realistic model)
            dni = self._calculate_dni(sun_elevation)
            
            # Performance factors
            temperature_factor = self._calculate_temperature_factor()
            shading_factor = self._calculate_shading_factor()
            soiling_factor = 0.95  # Dust/dirt on panels
            aging_factor = 0.98  # Panel degradation
            
            # Calculate total power
            total_power = 0
            panel_area = 1.65 * 1.0  # m²
            
            for panel in self.solar_panels:
                # Panel-specific irradiance
                panel_irradiance = dni * self._calculate_panel_angle_factor(panel, sun_pos)
                
                # Panel power calculation
                panel_power = (
                    panel_irradiance *  # W/m²
                    panel_area *  # Panel area in m²
                    panel['efficiency'] *  # Panel efficiency
                    temperature_factor *
                    shading_factor *
                    soiling_factor *
                    aging_factor
                ) / 1000  # Convert to kW
                
                total_power += panel_power
            
            # System-level calculations
            inverter_efficiency = 0.96
            dc_ac_loss = 0.95
            
            ac_power = total_power * inverter_efficiency * dc_ac_loss
            
            # Daily energy estimation
            daily_energy = ac_power * self._calculate_daily_sun_hours()
            
            # System efficiency
            max_theoretical_power = len(self.solar_panels) * self.panel_power / 1000
            system_efficiency = (ac_power / max_theoretical_power * 100) if max_theoretical_power > 0 else 0
            
            return ac_power, daily_energy, system_efficiency
            
        except Exception as e:
            print(f"Error calculating solar performance: {e}")
            return 0, 0, 0
    
    def calculate_advanced_solar_performance(self):
        """Calculate detailed solar performance with all factors"""
        try:
            if not self.solar_panels:
                return 0, 0, 0, {}
            
            # Environmental factors
            sun_pos = self.calculate_precise_sun_position()
            sun_elevation = np.arcsin(sun_pos[2] / np.linalg.norm(sun_pos))
            
            # Direct Normal Irradiance (realistic model)
            dni = self._calculate_dni(sun_elevation)
            
            # Performance factors
            temperature_factor = self._calculate_temperature_factor()
            shading_factor = self._calculate_shading_factor()
            soiling_factor = 0.95  # Dust/dirt on panels
            aging_factor = 0.98  # Panel degradation
            
            # Calculate per-panel performance
            total_power = 0
            panel_details = []
            
            for i, panel in enumerate(self.solar_panels):
                # Panel-specific irradiance (considering angle and shading)
                panel_irradiance = dni * self._calculate_panel_angle_factor(panel, sun_pos)
                
                # Individual panel shading
                individual_shading = self._calculate_individual_panel_shading(panel, sun_pos)
                
                # Panel power calculation
                panel_power = (
                    panel_irradiance *  # W/m²
                    1.65 *  # Panel area in m²
                    panel['efficiency'] *  # Panel efficiency
                    temperature_factor *
                    individual_shading *
                    soiling_factor *
                    aging_factor
                ) / 1000  # Convert to kW
                
                total_power += panel_power
                
                panel_details.append({
                    'panel_id': i,
                    'irradiance': panel_irradiance,
                    'power': panel_power,
                    'shading': individual_shading,
                    'efficiency': panel['efficiency'] * 100
                })
            
            # System-level calculations
            inverter_efficiency = 0.96
            dc_ac_loss = 0.95
            
            ac_power = total_power * inverter_efficiency * dc_ac_loss
            
            # Daily energy estimation
            daily_energy = ac_power * self._calculate_daily_sun_hours()
            
            # System efficiency
            max_theoretical_power = len(self.solar_panels) * self.panel_power / 1000
            system_efficiency = (ac_power / max_theoretical_power * 100) if max_theoretical_power > 0 else 0
            
            # Detailed metrics
            detailed_metrics = {
                'dni': dni,
                'temperature_factor': temperature_factor,
                'shading_factor': shading_factor,
                'inverter_efficiency': inverter_efficiency,
                'panel_count': len(self.solar_panels),
                'panel_details': panel_details,
                'sun_elevation': np.degrees(sun_elevation),
                'weather_factor': self.weather_factor
            }
            
            # Emit performance update signal
            self.performance_updated.emit(ac_power, daily_energy, system_efficiency)
            
            return ac_power, daily_energy, system_efficiency, detailed_metrics
            
        except Exception as e:
            print(f"Error calculating solar performance: {e}")
            return 0, 0, 0, {}
    
    def _calculate_dni(self, sun_elevation):
        """Calculate Direct Normal Irradiance"""
        if sun_elevation <= 0:
            return 0
        
        # Extraterrestrial radiation
        solar_constant = 1361  # W/m²
        
        # Atmospheric attenuation
        air_mass = 1 / np.sin(sun_elevation) if np.sin(sun_elevation) > 0 else 10
        atmospheric_transmission = 0.7 ** (air_mass ** 0.678)
        
        # Weather factor
        dni = solar_constant * atmospheric_transmission * self.weather_factor
        
        return max(0, dni)
    
    def _calculate_temperature_factor(self):
        """Calculate temperature derating factor"""
        # Simplified temperature model
        ambient_temp = 25  # °C
        sun_elevation = np.arcsin(self.calculate_precise_sun_position()[2] / 
                                np.linalg.norm(self.calculate_precise_sun_position()))
        
        # Panel temperature estimation
        cell_temp = ambient_temp + (sun_elevation / np.pi * 2) * 30  # Rough estimation
        
        # Temperature coefficient (typical for silicon panels)
        temp_coefficient = -0.004  # %/°C
        standard_temp = 25  # °C
        
        temp_factor = 1 + temp_coefficient * (cell_temp - standard_temp)
        
        return max(0.7, temp_factor)  # Minimum 70% efficiency
    
    def _calculate_shading_factor(self):
        """Calculate overall system shading factor"""
        if not self.shadows_enabled:
            return 1.0
        
        # Simplified shading calculation
        shaded_panels = 0
        
        for panel in self.solar_panels:
            if self._is_panel_shaded(panel):
                shaded_panels += 1
        
        unshaded_ratio = (len(self.solar_panels) - shaded_panels) / len(self.solar_panels)
        return max(0.1, unshaded_ratio)  # At least 10% efficiency even with heavy shading
    
    def _calculate_panel_angle_factor(self, panel, sun_pos):
        """Calculate irradiance factor based on panel angle to sun"""
        # Panel normal vector (assuming flat panels facing up)
        panel_normal = np.array([0, 0, 1])
        
        # Sun direction
        sun_direction = np.array(sun_pos) / np.linalg.norm(sun_pos)
        
        # Cosine of angle between panel and sun
        cos_angle = np.dot(panel_normal, sun_direction)
        
        return max(0, cos_angle)
    
    def _calculate_individual_panel_shading(self, panel, sun_pos):
        """Calculate shading factor for individual panel"""
        # Simplified - would integrate with detailed shadow analysis
        if self._is_panel_shaded(panel):
            return 0.3  # 30% of normal output when shaded
        return 1.0
    
    def _is_panel_shaded(self, panel):
        """Check if a specific panel is shaded"""
        # Simplified shadow check
        return False  # Placeholder
    
    def _calculate_daily_sun_hours(self):
        """Calculate effective sun hours for the day"""
        if self.current_day >= 80 and self.current_day <= 266:  # Spring to Fall
            return 10  # Peak season
        else:
            return 6   # Winter season
    
    def create_atmospheric_effects(self):
        """Create atmospheric effects like clouds, haze"""
        try:
            # Create dynamic clouds
            if np.random.random() > 0.7:  # 30% chance of clouds
                self.create_clouds()
            
            # Create atmospheric haze
            self.create_atmospheric_haze()
            
            print("✅ Atmospheric effects created")
            
        except Exception as e:
            print(f"Error creating atmospheric effects: {e}")
    
    def create_clouds(self):
        """Create dynamic cloud system"""
        try:
            num_clouds = np.random.randint(3, 8)
            
            for i in range(num_clouds):
                # Random cloud position
                x = np.random.uniform(-100, 100)
                y = np.random.uniform(-100, 100)
                z = np.random.uniform(40, 80)
                
                # Cloud size
                size = np.random.uniform(15, 25)
                
                # Create cloud mesh
                cloud = pv.Sphere(radius=size, center=[x, y, z])
                
                # Add to scene
                cloud_actor = self.plotter.add_mesh(
                    cloud,
                    color='white',
                    opacity=0.6,
                    name=f'cloud_{i}'
                )
                
                self.cloud_meshes.append(cloud_actor)
            
            print(f"✅ Created {num_clouds} clouds")
            
        except Exception as e:
            print(f"Error creating clouds: {e}")
    
    def create_atmospheric_haze(self):
        """Create atmospheric haze effect"""
        try:
            # Create large semi-transparent sphere for haze
            haze = pv.Sphere(radius=200, center=[0, 0, 50])
            
            self.plotter.add_mesh(
                haze,
                color='lightblue',
                opacity=0.02,
                name='atmospheric_haze'
            )
            
            print("✅ Atmospheric haze created")
            
        except Exception as e:
            print(f"Error creating atmospheric haze: {e}")
    
    # Control methods
    def set_time(self, hour):
        """Update time and recalculate everything"""
        self.current_hour = hour
        self.create_realistic_sun()
        self.update_comprehensive_shadows()
    
    def set_day(self, day):
        """Update day and recalculate everything"""
        self.current_day = day
        self.create_realistic_sun()
        self.update_comprehensive_shadows()
    
    def set_location(self, lat, lon):
        """Update location"""
        self.latitude = lat
        self.longitude = lon
        self.create_realistic_sun()
        self.update_comprehensive_shadows()
    
    def set_weather_factor(self, factor):
        """Set weather factor (0.0 = stormy, 1.0 = clear)"""
        self.weather_factor = max(0.0, min(1.0, factor))
        self.create_realistic_sun()
    
    def set_visual_effects(self, shadows=None, sunshafts=None, reflections=None):
        """Toggle visual effects"""
        if shadows is not None:
            self.shadows_enabled = shadows
            if shadows:
                self.update_comprehensive_shadows()
            else:
                self.clear_shadows()
        
        if sunshafts is not None:
            self.sunshafts_enabled = sunshafts
            if sunshafts:
                sun_pos = self.calculate_precise_sun_position()
                self.create_volumetric_sunshafts(sun_pos)
            else:
                if self.sunshaft_mesh:
                    try:
                        self.plotter.remove_actor('sunshafts')
                        self.plotter.remove_actor('sunshaft_particles')
                    except:
                        pass
        
        if reflections is not None:
            self.reflections_enabled = reflections
    
    # Cleanup methods
    def clear_solar_panels(self):
        """Clear all solar panels"""
        try:
            for i in range(len(self.panel_meshes)):
                try:
                    self.plotter.remove_actor(f'solar_panel_{i}')
                    self.plotter.remove_actor(f'panel_frame_{i}')
                except:
                    pass
            
            self.solar_panels.clear()
            self.panel_meshes.clear()
            
        except Exception as e:
            print(f"Error clearing solar panels: {e}")
    
    def clear_shadows(self):
        """Clear all shadow meshes"""
        try:
            try:
                self.plotter.remove_actor('building_shadow')
            except:
                pass
                
            for i in range(len(self.solar_panels)):
                try:
                    self.plotter.remove_actor(f'panel_shadow_{i}')
                except:
                    pass
            
            self.shadow_meshes.clear()
            
        except Exception as e:
            print(f"Error clearing shadows: {e}")
    
    def clear_all(self):
        """Clear everything"""
        try:
            self.clear_solar_panels()
            self.clear_shadows()
            
            # Clear atmospheric effects
            if self.sun_mesh:
                try:
                    self.plotter.remove_actor('sun')
                    self.plotter.remove_actor('sun_corona')
                except:
                    pass
            
            if self.sunshaft_mesh:
                try:
                    self.plotter.remove_actor('sunshafts')
                    self.plotter.remove_actor('sunshaft_particles')
                except:
                    pass
            
            for i, cloud in enumerate(self.cloud_meshes):
                try:
                    self.plotter.remove_actor(f'cloud_{i}')
                except:
                    pass
            
            try:
                self.plotter.remove_actor('atmospheric_haze')
            except:
                pass
            
            print("✅ Advanced solar visualization cleared")
            
        except Exception as e:
            print(f"Error clearing all: {e}")