#!/usr/bin/env python3
"""
Complete Left Panel Styles - Add this function to your left_panel_styles.py file
"""

def get_left_panel_complete_style():
    """Complete styling for left control panel - single theme"""
    return """
        /* Main Panel Background */
        QFrame#leftControlPanel {
            background-color: #3a4f5c;
            border: none;
        }
        
        /* Title Box */
        QWidget#titleBox {
            background-color: #34495e;
            border: 2px solid #5dade2;
            border-radius: 8px;
        }
        
        QLabel#titleLabel {
            color: #5dade2;
            background-color: transparent;
            border: none;
            font-weight: bold;
        }
        
        /* Scroll Area */
        QScrollArea#controlsScrollArea {
            background-color: transparent;
            border: none;
        }
        
        QScrollBar:vertical {
            background-color: #2c3e50;
            width: 12px;
            border-radius: 6px;
            border: 1px solid #5dade2;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #5dade2;
            border-radius: 5px;
            min-height: 30px;
            margin: 1px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #48a1d6;
        }
        
        QScrollBar::add-line:vertical, 
        QScrollBar::sub-line:vertical {
            background: none;
            border: none;
            height: 0px;
        }
        
        QScrollBar::add-page:vertical, 
        QScrollBar::sub-page:vertical {
            background: none;
        }
        
        /* Controls Container */
        QGroupBox#controlsContainer {
            background-color: #34495e;
            border: 2px solid #5dade2;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 15px;
            padding-left: 10px;
            padding-right: 10px;
            padding-bottom: 10px;
            font-weight: bold;
            font-size: 13px;
            color: #ffffff;
        }
        
        QGroupBox#controlsContainer::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 4px 15px;
            margin-top: -12px;
            color: #5dade2;
            background-color: #34495e;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 0px;
        }
        
        /* Stacked Widget */
        QStackedWidget#tabStackedWidget {
            background-color: transparent;
            border: none;
        }
        
        /* Enhanced Button Styling with Outlines and Animations */
        QPushButton {
            background-color: #34495e;
            color: #ffffff;
            border: 2px solid #5dade2;
            border-radius: 6px;
            padding: 8px 12px;
            font-weight: bold;
            font-size: 13px;
            min-height: 32px;
            text-align: center;
        }
        
        QPushButton:hover {
            background-color: #5dade2;
            border: 2px solid #5dade2;
            color: #ffffff;
        }
        
        QPushButton:pressed {
            background-color: #48a1d6;
            border: 2px solid #48a1d6;
            color: #ffffff;
            padding: 9px 11px 7px 13px;
        }
        
        QPushButton:checked {
            background-color: #e74c3c;
            border: 2px solid #e74c3c;
            color: #ffffff;
        }
        
        QPushButton:checked:hover {
            background-color: #c0392b;
            border: 2px solid #c0392b;
        }
        
        QPushButton:disabled {
            background-color: #7f8c8d;
            border: 2px solid #7f8c8d;
            color: #95a5a6;
        }
        
        QPushButton:focus {
            border: 3px solid #2980b9;
            outline: none;
        }
        
        /* Generate Button - Red with outline */
        QPushButton#generateButton:enabled {
            background-color: #34495e;
            border: 2px solid #e74c3c;
            color: #e74c3c;
            font-size: 13px;
            font-weight: bold;
        }
        
        QPushButton#generateButton:enabled:hover {
            background-color: #e74c3c;
            border: 2px solid #e74c3c;
            color: #ffffff;
        }
        
        QPushButton#generateButton:enabled:pressed {
            background-color: #c0392b;
            border: 2px solid #c0392b;
            color: #ffffff;
        }
        
        /* Export Button - Green with outline */
        QPushButton#exportButton {
            background-color: #34495e;
            border: 2px solid #27ae60;
            color: #27ae60;
            font-size: 13px;
            font-weight: bold;
        }
        
        QPushButton#exportButton:hover {
            background-color: #27ae60;
            border: 2px solid #27ae60;
            color: #ffffff;
        }
        
        QPushButton#exportButton:pressed {
            background-color: #229954;
            border: 2px solid #229954;
            color: #ffffff;
        }
        
        /* Small Buttons */
        QPushButton.smallButton {
            background-color: #34495e;
            border: 2px solid #5dade2;
            border-radius: 5px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: bold;
            min-height: 28px;
            color: #ffffff;
        }
        
        QPushButton.smallButton:hover {
            background-color: #5dade2;
            border: 2px solid #5dade2;
            color: #ffffff;
        }
        
        QPushButton.smallButton:pressed {
            background-color: #48a1d6;
            border: 2px solid #48a1d6;
            color: #ffffff;
        }
        
        /* Toggle Buttons */
        QPushButton.toggleButton {
            background-color: #34495e;
            border: 2px solid #5dade2;
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
            min-height: 30px;
            color: #ffffff;
        }
        
        QPushButton.toggleButton:hover {
            background-color: #5dade2;
            border: 2px solid #5dade2;
            color: #ffffff;
        }
        
        QPushButton.toggleButton:pressed {
            background-color: #48a1d6;
            border: 2px solid #48a1d6;
            color: #ffffff;
        }
        
        QPushButton.toggleButton:checked {
            background-color: #5dade2;
            border: 2px solid #5dade2;
            color: #ffffff;
        }
        
        QPushButton.toggleButton:checked:hover {
            background-color: #48a1d6;
            border: 2px solid #48a1d6;
        }
        
        /* Weather Buttons - Circular with outline */
        QPushButton#weatherButton {
            background-color: #34495e;
            border: 2px solid #5dade2;
            border-radius: 27px;
            font-size: 24px;
            padding: 0px;
            min-width: 54px;
            max-width: 54px;
            min-height: 54px;
            max-height: 54px;
            color: #ffffff;
        }
        
        QPushButton#weatherButton:hover {
            background-color: #5dade2;
            border: 2px solid #5dade2;
            color: #ffffff;
        }
        
        QPushButton#weatherButton:pressed {
            background-color: #48a1d6;
            border: 2px solid #48a1d6;
            color: #ffffff;
        }
        
        QPushButton#weatherButton:checked {
            background-color: #5dade2;
            border: 2px solid #5dade2;
            color: #ffffff;
        }
        
        QPushButton#weatherButton:checked:hover {
            background-color: #48a1d6;
            border: 2px solid #48a1d6;
        }
        
        /* Group Boxes */
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
        
        /* Labels */
        QLabel {
            color: #ecf0f1;
            background-color: transparent;
            font-size: 12px;
        }
        
        /* Input Fields */
        QSpinBox, QDoubleSpinBox {
            background-color: #2c3e50;
            color: #ffffff;
            border: 2px solid #5dade2;
            border-radius: 6px;
            padding: 6px;
            min-height: 30px;
            font-size: 13px;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #48a1d6;
            background-color: #2c3e50;
        }
        
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background-color: #5dade2;
            border: none;
            width: 20px;
        }
        
        /* ComboBoxes */
        QComboBox {
            background-color: #2c3e50;
            color: #ffffff;
            border: 2px solid #5dade2;
            border-radius: 6px;
            padding: 6px;
            min-height: 30px;
            font-size: 13px;
        }
        
        QComboBox:focus {
            border: 2px solid #48a1d6;
            background-color: #2c3e50;
        }
        
        QComboBox::drop-down {
            border: none;
            background-color: #5dade2;
            width: 25px;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid white;
            margin-right: 5px;
        }
        
        /* Checkboxes */
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
            font-size: 13px;
            background-color: transparent;
        }
        
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid #5dade2;
            background-color: #2c3e50;
        }
        
        QCheckBox::indicator:checked {
            background-color: #5dade2;
            border: 2px solid #48a1d6;
        }
        
        /* Progress Bars */
        QProgressBar {
            border: 2px solid #5dade2;
            border-radius: 6px;
            background-color: #2c3e50;
            color: #ffffff;
            text-align: center;
            font-weight: bold;
            min-height: 25px;
        }
        
        QProgressBar::chunk {
            background-color: #5dade2;
            border-radius: 4px;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 2px solid #5dade2;
            background-color: #34495e;
            border-radius: 8px;
            border-top-left-radius: 0px;
        }
        
        QTabBar::tab {
            background-color: #34495e;
            color: #b8c5ce;
            border: 2px solid #5dade2;
            border-bottom: none;
            padding: 10px 20px;
            margin-right: 3px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-size: 13px;
        }
        
        QTabBar::tab:selected {
            background-color: #5dade2;
            color: #ffffff;
            font-weight: bold;
        }
        
        /* Line Edits */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #2c3e50;
            color: #ffffff;
            border: 2px solid #5dade2;
            border-radius: 6px;
            padding: 8px;
            min-height: 28px;
            font-size: 13px;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            background-color: #253545;
            border: 2px solid #48a1d6;
        }
        
        /* Sliders */
        QSlider::groove:horizontal {
            border: 1px solid #2c3e50;
            height: 6px;
            background-color: #34495e;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background-color: #5dade2;
            border: 1px solid #48a1d6;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #48a1d6;
        }
        
        QSlider::sub-page:horizontal {
            background-color: #5dade2;
            border-radius: 3px;
        }
    """