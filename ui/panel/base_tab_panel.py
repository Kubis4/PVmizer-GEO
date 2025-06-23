#!/usr/bin/env python3
"""
Base Tab Panel - Common functionality for all tab panels with blue theme
"""
from PyQt5.QtWidgets import QWidget, QGroupBox, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BaseTabPanel(QWidget):
    """Base class for all tab panels with consistent blue styling"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Setup UI immediately
        self.setup_ui()
        
        # Apply base styling
        self._apply_base_styling()
    
    def setup_ui(self):
        """Override this method in subclasses to setup specific UI"""
        pass
    
    def _apply_base_styling(self):
        """Apply base blue theme styling to the panel"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
    
    def create_group_box(self, title, icon=""):
        """Create a styled group box with blue theme"""
        group_box = QGroupBox(f"{icon} {title}" if icon else title)
        
        # Apply blue-themed styling
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: -8px;
                background-color: #3498db;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        # Set font
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        group_box.setFont(font)
        
        return group_box
    
    def create_blue_button_style(self, base_color="#3498db", hover_color="#2980b9", pressed_color="#1f618d"):
        """Create blue button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
                color: #7f8c8d;
            }}
        """
    
    def create_input_style(self, border_color="#3498db"):
        """Create input field stylesheet with blue theme"""
        return f"""
            QDoubleSpinBox, QSpinBox, QComboBox {{
                background-color: white;
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                color: #2c3e50;
                min-height: 20px;
            }}
            QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
                margin-right: 5px;
            }}
        """
    
    def cleanup(self):
        """Cleanup resources - override in subclasses if needed"""
        self.main_window = None