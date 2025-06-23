#!/usr/bin/env python3
"""
Complete PyVista Building Generator with Solar Simulation - FIXED VERSION
"""
import numpy as np
import pyvista as pv
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import math
import traceback

class PyVistaBuildingGenerator(QObject):
    """Complete PyVista building generator with solar simulation - FIXED VERSION"""
    
    # Signals
    solar_time_changed = pyqtSignal(int)
    animation_step = pyqtSignal(int)
    building_generated = pyqtSignal()
    sun_position_changed = pyqtSignal(float, float)  # azimuth, elevation
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.plotter = None
        self.current_building = None
        
        # Solar simulation parameters
        self.solar_time = 12  # Hour of day (0-23)
        self.solar_day = 172  # Day of year (1-365), 172 = summer solstice
        self.latitude = 48.3  # Default latitude (Slovakia)
        self.longitude = 18.0  # Default longitude (Slovakia)
        
        # Building parameters
        self.current_height = 3.0
        self.current_roof_type = 'flat'
        self.current_roof_pitch = 30.0
        self.current_points = []
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_sun)
        self.animation_step_count = 0
        
        # FIXED: Debug mode for reliable basic display
        self.debug_mode = True
        self.shadows_enabled = True
        self.sunshafts_enabled = True
        self.reflections_enabled = True
        self.volumetric_lighting = True
        
        print("✅ PyVista Building Generator initialized - FIXED VERSION")
        
    def set_plotter(self, plotter):
        """Set the PyVista plotter reference - FIXED WITH RENDERING"""
        self.plotter = plotter
        if self.plotter:
            self._setup_scene_comprehensive()
            print("✅ Plotter connected to building generator")
        
    def _setup_scene_comprehensive(self):
        """Setup initial 3D scene - FIXED FOR RELIABILITY"""
        try:
            if not self.plotter:
                print("❌ No plotter available for scene setup")
                return
                
            print("🔧 Setting up 3D scene...")
            
            # FIXED: Simplified background setting
            try:
                self.plotter.set_background('lightblue')
                print("✅ Background set")
            except Exception as e:
                print(f"⚠️ Background warning: {e}")
            
            # FIXED: Simplified ground plane
            try:
                ground = pv.Plane(
                    center=(0, 0, -0.1),
                    direction=(0, 0, 1),
                    i_size=20,
                    j_size=20,
                    i_resolution=10,
                    j_resolution=10
                )
                
                self.plotter.add_mesh(
                    ground, 
                    name='ground',
                    color='lightgreen',
                    opacity=0.5,
                    show_edges=True,
                    edge_color='darkgreen'
                )
                print("✅ Ground plane added")
            except Exception as e:
                print(f"⚠️ Ground plane warning: {e}")
            
            # FIXED: Simplified axes
            try:
                self.plotter.add_axes(interactive=True)
                print("✅ Axes added")
            except Exception as e:
                print(f"⚠️ Axes warning: {e}")
            
            # FIXED: Reliable camera positioning
            try:
                self.plotter.camera_position = [
                    (15, 15, 10),  # Camera position
                    (0, 0, 0),     # Look at point
                    (0, 0, 1)      # Up vector
                ]
                print("✅ Camera positioned")
            except Exception as e:
                print(f"⚠️ Camera warning: {e}")
            
            # FIXED: Single render call
            self._force_render_multiple()
            
            print("✅ Scene setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up scene: {e}")
            traceback.print_exc()
    
    def _force_render_multiple(self):
        """Force render - SIMPLIFIED AND FIXED"""
        try:
            if not self.plotter:
                return
                
            print("🔄 Rendering...")
            
            # FIXED: Single, reliable render call
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                print("✅ Render complete")
            else:
                print("⚠️ No render method available")
                
        except Exception as e:
            print(f"⚠️ Render warning: {e}")
    
    def create_building_from_canvas(self, points, height=3.0, roof_type='flat', roof_pitch=30.0):
        """Create 3D building from canvas points - FIXED VERSION"""
        try:
            print(f"🏗️ Creating building from {len(points)} canvas points")
            print(f"Parameters: height={height}m, roof={roof_type}, pitch={roof_pitch}°")
            
            if not points or len(points) < 3:
                print("❌ Need at least 3 points to create building")
                return False
                
            if not self.plotter:
                print("❌ Plotter not set")
                return False
                
            # Store current parameters
            self.current_points = points
            self.current_height = height
            self.current_roof_type = roof_type
            self.current_roof_pitch = roof_pitch
                
            # Clear existing building
            self.clear_current_building()
            
            # Convert canvas points to 3D coordinates
            vertices_3d = self._canvas_points_to_3d(points)
            
            if not vertices_3d:
                print("❌ Failed to convert points to 3D")
                return False
            
            # Create building mesh
            building_mesh = self._create_building_mesh(vertices_3d, height, roof_type, roof_pitch)
            
            if not building_mesh:
                print("❌ Failed to create building mesh")
                return False
            
            # FIXED: Add building with reliable settings
            try:
                self.plotter.add_mesh(
                    building_mesh, 
                    name='building',
                    color='lightcoral',
                    show_edges=True,
                    edge_color='darkred',
                    line_width=2,
                    opacity=0.9
                )
                print("✅ Building mesh added to plotter")
            except Exception as e:
                print(f"❌ Error adding building mesh: {e}")
                return False
            
            # Store building reference
            self.current_building = building_mesh
            
            # FIXED: Reset camera for building
            self._reset_camera_for_building_fixed(building_mesh)
            
            # FIXED: Add ground plane for reference
            self._add_enhanced_ground_plane()
            
            # FIXED: Add solar visualization only if not in debug mode
            if not self.debug_mode:
                self._update_solar_visualization()
            
            # FIXED: Single render
            self._force_render_multiple()
            
            # Emit signal
            self.building_generated.emit()
            
            print("✅ 3D Building created successfully!")
            return True
                
        except Exception as e:
            print(f"❌ Error creating building: {e}")
            traceback.print_exc()
            return False
    
    def _canvas_points_to_3d(self, canvas_points):
        """Convert 2D canvas points to 3D building coordinates - FIXED"""
        try:
            # Convert to numpy array and normalize
            points = np.array(canvas_points, dtype=float)
            
            # Remove duplicate points (if polygon is closed)
            if len(points) > 3 and np.allclose(points[0], points[-1]):
                points = points[:-1]
            
            # Center the points
            center = np.mean(points, axis=0)
            centered_points = points - center
            
            # FIXED: Better scale for visibility
            scale = 0.1  # Increased from 0.05 to 0.1 for better visibility
            scaled_points = centered_points * scale
            
            # Create base vertices (ground level z=0)
            base_vertices = []
            for point in scaled_points:
                base_vertices.append([point[0], point[1], 0.0])
            
            print(f"📐 Converted {len(canvas_points)} canvas points to {len(base_vertices)} 3D vertices")
            print(f"📐 Scale factor: {scale}")
            
            # Debug: Print coordinate ranges
            if base_vertices:
                x_coords = [v[0] for v in base_vertices]
                y_coords = [v[1] for v in base_vertices]
                print(f"📍 X range: {min(x_coords):.3f} to {max(x_coords):.3f}")
                print(f"📍 Y range: {min(y_coords):.3f} to {max(y_coords):.3f}")
                
            return base_vertices
            
        except Exception as e:
            print(f"❌ Error converting canvas points: {e}")
            return None
    
    def _create_building_mesh(self, vertices_3d, height, roof_type, roof_pitch):
        """Create PyVista mesh from 3D vertices - FIXED"""
        try:
            base_verts = vertices_3d
            n_points = len(base_verts)
            
            print(f"🏗️ Creating mesh: {n_points} base points, height={height}")
            
            # Create wall top vertices
            wall_top_verts = []
            for vertex in base_verts:
                wall_top_verts.append([vertex[0], vertex[1], height])
            
            # Start with base and wall top vertices
            all_vertices = base_verts + wall_top_verts
            
            # Create faces list
            faces = []
            
            # Ground face (bottom) - reverse order for correct normal
            ground_face = [n_points] + list(reversed(range(n_points)))
            faces.append(ground_face)
            
            # Create roof vertices and faces
            if roof_type.lower() == 'flat':
                # Flat roof - just the top face
                roof_face = [n_points] + list(range(n_points, 2 * n_points))
                faces.append(roof_face)
                
            elif roof_type.lower() == 'gabled':
                # Gabled roof
                roof_vertices, roof_faces = self._create_gabled_roof(base_verts, height, roof_pitch)
                if roof_vertices:
                    all_vertices.extend(roof_vertices)
                    faces.extend(roof_faces)
                    
            elif roof_type.lower() == 'hipped':
                # Hipped roof
                roof_vertices, roof_faces = self._create_hipped_roof(base_verts, height, roof_pitch)
                if roof_vertices:
                    all_vertices.extend(roof_vertices)
                    faces.extend(roof_faces)
            else:
                # Default to flat roof
                roof_face = [n_points] + list(range(n_points, 2 * n_points))
                faces.append(roof_face)
            
            # Wall faces
            for i in range(n_points):
                next_i = (i + 1) % n_points
                # Create wall quad: base[i] -> base[next_i] -> top[next_i] -> top[i]
                wall_face = [4, i, next_i, next_i + n_points, i + n_points]
                faces.append(wall_face)
            
            # Convert to PyVista format
            vertices_array = np.array(all_vertices, dtype=float)
            
            # Flatten faces for PyVista
            faces_flat = []
            for face in faces:
                faces_flat.extend(face)
            faces_array = np.array(faces_flat, dtype=int)
            
            # Create mesh
            mesh = pv.PolyData(vertices_array, faces_array)
            
            # FIXED: Compute normals for better rendering
            try:
                mesh = mesh.compute_normals()
            except Exception as e:
                print(f"⚠️ Could not compute normals: {e}")
            
            print(f"✅ Created building mesh: {len(vertices_array)} vertices, {len(faces)} faces")
            print(f"📐 Mesh bounds: {mesh.bounds}")
            
            return mesh
            
        except Exception as e:
            print(f"❌ Error creating building mesh: {e}")
            traceback.print_exc()
            return None
    
    def _reset_camera_for_building_fixed(self, building_mesh):
        """Reset camera to properly view the building - FIXED"""
        try:
            if not building_mesh or not self.plotter:
                return
                
            print("📹 Resetting camera for building...")
            
            # Get building bounds and center
            bounds = building_mesh.bounds
            center = building_mesh.center
            
            print(f"📐 Building bounds: {bounds}")
            print(f"📐 Building center: {center}")
            
            # Calculate appropriate camera distance
            x_range = bounds[1] - bounds[0]
            y_range = bounds[3] - bounds[2]
            z_range = bounds[5] - bounds[4]
            max_range = max(x_range, y_range, z_range)
            
            # FIXED: Ensure reasonable camera distance
            camera_distance = max(5.0, max_range * 4.0)  # Minimum 5 units away
            
            # Set camera position
            camera_pos = [
                center[0] + camera_distance,
                center[1] + camera_distance,
                center[2] + camera_distance
            ]
            
            # FIXED: Apply camera position safely
            try:
                self.plotter.camera_position = [camera_pos, center, (0, 0, 1)]
                print(f"✅ Camera position set: {camera_pos}")
            except Exception as e:
                print(f"⚠️ Camera position warning: {e}")
            
            # FIXED: Additional camera commands with error handling
            try:
                self.plotter.reset_camera()
                print("✅ Camera reset")
            except Exception as e:
                print(f"⚠️ Camera reset warning: {e}")
                
            try:
                self.plotter.view_isometric()
                print("✅ Isometric view set")
            except Exception as e:
                print(f"⚠️ Isometric view warning: {e}")
            
            print(f"✅ Camera setup complete: distance={camera_distance:.2f}")
            
        except Exception as e:
            print(f"❌ Camera reset error: {e}")
            traceback.print_exc()
    
    def _add_enhanced_ground_plane(self):
        """Add enhanced ground plane with high visibility - FIXED"""
        try:
            if not self.plotter:
                return
                
            # Remove existing ground
            try:
                self.plotter.remove_actor('ground')
                self.plotter.remove_actor('ground_grid')
            except:
                pass
            
            # FIXED: Create larger, more visible ground plane
            ground = pv.Plane(
                center=(0, 0, -0.1),
                direction=(0, 0, 1),
                i_size=30,  # Larger
                j_size=30,  # Larger
                i_resolution=15,
                j_resolution=15
            )
            
            # Add ground with high visibility
            self.plotter.add_mesh(
                ground, 
                name='ground',
                color='lightgreen',
                opacity=0.6,
                show_edges=True,
                edge_color='darkgreen',
                line_width=1
            )
            
            print("✅ Enhanced ground plane added")
            
        except Exception as e:
            print(f"⚠️ Could not add enhanced ground plane: {e}")
    
    def clear_current_building(self):
        """Clear current building from plotter - FIXED"""
        try:
            if self.plotter:
                # Remove building-related actors
                actors_to_remove = ['building', 'sun', 'sun_ray', 'sun_path']
                for actor_name in actors_to_remove:
                    try:
                        self.plotter.remove_actor(actor_name)
                        print(f"✅ Removed actor: {actor_name}")
                    except:
                        pass
                
                # FIXED: Force render after clearing
                self._force_render_multiple()
                
            self.current_building = None
            print("✅ Building cleared")
            
        except Exception as e:
            print(f"❌ Error clearing building: {e}")
    
    def set_debug_mode(self, debug=True):
        """Enable debug mode - disables complex features for basic building display"""
        self.debug_mode = debug
        if debug:
            self.shadows_enabled = False
            self.sunshafts_enabled = False
            self.reflections_enabled = False
            self.volumetric_lighting = False
            print("🔧 Debug mode enabled - complex features disabled")
        else:
            self.shadows_enabled = True
            self.sunshafts_enabled = True
            self.reflections_enabled = True
            self.volumetric_lighting = True
            print("🔧 Debug mode disabled - all features enabled")
    
    def debug_plotter_state(self):
        """Debug plotter state for troubleshooting"""
        try:
            print("\n🔍 === PLOTTER DEBUG INFO ===")
            
            if not self.plotter:
                print("❌ No plotter available")
                return
            
            # Check plotter type and attributes
            print(f"📊 Plotter type: {type(self.plotter)}")
            
            # Check actors
            try:
                if hasattr(self.plotter, 'actors'):
                    actors = list(self.plotter.actors.keys())
                    print(f"🎭 Actors in scene: {actors}")
                else:
                    print("⚠️ No actors attribute")
            except Exception as e:
                print(f"❌ Error checking actors: {e}")
            
            # Check camera
            try:
                if hasattr(self.plotter, 'camera'):
                    cam_pos = self.plotter.camera_position
                    print(f"📹 Camera position: {cam_pos}")
                else:
                    print("⚠️ No camera attribute")
            except Exception as e:
                print(f"❌ Error checking camera: {e}")
            
            # Check bounds
            try:
                if hasattr(self.plotter, 'bounds'):
                    bounds = self.plotter.bounds
                    print(f"🌍 Scene bounds: {bounds}")
                else:
                    print("⚠️ No bounds attribute")
            except Exception as e:
                print(f"❌ Error checking bounds: {e}")
            
            # Check render window
            try:
                if hasattr(self.plotter, 'ren_win'):
                    print(f"🖼️ Render window: {self.plotter.ren_win}")
                else:
                    print("⚠️ No render window")
            except Exception as e:
                print(f"❌ Error checking render window: {e}")
            
            print("🔍 === DEBUG INFO END ===\n")
            
        except Exception as e:
            print(f"❌ Error in debug info: {e}")
    
    # ==========================================
    # ROOF CREATION METHODS
    # ==========================================
    
    def _create_gabled_roof(self, base_verts, height, roof_pitch):
        """Create gabled roof vertices and faces"""
        try:
            roof_vertices = []
            roof_faces = []
            n_points = len(base_verts)
            
            # Find the longest side for the ridge direction
            max_length = 0
            ridge_start_idx = 0
            
            for i in range(n_points):
                next_i = (i + 1) % n_points
                length = np.linalg.norm(np.array(base_verts[next_i][:2]) - np.array(base_verts[i][:2]))
                if length > max_length:
                    max_length = length
                    ridge_start_idx = i
                    
            ridge_end_idx = (ridge_start_idx + 1) % n_points
            
            # Calculate roof height from pitch
            building_width = max_length
            roof_height_add = (building_width / 2) * math.tan(math.radians(roof_pitch))
            total_height = height + roof_height_add
            
            # Create ridge line (midpoints of opposite sides)
            ridge_start = [
                (base_verts[ridge_start_idx][0] + base_verts[ridge_end_idx][0]) / 2,
                (base_verts[ridge_start_idx][1] + base_verts[ridge_end_idx][1]) / 2,
                total_height
            ]
            
            # Find opposite side midpoint
            opposite_idx = (ridge_start_idx + n_points // 2) % n_points
            opposite_next_idx = (opposite_idx + 1) % n_points
            
            ridge_end = [
                (base_verts[opposite_idx][0] + base_verts[opposite_next_idx][0]) / 2,
                (base_verts[opposite_idx][1] + base_verts[opposite_next_idx][1]) / 2,
                total_height
            ]
            
            roof_vertices = [ridge_start, ridge_end]
            ridge_start_idx_3d = 2 * n_points  # Index in all_vertices
            ridge_end_idx_3d = 2 * n_points + 1
            
            # Create triangular roof faces
            for i in range(n_points):
                next_i = (i + 1) % n_points
                
                # Determine which ridge point to use
                if i < n_points // 2:
                    ridge_idx = ridge_start_idx_3d
                else:
                    ridge_idx = ridge_end_idx_3d
                
                # Triangle from wall edge to ridge
                triangle = [3, i + n_points, next_i + n_points, ridge_idx]
                roof_faces.append(triangle)
            
            return roof_vertices, roof_faces
            
        except Exception as e:
            print(f"❌ Error creating gabled roof: {e}")
            return [], []
    
    def _create_hipped_roof(self, base_verts, height, roof_pitch):
        """Create hipped roof vertices and faces"""
        try:
            # Calculate center point
            center_x = np.mean([v[0] for v in base_verts])
            center_y = np.mean([v[1] for v in base_verts])
            
            # Calculate roof height
            max_distance = max([np.linalg.norm([v[0] - center_x, v[1] - center_y]) for v in base_verts])
            roof_height_add = max_distance * math.tan(math.radians(roof_pitch))
            total_height = height + roof_height_add
            
            # Single apex point
            apex = [center_x, center_y, total_height]
            roof_vertices = [apex]
            
            n_points = len(base_verts)
            apex_idx = 2 * n_points  # Index in all_vertices
            
            # Create triangular faces from each wall top edge to apex
            roof_faces = []
            for i in range(n_points):
                next_i = (i + 1) % n_points
                triangle = [3, i + n_points, next_i + n_points, apex_idx]
                roof_faces.append(triangle)
            
            return roof_vertices, roof_faces
            
        except Exception as e:
            print(f"❌ Error creating hipped roof: {e}")
            return [], []
    
    # ==========================================
    # SOLAR SIMULATION METHODS
    # ==========================================
    
    def update_solar_time(self, hour):
        """Update solar time for simulation"""
        try:
            self.solar_time = max(0, min(23, hour))  # Clamp to valid range
            print(f"☀️ Solar time updated: {self.solar_time}:00")
            
            # Calculate sun position
            azimuth, elevation = self._calculate_sun_position(self.solar_time, self.solar_day)
            self.sun_position_changed.emit(azimuth, elevation)
            
            # Update visualization if not in debug mode
            if not self.debug_mode:
                self._update_solar_visualization()
            
        except Exception as e:
            print(f"❌ Error updating solar time: {e}")

    def update_solar_day(self, day):
        """Update solar day for simulation"""
        try:
            self.solar_day = max(1, min(365, day))  # Clamp to valid range
            print(f"☀️ Solar day updated: {self.solar_day}")
            
            # Recalculate sun position with new day
            azimuth, elevation = self._calculate_sun_position(self.solar_time, self.solar_day)
            self.sun_position_changed.emit(azimuth, elevation)
            
            # Update visualization if not in debug mode
            if not self.debug_mode:
                self._update_solar_visualization()
            
        except Exception as e:
            print(f"❌ Error updating solar day: {e}")

    def _calculate_sun_position(self, hour, day_of_year):
        """Calculate sun position based on time and day"""
        try:
            # Solar declination angle (tilt of Earth)
            declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            
            # Hour angle (15 degrees per hour from solar noon)
            hour_angle = 15 * (hour - 12)
            
            # Convert to radians
            lat_rad = math.radians(self.latitude)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)
            
            # Solar elevation angle
            elevation = math.asin(
                math.sin(dec_rad) * math.sin(lat_rad) +
                math.cos(dec_rad) * math.cos(lat_rad) * math.cos(hour_rad)
            )
            elevation_deg = math.degrees(elevation)
            
            # Solar azimuth angle
            azimuth = math.atan2(
                math.sin(hour_rad),
                math.cos(hour_rad) * math.sin(lat_rad) - math.tan(dec_rad) * math.cos(lat_rad)
            )
            azimuth_deg = math.degrees(azimuth) + 180  # Convert to 0-360 range
            
            return azimuth_deg, max(0, elevation_deg)  # Ensure elevation is not negative
            
        except Exception as e:
            print(f"❌ Error calculating sun position: {e}")
            return 180, 45  # Default values

    def _update_solar_visualization(self):
        """Update solar visualization in 3D scene"""
        try:
            if not self.plotter or self.debug_mode:
                return
                
            # Calculate current sun position
            azimuth, elevation = self._calculate_sun_position(self.solar_time, self.solar_day)
            
            # Remove existing sun if any
            try:
                self.plotter.remove_actor('sun')
                self.plotter.remove_actor('sun_ray')
            except:
                pass
                
            # Add sun representation only if above horizon
            if elevation > 0:
                # Calculate sun position in 3D space
                distance = 20  # Distance from origin
                
                sun_x = distance * math.cos(math.radians(elevation)) * math.sin(math.radians(azimuth))
                sun_y = distance * math.cos(math.radians(elevation)) * math.cos(math.radians(azimuth))
                sun_z = distance * math.sin(math.radians(elevation))
                
                # Create sun sphere
                sun_sphere = pv.Sphere(radius=1.0, center=[sun_x, sun_y, sun_z])
                self.plotter.add_mesh(sun_sphere, name='sun', color='yellow', opacity=0.9)
                
                # Add sun ray to ground
                sun_ray_points = np.array([
                    [sun_x, sun_y, sun_z],
                    [0, 0, 0]
                ])
                sun_ray = pv.Line(sun_ray_points[0], sun_ray_points[1])
                self.plotter.add_mesh(sun_ray, name='sun_ray', color='orange', 
                                    line_width=3, opacity=0.6)
                
                # Force render after adding sun
                self._force_render_multiple()
                
        except Exception as e:
            print(f"⚠️ Could not update solar visualization: {e}")
    
    def start_sun_animation(self):
        """Start sun path animation"""
        try:
            if not self.animation_timer.isActive():
                self.animation_step_count = 0
                self.animation_timer.start(200)  # Update every 200ms
                print("🎬 Sun animation started")
        except Exception as e:
            print(f"❌ Error starting sun animation: {e}")
            
    def stop_sun_animation(self):
        """Stop sun path animation"""
        try:
            self.animation_timer.stop()
            print("⏹️ Sun animation stopped")
        except Exception as e:
            print(f"❌ Error stopping sun animation: {e}")
            
    def _animate_sun(self):
        """Animate sun position through the day"""
        try:
            # Cycle through hours of the day
            hour = (self.animation_step_count % 24)
            self.update_solar_time(hour)
            
            self.animation_step_count += 1
            self.animation_step.emit(hour)
            
            # Stop animation after one full day
            if self.animation_step_count >= 24:
                self.stop_sun_animation()
                
        except Exception as e:
            print(f"❌ Error in sun animation: {e}")
    
    # ==========================================
    # BUILDING UPDATE METHODS
    # ==========================================
    
    def update_building_height(self, height):
        """Update building height and regenerate"""
        try:
            if self.current_points and height != self.current_height:
                self.current_height = height
                self.create_building_from_canvas(
                    self.current_points, height, 
                    self.current_roof_type, self.current_roof_pitch
                )
                print(f"🏗️ Building height updated to {height}m")
        except Exception as e:
            print(f"❌ Error updating building height: {e}")
        
    def update_roof_type(self, roof_type):
        """Update roof type and regenerate"""
        try:
            if self.current_points and roof_type != self.current_roof_type:
                self.current_roof_type = roof_type
                self.create_building_from_canvas(
                    self.current_points, self.current_height, 
                    roof_type, self.current_roof_pitch
                )
                print(f"🏗️ Roof type updated to {roof_type}")
        except Exception as e:
            print(f"❌ Error updating roof type: {e}")
        
    def update_roof_pitch(self, pitch):
        """Update roof pitch and regenerate"""
        try:
            if self.current_points and pitch != self.current_roof_pitch:
                self.current_roof_pitch = pitch
                if self.current_roof_type != 'flat':  # Only update if not flat roof
                    self.create_building_from_canvas(
                        self.current_points, self.current_height, 
                        self.current_roof_type, pitch
                    )
                print(f"🏗️ Roof pitch updated to {pitch}°")
        except Exception as e:
            print(f"❌ Error updating roof pitch: {e}")
    
    # ==========================================
    # PUBLIC API METHODS
    # ==========================================
    
    def generate_from_points(self, points, **kwargs):
        """Generate building from points - public API method"""
        try:
            # Extract parameters with defaults
            height = kwargs.get('wall_height', 3.0)
            roof_type = kwargs.get('roof_type', 'Flat').lower()
            roof_pitch = kwargs.get('roof_pitch', 30.0)
            
            # Create building
            success = self.create_building_from_canvas(points, height, roof_type, roof_pitch)
            
            if success:
                return {'status': 'success', 'building': self.current_building}
            else:
                return {'status': 'failed', 'building': None}
                
        except Exception as e:
            print(f"❌ Error in generate_from_points: {e}")
            return {'status': 'error', 'building': None, 'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_sun_animation()
            self.clear_current_building()
            print("✅ Building generator cleanup completed")
        except Exception as e: 
            print(f"❌ Error during cleanup: {e}")