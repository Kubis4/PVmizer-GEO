#!/usr/bin/env python3
"""
roofs/base/environment_manager.py
Manages environment objects (trees and poles) with shadow casting
"""
import pyvista as pv
import numpy as np
import os

class EnvironmentManager:
    """Manages environment objects with shadow casting capabilities"""
    
    def __init__(self, base_roof):
        """Initialize environment manager"""
        self.roof = base_roof
        self.plotter = base_roof.plotter
        
        # Environment state
        self.ground_mesh = None
        self.ground_actor = None
        self.ground_size = 40.0
        self.grass_ground_level = -0.05  # SAME AS WORKING CODE
        
        self.environment_obstacles = []
        self.environment_attachment_points = []
        self.environment_meshes = {}  # Store meshes for shadow casting
        
        # Attachment point visualization
        self.attachment_points_visible = False
        self.attachment_points_actor = None
        self.attachment_points_mesh = None
        
        # Placement state
        self.selected_tree_type = None
        self.tree_size_multiplier = 1.0
        self.pole_height_multiplier = 1.0
        self.environment_placement_mode = None
        self._environment_click_callback_id = None
        self.tree_type_index = 0
        
    
    def initialize_environment(self):
        """Initialize environment components"""
        self._calculate_ground_size()
        self._create_coordinated_grass_ground()
        self._create_environment_attachment_points()
        self._create_attachment_points_visualization()  # Create the black dots mesh
    
    def reinitialize_for_dimensions(self, dimensions):
        """Reinitialize environment for new building dimensions"""
        self.roof.dimensions = dimensions
        self._calculate_ground_size()
        
        # Recreate ground
        if self.ground_actor:
            try:
                self.plotter.remove_actor(self.ground_actor)
            except:
                pass
        self._create_coordinated_grass_ground()
        
        # Recreate attachment points
        self.environment_attachment_points.clear()
        self._create_environment_attachment_points()
        self._create_attachment_points_visualization()
    
    def _calculate_ground_size(self):
        """Calculate ground size based on building dimensions"""
        try:
            default_size = 40.0
            
            if self.roof.dimensions and len(self.roof.dimensions) >= 2:
                length = self.roof.dimensions[0]
                width = self.roof.dimensions[1]
                building_size = max(length, width)
                self.ground_size = max(building_size * 4.5, default_size)
                self.ground_size = min(self.ground_size, 80.0)
            else:
                self.ground_size = default_size
                
        except Exception as e:
            self.ground_size = 40.0
    
    def _create_coordinated_grass_ground(self):
        """Create grass ground using pv.Plane for reliable texture support"""
        try:
            ground_size = self.ground_size
            z_level = self.grass_ground_level


            # Use pv.Plane — it has proper built-in texture coordinates
            self.ground_mesh = pv.Plane(
                center=(0, 0, z_level),
                direction=(0, 0, 1),
                i_size=ground_size,
                j_size=ground_size,
                i_resolution=20,
                j_resolution=20
            )

            # Scale texture so it tiles instead of stretching
            texture_tiles = max(4, int(ground_size / 5))
            raw_tc = self.ground_mesh.active_texture_coordinates
            if raw_tc is not None:
                self.ground_mesh.active_texture_coordinates = raw_tc * texture_tiles

            # Use solid grass colour — texture loading is skipped for reliability
            grass_color = "#5AAA5A"
            self.ground_actor = self.plotter.add_mesh(
                self.ground_mesh,
                color=grass_color,
                name="ground_plane_roof",
                lighting=True,
                smooth_shading=True,
                ambient=0.35,
                diffuse=0.95,
                specular=0.0,
                pickable=False,
                reset_camera=False
            )

            # Tell sun system about ground level
            if self.roof.sun_system and hasattr(self.roof.sun_system, 'set_shadow_height'):
                self.roof.sun_system.set_shadow_height(z_level + 0.02)


        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _create_environment_attachment_points(self):
        """Create MORE attachment points for environment objects"""
        try:
            building_buffer = self.ground_size * 0.2

            # Calculate minimum safe distance outside the actual building footprint
            if self.roof.dimensions and len(self.roof.dimensions) >= 2:
                half_length = self.roof.dimensions[0] / 2
                half_width = self.roof.dimensions[1] / 2
                # Use half-diagonal so circular rings clear every corner
                min_safe_radius = np.sqrt(half_length**2 + half_width**2) + 1.5
            else:
                min_safe_radius = 6.0

            # Very close ring - right around the building (but never inside it)
            very_close_radius = max(building_buffer * 0.5, min_safe_radius)
            very_close_angles = np.linspace(0, 2*np.pi, 16, endpoint=False)
            
            for angle in very_close_angles:
                x = very_close_radius * np.cos(angle)
                y = very_close_radius * np.sin(angle)
                z = 0.3  # Above ground level for visibility
                self.environment_attachment_points.append({
                    'position': [x, y, z],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'very_close'
                })
            
            # Inner ring - closer to building (but never inside it)
            inner_radius = max(building_buffer, min_safe_radius)
            inner_angles = np.linspace(np.pi/16, 2*np.pi, 12, endpoint=False)
            
            for angle in inner_angles:
                x = inner_radius * np.cos(angle)
                y = inner_radius * np.sin(angle)
                z = 0.3
                self.environment_attachment_points.append({
                    'position': [x, y, z],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'inner'
                })
            
            # Middle ring
            middle_radius = building_buffer * 1.5
            middle_angles = np.linspace(0, 2*np.pi, 10, endpoint=False)
            
            for angle in middle_angles:
                x = middle_radius * np.cos(angle)
                y = middle_radius * np.sin(angle)
                z = 0.3
                self.environment_attachment_points.append({
                    'position': [x, y, z],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'middle'
                })
            
            # Outer ring
            outer_radius = building_buffer * 2.0
            outer_angles = np.linspace(np.pi/12, 2*np.pi, 8, endpoint=False)
            
            for angle in outer_angles:
                x = outer_radius * np.cos(angle)
                y = outer_radius * np.sin(angle)
                z = 0.3
                self.environment_attachment_points.append({
                    'position': [x, y, z],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'outer'
                })
            
            # Far ring (for large grounds)
            if self.ground_size > 40:
                far_radius = building_buffer * 2.5
                far_angles = np.linspace(0, 2*np.pi, 6, endpoint=False)
                
                for angle in far_angles:
                    x = far_radius * np.cos(angle)
                    y = far_radius * np.sin(angle)
                    z = 0.3
                    self.environment_attachment_points.append({
                        'position': [x, y, z],
                        'occupied': False,
                        'obstacle': None,
                        'ring': 'far'
                    })
            
            # Corner points for rectangular arrangement (outside building footprint)
            corner_offset = max(building_buffer * 0.7, min_safe_radius)
            corners = [
                (corner_offset, corner_offset),
                (corner_offset, -corner_offset),
                (-corner_offset, corner_offset),
                (-corner_offset, -corner_offset)
            ]
            
            for x, y in corners:
                self.environment_attachment_points.append({
                    'position': [x, y, 0.3],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'corner'
                })
            
            
        except Exception as e:
            pass

    
    def _create_attachment_points_visualization(self):
        """Create black dots mesh for all attachment points"""
        try:
            if not self.environment_attachment_points:
                return
            
            # Create a single mesh with all attachment points as spheres
            points = []
            for point_data in self.environment_attachment_points:
                points.append(point_data['position'])
            
            if points:
                # Create point cloud
                points_array = np.array(points)
                self.attachment_points_mesh = pv.PolyData(points_array)
                
                # Add scalar values for coloring (could be used for different states)
                scalars = np.ones(len(points))
                self.attachment_points_mesh['state'] = scalars
                
                
        except Exception as e:
            pass
    
    def show_environment_attachment_points(self):
        """Show attachment points as black dots on the ground"""
        try:
            # Remove existing actor if any
            if self.attachment_points_actor:
                try:
                    self.plotter.remove_actor(self.attachment_points_actor)
                    self.attachment_points_actor = None
                except:
                    pass
            
            # Get available (unoccupied) points
            available_points = []
            occupied_points = []
            
            for point_data in self.environment_attachment_points:
                if point_data['occupied']:
                    occupied_points.append(point_data['position'])
                else:
                    available_points.append(point_data['position'])
            
            # Show available points as black dots
            if available_points:
                available_array = np.array(available_points)
                available_cloud = pv.PolyData(available_array)

                self.attachment_points_actor = self.plotter.add_mesh(
                    available_cloud,
                    color='black',
                    point_size=25,
                    render_points_as_spheres=True,
                    name="env_attachment_points_available",
                    pickable=False,
                    opacity=1.0,
                    lighting=False  # No lighting = no shadow casting
                )

            self.attachment_points_visible = True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def hide_environment_attachment_points(self):
        """Hide all attachment points and cleanup visualization"""
        try:
            # Always restore interactor when hiding points (safety net)
            self._remove_click_placement_callback()
            self.environment_placement_mode = None

            # Remove main attachment points actor
            if self.attachment_points_actor:
                try:
                    self.plotter.remove_actor(self.attachment_points_actor)
                    self.attachment_points_actor = None
                except:
                    pass
            
            # Remove any text
            try:
                self.plotter.remove_actor("attachment_points_text")
            except:
                pass
            
            # Remove occupied points if shown
            try:
                self.plotter.remove_actor("env_attachment_points_occupied")
            except:
                pass
            
            self.attachment_points_visible = False
            
            # Force render to update display
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
            
        except Exception as e:
            pass

    def handle_environment_action(self, action_type, parameters):
        """Handle environment actions from UI"""
        try:
            
            action_handlers = {
                'add_tree': self._add_tree_direct,  # New direct placement
                'add_pole': self._add_pole_direct,  # New direct placement
                'prepare_tree_placement': self._prepare_tree_placement,  # Interactive mode
                'prepare_pole_placement': self._prepare_pole_placement,  # Interactive mode
                'update_tree_size': lambda p: setattr(self, 'tree_size_multiplier', p.get('multiplier', 1.0)),
                'update_pole_height': lambda p: setattr(self, 'pole_height_multiplier', p.get('multiplier', 1.0)),
                'toggle_attachment_points': self._toggle_attachment_points,
                'add_multiple_trees': self._add_multiple_trees_auto,
                'add_multiple_poles': self._add_multiple_poles_auto,
                'clear_all_environment': lambda p: self.clear_environment_obstacles(),
                'auto_populate_scene': self._auto_populate_environment,
            }
            
            handler = action_handlers.get(action_type)
            if handler:
                handler(parameters)
            
            # Render after action
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _add_tree_direct(self, parameters):
        """Enter interactive tree placement mode — user clicks a dot to place"""
        self.selected_tree_type = parameters.get('tree_type', 'deciduous')
        self.tree_size_multiplier = parameters.get('size_multiplier', 1.0)
        self.environment_placement_mode = 'tree'
        if not self.attachment_points_visible:
            self.show_environment_attachment_points()
        self._setup_click_placement_callback()

    def _add_pole_direct(self, parameters):
        """Enter interactive pole placement mode — user clicks a dot to place"""
        self.pole_height_multiplier = parameters.get('height_multiplier', 1.0)
        self.environment_placement_mode = 'pole'
        if not self.attachment_points_visible:
            self.show_environment_attachment_points()
        self._setup_click_placement_callback()

    # ──────────────────── click-to-place machinery ────────────────────

    def _setup_click_placement_callback(self):
        """Register left-click VTK observers for interactive placement.
        Disables the interactor style so left-click doesn't rotate the camera."""
        self._remove_click_placement_callback()
        self._press_pos = None

        # Disable camera interaction so left-click goes to our handler
        iren = self.plotter.iren
        self._saved_interactor_style = iren.GetInteractorStyle()
        iren.SetInteractorStyle(None)

        def on_press(obj, event):
            if self.environment_placement_mode:
                self._press_pos = self.plotter.iren.GetEventPosition()

        def on_release(obj, event):
            if not self.environment_placement_mode or self._press_pos is None:
                return
            cur = self.plotter.iren.GetEventPosition()
            if abs(cur[0] - self._press_pos[0]) > 5 or abs(cur[1] - self._press_pos[1]) > 5:
                self._press_pos = None
                return
            try:
                import vtk as _vtk
                renderer = getattr(self.plotter, 'renderer', None)
                if renderer is None and hasattr(self.plotter, 'renderers'):
                    renderer = self.plotter.renderers[0]
                if renderer is None:
                    return
                picker = _vtk.vtkWorldPointPicker()
                picker.Pick(self._press_pos[0], self._press_pos[1], 0, renderer)
                world_pos = picker.GetPickPosition()
                self._handle_placement_at_position(world_pos)
            except Exception:
                pass
            self._press_pos = None

        self._press_cb_id = self.plotter.iren.AddObserver(
            'LeftButtonPressEvent', on_press)
        self._release_cb_id = self.plotter.iren.AddObserver(
            'LeftButtonReleaseEvent', on_release)

    def _remove_click_placement_callback(self):
        """Remove click placement VTK observers and restore interactor style."""
        for attr in ('_press_cb_id', '_release_cb_id'):
            cb_id = getattr(self, attr, None)
            if cb_id is not None:
                try:
                    self.plotter.iren.RemoveObserver(cb_id)
                except Exception:
                    pass
                setattr(self, attr, None)
        # Restore camera interaction
        saved = getattr(self, '_saved_interactor_style', None)
        if saved is not None:
            try:
                self.plotter.iren.SetInteractorStyle(saved)
            except Exception:
                pass
            self._saved_interactor_style = None

    def _handle_placement_at_position(self, world_pos):
        """Find the nearest unoccupied dot to world_pos and place the object."""
        best_idx = None
        best_dist = float('inf')
        for i, pt_data in enumerate(self.environment_attachment_points):
            if pt_data['occupied']:
                continue
            pos = pt_data['position']
            # Compare in XY only — dots all sit at ground level
            dist = np.sqrt((pos[0] - world_pos[0]) ** 2 +
                           (pos[1] - world_pos[1]) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        if best_idx is None or best_dist > 6.0:
            return  # No nearby free point

        mode = self.environment_placement_mode
        if mode == 'tree':
            success = self._place_tree_at_index(best_idx)
        elif mode == 'pole':
            success = self._place_pole_at_index(best_idx)
        else:
            return

        if success:
            self.environment_placement_mode = None
            self._remove_click_placement_callback()
            self.hide_environment_attachment_points()
            if hasattr(self.plotter, 'render'):
                self.plotter.render()


    
    def _prepare_tree_placement(self, parameters):
        """Prepare for interactive tree placement"""
        try:
            self.selected_tree_type = parameters.get('tree_type', 'deciduous')
            self.tree_size_multiplier = parameters.get('size_multiplier', 1.0)
            self.environment_placement_mode = 'tree'

            if not self.attachment_points_visible:
                self.show_environment_attachment_points()

            self._setup_click_placement_callback()

        except Exception as e:
            pass
    
    def _prepare_pole_placement(self, parameters):
        """Prepare for interactive pole placement"""
        try:
            self.pole_height_multiplier = parameters.get('height_multiplier', 1.0)
            self.environment_placement_mode = 'pole'

            if not self.attachment_points_visible:
                self.show_environment_attachment_points()

            self._setup_click_placement_callback()

        except Exception as e:
            pass
    
    def _place_tree_at_index(self, point_index):
        """Place tree at attachment point and ensure points are hidden"""
        try:
            if point_index >= len(self.environment_attachment_points):
                return False
            
            point_data = self.environment_attachment_points[point_index]
            if point_data['occupied']:
                return False
            
            position = point_data['position']
            tree_type = self.selected_tree_type or 'deciduous'
            
            # Place tree at ground level (z=0)
            obstacle = self._add_scaled_tree([position[0], position[1]], tree_type, self.tree_size_multiplier)
            
            if obstacle:
                point_data['occupied'] = True
                point_data['obstacle'] = obstacle
                
                # Force hide attachment points after successful placement
                self.attachment_points_visible = False
                return True
            
            return False
            
        except Exception as e:
            return False

    def _place_pole_at_index(self, point_index):
        """Place pole at attachment point and ensure points are hidden"""
        try:
            if point_index >= len(self.environment_attachment_points):
                return False
            
            point_data = self.environment_attachment_points[point_index]
            if point_data['occupied']:
                return False
            
            position = point_data['position']
            
            # Place pole at ground level (z=0)
            obstacle = self._add_scaled_pole([position[0], position[1]], self.pole_height_multiplier)
            
            if obstacle:
                point_data['occupied'] = True
                point_data['obstacle'] = obstacle
                
                # Force hide attachment points after successful placement
                self.attachment_points_visible = False
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def _add_scaled_tree(self, position, tree_type='deciduous', size_multiplier=1.0):
        """Add tree with shadow casting capability - ENHANCED FOR ROOF SHADOWS"""
        try:
            x, y = position
            obstacle_id = len(self.environment_obstacles)
            
            # Check if tree is close enough to cast shadow on roof
            distance_from_center = np.sqrt(x**2 + y**2)
            building_size = max(self.roof.dimensions[0:2]) if self.roof.dimensions else 10
            
            # Tree dimensions with size multiplier
            if tree_type == 'pine':
                trunk_height = 2.5 * size_multiplier
                trunk_radius = 0.3 * size_multiplier
                tree_height = trunk_height + 5 * size_multiplier
                crown_radius = 1.5 * size_multiplier
            elif tree_type == 'oak':
                trunk_height = 3.0 * size_multiplier
                trunk_radius = 0.4 * size_multiplier
                tree_height = trunk_height + 5.5 * size_multiplier
                crown_radius = 3.5 * size_multiplier
            else:  # deciduous
                trunk_height = 3.5 * size_multiplier
                trunk_radius = 0.35 * size_multiplier
                tree_height = trunk_height + 4 * size_multiplier
                crown_radius = 2.5 * size_multiplier
            
            # Check if tree is tall enough and close enough to cast shadow on roof
            roof_height = self.roof.base_height + (self.roof.dimensions[2] if len(self.roof.dimensions) > 2 else 4)
            can_cast_on_roof = (tree_height > roof_height * 0.8) and (distance_from_center < building_size * 2)
            
            if can_cast_on_roof:
                pass
            
            # Create trunk
            trunk = pv.Cylinder(
                center=(x, y, trunk_height/2),
                direction=(0, 0, 1),
                radius=trunk_radius,
                height=trunk_height,
                resolution=20
            )
            trunk.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Store trunk mesh for shadow casting
            trunk_name = f"{tree_type}_trunk_{obstacle_id}"
            self.environment_meshes[trunk_name] = trunk
            
            # Get textures and colors
            if hasattr(self.roof, 'texture_manager'):
                bark_texture_file = (self.roof.texture_manager.pine_bark_texture_file 
                                    if tree_type == 'pine' 
                                    else self.roof.texture_manager.leaf_bark_texture_file)
                bark_texture, bark_loaded = self.roof.texture_manager.load_texture_safely(
                    bark_texture_file,
                    self.roof.texture_manager.default_bark_color
                )
            else:
                bark_texture = "#B08060"
                bark_loaded = False
            
            # Add trunk using sun compatible mesh
            if bark_loaded:
                self.roof.add_sun_compatible_mesh(
                    trunk,
                    texture=bark_texture,
                    name=trunk_name
                )
            else:
                self.roof.add_sun_compatible_mesh(
                    trunk,
                    color=bark_texture,
                    name=trunk_name
                )
            
            # Create crown based on tree type
            if tree_type == 'pine':
                # Pine tree with layered cones
                layers = [
                    (0.5 * size_multiplier, 2.2 * size_multiplier, 0.8 * size_multiplier),
                    (1.2 * size_multiplier, 1.9 * size_multiplier, 0.8 * size_multiplier),
                    (1.9 * size_multiplier, 1.6 * size_multiplier, 0.8 * size_multiplier),
                    (2.6 * size_multiplier, 1.3 * size_multiplier, 0.7 * size_multiplier),
                    (3.2 * size_multiplier, 1.0 * size_multiplier, 0.7 * size_multiplier)
                ]
                
                if hasattr(self.roof, 'texture_manager'):
                    pine_texture, pine_loaded = self.roof.texture_manager.load_texture_safely(
                        self.roof.texture_manager.pine_texture_file,
                        self.roof.texture_manager.default_pine_color
                    )
                else:
                    pine_texture = "#5A9A5A"
                    pine_loaded = False
                
                for layer_idx, (h_offset, radius, thickness) in enumerate(layers):
                    layer = pv.Cylinder(
                        center=(x, y, trunk_height + h_offset),
                        direction=(0, 0, 1),
                        radius=radius,
                        height=thickness,
                        resolution=30,
                        capping=True
                    )
                    layer.compute_normals(inplace=True, auto_orient_normals=True)
                    
                    layer_name = f"pine_crown_{obstacle_id}_layer_{layer_idx}"
                    self.environment_meshes[layer_name] = layer
                    
                    if pine_loaded:
                        self.roof.add_sun_compatible_mesh(
                            layer,
                            texture=pine_texture,
                            name=layer_name
                        )
                    else:
                        self.roof.add_sun_compatible_mesh(
                            layer,
                            color=pine_texture,
                            name=layer_name
                        )
            else:
                # Deciduous or oak tree with spherical crown
                crown_height = trunk_height + (2 * size_multiplier if tree_type == 'oak' else 1.5 * size_multiplier)
                
                crown = pv.Sphere(
                    center=(x, y, crown_height),
                    radius=crown_radius,
                    theta_resolution=35,
                    phi_resolution=35
                )
                
                # Generate texture coordinates
                if hasattr(self.roof, 'texture_manager'):
                    texture_coords = self.roof.texture_manager.generate_sphere_texture_coordinates(
                        crown, (x, y, crown_height), crown_radius
                    )
                    crown.active_texture_coordinates = texture_coords
                
                crown.compute_normals(inplace=True, auto_orient_normals=True)
                
                crown_name = f"{tree_type}_crown_{obstacle_id}"
                self.environment_meshes[crown_name] = crown
                
                if hasattr(self.roof, 'texture_manager'):
                    leaf_texture, leaf_loaded = self.roof.texture_manager.load_texture_safely(
                        self.roof.texture_manager.leaf_texture_file,
                        "#7EA040" if tree_type == 'oak' else self.roof.texture_manager.default_leaf_color
                    )
                else:
                    leaf_texture = "#7EA040" if tree_type == 'oak' else "#85D685"
                    leaf_loaded = False
                
                if leaf_loaded:
                    self.roof.add_sun_compatible_mesh(
                        crown,
                        texture=leaf_texture,
                        name=crown_name,
                        opacity=1.0
                    )
                else:
                    self.roof.add_sun_compatible_mesh(
                        crown,
                        color=leaf_texture,
                        name=crown_name,
                        opacity=1.0
                    )
            
            # REGISTER TREE WITH SUN SYSTEM FOR SHADOW - ENHANCED
            if self.roof.sun_system and hasattr(self.roof.sun_system, 'register_environment_object'):
                self.roof.sun_system.register_environment_object(
                    obj_type=f'tree_{tree_type}',
                    position=[x, y, 0],
                    height=tree_height,
                    radius=crown_radius
                )
                
                # If tree can cast on roof, ensure it's registered with higher priority
                if can_cast_on_roof and hasattr(self.roof.sun_system, 'register_roof_shadow_caster'):
                    self.roof.sun_system.register_roof_shadow_caster(
                        obj_type=f'tree_{tree_type}',
                        position=[x, y, 0],
                        height=tree_height,
                        radius=crown_radius
                    )
            
            obstacle_data = {
                'type': f'tree_{tree_type}',
                'position': position,
                'height': tree_height,
                'radius': crown_radius,
                'size_multiplier': size_multiplier,
                'id': obstacle_id,
                'can_cast_on_roof': can_cast_on_roof
            }
            
            self.environment_obstacles.append(obstacle_data)
            return obstacle_data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def _add_scaled_pole(self, position, height_multiplier=1.0):
        """Add pole with shadow casting capability"""
        try:
            x, y = position
            obstacle_id = len(self.environment_obstacles)
            
            pole_height = 7.0 * height_multiplier
            pole_radius = 0.15
            
            # Create pole cylinder
            pole = pv.Cylinder(
                center=(x, y, pole_height/2),
                direction=(0, 0, 1),
                radius=pole_radius,
                height=pole_height,
                resolution=12
            )
            pole.compute_normals(inplace=True, auto_orient_normals=True)
            
            pole_name = f"pole_{obstacle_id}"
            self.environment_meshes[pole_name] = pole
            
            # Get texture
            if hasattr(self.roof, 'texture_manager'):
                concrete_texture, concrete_loaded = self.roof.texture_manager.load_texture_safely(
                    self.roof.texture_manager.concrete_texture_file,
                    self.roof.texture_manager.default_concrete_color
                )
            else:
                concrete_texture = "#A0A0A0"
                concrete_loaded = False
            
            # Add pole
            if concrete_loaded:
                self.roof.add_sun_compatible_mesh(
                    pole,
                    texture=concrete_texture,
                    name=pole_name
                )
            else:
                self.roof.add_sun_compatible_mesh(
                    pole,
                    color=concrete_texture,
                    name=pole_name
                )
            
            # Create crossbeam
            beam_width = 2.0 * height_multiplier
            beam_thickness = 0.1
            beam = pv.Box(bounds=(
                x - beam_width/2, x + beam_width/2,
                y - beam_thickness/2, y + beam_thickness/2,
                pole_height - 1.0 * height_multiplier, pole_height - 0.7 * height_multiplier
            ))
            beam.compute_normals(inplace=True, auto_orient_normals=True)
            
            beam_name = f"pole_beam_{obstacle_id}"
            self.environment_meshes[beam_name] = beam
            
            self.roof.add_sun_compatible_mesh(
                beam,
                color="#B85432",
                name=beam_name
            )
            
            # REGISTER POLE WITH SUN SYSTEM FOR SHADOW
            if self.roof.sun_system and hasattr(self.roof.sun_system, 'register_environment_object'):
                self.roof.sun_system.register_environment_object(
                    obj_type='pole',
                    position=[x, y, 0],
                    height=pole_height,
                    radius=pole_radius
                )
            
            obstacle_data = {
                'type': 'pole',
                'position': position,
                'height': pole_height,
                'radius': pole_radius,
                'height_multiplier': height_multiplier,
                'id': obstacle_id
            }
            
            self.environment_obstacles.append(obstacle_data)
            return obstacle_data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def _toggle_attachment_points(self, parameters):
        """Toggle attachment points visibility"""
        visible = parameters.get('visible', False)
        if visible:
            self.show_environment_attachment_points()
        else:
            self.hide_environment_attachment_points()
    
    def _add_multiple_trees_auto(self, parameters):
        """Add multiple trees automatically"""
        try:
            count = parameters.get('count', 5)
            size_multiplier = parameters.get('size_multiplier', 1.0)
            
            tree_types = ['deciduous', 'pine', 'oak']
            added = 0
            
            for i, point_data in enumerate(self.environment_attachment_points):
                if not point_data['occupied'] and added < count:
                    tree_type = tree_types[added % len(tree_types)]
                    self.selected_tree_type = tree_type
                    self.tree_size_multiplier = size_multiplier
                    
                    if self._place_tree_at_index(i):
                        added += 1
            
            
        except Exception as e:
            pass
    
    def _add_multiple_poles_auto(self, parameters):
        """Add multiple poles automatically"""
        try:
            count = parameters.get('count', 3)
            height_multiplier = parameters.get('height_multiplier', 1.0)
            
            added = 0
            for i, point_data in enumerate(self.environment_attachment_points):
                if not point_data['occupied'] and added < count:
                    self.pole_height_multiplier = height_multiplier
                    if self._place_pole_at_index(i):
                        added += 1
            
            
        except Exception as e:
            pass
    
    def _auto_populate_environment(self, parameters):
        """Auto-populate environment with trees and poles"""
        try:
            tree_size = parameters.get('tree_size_multiplier', 1.0)
            pole_height = parameters.get('pole_height_multiplier', 1.0)
            
            # Add 6 trees
            self._add_multiple_trees_auto({'count': 6, 'size_multiplier': tree_size})
            
            # Add 3 poles
            self._add_multiple_poles_auto({'count': 3, 'height_multiplier': pole_height})
            
            
        except Exception as e:
            pass
    
    def add_environment_obstacle_at_point(self, obstacle_type, point_index=None):
        """Add environment obstacle at random available point and hide attachment points after placement"""
        try:
            if point_index is None:
                available_points = [i for i, p in enumerate(self.environment_attachment_points) 
                                if not p['occupied']]
                if not available_points:
                    return False
                
                import random
                point_index = random.choice(available_points)
            
            if point_index >= len(self.environment_attachment_points):
                return False
            
            point_data = self.environment_attachment_points[point_index]
            if point_data['occupied']:
                return False
            
            position = point_data['position']
            
            if obstacle_type == 'tree':
                tree_types = ['deciduous', 'pine', 'oak']
                tree_type = tree_types[self.tree_type_index % len(tree_types)]
                self.tree_type_index += 1
                obstacle = self._add_scaled_tree([position[0], position[1]], tree_type, 1.0)
            elif obstacle_type == 'pole':
                obstacle = self._add_scaled_pole([position[0], position[1]], 1.0)
            else:
                return False
            
            if obstacle:
                point_data['occupied'] = True
                point_data['obstacle'] = obstacle
                
                # IMPORTANT: Hide attachment points after successful placement
                self.hide_environment_attachment_points()
                
                # Clean up placement mode
                self.environment_placement_mode = None
                
                # Remove instruction text if exists
                if hasattr(self.roof, 'placement_instruction') and self.roof.placement_instruction:
                    try:
                        self.plotter.remove_actor(self.roof.placement_instruction)
                        self.roof.placement_instruction = None
                    except:
                        pass
                
                # Remove click callback if exists
                if self._environment_click_callback_id:
                    try:
                        self.plotter.iren.RemoveObserver(self._environment_click_callback_id)
                        self._environment_click_callback_id = None
                    except:
                        pass
                
                return True
            
            return False
            
        except Exception as e:
            return False

    
    def clear_environment_obstacles(self):
        """Clear all environment obstacles and update attachment points"""
        try:
            # Clear trees and poles from the scene
            for i in range(len(self.environment_obstacles)):
                obstacle = self.environment_obstacles[i]
                if obstacle['type'].startswith('tree'):
                    tree_type = obstacle['type'].split('_')[1] if '_' in obstacle['type'] else 'tree'
                    for prefix in ['tree', 'deciduous', 'oak', 'pine']:
                        try:
                            self.plotter.remove_actor(f"{prefix}_trunk_{i}")
                            self.plotter.remove_actor(f"{prefix}_crown_{i}")
                        except:
                            pass
                    
                    for layer_idx in range(10):
                        try:
                            self.plotter.remove_actor(f"pine_crown_{i}_layer_{layer_idx}")
                        except:
                            pass
                            
                elif obstacle['type'] == 'pole':
                    try:
                        self.plotter.remove_actor(f"pole_{i}")
                        self.plotter.remove_actor(f"pole_beam_{i}")
                    except:
                        pass
            
            # IMPORTANT: Clear shadows from sun system
            if self.roof.sun_system:
                # Method 1: Clear all environment objects from sun system
                if hasattr(self.roof.sun_system, 'clear_environment_objects'):
                    self.roof.sun_system.clear_environment_objects()
                
                # Method 2: Unregister each object individually (if method 1 doesn't exist)
                elif hasattr(self.roof.sun_system, 'unregister_environment_object'):
                    for obstacle in self.environment_obstacles:
                        self.roof.sun_system.unregister_environment_object(obstacle['id'])
                
                # Method 3: Clear all scene objects and re-register building only
                elif hasattr(self.roof.sun_system, 'clear_scene_objects'):
                    self.roof.sun_system.clear_scene_objects()
                    # Re-register building meshes
                    if hasattr(self.roof, 'house_walls'):
                        for i, wall in enumerate(self.roof.house_walls):
                            if wall:
                                self.roof.sun_system.register_scene_object(
                                    wall, f'building_wall_{i}', cast_shadow=True
                                )
                
                # Force shadow update after clearing
                if hasattr(self.roof.sun_system, '_update_shadows_only'):
                    self.roof.sun_system._update_shadows_only()
                elif hasattr(self.roof.sun_system, 'update_shadows'):
                    self.roof.sun_system.update_shadows()
            
            # Clear internal tracking
            self.environment_obstacles.clear()
            self.environment_meshes.clear()
            
            # Reset attachment points
            for point in self.environment_attachment_points:
                point['occupied'] = False
                point['obstacle'] = None
            
            self.tree_type_index = 0
            
            # Update attachment points display if visible
            if self.attachment_points_visible:
                self.show_environment_attachment_points()
            
            # Remove any messages
            try:
                self.plotter.remove_actor("all_occupied_message")
            except:
                pass
            
            # Force render to update the scene
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
            
            
        except Exception as e:
            import traceback
            traceback.print_exc()

    
    def cleanup(self):
        """Cleanup environment manager"""
        try:
            if self._environment_click_callback_id:
                self.plotter.iren.RemoveObserver(self._environment_click_callback_id)
                self._environment_click_callback_id = None
            
            self.environment_placement_mode = None
            self._remove_click_placement_callback()
            self.hide_environment_attachment_points()
            self.clear_environment_obstacles()
        except Exception as e:
            pass

            

