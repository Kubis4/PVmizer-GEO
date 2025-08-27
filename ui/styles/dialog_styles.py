#!/usr/bin/env python3
"""
Dialog styling for dark theme only
"""

class DialogStyles:
    """Dialog styling for dark theme only"""
    
    @staticmethod
    def get_dark_dialog_style():
        """Dark dialog style with light blue outlines and improved dropdowns"""
        return """
            /* Main Dialog */
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 10px;
            }
            
            /* All Widgets */
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            
            /* Labels */
            QLabel {
                color: #ecf0f1;
                background-color: transparent;
                font-size: 12px;
            }
            
            /* Line Edits with light blue outline */
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: normal;
            }
            
            QLineEdit:focus {
                border: 2px solid #5dade2;
                background-color: #34495e;
            }
            
            QLineEdit:disabled {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 2px solid #7f8c8d;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-height: 30px;
                min-width: 100px;
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
            
            /* Cancel Button - Red styling */
            QPushButton[objectName="cancel_button"] {
                background-color: #e74c3c;
                color: white;
            }
            
            QPushButton[objectName="cancel_button"]:hover {
                background-color: #c0392b;
            }
            
            /* Group Boxes with light blue outline */
            QGroupBox {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                font-weight: bold;
                color: #ecf0f1;
                font-size: 14px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 8px 15px;
                background-color: #2c3e50;
                color: #3498db;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            
            /* Radio Buttons with light blue outline */
            QRadioButton {
                color: #ecf0f1;
                background-color: transparent;
                font-size: 12px;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3498db;
                border-radius: 9px;
                background-color: #34495e;
            }
            
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #5dade2;
            }
            
            QRadioButton::indicator:hover {
                border: 2px solid #5dade2;
            }
            
            /* Check Boxes with light blue outline */
            QCheckBox {
                color: #ecf0f1;
                background-color: transparent;
                font-size: 12px;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3498db;
                border-radius: 3px;
                background-color: #34495e;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #5dade2;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #5dade2;
            }
            
            /* Combo Boxes with visible arrows and proper highlighting */
            QComboBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 4px;
                padding: 8px 30px 8px 8px;
                font-size: 12px;
                min-height: 20px;
            }
            
            QComboBox:focus {
                border: 2px solid #5dade2;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #3498db;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #3498db;
            }
            
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #ecf0f1;
                margin-right: 2px;
            }
            
            QComboBox::down-arrow:on {
                border-top: 8px solid #bdc3c7;
            }
            
            /* Dropdown list styling with proper theme colors */
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 4px;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-bottom: 1px solid #2c3e50;
                background-color: #34495e;
                color: #ecf0f1;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #2980b9;
                color: #ffffff;
            }
            
            /* Category items (non-selectable) styling */
            QComboBox QAbstractItemView::item[category="true"] {
                background-color: #2c3e50;
                color: #3498db;
                font-weight: bold;
                border-bottom: 2px solid #3498db;
            }
            
            /* Spin Boxes with light blue outline */
            QSpinBox, QDoubleSpinBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #5dade2;
            }
            
            /* Text Edits with light blue outline */
            QTextEdit, QPlainTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            
            QTextEdit:focus, QPlainTextEdit:focus {
                border: 2px solid #5dade2;
            }
            
            /* List Widgets */
            QListWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                alternate-background-color: #2c3e50;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            
            QListWidget::item:hover {
                background-color: #2980b9;
                color: #ffffff;
            }
            
            /* Scroll Areas */
            QScrollArea {
                background-color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 4px;
            }
            
            /* Progress Bars */
            QProgressBar {
                border: 2px solid #3498db;
                background-color: #34495e;
                color: #ecf0f1;
                border-radius: 4px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            
            /* Form Layout Styling */
            QFormLayout {
                spacing: 10px;
            }
            
            /* Dialog Button Box */
            QDialogButtonBox {
                background-color: transparent;
            }
            
            /* Styled Labels for Forms */
            QLabel[objectName="form_label"] {
                font-size: 12px;
                font-weight: bold;
                color: #ecf0f1;
            }
            
            /* Title Labels */
            QLabel[objectName="title_label"] {
                font-size: 18px;
                font-weight: bold;
                color: #ecf0f1;
            }
            
            /* Description Labels */
            QLabel[objectName="description_label"] {
                font-size: 12px;
                color: #bdc3c7;
            }
            
            /* Grid Layout */
            QGridLayout {
                spacing: 10px;
            }
        """
    
    @staticmethod
    def detect_theme(parent_widget=None):
        """Always returns dark theme"""
        return "dark"
    
    @staticmethod
    def create_styled_label(text, label_type="form"):
        """Create a styled label"""
        from PyQt5.QtWidgets import QLabel
        
        label = QLabel(text)
        
        if label_type == "title":
            label.setObjectName("title_label")
        elif label_type == "description":
            label.setObjectName("description_label")
        else:
            label.setObjectName("form_label")
        
        return label
