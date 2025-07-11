#!/usr/bin/env python3
"""
Dialog Styles for PVmizer GEO Application
Centralized CSS styling for all dialogs with professional, compact design
"""

class DialogStyles:
    """Centralized dialog styling with professional, compact design"""
    
    @staticmethod
    def get_dark_dialog_style():
        """Dark theme for dialogs with compact, professional design"""
        return """
            /* Main Dialog - Custom Dark Background */
            QDialog {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 15px;
            }
            
            /* All Widgets Default - Force Custom Background */
            QWidget {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
            }
            
            /* GroupBox - Professional Compact Design */
            QGroupBox {
                background-color: #34495e !important;
                border: 1px solid #3498db;
                border-radius: 6px;
                margin-top: 10px;
                margin-bottom: 8px;
                padding-top: 12px;
                padding-left: 8px;
                padding-right: 8px;
                padding-bottom: 8px;
                font-weight: bold;
                font-size: 13px;
                color: #ffffff !important;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 2px 8px;
                color: #3498db !important;
                background-color: #34495e !important;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
            
            /* Labels - Professional Text Sizing */
            QLabel {
                color: #ffffff !important;
                background-color: transparent !important;
                font-size: 12px;
                font-weight: normal;
                padding: 1px 0px;
            }
            
            /* Small Detail Text - White with Smaller Font */
            QLabel[styleSheet*="color: gray"], 
            QLabel[styleSheet*="color: grey"],
            QLabel[text*="Max:"],
            QLabel[text*="Min:"],
            QLabel[text*="Default:"],
            QLabel[text*="Limits:"],
            QLabel[text*="Range:"] {
                color: #ffffff !important;
                background-color: transparent !important;
                font-size: 10px !important;
                font-weight: normal;
                font-style: italic;
                padding: 1px 0px;
                margin-left: 15px;
            }
            
            /* Input Fields - Compact Professional Design */
            QLineEdit {
                background-color: #34495e !important;
                color: #ffffff !important;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                font-weight: normal;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                min-height: 16px;
            }
            
            QLineEdit:focus {
                border: 1px solid #2980b9 !important;
                background-color: #3d566e !important;
            }
            
            QLineEdit:hover {
                border: 1px solid #2980b9 !important;
                background-color: #3d566e !important;
            }
            
            QLineEdit:disabled {
                background-color: #2c3e50 !important;
                color: #7f8c8d !important;
                border: 1px solid #34495e;
            }
            
            QLineEdit:read-only {
                background-color: #2c3e50 !important;
                color: #bdc3c7 !important;
                border: 1px solid #34495e;
            }
            
            /* ComboBox - Compact Professional Design */
            QComboBox {
                background-color: #34495e !important;
                color: #ffffff !important;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                font-weight: normal;
                min-height: 16px;
            }
            
            QComboBox:focus {
                border: 1px solid #2980b9 !important;
                background-color: #3d566e !important;
            }
            
            QComboBox:hover {
                border: 1px solid #2980b9 !important;
                background-color: #3d566e !important;
            }
            
            QComboBox:disabled {
                background-color: #2c3e50 !important;
                color: #7f8c8d !important;
                border: 1px solid #34495e;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: #34495e !important;
                width: 20px;
                border-left: 1px solid #3498db;
                border-radius: 0px 4px 4px 0px;
            }
            
            QComboBox::drop-down:hover {
                background-color: #3d566e !important;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 6px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #34495e !important;
                color: #ffffff !important;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                border: 1px solid #3498db;
                border-radius: 4px;
                outline: none;
                padding: 4px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px 8px;
                border-radius: 2px;
                margin: 1px;
                background-color: #34495e !important;
                color: #ffffff !important;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db !important;
                color: #ffffff !important;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #2980b9 !important;
                color: #ffffff !important;
            }
            
            /* Buttons - Professional Compact Sizing */
            QPushButton {
                background-color: #3498db !important;
                color: #ffffff !important;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                text-align: center;
                min-width: 80px;
                min-height: 28px;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
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
            
            /* Special Cancel Button Styling */
            QPushButton[text="Cancel"], 
            QPushButton[text="cancel"],
            QPushButton[text="Abbrechen"] {
                background-color: #e74c3c !important;
                color: #ffffff !important;
                min-width: 80px;
                min-height: 28px;
            }
            
            QPushButton[text="Cancel"]:hover, 
            QPushButton[text="cancel"]:hover,
            QPushButton[text="Abbrechen"]:hover {
                background-color: #c0392b !important;
            }
            
            QPushButton[text="Cancel"]:pressed, 
            QPushButton[text="cancel"]:pressed,
            QPushButton[text="Abbrechen"]:pressed {
                background-color: #a93226 !important;
            }
            
            /* CheckBox - Compact Professional Design */
            QCheckBox {
                color: #ffffff !important;
                background-color: transparent !important;
                font-weight: bold;
                spacing: 8px;
                font-size: 12px;
                padding: 4px 0px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #34495e !important;
                border: 1px solid #3498db;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:hover {
                border: 1px solid #2980b9;
                background-color: #3d566e !important;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db !important;
                border: 1px solid #3498db;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9 !important;
                border: 1px solid #2980b9;
            }
            
            QCheckBox::indicator:disabled {
                background-color: #2c3e50 !important;
                border: 1px solid #34495e;
            }
            
            /* Radio Buttons - Compact Professional Design */
            QRadioButton {
                color: #ffffff !important;
                background-color: transparent !important;
                font-weight: bold;
                spacing: 8px;
                font-size: 12px;
                padding: 4px 0px;
            }
            
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                background-color: #34495e !important;
                border: 1px solid #3498db;
                border-radius: 8px;
            }
            
            QRadioButton::indicator:hover {
                border: 1px solid #2980b9;
                background-color: #3d566e !important;
            }
            
            QRadioButton::indicator:checked {
                background-color: #3498db !important;
                border: 1px solid #3498db;
            }
            
            QRadioButton::indicator:checked:hover {
                background-color: #2980b9 !important;
                border: 1px solid #2980b9;
            }
            
            QRadioButton::indicator:disabled {
                background-color: #2c3e50 !important;
                border: 1px solid #34495e;
            }
            
            /* Dialog Buttons - Compact Professional Design */
            QDialogButtonBox {
                background-color: #2c3e50 !important;
                border: none;
                padding: 10px;
                spacing: 8px;
            }
            
            QDialogButtonBox > QPushButton {
                background-color: #3498db !important;
                color: #ffffff !important;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
                min-height: 28px;
                font-weight: bold;
                font-size: 12px;
                margin: 2px;
            }
            
            QDialogButtonBox > QPushButton:hover {
                background-color: #2980b9 !important;
            }
            
            QDialogButtonBox > QPushButton:pressed {
                background-color: #21618c !important;
            }
            
            /* Form Layout - Compact Spacing */
            QFormLayout {
                background-color: #2c3e50 !important;
                spacing: 8px;
            }
            
            QFormLayout QLabel {
                padding: 4px 0px;
                font-weight: bold;
                font-size: 12px;
            }
            
            /* Grid Layout - Compact Spacing */
            QGridLayout {
                background-color: #2c3e50 !important;
                spacing: 8px;
            }
            
            /* VBox and HBox Layouts - Compact Spacing */
            QVBoxLayout {
                spacing: 8px;
            }
            
            QHBoxLayout {
                spacing: 6px;
            }
            
            /* Title Labels - Professional Styling */
            QLabel[styleSheet*="font-size: 14px"],
            QLabel[styleSheet*="font-size: 18px"] {
                color: #3498db !important;
                font-weight: bold;
                font-size: 14px !important;
                padding: 8px 0px;
                background-color: transparent !important;
                text-align: center;
            }
            
            /* Separator Lines */
            QFrame[frameShape="4"] {
                color: #34495e;
                background-color: #34495e;
                border: 1px solid #34495e;
                margin: 6px 0px;
            }
            
            /* Scroll Areas - Compact Design */
            QScrollArea {
                background-color: #2c3e50 !important;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 4px;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: #2c3e50 !important;
            }
            
            QScrollBar:vertical {
                background-color: #34495e !important;
                width: 14px;
                border-radius: 7px;
                border: 1px solid #3498db;
            }
            
            QScrollBar::handle:vertical {
                background-color: #3498db !important;
                border-radius: 5px;
                min-height: 20px;
                border: none;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9 !important;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #21618c !important;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Enhanced Focus Indicators */
            QWidget:focus {
                outline: 1px solid #3498db;
                outline-offset: 1px;
            }
            
            /* Enhanced Tooltip Styling */
            QToolTip {
                background-color: #34495e !important;
                color: #ffffff !important;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
                font-weight: normal;
            }
            
            /* Message Box Styling */
            QMessageBox {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: 1px solid #34495e;
                border-radius: 6px;
            }
            
            QMessageBox QLabel {
                color: #ffffff !important;
                background-color: transparent !important;
                font-size: 12px;
                padding: 8px;
            }
            
            QMessageBox QPushButton {
                background-color: #3498db !important;
                color: #ffffff !important;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 70px;
                min-height: 26px;
                font-weight: bold;
                font-size: 11px;
                margin: 2px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #2980b9 !important;
            }
            
            QMessageBox QPushButton:pressed {
                background-color: #21618c !important;
            }
        """
    
    @staticmethod
    def get_light_dialog_style():
        """Light theme for dialogs - Compact professional design"""
        return """
            /* Main Dialog - Light Background */
            QDialog {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 15px;
            }
            
            /* All Widgets Default */
            QWidget {
                background-color: #ffffff !important;
                color: #2c3e50 !important;
            }
            
            /* GroupBox - Compact Light Design */
            QGroupBox {
                background-color: #f8f9fa !important;
                border: 1px solid #3498db;
                border-radius: 6px;
                margin-top: 10px;
                margin-bottom: 8px;
                padding-top: 12px;
                padding-left: 8px;
                padding-right: 8px;
                padding-bottom: 8px;
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50 !important;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 2px 8px;
                color: #3498db !important;
                background-color: #ffffff !important;
                border-radius: 3px;
                font-weight: bold;
                font-size: 13px;
            }
            
            /* Labels - Professional Text Sizing */
            QLabel {
                color: #2c3e50 !important;
                background-color: transparent !important;
                font-size: 12px;
                font-weight: normal;
                padding: 1px 0px;
            }
            
            /* Small Detail Text - Dark with Smaller Font */
            QLabel[styleSheet*="color: gray"], 
            QLabel[styleSheet*="color: grey"],
            QLabel[text*="Max:"],
            QLabel[text*="Min:"],
            QLabel[text*="Default:"],
            QLabel[text*="Limits:"],
            QLabel[text*="Range:"] {
                color: #2c3e50 !important;
                background-color: transparent !important;
                font-size: 10px !important;
                font-weight: normal;
                font-style: italic;
                padding: 1px 0px;
                margin-left: 15px;
            }
            
            /* Buttons - Professional Compact Sizing */
            QPushButton {
                background-color: #3498db !important;
                color: #ffffff !important;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                text-align: center;
                min-width: 80px;
                min-height: 28px;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
            }
            
            QPushButton:hover {
                background-color: #2980b9 !important;
            }
            
            QPushButton:pressed {
                background-color: #21618c !important;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7 !important;
                color: #7f8c8d !important;
            }
            
            /* Enhanced Tooltip Styling */
            QToolTip {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
                font-weight: normal;
            }
        """
    
    @staticmethod
    def detect_theme(parent_widget):
        """Detect current theme from parent widget"""
        theme = "dark"  # Default to dark
        
        try:
            # Try multiple ways to detect theme
            if parent_widget:
                # Method 1: Check if parent has main_window with theme_manager
                if hasattr(parent_widget, 'main_window') and hasattr(parent_widget.main_window, 'theme_manager'):
                    theme = parent_widget.main_window.theme_manager.current_theme
                    print(f"✅ Theme detected from main_window.theme_manager: {theme}")
                    return theme
                
                # Method 2: Check if parent has theme_manager directly
                elif hasattr(parent_widget, 'theme_manager'):
                    theme = parent_widget.theme_manager.current_theme
                    print(f"✅ Theme detected from parent.theme_manager: {theme}")
                    return theme
                
                # Method 3: Check parent's parent
                elif hasattr(parent_widget, 'parent') and parent_widget.parent():
                    parent_parent = parent_widget.parent()
                    if hasattr(parent_parent, 'main_window') and hasattr(parent_parent.main_window, 'theme_manager'):
                        theme = parent_parent.main_window.theme_manager.current_theme
                        print(f"✅ Theme detected from parent.parent.main_window.theme_manager: {theme}")
                        return theme
                
                # Method 4: Walk up the widget hierarchy
                current_widget = parent_widget
                while current_widget:
                    if hasattr(current_widget, 'theme_manager'):
                        theme = current_widget.theme_manager.current_theme
                        print(f"✅ Theme detected from widget hierarchy: {theme}")
                        return theme
                    current_widget = current_widget.parent()
            
            print(f"⚠️ Could not detect theme, using default: {theme}")
            return theme
            
        except Exception as e:
            print(f"❌ Error detecting theme: {e}, using default: {theme}")
            return theme
