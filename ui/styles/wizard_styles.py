#!/usr/bin/env python3
"""
Separate CSS styling for the project wizard
"""

class WizardStyles:
    """CSS styles for the project wizard"""
    
    @staticmethod
    def get_dark_theme():
        """Dark theme CSS for wizard"""
        return """
            /* Main Dialog */
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            
            /* All Widgets Default */
            QWidget {
                background-color: #2c3e50 !important;
                color: #ecf0f1;
            }
            
            /* Frame Containers */
            QFrame {
                background-color: #2c3e50 !important;
                border: 1px solid #3498db;
                color: #ecf0f1;
                border-radius: 4px;
            }
            
            /* Labels */
            QLabel {
                color: #ecf0f1;
                border: none;
                background-color: transparent !important;
            }
            
            /* Stack Widget and Pages */
            QStackedWidget {
                background-color: #2c3e50 !important;
                border: 1px solid #3498db;
                border-radius: 4px;
            }
            
            QStackedWidget > QWidget {
                background-color: #2c3e50 !important;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 1px solid #3498db;
                background-color: #34495e;
                color: #ecf0f1;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            
            /* Line Edits */
            QLineEdit {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QLineEdit:hover {
                border: 1px solid #2980b9 !important;
            }
            
            /* Text Edits */
            QTextEdit {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QTextEdit:focus {
                border: 1px solid #2980b9 !important;
            }
            
            /* Combo Boxes */
            QComboBox {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QComboBox:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QComboBox:hover {
                border: 1px solid #2980b9 !important;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: #34495e;
                width: 20px;
                border-left: 1px solid #3498db;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ecf0f1;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #3498db;
                outline: none;
            }
            
            /* Spin Boxes */
            QSpinBox, QDoubleSpinBox {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QSpinBox:hover, QDoubleSpinBox:hover {
                border: 1px solid #2980b9 !important;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: #3498db;
                border: none;
                width: 16px;
            }
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #2980b9;
            }
            
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #ecf0f1;
            }
            
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ecf0f1;
            }
            
            /* Check Boxes */
            QCheckBox {
                color: #ecf0f1;
                background-color: transparent !important;
                font-weight: bold;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #34495e;
                border: 1px solid #3498db;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:hover {
                border: 1px solid #2980b9;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 1px solid #3498db;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9;
                border: 1px solid #2980b9;
            }
            
            /* Scroll Areas */
            QScrollArea {
                background-color: #2c3e50 !important;
                border: 1px solid #3498db;
                border-radius: 4px;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: #2c3e50 !important;
            }
            
            QScrollBar:vertical {
                background-color: #34495e;
                width: 15px;
                border-radius: 4px;
                border: 1px solid #3498db;
            }
            
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 4px;
                min-height: 20px;
                border: none;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #21618c;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            
            /* Push Buttons */
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                text-align: center;
                min-width: 90px;
                min-height: 30px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
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
            
            /* Dialog Buttons */
            QDialogButtonBox > QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 90px;
                font-weight: bold;
            }
            
            QDialogButtonBox > QPushButton:hover {
                background-color: #2980b9;
            }
            
            QDialogButtonBox > QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    @staticmethod
    def get_light_theme():
        """Light theme CSS for wizard"""
        return """
            /* Main Dialog */
            QDialog {
                background-color: #ffffff;
                color: #2c3e50;
            }
            
            /* All Widgets Default */
            QWidget {
                background-color: #ffffff !important;
                color: #2c3e50;
            }
            
            /* Frame Containers */
            QFrame {
                background-color: #ffffff !important;
                border: 1px solid #3498db;
                color: #2c3e50;
                border-radius: 4px;
            }
            
            /* Labels */
            QLabel {
                color: #2c3e50;
                border: none;
                background-color: transparent !important;
            }
            
            /* Stack Widget and Pages */
            QStackedWidget {
                background-color: #ffffff !important;
                border: 1px solid #3498db;
                border-radius: 4px;
            }
            
            QStackedWidget > QWidget {
                background-color: #ffffff !important;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 1px solid #3498db;
                background-color: #ecf0f1;
                color: #2c3e50;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            
            /* Line Edits */
            QLineEdit {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QLineEdit:hover {
                border: 1px solid #2980b9 !important;
            }
            
            /* Text Edits */
            QTextEdit {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QTextEdit:focus {
                border: 1px solid #2980b9 !important;
            }
            
            /* Combo Boxes */
            QComboBox {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QComboBox:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QComboBox:hover {
                border: 1px solid #2980b9 !important;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: #ffffff;
                width: 20px;
                border-left: 1px solid #3498db;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #3498db;
                outline: none;
            }
            
            /* Spin Boxes */
            QSpinBox, QDoubleSpinBox {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QSpinBox:hover, QDoubleSpinBox:hover {
                border: 1px solid #2980b9 !important;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: #3498db;
                border: none;
                width: 16px;
            }
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #2980b9;
            }
            
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #ffffff;
            }
            
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
            }
            
            /* Check Boxes */
            QCheckBox {
                color: #2c3e50;
                background-color: transparent !important;
                font-weight: bold;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #ffffff;
                border: 1px solid #3498db;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:hover {
                border: 1px solid #2980b9;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 1px solid #3498db;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9;
                border: 1px solid #2980b9;
            }
            
            /* Scroll Areas */
            QScrollArea {
                background-color: #f8f9fa !important;
                border: 1px solid #3498db;
                border-radius: 4px;
            }
            
            QScrollBar:vertical {
                background-color: #ecf0f1;
                width: 15px;
                border-radius: 4px;
                border: 1px solid #3498db;
            }
            
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 4px;
                min-height: 20px;
                border: none;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #21618c;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            
            /* Push Buttons */
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                text-align: center;
                min-width: 90px;
                min-height: 30px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            
            /* Dialog Buttons */
            QDialogButtonBox > QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 90px;
                font-weight: bold;
            }
            
            QDialogButtonBox > QPushButton:hover {
                background-color: #2980b9;
            }
            
            QDialogButtonBox > QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    