#!/usr/bin/env python3
"""
unified_sun_system.py - OPTIMIZED VERSION
Unified sun visual system - NO PARTICLES, MORE YELLOW, BETTER PERFORMANCE
"""
import numpy as np
import pyvista as pv
from solar_system.solar_calculations import SolarCalculations

class UnifiedSunSystem:
    """Unified sun system - OPTIMIZED for performance"""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.sun_mesh = None
        self.current_sun_position = [15, 15, 8]  # Closer default position
        self.solar_settings = {
            'sunshafts_enabled': True,
            'weather_factor': 1.0
        }
    
    def create_unified_sun(self, sun_pos, solar_settings):
        """Create optimized sun - NO PARTICLES, MORE YELLOW"""
        try:
            self.current_sun_position = sun_pos
            self.solar_settings.update(solar_settings)
            
            # Check if sun is above horizon
            if sun_pos[2] <= 0:
                self.create_night_scene()
                return
            
            # Remove ALL existing sun elements
            self.clear_all_sun_elements()
            
            # Create OPTIMIZED sun system
            self.create_optimized_sun_core(sun_pos)
            
            if self.solar_settings.get('sunshafts_enabled', True):
                self.create_simple_sunshafts(sun_pos)
            
            print(f"☀️ Optimized sun created at {sun_pos}")
            
        except Exception as e:
            print(f"❌ Error creating optimized sun: {e}")
    
    def clear_all_sun_elements(self):
        """Clear ALL sun-related elements - OPTIMIZED"""
        try:
            # Main sun elements
            sun_elements = [
                'sun_core', 'sun_corona', 'sun_glow',
                'sun', 'sunshafts', 'sunshaft_particles'  # Also remove particles
            ]
            
            for element in sun_elements:
                try:
                    self.plotter.remove_actor(element)
                except:
                    pass
            
        except Exception as e:
            print(f"❌ Error clearing sun elements: {e}")
    
    def create_optimized_sun_core(self, sun_pos):
        """Create OPTIMIZED sun core - MORE YELLOW, SIMPLER"""
        try:
            # 1. MAIN SUN CORE - MORE YELLOW
            sun_core = pv.Sphere(radius=1.5, center=sun_pos)  # Smaller for performance
            
            self.sun_mesh = self.plotter.add_mesh(
                sun_core,
                color='#FFFF00',  # Pure yellow
                name='sun_core',
                smooth_shading=True,
                opacity=1.0,
                show_edges=False
            )
            
            # 2. SIMPLE SUN GLOW - MORE YELLOW
            sun_glow = pv.Sphere(radius=3, center=sun_pos)  # Smaller glow
            
            self.plotter.add_mesh(
                sun_glow,
                color='#FFFF80',  # Light yellow
                name='sun_glow',
                opacity=0.3,
                show_edges=False
            )
            
            print("✅ Optimized yellow sun core created")
            
        except Exception as e:
            print(f"❌ Error creating optimized sun core: {e}")
    
    def create_simple_sunshafts(self, sun_pos):
        """Create SIMPLE sunshafts - NO PARTICLES"""
        try:
            # Calculate sunshaft direction
            target_point = np.array([0, 0, 0])
            sun_position = np.array(sun_pos)
            
            direction = target_point - sun_position
            direction_length = np.linalg.norm(direction)
            
            if direction_length > 0:
                direction = direction / direction_length
            else:
                direction = np.array([0, 0, -1])
            
            # Create SIMPLE sunshaft cone - NO PARTICLES
            cone_height = min(20, direction_length * 0.6)  # Smaller cone
            cone_radius = cone_height * 0.2  # Thinner cone
            cone_center = sun_position + direction * 3
            
            sunshaft_cone = pv.Cone(
                center=cone_center,
                direction=direction,
                height=cone_height,
                radius=cone_radius,
                resolution=12  # Lower resolution for performance
            )
            
            self.plotter.add_mesh(
                sunshaft_cone,
                color='#FFFF99',  # Yellow sunshafts
                opacity=0.06,  # More subtle
                name='sunshafts',
                show_edges=False
            )
            
            print("✅ Simple sunshafts created (no particles)")
            
        except Exception as e:
            print(f"❌ Error creating simple sunshafts: {e}")
    
    def create_night_scene(self):
        """Create night scene - OPTIMIZED"""
        try:
            self.clear_all_sun_elements()
            self.plotter.background_color = '#191970'
            print("✅ Night scene created")
        except Exception as e:
            print(f"❌ Error creating night scene: {e}")
    
    def update_position(self, new_sun_pos, solar_settings):
        """Update sun position - OPTIMIZED"""
        try:
            self.create_unified_sun(new_sun_pos, solar_settings)
        except Exception as e:
            print(f"❌ Error updating sun position: {e}")
