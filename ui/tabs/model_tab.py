#!/usr/bin/env python3
"""
ui/tabs/model_tab.py - OPTIMIZED VERSION
Model Tab without debug lines for better performance
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont
import math
import numpy as np
from datetime import datetime, timedelta

# Import PyVista components for 3D view
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

# Import solar system modules
try:
    from solar_system.solar_calculations import SolarCalculations
    SOLAR_CALCULATIONS_AVAILABLE = True
except ImportError:
    SOLAR_CALCULATIONS_AVAILABLE = False

# Import the Enhanced Realistic Sun System
try:
    from solar_system.enhanced_sun_system import EnhancedRealisticSunSystem
    ENHANCED_SUN_AVAILABLE = True
except ImportError:
    ENHANCED_SUN_AVAILABLE = False

class ModelTab(QWidget):
    """Optimized Model Tab without debug output"""
    
    # Signals
    building_generated = pyqtSignal(object)
    model_updated = pyqtSignal(object)
    view_changed = pyqtSignal(str)
    roof_generated = pyqtSignal(object)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Initialize state
        self.current_building = None
        self.current_roof = None
        self.plotter = None
        self.vtk_widget = None
        
        # Building meshes and materials
        self.building_meshes = []
        self.roof_meshes = []
        self.panel_meshes = []
        
        # Solar simulation state
        self.current_time = 12.0
        self.current_day = 172
        self.latitude = 40.7128
        self.longitude = -74.0060
        self.weather_factor = 1.0
        self.shadows_enabled = True
        self.sunshafts_enabled = True
        self.quality_level = 'medium'
        
        # Solar panel configuration
        self.solar_panel_config = {
            'panel_type': 'monocrystalline',
            'efficiency': 0.20,
            'tilt_angle': 30.0,
            'azimuth_angle': 180.0,
            'panel_width': 1.0,
            'panel_height': 2.0,
            'spacing': 0.1
        }
        
        # Animation state
        self.animation_active = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_solar_position)
        
        # Initialize solar system modules
        self.solar_calculations = None
        self.enhanced_sun_system = None
        
        # Sun position and lighting
        self.sun_position = None
        self.sun_actor = None
        self.shadow_actors = []
        
        # Camera interaction tracking
        self.camera_interacting = False
        
        try:
            self.setup_ui()
            self._initialize_solar_systems()
            self._calculate_initial_sun_position()
        except Exception as e:
            pass  # Silent fail for performance

    def setup_ui(self):
        """Setup the UI with only the 3D plotter"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create 3D view container
        view_container = QFrame()
        view_container.setFrameStyle(QFrame.StyledPanel)
        
        view_layout = QVBoxLayout(view_container)
        view_layout.setContentsMargins(5, 5, 5, 5)
        view_layout.setSpacing(5)
        
        # 3D View Area
        if PYVISTA_AVAILABLE:
            self.setup_pyvista_view(view_layout)
        else:
            self.setup_fallback_3d_view(view_layout)
        
        main_layout.addWidget(view_container)

    def setup_pyvista_view(self, layout):
        """Setup PyVista 3D view - optimized version"""
        try:
            # Create PyVista plotter widget
            self.plotter = QtInteractor(layout.parent())
            self.plotter.setMinimumHeight(500)
            
            # Set reference to this ModelTab
            self.plotter.model_tab = self
            
            # Enable optimized rendering features
            if hasattr(self.plotter, 'enable_shadows'):
                self.plotter.enable_shadows()
            
            if hasattr(self.plotter, 'enable_anti_aliasing'):
                self.plotter.enable_anti_aliasing()
            
            if hasattr(self.plotter, 'enable_ssao'):
                self.plotter.enable_ssao(radius=0.5, bias=0.01, kernel_size=32)
            
            # Connect camera events for performance optimization
            if hasattr(self.plotter, 'iren'):
                try:
                    self.plotter.iren.add_observer('StartInteractionEvent', self._on_camera_start)
                    self.plotter.iren.add_observer('EndInteractionEvent', self._on_camera_end)
                except:
                    pass  # Silent fail
            
            # Set up the plotter
            self.plotter.set_background('#87CEEB', top='#E6F3FF')
            
            # Add axes and grid
            if hasattr(self.plotter, 'show_axes'):
                self.plotter.show_axes()
            if hasattr(self.plotter, 'show_grid'):
                self.plotter.show_grid()
            
            # Store reference to the VTK widget
            self.vtk_widget = self.plotter.interactor
            layout.addWidget(self.vtk_widget)
            
        except Exception as e:
            self.plotter = None
            self.vtk_widget = None
            self.setup_fallback_3d_view(layout)
    
    def _on_camera_start(self, obj, event):
        """Called when camera interaction starts"""
        self.camera_interacting = True
        if self.enhanced_sun_system:
            self.enhanced_sun_system.set_interactive_mode(True)
    
    def _on_camera_end(self, obj, event):
        """Called when camera interaction ends"""
        self.camera_interacting = False
        if self.enhanced_sun_system:
            self.enhanced_sun_system.set_interactive_mode(False)

    def setup_fallback_3d_view(self, layout):
        """Setup fallback 3D view placeholder"""
        placeholder = QLabel("3D View Area")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(500)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                border: 2px dashed #7f8c8d;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        placeholder.setText("""
🌞 Enhanced Solar Model View

PyVista not available
3D visualization limited

To enable full 3D features:
pip install pyvista pyvistaqt

Current status: Fallback mode
        """)
        
        layout.addWidget(placeholder)
        self.plotter = None
        self.vtk_widget = None

    def _initialize_solar_systems(self):
        """Initialize solar system modules - minimal version"""
        try:
            if not self.plotter:
                return
            
            # Initialize SolarCalculations
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.solar_calculations = SolarCalculations
            
            # Initialize Enhanced Realistic Sun System
            if ENHANCED_SUN_AVAILABLE:
                try:
                    self.enhanced_sun_system = EnhancedRealisticSunSystem(self.plotter)
                    
                    # Set global reference for roof finding
                    import sys
                    sys.modules[__name__]._global_sun_system = self.enhanced_sun_system
                    
                    # Set initial quality level
                    self.enhanced_sun_system.set_quality_level(self.quality_level)
                    
                    # Initial sun creation
                    if self.sun_position:
                        solar_settings = {
                            'current_hour': self.current_time,
                            'weather_factor': self.weather_factor,
                            'quality': self.quality_level
                        }
                        self.enhanced_sun_system.create_photorealistic_sun(
                            self.sun_position, 
                            solar_settings
                        )
                    
                except Exception as e:
                    self.enhanced_sun_system = None
            else:
                self.enhanced_sun_system = None
            
        except Exception as e:
            pass  # Silent fail

    def _calculate_initial_sun_position(self):
        """Calculate initial sun position"""
        try:
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude
                )
            else:
                self.sun_position = [30, 30, 30]
                
        except Exception as e:
            self.sun_position = [30, 30, 30]

    def _update_all_solar_systems(self):
        """Update all solar systems - optimized version"""
        try:
            # Don't update if camera is moving
            if self.camera_interacting:
                return
            
            # Get building height if available
            building_height = 3.0
            if self.current_building:
                building_height = self.current_building.get('height', 3.0)
            
            # Calculate new sun position
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude,
                    building_height
                )
                
                # Update background based on time of day
                self._update_background_for_time()
                
            else:
                self.sun_position = [30, 30, 30]
            
            # Update Enhanced Sun System
            if self.enhanced_sun_system and self.sun_position:
                solar_settings = {
                    'current_hour': self.current_time,
                    'current_day': self.current_day,
                    'latitude': self.latitude,
                    'longitude': self.longitude,
                    'weather_factor': self.weather_factor,
                    'quality': self.quality_level,
                    'shadows_enabled': self.shadows_enabled,
                    'sunshafts_enabled': self.sunshafts_enabled
                }
                
                self.enhanced_sun_system.update_sun_position(
                    self.sun_position, 
                    solar_settings
                )
                
                # Create building shadows if available
                if self.current_building and self.shadows_enabled:
                    building_bounds = self._get_building_bounds()
                    if building_bounds:
                        self.enhanced_sun_system.create_building_shadows(
                            building_bounds,
                            self.sun_position,
                            self.weather_factor
                        )
            
        except Exception as e:
            pass  # Silent fail
    
    def _update_background_for_time(self):
        """Update background color based on time of day"""
        if not self.plotter:
            return
            
        try:
            if self.sun_position and self.sun_position[2] > 0:  # Sun above horizon
                if 10 <= self.current_time <= 14:  # Noon
                    bg_color = '#87CEEB'
                    top_color = '#E6F3FF'
                elif self.current_time < 6 or self.current_time > 20:  # Dawn/Dusk
                    bg_color = '#FF6B35'
                    top_color = '#4A5A8A'
                elif self.current_time < 8 or self.current_time > 18:  # Early/Late
                    bg_color = '#FFA500'
                    top_color = '#87CEEB'
                else:  # Day
                    bg_color = '#87CEEB'
                    top_color = '#B0E0E6'
            else:  # Night
                bg_color = '#0A0A1A'
                top_color = '#1A1A3A'
            
            self.plotter.set_background(bg_color, top=top_color)
            
        except Exception as e:
            pass  # Silent fail

    def _get_building_bounds(self):
        """Get building bounds for shadow calculation"""
        try:
            if not self.current_building:
                return None
            
            points = self.current_building.get('points', [])
            height = self.current_building.get('height', 3.0)
            scale = self.current_building.get('scale', 0.05)
            
            if not points:
                return None
            
            xs = []
            ys = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    x, y = point.x() * scale, point.y() * scale
                else:
                    x, y = point[0] * scale, point[1] * scale
                xs.append(x)
                ys.append(y)
            
            if xs and ys:
                return [min(xs), max(xs), min(ys), max(ys), 0, height]
            
            return None
            
        except Exception as e:
            return None

    # Solar simulation methods (Left Panel Signals)
    def update_solar_time(self, decimal_time):
        """Update solar time simulation"""
        try:
            if self.camera_interacting:
                return
            
            self.current_time = decimal_time
            self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    def update_solar_day(self, day_of_year):
        """Update solar day simulation"""
        try:
            if self.camera_interacting:
                return
            
            self.current_day = day_of_year
            self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    def set_location(self, latitude, longitude):
        """Set location"""
        try:
            self.latitude = latitude
            self.longitude = longitude
            self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    def set_weather_factor(self, factor):
        """Set weather factor"""
        try:
            self.weather_factor = factor
            self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    def toggle_solar_effects(self, shadows=None, sunshafts=None):
        """Toggle solar effects"""
        try:
            if shadows is not None:
                self.shadows_enabled = shadows
                
            if sunshafts is not None:
                self.sunshafts_enabled = sunshafts
            
            self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    def set_quality_level(self, quality):
        """Set rendering quality level"""
        try:
            self.quality_level = quality
            
            if self.enhanced_sun_system:
                self.enhanced_sun_system.set_quality_level(quality)
            
        except Exception as e:
            pass  # Silent fail

    def handle_animation_toggle(self, enabled):
        """Handle animation toggle"""
        try:
            self.animation_active = enabled
            
            if enabled:
                self.animation_timer.start(100)
            else:
                self.animation_timer.stop()
                
        except Exception as e:
            pass  # Silent fail

    def _animate_solar_position(self):
        """Animate solar position over time"""
        try:
            if not self.animation_active:
                return
            
            # Increment time by 0.1 hours (6 minutes)
            self.current_time += 0.1
            
            # Reset at end of day
            if self.current_time >= 24:
                self.current_time = 0
            
            # Update all solar systems
            self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    # Building and roof methods
    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05):
        """Create building in 3D view - optimized version"""
        try:
            if not points or len(points) < 3:
                return False
            
            # Clear existing building but preserve sun system
            if self.plotter:
                self._clear_building_actors()
                
                # Reset background and basic elements
                self.plotter.set_background('#87CEEB', top='#E6F3FF')
                if hasattr(self.plotter, 'show_axes'):
                    self.plotter.show_axes()
                if hasattr(self.plotter, 'show_grid'):
                    self.plotter.show_grid()
            
            # Create building data
            building_data = {
                'points': points,
                'height': height,
                'roof_type': roof_type,
                'roof_pitch': roof_pitch,
                'scale': scale,
                'created_at': datetime.now()
            }
            
            # Store building
            self.current_building = building_data
            
            # Create roof object based on type
            self._create_roof_object(roof_type, points, height, scale)
            
            # Update all solar systems
            self._update_all_solar_systems()
            
            # Emit signal
            self.building_generated.emit(building_data)
            
            return True
            
        except Exception as e:
            return False
    
    def _clear_building_actors(self):
        """Clear building-specific actors but preserve sun system"""
        try:
            # Clear mesh lists
            self.building_meshes.clear()
            self.roof_meshes.clear()
            self.panel_meshes.clear()
            
            # Remove building-specific actors
            actors_to_remove = []
            for name in self.plotter.renderer.actors:
                if hasattr(name, 'name'):
                    actor_name = str(name.name).lower()
                    if any(keyword in actor_name for keyword in 
                           ['wall', 'roof', 'foundation', 'building', 'panel']):
                        actors_to_remove.append(name)
            
            for actor in actors_to_remove:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            
        except Exception as e:
            pass  # Silent fail

    def _create_roof_object(self, roof_type, points, height, scale):
        """Create roof object based on type - optimized"""
        try:
            base_points = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    x, y = point.x() * scale, point.y() * scale
                else:
                    x, y = point[0] * scale, point[1] * scale
                base_points.append([x, y, 0])
            
            # Cleanup previous roof
            if hasattr(self, 'current_roof') and self.current_roof:
                try:
                    if hasattr(self.current_roof, 'cleanup'):
                        self.current_roof.cleanup()
                    del self.current_roof
                except:
                    pass
            
            if roof_type == 'pyramid':
                from roofs.concrete.pyramid_roof import PyramidRoof
                self.current_roof = PyramidRoof(
                    plotter=self.plotter,
                    base_points=base_points[:4],
                    apex_height=height,
                    building_height=0
                )
                
            elif roof_type == 'gable':
                from roofs.concrete.gable_roof import GableRoof
                # Calculate dimensions from base points
                if len(base_points) >= 4:
                    length = abs(base_points[1][1] - base_points[0][1])
                    width = abs(base_points[2][0] - base_points[1][0])
                    dimensions = (length, width, height)
                else:
                    dimensions = (10.0, 8.0, height)
                
                self.current_roof = GableRoof(
                    plotter=self.plotter,
                    dimensions=dimensions,
                    theme="light",
                    rotation_angle=0
                )
                
            elif roof_type == 'flat':
                from roofs.concrete.flat_roof import FlatRoof
                roof_points = []
                for point in points:
                    if hasattr(point, 'x') and hasattr(point, 'y'):
                        x, y = point.x() * scale, point.y() * scale
                    else:
                        x, y = point[0] * scale, point[1] * scale
                    roof_points.append([x, y, height])
                
                self.current_roof = FlatRoof(
                    plotter=self.plotter,
                    base_points=roof_points,
                    building_height=height
                )
                
            else:
                self.current_roof = None
            
            # Register roof with sun system
            if self.current_roof and self.enhanced_sun_system:
                if hasattr(self.current_roof, 'mesh_cache'):
                    for mesh_name, mesh in self.current_roof.mesh_cache.items():
                        self.enhanced_sun_system.register_scene_object(
                            mesh, f"roof_{mesh_name}", cast_shadow=True
                        )
                
            self.roof_generated.emit(self.current_roof)
                
        except Exception as e:
            self.current_roof = None

    # Utility methods
    def get_solar_performance(self):
        """Get solar performance metrics"""
        try:
            # Basic calculation
            base_power = 5.0
            base_energy = 40.0
            base_efficiency = 75.0
            
            # Adjustments
            weather_adjustment = self.weather_factor
            
            # Time of day adjustment
            if 6 <= self.current_time <= 18:
                time_adjustment = 1.0
            else:
                time_adjustment = 0.1
            
            # Sun elevation adjustment
            if self.sun_position and len(self.sun_position) > 2 and self.sun_position[2] > 0:
                elevation_adjustment = min(1.0, self.sun_position[2] / 20.0)
            else:
                elevation_adjustment = 0.0
            
            # Calculate final values
            power = base_power * weather_adjustment * time_adjustment * elevation_adjustment
            energy = base_energy * weather_adjustment * elevation_adjustment
            efficiency = base_efficiency * weather_adjustment * elevation_adjustment
            
            return power, energy, efficiency
            
        except Exception as e:
            return 0.0, 0.0, 0.0

    def refresh_view(self):
        """Refresh the 3D view"""
        try:
            if self.plotter:
                if hasattr(self.plotter, 'update'):
                    self.plotter.update()
                if hasattr(self.plotter, 'reset_camera'):
                    self.plotter.reset_camera()
                
                # Update solar visualization
                self._update_all_solar_systems()
            
        except Exception as e:
            pass  # Silent fail

    def reset_plotter(self, camera_position=None):
        """Reset the plotter to clean state"""
        try:
            if PYVISTA_AVAILABLE and self.plotter:
                # Clear building actors but preserve sun system
                self._clear_building_actors()
                
                # Recreate enhanced sun system
                if self.enhanced_sun_system:
                    self.enhanced_sun_system.destroy()
                    self.enhanced_sun_system = EnhancedRealisticSunSystem(self.plotter)
                    self.enhanced_sun_system.set_quality_level(self.quality_level)
                
                # Reset background and basic elements
                self.plotter.set_background('#87CEEB', top='#E6F3FF')
                if hasattr(self.plotter, 'show_axes'):
                    self.plotter.show_axes()
                if hasattr(self.plotter, 'show_grid'):
                    self.plotter.show_grid()
                
                # Reset camera
                if camera_position:
                    try:
                        self.plotter.camera_position = camera_position
                    except:
                        pass
                else:
                    if hasattr(self.plotter, 'reset_camera'):
                        self.plotter.reset_camera()
                
                # Force update
                if hasattr(self.plotter, 'update'):
                    self.plotter.update()
                
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                
                return True
            
            return False
            
        except Exception as e:
            return False

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop animation
            if self.animation_timer.isActive():
                self.animation_timer.stop()
            
            # Cleanup enhanced sun system
            if self.enhanced_sun_system:
                self.enhanced_sun_system.destroy()
                self.enhanced_sun_system = None

            # Clear current roof
            if hasattr(self, 'current_roof') and self.current_roof:
                if hasattr(self.current_roof, 'cleanup'):
                    self.current_roof.cleanup()
                del self.current_roof
                self.current_roof = None
            
            # Clear buildings
            self.building_meshes.clear()
            self.roof_meshes.clear()
            self.panel_meshes.clear()
            self.shadow_actors.clear()
            self.current_building = None
            
            # Clear global reference
            import sys
            if hasattr(sys.modules[__name__], '_global_sun_system'):
                delattr(sys.modules[__name__], '_global_sun_system')
            
            # Close plotter
            if PYVISTA_AVAILABLE and self.plotter:
                if hasattr(self.plotter, 'close'):
                    self.plotter.close()
            
        except Exception as e:
            pass  # Silent fail

    # Additional helper methods
    def has_building(self):
        """Check if building exists"""
        return self.current_building is not None

    def get_plotter(self):
        """Get the 3D plotter"""
        return self.plotter

    def get_valid_plotter(self):
        """Get a valid plotter instance"""
        try:
            if self.plotter and hasattr(self.plotter, 'add_mesh'):
                return self.plotter
            return None
        except Exception as e:
            return None

    def get_time_range(self):
        """Get time range for current location and date"""
        try:
            if SOLAR_CALCULATIONS_AVAILABLE:
                return self.solar_calculations.get_time_range(self.latitude, self.current_day)
            return 6.0, 18.0
        except Exception as e:
            return 6.0, 18.0