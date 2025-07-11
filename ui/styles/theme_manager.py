#!/usr/bin/env python3
"""
Theme Manager - Refined design with standard export button and dark popups
"""
from PyQt5.QtCore import QObject

class ThemeManager(QObject):
    """Manages application themes with enhanced styling"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
    
    @property
    def current_theme(self):
        """Get current theme name"""
        return "dark" if self.main_window.config.dark_theme else "light"
    
    def apply_theme(self):
        """Apply current theme with enhanced styling"""
        try:
            if self.main_window.config.dark_theme:
                self.main_window.setStyleSheet(self._get_dark_style())
            else:
                self.main_window.setStyleSheet(self._get_light_style())
            
            # Update VTK plotter background if available
            if hasattr(self.main_window, 'content_tabs') and hasattr(self.main_window.content_tabs, 'model_tab'):
                model_tab = self.main_window.content_tabs.model_tab
                if hasattr(model_tab, 'plotter') and model_tab.plotter is not None:
                    if self.main_window.config.dark_theme:
                        model_tab.plotter.background_color = [0.25, 0.25, 0.25]
                    else:
                        model_tab.plotter.background_color = [0.95, 0.95, 0.95]
                    model_tab.plotter.update()
        except Exception as e:
            print(f"Warning: Theme application failed: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.main_window.config.dark_theme = not self.main_window.config.dark_theme
        self.apply_theme()
        theme_name = "Dark" if self.main_window.config.dark_theme else "Light"
        self.main_window.statusBar().showMessage(f"Switched to {theme_name} theme")
    
    def _get_dark_style(self):
        """Enhanced dark theme style"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        /* Left Menu Panel */
        #leftMenu {
            background-color: #2c3e50;
            border: none;
            border-right: 2px solid #34495e;
        }
        
        #menuTitle {
            color: #ecf0f1;
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background-color: #34495e;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        /* Group Boxes */
        QGroupBox {
            border: 2px solid #34495e;
            border-radius: 12px;
            margin-top: 1ex;
            padding: 20px 15px 15px 15px;
            font-weight: bold;
            color: #ecf0f1;
            background-color: #34495e;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 8px 15px;
            background-color: #2c3e50;
            color: #3498db;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
        }
        
        /* Tips Group - Special styling for dark theme */
        QGroupBox#tipsGroup {
            border: 2px solid #7f8c8d;
            background-color: #34495e;
            color: #bdc3c7;
        }
        
        QGroupBox#tipsGroup::title {
            color: #f39c12;
            background-color: #2c3e50;
        }
        
        /* Collapsible Tips Button */
        QPushButton#tipsToggle {
            background-color: #7f8c8d;
            color: #ecf0f1;
            border: 1px solid #95a5a6;
            font-size: 11px;
            padding: 8px 16px;
        }
        
        QPushButton#tipsToggle:hover {
            background-color: #95a5a6;
        }
        
        QPushButton#tipsToggle:checked {
            background-color: #f39c12;
            border-color: #e67e22;
            color: #2c3e50;
        }
        
        /* Buttons - Standard styling */
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #21618c;
        }
        
        QPushButton:disabled {
            background-color: #7f8c8d;
            color: #bdc3c7;
        }
        
        QPushButton:checked {
            background-color: #27ae60;
            border: 2px solid #2ecc71;
        }
        
        QPushButton#generateButton:enabled {
            background-color: #e74c3c;
            border: 2px solid #c0392b;
            font-size: 13px;
            font-weight: bold;
        }
        
        QPushButton#generateButton:enabled:hover {
            background-color: #c0392b;
            border-color: #a93226;
        }
        
        /* Export Button - Standard blue styling (not orange) */
        QPushButton#exportButton {
            background-color: #3498db;
            border: 2px solid #2980b9;
            font-size: 13px;
            font-weight: bold;
            color: white;
        }
        
        QPushButton#exportButton:hover {
            background-color: #2980b9;
            border-color: #21618c;
        }
        
        QPushButton#exportButton:pressed {
            background-color: #21618c;
        }
        
        /* Message Boxes - Dark theme for popups */
        QMessageBox {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        
        QMessageBox QLabel {
            color: #ecf0f1;
            background-color: transparent;
        }
        
        QMessageBox QPushButton {
            background-color: #3498db;
            color: white;
            border: 1px solid #2980b9;
            border-radius: 6px;
            padding: 8px 16px;
            min-width: 80px;
        }
        
        QMessageBox QPushButton:hover {
            background-color: #2980b9;
        }
        
        QMessageBox QPushButton:pressed {
            background-color: #21618c;
        }
        
        /* Toolbar */
        QToolBar {
            background-color: #2c3e50;
            border-bottom: 2px solid #34495e;
            spacing: 10px;
            padding: 8px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            color: #ecf0f1;
            padding: 8px 12px;
            margin: 2px;
            font-weight: bold;
        }
        
        QToolBar QToolButton:hover {
            background-color: #34495e;
            border-color: #3498db;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #3498db;
        }
        
        QToolBar QToolButton::menu-indicator {
            image: none;
        }
        
        /* Tab Widget */
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
        
        /* Combo Boxes */
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
        
        /* Sliders */
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
        
        /* Labels */
        QLabel {
            color: #E0E0E0;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #343a40;
            color: #E0E0E0;
            border-top: 1px solid #333333;
        }
        """
    
    def _get_light_style(self):
        """Enhanced light theme style"""
        return """
        QMainWindow {
            background-color: #f8f9fa;
            color: #212529;
        }
        
        /* Left Menu Panel */
        #leftMenu {
            background-color: #ffffff;
            border: none;
            border-right: 2px solid #e9ecef;
        }
        
        #menuTitle {
            color: #495057;
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        /* Group Boxes */
        QGroupBox {
            border: 2px solid #dee2e6;
            border-radius: 12px;
            margin-top: 1ex;
            padding: 20px 15px 15px 15px;
            background-color: #ffffff;
            font-weight: bold;
            color: #495057;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 8px 15px;
            background-color: #f8f9fa;
            color: #0d6efd;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
        }
        
        /* Tips Group - Special styling for light theme */
        QGroupBox#tipsGroup {
            border: 2px solid #dee2e6;
            background-color: #f8f9fa;
            color: #6c757d;
        }
        
        QGroupBox#tipsGroup::title {
            color: #fd7e14;
            background-color: #ffffff;
        }
        
        /* Collapsible Tips Button */
        QPushButton#tipsToggle {
            background-color: #6c757d;
            color: white;
            border: 1px solid #5a6268;
            font-size: 11px;
            padding: 8px 16px;
        }
        
        QPushButton#tipsToggle:hover {
            background-color: #5a6268;
        }
        
        QPushButton#tipsToggle:checked {
            background-color: #fd7e14;
            border-color: #e76707;
            color: white;
        }
        
        /* Buttons - Standard styling */
        QPushButton {
            background-color: #0d6efd;
            color: white;
            border: 1px solid #0d6efd;
            border-radius: 8px;
            padding: 12px 20px;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }
        
        QPushButton:pressed {
            background-color: #0a58ca;
            border-color: #0653c4;
        }
        
        QPushButton:disabled {
            background-color: #6c757d;
            border-color: #6c757d;
            color: #fff;
        }
        
        QPushButton:checked {
            background-color: #198754;
            border-color: #157347;
        }
        
        QPushButton#generateButton:enabled {
            background-color: #dc3545;
            border: 2px solid #bb2d3b;
            font-size: 13px;
            font-weight: bold;
        }
        
        QPushButton#generateButton:enabled:hover {
            background-color: #bb2d3b;
            border-color: #a02834;
        }
        
        /* Export Button - Standard blue styling */
        QPushButton#exportButton {
            background-color: #0d6efd;
            border: 2px solid #0b5ed7;
            font-size: 13px;
            font-weight: bold;
            color: white;
        }
        
        QPushButton#exportButton:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }
        
        QPushButton#exportButton:pressed {
            background-color: #0a58ca;
        }
        
        /* Message Boxes - Standard light theme */
        QMessageBox {
            background-color: #ffffff;
            color: #212529;
        }
        
        QMessageBox QLabel {
            color: #212529;
            background-color: transparent;
        }
        
        QMessageBox QPushButton {
            background-color: #0d6efd;
            color: white;
            border: 1px solid #0b5ed7;
            border-radius: 6px;
            padding: 8px 16px;
            min-width: 80px;
        }
        
        QMessageBox QPushButton:hover {
            background-color: #0b5ed7;
        }
        
        /* Toolbar */
        QToolBar {
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            spacing: 10px;
            padding: 8px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            color: #495057;
            padding: 8px 12px;
            margin: 2px;
            font-weight: bold;
        }
        
        QToolBar QToolButton:hover {
            background-color: #e9ecef;
            border-color: #0d6efd;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #0d6efd;
            color: white;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: none;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f8f9fa;
            border: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 100px;
            color: #6c757d;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #0d6efd;
            font-weight: bold;
            border-bottom: 2px solid #0d6efd;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #e9ecef;
        }
        
        /* Combo Boxes */
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 4px 8px;
            min-width: 6em;
            background-color: #ffffff;
            color: #495057;
        }
        
        QComboBox:hover {
            border-color: #0d6efd;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 20px;
            border-left: none;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #495057;
            selection-background-color: #0d6efd;
            selection-color: white;
        }
        
        /* Sliders */
        QSlider::groove:horizontal {
            border: 1px solid #ced4da;
            background: #f8f9fa;
            height: 8px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #0d6efd;
            border: 1px solid #0d6efd;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #0b5ed7;
        }
        
        /* Labels */
        QLabel {
            color: #495057;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #f8f9fa;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
        """
