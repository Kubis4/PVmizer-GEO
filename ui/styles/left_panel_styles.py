#!/usr/bin/env python3
"""
Centralized Styles for PVmizer GEO Application
All CSS styles organized by component type
"""

def get_dark_theme_style():
    """Return the CSS for dark theme"""
    return """
        QMainWindow, QWidget {
            background-color: #4A4A4A;
            color: #E0E0E0;
        }
        
        #leftMenu {
            background-color: #343a40;
            border: none;
        }
        
        #menuTitle {
            color: #E0E0E0;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        }
        
        QGroupBox {
            border: 1px solid #666666;
            border-radius: 4px;
            margin-top: 16px;
            font-weight: bold;
            color: #E0E0E0;
        }
        
        #leftMenu QGroupBox {
            background-color: #343a40;
            border-color: #495057;
        }
        
        #leftMenu QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 5px;
            color: #62B5F6;
        }
        
        QPushButton {
            background-color: #0D6EFD;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            text-align: left;
        }
        
        QPushButton:hover {
            background-color: #0B5ED7;
        }
        
        QPushButton:pressed {
            background-color: #0A58CA;
        }
        
        QPushButton:disabled {
            background-color: #6C757D;
            color: #C0C0C0;
        }
        
        QToolBar {
            background-color: #404040;
            border-bottom: 1px solid #333333;
            spacing: 5px;
            padding: 2px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 4px;
            color: #E0E0E0;
            padding: 4px;
            margin: 1px;
        }
        
        QToolBar QToolButton:hover {
            background-color: #505050;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #606060;
        }
        
        QTabWidget::pane {
            border: none;
            background-color: #4A4A4A;
        }
        
        QTabBar::tab {
            background-color: #343a40;
            border: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 100px;
            color: #CCCCCC;
        }
        
        QTabBar::tab:selected {
            background-color: #4A4A4A;
            color: #62B5F6;
            font-weight: bold;
            border-bottom: 2px solid #62B5F6;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #404040;
        }
        
        QComboBox {
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px 8px;
            min-width: 6em;
            background-color: #555555;
            color: #E0E0E0;
        }
        
        QComboBox:hover {
            border-color: #62B5F6;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 20px;
            border-left: none;
        }
        
        QComboBox QAbstractItemView {
            background-color: #555555;
            color: #E0E0E0;
            selection-background-color: #0A58CA;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #666666;
            background: #404040;
            height: 8px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #62B5F6;
            border: 1px solid #62B5F6;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #0A58CA;
        }
        
        QLabel {
            color: #E0E0E0;
        }
        
        QStatusBar {
            background-color: #343a40;
            color: #E0E0E0;
            border-top: 1px solid #333333;
        }
    """

def get_light_theme_style():
    """Return the CSS for light theme"""
    return """
        QMainWindow, QWidget {
            background-color: #FFFFFF;
            color: #333333;
        }
        
        #leftMenu {
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
        }
        
        #menuTitle {
            color: #2196F3;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        }
        
        QGroupBox {
            border: 1px solid #DDDDDD;
            border-radius: 4px;
            margin-top: 16px;
            font-weight: bold;
            color: #333333;
        }
        
        #leftMenu QGroupBox {
            background-color: #FFFFFF;
        }
        
        #leftMenu QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 5px;
            color: #2196F3;
        }
        
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px;
            text-align: left;
        }
        
        QPushButton:hover {
            background-color: #1976D2;
        }
        
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #757575;
        }
        
        QToolBar {
            background-color: #F5F5F5;
            border-bottom: 1px solid #E0E0E0;
            spacing: 5px;
            padding: 2px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 4px;
            color: #444;
            padding: 4px;
            margin: 1px;
        }
        
        QToolBar QToolButton:hover {
            background-color: #E0E0E0;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #CCCCCC;
        }
        
        QTabWidget::pane {
            border: none;
            background-color: #FFFFFF;
        }
        
        QTabBar::tab {
            background-color: #F5F5F5;
            border: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 100px;
            color: #666;
        }
        
        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #2196F3;
            font-weight: bold;
            border-bottom: 2px solid #2196F3;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #EEEEEE;
        }
        
        QComboBox {
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            padding: 4px 8px;
            min-width: 6em;
            background-color: white;
            color: #333333;
        }
        
        QComboBox:hover {
            border-color: #2196F3;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 20px;
            border-left: none;
        }
        
        QComboBox QAbstractItemView {
            background-color: white;
            selection-background-color: #2196F3;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #CCCCCC;
            background: #F5F5F5;
            height: 8px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #2196F3;
            border: 1px solid #2196F3;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #1976D2;
        }
        
        QLabel {
            color: #444;
        }
        
        QStatusBar {
            background-color: #F8F9FA;
            color: #666;
            border-top: 1px solid #E0E0E0;
        }
    """

# ============================================================================
# MODEL 3D TAB PANEL SPECIFIC STYLES
# ============================================================================

def get_model3d_white_label_style():
    """White text labels for Model3D panel"""
    return """
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 12px;
        }
    """

def get_model3d_input_style():
    """Input controls style for Model3D panel"""
    return """
        QDoubleSpinBox, QSpinBox {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 4px 8px;
            background-color: white;
            color: #2c3e50;
            font-size: 12px;
        }
        QDoubleSpinBox:focus, QSpinBox:focus {
            border-color: #3498db;
        }
    """

def get_model3d_combo_style():
    """ComboBox style for Model3D panel"""
    return """
        QComboBox {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 4px 8px;
            background-color: white;
            color: #2c3e50;
            font-size: 12px;
        }
        QComboBox:focus {
            border-color: #3498db;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
    """

def get_model3d_slider_style(slider_type="building"):
    """Slider styles for Model3D panel"""
    if slider_type == "building":
        return """
            QSlider::groove:horizontal {
                border: 1px solid #dee2e6;
                background: #f8f9fa;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #3498db;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
        """
    elif slider_type == "solar":
        return """
            QSlider::groove:horizontal {
                border: 1px solid #dee2e6;
                background: #f8f9fa;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #f39c12;
                border: 1px solid #f39c12;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #e67e22;
            }
        """
    
    return get_model3d_slider_style("building")

def get_model3d_button_style(button_type="default"):
    """Button styles for Model3D panel"""
    
    if button_type == "animation":
        return """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """
    
    elif button_type == "solar_config":
        return """
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
            }
            QPushButton:hover:enabled {
                background-color: #138496;
            }
            QPushButton:pressed:enabled {
                background-color: #117a8b;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """
    
    elif button_type == "obstacle":
        return """
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 12px;
            }
            QPushButton:hover:enabled {
                background-color: #5a32a3;
            }
            QPushButton:pressed:enabled {
                background-color: #4e2a8e;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """
    
    elif button_type == "export":
        return """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
                text-align: center;
            }
            QPushButton:hover:enabled {
                background-color: #218838;
            }
            QPushButton:pressed:enabled {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """
    
    # Default button style
    return """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            padding: 8px 12px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QPushButton:disabled {
            background-color: #6c757d;
            color: #adb5bd;
        }
    """

def get_model3d_info_label_style():
    """Info label style for Model3D panel"""
    return """
        QLabel {
            color: #adb5bd;
            font-size: 11px;
            font-style: italic;
        }
    """

def get_model3d_help_label_style():
    """Help label style for Model3D panel"""
    return """
        QLabel {
            color: #28a745;
            font-size: 10px;
        }
    """

def get_model3d_error_label_style():
    """Error label style for Model3D panel"""
    return """
        QLabel {
            color: #dc3545;
            font-size: 10px;
        }
    """

# ============================================================================
# DIALOG STYLES FOR CONSISTENCY
# ============================================================================

def get_dialog_button_style(button_type="ok"):
    """Dialog button styles matching the application design"""
    
    if button_type == "ok":
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-height: 40px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    elif button_type == "cancel":
        return """
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                min-height: 40px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
            }
        """
    
    # Default button style
    return get_dialog_button_style("ok")

def get_dialog_input_style():
    """Dialog input field styles"""
    return """
        QLineEdit, QSpinBox, QDoubleSpinBox {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 4px 8px;
            background-color: white;
            color: #2c3e50;
            font-size: 12px;
        }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #3498db;
        }
    """

def get_dialog_combo_style():
    """Dialog ComboBox styles"""
    return """
        QComboBox {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 4px 8px;
            background-color: white;
            color: #2c3e50;
            font-size: 12px;
        }
        QComboBox:focus {
            border-color: #3498db;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
    """

# ============================================================================
# EXISTING STYLES (KEPT FOR COMPATIBILITY)
# ============================================================================

def get_checkbox_style(is_dark_theme=False):
    """Enhanced checkbox style with better visibility"""
    if is_dark_theme:
        return """
            QCheckBox {
                font-weight: bold;
                font-size: 14px;
                padding: 12px 16px;
                border-radius: 8px;
                border: 2px solid #3498db;
                background-color: #34495e;
                color: #ecf0f1;
                margin: 4px 0px;
            }
            QCheckBox:checked {
                background-color: #3498db;
                color: white;
                border-color: #2980b9;
            }
            QCheckBox:hover {
                border-color: #2980b9;
                background-color: #2c3e50;
            }
            QCheckBox:checked:hover {
                background-color: #2980b9;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #3498db;
                background-color: #2c3e50;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                border-color: white;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #ecf0f1;
            }
        """
    else:
        return """
            QCheckBox {
                font-weight: bold;
                font-size: 14px;
                padding: 12px 16px;
                border-radius: 8px;
                border: 2px solid #3498db;
                background-color: #ecf0f1;
                color: #2c3e50;
                margin: 4px 0px;
            }
            QCheckBox:checked {
                background-color: #3498db;
                color: white;
                border-color: #2980b9;
            }
            QCheckBox:hover {
                border-color: #2980b9;
                background-color: #d5dbdb;
            }
            QCheckBox:checked:hover {
                background-color: #2980b9;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #3498db;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                border-color: white;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #ecf0f1;
            }
        """

def get_text_area_style(is_dark_theme=False):
    """Text area style for measurements display"""
    if is_dark_theme:
        return """
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 12px;
                margin: 0px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """
    else:
        return """
            QTextEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 12px;
                margin: 0px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """

def get_drawing_tab_background_style(is_dark_theme=False):
    """Drawing tab main background style"""
    if is_dark_theme:
        return """
            QFrame {
                background-color: #34495e !important;
                border: none;
            }
            QFrame > QWidget {
                background-color: #34495e !important;
            }
            QStackedWidget > QFrame {
                background-color: #34495e !important;
            }
            QTabWidget::pane {
                background-color: #34495e !important;
            }
        """
    else:
        return """
            QFrame {
                background-color: #f8f9fa !important;
                border: none;
            }
            QFrame > QWidget {
                background-color: #f8f9fa !important;
            }
            QStackedWidget > QFrame {
                background-color: #f8f9fa !important;
            }
            QTabWidget::pane {
                background-color: #f8f9fa !important;
            }
        """

def get_content_tabs_background_style(is_dark_theme=False):
    """Content tabs background"""
    if is_dark_theme:
        return """
            QTabWidget::pane {
                background-color: #34495e !important;
                border: 1px solid #2c3e50;
            }
            QTabWidget > QFrame {
                background-color: #34495e !important;
            }
            QWidget[objectName="drawing_tab"] {
                background-color: #34495e !important;
            }
        """
    else:
        return """
            QTabWidget::pane {
                background-color: #ffffff !important;
                border: 1px solid #dee2e6;
            }
            QTabWidget > QFrame {
                background-color: #ffffff !important;
            }
            QWidget[objectName="drawing_tab"] {
                background-color: #ffffff !important;
            }
        """

def get_canvas_area_background_style(is_dark_theme=False):
    """Canvas drawing area background"""
    if is_dark_theme:
        return """
            QWidget {
                background-color: #95a5a6 !important;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
            }
        """
    else:
        return """
            QWidget {
                background-color: #ffffff !important;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """

def get_primary_button_style(button_type="default", is_dark_theme=False):
    """Primary button styles for different button types"""
    
    if button_type == "snip":
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    elif button_type == "generate":
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover:enabled {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
            QPushButton:enabled {
                background-color: #27ae60;
            }
            QPushButton:enabled:hover {
                background-color: #229954;
            }
        """
    
    elif button_type == "export":
        return """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
    
    # Default button style
    return """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
    """

def get_small_button_style(is_dark_theme=False):
    """Small button style for undo/clear buttons"""
    if is_dark_theme:
        return """
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
                border-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
                border-color: #2980b9;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
                border-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
                border-color: #2980b9;
            }
        """

def get_tips_style(is_dark_theme=False):
    """Tips section label style"""
    if is_dark_theme:
        return """
            QLabel {
                font-style: italic; 
                font-size: 12px; 
                padding: 8px;
                line-height: 1.4;
                color: #ecf0f1;
                background-color: transparent;
            }
        """
    else:
        return """
            QLabel {
                font-style: italic; 
                font-size: 12px; 
                padding: 8px;
                line-height: 1.4;
                color: #7f8c8d;
                background-color: transparent;
            }
        """

def get_combobox_style(is_dark_theme=False):
    """Combobox style for scale input"""
    if is_dark_theme:
        return """
            QComboBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border: none;
                width: 12px;
                height: 12px;
            }
        """
    else:
        return """
            QComboBox {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border: none;
                width: 12px;
                height: 12px;
            }
        """

def get_slider_style(is_dark_theme=False):
    """Slider style for roof parameters"""
    if is_dark_theme:
        return """
            QSlider::groove:horizontal {
                border: 1px solid #2c3e50;
                height: 6px;
                background-color: #34495e;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #3498db;
                border: 1px solid #2980b9;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background-color: #2980b9;
            }
            QSlider::sub-page:horizontal {
                background-color: #3498db;
                border-radius: 3px;
            }
        """
    else:
        return """
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 6px;
                background-color: #ecf0f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #3498db;
                border: 1px solid #2980b9;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background-color: #2980b9;
            }
            QSlider::sub-page:horizontal {
                background-color: #3498db;
                border-radius: 3px;
            }
        """

def get_groupbox_style(is_dark_theme=False):
    """Group box style for sections"""
    if is_dark_theme:
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #3498db;
            }
        """
    else:
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #3498db;
            }
        """

def get_label_style(is_dark_theme=False):
    """Label style for parameters"""
    if is_dark_theme:
        return """
            QLabel {
                color: #ecf0f1;
                background-color: transparent;
                font-size: 12px;
            }
        """
    else:
        return """
            QLabel {
                color: #2c3e50;
                background-color: transparent;
                font-size: 12px;
            }
        """
