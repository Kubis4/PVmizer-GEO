#!/usr/bin/env python3
"""
Enhanced Drawing Canvas - Improved 3D Model Integration
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPointF
from PyQt5.QtGui import QColor
import math
from drawing_view.drawing_area import EnhancedDrawingArea

class DrawingCanvas(QWidget):
    """Enhanced drawing canvas with improved 3D model integration"""
    
    # Signals
    polygon_completed = pyqtSignal(list)
    drawing_cleared = pyqtSignal()
    generate_3d_model = pyqtSignal(list)
    model_generation_requested = pyqtSignal(list, dict)  # points, settings
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Drawing state
        self.points = []
        self.is_drawing = False
        self.is_complete = False
        self.background_pixmap = None
        self.current_mouse_pos = None
        self.original_mouse_pos = None
        
        # Point movement state
        self.dragging_point = None
        self.drag_offset = QPoint(0, 0)
        
        # Scale factor (controlled by left panel)
        self.scale_factor = 0.05  # meters per pixel
        
        # Right angle settings
        self.angle_snap_enabled = True
        self.angle_tolerance = 15  # degrees
        self.right_angle_size = 15  # pixels for the square indicator
        
        # Zoom and pan
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.is_panning = False
        self.last_pan_point = QPoint(0, 0)
        
        # 3D Generation settings
        self.auto_generate_3d = False  # Can be controlled by UI
        self.last_3d_generation_successful = False
        
        # VISUAL SETTINGS
        self.point_color = QColor(0, 220, 0)
        self.preview_line_color = QColor(150, 150, 150)
        self.completed_line_color = QColor(0, 100, 200)
        self.polygon_fill = QColor(100, 150, 255, 40)
        self.right_angle_color = QColor(255, 100, 100)
        self.snap_line_color = QColor(255, 200, 0)
        self.number_bg_color = QColor(55, 55, 55)
        self.number_text_color = QColor(255, 255, 255)
        self.text_bg_color = QColor(100, 100, 100)
        self.text_color = QColor(255, 255, 255)
        
        self.point_radius = 9
        self.line_width = 4
        self.snap_distance = 15
        
        # Setup UI
        self._setup_ui()
        self.setMouseTracking(True)
        
        print("✅ Enhanced Drawing Canvas - Improved 3D Integration!")
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
                
        # Main drawing area
        self.drawing_area = EnhancedDrawingArea(self)
        layout.addWidget(self.drawing_area)
        
        # Status bar
        status = self._create_status()
        layout.addWidget(status)
    
    def _create_status(self):
        """Create status bar"""
        status = QFrame()
        status.setFixedHeight(22)
        status.setStyleSheet("""
            QFrame { background-color: #2c3e50; border-radius: 3px; }
            QLabel { color: white; padding: 2px 5px; font-size: 10px; }
        """)
        
        layout = QHBoxLayout(status)
        layout.setContentsMargins(5, 0, 5, 0)
        
        self.status_label = QLabel("Click to add first point")
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        self.info_label = QLabel("Points: 0")
        layout.addWidget(self.info_label)
        
        return status
    
    # ===== PUBLIC METHODS FOR CONTROL =====
    
    def set_scale(self, scale):
        """Set scale factor"""
        self.scale_factor = scale
        self.update()
        print(f"✓ Scale set to {scale}m/pixel")
    
    def set_angle_snap(self, enabled):
        """Set angle snap"""
        self.angle_snap_enabled = enabled
        self._update_status()
        self.update()
        print(f"✓ Angle snap {'enabled' if enabled else 'disabled'}")
    
    def clear_all(self):
        """Clear all drawing"""
        self.points.clear()
        self.is_drawing = False
        self.is_complete = False
        self.current_mouse_pos = None
        self.original_mouse_pos = None
        self.dragging_point = None
        self.last_3d_generation_successful = False
        self._update_status()
        self.update()
        self.drawing_cleared.emit()
        print("✓ Drawing cleared")
    
    def undo_point(self):
        """Remove last point"""
        if self.points:
            self.points.pop()
            if not self.points:
                self.is_drawing = False
                self.is_complete = False
            self.dragging_point = None
            self._update_status()
            self.update()
            print(f"✓ Point removed, {len(self.points)} points remaining")
    
    def force_right_angle_at_point(self, point_index):
        """Force right angle at specified point"""
        if not self.is_complete or len(self.points) < 3:
            return False
        
        n = len(self.points)
        if point_index < 0 or point_index >= n:
            return False
        
        # Get the three points involved
        prev_idx = (point_index - 1) % n
        curr_idx = point_index
        next_idx = (point_index + 1) % n
        
        prev_point = self.points[prev_idx]
        curr_point = self.points[curr_idx]
        next_point = self.points[next_idx]
        
        # Calculate vectors
        v1 = QPointF(prev_point.x() - curr_point.x(), prev_point.y() - curr_point.y())
        v2 = QPointF(next_point.x() - curr_point.x(), next_point.y() - curr_point.y())
        
        # Check current angle
        current_angle = self.calculate_angle_between_vectors(v1, v2)
        
        if abs(current_angle - 90) > 5:  # Only adjust if not already close to 90°
            # Calculate perpendicular direction to v1
            if abs(v1.x()) < 0.001:  # Nearly vertical
                new_next = QPointF(curr_point.x() + (1 if v2.x() > 0 else -1) * abs(v2.y()), curr_point.y())
            elif abs(v1.y()) < 0.001:  # Nearly horizontal
                new_next = QPointF(curr_point.x(), curr_point.y() + (1 if v2.y() > 0 else -1) * abs(v2.x()))
            else:
                # General case - create perpendicular
                perp_x = -v1.y()
                perp_y = v1.x()
                
                # Normalize and scale to original distance
                perp_mag = math.sqrt(perp_x ** 2 + perp_y ** 2)
                if perp_mag > 0:
                    perp_x /= perp_mag
                    perp_y /= perp_mag
                
                dist = math.sqrt(v2.x() ** 2 + v2.y() ** 2)
                
                # Choose direction closest to original next point
                option1 = QPointF(curr_point.x() + perp_x * dist, curr_point.y() + perp_y * dist)
                option2 = QPointF(curr_point.x() - perp_x * dist, curr_point.y() - perp_y * dist)
                
                dist1 = (next_point.x() - option1.x()) ** 2 + (next_point.y() - option1.y()) ** 2
                dist2 = (next_point.x() - option2.x()) ** 2 + (next_point.y() - option2.y()) ** 2
                
                new_next = option1 if dist1 < dist2 else option2
            
            # Update the next point
            self.points[next_idx] = new_next
            self.update()
            print(f"✓ Forced right angle at point {point_index + 1}")
            return True
        
        return False
    
    # ===== BACKGROUND IMAGE METHODS =====
    
    def set_background_image(self, pixmap):
        """Set background image"""
        self.background_pixmap = pixmap
        self.drawing_area.set_background(pixmap)
        self.zoom_fit()
        print("✓ Background image set")
        return True
    
    def clear_background(self):
        """Clear background image"""
        self.background_pixmap = None
        self.drawing_area.clear_background()
        self.update()
        print("✓ Background image cleared")
    
    def zoom_fit(self):
        """Fit view to background image"""
        if self.background_pixmap:
            widget_size = self.drawing_area.size()
            image_size = self.background_pixmap.size()
            
            scale_x = widget_size.width() / image_size.width()
            scale_y = widget_size.height() / image_size.height()
            self.zoom_factor = min(scale_x, scale_y) * 0.9
            
            center_x = int((widget_size.width() - image_size.width() * self.zoom_factor) / 2)
            center_y = int((widget_size.height() - image_size.height() * self.zoom_factor) / 2)
            self.pan_offset = QPoint(center_x, center_y)
            
            self.update()
            print("✓ View fitted to background")
    
    # ===== STATUS UPDATES =====
    
    def _update_status(self):
        """Update status text"""
        count = len(self.points)
        self.info_label.setText(f"Points: {count}")
        
        if self.dragging_point is not None:
            self.status_label.setText(f"Dragging point {self.dragging_point + 1} - Right-click to force 90° angle")
        elif count == 0:
            self.status_label.setText("Click to add first point")
        elif count == 1:
            self.status_label.setText("Click to add second point")
        elif count == 2:
            self.status_label.setText("Click to add third point - DOUBLE-CLICK to complete")
        elif not self.is_complete:
            snap_text = " | 90° snap ON" if self.angle_snap_enabled else ""
            self.status_label.setText(f"Click for more points - DOUBLE-CLICK to complete{snap_text}")
        else:
            if self.last_3d_generation_successful:
                self.status_label.setText("✅ Polygon complete! 3D model ready. Drag points to adjust.")
            else:
                self.status_label.setText("Polygon complete! Click 'Generate 3D Model' button or drag points.")
    
    # ===== MATHEMATICAL CALCULATIONS =====
    
    def calculate_angle_between_vectors(self, v1, v2):
        """Calculate angle between two vectors in degrees"""
        dot_product = v1.x() * v2.x() + v1.y() * v2.y()
        mag1 = math.sqrt(v1.x() ** 2 + v1.y() ** 2)
        mag2 = math.sqrt(v2.x() ** 2 + v2.y() ** 2)
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(-1, min(1, cos_angle))
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def snap_to_right_angle(self, new_point, prev_point, prev_prev_point):
        """Snap new point to create right angle if close enough"""
        if not self.angle_snap_enabled:
            return new_point
        
        # Vector from prev_prev to prev
        v1 = QPointF(prev_point.x() - prev_prev_point.x(), prev_point.y() - prev_prev_point.y())
        # Vector from prev to new
        v2 = QPointF(new_point.x() - prev_point.x(), new_point.y() - prev_point.y())
        
        angle = self.calculate_angle_between_vectors(v1, v2)
        
        # Check if close to 90 degrees
        if abs(angle - 90) <= self.angle_tolerance:
            # Calculate perpendicular direction
            if abs(v1.x()) < 0.001:  # Nearly vertical line
                return QPointF(new_point.x(), prev_point.y())
            elif abs(v1.y()) < 0.001:  # Nearly horizontal line
                return QPointF(prev_point.x(), new_point.y())
            else:
                # Calculate perpendicular vector
                perp_x = -v1.y()
                perp_y = v1.x()
                
                # Normalize
                perp_mag = math.sqrt(perp_x ** 2 + perp_y ** 2)
                if perp_mag > 0:
                    perp_x /= perp_mag
                    perp_y /= perp_mag
                
                # Calculate distance to new point
                dist = math.sqrt(v2.x() ** 2 + v2.y() ** 2)
                
                # Create perpendicular point
                snapped_x = prev_point.x() + perp_x * dist
                snapped_y = prev_point.y() + perp_y * dist
                
                # Choose the perpendicular direction closest to the original point
                alt_x = prev_point.x() - perp_x * dist
                alt_y = prev_point.y() - perp_y * dist
                
                dist1 = (new_point.x() - snapped_x) ** 2 + (new_point.y() - snapped_y) ** 2
                dist2 = (new_point.x() - alt_x) ** 2 + (new_point.y() - alt_y) ** 2
                
                if dist2 < dist1:
                    return QPointF(alt_x, alt_y)
                else:
                    return QPointF(snapped_x, snapped_y)
        
        return new_point
    
    # ===== POLYGON CALCULATIONS =====
    
    def calculate_polygon_area(self):
        """Calculate polygon area in square meters"""
        if len(self.points) < 3:
            return 0
        
        # Calculate area using shoelace formula
        area = 0
        for i in range(len(self.points)):
            j = (i + 1) % len(self.points)
            area += self.points[i].x() * self.points[j].y()
            area -= self.points[j].x() * self.points[i].y()
        
        area = abs(area) / 2
        real_area = area * (self.scale_factor ** 2)
        
        return real_area
    
    def calculate_polygon_perimeter(self):
        """Calculate polygon perimeter in meters"""
        if len(self.points) < 2:
            return 0
        
        perimeter = 0
        for i in range(len(self.points)):
            j = (i + 1) % len(self.points)
            dx = self.points[j].x() - self.points[i].x()
            dy = self.points[j].y() - self.points[i].y()
            distance = math.sqrt(dx * dx + dy * dy)
            perimeter += distance
        
        real_perimeter = perimeter * self.scale_factor
        
        return real_perimeter
    
    def get_polygon_measurements(self):
        """Get polygon measurements as dictionary"""
        return {
            'points': len(self.points),
            'area': self.calculate_polygon_area(),
            'perimeter': self.calculate_polygon_perimeter(),
            'is_complete': self.is_complete,
            'scale_factor': self.scale_factor
        }
    
    def get_polygon_info(self):
        """Get polygon information for UI updates"""
        return {
            'points': len(self.points),
            'area': self.calculate_polygon_area(),
            'perimeter': self.calculate_polygon_perimeter(),
            'is_complete': self.is_complete,
            'scale_factor': self.scale_factor
        }
    
    def fit_in_view(self):
        """Alias for zoom_fit"""
        self.zoom_fit()
    
    def reset_view(self):
        """Reset zoom and pan"""
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update()
        print("✓ View reset")
    
    # ===== ENHANCED 3D MODEL GENERATION =====
    
    def create_3d_model(self, points=None, source="manual", emit_signal=True, **kwargs):
        """Enhanced 3D model generation with comprehensive validation"""
        if points is None:
            points = self.points.copy()
        
        print(f"🏗️ Creating 3D model from {len(points)} points... [Source: {source}]")
        
        # Comprehensive validation
        validation_result = self._validate_points_for_3d_generation(points)
        if not validation_result['valid']:
            print(f"❌ Validation failed: {validation_result['error']}")
            self._show_error_message(validation_result['error'])
            return False
        
        try:
            # Find main window
            main_window = self._find_main_window_enhanced()
            if not main_window:
                self._show_error_message("Cannot find main window for 3D generation")
                return False
            
            # Get model tab
            model_tab = self._get_model_tab_enhanced(main_window)
            if not model_tab:
                self._show_error_message("Cannot find 3D model tab")
                return False
            
            # Prepare building settings
            settings = self._prepare_building_settings(main_window, **kwargs)
            print(f"🔧 Building settings: {settings}")
            
            # Pre-generation notification
            if emit_signal:
                self.model_generation_requested.emit(points, settings)
            
            # Generate building
            success = model_tab.create_building(
                points,
                height=settings.get('height', 3.0),
                roof_type=settings.get('roof_type', 'flat'),
                roof_pitch=settings.get('roof_pitch', 30),
                scale=settings.get('scale', self.scale_factor),
                source=source,
                emit_signal=emit_signal
            )
            
            if success:
                self._handle_successful_3d_generation(main_window, source, len(points))
                self.last_3d_generation_successful = True
                
                # Post-generation signal
                if emit_signal:
                    self.generate_3d_model.emit(points)
                
                return True
            else:
                self._handle_failed_3d_generation()
                return False
            
        except Exception as e:
            print(f"❌ Error creating 3D model: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_message(f"3D generation failed: {str(e)}")
            return False
    
    def _validate_points_for_3d_generation(self, points):
        """Comprehensive validation for 3D generation"""
        # Basic point count check
        if not points or len(points) < 3:
            return {
                'valid': False,
                'error': f"Need at least 3 points for 3D model. Found {len(points)} points."
            }
        
        # Check point format
        for i, point in enumerate(points):
            if not hasattr(point, 'x') or not hasattr(point, 'y'):
                return {
                    'valid': False,
                    'error': f"Invalid point format at index {i}"
                }
        
        # Check minimum area
        area = self.calculate_polygon_area()
        if area < 0.01:  # Less than 0.01 m²
            return {
                'valid': False,
                'error': f"Polygon area too small ({area:.4f}m²). Minimum 0.01m²."
            }
        
        # Check for reasonable polygon size
        if area > 10000:  # Larger than 10,000 m²
            return {
                'valid': False,
                'error': f"Polygon area very large ({area:.1f}m²). Please check scale."
            }
        
        # Check for self-intersections (basic)
        if self._has_self_intersections(points):
            return {
                'valid': False,
                'error': "Polygon has self-intersections. Please fix the drawing."
            }
        
        return {'valid': True, 'error': None}
    
    def _has_self_intersections(self, points):
        """Basic check for self-intersecting polygon"""
        if len(points) < 4:
            return False
        
        try:
            for i in range(len(points)):
                for j in range(i + 2, len(points)):
                    if j == len(points) - 1 and i == 0:
                        continue  # Skip adjacent segments
                    
                    p1 = points[i]
                    p2 = points[(i + 1) % len(points)]
                    p3 = points[j]
                    p4 = points[(j + 1) % len(points)]
                    
                    if self._segments_intersect(p1, p2, p3, p4):
                        return True
            return False
        except:
            return False
    
    def _segments_intersect(self, p1, p2, p3, p4):
        """Check if two line segments intersect"""
        try:
            def ccw(A, B, C):
                return (C.y() - A.y()) * (B.x() - A.x()) > (B.y() - A.y()) * (C.x() - A.x())
            
            return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
        except:
            return False
    
    def _find_main_window_enhanced(self):
        """Enhanced main window discovery"""
        widget = self
        attempts = 0
        max_attempts = 15
        
        while widget and attempts < max_attempts:
            # Check for multiple main window indicators
            if (hasattr(widget, 'content_tabs') and 
                (hasattr(widget, 'left_panel') or hasattr(widget, 'canvas_manager'))):
                return widget
            widget = widget.parent()
            attempts += 1
        
        return None
    
    def _get_model_tab_enhanced(self, main_window):
        """Enhanced model tab discovery"""
        try:
            if not hasattr(main_window, 'content_tabs'):
                return None
            
            # Method 1: Try index 2 (common model tab position)
            if main_window.content_tabs.count() > 2:
                model_tab = main_window.content_tabs.widget(2)
                if model_tab and hasattr(model_tab, 'create_building'):
                    return model_tab
            
            # Method 2: Search all tabs for model functionality
            for i in range(main_window.content_tabs.count()):
                tab = main_window.content_tabs.widget(i)
                if tab and hasattr(tab, 'create_building'):
                    print(f"🔍 Found model tab at index {i}")
                    return tab
            
            # Method 3: Check tab titles
            for i in range(main_window.content_tabs.count()):
                tab_title = main_window.content_tabs.tabText(i).lower()
                if any(keyword in tab_title for keyword in ['model', '3d', 'building']):
                    tab = main_window.content_tabs.widget(i)
                    if tab:
                        return tab
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding model tab: {e}")
            return None
    
    def _prepare_building_settings(self, main_window, **kwargs):
        """Prepare comprehensive building settings"""
        # Start with defaults
        settings = {
            'height': 3.0,
            'roof_type': 'flat',
            'roof_pitch': 30,
            'scale': self.scale_factor,
            'wall_thickness': 0.2,
            'foundation_height': 0.3,
            'material_color': 'lightcoral',
            'roof_color': 'darkred'
        }
        
        # Apply kwargs overrides
        settings.update(kwargs)
        
        # Try to get from UI components
        try:
            if hasattr(main_window, 'left_panel'):
                panel = main_window.left_panel
                
                # Multiple methods to get settings
                methods_to_try = [
                    'get_building_settings',
                    'get_building_parameters', 
                    'get_all_settings',
                    'get_current_settings'
                ]
                
                for method_name in methods_to_try:
                    if hasattr(panel, method_name):
                        try:
                            method = getattr(panel, method_name)
                            panel_settings = method()
                            if isinstance(panel_settings, dict):
                                settings.update(panel_settings)
                                print(f"✅ Got settings from {method_name}")
                                break
                        except Exception as e:
                            print(f"⚠️ Failed to get settings from {method_name}: {e}")
                            continue
        
        except Exception as e:
            print(f"⚠️ Error getting UI settings: {e}")
        
        return settings
    
    def _handle_successful_3d_generation(self, main_window, source, point_count):
        """Handle successful 3D generation"""
        print("✅ 3D model created successfully")
        
        # Update status
        self._update_status()
        
        # Show success message in main window
        if hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(
                f"✅ 3D building generated from {point_count} points!", 4000
            )
        
        # Auto-switch logic based on source
        if source == "manual" or source == "double_click":
            main_window.content_tabs.setCurrentIndex(2)
            print("🔄 Auto-switched to model tab")
        elif source == "button":
            # Check if auto-switch is enabled
            if getattr(main_window, 'auto_switch_enabled', True):
                main_window.content_tabs.setCurrentIndex(2)
                print("🔄 Auto-switched to model tab (button)")
            else:
                print("🤖 No auto-switch for button generation")
        
        print(f"✅ 3D generation completed successfully [Source: {source}]")
    
    def _handle_failed_3d_generation(self):
        """Handle failed 3D generation"""
        print("❌ Failed to create 3D model")
        self.last_3d_generation_successful = False
        self._update_status()
        self._show_error_message("Failed to generate 3D model. Check your drawing and try again.")
    
    def _show_error_message(self, message):
        """Show error message to user"""
        print(f"❌ {message}")
        
        # Try to show in main window status bar
        main_window = self._find_main_window_enhanced()
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar().showMessage(f"❌ {message}", 6000)
    
    # ===== MANUAL 3D GENERATION METHODS =====
    
    def generate_3d_model_manually(self, **kwargs):
        """Manual 3D model generation (called from buttons)"""
        if not self.is_complete or len(self.points) < 3:
            self._show_error_message("Complete a polygon first before generating 3D model")
            return False
        
        return self.create_3d_model(
            source="manual_button",
            emit_signal=True,
            **kwargs
        )
    
    def preview_3d_model(self, **kwargs):
        """Preview 3D model without full generation"""
        if not self.is_complete or len(self.points) < 3:
            return False
        
        # Quick preview with basic settings
        basic_settings = {
            'height': 2.0,
            'roof_type': 'flat',
            'scale': self.scale_factor
        }
        basic_settings.update(kwargs)
        
        return self.create_3d_model(
            source="preview",
            emit_signal=False,
            **basic_settings
        )
    
    def set_auto_3d_generation(self, enabled):
        """Enable/disable automatic 3D generation on polygon completion"""
        self.auto_generate_3d = enabled
        print(f"✓ Auto 3D generation {'enabled' if enabled else 'disabled'}")
    
    # ===== UTILITY METHODS =====
    
    def get_drawing_info(self):
        """Get comprehensive drawing information"""
        return {
            'points': len(self.points),
            'is_complete': self.is_complete,
            'area': self.calculate_polygon_area(),
            'perimeter': self.calculate_polygon_perimeter(),
            'scale_factor': self.scale_factor,
            'last_3d_successful': self.last_3d_generation_successful,
            'auto_3d_enabled': self.auto_generate_3d
        }
    
    def cleanup(self):
        """Cleanup canvas resources"""
        try:
            self.clear_all()
            if self.background_pixmap:
                self.background_pixmap = None
            print("✅ Drawing canvas cleanup completed")
        except Exception as e:
            print(f"❌ Error during canvas cleanup: {e}")

