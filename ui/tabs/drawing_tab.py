#!/usr/bin/env python3
"""
Drawing Tab - Canvas for building outline drawing
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap

class DrawingTab(QWidget):
    """Drawing tab with canvas for building outline"""
    
    canvas_ready = pyqtSignal()
    canvas_error = pyqtSignal(str)
    drawing_completed = pyqtSignal(list)
    
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
        
        self._setup_ui()
        self._schedule_canvas_operations()
    
    def _setup_ui(self):
        """Setup drawing tab UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        # Set initial size
        self.setMinimumSize(self.target_width, self.target_height)
        self.resize(self.target_width, self.target_height)
        
        # Try to create canvas immediately
        if not self._create_canvas():
            self._create_placeholder()
    
    def _create_canvas(self):
        """Create drawing canvas"""
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
                self.layout.addWidget(self.drawing_canvas)
                self.canvas_properly_sized = True
                self.canvas_ready.emit()
                return True
                
        except Exception as e:
            self.canvas_error.emit(str(e))
            return False
        
        return False
    
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
                print("✅ Canvas created successfully on retry")
            else:
                print("❌ Canvas creation failed on retry")
                
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
        """Get current drawing points"""
        try:
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
