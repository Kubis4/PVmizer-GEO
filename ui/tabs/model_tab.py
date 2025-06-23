#!/usr/bin/env python3
"""
ENHANCED Model Tab - PyVista 3D Building Generator
FIXED: Polygon shape preservation + No false validation errors
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import math

# PyVista imports with fallback
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
    pv.set_plot_theme("document")
except ImportError:
    PYVISTA_AVAILABLE = False
    print("⚠️ PyVista not available - using fallback 3D viewer")

class ModelTab(QWidget):
    """ENHANCED Model Tab - Polygon Shape Preserving 3D Generator"""
    
    # Signals
    model_generated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    generation_progress = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 3D Components
        self.plotter = None
        self.vtk_widget = None
        self.current_building = None
        self.building_meshes = []
        
        # Building parameters
        self.default_settings = {
            'height': 3.0,
            'roof_type': 'flat',
            'roof_pitch': 30.0,
            'scale': 0.05,
            'wall_thickness': 0.2,
            'foundation_height': 0.3,
            'material_color': 'lightcoral',
            'roof_color': 'darkred'
        }
        
        # Generation state
        self.generation_in_progress = False
        self.last_generation_points = []
        self.debug_mode = True  # Enable debug output
        
        # 🔧 MINIMAL UI setup - ONLY plotter
        self.setup_minimal_ui()
        self.setup_3d_environment()
        
        print("✅ ENHANCED Model Tab - Polygon shape preserving generator")
    
    def setup_minimal_ui(self):
        """Setup MINIMAL UI - ONLY 3D view"""
        # Main layout - minimal margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Minimal margins
        layout.setSpacing(5)  # Minimal spacing
        
        # 3D View placeholder (will be replaced in setup_3d_environment)
        self.view_placeholder = QLabel("Initializing 3D View...")
        self.view_placeholder.setAlignment(Qt.AlignCenter)
        self.view_placeholder.setMinimumSize(800, 600)
        self.view_placeholder.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.view_placeholder)
    
    def setup_3d_environment(self):
        """Setup 3D visualization environment"""
        try:
            if not PYVISTA_AVAILABLE:
                self.setup_fallback_3d_view()
                return
            
            # Remove placeholder
            if self.view_placeholder:
                self.layout().removeWidget(self.view_placeholder)
                self.view_placeholder.deleteLater()
                self.view_placeholder = None
            
            # Create PyVista widget
            self.vtk_widget = QtInteractor(self)
            self.vtk_widget.setMinimumSize(800, 600)
            
            # Add to layout
            self.layout().addWidget(self.vtk_widget)
            
            # Setup plotter
            self.plotter = self.vtk_widget
            
            # Initialize 3D scene
            self.initialize_3d_scene()
            
            print("✅ 3D environment setup completed with PyVista")
            
        except Exception as e:
            print(f"❌ Error setting up 3D environment: {e}")
            self.setup_fallback_3d_view()
    
    def setup_fallback_3d_view(self):
        """Setup fallback 3D view when PyVista is not available"""
        if self.view_placeholder:
            self.view_placeholder.setText("""
🏗️ 3D Model Viewer

PyVista not available
Install with: pip install pyvista pyvistaqt

Generated 3D models will be described here.
            """)
            self.view_placeholder.setStyleSheet("""
                QLabel {
                    background-color: #fff3cd;
                    border: 2px dashed #856404;
                    border-radius: 10px;
                    color: #856404;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 20px;
                }
            """)
    
    def initialize_3d_scene(self):
        """Initialize 3D scene with ground, lighting, etc."""
        try:
            if not self.plotter:
                return
            
            # Clear any existing content
            self.plotter.clear()
            
            # Add ground plane
            ground = pv.Plane(center=(0, 0, -0.05), direction=(0, 0, 1), i_size=50, j_size=50)
            self.plotter.add_mesh(
                ground, 
                color='lightgray', 
                opacity=0.3, 
                name='ground',
                show_edges=False
            )
            
            # Add coordinate axes
            self.plotter.add_axes(
                xlabel='X (East)', 
                ylabel='Y (North)', 
                zlabel='Z (Up)',
                line_width=3,
                labels_off=False
            )
            
            # Set nice camera position
            self.plotter.camera_position = 'iso'
            self.plotter.camera.zoom(1.2)
            
            # Add some ambient lighting
            self.plotter.enable_shadows()
            
            # Set background
            self.plotter.background_color = 'aliceblue'
            
            print("✅ 3D scene initialized")
            
        except Exception as e:
            print(f"❌ Error initializing 3D scene: {e}")
    
    def generate_building_from_canvas(self):
        """Generate building from current canvas drawing - FIXED VALIDATION"""
        if self.generation_in_progress:
            print("⚠️ Generation already in progress")
            return False
        
        try:
            self.generation_in_progress = True
            
            print("🔍 Starting building generation...")
            
            # Get main window
            main_window = self.find_main_window()
            if not main_window:
                print("❌ Cannot find main window")
                return False
            
            # Get canvas points with BETTER validation
            print("🔄 Getting canvas points...")
            points = self.get_canvas_points(main_window)
            
            # 🔧 IMPROVED: More detailed point validation
            if not points:
                print("❌ No drawing found. Please draw a polygon on the canvas first.")
                return False
            
            print(f"🔍 Found {len(points)} raw points")
            
            # 🔧 FIXED: Only show error if we actually don't have enough points
            if len(points) < 3:
                print(f"❌ Insufficient points: Found {len(points)}, need at least 3")
                return False
            
            print(f"✅ Valid point count: {len(points)} points")
            
            # 🔧 DEBUG: Show polygon shape
            if self.debug_mode:
                self.debug_polygon_shape(points)
            
            # Get building parameters
            print("🔄 Getting building settings...")
            settings = self.get_building_settings(main_window)
            
            print(f"🏗️ Generating building from {len(points)} canvas points")
            print(f"   Settings: {settings}")
            
            # Store points for regeneration
            self.last_generation_points = points.copy()
            
            # Generate building
            print("🔄 Creating 3D building...")
            success = self.create_3d_building(points, settings)
            
            if success:
                print("✅ Building generated successfully!")
                self.model_generated.emit(f"Building with {len(points)} vertices")
                return True
            else:
                print("❌ Failed to generate building geometry")
                return False
                
        except Exception as e:
            error_msg = f"Error generating building: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.generation_in_progress = False
    
    def debug_polygon_shape(self, points):
        """Debug polygon shape to understand the issue"""
        try:
            print("🔍 === POLYGON SHAPE DEBUG ===")
            print(f"📊 Total points: {len(points)}")
            
            for i, point in enumerate(points):
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    print(f"  Point {i}: QPointF({point.x():.2f}, {point.y():.2f})")
                elif isinstance(point, (tuple, list)):
                    print(f"  Point {i}: {type(point)}({point[0]:.2f}, {point[1]:.2f})")
                else:
                    print(f"  Point {i}: {type(point)} - {point}")
            
            # Calculate polygon properties
            if len(points) >= 3:
                # Calculate center
                if hasattr(points[0], 'x'):
                    center_x = sum(p.x() for p in points) / len(points)
                    center_y = sum(p.y() for p in points) / len(points)
                else:
                    center_x = sum(p[0] for p in points) / len(points)
                    center_y = sum(p[1] for p in points) / len(points)
                
                print(f"📍 Polygon center: ({center_x:.2f}, {center_y:.2f})")
                
                # Calculate approximate area
                area = self._calculate_polygon_area(points)
                print(f"📐 Polygon area: {area:.2f}")
                
                # Check polygon type
                if len(points) == 3:
                    print("🔺 Shape: Triangle")
                elif len(points) == 4:
                    print("🔶 Shape: Quadrilateral (should create 4-sided building)")
                elif len(points) == 5:
                    print("⬟ Shape: Pentagon")
                elif len(points) == 6:
                    print("⬡ Shape: Hexagon")
                else:
                    print(f"⬢ Shape: {len(points)}-gon")
            
            print("🔍 === POLYGON SHAPE DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Debug polygon shape failed: {e}")
    
    def _calculate_polygon_area(self, points):
        """Calculate polygon area using shoelace formula"""
        try:
            if len(points) < 3:
                return 0.0
            
            area = 0.0
            n = len(points)
            
            for i in range(n):
                j = (i + 1) % n
                
                if hasattr(points[i], 'x'):
                    x1, y1 = points[i].x(), points[i].y()
                    x2, y2 = points[j].x(), points[j].y()
                else:
                    x1, y1 = points[i][0], points[i][1]
                    x2, y2 = points[j][0], points[j][1]
                
                area += (x1 * y2 - x2 * y1)
            
            return abs(area) / 2.0
            
        except Exception as e:
            print(f"❌ Area calculation failed: {e}")
            return 0.0
    
    def find_main_window(self):
        """Find the main window"""
        widget = self
        attempts = 0
        while widget and attempts < 10:
            if hasattr(widget, 'content_tabs') or hasattr(widget, 'canvas_manager'):
                return widget
            widget = widget.parent()
            attempts += 1
        return None
    
    def get_canvas_points(self, main_window):
        """Get drawing points from canvas with IMPROVED validation"""
        try:
            print("🔍 Searching for canvas points...")
            
            # Method 1: Direct canvas access from drawing tab
            if hasattr(main_window, 'content_tabs'):
                print("   Method 1: Checking content_tabs...")
                drawing_tab = main_window.content_tabs.widget(1)  # Drawing tab
                if drawing_tab:
                    print(f"   Found drawing tab: {type(drawing_tab)}")
                    
                    # Try different canvas access methods
                    canvas = None
                    if hasattr(drawing_tab, 'canvas'):
                        canvas = drawing_tab.canvas
                        print("   Found canvas via .canvas")
                    elif hasattr(drawing_tab, 'drawing_canvas'):
                        canvas = drawing_tab.drawing_canvas
                        print("   Found canvas via .drawing_canvas")
                    elif hasattr(drawing_tab, 'canvas_widget'):
                        canvas = drawing_tab.canvas_widget
                        print("   Found canvas via .canvas_widget")
                    
                    if canvas and hasattr(canvas, 'points'):
                        raw_points = canvas.points
                        print(f"   Canvas has {len(raw_points) if raw_points else 0} raw points")
                        
                        if raw_points and len(raw_points) > 0:
                            converted = self.convert_points_to_world_coords(raw_points)
                            if converted and len(converted) >= 3:
                                print(f"✅ Method 1 success: {len(converted)} points")
                                return converted
                            else:
                                print(f"⚠️ Method 1: Conversion failed or insufficient points")
            
            # Method 2: Canvas manager
            if hasattr(main_window, 'canvas_manager'):
                print("   Method 2: Checking canvas_manager...")
                try:
                    points = main_window.canvas_manager.get_drawing_points()
                    if points and len(points) > 0:
                        print(f"   Canvas manager has {len(points)} points")
                        converted = self.convert_points_to_world_coords(points)
                        if converted and len(converted) >= 3:
                            print(f"✅ Method 2 success: {len(converted)} points")
                            return converted
                        else:
                            print(f"⚠️ Method 2: Conversion failed or insufficient points")
                except Exception as e:
                    print(f"   Method 2 failed: {e}")
            
            # Method 3: Widget tree search
            if hasattr(main_window, 'content_tabs'):
                print("   Method 3: Searching widget tree...")
                drawing_tab = main_window.content_tabs.widget(1)
                if drawing_tab:
                    canvas = self.find_canvas_in_widget(drawing_tab)
                    if canvas and hasattr(canvas, 'points'):
                        raw_points = canvas.points
                        print(f"   Widget tree canvas has {len(raw_points) if raw_points else 0} points")
                        
                        if raw_points and len(raw_points) > 0:
                            converted = self.convert_points_to_world_coords(raw_points)
                            if converted and len(converted) >= 3:
                                print(f"✅ Method 3 success: {len(converted)} points")
                                return converted
                            else:
                                print(f"⚠️ Method 3: Conversion failed or insufficient points")
            
            print("❌ No valid canvas points found through any method")
            return []
            
        except Exception as e:
            print(f"❌ Error getting canvas points: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def find_canvas_in_widget(self, widget):
        """Recursively find canvas in widget tree"""
        try:
            # Check if this widget is a canvas
            if hasattr(widget, 'points') and hasattr(widget, 'is_complete'):
                return widget
            
            # Check children
            for child in widget.findChildren(QWidget):
                if hasattr(child, 'points') and hasattr(child, 'is_complete'):
                    return child
            
            return None
        except:
            return None
    
    def convert_points_to_world_coords(self, canvas_points):
        """Convert canvas points to world coordinates with BETTER validation"""
        try:
            if not canvas_points:
                print("⚠️ No canvas points to convert")
                return []
            
            print(f"🔄 Converting {len(canvas_points)} canvas points...")
            world_points = []
            
            for i, point in enumerate(canvas_points):
                try:
                    if hasattr(point, 'x') and hasattr(point, 'y'):
                        # QPointF object
                        x = float(point.x())
                        y = float(point.y())
                    elif isinstance(point, (list, tuple)) and len(point) >= 2:
                        # Tuple/list
                        x = float(point[0])
                        y = float(point[1])
                    else:
                        print(f"⚠️ Skipping unknown point format at index {i}: {type(point)}")
                        continue
                    
                    world_points.append((x, y))
                    
                except (ValueError, AttributeError) as e:
                    print(f"⚠️ Error converting point {i}: {e}")
                    continue
            
            print(f"✅ Successfully converted {len(world_points)}/{len(canvas_points)} points")
            
            # 🔧 ADDED: Validate converted points
            if len(world_points) < 3:
                print(f"⚠️ Insufficient converted points: {len(world_points)} < 3")
                return []
            
            return world_points
            
        except Exception as e:
            print(f"❌ Error converting points: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_building_settings(self, main_window):
        """Get building settings from UI"""
        settings = self.default_settings.copy()
        
        try:
            # Try to get from left panel
            if hasattr(main_window, 'left_panel'):
                panel = main_window.left_panel
                
                # Try different methods
                if hasattr(panel, 'get_building_parameters'):
                    params = panel.get_building_parameters()
                    settings.update(params)
                elif hasattr(panel, 'get_building_settings'):
                    params = panel.get_building_settings()
                    settings.update(params)
                
                # Try to get scale from drawing tab
                if hasattr(panel, 'drawing_tab'):
                    if hasattr(panel.drawing_tab, 'get_scale_factor'):
                        settings['scale'] = panel.drawing_tab.get_scale_factor()
            
            # Try to get scale from canvas
            if hasattr(main_window, 'canvas_manager'):
                if hasattr(main_window.canvas_manager, 'scale_factor'):
                    settings['scale'] = main_window.canvas_manager.scale_factor
            
        except Exception as e:
            print(f"⚠️ Using default settings due to error: {e}")
        
        return settings
    
    def create_3d_building(self, points, settings):
        """Create complete 3D building from 2D points - SHAPE PRESERVING"""
        try:
            # 🔧 ADDED: Early validation with detailed logging
            if not points:
                print("❌ No points provided to create_3d_building")
                return False
            
            if len(points) < 3:
                print(f"❌ Insufficient points in create_3d_building: {len(points)} < 3")
                return False
            
            print(f"✅ Starting 3D building creation with {len(points)} valid points")
            
            if not PYVISTA_AVAILABLE:
                print("ℹ️ PyVista not available, using fallback description")
                return self.create_fallback_building_description(points, settings)
            
            if not self.plotter:
                print("❌ No plotter available")
                return False
            
            # 🔧 FIXED: Ensure points are in proper format and order
            fixed_points = self._fix_polygon_points(points)
            if len(fixed_points) < 3:
                print("❌ Point fixing failed")
                return False
            
            # Convert to 3D coordinates
            print("🔄 Converting to 3D vertices...")
            vertices_3d = self.points_to_3d_vertices(fixed_points, settings['scale'])
            if len(vertices_3d) < 3:
                print(f"❌ Not enough valid 3D vertices: {len(vertices_3d)}")
                return False
            
            print(f"✅ Created {len(vertices_3d)} 3D vertices")
            
            # Generate building mesh - SHAPE PRESERVING
            print("🔄 Generating building mesh...")
            building_mesh = self.generate_building_mesh_shape_preserving(
                vertices_3d, 
                settings['height'],
                settings['roof_type'],
                settings.get('roof_pitch', 30),
                settings
            )
            
            if not building_mesh:
                print("❌ Failed to generate building mesh")
                return False
            
            print("✅ Building mesh generated successfully")
            
            # Clear previous building
            print("🔄 Clearing previous buildings...")
            self.clear_existing_buildings()
            
            # Add building to scene
            print("🔄 Adding building to 3D scene...")
            self.add_building_to_scene(building_mesh, settings)
            
            # Store current building
            self.current_building = building_mesh
            self.building_meshes.append(building_mesh)
            
            # Update camera view
            print("🔄 Updating camera view...")
            self.plotter.reset_camera()
            self.plotter.camera.zoom(0.8)
            
            print("✅ 3D building created and added to scene successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating 3D building: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _fix_polygon_points(self, points):
        """Fix polygon points to ensure correct shape"""
        try:
            if not points or len(points) < 3:
                return []
            
            # Convert all points to consistent format
            fixed_points = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    # QPointF object
                    fixed_points.append((float(point.x()), float(point.y())))
                elif isinstance(point, (list, tuple)) and len(point) >= 2:
                    # Tuple/list format
                    fixed_points.append((float(point[0]), float(point[1])))
                else:
                    print(f"⚠️ Skipping invalid point: {point}")
                    continue
            
            if len(fixed_points) < 3:
                return []
            
            # Remove duplicate points
            unique_points = []
            tolerance = 1e-6
            
            for point in fixed_points:
                is_duplicate = False
                for existing in unique_points:
                    if (abs(point[0] - existing[0]) < tolerance and 
                        abs(point[1] - existing[1]) < tolerance):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_points.append(point)
            
            if len(unique_points) < 3:
                print("❌ Not enough unique points after cleanup")
                return []
            
            # Ensure counter-clockwise order for correct face orientation
            ordered_points = self._ensure_counter_clockwise(unique_points)
            
            print(f"🔧 Polygon processing:")
            print(f"   Original: {len(points)} points")
            print(f"   Fixed: {len(fixed_points)} points")
            print(f"   Unique: {len(unique_points)} points")
            print(f"   Final: {len(ordered_points)} points")
            
            return ordered_points
            
        except Exception as e:
            print(f"❌ Error fixing polygon points: {e}")
            return []
    
    def _ensure_counter_clockwise(self, points):
        """Ensure points are in counter-clockwise order"""
        try:
            if len(points) < 3:
                return points
            
            # Calculate signed area using shoelace formula
            signed_area = 0.0
            n = len(points)
            
            for i in range(n):
                j = (i + 1) % n
                signed_area += (points[j][0] - points[i][0]) * (points[j][1] + points[i][1])
            
            # If positive, points are clockwise - reverse them
            if signed_area > 0:
                print("🔄 Converting clockwise to counter-clockwise")
                return list(reversed(points))
            else:
                print("✅ Points already counter-clockwise")
                return points
                
        except Exception as e:
            print(f"❌ Error checking point order: {e}")
            return points
    
    def points_to_3d_vertices(self, points_2d, scale):
        """Convert 2D points to 3D vertices with proper scaling"""
        try:
            vertices = []
            
            # Calculate centroid for centering
            if points_2d:
                center_x = sum(p[0] for p in points_2d) / len(points_2d)
                center_y = sum(p[1] for p in points_2d) / len(points_2d)
            else:
                center_x = center_y = 0
            
            # Convert each point
            for i, (x, y) in enumerate(points_2d):
                # Center around origin and apply scale
                world_x = (x - center_x) * scale
                world_y = (center_y - y) * scale  # Flip Y for 3D coordinate system
                world_z = 0.0  # Ground level
                
                vertices.append([world_x, world_y, world_z])
                
                if self.debug_mode:
                    print(f"  Vertex {i+1}: ({x:.1f}, {y:.1f}) → ({world_x:.3f}, {world_y:.3f}, {world_z:.3f})")
            
            return np.array(vertices)
            
        except Exception as e:
            print(f"❌ Error converting to 3D vertices: {e}")
            return np.array([])
    
    
    def generate_building_mesh_shape_preserving(self, vertices_3d, height, roof_type, roof_pitch, settings):
        """Generate building mesh - FIX TOP FACE ORDERING"""
        try:
            print(f"🏗️ Generating mesh preserving {len(vertices_3d)} point polygon shape")
            
            if len(vertices_3d) < 3:
                print("❌ Need at least 3 vertices")
                return None
            
            # Create base vertices (z=0)
            base_vertices = vertices_3d.copy()
            base_vertices[:, 2] = 0
            
            # Create top vertices (z=height)
            top_vertices = base_vertices.copy()
            top_vertices[:, 2] = height
            
            # Combine all vertices
            all_vertices = np.vstack([base_vertices, top_vertices])
            n_points = len(vertices_3d)
            
            print(f"✅ Created {len(all_vertices)} vertices for {n_points}-sided building")
            
            # ==========================================
            # 🔧 CREATE FACES WITH FIXED TOP FACE
            # ==========================================
            
            faces = []
            
            # 🔧 BOTTOM FACE - Keep simple (normal order)
            print("🔧 Creating bottom face...")
            bottom_indices = list(range(n_points))
            bottom_face = [n_points] + bottom_indices
            faces.extend(bottom_face)
            print(f"✅ Bottom face: {n_points}-sided polygon")
            
            # 🔧 TOP FACE - FIXED: Reverse the vertex order for correct normal
            print("🔧 Creating TOP face with FIXED ordering...")
            
            # Create top face indices in REVERSE order for correct upward normal
            top_indices = list(range(n_points, 2 * n_points))
            top_indices.reverse()  # 🔧 KEY FIX: Reverse top face vertices
            
            top_face = [n_points] + top_indices
            faces.extend(top_face)
            print(f"✅ TOP face: {n_points}-sided polygon (REVERSED for correct normal)")
            
            # 🔧 SIDE FACES - Keep original
            print("🔧 Creating side walls...")
            for i in range(n_points):
                next_i = (i + 1) % n_points
                wall_face = [4, i, next_i, next_i + n_points, i + n_points]
                faces.extend(wall_face)
            
            print(f"✅ Created {n_points} side walls")
            
            # Create PyVista mesh
            mesh = pv.PolyData(all_vertices, faces)
            
            if mesh.n_points == 0 or mesh.n_cells == 0:
                print("❌ Generated mesh has no points/cells")
                return None
            
            print(f"✅ Mesh created with FIXED top face:")
            print(f"   Vertices: {mesh.n_points}")
            print(f"   Cells: {mesh.n_cells}")
            
            return mesh
            
        except Exception as e:
            print(f"❌ Error generating mesh: {e}")
            return None
        
    def generate_building_mesh(self, base_vertices, height, roof_type, roof_pitch, settings):
        """Generate complete building mesh with walls and roof"""
        # Use the shape-preserving method
        return self.generate_building_mesh_shape_preserving(base_vertices, height, roof_type, roof_pitch, settings)
    
    def create_roof_mesh(self, base_vertices, base_height, roof_type, roof_pitch):
        """Create roof mesh based on type"""
        try:
            roof_type_lower = roof_type.lower()
            
            if 'flat' in roof_type_lower:
                return None  # No additional roof mesh needed
            elif 'gable' in roof_type_lower or 'pitched' in roof_type_lower:
                return self.create_gable_roof_mesh(base_vertices, base_height, roof_pitch)
            elif 'hip' in roof_type_lower:
                return self.create_hip_roof_mesh(base_vertices, base_height, roof_pitch)
            elif 'pyramid' in roof_type_lower:
                return self.create_pyramid_roof_mesh(base_vertices, base_height, roof_pitch)
            else:
                print(f"⚠️ Unknown roof type: {roof_type}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating roof mesh: {e}")
            return None
    
    def create_gable_roof_mesh(self, base_vertices, base_height, roof_pitch):
        """Create gable roof mesh"""
        try:
            # Find longest edge for ridge direction
            n_points = len(base_vertices)
            max_length = 0
            ridge_edge = (0, 1)
            
            for i in range(n_points):
                next_i = (i + 1) % n_points
                length = np.linalg.norm(base_vertices[next_i] - base_vertices[i])
                if length > max_length:
                    max_length = length
                    ridge_edge = (i, next_i)
            
            # Create ridge line
            ridge_start = base_vertices[ridge_edge[0]]
            ridge_end = base_vertices[ridge_edge[1]]
            ridge_center = (ridge_start + ridge_end) / 2
            
            # Calculate roof height
            building_width = max_length * 0.4  # Approximate building width
            roof_height = building_width * np.tan(np.radians(roof_pitch))
            
            # Ridge vertices
            ridge_start_top = ridge_start.copy()
            ridge_start_top[2] = base_height + roof_height
            ridge_end_top = ridge_end.copy()
            ridge_end_top[2] = base_height + roof_height
            
            # Create roof vertices
            roof_vertices = np.vstack([base_vertices, ridge_start_top, ridge_end_top])
            
            # Create roof faces
            faces = []
            ridge_start_idx = len(base_vertices)
            ridge_end_idx = len(base_vertices) + 1
            
            # Create triangular roof faces
            for i in range(n_points):
                next_i = (i + 1) % n_points
                
                # Determine which ridge point to use
                if i <= n_points // 2:
                    ridge_idx = ridge_start_idx
                else:
                    ridge_idx = ridge_end_idx
                
                # Triangle face
                face = [3, i, next_i, ridge_idx]
                faces.extend(face)
            
            return pv.PolyData(roof_vertices, faces)
            
        except Exception as e:
            print(f"❌ Error creating gable roof: {e}")
            return None
    
    def create_pyramid_roof_mesh(self, base_vertices, base_height, roof_pitch):
        """Create pyramid roof with apex at center"""
        try:
            # Calculate centroid
            centroid = np.mean(base_vertices, axis=0)
            
            # Calculate roof height
            avg_radius = np.mean([np.linalg.norm(v - centroid) for v in base_vertices])
            roof_height = avg_radius * np.tan(np.radians(roof_pitch))
            
            # Create apex
            apex = centroid.copy()
            apex[2] = base_height + roof_height
            
            # Roof vertices
            roof_vertices = np.vstack([base_vertices, apex])
            apex_idx = len(base_vertices)
            
            # Create triangular faces
            faces = []
            n_points = len(base_vertices)
            
            for i in range(n_points):
                next_i = (i + 1) % n_points
                face = [3, i, next_i, apex_idx]
                faces.extend(face)
            
            return pv.PolyData(roof_vertices, faces)
            
        except Exception as e:
            print(f"❌ Error creating pyramid roof: {e}")
            return None
    
    def create_hip_roof_mesh(self, base_vertices, base_height, roof_pitch):
        """Create hip roof (simplified as pyramid for now)"""
        return self.create_pyramid_roof_mesh(base_vertices, base_height, roof_pitch)
    
    def clear_existing_buildings(self):
        """Clear existing buildings from scene"""
        try:
            if self.plotter:
                # Remove building meshes
                for i, mesh in enumerate(self.building_meshes):
                    try:
                        self.plotter.remove_actor(f'building_{i}')
                    except:
                        pass
                
                # Clear generic building actor
                try:
                    self.plotter.remove_actor('building')
                except:
                    pass
            
            self.building_meshes.clear()
            self.current_building = None
            
        except Exception as e:
            print(f"⚠️ Error clearing buildings: {e}")
    
    def add_building_to_scene(self, building_mesh, settings):
        """Add building mesh to 3D scene"""
        try:
            if not self.plotter:
                return
            
            # Add main building
            self.plotter.add_mesh(
                building_mesh,
                name='building',
                color=settings.get('material_color', 'lightcoral'),
                show_edges=True,
                edge_color='darkred',
                line_width=1,
                opacity=0.9
            )
            
            print("✅ Building added to 3D scene")
            
        except Exception as e:
            print(f"❌ Error adding building to scene: {e}")
    
    def create_fallback_building_description(self, points, settings):
        """Create text description when PyVista not available"""
        try:
            # Calculate some basic properties
            n_points = len(points)
            
            # Calculate area (simple polygon area)
            area = 0
            for i in range(n_points):
                j = (i + 1) % n_points
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            area = abs(area) / 2 * (settings['scale'] ** 2)
            
            # Calculate perimeter
            perimeter = 0
            for i in range(n_points):
                j = (i + 1) % n_points
                dx = points[j][0] - points[i][0]
                dy = points[j][1] - points[i][1]
                perimeter += math.sqrt(dx*dx + dy*dy) * settings['scale']
            
            # Volume
            volume = area * settings['height']
            
            description = f"""
🏗️ 3D BUILDING GENERATED
📐 Vertices: {n_points}
📏 Floor Area: {area:.2f} m²
📏 Perimeter: {perimeter:.2f} m
📏 Height: {settings['height']:.2f} m
📊 Volume: {volume:.2f} m³
🏠 Roof Type: {settings['roof_type']}
📏 Scale: {settings['scale']:.3f} m/pixel

SHAPE PRESERVED: {n_points}-sided polygon

To view the 3D model, install PyVista:
pip install pyvista pyvistaqt
            """
            
            if self.view_placeholder:
                self.view_placeholder.setText(description)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating fallback description: {e}")
            return False
    
    def regenerate_building(self):
        """Regenerate building with last points"""
        if self.last_generation_points:
            main_window = self.find_main_window()
            if main_window:
                settings = self.get_building_settings(main_window)
                self.create_3d_building(self.last_generation_points, settings)
    
    def clear_model(self):
        """Clear all 3D models"""
        try:
            self.clear_existing_buildings()
            
            if PYVISTA_AVAILABLE and self.plotter:
                self.initialize_3d_scene()
            
            print("✅ All models cleared")
            
        except Exception as e:
            print(f"❌ Error clearing models: {e}")
    
    def export_model(self):
        """Export current 3D model"""
        try:
            if not self.current_building:
                print("❌ No model to export")
                return
            
            if not PYVISTA_AVAILABLE:
                print("❌ PyVista required for model export")
                return
            
            # File dialog
            filename, file_type = QFileDialog.getSaveFileName(
                self,
                "Export 3D Building Model",
                f"building_model.stl",
                "STL Files (*.stl);;OBJ Files (*.obj);;PLY Files (*.ply);;VTK Files (*.vtk)"
            )
            
            if filename:
                self.current_building.save(filename)
                print(f"✅ Model exported to {filename}")
            
        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            print(f"❌ {error_msg}")
    
    # 🔧 ADDED: Legacy compatibility with better validation
    def create_building(self, points, height=None, roof_type=None, roof_pitch=None, scale=None, source="legacy", emit_signal=True):
        """Legacy method for compatibility - IMPROVED validation"""
        try:
            print(f"🔄 Legacy create_building called from {source}")
            
            # 🔧 BETTER: Validate points early
            if not points:
                print("❌ Legacy create_building: No points provided")
                return False
            
            if len(points) < 3:
                print(f"❌ Legacy create_building: Insufficient points {len(points)} < 3")
                return False
            
            print(f"✅ Legacy create_building: {len(points)} points received")
            
            settings = self.default_settings.copy()
            if height is not None:
                settings['height'] = height
            if roof_type is not None:
                settings['roof_type'] = roof_type
            if roof_pitch is not None:
                settings['roof_pitch'] = roof_pitch
            if scale is not None:
                settings['scale'] = scale
            
            # Convert points if needed
            if points and hasattr(points[0], 'x'):
                print("🔄 Converting QPointF objects...")
                points = self.convert_points_to_world_coords(points)
                if not points or len(points) < 3:
                    print("❌ Point conversion failed in legacy method")
                    return False
            
            print(f"🔄 Creating building with settings: {settings}")
            success = self.create_3d_building(points, settings)
            
            if success and emit_signal:
                self.model_generated.emit(f"Building from {source}")
                print(f"✅ Legacy create_building succeeded from {source}")
            else:
                print(f"❌ Legacy create_building failed from {source}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error in legacy create_building: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if PYVISTA_AVAILABLE and self.plotter:
                self.plotter.close()
            self.building_meshes.clear()
            self.current_building = None
            print("✅ Model Tab cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    def refresh_view(self):
        """Refresh the 3D view - for compatibility"""
        try:
            if PYVISTA_AVAILABLE and self.plotter:
                self.plotter.render()
                print("✅ 3D view refreshed")
        except Exception as e:
            print(f"⚠️ Error refreshing view: {e}")