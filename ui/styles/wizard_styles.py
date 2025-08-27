#!/usr/bin/env python3
"""
Separate CSS styling for the project wizard - Dark theme only
"""

class WizardStyles:
    """CSS styles for the project wizard - Dark theme only"""
    
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
            
            QLineEdit:disabled {
                background-color: #7f8c8d !important;
                color: #bdc3c7 !important;
                border: 1px solid #95a5a6 !important;
            }
            
            /* Spin Boxes */
            QSpinBox, QDoubleSpinBox {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QSpinBox:disabled, QDoubleSpinBox:disabled {
                background-color: #7f8c8d !important;
                color: #bdc3c7 !important;
                border: 1px solid #95a5a6 !important;
            }
            
            /* Text Edits */
            QTextEdit, QPlainTextEdit {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 6px;
            }
            
            QTextEdit:focus, QPlainTextEdit:focus {
                border: 1px solid #2980b9 !important;
            }
            
            /* Combo Boxes */
            QComboBox {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db !important;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                min-width: 120px;
            }
            
            QComboBox:focus {
                border: 1px solid #2980b9 !important;
            }
            
            QComboBox:disabled {
                background-color: #7f8c8d !important;
                color: #bdc3c7 !important;
                border: 1px solid #95a5a6 !important;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 25px;
                border-left: 1px solid #3498db;
                background-color: #3498db;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: 1px solid #3498db;
                selection-background-color: #2980b9;
            }
            
            /* Check Boxes */
            QCheckBox {
                color: #ecf0f1 !important;
                background-color: transparent !important;
                font-size: 13px;
            }
            
            QCheckBox:disabled {
                color: #bdc3c7 !important;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #3498db;
                border-radius: 3px;
                background-color: #34495e;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 1px solid #2980b9;
            }
            
            QCheckBox::indicator:disabled {
                background-color: #7f8c8d;
                border: 1px solid #95a5a6;
            }
            
            /* Radio Buttons */
            QRadioButton {
                color: #ecf0f1 !important;
                background-color: transparent !important;
                font-size: 13px;
            }
            
            QRadioButton:disabled {
                color: #bdc3c7 !important;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #3498db;
                border-radius: 9px;
                background-color: #34495e;
            }
            
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 1px solid #2980b9;
            }
            
            QRadioButton::indicator:disabled {
                background-color: #7f8c8d;
                border: 1px solid #95a5a6;
            }
            
            /* Group Boxes */
            QGroupBox {
                background-color: #34495e !important;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 6px 15px;
                background-color: #2c3e50;
                color: #3498db;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #3498db !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                min-height: 25px;
            }
            
            QPushButton:hover {
                background-color: #2980b9 !important;
            }
            
            QPushButton:pressed {
                background-color: #21618c !important;
            }
            
            QPushButton:disabled {
                background-color: #7f8c8d !important;
                color: #bdc3c7 !important;
            }
            
            /* Dialog Button Box */
            QDialogButtonBox > QPushButton {
                background-color: #3498db !important;
                color: #ffffff !important;
                border: 1px solid #2980b9 !important;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            
            QDialogButtonBox > QPushButton:hover {
                background-color: #2980b9 !important;
            }
            
            QDialogButtonBox > QPushButton:pressed {
                background-color: #21618c !important;
            }
        """