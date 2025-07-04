"""
Building Management Module
Handles building generation strategies and coordination
"""

import traceback
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox


class BuildingManager:
    """Manages building generation with multiple strategies"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.generation_strategies = [
            'content_tabs_strategy',
            'pyvista_integration_strategy', 
            'main_generator_strategy',
            'basic_mesh_strategy'
        ]
    
    def initialize_building_generator(self):
        """Initialize building generator with proper error handling"""
        try:
            from models.pyvista_building_generator import PyVistaBuildingGenerator
            
            self.main_window.building_generator = PyVistaBuildingGenerator(self.main_window)
            
            # Connect signals if available
            if hasattr(self.main_window.building_generator, 'building_generated'):
                self.main_window.building_generator.building_generated.connect(
                    self.main_window._on_building_generated)
                print("✅ Connected building_generated signal")
            
            if hasattr(self.main_window.building_generator, 'solar_time_changed'):
                self.main_window.building_generator.solar_time_changed.connect(
                    self.main_window._on_solar_time_changed)
                print("✅ Connected solar_time_changed signal")
            
            print("✅ BuildingGenerator initialized")
            
        except ImportError as e:
            print(f"⚠️ PyVistaBuildingGenerator not available: {e}")
            self.main_window.building_generator = None
        except Exception as e:
            print(f"❌ BuildingGenerator initialization failed: {e}")
            self.main_window.building_generator = None
    
    def generate_building_with_settings(self, points, settings):
        """Generate building with given points and settings using multiple strategies"""
        try:
            print(f"🏗️ Generating building with {len(points)} points...")
            print(f"🏗️ Settings: {settings}")
            
            # Try each strategy in order
            for strategy_name in self.generation_strategies:
                strategy_method = getattr(self, strategy_name)
                try:
                    result = strategy_method(points, settings)
                    if result:
                        print(f"✅ Building created via {strategy_name}")
                        self.main_window._building_generated = True
                        self.main_window.building_generated.emit({'points': points, **settings})
                        return True
                    else:
                        print(f"❌ {strategy_name} returned False")
                except Exception as e:
                    print(f"❌ {strategy_name} failed: {e}")
                    continue
            
            # If all strategies failed
            print("❌ ALL BUILDING GENERATION STRATEGIES FAILED")
            self._show_generation_failed_error()
            return False
            
        except Exception as e:
            print(f"❌ Critical error in building generation: {e}")
            traceback.print_exc()
            self._show_error("Generation Error", f"Critical error: {str(e)}")
            return False
    
    def content_tabs_strategy(self, points, settings):
        """Strategy 1: Use content tabs building creation (PREFERRED)"""
        if not (self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'create_building')):
            return False
        
        print("🏗️ Using ContentTabs.create_building...")
        result = self.main_window.content_tabs.create_building(
            points=points,
            height=settings.get('wall_height', 3.0),
            roof_type=settings.get('roof_type', 'Flat'),
            roof_pitch=settings.get('roof_pitch', 15.0),
            scale=self.main_window._current_scale
        )
        
        return result
    
    def pyvista_integration_strategy(self, points, settings):
        """Strategy 2: Use PyVista integration (SECONDARY)"""
        if not (self.main_window.pyvista_integration and 
                hasattr(self.main_window.pyvista_integration, 'create_building_from_points')):
            return False
        
        print("🏗️ Using PyVista integration...")
        result = self.main_window.pyvista_integration.create_building_from_points(
            points=points,
            **settings
        )
        
        return result
    
    def main_generator_strategy(self, points, settings):
        """Strategy 3: Use main building generator (FALLBACK)"""
        if not (hasattr(self.main_window, 'building_generator') and self.main_window.building_generator):
            return False
        
        print("🏗️ Using main building generator...")
        
        # Try different generation methods
        generation_methods = [
            'generate_building_model',
            'create_building_from_canvas', 
            'generate_from_points',
            'create_building'
        ]
        
        for method_name in generation_methods:
            if hasattr(self.main_window.building_generator, method_name):
                try:
                    print(f"🏗️ Trying method: {method_name}")
                    method = getattr(self.main_window.building_generator, method_name)
                    
                    # Call with appropriate parameters
                    if method_name == 'generate_building_model':
                        result = method(
                            points=points,
                            scale=settings.get('scale', 0.05),
                            height=settings.get('wall_height', 3.0),
                            roof_type=settings.get('roof_type', 'Flat Roof'),
                            roof_pitch=settings.get('roof_pitch', 30.0)
                        )
                    elif method_name == 'create_building_from_canvas':
                        result = method(
                            points=points,
                            height=settings.get('wall_height', 3.0),
                            roof_type=settings.get('roof_type', 'flat'),
                            roof_pitch=settings.get('roof_pitch', 30.0)
                        )
                    else:
                        result = method(points, **settings)
                    
                    if result:
                        print(f"✅ Building created via {method_name}")
                        # Switch to model tab
                        self.main_window.switch_to_model_tab()
                        return True
                    else:
                        print(f"❌ Method {method_name} returned False")
                        
                except Exception as method_error:
                    print(f"❌ Method {method_name} failed: {method_error}")
                    continue
        
        return False
    
    def basic_mesh_strategy(self, points, settings):
        """Strategy 4: Create basic building mesh (LAST RESORT)"""
        print("🏗️ Creating basic building mesh as fallback...")
        
        try:
            import pyvista as pv
            import numpy as np
        except ImportError:
            print("❌ PyVista not available for basic mesh")
            return False
        
        if len(points) < 3:
            print("❌ Need at least 3 points for basic mesh")
            return False
        
        # Convert points to numpy array
        base_points = np.array(points)
        height = settings.get('wall_height', 3.0)
        
        # Create base polygon
        n_points = len(points)
        
        # Create vertices for base and top
        vertices = []
        
        # Base vertices (z=0)
        for point in base_points:
            vertices.append([point[0], point[1], 0])
        
        # Top vertices (z=height)
        for point in base_points:
            vertices.append([point[0], point[1], height])
        
        vertices = np.array(vertices)
        
        # Create faces
        faces = []
        
        # Base face (bottom)
        base_face = [n_points] + list(range(n_points))
        faces.extend(base_face)
        
        # Top face (top)
        top_face = [n_points] + list(range(n_points, 2 * n_points))
        faces.extend(top_face)
        
        # Side faces
        for i in range(n_points):
            next_i = (i + 1) % n_points
            
            # Each side face is a quad
            side_face = [4, i, next_i, next_i + n_points, i + n_points]
            faces.extend(side_face)
        
        # Create PyVista mesh
        mesh = pv.PolyData(vertices, faces)
        
        # Try to display in content tabs
        if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'display_building_mesh'):
            return self.main_window.content_tabs.display_building_mesh(mesh)
        
        print("✅ Basic mesh created but no display method available")
        return True
    
    def ensure_building_generator(self):
        """Ensure building generator is properly initialized"""
        try:
            if not hasattr(self.main_window, 'building_generator') or not self.main_window.building_generator:
                from models.pyvista_building_generator import PyVistaBuildingGenerator
                self.main_window.building_generator = PyVistaBuildingGenerator(self.main_window)
            
            return True
        except Exception as e:
            print(f"❌ Building generator initialization failed: {e}")
            return False
    
    def _show_generation_failed_error(self):
        """Show error when all generation strategies fail"""
        self._show_error("Generation Failed", 
                        "Failed to generate 3D model. Please check:\n"
                        "• PyVista is properly installed\n"
                        "• Building generator is initialized\n"
                        "• Points are valid (at least 3 points)\n"
                        "• Content tabs are properly configured")
    
    def _show_error(self, title, message):
        """Show error message"""
        try:
            QMessageBox.warning(self.main_window, title, message)
        except Exception as e:
            print(f"❌ Could not show error dialog: {e}")