#!/usr/bin/env python3
"""
Enhanced PyVista Integration Manager - Combines both approaches
"""
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("⚠ PyVista not available")

# Import the building generator
from models.pyvista_building_generator import PyVistaBuildingGenerator

class PyVistaIntegration:
    """Enhanced PyVista integration that combines visualization and building generation"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.pyvista_widget = None
        self.plotter = None
        self.building_generator = None
        self.current_building = None
        
        # Initialize building generator
        self._initialize_building_generator()
        
    def _initialize_building_generator(self):
        """Initialize the building generator"""
        try:
            self.building_generator = PyVistaBuildingGenerator(self.main_window)
            print("✅ Building generator initialized in integration")
        except Exception as e:
            print(f"❌ Error initializing building generator: {e}")
            self.building_generator = None
        
    def create_pyvista_model_tab(self):
        """Create comprehensive 3D Model tab with building generation"""
        model_tab = QWidget()
        layout = QVBoxLayout(model_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        if PYVISTA_AVAILABLE:
            try:
                # Create PyVista Qt widget
                self.pyvista_widget = QtInteractor(model_tab)
                self.plotter = self.pyvista_widget
                
                # Connect building generator to plotter
                if self.building_generator:
                    self.building_generator.set_plotter(self.plotter)
                
                # Setup initial scene
                self._setup_initial_scene()
                
                # Add to layout - full size
                layout.addWidget(self.pyvista_widget, 1)
                
                # Store references for external access
                model_tab.pyvista_widget = self.pyvista_widget
                model_tab.plotter = self.plotter
                model_tab.building_generator = self.building_generator
                model_tab.pyvista_available = True
                
                print("✅ Enhanced PyVista 3D widget created successfully")
                
            except Exception as e:
                print(f"❌ Error creating PyVista widget: {e}")
                model_tab = self._create_fallback_tab()
                
        else:
            model_tab = self._create_fallback_tab()
        
        return model_tab
    
    def _create_fallback_tab(self):
        """Create fallback tab when PyVista not available"""
        model_tab = QWidget()
        layout = QVBoxLayout(model_tab)
        
        fallback_label = QLabel("🏗️ 3D Visualization\n\nPyVista not available\n\nPlease install PyVista:\npip install pyvista[all]")
        fallback_label.setAlignment(Qt.AlignCenter)
        fallback_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                padding: 50px;
                border: 2px dashed #ccc;
                border-radius: 10px;
                margin: 20px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(fallback_label)
        
        # Store references for fallback
        model_tab.pyvista_widget = None
        model_tab.plotter = None
        model_tab.building_generator = None
        model_tab.pyvista_available = False
        
        return model_tab
    
    def _setup_initial_scene(self):
        """Setup initial 3D scene"""
        try:
            if not self.plotter:
                return
            
            # Set background color
            self.plotter.set_background('lightblue')
            
            # Add ground plane
            ground = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=100, j_size=100)
            self.plotter.add_mesh(ground, color='lightgreen', opacity=0.2, name='ground')
            
            # Add coordinate axes
            self.plotter.add_axes(viewport=(0, 0, 0.2, 0.2))
            
            # Add default lighting
            self.plotter.add_light(pv.Light(position=(20, 20, 20), intensity=0.8))
            
            # Set initial camera position
            self.plotter.camera_position = [(30, 30, 30), (0, 0, 0), (0, 0, 1)]
            
            print("✅ Initial enhanced PyVista scene setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up initial scene: {e}")
    
    def create_building_from_points(self, points, **kwargs):
        """Create 3D building from 2D drawing points using the building generator"""
        try:
            if not self.building_generator:
                print("❌ Building generator not available")
                return self._fallback_building_creation(points, **kwargs)
            
            # Use the advanced building generator
            result = self.building_generator.generate_from_points(points, **kwargs)
            
            if result.get('status') == 'success':
                self.current_building = result.get('building')
                print("✅ Building created using advanced generator")
                return True
            else:
                print(f"❌ Building generator failed: {result}")
                return self._fallback_building_creation(points, **kwargs)
                
        except Exception as e:
            print(f"❌ Error creating building: {e}")
            return self._fallback_building_creation(points, **kwargs)
    
    def _fallback_building_creation(self, points, **kwargs):
        """Fallback building creation using simple method"""
        try:
            if not self.plotter or not PYVISTA_AVAILABLE:
                print("❌ PyVista not available for building creation")
                return False
            
            if not points or len(points) < 3:
                print("❌ Need at least 3 points to create building")
                return False
            
            # Get parameters
            wall_height = kwargs.get('wall_height', 3.0)
            roof_type = kwargs.get('roof_type', 'flat')
            roof_pitch = kwargs.get('roof_pitch', 30.0)
            scale = kwargs.get('scale', 0.05)
            
            # Clear existing building
            self.clear_building()
            
            # Convert points to 3D coordinates
            vertices = self._convert_points_to_3d(points, scale)
            
            # Create simple building mesh
            building_mesh = self._create_simple_building_mesh(vertices, wall_height)
            
            if building_mesh:
                self.plotter.add_mesh(building_mesh, name='building', color='lightcoral')
                self.current_building = building_mesh
                
                # Reset camera to show building
                self.plotter.reset_camera()
                
                print(f"✅ Fallback building created: {len(points)} points, {wall_height}m height")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error in fallback building creation: {e}")
            return False
    
    def _convert_points_to_3d(self, points, scale):
        """Convert 2D drawing points to 3D coordinates"""
        vertices = []
        
        for point in points:
            # Handle different point formats
            if hasattr(point, 'x') and hasattr(point, 'y'):
                x, y = point.x(), point.y()
            elif isinstance(point, (tuple, list)) and len(point) >= 2:
                x, y = float(point[0]), float(point[1])
            elif isinstance(point, dict):
                x, y = float(point.get('x', 0)), float(point.get('y', 0))
            else:
                x, y = 0, 0
            
            # Scale and add to vertices
            vertices.append([x * scale, y * scale, 0])
        
        return vertices
    
    def _create_simple_building_mesh(self, vertices, height):
        """Create simple building mesh"""
        try:
            if len(vertices) < 3:
                return None
            
            # Create bottom and top points
            bottom_points = np.array(vertices)
            top_points = np.array([[v[0], v[1], height] for v in vertices])
            
            # Combine all points
            all_points = np.vstack([bottom_points, top_points])
            
            # Create faces
            faces = []
            n_vertices = len(vertices)
            
            # Bottom face
            bottom_face = [n_vertices] + list(range(n_vertices))
            faces.extend(bottom_face)
            
            # Top face (reversed for correct normal)
            top_face = [n_vertices] + list(range(n_vertices, 2 * n_vertices))[::-1]
            faces.extend(top_face)
            
            # Side faces
            for i in range(n_vertices):
                next_i = (i + 1) % n_vertices
                # Create quad face
                face = [4, i, next_i, next_i + n_vertices, i + n_vertices]
                faces.extend(face)
            
            mesh = pv.PolyData(all_points, faces)
            return mesh
            
        except Exception as e:
            print(f"❌ Error creating simple building mesh: {e}")
            return None
    
    # ==========================================
    # BUILDING PARAMETER UPDATE METHODS
    # ==========================================
    
    def update_building_height(self, height):
        """Update building height"""
        if self.building_generator:
            self.building_generator.update_building_height(height)
        else:
            print("⚠ Building generator not available for height update")
    
    def update_roof_type(self, roof_type):
        """Update roof type"""
        if self.building_generator:
            self.building_generator.update_roof_type(roof_type)
        else:
            print("⚠ Building generator not available for roof type update")
    
    def update_roof_pitch(self, pitch):
        """Update roof pitch"""
        if self.building_generator:
            self.building_generator.update_roof_pitch(pitch)
        else:
            print("⚠ Building generator not available for roof pitch update")
    
    # ==========================================
    # SOLAR SIMULATION METHODS
    # ==========================================
    
    def update_solar_time(self, hour):
        """Update solar time"""
        if self.building_generator:
            self.building_generator.update_solar_time(hour)
        else:
            print("⚠ Building generator not available for solar time update")
    
    def update_solar_day(self, day):
        """Update solar day"""
        if self.building_generator:
            self.building_generator.update_solar_day(day)
        else:
            print("⚠ Building generator not available for solar day update")
    
    def start_sun_animation(self):
        """Start sun animation"""
        if self.building_generator:
            self.building_generator.start_sun_animation()
        else:
            print("⚠ Building generator not available for sun animation")
    
    def stop_sun_animation(self):
        """Stop sun animation"""
        if self.building_generator:
            self.building_generator.stop_sun_animation()
        else:
            print("⚠ Building generator not available to stop sun animation")
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def clear_building(self):
        """Clear existing building"""
        try:
            if self.building_generator:
                self.building_generator.clear_current_building()
            elif self.plotter:
                # Fallback clearing
                try:
                    self.plotter.remove_actor('building')
                except:
                    pass
                
            self.current_building = None
            print("✅ Building cleared")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing building: {e}")
            return False
    
    def clear_scene(self):
        """Clear entire scene"""
        try:
            if self.plotter:
                self.plotter.clear()
                self._setup_initial_scene()
                self.current_building = None
                print("✅ Scene cleared")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error clearing scene: {e}")
            return False
    
    def reset_camera(self):
        """Reset camera view"""
        try:
            if self.plotter:
                self.plotter.reset_camera()
                print("✅ Camera reset")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error resetting camera: {e}")
            return False
    
    def export_model(self, filepath):
        """Export 3D model"""
        try:
            if self.current_building and filepath:
                self.current_building.save(filepath)
                print(f"✅ Model exported to: {filepath}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error exporting model: {e}")
            return False
    
    def get_pyvista_widget(self):
        """Get PyVista widget for external access"""
        return self.pyvista_widget
    
    def get_plotter(self):
        """Get PyVista plotter for external access"""
        return self.plotter
    
    def get_building_generator(self):
        """Get building generator for external access"""
        return self.building_generator
    
    def is_available(self):
        """Check if PyVista is available"""
        return PYVISTA_AVAILABLE and self.plotter is not None
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.building_generator:
                self.building_generator.cleanup()
            self.clear_scene()
            print("✅ Enhanced PyVista integration cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")