#!/usr/bin/env python3
"""
roofs/base/sun_system_manager.py
Manages sun system integration and shadow rendering
"""
import numpy as np

class SunSystemManager:
    """Manages sun system and shadow integration"""
    
    def __init__(self, base_roof):
        """Initialize sun system manager"""
        self.roof = base_roof
        self.plotter = base_roof.plotter
        self.sun_system = None
        self.shadow_ground_registered = False
        
        # CRITICAL: Shadow level should be ABOVE ground
        self.shadow_level = -0.01  # Shadows at -0.01, ground at -0.05
        
        self._find_and_configure_sun_system()
        print("✅ SunSystemManager initialized")
    
    def _find_and_configure_sun_system(self):
        """Find and configure sun system - COMPREHENSIVE SEARCH"""
        try:
            print("🔍 Searching for sun system...")
            
            # Method 1: Direct plotter attributes
            if hasattr(self.plotter, 'enhanced_sun_system'):
                self.sun_system = self.plotter.enhanced_sun_system
                print("✅ Found sun system via plotter.enhanced_sun_system")
            elif hasattr(self.plotter, 'sun_system'):
                self.sun_system = self.plotter.sun_system
                print("✅ Found sun system via plotter.sun_system")
            
            # Method 2: Check plotter's app reference (QtInteractor pattern)
            if not self.sun_system and hasattr(self.plotter, 'app'):
                app = self.plotter.app
                if hasattr(app, 'main_window'):
                    main_window = app.main_window
                    
                    # Check model_tab
                    if hasattr(main_window, 'model_tab'):
                        model_tab = main_window.model_tab
                        if hasattr(model_tab, 'enhanced_sun_system'):
                            self.sun_system = model_tab.enhanced_sun_system
                            print("✅ Found sun system via app.main_window.model_tab.enhanced_sun_system")
                        elif hasattr(model_tab, 'sun_system'):
                            self.sun_system = model_tab.sun_system
                            print("✅ Found sun system via app.main_window.model_tab.sun_system")
                    
                    # Check main_window directly
                    if not self.sun_system:
                        if hasattr(main_window, 'enhanced_sun_system'):
                            self.sun_system = main_window.enhanced_sun_system
                            print("✅ Found sun system via app.main_window.enhanced_sun_system")
                        elif hasattr(main_window, 'sun_system'):
                            self.sun_system = main_window.sun_system
                            print("✅ Found sun system via app.main_window.sun_system")
            
            # Method 3: Check parent hierarchy (Qt widget pattern)
            if not self.sun_system and hasattr(self.plotter, 'parent'):
                parent = self.plotter.parent()
                search_depth = 0
                while parent and search_depth < 10:
                    # Check current parent
                    if hasattr(parent, 'enhanced_sun_system'):
                        self.sun_system = parent.enhanced_sun_system
                        print(f"✅ Found sun system via parent hierarchy (depth {search_depth})")
                        break
                    elif hasattr(parent, 'sun_system'):
                        self.sun_system = parent.sun_system
                        print(f"✅ Found sun system via parent hierarchy (depth {search_depth})")
                        break
                    
                    # Check if parent has model_tab
                    if hasattr(parent, 'model_tab'):
                        model_tab = parent.model_tab
                        if hasattr(model_tab, 'enhanced_sun_system'):
                            self.sun_system = model_tab.enhanced_sun_system
                            print(f"✅ Found sun system via parent.model_tab (depth {search_depth})")
                            break
                        elif hasattr(model_tab, 'sun_system'):
                            self.sun_system = model_tab.sun_system
                            print(f"✅ Found sun system via parent.model_tab (depth {search_depth})")
                            break
                    
                    # Move up the hierarchy
                    if hasattr(parent, 'parent'):
                        parent = parent.parent()
                    else:
                        parent = None
                    search_depth += 1
            
            # Method 4: Check if plotter has a reference to the interactor
            if not self.sun_system and hasattr(self.plotter, 'iren'):
                iren = self.plotter.iren
                if hasattr(iren, 'GetRenderWindow'):
                    render_window = iren.GetRenderWindow()
                    if hasattr(render_window, 'enhanced_sun_system'):
                        self.sun_system = render_window.enhanced_sun_system
                        print("✅ Found sun system via render window")
                    elif hasattr(render_window, 'sun_system'):
                        self.sun_system = render_window.sun_system
                        print("✅ Found sun system via render window")
            
            # Method 5: Global search through model_tab module
            if not self.sun_system:
                try:
                    # Try to import model_tab and check for global references
                    import sys
                    for module_name, module in sys.modules.items():
                        if 'model_tab' in module_name.lower():
                            if hasattr(module, '_global_sun_system'):
                                self.sun_system = module._global_sun_system
                                print(f"✅ Found sun system via {module_name}._global_sun_system")
                                break
                            if hasattr(module, 'enhanced_sun_system'):
                                self.sun_system = module.enhanced_sun_system
                                print(f"✅ Found sun system via {module_name}.enhanced_sun_system")
                                break
                except Exception as e:
                    print(f"⚠️ Global search failed: {e}")
            
            # Method 6: Check plotter's renderer for lights (indirect check)
            if not self.sun_system and hasattr(self.plotter, 'renderer'):
                renderer = self.plotter.renderer
                if hasattr(renderer, 'enhanced_sun_system'):
                    self.sun_system = renderer.enhanced_sun_system
                    print("✅ Found sun system via renderer")
                elif hasattr(renderer, 'sun_system'):
                    self.sun_system = renderer.sun_system
                    print("✅ Found sun system via renderer")
            
            # Configure if found
            if self.sun_system:
                print(f"✅ Sun system found: {type(self.sun_system)}")
                self._configure_sun_system()
                # Register ground for shadows
                self._register_ground_for_shadows()
                return True
            else:
                print("⚠️ No sun system found - shadows will not work")
                print("   Searched locations:")
                print("   - plotter.enhanced_sun_system / plotter.sun_system")
                print("   - plotter.app.main_window.model_tab")
                print("   - plotter parent hierarchy")
                print("   - render window")
                print("   - global module references")
                return False
                
        except Exception as e:
            print(f"❌ Error finding sun system: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _configure_sun_system(self):
        """Configure sun system with building parameters"""
        try:
            if not self.sun_system:
                return
            
            print("⚙️ Configuring sun system...")
            print(f"   Sun system type: {type(self.sun_system)}")
            print(f"   Available methods: {[m for m in dir(self.sun_system) if not m.startswith('_')][:10]}...")
            
            building_center = self._calculate_building_center()
            building_dims = self._calculate_building_dimensions()
            
            # Set building center
            if building_center:
                if hasattr(self.sun_system, 'set_building_center'):
                    self.sun_system.set_building_center(building_center)
                    print(f"✅ Set building center: {building_center}")
                elif hasattr(self.sun_system, 'building_center'):
                    self.sun_system.building_center = building_center
                    print(f"✅ Set building_center attribute: {building_center}")
            
            # Set building dimensions
            if building_dims:
                width, length, height, roof_height = building_dims
                if hasattr(self.sun_system, 'set_building_dimensions'):
                    self.sun_system.set_building_dimensions(width, length, height, roof_height)
                    print(f"✅ Set building dimensions: {width}x{length}x{height} (roof: {roof_height})")
                elif hasattr(self.sun_system, 'building_width'):
                    self.sun_system.building_width = width
                    self.sun_system.building_length = length
                    self.sun_system.building_height = height
                    self.sun_system.roof_height = roof_height
                    print(f"✅ Set dimension attributes")
            
            # CRITICAL: Set shadow level ABOVE ground
            if hasattr(self.sun_system, 'shadow_level'):
                self.sun_system.shadow_level = self.shadow_level  # -0.01 (above -0.05 ground)
                print(f"✅ Set shadow_level: {self.sun_system.shadow_level}")
            
            if hasattr(self.sun_system, 'set_shadow_height'):
                self.sun_system.set_shadow_height(self.shadow_level)
                print(f"✅ Called set_shadow_height({self.shadow_level})")
            
            if hasattr(self.sun_system, 'shadow_height'):
                self.sun_system.shadow_height = self.shadow_level
                print(f"✅ Set shadow_height attribute: {self.shadow_level}")
            
            # Enable shadows if not already enabled
            if hasattr(self.sun_system, 'enable_shadows'):
                self.sun_system.enable_shadows(True)
                print("✅ Called enable_shadows(True)")
            elif hasattr(self.sun_system, 'shadows_enabled'):
                self.sun_system.shadows_enabled = True
                print("✅ Set shadows_enabled = True")
            
            # Try to update/refresh the sun system
            if hasattr(self.sun_system, 'update'):
                self.sun_system.update()
                print("✅ Called sun_system.update()")
            elif hasattr(self.sun_system, 'update_lighting'):
                self.sun_system.update_lighting()
                print("✅ Called sun_system.update_lighting()")
            elif hasattr(self.sun_system, '_update_shadows_only'):
                self.sun_system._update_shadows_only()
                print("✅ Called sun_system._update_shadows_only()")
            
            print("✅ Sun system configured")
            
        except Exception as e:
            print(f"❌ Error configuring sun system: {e}")
            import traceback
            traceback.print_exc()
    
    def _register_ground_for_shadows(self):
        """Register ground mesh to receive shadows"""
        try:
            if not self.sun_system:
                print("⚠️ No sun system - cannot register ground")
                return
            
            if self.shadow_ground_registered:
                print("⚠️ Ground already registered")
                return
            
            # Wait for ground mesh to be available
            if not hasattr(self.roof, 'environment_manager'):
                print("⚠️ No environment manager yet")
                return
            
            if not self.roof.environment_manager.ground_mesh:
                print("⚠️ No ground mesh yet")
                return
            
            ground_mesh = self.roof.environment_manager.ground_mesh
            shadow_receive_level = self.shadow_level  # -0.01
            
            print(f"📋 Registering ground for shadows at level {shadow_receive_level}")
            
            # Try multiple registration methods
            registration_successful = False
            
            # Method 1: register_shadow_receiver
            if hasattr(self.sun_system, 'register_shadow_receiver'):
                self.sun_system.register_shadow_receiver(ground_mesh, shadow_receive_level)
                registration_successful = True
                print(f"✅ Called register_shadow_receiver(ground_mesh, {shadow_receive_level})")
            
            # Method 2: set_ground_mesh
            if hasattr(self.sun_system, 'set_ground_mesh'):
                self.sun_system.set_ground_mesh(ground_mesh)
                if hasattr(self.sun_system, 'set_shadow_height'):
                    self.sun_system.set_shadow_height(shadow_receive_level)
                registration_successful = True
                print(f"✅ Called set_ground_mesh() and set_shadow_height({shadow_receive_level})")
            
            # Method 3: register_ground_plane
            if hasattr(self.sun_system, 'register_ground_plane'):
                self.sun_system.register_ground_plane(ground_mesh, shadow_receive_level)
                registration_successful = True
                print(f"✅ Called register_ground_plane(ground_mesh, {shadow_receive_level})")
            
            # Method 4: register_scene_object (no shadow casting)
            if hasattr(self.sun_system, 'register_scene_object'):
                self.sun_system.register_scene_object(
                    ground_mesh, 
                    'ground_plane', 
                    cast_shadow=False,
                    receive_shadow=True
                )
                registration_successful = True
                print("✅ Called register_scene_object(ground_mesh, receive_shadow=True)")
            
            # Method 5: Direct attribute setting
            if hasattr(self.sun_system, 'ground_mesh'):
                self.sun_system.ground_mesh = ground_mesh
                registration_successful = True
                print("✅ Set sun_system.ground_mesh attribute")
            
            if hasattr(self.sun_system, 'ground_level'):
                self.sun_system.ground_level = self.roof.grass_ground_level
                print(f"✅ Set sun_system.ground_level = {self.roof.grass_ground_level}")
            
            if registration_successful:
                self.shadow_ground_registered = True
                print("✅ Ground registered for shadows")
                
                # Force update after registration
                if hasattr(self.sun_system, '_update_shadows_only'):
                    self.sun_system._update_shadows_only()
                elif hasattr(self.sun_system, 'update_lighting'):
                    self.sun_system.update_lighting()
            else:
                print("⚠️ Could not register ground - no compatible methods found")
            
        except Exception as e:
            print(f"⚠️ Could not register ground for shadows: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_building_center(self):
        """Calculate building center"""
        try:
            default_center = [0, 0, self.roof.base_height / 2]
            
            if hasattr(self.roof, 'dimensions') and self.roof.dimensions:
                if len(self.roof.dimensions) >= 3:
                    length, width, height = self.roof.dimensions[:3]
                    return [0, 0, self.roof.base_height + height / 2]
            
            elif hasattr(self.roof, 'base_points') and self.roof.base_points:
                points = np.array(self.roof.base_points)
                center_x = np.mean(points[:, 0])
                center_y = np.mean(points[:, 1])
                center_z = self.roof.base_height / 2
                return [center_x, center_y, center_z]
            
            return default_center
            
        except Exception as e:
            print(f"⚠️ Error calculating building center: {e}")
            return [0, 0, self.roof.base_height / 2]
    
    def _calculate_building_dimensions(self):
        """Calculate building dimensions"""
        try:
            default_dims = (8.0, 10.0, self.roof.base_height, 4.0)
            
            if hasattr(self.roof, 'dimensions') and self.roof.dimensions:
                if len(self.roof.dimensions) >= 3:
                    length, width, height = self.roof.dimensions[:3]
                    return (width, length, self.roof.base_height, height)
            
            return default_dims
            
        except Exception as e:
            print(f"⚠️ Error calculating dimensions: {e}")
            return (8.0, 10.0, self.roof.base_height, 4.0)
    
    def add_sun_compatible_mesh(self, mesh, **kwargs):
        """Add mesh with proper lighting properties for shadows"""
        # Always enable lighting for shadow compatibility
        kwargs['lighting'] = True
        kwargs['smooth_shading'] = True
        
        # Set material properties based on mesh type
        mesh_name = kwargs.get('name', '').lower()
        
        if 'ground' in mesh_name:
            # Ground should receive shadows but not cast them
            kwargs.setdefault('ambient', 0.3)
            kwargs.setdefault('diffuse', 1.0)  # Maximum diffuse for shadow visibility
            kwargs.setdefault('specular', 0.0)
            kwargs.setdefault('specular_power', 1)
            kwargs['pickable'] = False
            
            # Add the mesh
            actor = self.plotter.add_mesh(mesh, **kwargs)
            
            # Register ground for shadows if not already done
            if self.sun_system and not self.shadow_ground_registered:
                # Store the ground mesh reference
                self.roof.environment_manager.ground_mesh = mesh
                # Try to register it
                self._register_ground_for_shadows()
            
            return actor
            
        elif 'wall' in mesh_name:
            kwargs.setdefault('ambient', 0.35)
            kwargs.setdefault('diffuse', 0.85)
            kwargs.setdefault('specular', 0.05)
            kwargs.setdefault('specular_power', 2)
        elif 'roof' in mesh_name or 'slope' in mesh_name:
            kwargs.setdefault('ambient', 0.3)
            kwargs.setdefault('diffuse', 0.9)
            kwargs.setdefault('specular', 0.1)
            kwargs.setdefault('specular_power', 8)
        elif 'tree' in mesh_name or 'trunk' in mesh_name or 'crown' in mesh_name:
            kwargs.setdefault('ambient', 0.3)
            kwargs.setdefault('diffuse', 0.7)
            kwargs.setdefault('specular', 0.05)
            kwargs.setdefault('specular_power', 2)
        elif 'pole' in mesh_name:
            kwargs.setdefault('ambient', 0.3)
            kwargs.setdefault('diffuse', 0.7)
            kwargs.setdefault('specular', 0.2)
            kwargs.setdefault('specular_power', 10)
        else:
            kwargs.setdefault('ambient', 0.25)
            kwargs.setdefault('diffuse', 0.8)
            kwargs.setdefault('specular', 0.1)
            kwargs.setdefault('specular_power', 5)
        
        # Add mesh
        actor = self.plotter.add_mesh(mesh, **kwargs)
        
        # Register with sun system for shadow casting (except ground)
        if self.sun_system and 'ground' not in mesh_name.lower():
            # Try different registration methods
            name = kwargs.get('name', 'unnamed')
            
            if hasattr(self.sun_system, 'register_scene_object'):
                self.sun_system.register_scene_object(mesh, name, cast_shadow=True)
                print(f"✅ Registered '{name}' for shadow casting")
            elif hasattr(self.sun_system, 'add_shadow_caster'):
                self.sun_system.add_shadow_caster(mesh, name)
                print(f"✅ Added '{name}' as shadow caster")
            elif hasattr(self.sun_system, 'register_mesh'):
                self.sun_system.register_mesh(mesh, name)
                print(f"✅ Registered mesh '{name}'")
        
        return actor
    
    def update_after_changes(self):
        """Update sun system after roof changes"""
        try:
            if not self.sun_system:
                # Try to find sun system again
                self._find_and_configure_sun_system()
                if not self.sun_system:
                    return
            
            building_center = self._calculate_building_center()
            building_dims = self._calculate_building_dimensions()
            
            if building_center and hasattr(self.sun_system, 'set_building_center'):
                self.sun_system.set_building_center(building_center)
            
            if building_dims and hasattr(self.sun_system, 'set_building_dimensions'):
                width, length, height, roof_height = building_dims
                self.sun_system.set_building_dimensions(width, length, height, roof_height)
            
            # Ensure shadow level is correct
            if hasattr(self.sun_system, 'shadow_level'):
                self.sun_system.shadow_level = self.shadow_level
            
            if hasattr(self.sun_system, 'set_shadow_height'):
                self.sun_system.set_shadow_height(self.shadow_level)
            
            # Force shadow update
            self.force_shadow_update()
            
            # Re-register ground if needed
            if not self.shadow_ground_registered:
                self._register_ground_for_shadows()
            
        except Exception as e:
            print(f"❌ Error updating sun system: {e}")
    
    def force_shadow_update(self):
        """Force an immediate shadow update"""
        try:
            if not self.sun_system:
                print("⚠️ No sun system for shadow update")
                return
            
            print("🔄 Forcing shadow update...")
            
            # Ensure shadow level is set
            if hasattr(self.sun_system, 'shadow_level'):
                self.sun_system.shadow_level = self.shadow_level
                print(f"   Shadow level: {self.shadow_level}")
            
            if hasattr(self.sun_system, 'set_shadow_height'):
                self.sun_system.set_shadow_height(self.shadow_level)
            
            # Try different update methods
            update_called = False
            
            if hasattr(self.sun_system, '_update_shadows_only'):
                self.sun_system._update_shadows_only()
                update_called = True
                print("✅ Called _update_shadows_only()")
            
            if hasattr(self.sun_system, 'update_shadows'):
                self.sun_system.update_shadows()
                update_called = True
                print("✅ Called update_shadows()")
            
            if hasattr(self.sun_system, 'update_lighting'):
                self.sun_system.update_lighting()
                update_called = True
                print("✅ Called update_lighting()")
            
            if hasattr(self.sun_system, 'update'):
                self.sun_system.update()
                update_called = True
                print("✅ Called update()")
            
            if hasattr(self.sun_system, 'render'):
                self.sun_system.render()
                update_called = True
                print("✅ Called render()")
            
            if not update_called:
                print("⚠️ No update method found on sun system")
            
        except Exception as e:
            print(f"⚠️ Could not force shadow update: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """Cleanup sun system manager"""
        self.sun_system = None
        self.shadow_ground_registered = False
        print("✅ SunSystemManager cleanup completed")
