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
        
        print("✅ EnvironmentManager initialized")
    
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
                print(f"📏 Ground size: {self.ground_size:.1f}m")
            else:
                self.ground_size = default_size
                
        except Exception as e:
            print(f"⚠️ Error calculating ground size: {e}")
            self.ground_size = 40.0
    
    def _create_coordinated_grass_ground(self):
        """Create SCALABLE grass ground based on building dimensions - SAME AS WORKING CODE"""
        try:
            ground_size = self.ground_size
            z_level = self.grass_ground_level
            
            print(f"🌱 Creating grass ground ({ground_size:.1f}x{ground_size:.1f}m) at level: {z_level:.3f}")
            
            # Adjust resolution based on ground size
            resolution = int(40 + ground_size / 2)
            resolution = min(resolution, 80)
            
            x = np.linspace(-ground_size/2, ground_size/2, resolution)
            y = np.linspace(-ground_size/2, ground_size/2, resolution)
            x, y = np.meshgrid(x, y)
            
            # Add subtle terrain variation for realism
            z = np.ones_like(x) * z_level
            z += 0.02 * np.sin(x/5) * np.cos(y/5)
            
            # Create mesh
            points = np.c_[x.ravel(), y.ravel(), z.ravel()]
            self.ground_mesh = pv.PolyData(points)
            self.ground_mesh = self.ground_mesh.delaunay_2d()
            
            # Compute normals
            self.ground_mesh.compute_normals(inplace=True, auto_orient_normals=True)
            
            # Generate texture coordinates - scale based on ground size
            texture_scale = ground_size / 5.0
            texture_coords = np.zeros((self.ground_mesh.n_points, 2))
            for i in range(self.ground_mesh.n_points):
                point = self.ground_mesh.points[i]
                u = (point[0] + ground_size/2) / ground_size * texture_scale
                v = (point[1] + ground_size/2) / ground_size * texture_scale
                texture_coords[i] = [u, v]
            
            self.ground_mesh.active_t_coords = texture_coords
            
            # Load texture
            if hasattr(self.roof, 'texture_manager'):
                grass_texture, texture_loaded = self.roof.texture_manager.load_texture_safely(
                    self.roof.texture_manager.grass_texture_file,
                    self.roof.texture_manager.default_grass_color
                )
            else:
                grass_texture = "#6BCD6B"
                texture_loaded = False
            
            # Add ground with special rendering - SAME AS WORKING CODE
            if texture_loaded:
                self.ground_actor = self.plotter.add_mesh(
                    self.ground_mesh,
                    texture=grass_texture,
                    name="ground_plane_roof",
                    lighting=True,
                    smooth_shading=True,
                    ambient=0.4,
                    diffuse=0.95,
                    specular=0.0,
                    pickable=False,
                    render=True,
                    reset_camera=False
                )
            else:
                self.ground_actor = self.plotter.add_mesh(
                    self.ground_mesh,
                    color=grass_texture,
                    name="ground_plane_roof",
                    lighting=True,
                    smooth_shading=True,
                    ambient=0.4,
                    diffuse=0.95,
                    specular=0.0,
                    pickable=False,
                    render=True,
                    reset_camera=False
                )
            
            # Set render order if possible - SAME AS WORKING CODE
            if self.ground_actor and hasattr(self.ground_actor, 'GetProperty'):
                prop = self.ground_actor.GetProperty()
                if hasattr(prop, 'SetOpacity'):
                    prop.SetOpacity(0.999)
                if hasattr(prop, 'SetBackfaceCulling'):
                    prop.SetBackfaceCulling(False)
            
            # Tell sun system about ground level - CRITICAL
            if self.roof.sun_system and hasattr(self.roof.sun_system, 'set_shadow_height'):
                self.roof.sun_system.set_shadow_height(z_level + 0.02)
            
            print(f"✅ Scalable grass ground created")
            
        except Exception as e:
            print(f"❌ Error creating grass ground: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_environment_attachment_points(self):
        """Create attachment points for environment objects"""
        try:
            building_buffer = self.ground_size * 0.2
            
            # Inner ring - closer to building
            angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
            radius = building_buffer
            
            for angle in angles:
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                # Place points slightly above ground to be visible
                z = 0.01  # Just above ground level
                self.environment_attachment_points.append({
                    'position': [x, y, z],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'inner'
                })
            
            # Middle ring
            middle_radius = building_buffer * 1.5
            middle_angles = np.linspace(np.pi/12, 2*np.pi, 8, endpoint=False)
            
            for angle in middle_angles:
                x = middle_radius * np.cos(angle)
                y = middle_radius * np.sin(angle)
                z = 0.01
                self.environment_attachment_points.append({
                    'position': [x, y, z],
                    'occupied': False,
                    'obstacle': None,
                    'ring': 'middle'
                })
            
            # Outer ring (for large grounds)
            if self.ground_size > 40:
                outer_radius = building_buffer * 2.0
                outer_angles = np.linspace(0, 2*np.pi, 6, endpoint=False)
                
                for angle in outer_angles:
                    x = outer_radius * np.cos(angle)
                    y = outer_radius * np.sin(angle)
                    z = 0.01
                    self.environment_attachment_points.append({
                        'position': [x, y, z],
                        'occupied': False,
                        'obstacle': None,
                        'ring': 'outer'
                    })
            
            print(f"✅ Created {len(self.environment_attachment_points)} attachment points")
            
        except Exception as e:
            print(f"❌ Error creating attachment points: {e}")
    
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
                
                print(f"✅ Created attachment points visualization mesh with {len(points)} points")
                
        except Exception as e:
            print(f"❌ Error creating attachment points visualization: {e}")
    
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
                
                # Add as black spheres
                self.attachment_points_actor = self.plotter.add_mesh(
                    available_cloud,
                    color='black',
                    point_size=20,
                    render_points_as_spheres=True,
                    name="env_attachment_points_available",
                    pickable=True,  # Make them pickable for interaction
                    opacity=0.8
                )
            
            # Optionally show occupied points in a different color (red)
            if occupied_points and False:  # Set to True if you want to see occupied points
                occupied_array = np.array(occupied_points)
                occupied_cloud = pv.PolyData(occupied_array)
                
                self.plotter.add_mesh(
                    occupied_cloud,
                    color='red',
                    point_size=15,
                    render_points_as_spheres=True,
                    name="env_attachment_points_occupied",
                    pickable=False,
                    opacity=0.5
                )
            
            self.attachment_points_visible = True
            print(f"✅ Showing {len(available_points)} available attachment points as black dots")
            
            # Add helper text
            if available_points:
                self.plotter.add_text(
                    f"{len(available_points)} placement points available",
                    position="upper_right",
                    font_size=10,
                    color="black",
                    name="attachment_points_text"
                )
            
        except Exception as e:
            print(f"❌ Error showing attachment points: {e}")
            import traceback
            traceback.print_exc()
    
    def hide_environment_attachment_points(self):
        """Hide attachment points"""
        try:
            # Remove attachment points actor
            if self.attachment_points_actor:
                self.plotter.remove_actor(self.attachment_points_actor)
                self.attachment_points_actor = None
            
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
            print("✅ Hidden attachment points")
            
        except Exception as e:
            print(f"⚠️ Error hiding attachment points: {e}")
    
    def handle_environment_action(self, action_type, parameters):
        """Handle environment actions from UI"""
        try:
            print(f"🎯 Handling environment action: {action_type}")
            
            action_handlers = {
                'prepare_tree_placement': self._prepare_tree_placement,
                'prepare_pole_placement': self._prepare_pole_placement,
                'update_tree_size': lambda p: setattr(self, 'tree_size_multiplier', p.get('multiplier', 1.0)),
                'update_pole_height': lambda p: setattr(self, 'pole_height_multiplier', p.get('multiplier', 1.0)),
                'toggle_attachment_points': self._toggle_attachment_points,
                'add_multiple_trees': self._add_multiple_trees_auto,
                'add_multiple_poles': self._add_multiple_poles_auto,
                'clear_all_environment': lambda p: self.clear_environment_obstacles(),
                'auto_populate_scene': self._auto_populate_environment,
                # Ignore cardinal-related actions
                'add_cardinal': lambda p: None,
                'add_cardinal_flock': lambda p: None,
                'clear_cardinals': lambda p: None
            }
            
            handler = action_handlers.get(action_type)
            if handler:
                handler(parameters)
            
            # Update attachment points display if visible
            if self.attachment_points_visible:
                self.show_environment_attachment_points()
            
            # Render after action
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                
        except Exception as e:
            print(f"❌ Error handling environment action: {e}")
            import traceback
            traceback.print_exc()
    
    def _prepare_tree_placement(self, parameters):
        """Prepare for interactive tree placement"""
        try:
            self.selected_tree_type = parameters.get('tree_type', 'deciduous')
            self.tree_size_multiplier = parameters.get('size_multiplier', 1.0)
            self.environment_placement_mode = 'tree'
            
            # Show attachment points if not already visible
            if not self.attachment_points_visible:
                self.show_environment_attachment_points()
            
            # Update instruction text
            if hasattr(self.roof, 'placement_instruction') and self.roof.placement_instruction:
                self.plotter.remove_actor(self.roof.placement_instruction)
            
            self.roof.placement_instruction = self.plotter.add_text(
                f"Click on a black dot to place {self.selected_tree_type} tree",
                position="lower_left",
                font_size=12,
                color="white"
            )
            
            self._setup_environment_click_callback()
            print(f"✅ Ready to place {self.selected_tree_type} tree on black dots")
            
        except Exception as e:
            print(f"❌ Error preparing tree placement: {e}")
    
    def _prepare_pole_placement(self, parameters):
        """Prepare for interactive pole placement"""
        try:
            self.pole_height_multiplier = parameters.get('height_multiplier', 1.0)
            self.environment_placement_mode = 'pole'
            
            # Show attachment points if not already visible
            if not self.attachment_points_visible:
                self.show_environment_attachment_points()
            
            # Update instruction text
            if hasattr(self.roof, 'placement_instruction') and self.roof.placement_instruction:
                self.plotter.remove_actor(self.roof.placement_instruction)
            
            self.roof.placement_instruction = self.plotter.add_text(
                "Click on a black dot to place utility pole",
                position="lower_left",
                font_size=12,
                color="white"
            )
            
            self._setup_environment_click_callback()
            print("✅ Ready to place utility pole on black dots")
            
        except Exception as e:
            print(f"❌ Error preparing pole placement: {e}")
    
    def _setup_environment_click_callback(self):
        """Set up click callback for placement"""
        try:
            if self._environment_click_callback_id:
                self.plotter.iren.RemoveObserver(self._environment_click_callback_id)
                self._environment_click_callback_id = None
            
            def on_click(obj, event):
                click_pos = self.plotter.pick_mouse_position()
                if click_pos:
                    self._handle_environment_click(click_pos)
            
            self._environment_click_callback_id = self.plotter.iren.AddObserver(
                "LeftButtonPressEvent", on_click
            )
            
        except Exception as e:
            print(f"❌ Error setting up click callback: {e}")
    
    def _handle_environment_click(self, click_pos):
        """Handle click for object placement"""
        try:
            # Find closest attachment point
            closest_index = None
            closest_distance = float('inf')
            
            for i, point_data in enumerate(self.environment_attachment_points):
                if not point_data['occupied']:
                    pos = point_data['position']
                    # Calculate 2D distance (ignore Z)
                    distance = np.sqrt((pos[0] - click_pos[0])**2 + (pos[1] - click_pos[1])**2)
                    if distance < closest_distance and distance < 2.0:  # Within 2 units
                        closest_distance = distance
                        closest_index = i
            
            if closest_index is not None:
                # Place object
                success = False
                if self.environment_placement_mode == 'tree':
                    success = self._place_tree_at_index(closest_index)
                elif self.environment_placement_mode == 'pole':
                    success = self._place_pole_at_index(closest_index)
                
                if success:
                    # Update attachment points display
                    if self.attachment_points_visible:
                        self.show_environment_attachment_points()
                    
                    # Check if all points are occupied
                    available_count = sum(1 for p in self.environment_attachment_points if not p['occupied'])
                    if available_count == 0:
                        # All points occupied, exit placement mode
                        self.environment_placement_mode = None
                        
                        # Remove instruction
                        if hasattr(self.roof, 'placement_instruction') and self.roof.placement_instruction:
                            self.plotter.remove_actor(self.roof.placement_instruction)
                            self.roof.placement_instruction = None
                        
                        # Remove click callback
                        if self._environment_click_callback_id:
                            self.plotter.iren.RemoveObserver(self._environment_click_callback_id)
                            self._environment_click_callback_id = None
                        
                        # Show message
                        self.plotter.add_text(
                            "All attachment points occupied!",
                            position="lower_left",
                            font_size=12,
                            color="red",
                            name="all_occupied_message"
                        )
                
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
            else:
                print("⚠️ No available attachment point near click location")
        
        except Exception as e:
            print(f"❌ Error handling click: {e}")
    
    def _place_tree_at_index(self, point_index):
        """Place tree at attachment point"""
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
                print(f"✅ Placed {tree_type} tree at point {point_index} (will cast shadows)")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error placing tree: {e}")
            return False
    
    def _place_pole_at_index(self, point_index):
        """Place pole at attachment point"""
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
                print(f"✅ Placed utility pole at point {point_index} (will cast shadows)")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error placing pole: {e}")
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
                print(f"🌳 Tree at ({x:.1f}, {y:.1f}) is close enough to cast shadow on roof")
            
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
                    crown.active_t_coords = texture_coords
                
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
                    print(f"✅ Tree registered as roof shadow caster")
            
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
            print(f"❌ Error adding scaled tree: {e}")
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
            print(f"❌ Error adding scaled pole: {e}")
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
            
            print(f"✅ Added {added} mixed trees")
            
        except Exception as e:
            print(f"❌ Error adding multiple trees: {e}")
    
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
            
            print(f"✅ Added {added} utility poles")
            
        except Exception as e:
            print(f"❌ Error adding multiple poles: {e}")
    
    def _auto_populate_environment(self, parameters):
        """Auto-populate environment with trees and poles"""
        try:
            tree_size = parameters.get('tree_size_multiplier', 1.0)
            pole_height = parameters.get('pole_height_multiplier', 1.0)
            
            # Add 6 trees
            self._add_multiple_trees_auto({'count': 6, 'size_multiplier': tree_size})
            
            # Add 3 poles
            self._add_multiple_poles_auto({'count': 3, 'height_multiplier': pole_height})
            
            print("✅ Auto-populated environment")
            
        except Exception as e:
            print(f"❌ Error auto-populating: {e}")
    
    def add_environment_obstacle_at_point(self, obstacle_type, point_index=None):
        """Add environment obstacle at random available point"""
        try:
            if point_index is None:
                available_points = [i for i, p in enumerate(self.environment_attachment_points) 
                                  if not p['occupied']]
                if not available_points:
                    print("⚠️ No available points")
                    return False
                
                import random
                point_index = random.choice(available_points)
            
            if point_index >= len(self.environment_attachment_points):
                print(f"⚠️ Invalid point index: {point_index}")
                return False
            
            point_data = self.environment_attachment_points[point_index]
            if point_data['occupied']:
                print(f"⚠️ Point {point_index} is occupied")
                return False
            
            position = point_data['position']
            
            if obstacle_type == 'tree':
                tree_types = ['deciduous', 'pine', 'oak']
                tree_type = tree_types[self.roof.tree_type_index % len(tree_types)]
                self.roof.tree_type_index += 1
                obstacle = self._add_scaled_tree([position[0], position[1]], tree_type, 1.0)
            elif obstacle_type == 'pole':
                obstacle = self._add_scaled_pole([position[0], position[1]], 1.0)
            else:
                print(f"⚠️ Unknown obstacle type: {obstacle_type}")
                return False
            
            point_data['occupied'] = True
            point_data['obstacle'] = obstacle
            
            # Update attachment points display if visible
            if self.attachment_points_visible:
                self.show_environment_attachment_points()
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding obstacle: {e}")
            return False
    
    def clear_environment_obstacles(self):
        """Clear all environment obstacles and update attachment points"""
        try:
            # Clear trees and poles
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
            
            print("✅ Cleared all environment obstacles, attachment points reset")
            
        except Exception as e:
            print(f"❌ Error clearing environment: {e}")
    
    def cleanup(self):
        """Cleanup environment manager"""
        try:
            if self._environment_click_callback_id:
                self.plotter.iren.RemoveObserver(self._environment_click_callback_id)
                self._environment_click_callback_id = None
            
            self.hide_environment_attachment_points()
            self.clear_environment_obstacles()
            print("✅ EnvironmentManager cleanup completed")
        except Exception as e:
            print(f"❌ Error during environment cleanup: {e}")

    def show_environment_attachment_points(self):
        """Show attachment points as black dots on the ground - ENHANCED DEBUG VERSION"""
        try:
            print("\n" + "-"*50)
            print("DEBUG: show_environment_attachment_points called")
            print("-"*50)
            
            # Check plotter
            if not self.plotter:
                print("❌ No plotter available!")
                return
            print(f"✅ Plotter: {type(self.plotter)}")
            
            # Check attachment points
            if not self.environment_attachment_points:
                print("❌ No attachment points created!")
                return
            print(f"✅ Total attachment points: {len(self.environment_attachment_points)}")
            
            # Remove existing actor if any
            if self.attachment_points_actor:
                try:
                    self.plotter.remove_actor(self.attachment_points_actor)
                    self.attachment_points_actor = None
                    print("✅ Removed existing attachment points actor")
                except Exception as e:
                    print(f"⚠️ Could not remove existing actor: {e}")
            
            # Get available (unoccupied) points
            available_points = []
            occupied_points = []
            
            for point_data in self.environment_attachment_points:
                if point_data['occupied']:
                    occupied_points.append(point_data['position'])
                else:
                    available_points.append(point_data['position'])
            
            print(f"📍 Available points: {len(available_points)}")
            print(f"📍 Occupied points: {len(occupied_points)}")
            
            if not available_points:
                print("⚠️ No available points to show")
                return
            
            # Show first few points for debugging
            print("First 3 available points:")
            for i, point in enumerate(available_points[:3]):
                print(f"  Point {i}: {point}")
            
            # Create point cloud
            available_array = np.array(available_points)
            available_cloud = pv.PolyData(available_array)
            print(f"✅ Created PolyData with {available_cloud.n_points} points")
            
            # Try different visualization methods
            print("\n🎯 Attempting to add points to scene...")
            
            # Method 1: As spheres at each point
            try:
                for i, point in enumerate(available_points[:5]):  # Show first 5 as test
                    sphere = pv.Sphere(center=point, radius=0.2)
                    actor = self.plotter.add_mesh(
                        sphere,
                        color='red',  # Use red for visibility
                        name=f"attachment_sphere_{i}",
                        opacity=1.0
                    )
                    print(f"  ✅ Added sphere {i} at {point}")
            except Exception as e:
                print(f"  ❌ Failed to add spheres: {e}")
            
            # Method 2: As point cloud
            try:
                self.attachment_points_actor = self.plotter.add_mesh(
                    available_cloud,
                    color='black',
                    point_size=30,  # Larger size
                    render_points_as_spheres=True,
                    name="env_attachment_points_available",
                    pickable=True,
                    opacity=1.0,
                    reset_camera=False  # Don't reset camera
                )
                print(f"✅ Added point cloud actor")
            except Exception as e:
                print(f"❌ Failed to add point cloud: {e}")
                import traceback
                traceback.print_exc()
            
            # Force render
            try:
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                    print("✅ Called plotter.render()")
            except Exception as e:
                print(f"⚠️ Could not call render: {e}")
            
            self.attachment_points_visible = True
            print(f"✅ attachment_points_visible = {self.attachment_points_visible}")
            
            # Check camera position
            if hasattr(self.plotter, 'camera_position'):
                cam_pos = self.plotter.camera_position
                print(f"📷 Camera position: {cam_pos}")
            
            print("-"*50 + "\n")
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR in show_environment_attachment_points: {e}")
            import traceback
            traceback.print_exc()
            