#!/usr/bin/env python3
"""
Google Maps Tab - Deferred loading for safe initialization
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap

class MapsTab(QWidget):
    """Google Maps tab with deferred loading"""
    
    maps_loaded = pyqtSignal()
    maps_error = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.satellite_view = None
        self.maps_loaded_flag = False
        
        self._setup_ui()
        self._schedule_auto_load()
    
    def _setup_ui(self):
        """Setup initial UI with placeholder"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.placeholder = QLabel(
            "🗺️ Google Maps\n\n"
            "Loading maps safely...\n"
            "Maps will load automatically in 3 seconds\n\n"
            "(Click here to load immediately)"
        )
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                padding: 40px;
                border: 2px dashed #3498db;
                border-radius: 8px;
                background-color: #ecf0f1;
                min-height: 200px;
            }
            QLabel:hover {
                background-color: #d5e8f3;
                border-color: #2980b9;
                cursor: pointer;
            }
        """)
        
        self.placeholder.mousePressEvent = lambda event: self.load_maps()
        self.layout.addWidget(self.placeholder)
    
    def _schedule_auto_load(self):
        """Schedule automatic maps loading"""
        QTimer.singleShot(3000, self.load_maps)
    
    def load_maps(self):
        """Load Google Maps"""
        if self.maps_loaded_flag:
            return
            
        try:
            # Remove placeholder
            if self.placeholder:
                self.layout.removeWidget(self.placeholder)
                self.placeholder.deleteLater()
                self.placeholder = None
            
            # Create maps view
            self.satellite_view = QWebEngineView()
            maps_url = "https://www.google.com/maps/@48.3084263,18.0875649,15.96z/data=!3m1!1e3"
            self.satellite_view.setMinimumSize(800, 600)
            self.satellite_view.setUrl(QUrl(maps_url))
            
            self.layout.addWidget(self.satellite_view)
            self.maps_loaded_flag = True
            
            self.maps_loaded.emit()
            
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Google Maps loaded successfully!", 3000)
                
        except Exception as e:
            self._create_error_message(str(e))
            self.maps_error.emit(str(e))
    
    def _create_error_message(self, error_msg):
        """Create error message for failed loading"""
        try:
            error_label = QLabel(
                f"🗺️ Google Maps\n\n"
                f"Error loading maps:\n{error_msg}\n\n"
                f"You can continue using other features.\n"
                f"Try refreshing or check your internet connection."
            )
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            error_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 14px;
                    padding: 40px;
                    border: 2px solid #e74c3c;
                    border-radius: 8px;
                    background-color: #fadbd8;
                }
            """)
            self.layout.addWidget(error_label)
        except Exception as e:
            pass
    
    def is_loaded(self):
        """Check if maps are loaded"""
        return self.maps_loaded_flag
    
    def get_maps_view(self):
        """Get the maps view widget"""
        return self.satellite_view