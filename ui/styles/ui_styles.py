#!/usr/bin/env python3
"""
ui/styles/ui_styles.py
Centralized Styles for PVmizer GEO Application - Dark Theme Only
All CSS styles organized by component type
"""

# ============================================================================
# MODEL 3D TAB PANEL STYLES - Dark Theme Only
# ============================================================================

def get_model3d_panel_style():
    """Main panel style for Model3D tab panel - Dark theme only"""
    return """
        Model3DTabPanel {
            background-color: #2c3e50;
            border: none;
        }
    """

def get_model3d_tab_widget_style():
    """Tab widget style for Model3D panel - Dark theme only"""
    return """
        QTabWidget {
            background-color: #2c3e50;
        }
        
        QTabWidget::pane {
            border: 1px solid #34495e;
            background-color: #2c3e50;
            border-radius: 6px;
        }
        
        QTabWidget::tab-bar {
            alignment: left;
        }
        
        QTabBar {
            background-color: #2c3e50;
        }
        
        QTabBar::tab {
            background-color: #34495e;
            color: #ffffff;
            border: none;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            min-width: 80px;
            max-width: 120px;
            font-size: 12px;
            font-weight: normal;
        }
        
        QTabBar::tab:selected {
            background-color: #3498db;
            color: #ffffff;
            font-weight: bold;
            padding-bottom: 10px;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #2980b9;
            color: #ffffff;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
            background-color: #34495e;
        }
    """

def get_model3d_groupbox_style():
    """GroupBox style for Model3D panel - Dark theme only"""
    return """
        QGroupBox {
            background-color: #34495e;
            border: 1px solid #3498db;
            border-radius: 6px;
            margin-top: 10px;
            margin-bottom: 8px;
            padding-top: 15px;
            padding-left: 8px;
            padding-right: 8px;
            padding-bottom: 8px;
            font-weight: bold;
            font-size: 13px;
            color: #ffffff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 6px 12px;
            background-color: #2c3e50;
            color: #3498db;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
    """

def get_model3d_export_button_style():
    """Export button style for Model3D panel - Dark theme only"""
    return """
        QPushButton {
            background-color: #16a085;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 12px;
            margin: 5px;
        }
        
        QPushButton:hover {
            background-color: #138d75;
        }
        
        QPushButton:pressed {
            background-color: #117a65;
        }
        
        QPushButton:disabled {
            background-color: #7f8c8d;
            color: #bdc3c7;
        }
    """

def get_model3d_tab_content_style():
    """Tab content style for Model3D panel - Dark theme only"""
    return """
        QWidget {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        
        QLabel {
            color: #ecf0f1;
            font-size: 12px;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 11px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #21618c;
        }
        
        QLineEdit {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px;
            font-size: 11px;
        }
        
        QLineEdit:focus {
            border-color: #2980b9;
        }
        
        QComboBox {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px;
            font-size: 11px;
        }
        
        QComboBox:focus {
            border-color: #2980b9;
        }
        
        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: #ecf0f1;
            selection-background-color: #2980b9;
        }
    """

def get_model3d_error_label_style():
    """Error label style for Model3D panel - Dark theme only"""
    return """
        QLabel {
            color: #e74c3c;
            background-color: #2c3e50;
            border: 1px solid #e74c3c;
            border-radius: 4px;
            padding: 10px;
            font-weight: bold;
            font-size: 12px;
        }
    """

# ============================================================================
# GENERAL UI COMPONENT STYLES - Dark Theme Only
# ============================================================================

def get_standard_button_style():
    """Standard button style - Dark theme only"""
    return """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
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
    """

def get_success_button_style():
    """Success/OK button style - Dark theme only"""
    return """
        QPushButton {
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #219a52;
        }
        
        QPushButton:pressed {
            background-color: #1e8449;
        }
    """

def get_danger_button_style():
    """Danger/Delete button style - Dark theme only"""
    return """
        QPushButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #c0392b;
        }
        
        QPushButton:pressed {
            background-color: #a93226;
        }
    """

def get_secondary_button_style():
    """Secondary/Cancel button style - Dark theme only"""
    return """
        QPushButton {
            background-color: #95a5a6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 12px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #7f8c8d;
        }
        
        QPushButton:pressed {
            background-color: #6c757d;
        }
    """

def get_input_field_style():
    """Input field style - Dark theme only"""
    return """
        QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 8px;
            font-size: 13px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #2980b9;
            background-color: #2c3e50;
        }
        
        QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {
            background-color: #7f8c8d;
            color: #bdc3c7;
            border-color: #95a5a6;
        }
    """

def get_combobox_style():
    """ComboBox style - Dark theme only"""
    return """
        QComboBox {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 13px;
            min-width: 120px;
        }
        
        QComboBox:focus {
            border-color: #2980b9;
        }
        
        QComboBox:disabled {
            background-color: #7f8c8d;
            color: #bdc3c7;
            border-color: #95a5a6;
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
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            selection-background-color: #2980b9;
        }
    """

def get_checkbox_style():
    """CheckBox style - Dark theme only"""
    return """
        QCheckBox {
            color: #ecf0f1;
            background-color: transparent;
            font-size: 13px;
        }
        
        QCheckBox:disabled {
            color: #bdc3c7;
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
    """

def get_radiobutton_style():
    """RadioButton style - Dark theme only"""
    return """
        QRadioButton {
            color: #ecf0f1;
            background-color: transparent;
            font-size: 13px;
        }
        
        QRadioButton:disabled {
            color: #bdc3c7;
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
    """

def get_groupbox_style():
    """GroupBox style - Dark theme only"""
    return """
        QGroupBox {
            background-color: #34495e;
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
    """

def get_label_style():
    """Label style - Dark theme only"""
    return """
        QLabel {
            color: #ecf0f1;
            font-size: 12px;
        }
    """

def get_text_edit_style():
    """TextEdit style - Dark theme only"""
    return """
        QTextEdit, QPlainTextEdit {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 8px;
            font-size: 12px;
        }
        
        QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #2980b9;
        }
    """

def get_progress_bar_style():
    """Progress bar style - Dark theme only"""
    return """
        QProgressBar {
            border: 1px solid #3498db;
            background-color: #34495e;
            color: #ecf0f1;
            border-radius: 4px;
            text-align: center;
            font-weight: bold;
        }
        
        QProgressBar::chunk {
            background-color: #3498db;
            border-radius: 3px;
        }
    """

def get_slider_style():
    """Slider style - Dark theme only"""
    return """
        QSlider::groove:horizontal {
            border: 1px solid #34495e;
            height: 8px;
            background: #2c3e50;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #3498db;
            border: 1px solid #2980b9;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #2980b9;
        }
        
        QSlider::handle:horizontal:pressed {
            background: #21618c;
        }
    """

def get_tab_widget_style():
    """Tab widget style - Dark theme only"""
    return """
        QTabWidget {
            border: none;
            background-color: #2c3e50;
        }
        
        QTabWidget::pane {
            border: 1px solid #34495e;
            border-radius: 4px;
            background-color: #2c3e50;
        }
        
        QTabBar {
            border: none;
            background-color: #2c3e50;
        }
        
        QTabBar::tab {
            background-color: #34495e;
            border: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 100px;
            color: #ecf0f1;
        }
        
        QTabBar::tab:selected {
            background-color: #3498db;
            color: #ffffff;
            font-weight: bold;
            border-bottom: 2px solid #2980b9;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #2980b9;
        }
    """

def get_scroll_bar_style():
    """Scroll bar style - Dark theme only"""
    return """
        QScrollBar:vertical {
            background-color: #34495e;
            width: 16px;
            border: none;
            border-radius: 8px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3498db;
            border-radius: 8px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #2980b9;
        }
        
        QScrollBar:horizontal {
            background-color: #34495e;
            height: 16px;
            border: none;
            border-radius: 8px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #3498db;
            border-radius: 8px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #2980b9;
        }
    """

def get_list_widget_style():
    """List widget style - Dark theme only"""
    return """
        QListWidget {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            alternate-background-color: #2c3e50;
        }
        
        QListWidget::item:selected {
            background-color: #2980b9;
        }
        
        QListWidget::item:hover {
            background-color: #3498db;
        }
    """

def get_tree_widget_style():
    """Tree widget style - Dark theme only"""
    return """
        QTreeWidget {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            border-radius: 4px;
            alternate-background-color: #2c3e50;
        }
        
        QTreeWidget::item:selected {
            background-color: #2980b9;
        }
        
        QTreeWidget::item:hover {
            background-color: #3498db;
        }
        
        QHeaderView::section {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            padding: 4px;
        }
    """

def get_table_widget_style():
    """Table widget style - Dark theme only"""
    return """
        QTableWidget {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #3498db;
            gridline-color: #2c3e50;
            alternate-background-color: #2c3e50;
        }
        
        QTableWidget::item:selected {
            background-color: #2980b9;
        }
        
        QTableWidget::item:hover {
            background-color: #3498db;
        }
        
        QHeaderView::section {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            padding: 4px;
            font-weight: bold;
        }
    """

# ============================================================================
# DIALOG SPECIFIC STYLES - Dark Theme Only
# ============================================================================

def get_dialog_style():
    """General dialog style - Dark theme only"""
    return """
        QDialog {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        
        QWidget {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
    """

def get_message_box_style():
    """Message box style - Dark theme only"""
    return """
        QMessageBox {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        
        QMessageBox QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        
        QMessageBox QPushButton:hover {
            background-color: #2980b9;
        }
    """

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def apply_dark_theme_to_widget(widget):
    """Apply comprehensive dark theme to any widget"""
    widget.setStyleSheet(f"""
        {get_dialog_style()}
        {get_standard_button_style()}
        {get_input_field_style()}
        {get_combobox_style()}
        {get_checkbox_style()}
        {get_radiobutton_style()}
        {get_groupbox_style()}
        {get_label_style()}
        {get_text_edit_style()}
        {get_progress_bar_style()}
        {get_tab_widget_style()}
        {get_scroll_bar_style()}
    """)

def get_complete_dark_theme():
    """Get complete dark theme stylesheet"""
    return f"""
        {get_dialog_style()}
        {get_standard_button_style()}
        {get_input_field_style()}
        {get_combobox_style()}
        {get_checkbox_style()}
        {get_radiobutton_style()}
        {get_groupbox_style()}
        {get_label_style()}
        {get_text_edit_style()}
        {get_progress_bar_style()}
        {get_slider_style()}
        {get_tab_widget_style()}
        {get_scroll_bar_style()}
        {get_list_widget_style()}
        {get_tree_widget_style()}
        {get_table_widget_style()}
        {get_message_box_style()}
    """