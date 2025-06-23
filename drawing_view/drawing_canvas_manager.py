#!/usr/bin/env python3
"""
CLEAN Canvas Manager - Creates real DrawingCanvas with proper import handling
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPixmap, QColor
import sys
import os
import importlib.util

class CanvasManager(QObject):
    """CLEAN canvas manager - creates and integrates real DrawingCanvas"""
    
    # Signals
    boundary_completed = pyqtSignal(list)      
    ridge_completed = pyqtSignal(list)         
    area_calculated = pyqtSignal(float, str)   
    drawing_completed = pyqtSignal(list)       
    scale_changed = pyqtSignal(float)          
    mode_changed = pyqtSignal(str)             
    canvas_ready = pyqtSignal()                
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Canvas references
        self.canvas_widget = None
        self.drawing_canvas = None
        self.drawing_area = None
        
        # State tracking
        self.scale_factor = 0.05
        self.current_mode = "boundary"
        self.canvas_initialized = False
        
        # Canvas size management
        self.default_canvas_size = (1180, 780)
        self.actual_canvas_size = (1180, 780)
        
        # Enhancement settings
        self.center_screenshots = True
        self.enhance_screenshots = True
        self.enhancement_settings = {
            'transparency': 0.75,
            'brightness': 1.1,
            'add_border': True,
            'border_color': (180, 180, 180),
            'background_color': (220, 220, 220)
        }
        
        # Import DrawingCanvas
        self.DrawingCanvas = self._import_drawing_canvas()
    
    def _import_drawing_canvas(self):
        """Import DrawingCanvas with multiple fallback methods"""
        try:
            # Method 1: Direct import
            try:
                from drawing_canvas import DrawingCanvas
                return DrawingCanvas
            except ImportError:
                pass
            
            # Method 2: Add current directory to path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            try:
                from drawing_canvas import DrawingCanvas
                return DrawingCanvas
            except ImportError:
                pass
            
            # Method 3: Search for the file and load manually
            drawing_canvas_path = self._find_drawing_canvas_file()
            if drawing_canvas_path:
                return self._load_drawing_canvas_from_path(drawing_canvas_path)
            
            # Method 4: Create embedded DrawingCanvas
            return self._create_embedded_drawing_canvas()
            
        except Exception as e:
            return None
    
    def _find_drawing_canvas_file(self):
        """Find drawing_canvas.py file"""
        search_paths = [
            os.path.dirname(os.path.abspath(__file__)),
            os.getcwd(),
            os.path.join(os.getcwd(), 'drawing_view'),
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ]
        
        for path in search_paths:
            file_path = os.path.join(path, 'drawing_canvas.py')
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def _load_drawing_canvas_from_path(self, file_path):
        """Load DrawingCanvas from file path"""
        try:
            spec = importlib.util.spec_from_file_location("drawing_canvas", file_path)
            drawing_canvas_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(drawing_canvas_module)
            
            if hasattr(drawing_canvas_module, 'DrawingCanvas'):
                return drawing_canvas_module.DrawingCanvas
            else:
                return None
                
        except Exception as e:
            return None
    
    def _create_embedded_drawing_canvas(self):
        """Create embedded DrawingCanvas class as fallback"""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
        from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPointF
        from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QTransform, QPolygonF
        import math
        
        class EmbeddedDrawingArea(QWidget):
            """Embedded drawing area"""
            
            def __init__(self, parent_canvas):
                super().__init__()
                self.parent_canvas = parent_canvas
                self.background_pixmap = None
                self.setMinimumSize(800, 600)
                self.setMouseTracking(True)
            
            def set_background(self, pixmap):
                self.background_pixmap = pixmap
                self.update()
            
            def clear_background(self):
                self.background_pixmap = None
                self.update()
            
            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    if not self.parent_canvas.is_complete:
                        draw_pos = self._screen_to_drawing(event.pos())
                        self.parent_canvas.points.append(draw_pos)
                        self.parent_canvas.is_drawing = True
                        self.parent_canvas._update_status()
                        self.update()
            
            def mouseDoubleClickEvent(self, event):
                if event.button() == Qt.LeftButton and len(self.parent_canvas.points) >= 3:
                    self.parent_canvas.is_complete = True
                    self.parent_canvas.is_drawing = False
                    
                    # ONLY emit polygon_completed signal - NO auto-generation
                    if hasattr(self.parent_canvas, 'polygon_completed'):
                        self.parent_canvas.polygon_completed.emit(self.parent_canvas.points.copy())
                    
                    # REMOVED: Auto 3D model generation
                    # if hasattr(self.parent_canvas, 'create_3d_model'):
                    #     self.parent_canvas.create_3d_model(self.parent_canvas.points.copy())
                    
                    self.parent_canvas._update_status()
                    self.update()
            
            def mouseMoveEvent(self, event):
                if not self.parent_canvas.is_complete:
                    self.parent_canvas.current_mouse_pos = self._screen_to_drawing(event.pos())
                    if self.parent_canvas.is_drawing:
                        self.update()
            
            def wheelEvent(self, event):
                zoom_in = event.angleDelta().y() > 0
                factor = 1.15 if zoom_in else 1.0 / 1.15
                old_zoom = self.parent_canvas.zoom_factor
                self.parent_canvas.zoom_factor *= factor
                self.parent_canvas.zoom_factor = max(0.1, min(10.0, self.parent_canvas.zoom_factor))
                self.update()
            
            def _screen_to_drawing(self, screen_pos):
                x = (screen_pos.x() - self.parent_canvas.pan_offset.x()) / self.parent_canvas.zoom_factor
                y = (screen_pos.y() - self.parent_canvas.pan_offset.y()) / self.parent_canvas.zoom_factor
                return QPointF(x, y)
            
            def _drawing_to_screen(self, drawing_pos):
                x = int(drawing_pos.x() * self.parent_canvas.zoom_factor + self.parent_canvas.pan_offset.x())
                y = int(drawing_pos.y() * self.parent_canvas.zoom_factor + self.parent_canvas.pan_offset.y())
                return QPoint(x, y)
            
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Background
                painter.fillRect(self.rect(), QColor("#4A4A4A"))
                
                # Transform for zoom/pan
                transform = QTransform()
                transform.translate(self.parent_canvas.pan_offset.x(), self.parent_canvas.pan_offset.y())
                transform.scale(self.parent_canvas.zoom_factor, self.parent_canvas.zoom_factor)
                painter.setTransform(transform)
                
                # Draw background image
                if self.background_pixmap:
                    painter.drawPixmap(0, 0, self.background_pixmap)
                
                painter.resetTransform()
                
                # Draw polygon
                self._draw_polygon(painter)
            
            def _draw_polygon(self, painter):
                if not self.parent_canvas.points:
                    return
                
                points = self.parent_canvas.points
                screen_points = [self._drawing_to_screen(p) for p in points]
                
                # Draw lines
                if len(screen_points) > 1:
                    painter.setPen(QPen(QColor(0, 100, 200), 4, Qt.SolidLine))
                    for i in range(len(screen_points) - 1):
                        painter.drawLine(screen_points[i], screen_points[i + 1])
                
                # Draw closing line if complete
                if self.parent_canvas.is_complete and len(screen_points) >= 3:
                    painter.drawLine(screen_points[-1], screen_points[0])
                    
                    # Fill polygon
                    polygon = QPolygonF([QPointF(p.x(), p.y()) for p in screen_points])
                    painter.setPen(QPen())
                    painter.setBrush(QBrush(QColor(100, 150, 255, 40)))
                    painter.drawPolygon(polygon)
                
                # Draw preview line
                elif (self.parent_canvas.is_drawing and 
                    self.parent_canvas.current_mouse_pos and 
                    len(screen_points) > 0):
                    mouse_screen = self._drawing_to_screen(self.parent_canvas.current_mouse_pos)
                    painter.setPen(QPen(QColor(150, 150, 150), 4, Qt.DashLine))
                    painter.drawLine(screen_points[-1], mouse_screen)
                
                # Draw points
                for i, screen_point in enumerate(screen_points):
                    painter.setPen(QPen(QColor(0, 0, 0), 3))
                    painter.setBrush(QBrush(QColor(0, 220, 0)))
                    painter.drawEllipse(screen_point, 9, 9)
                    
                    # Number
                    painter.setFont(QFont("Arial", 11, QFont.Bold))
                    painter.setPen(QPen(QColor(255, 255, 255), 1))
                    painter.drawText(screen_point.x() - 5, screen_point.y() - 15, str(i + 1))
        
        class EmbeddedDrawingCanvas(QWidget):
            """Embedded DrawingCanvas class"""
            
            polygon_completed = pyqtSignal(list)
            drawing_cleared = pyqtSignal()
            generate_3d_model = pyqtSignal(list)
            
            def __init__(self, parent=None):
                super().__init__(parent)
                
                # Drawing state
                self.points = []
                self.is_drawing = False
                self.is_complete = False
                self.background_pixmap = None
                self.current_mouse_pos = None
                
                # Scale factor
                self.scale_factor = 0.05
                
                # Zoom and pan
                self.zoom_factor = 1.0
                self.pan_offset = QPoint(0, 0)
                
                # Setup UI
                self._setup_ui()
            
            def _setup_ui(self):
                layout = QVBoxLayout(self)
                layout.setContentsMargins(3, 3, 3, 3)
                
                self.drawing_area = EmbeddedDrawingArea(self)
                layout.addWidget(self.drawing_area)
                
                # Status bar
                status = QFrame()
                status.setFixedHeight(22)
                status.setStyleSheet("""
                    QFrame { background-color: #2c3e50; border-radius: 3px; }
                    QLabel { color: white; padding: 2px 5px; font-size: 10px; }
                """)
                
                status_layout = QHBoxLayout(status)
                status_layout.setContentsMargins(5, 0, 5, 0)
                
                self.status_label = QLabel("Click to add first point")
                status_layout.addWidget(self.status_label)
                status_layout.addStretch()
                
                self.info_label = QLabel("Points: 0")
                status_layout.addWidget(self.info_label)
                
                layout.addWidget(status)
            
            def _update_status(self):
                count = len(self.points)
                self.info_label.setText(f"Points: {count}")
                
                if count == 0:
                    self.status_label.setText("Click to add first point")
                elif count < 3:
                    self.status_label.setText(f"Click to add point {count + 1}")
                elif not self.is_complete:
                    self.status_label.setText("Double-click to complete polygon")
                else:
                    self.status_label.setText("Polygon ready! Click 'Generate 3D Model' button")
            
            def set_scale(self, scale):
                self.scale_factor = scale
                self.update()
            
            def set_background_image(self, pixmap):
                self.background_pixmap = pixmap
                self.drawing_area.set_background(pixmap)
                self.zoom_fit()
                return True
            
            def clear_all(self):
                self.points.clear()
                self.is_drawing = False
                self.is_complete = False
                self.current_mouse_pos = None
                self._update_status()
                self.update()
                self.drawing_cleared.emit()
            
            def undo_point(self):
                if self.points:
                    self.points.pop()
                    if not self.points:
                        self.is_drawing = False
                        self.is_complete = False
                    self._update_status()
                    self.update()
            
            def zoom_fit(self):
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
            
            def calculate_polygon_area(self):
                if len(self.points) < 3:
                    return 0
                
                area = 0
                for i in range(len(self.points)):
                    j = (i + 1) % len(self.points)
                    area += self.points[i].x() * self.points[j].y()
                    area -= self.points[j].x() * self.points[i].y()
                
                area = abs(area) / 2
                real_area = area * (self.scale_factor ** 2)
                return real_area
            
            def get_polygon_measurements(self):
                return {
                    'points': len(self.points),
                    'area': self.calculate_polygon_area(),
                    'perimeter': 0.0,
                    'is_complete': self.is_complete
                }
            
            def create_3d_model(self, points=None):
                """MANUAL 3D model creation - called only from button"""
                if points is None:
                    points = self.points.copy()
                
                if len(points) < 3:
                    return False
                
                # Find the main window
                main_window = self
                while main_window and not hasattr(main_window, 'content_tabs'):
                    main_window = main_window.parent()
                
                if not main_window:
                    return False
                
                try:
                    # Get building parameters from left panel
                    height = 3.0
                    roof_type = 'Flat Roof'
                    
                    if hasattr(main_window, 'left_panel'):
                        if hasattr(main_window.left_panel, 'get_building_parameters'):
                            params = main_window.left_panel.get_building_parameters()
                            height = params.get('height', 3.0)
                            roof_type = params.get('roof_type', 'Flat Roof')
                    
                    # Get model tab
                    model_tab = main_window.content_tabs.widget(2)
                    if not model_tab:
                        return False
                    
                    # Create building
                    success = model_tab.create_building(points, height=height, roof_type=roof_type)
                    
                    if success:
                        # Switch to 3D model tab
                        main_window.content_tabs.setCurrentIndex(2)
                        if hasattr(main_window, 'statusBar'):
                            main_window.statusBar().showMessage("3D model generated!", 3000)
                        return True
                    
                    return False
                    
                except Exception as e:
                    return False
        
        return EmbeddedDrawingCanvas
    
    def create_canvas(self):
        """Create the DrawingCanvas instance"""
        try:
            if self.canvas_widget and self.canvas_initialized:
                return self.canvas_widget
            
            if self.DrawingCanvas:
                # Create the DrawingCanvas instance
                self.drawing_canvas = self.DrawingCanvas(self.main_window)
                
                # Get the drawing area
                if hasattr(self.drawing_canvas, 'drawing_area'):
                    self.drawing_area = self.drawing_canvas.drawing_area
                
                # Set initial size
                self.drawing_canvas.setMinimumSize(*self.actual_canvas_size)
                self.drawing_canvas.resize(*self.actual_canvas_size)
                
                # Connect signals
                self._connect_drawing_canvas_signals()
                
                # Set initial scale
                if hasattr(self.drawing_canvas, 'set_scale'):
                    self.drawing_canvas.set_scale(self.scale_factor)
                
                self.canvas_widget = self.drawing_canvas
                self.canvas_initialized = True
                
                self.canvas_ready.emit()
                
                return self.canvas_widget
            else:
                return self._create_error_placeholder()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._create_error_placeholder()
    
    def _connect_drawing_canvas_signals(self):
        """Connect signals from DrawingCanvas"""
        try:
            if hasattr(self.drawing_canvas, 'polygon_completed'):
                self.drawing_canvas.polygon_completed.connect(self._handle_polygon_completed)
            
            if hasattr(self.drawing_canvas, 'drawing_cleared'):
                self.drawing_canvas.drawing_cleared.connect(self._handle_drawing_cleared)
            
            if hasattr(self.drawing_canvas, 'generate_3d_model'):
                self.drawing_canvas.generate_3d_model.connect(self._handle_3d_generation)
                
        except Exception as e:
            pass
    
    def _handle_polygon_completed(self, points):
        """Handle polygon completion - ONLY enable button, no auto-generation"""
        self.boundary_completed.emit(points)
        
        if self.drawing_canvas and hasattr(self.drawing_canvas, 'calculate_polygon_area'):
            area = self.drawing_canvas.calculate_polygon_area()
            self.area_calculated.emit(area, f"{area:.2f}m²")
        
        # Emit signal but don't auto-generate
        self.drawing_completed.emit(points)
    
    def _handle_drawing_cleared(self):
        pass
    
    def _handle_3d_generation(self, points):
        pass
    
    def _create_error_placeholder(self):
        """Create error placeholder"""
        self.canvas_widget = QWidget()
        layout = QVBoxLayout(self.canvas_widget)
        
        label = QLabel("DrawingCanvas Creation Failed\nUsing embedded canvas")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 2px dashed #856404;
                border-radius: 8px;
                padding: 20px;
                color: #856404;
                font-size: 12px;
            }
        """)
        layout.addWidget(label)
        
        self.canvas_initialized = True
        return self.canvas_widget
    
    def get_canvas(self):
        """Get the DrawingCanvas instance"""
        if self.drawing_canvas:
            return self.drawing_canvas
        
        self.create_canvas()
        return self.drawing_canvas
    
    def process_screenshot(self, pixmap):
        """Process screenshot and apply to DrawingCanvas"""
        try:
            if pixmap.isNull():
                return False
            
            canvas = self.get_canvas()
            if not canvas:
                return False
            
            # Create enhanced pixmap
            enhanced_pixmap = self._create_enhanced_pixmap(pixmap)
            
            # Apply to DrawingCanvas
            if hasattr(canvas, 'set_background_image'):
                success = canvas.set_background_image(enhanced_pixmap)
                if success:
                    if hasattr(self.main_window, 'statusBar'):
                        self.main_window.statusBar().showMessage(
                            f"Screenshot captured! ({pixmap.width()}x{pixmap.height()})", 3000
                        )
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def _create_enhanced_pixmap(self, original_pixmap):
        """Create enhanced and centered pixmap"""
        try:
            canvas_width, canvas_height = self.actual_canvas_size
            
            # Scale to fit canvas
            scale = min(
                (canvas_width * 0.9) / original_pixmap.width(),
                (canvas_height * 0.9) / original_pixmap.height(),
                1.0
            )
            
            if scale < 1.0:
                scaled_pixmap = original_pixmap.scaled(
                    int(original_pixmap.width() * scale),
                    int(original_pixmap.height() * scale),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            else:
                scaled_pixmap = original_pixmap
            
            # Create canvas-sized pixmap
            canvas_pixmap = QPixmap(canvas_width, canvas_height)
            canvas_pixmap.fill(QColor(220, 220, 220))
            
            # Center the image
            x = (canvas_width - scaled_pixmap.width()) // 2
            y = (canvas_height - scaled_pixmap.height()) // 2
            
            from PyQt5.QtGui import QPainter
            painter = QPainter(canvas_pixmap)
            if self.enhance_screenshots:
                painter.setOpacity(self.enhancement_settings['transparency'])
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            return canvas_pixmap
            
        except Exception as e:
            return original_pixmap
    
    def set_background_image(self, pixmap):
        """Main background setting method"""
        return self.process_screenshot(pixmap)
    
    def clear_drawing(self):
        """Clear drawing"""
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, 'clear_all'):
            canvas.clear_all()
    
    def get_drawing_points(self):
        """Get drawing points"""
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, 'points'):
            return canvas.points.copy()
        return []
    
    def set_canvas_scale(self, scale):
        """Set canvas scale"""
        self.scale_factor = scale
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, 'set_scale'):
            canvas.set_scale(scale)
        self.scale_changed.emit(scale)
    
    def get_canvas_measurements(self):
        """Get measurements"""
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, 'get_polygon_measurements'):
            return canvas.get_polygon_measurements()
        return {'points': 0, 'area': 0.0, 'perimeter': 0.0}
    
    def generate_model_from_button(self):
        """Generate model from button press - manual control"""
        try:
            canvas = self.get_canvas()
            if canvas and hasattr(canvas, 'points') and len(canvas.points) >= 3:
                # Use create_3d_model method
                if hasattr(canvas, 'create_3d_model'):
                    return canvas.create_3d_model(canvas.points.copy())
            return False
        except:
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.drawing_canvas:
            try:
                self.drawing_canvas.deleteLater()
            except:
                pass
            self.drawing_canvas = None
        self.drawing_area = None
        self.canvas_widget = None