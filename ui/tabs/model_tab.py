#!/usr/bin/env python3
"""
ui/content_tabs/model_tab.py
Model Tab with Enhanced Sun System Integration - COMPLETE FIXED VERSION
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
    print("✅ PyVista available for 3D visualization")
except ImportError:
    PYVISTA_AVAILABLE = False
    print("⚠️ PyVista not available - 3D view will be limited")

# Import your advanced solar system modules
try:
    from solar_system.solar_calculations import SolarCalculations
    SOLAR_CALCULATIONS_AVAILABLE = True
    print("✅ SolarCalculations module available")
except ImportError:
    SOLAR_CALCULATIONS_AVAILABLE = False
    print("⚠️ SolarCalculations module not found")

# Import the Enhanced Realistic Sun System
try:
    from solar_system.enhanced_sun_system import EnhancedRealisticSunSystem
    ENHANCED_SUN_AVAILABLE = True
    print("✅ EnhancedRealisticSunSystem module available")
except ImportError:
    ENHANCED_SUN_AVAILABLE = False
    print("⚠️ EnhancedRealisticSunSystem module not found")

class ModelTab(QWidget):
    """
    Model Tab with Enhanced Sun System Integration
    """
    
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
        self.debug_mode = True
        
        # Building meshes and materials
        self.building_meshes = []
        self.roof_meshes = []
        self.panel_meshes = []
        
        # Solar simulation state
        self.current_time = 12.0  # Decimal hours (noon)
        self.current_day = 172  # Day of year (summer solstice)
        self.latitude = 40.7128  # Default NYC
        self.longitude = -74.0060
        self.weather_factor = 1.0  # Clear sky
        self.shadows_enabled = True
        self.sunshafts_enabled = True  # Enable by default for enhanced system
        self.quality_level = 'medium'  # Quality setting for enhanced sun
        
        # Solar panel configuration
        self.solar_panel_config = {
            'panel_type': 'monocrystalline',
            'efficiency': 0.20,
            'tilt_angle': 30.0,
            'azimuth_angle': 180.0,  # South facing
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
        
        print("🏗️ Initializing ModelTab with Enhanced Sun System...")
        
        try:
            self.setup_ui()
            self._initialize_solar_systems()
            self._calculate_initial_sun_position()
            print("✅ ModelTab with Enhanced Sun System initialized successfully")
        except Exception as e:
            print(f"❌ ModelTab initialization failed: {e}")
            import traceback
            traceback.print_exc()

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
        
        print("✅ ModelTab UI setup completed")

    def setup_pyvista_view(self, layout):
        """ENHANCED: Setup PyVista 3D view with advanced features"""
        try:
            # Create PyVista plotter widget with advanced features
            self.plotter = QtInteractor(layout.parent())
            self.plotter.setMinimumHeight(500)
            
            # CRITICAL: Set reference to this ModelTab for roof system finding
            self.plotter.model_tab = self
            
            # Enable advanced rendering features for enhanced sun
            if hasattr(self.plotter, 'enable_shadows'):
                self.plotter.enable_shadows()
                print("✅ Shadows enabled")
            
            if hasattr(self.plotter, 'enable_anti_aliasing'):
                self.plotter.enable_anti_aliasing()
                print("✅ Anti-aliasing enabled")
            
            # Enable SSAO for better lighting
            if hasattr(self.plotter, 'enable_ssao'):
                self.plotter.enable_ssao(radius=0.5, bias=0.01, kernel_size=32)
                print("✅ SSAO enabled")
            
            # Connect camera events for performance optimization
            if hasattr(self.plotter, 'iren'):
                try:
                    # Track when camera is being moved
                    self.plotter.iren.add_observer('StartInteractionEvent', self._on_camera_start)
                    self.plotter.iren.add_observer('EndInteractionEvent', self._on_camera_end)
                    print("✅ Camera interaction observers connected")
                except Exception as e:
                    print(f"⚠️ Could not add camera observers: {e}")
            
            # Set up the plotter with enhanced lighting
            self.plotter.set_background('#87CEEB', top='#E6F3FF')  # Sky gradient
            
            # Add axes and grid
            if hasattr(self.plotter, 'show_axes'):
                self.plotter.show_axes()
            if hasattr(self.plotter, 'show_grid'):
                self.plotter.show_grid()
            
            # Store reference to the VTK widget
            self.vtk_widget = self.plotter.interactor
            layout.addWidget(self.vtk_widget)
            
            print("✅ Enhanced PyVista 3D view initialized")
            
        except Exception as e:
            print(f"❌ PyVista view setup failed: {e}")
            import traceback
            traceback.print_exc()
            self.plotter = None
            self.vtk_widget = None
            self.setup_fallback_3d_view(layout)
    
    def _on_camera_start(self, obj, event):
        """Called when camera interaction starts"""
        self.camera_interacting = True
        if self.enhanced_sun_system:
            self.enhanced_sun_system.set_interactive_mode(True)
        print("📷 Camera interaction started")
    
    def _on_camera_end(self, obj, event):
        """Called when camera interaction ends"""
        self.camera_interacting = False
        if self.enhanced_sun_system:
            self.enhanced_sun_system.set_interactive_mode(False)
        print("📷 Camera interaction ended")

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
        
        print("⚠️ Using fallback 3D view")

    def _initialize_solar_systems(self):
        """ENHANCED: Initialize solar system modules"""
        try:
            if not self.plotter:
                print("⚠️ No plotter available for solar system initialization")
                return
            
            # Initialize SolarCalculations (static class)
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.solar_calculations = SolarCalculations
                print("✅ SolarCalculations initialized")
            
            # Initialize Enhanced Realistic Sun System
            if ENHANCED_SUN_AVAILABLE:
                try:
                    self.enhanced_sun_system = EnhancedRealisticSunSystem(self.plotter)
                    
                    # CRITICAL: Set global reference for roof finding
                    import sys
                    sys.modules[__name__]._global_sun_system = self.enhanced_sun_system
                    
                    # Set initial quality level
                    self.enhanced_sun_system.set_quality_level(self.quality_level)
                    
                    print("✅ EnhancedRealisticSunSystem initialized successfully")
                    
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
                    print(f"❌ Failed to initialize EnhancedRealisticSunSystem: {e}")
                    import traceback
                    traceback.print_exc()
                    self.enhanced_sun_system = None
            else:
                print("⚠️ EnhancedRealisticSunSystem module not available")
                self.enhanced_sun_system = None
            
            print("✅ Solar system initialization complete")
            
        except Exception as e:
            print(f"❌ Solar system initialization failed: {e}")
            import traceback
            traceback.print_exc()

    def _calculate_initial_sun_position(self):
        """Calculate initial sun position"""
        try:
            if SOLAR_CALCULATIONS_AVAILABLE:
                self.sun_position = self.solar_calculations.calculate_sun_position(
                    self.current_time,
                    self.current_day,
                    self.latitude
                )
                print(f"✅ Initial sun position calculated: {self.sun_position}")
            else:
                # Fallback calculation
                self.sun_position = [30, 30, 30]
                print("⚠️ Using fallback sun position")
                
        except Exception as e:
            print(f"❌ Initial sun position calculation failed: {e}")
            self.sun_position = [30, 30, 30]

    def _update_all_solar_systems(self):
        """ENHANCED: Update all solar systems with current parameters"""
        try:
            # Don't update if camera is moving
            if self.camera_interacting:
                print("⚠️ Skipping sun update - camera is moving")
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
                # Fallback sun position
                self.sun_position = [30, 30, 30]
            
            # Update Enhanced Sun System - Use update_sun_position for debounced updates
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
                
                # Use update method instead of create for debouncing
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
            
            # Don't print every minor update
            if not hasattr(self, '_last_update_hour'):
                self._last_update_hour = self.current_time
            
            if abs(self._last_update_hour - self.current_time) >= 0.5:
                self._last_update_hour = self.current_time
                print(f"✅ Solar systems updated for time {self.current_time:.1f}h")
            
        except Exception as e:
            print(f"❌ Solar systems update failed: {e}")
            import traceback
            traceback.print_exc()
    
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
            print(f"⚠️ Error updating background: {e}")

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
            print(f"❌ Error getting building bounds: {e}")
            return None

    # ===========================================
    # SOLAR SIMULATION METHODS (Left Panel Signals)
    # ===========================================

    def update_solar_time(self, decimal_time):
        """Update solar time simulation"""
        try:
            # Don't update if camera is moving
            if self.camera_interacting:
                return
            
            print(f"🌞 Updating solar time to {decimal_time:.1f}")
            
            self.current_time = decimal_time
            self._update_all_solar_systems()
            
            print(f"✅ Solar time updated to {decimal_time:.1f}")
            
        except Exception as e:
            print(f"❌ Solar time update failed: {e}")
            import traceback
            traceback.print_exc()

    def update_solar_day(self, day_of_year):
        """Update solar day simulation"""
        try:
            # Don't update if camera is moving
            if self.camera_interacting:
                return
            
            print(f"📅 Updating solar day to {day_of_year}")
            
            self.current_day = day_of_year
            self._update_all_solar_systems()
            
            print(f"✅ Solar day updated to {day_of_year}")
            
        except Exception as e:
            print(f"❌ Solar day update failed: {e}")
            import traceback
            traceback.print_exc()

    def set_location(self, latitude, longitude):
        """Set location"""
        try:
            print(f"🌍 Setting location to {latitude:.2f}, {longitude:.2f}")
            
            self.latitude = latitude
            self.longitude = longitude
            self._update_all_solar_systems()
            
            print(f"✅ Location set to {latitude:.2f}, {longitude:.2f}")
            
        except Exception as e:
            print(f"❌ Location setting failed: {e}")
            import traceback
            traceback.print_exc()

    def set_weather_factor(self, factor):
        """Set weather factor"""
        try:
            print(f"🌤️ Setting weather factor to {factor:.2f}")
            
            self.weather_factor = factor
            self._update_all_solar_systems()
            
            print(f"✅ Weather factor set to {factor:.2f}")
            
        except Exception as e:
            print(f"❌ Weather factor setting failed: {e}")
            import traceback
            traceback.print_exc()

    def toggle_solar_effects(self, shadows=None, sunshafts=None):
        """Toggle solar effects"""
        try:
            if shadows is not None:
                print(f"🌑 Shadows: {'ON' if shadows else 'OFF'}")
                self.shadows_enabled = shadows
                
            if sunshafts is not None:
                print(f"☀️ Sunshafts: {'ON' if sunshafts else 'OFF'}")
                self.sunshafts_enabled = sunshafts
            
            self._update_all_solar_systems()
            
            print("✅ Solar effects updated")
            
        except Exception as e:
            print(f"❌ Solar effects toggle failed: {e}")
            import traceback
            traceback.print_exc()

    def set_quality_level(self, quality):
        """Set rendering quality level"""
        try:
            print(f"⚙️ Setting quality level to {quality}")
            
            self.quality_level = quality
            
            if self.enhanced_sun_system:
                self.enhanced_sun_system.set_quality_level(quality)
            
            print(f"✅ Quality level set to {quality}")
            
        except Exception as e:
            print(f"❌ Quality level setting failed: {e}")

    def handle_animation_toggle(self, enabled):
        """Handle animation toggle"""
        try:
            print(f"🎬 Animation: {'ON' if enabled else 'OFF'}")
            
            self.animation_active = enabled
            
            if enabled:
                self.animation_timer.start(100)  # Update every 100ms
                print("✅ Solar animation started")
            else:
                self.animation_timer.stop()
                print("✅ Solar animation stopped")
                
        except Exception as e:
            print(f"❌ Animation toggle failed: {e}")

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
            print(f"❌ Solar animation failed: {e}")

    # ===========================================
    # BUILDING AND ROOF METHODS
    # ===========================================

    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05):
        """ENHANCED: Create building in 3D view with enhanced solar features"""
        try:
            print(f"🏗️ Creating building with {len(points)} points, {roof_type} roof")
            
            if not points or len(points) < 3:
                print("❌ Invalid points for building creation")
                return False
            
            # Clear existing building but preserve sun system
            if self.plotter:
                # Remove building-specific actors but keep sun system
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
            
            print("✅ Building created successfully")
            
            
            if hasattr(self, 'test_shadows_immediately'):
                QTimer.singleShot(1000, self.test_shadows_immediately)
                
            return True
            

        except Exception as e:
            print(f"❌ Building creation failed: {e}")
            import traceback
            traceback.print_exc()
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
            
            print("✅ Building actors cleared")
            
        except Exception as e:
            print(f"⚠️ Error clearing building actors: {e}")

    def _create_roof_object(self, roof_type, points, height, scale):
        """ENHANCED: Create roof object based on type"""
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
                print("✅ Created PyramidRoof object")
                
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
                print("✅ Created GableRoof object")
                
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
                print("✅ Created FlatRoof object")
                
            else:
                print(f"⚠️ Roof type '{roof_type}' not implemented")
                self.current_roof = None
            
            # Register roof with sun system
            if self.current_roof and self.enhanced_sun_system:
                # Get roof meshes and register them
                if hasattr(self.current_roof, 'mesh_cache'):
                    for mesh_name, mesh in self.current_roof.mesh_cache.items():
                        self.enhanced_sun_system.register_scene_object(
                            mesh, f"roof_{mesh_name}", cast_shadow=True
                        )
                
            self.roof_generated.emit(self.current_roof)
                
        except Exception as e:
            print(f"❌ Error creating roof object: {e}")
            import traceback
            traceback.print_exc()
            self.current_roof = None

    # ===========================================
    # UTILITY METHODS
    # ===========================================

    def get_solar_performance(self):
        """Get solar performance metrics"""
        try:
            # Basic calculation
            base_power = 5.0  # kW
            base_energy = 40.0  # kWh
            base_efficiency = 75.0  # %
            
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
            print(f"❌ Solar performance calculation failed: {e}")
            return 0.0, 0.0, 0.0

    def refresh_view(self):
        """Refresh the 3D view"""
        try:
            print("🔄 Refreshing 3D view")
            
            if self.plotter:
                if hasattr(self.plotter, 'update'):
                    self.plotter.update()
                if hasattr(self.plotter, 'reset_camera'):
                    self.plotter.reset_camera()
                
                # Update solar visualization
                self._update_all_solar_systems()
            
            print("✅ 3D view refreshed")
            
        except Exception as e:
            print(f"❌ View refresh failed: {e}")

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
                
                print("✅ Plotter reset")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error resetting plotter: {e}")
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
            
            print("✅ Model Tab cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

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
            print(f"❌ Error getting valid plotter: {e}")
            return None

    def get_time_range(self):
        """Get time range for current location and date"""
        try:
            if SOLAR_CALCULATIONS_AVAILABLE:
                return self.solar_calculations.get_time_range(self.latitude, self.current_day)
            
            # Fallback calculation
            return 6.0, 18.0
            
        except Exception as e:
            print(f"❌ Time range calculation failed: {e}")
            return 6.0, 18.0
        
    def test_shadows_immediately(self):
        """DEBUGGING: Test shadows immediately"""
        try:
            print("🐛 TESTING SHADOWS IMMEDIATELY...")
            
            if not self.enhanced_sun_system:
                print("❌ No enhanced sun system available")
                return False
            
            # Force building center and dimensions
            self.enhanced_sun_system.set_building_center([0, 0, 0])
            self.enhanced_sun_system.set_building_dimensions(8.0, 10.0, 3.0, 4.0)
            
            # Force sun update with high elevation
            test_sun_position = [20, 20, 30]
            test_settings = {
                'sun_elevation': 60.0,
                'sun_azimuth': 180.0,
                'current_hour': 12.0,
                'weather_factor': 1.0
            }
            
            print(f"🐛 Forcing sun update with: {test_sun_position}")
            self.enhanced_sun_system.create_photorealistic_sun(test_sun_position, test_settings)
            
            # Force render
            if self.plotter:
                self.plotter.render()
                print("✅ Forced render completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Shadow test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
