#!/usr/bin/env python3
"""
Theme Manager - Dark theme only
"""
from PyQt5.QtCore import QObject

class ThemeManager(QObject):
    """Manages application themes - Dark theme only"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
    
    @property
    def current_theme(self):
        """Always returns dark theme"""
        return "dark"
    
    def apply_theme(self):
        """Apply dark theme only"""
        try:
            # Always apply dark theme
            self.main_window.setStyleSheet(self._get_dark_style())
            
            # Update VTK plotter background if available
            if hasattr(self.main_window, 'content_tabs') and hasattr(self.main_window.content_tabs, 'model_tab'):
                model_tab = self.main_window.content_tabs.model_tab
                if hasattr(model_tab, 'plotter') and model_tab.plotter is not None:
                    # Always use dark theme background
                    model_tab.plotter.background_color = [0.25, 0.25, 0.25]
                    model_tab.plotter.update()
        except Exception as e:
            print(f"Warning: Theme application failed: {e}")
    
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
            color: white;
            font-weight: bold;
            font-size: 13px;
        }
        
        QPushButton#generateButton:hover:enabled {
            background-color: #c0392b;
            border-color: #a93226;
        }
        
        QPushButton#generateButton:pressed:enabled {
            background-color: #a93226;
            border-color: #922b21;
        }
        
        QPushButton#generateButton:disabled {
            background-color: #7f8c8d;
            border-color: #95a5a6;
            color: #bdc3c7;
        }
        
        /* Export Buttons */
        QPushButton#exportButton {
            background-color: #16a085;
            border: 1px solid #138d75;
            color: white;
            font-weight: bold;
        }
        
        QPushButton#exportButton:hover {
            background-color: #138d75;
        }
        
        QPushButton#exportButton:pressed {
            background-color: #117a65;
        }
        
        /* Line Edits */
        QLineEdit {
            background-color: #555555;
            color: #E0E0E0;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 13px;
        }
        
        QLineEdit:focus {
            border-color: #62B5F6;
            background-color: #444444;
        }
        
        QLineEdit:disabled {
            background-color: #3d3d3d;
            color: #999999;
            border-color: #555555;
        }
        
        /* Spin Boxes */
        QSpinBox, QDoubleSpinBox {
            background-color: #555555;
            color: #E0E0E0;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 4px 6px;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #62B5F6;
        }
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            background-color: #666666;
            border: 1px solid #777777;
            border-radius: 2px;
        }
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            background-color: #666666;
            border: 1px solid #777777;
            border-radius: 2px;
        }
        
        /* Text Edits */
        QTextEdit, QPlainTextEdit {
            background-color: #444444;
            color: #E0E0E0;
            border: 1px solid #666666;
            border-radius: 4px;
        }
        
        QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #62B5F6;
        }
        
        /* Tab Widgets */
        QTabWidget {
            border: none;
            background-color: #4A4A4A;
        }
        
        QTabWidget::pane {
            border: 1px solid #666666;
            border-radius: 4px;
            background-color: #4A4A4A;
        }
        
        QTabBar {
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
        
        /* Check Boxes */
        QCheckBox {
            color: #E0E0E0;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #666666;
            border-radius: 2px;
            background-color: #555555;
        }
        
        QCheckBox::indicator:checked {
            background-color: #62B5F6;
            border-color: #0A58CA;
        }
        
        /* Radio Buttons */
        QRadioButton {
            color: #E0E0E0;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #666666;
            border-radius: 8px;
            background-color: #555555;
        }
        
        QRadioButton::indicator:checked {
            background-color: #62B5F6;
            border-color: #0A58CA;
        }
        
        /* Progress Bars */
        QProgressBar {
            border: 1px solid #666666;
            background-color: #444444;
            color: #E0E0E0;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #62B5F6;
            border-radius: 3px;
        }
        
        /* Scroll Bars */
        QScrollBar:vertical {
            background-color: #555555;
            width: 16px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #888888;
            border-radius: 8px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #aaaaaa;
        }
        
        QScrollBar:horizontal {
            background-color: #555555;
            height: 16px;
            border: none;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #888888;
            border-radius: 8px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #aaaaaa;
        }
        
        /* Tree Widgets */
        QTreeWidget {
            background-color: #444444;
            color: #E0E0E0;
            border: 1px solid #666666;
            alternate-background-color: #4A4A4A;
        }
        
        QTreeWidget::item:selected {
            background-color: #0A58CA;
        }
        
        QTreeWidget::item:hover {
            background-color: #555555;
        }
        
        /* List Widgets */
        QListWidget {
            background-color: #444444;
            color: #E0E0E0;
            border: 1px solid #666666;
            alternate-background-color: #4A4A4A;
        }
        
        QListWidget::item:selected {
            background-color: #0A58CA;
        }
        
        QListWidget::item:hover {
            background-color: #555555;
        }
        
        /* Table Widgets */
        QTableWidget {
            background-color: #444444;
            color: #E0E0E0;
            border: 1px solid #666666;
            gridline-color: #666666;
            alternate-background-color: #4A4A4A;
        }
        
        QTableWidget::item:selected {
            background-color: #0A58CA;
        }
        
        QTableWidget::item:hover {
            background-color: #555555;
        }
        
        QHeaderView::section {
            background-color: #555555;
            color: #E0E0E0;
            border: 1px solid #666666;
            padding: 4px;
        }
        """