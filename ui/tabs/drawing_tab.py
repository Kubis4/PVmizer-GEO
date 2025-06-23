#!/usr/bin/env python3
"""
Drawing Tab - Canvas for building outline drawing
CLEAN VERSION - Controls moved to left panel
"""
import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont

class DrawingTab(QWidget):
    """Drawing tab with canvas for building outline - CLEAN with magnetic snapping"""
    
    # Existing signals
    canvas_ready = pyqtSignal()
    canvas_error = pyqtSignal(str)
    drawing_completed = pyqtSignal(list)
    
    # NEW: Signals for left panel communication
    snap_point_added = pyqtSignal(QPointF)  # Point added with snapping
    line_completed = pyqtSignal(list)  # Line completed
    measurements_changed = pyqtSignal(dict)  # Real-time measurements
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.drawing_canvas = None
        self.canvas_properly_sized = False
        
        # Target sizes
        self.target_width = 1200
        self.target_height = 800
        self.canvas_width = self.target_width - 20
        self.canvas_height = self.target_height - 20
        
        # Magnetic snapping system (controlled by left panel)
        self._init_magnetic_snapping()
        
        # Connect to left panel signals
        self._connect_to_left_panel()
        
        self._setup_ui()
        self._schedule_canvas_operations()
    
    def _init_magnetic_snapping(self):
        """Initialize magnetic snapping system"""
        # Snapping settings (controlled by left panel)
        self.snap_enabled = True
        self.grid_visible = False  # Start hidden, controlled by left panel
        self.grid_size = 20
        self.snap_tolerance = 15
        self.angle_constraints = [0, 15, 30, 45, 90, 135, 180]
        self.angle_snap_enabled = True  # Controlled by left panel
        
        # Drawing state
        self.drawing_points = []
        self.completed_lines = []
        self.current_line = []
        self.reference_point = None
        self.current_snap_pos = None
        self.current_snap_info = None
        
        # Scale factor (from left panel)
        self.scale_factor = 0.05
        
        print("🧲 Magnetic snapping system initialized")
    
    def _connect_to_left_panel(self):
        """Connect to left panel signals"""
        try:
            # Get the drawing tab panel from main window
            if hasattr(self.main_window, 'left_panel') and hasattr(self.main_window.left_panel, 'drawing_panel'):
                panel = self.main_window.left_panel.drawing_panel
                
                # Connect signals FROM left panel TO canvas
                panel.scale_changed.connect(self._on_scale_changed)
                panel.angle_snap_toggled.connect(self._on_angle_snap_toggled)
                panel.clear_drawing_requested.connect(self._on_clear_requested)
                
                # Connect signals FROM canvas TO left panel
                self.measurements_changed.connect(panel.update_polygon_info)
                self.line_completed.connect(panel.polygon_completed.emit)
                
                print("✅ Connected to left panel")
        except Exception as e:
            print(f"⚠️ Could not connect to left panel: {e}")
    
    def _setup_ui(self):
        """Setup drawing tab UI - CLEAN, no controls"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        # Set initial size
        self.setMinimumSize(self.target_width, self.target_height)
        self.resize(self.target_width, self.target_height)
        
        # Try to create canvas immediately
        if not self._create_canvas():
            self._create_placeholder()
    
    def _create_canvas(self):
        """Create drawing canvas - ENHANCED with snapping integration"""
        if not (hasattr(self.main_window, 'canvas_manager') and 
                self.main_window.canvas_manager is not None and
                hasattr(self.main_window.canvas_manager, 'create_canvas')):
            return False
        
        try:
            # Set canvas manager sizing
            self.main_window.canvas_manager.actual_canvas_size = (
                self.canvas_width, self.canvas_height
            )
            if hasattr(self.main_window.canvas_manager, 'default_canvas_size'):
                self.main_window.canvas_manager.default_canvas_size = (
                    self.canvas_width, self.canvas_height
                )
            
            # Create canvas
            self.drawing_canvas = self.main_window.canvas_manager.create_canvas()
            if self.drawing_canvas is not None:
                self.drawing_canvas.setMinimumSize(self.canvas_width, self.canvas_height)
                self.drawing_canvas.resize(self.canvas_width, self.canvas_height)
                
                # Enable mouse tracking for snapping
                self.drawing_canvas.setMouseTracking(True)
                
                # Enhance canvas with magnetic snapping
                self._enhance_canvas_with_snapping()
                
                self.layout.addWidget(self.drawing_canvas)
                self.canvas_properly_sized = True
                self.canvas_ready.emit()
                
                print("✅ Clean canvas created with magnetic snapping")
                return True
                
        except Exception as e:
            self.canvas_error.emit(str(e))
            print(f"❌ Canvas creation error: {e}")
            return False
        
        return False
    
    def _enhance_canvas_with_snapping(self):
        """ENHANCE: Add magnetic snapping to existing canvas"""
        if not self.drawing_canvas:
            return
        
        # Store original event handlers
        self._original_mouse_press = getattr(self.drawing_canvas, 'mousePressEvent', None)
        self._original_mouse_move = getattr(self.drawing_canvas, 'mouseMoveEvent', None)
        self._original_mouse_double_click = getattr(self.drawing_canvas, 'mouseDoubleClickEvent', None)
        self._original_paint_event = getattr(self.drawing_canvas, 'paintEvent', None)
        
        # Override with snapping-enhanced events
        self.drawing_canvas.mousePressEvent = self._enhanced_mouse_press
        self.drawing_canvas.mouseMoveEvent = self._enhanced_mouse_move
        self.drawing_canvas.mouseDoubleClickEvent = self._enhanced_double_click
        self.drawing_canvas.paintEvent = self._enhanced_paint_event
        
        print("🎯 Canvas enhanced with magnetic snapping")
    
    # ENHANCED EVENT HANDLERS
    def _enhanced_mouse_press(self, event):
        """ENHANCED: Mouse press with magnetic snapping"""
        try:
            # Call original handler first
            if self._original_mouse_press:
                self._original_mouse_press(event)
            
            # Apply magnetic snapping
            if event.button() == Qt.LeftButton and self.snap_enabled:
                raw_point = event.pos()
                snapped_point, snap_info = self._snap_point(raw_point)
                
                # Update drawing state
                self.current_line.append(snapped_point)
                self.drawing_points.append(snapped_point)
                self.reference_point = snapped_point
                
                # Emit signals to left panel
                self.snap_point_added.emit(snapped_point)
                self._emit_measurements_update()
                
                self.drawing_canvas.update()
                
                print(f"🎯 Point added: ({snapped_point.x():.1f}, {snapped_point.y():.1f})")
        
        except Exception as e:
            print(f"❌ Enhanced mouse press error: {e}")
    
    def _enhanced_mouse_move(self, event):
        """ENHANCED: Mouse move with snap preview"""
        try:
            # Call original handler first
            if self._original_mouse_move:
                self._original_mouse_move(event)
            
            # Update snap preview
            if self.snap_enabled:
                self.current_mouse_pos = event.pos()
                self.current_snap_pos, self.current_snap_info = self._snap_point(event.pos())
                self.drawing_canvas.update()
        
        except Exception as e:
            pass  # Mouse move errors are non-critical
    
    def _enhanced_double_click(self, event):
        """ENHANCED: Double click to complete line"""
        try:
            # Call original handler first
            if self._original_mouse_double_click:
                self._original_mouse_double_click(event)
            
            # Complete current line
            if len(self.current_line) > 1:
                completed_line = self.current_line.copy()
                self.completed_lines.append(completed_line)
                
                # Emit signals to left panel
                self.line_completed.emit(completed_line)
                self.drawing_completed.emit(completed_line)
                self._emit_measurements_update()
                
                self.current_line.clear()
                self.reference_point = None
                self.drawing_canvas.update()
                
                print(f"✅ Line completed with {len(completed_line)} points")
        
        except Exception as e:
            print(f"❌ Enhanced double click error: {e}")
    
    def _enhanced_paint_event(self, event):
        """ENHANCED: Paint event with grid and snap indicators"""
        try:
            # Call original paint event first
            if self._original_paint_event:
                self._original_paint_event(event)
            
            # Add magnetic snapping visuals
            painter = QPainter(self.drawing_canvas)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw grid if enabled (controlled by left panel)
            if self.grid_visible:
                self._draw_magnetic_grid(painter)
            
            # Draw snap indicators
            if self.snap_enabled and self.current_snap_pos and self.current_snap_info:
                self._draw_snap_indicator(painter, self.current_snap_pos, self.current_snap_info)
            
            # Draw magnetic drawing overlays
            self._draw_magnetic_overlays(painter)
            
        except Exception as e:
            print(f"❌ Enhanced paint error: {e}")
    
    # MAGNETIC SNAPPING CORE FUNCTIONS (same as before)
    def _snap_point(self, raw_point):
        """Core magnetic snapping function"""
        if not self.snap_enabled:
            return raw_point, None
            
        snapped_point = raw_point
        snap_info = {"type": None, "target": None}
        
        # Priority 1: Snap to existing points
        point_snap = self._snap_to_points(raw_point)
        if point_snap:
            return point_snap
            
        # Priority 2: Snap to lines
        line_snap = self._snap_to_lines(raw_point)
        if line_snap:
            return line_snap
            
        # Priority 3: Snap to grid
        if self.grid_visible:
            grid_snap = self._snap_to_grid(raw_point)
            snapped_point = grid_snap
            snap_info = {"type": "grid", "target": grid_snap}
        
        # Priority 4: Apply angle constraints (controlled by left panel)
        if self.reference_point and self.angle_snap_enabled:
            angle_snap = self._snap_to_angle(snapped_point, self.reference_point)
            if angle_snap != snapped_point:
                snapped_point = angle_snap
                snap_info["angle_constrained"] = True
        
        return snapped_point, snap_info
    
    def _snap_to_grid(self, point):
        """Snap to grid intersection"""
        x, y = point.x(), point.y()
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return QPointF(snapped_x, snapped_y)
    
    def _snap_to_points(self, point):
        """Snap to existing points"""
        for existing_point in self.drawing_points:
            distance = self._calculate_distance(point, existing_point)
            if distance < self.snap_tolerance:
                return existing_point, {"type": "point", "target": existing_point}
        return None
    
    def _snap_to_lines(self, point):
        """Snap to existing lines"""
        for line in self.completed_lines:
            if len(line) >= 2:
                for i in range(len(line) - 1):
                    projection = self._project_point_to_line(point, line[i], line[i+1])
                    distance = self._calculate_distance(point, projection)
                    if distance < self.snap_tolerance:
                        return projection, {"type": "line", "target": (line[i], line[i+1])}
        return None
    
    def _snap_to_angle(self, point, reference_point):
        """Apply angle constraints"""
        if not reference_point:
            return point
            
        dx = point.x() - reference_point.x()
        dy = point.y() - reference_point.y()
        current_angle = math.degrees(math.atan2(dy, dx))
        
        # Find closest constraint angle
        min_diff = float('inf')
        best_angle = current_angle
        
        for constraint_angle in self.angle_constraints:
            diff = abs(current_angle - constraint_angle)
            if diff > 180:
                diff = 360 - diff
            if diff < min_diff and diff < 15:
                min_diff = diff
                best_angle = constraint_angle
        
        if min_diff < 15:
            distance = math.sqrt(dx*dx + dy*dy)
            constrained_angle = math.radians(best_angle)
            new_x = reference_point.x() + distance * math.cos(constrained_angle)
            new_y = reference_point.y() + distance * math.sin(constrained_angle)
            return QPointF(new_x, new_y)
        
        return point
    
    # VISUAL FUNCTIONS
    def _draw_magnetic_grid(self, painter):
        """Draw magnetic grid overlay"""
        painter.setPen(QPen(QColor(200, 200, 200, 80), 1))
        
        # Vertical lines
        x = 0
        while x <= self.drawing_canvas.width():
            painter.drawLine(x, 0, x, self.drawing_canvas.height())
            x += self.grid_size
        
        # Horizontal lines
        y = 0
        while y <= self.drawing_canvas.height():
            painter.drawLine(0, y, self.drawing_canvas.width(), y)
            y += self.grid_size
    
    def _draw_snap_indicator(self, painter, point, snap_info):
        """Draw magnetic snap visual feedback"""
        painter.setPen(QPen(QColor(0, 120, 255, 180), 2))
        
        x, y = point.x(), point.y()
        
        if snap_info.get("type") == "point":
            # Circle for point snap
            painter.drawEllipse(QPointF(x, y), 8, 8)
        elif snap_info.get("type") == "line":
            # Square for line snap
            painter.drawRect(x-4, y-4, 8, 8)
        elif snap_info.get("type") == "grid":
            # Cross for grid snap
            painter.drawLine(x-6, y, x+6, y)
            painter.drawLine(x, y-6, x, y+6)
    
    def _draw_magnetic_overlays(self, painter):
        """Draw magnetic drawing overlays"""
        if not self.snap_enabled:
            return
        
        # Draw magnetic points
        painter.setPen(QPen(QColor(255, 100, 100), 2))
        painter.setBrush(QColor(255, 100, 100, 100))
        for point in self.drawing_points:
            painter.drawEllipse(point, 3, 3)
        
        # Draw magnetic lines
        painter.setPen(QPen(QColor(255, 0, 0, 150), 2))
        for line in self.completed_lines:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    painter.drawLine(line[i], line[i + 1])
        
        # Draw current line preview
        if self.current_line and self.current_snap_pos:
            painter.setPen(QPen(QColor(255, 0, 0, 100), 1))
            if len(self.current_line) > 0:
                painter.drawLine(self.current_line[-1], self.current_snap_pos)
    
    # LEFT PANEL SIGNAL HANDLERS
    def _on_scale_changed(self, scale):
        """Handle scale change from left panel"""
        self.scale_factor = scale
        self._emit_measurements_update()
        print(f"📏 Canvas scale updated: {scale}")
    
    def _on_angle_snap_toggled(self, enabled):
        """Handle angle snap toggle from left panel"""
        self.angle_snap_enabled = enabled
        print(f"📐 Canvas angle snap: {'ON' if enabled else 'OFF'}")
    
    def _on_clear_requested(self):
        """Handle clear request from left panel"""
        self._clear_magnetic_drawing()
        self.clear_drawing()  # Also clear original canvas
        print("🗑️ Canvas cleared from left panel")
    
    def _clear_magnetic_drawing(self):
        """Clear magnetic drawing data"""
        self.drawing_points.clear()
        self.completed_lines.clear()
        self.current_line.clear()
        self.reference_point = None
        self.current_snap_pos = None
        self.current_snap_info = None
        
        if self.drawing_canvas:
            self.drawing_canvas.update()
    
    def _emit_measurements_update(self):
        """Emit measurements update to left panel"""
        try:
            measurements = self._calculate_measurements()
            self.measurements_changed.emit(measurements)
        except Exception as e:
            print(f"❌ Error emitting measurements: {e}")
    
    def _calculate_measurements(self):
        """Calculate real-time measurements"""
        point_count = len(self.drawing_points)
        area = 0.0
        perimeter = 0.0
        is_complete = False
        
        try:
            # Calculate area and perimeter for completed polygons
            if len(self.completed_lines) > 0:
                total_points = []
                for line in self.completed_lines:
                    total_points.extend(line)
                
                if len(total_points) >= 3:
                    # Calculate area using shoelace formula
                    area = self._calculate_polygon_area(total_points) * (self.scale_factor ** 2)
                    perimeter = self._calculate_polygon_perimeter(total_points) * self.scale_factor
                    is_complete = True
            
        except Exception as e:
            print(f"❌ Error calculating measurements: {e}")
        
        return {
            'points': point_count,
            'area': area,
            'perimeter': perimeter,
            'is_complete': is_complete
        }
    
    def _calculate_polygon_area(self, points):
        """Calculate polygon area using shoelace formula"""
        if len(points) < 3:
            return 0.0
        
        area = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i].x() * points[j].y()
            area -= points[j].x() * points[i].y()
        return abs(area) / 2.0
    
    def _calculate_polygon_perimeter(self, points):
        """Calculate polygon perimeter"""
        if len(points) < 2:
            return 0.0
        
        perimeter = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            perimeter += self._calculate_distance(points[i], points[j])
        return perimeter
    
    # UTILITY FUNCTIONS
    def _calculate_distance(self, p1, p2):
        """Calculate distance between points"""
        return math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
    
    def _project_point_to_line(self, point, line_start, line_end):
        """Project point onto line"""
        x, y = point.x(), point.y()
        x1, y1 = line_start.x(), line_start.y()
        x2, y2 = line_end.x(), line_end.y()
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return QPointF(x1, y1)
        
        t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        return QPointF(proj_x, proj_y)
    
    # PUBLIC API METHODS FOR LEFT PANEL
    def enable_grid(self, enabled=True):
        """Enable/disable grid from left panel"""
        self.grid_visible = enabled
        if self.drawing_canvas:
            self.drawing_canvas.update()
    
    def set_grid_size(self, size):
        """Set grid size from left panel"""
        self.grid_size = max(10, min(100, size))
        if self.drawing_canvas:
            self.drawing_canvas.update()
    
    def get_magnetic_drawing_data(self):
        """Get drawing data for 3D generation"""
        return {
            'points': self.drawing_points,
            'lines': self.completed_lines,
            'measurements': self._calculate_measurements(),
            'canvas_size': (self.canvas_width, self.canvas_height),
            'scale_factor': self.scale_factor
        }
    
    # KEEP ALL EXISTING METHODS (same as before)
    def _create_placeholder(self):
        """Create placeholder when canvas creation fails"""
        placeholder_label = QLabel(
            "Drawing canvas loading...\nCanvas will be available shortly"
        )
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setMinimumSize(self.canvas_width, self.canvas_height)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 40px;
                border: 2px dashed #007acc;
                border-radius: 8px;
                background-color: #f0f8ff;
            }
        """)
        self.layout.addWidget(placeholder_label)
        
        # Schedule retry
        QTimer.singleShot(200, self._retry_canvas_creation)
        QTimer.singleShot(800, self._retry_canvas_creation)
    
    def _retry_canvas_creation(self):
        """Retry canvas creation with proper sizing"""
        try:
            if self.drawing_canvas is not None:
                return  # Canvas already created
            
            # Clear existing widgets
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Try creating canvas again
            if self._create_canvas():
                print("✅ Clean canvas created successfully on retry")
            else:
                print("❌ Clean canvas creation failed on retry")
                
        except Exception as e:
            print(f"❌ Error during canvas retry: {e}")
    
    def _schedule_canvas_operations(self):
        """Schedule canvas sizing operations"""
        QTimer.singleShot(100, self._force_immediate_sizing)
        QTimer.singleShot(500, self._finalize_sizing)
        QTimer.singleShot(1000, self._verify_sizing)
    
    def _force_immediate_sizing(self):
        """Force immediate canvas sizing"""
        try:
            self.resize(self.target_width, self.target_height)
            
            if hasattr(self.main_window, 'canvas_manager'):
                self.main_window.canvas_manager.actual_canvas_size = (
                    self.canvas_width, self.canvas_height
                )
                if hasattr(self.main_window.canvas_manager, 'default_canvas_size'):
                    self.main_window.canvas_manager.default_canvas_size = (
                        self.canvas_width, self.canvas_height
                    )
            
            QApplication.processEvents()
            self.canvas_properly_sized = True
            
        except Exception as e:
            pass
    
    def _finalize_sizing(self):
        """Finalize canvas sizing after initialization"""
        try:
            current_size = self.size()
            
            if current_size.width() < 1000 or current_size.height() < 700:
                self.resize(self.target_width, self.target_height)
            
            if hasattr(self.main_window, 'canvas_manager'):
                final_size = self.size()
                canvas_w = final_size.width() - 20
                canvas_h = final_size.height() - 20
                
                self.main_window.canvas_manager.actual_canvas_size = (canvas_w, canvas_h)
                if hasattr(self.main_window.canvas_manager, 'default_canvas_size'):
                    self.main_window.canvas_manager.default_canvas_size = (canvas_w, canvas_h)
            
        except Exception as e:
            pass
    
    def _verify_sizing(self):
        """Verify canvas sizing is correct"""
        try:
            if hasattr(self.main_window, 'canvas_manager'):
                if hasattr(self.main_window.canvas_manager, 'actual_canvas_size'):
                    size = self.main_window.canvas_manager.actual_canvas_size
                    
                    if size[0] < 800 or size[1] < 600:
                        self.main_window.canvas_manager.actual_canvas_size = (
                            self.canvas_width, self.canvas_height
                        )
                else:
                    self.main_window.canvas_manager.actual_canvas_size = (
                        self.canvas_width, self.canvas_height
                    )
            
        except Exception as e:
            pass
    
    def get_canvas(self):
        """Get the drawing canvas"""
        return self.drawing_canvas
    
    def is_canvas_ready(self):
        """Check if canvas is ready"""
        return self.drawing_canvas is not None and self.canvas_properly_sized
    
    def set_background_image(self, pixmap):
        """Set background image for canvas"""
        try:
            if self.drawing_canvas and hasattr(self.drawing_canvas, 'set_background_image'):
                self.drawing_canvas.set_background_image(pixmap)
                return True
            elif self.drawing_canvas and hasattr(self.drawing_canvas, 'load_background'):
                self.drawing_canvas.load_background(pixmap)
                return True
            return False
        except Exception as e:
            return False
    
    def clear_drawing(self):
        """Clear the drawing"""
        try:
            if self.drawing_canvas:
                if hasattr(self.drawing_canvas, 'clear'):
                    self.drawing_canvas.clear()
                elif hasattr(self.drawing_canvas, 'points'):
                    self.drawing_canvas.points.clear()
                    if hasattr(self.drawing_canvas, 'update'):
                        self.drawing_canvas.update()
                return True
            return False
        except Exception as e:
            return False
    
    def get_drawing_points(self):
        """Get current drawing points - ENHANCED with magnetic points"""
        try:
            # First try magnetic points
            if self.drawing_points:
                return self.drawing_points
            
            # Fall back to original canvas points
            if self.drawing_canvas:
                for attr_name in ['get_drawing_points', 'points']:
                    if hasattr(self.drawing_canvas, attr_name):
                        attr = getattr(self.drawing_canvas, attr_name)
                        points = attr() if callable(attr) else attr
                        if points:
                            return points
            return []
        except Exception as e:
            return []