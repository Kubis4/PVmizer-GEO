#!/usr/bin/env python3
"""
ui/styles/ui_styles.py
Centralized Styles for PVmizer GEO Application
All CSS styles organized by component type
"""

# ============================================================================
# MODEL 3D TAB PANEL STYLES - Professional Dark Theme
# ============================================================================

def get_model3d_panel_style(is_dark_theme=False):
    """Main panel style for Model3D tab panel"""
    return """
        Model3DTabPanel {
            background-color: #2c3e50;
            border: none;
        }
    """

def get_model3d_tab_widget_style(is_dark_theme=False):
    """Tab widget style for Model3D panel"""
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

def get_model3d_groupbox_style(is_dark_theme=False):
    """GroupBox style for Model3D panel - WITH BORDER, centered title"""
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
            padding: 0px 8px;
            color: #3498db;
            background-color: #34495e;
            font-weight: bold;
            font-size: 13px;
        }
    """

def get_model3d_button_style(button_type="default"):
    """Button styles for Model3D panel - ALL buttons use #3498db"""
    base_style = """
        QPushButton {
            background-color: #3498db;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
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
    
    if button_type == "animate":
        # Animate button - same blue color
        return """
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                text-align: center;
                min-height: 28px;
                font-size: 11px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:checked {
                background-color: #e74c3c;
            }
            QPushButton:checked:hover {
                background-color: #c0392b;
            }
        """
    else:
        # Default button style
        return base_style + """
            QPushButton {
                min-height: 32px;
            }
        """

def get_model3d_label_style():
    """Label style with white text"""
    return """
        QLabel {
            color: #ffffff;
            background-color: transparent;
            font-size: 12px;
            font-weight: normal;
            padding: 2px 0px;
        }
    """

def get_model3d_combobox_style():
    """ComboBox style with WHITE TEXT and visible dropdown arrow"""
    return """
        QComboBox {
            background-color: #34495e;
            color: #ffffff;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px 8px;
            padding-right: 25px;
            font-size: 12px;
            font-weight: normal;
            min-height: 20px;
        }
        
        QComboBox:focus {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QComboBox:hover {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QComboBox:disabled {
            background-color: #2c3e50;
            color: #7f8c8d;
            border: 1px solid #34495e;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border: none;
            background-color: #3498db;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::drop-down:hover {
            background-color: #2980b9;
        }
        
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        
        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: #ffffff;
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
            background-color: #34495e;
            color: #ffffff;
            min-height: 20px;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #3498db;
            color: #ffffff;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #2980b9;
            color: #ffffff;
        }
        
        /* Force white text in all states */
        QComboBox QListView {
            color: #ffffff;
            background-color: #34495e;
        }
    """

def get_model3d_timeedit_style():
    """Time edit style with white text"""
    return """
        QTimeEdit {
            background-color: #34495e;
            color: #ffffff;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 12px;
            font-weight: normal;
            min-height: 20px;
        }
        
        QTimeEdit:focus {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QTimeEdit:hover {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QTimeEdit::up-button, QTimeEdit::down-button {
            background-color: #3498db;
            border: none;
            width: 16px;
        }
        
        QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
            background-color: #2980b9;
        }
        
        QTimeEdit::up-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 4px solid #ffffff;
        }
        
        QTimeEdit::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #ffffff;
        }
    """

def get_model3d_dateedit_style():
    """Date edit style with calendar fixes - WHITE TEXT"""
    return """
        QDateEdit {
            background-color: #34495e;
            color: #ffffff;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px 8px;
            padding-right: 25px;
            font-size: 12px;
            font-weight: normal;
            min-height: 20px;
        }
        
        QDateEdit:focus {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QDateEdit:hover {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QDateEdit::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border: none;
            background-color: #3498db;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QDateEdit::drop-down:hover {
            background-color: #2980b9;
        }
        
        QDateEdit::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        
        /* Calendar Widget Styling - FORCE ALL WHITE TEXT */
        QCalendarWidget {
            background-color: #2c3e50;
            color: #ffffff;
            border: 1px solid #3498db;
            border-radius: 4px;
        }
        
        QCalendarWidget * {
            color: #ffffff;
            background-color: #2c3e50;
        }
        
        QCalendarWidget QWidget {
            color: #ffffff;
        }
        
        QCalendarWidget QToolButton {
            background-color: #34495e;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 4px;
            margin: 2px;
        }
        
        QCalendarWidget QToolButton:hover {
            background-color: #3498db;
            color: #ffffff;
        }
        
        QCalendarWidget QToolButton:pressed {
            background-color: #2980b9;
            color: #ffffff;
        }
        
        QCalendarWidget QMenu {
            background-color: #34495e;
            color: #ffffff;
            border: 1px solid #3498db;
        }
        
        QCalendarWidget QMenu::item {
            background-color: #34495e;
            color: #ffffff;
            padding: 4px 20px;
        }
        
        QCalendarWidget QMenu::item:selected {
            background-color: #3498db;
            color: #ffffff;
        }
        
        QCalendarWidget QSpinBox {
            background-color: #34495e;
            color: #ffffff;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 2px;
            selection-background-color: #3498db;
            selection-color: #ffffff;
        }
        
        QCalendarWidget QSpinBox::up-button,
        QCalendarWidget QSpinBox::down-button {
            background-color: #3498db;
            border: none;
            width: 16px;
        }
        
        QCalendarWidget QSpinBox::up-arrow,
        QCalendarWidget QSpinBox::down-arrow {
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
        }
        
        QCalendarWidget QSpinBox::up-arrow {
            border-bottom: 4px solid #ffffff;
        }
        
        QCalendarWidget QSpinBox::down-arrow {
            border-top: 4px solid #ffffff;
        }
        
        QCalendarWidget QAbstractItemView {
            background-color: #2c3e50;
            color: #ffffff;
            selection-background-color: #3498db;
            selection-color: #ffffff;
            border: none;
            alternate-background-color: #2c3e50;
        }
        
        /* Calendar table view - day numbers */
        QCalendarWidget QTableView {
            background-color: #2c3e50;
            color: #ffffff;
            selection-background-color: #3498db;
            selection-color: #ffffff;
            gridline-color: #34495e;
            outline: none;
        }
        
        /* Individual day cells */
        QCalendarWidget QTableView::item {
            color: #ffffff;
            background-color: #2c3e50;
            padding: 4px;
            border: none;
        }
        
        QCalendarWidget QTableView::item:selected {
            background-color: #3498db;
            color: #ffffff;
            font-weight: bold;
        }
        
        QCalendarWidget QTableView::item:hover {
            background-color: #34495e;
            color: #ffffff;
        }
        
        /* Weekday headers */
        QCalendarWidget QHeaderView {
            background-color: #34495e;
            color: #ffffff;
            border: none;
        }
        
        QCalendarWidget QHeaderView::section {
            background-color: #34495e;
            color: #3498db;
            font-weight: bold;
            border: none;
            padding: 4px;
        }
        
        /* Navigation bar */
        QCalendarWidget QWidget#qt_calendar_navigationbar {
            background-color: #34495e;
            color: #ffffff;
        }
        
        QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {
            color: #ffffff;
            background-color: #34495e;
        }
        
        /* Month/Year buttons */
        QCalendarWidget QToolButton#qt_calendar_monthbutton,
        QCalendarWidget QToolButton#qt_calendar_yearbutton {
            color: #ffffff;
            background-color: #34495e;
            padding: 2px 10px;
            border-radius: 4px;
        }
        
        QCalendarWidget QToolButton#qt_calendar_monthbutton:hover,
        QCalendarWidget QToolButton#qt_calendar_yearbutton:hover {
            color: #ffffff;
            background-color: #3498db;
        }
        
        /* Navigation arrows */
        QCalendarWidget QToolButton#qt_calendar_prevmonth,
        QCalendarWidget QToolButton#qt_calendar_nextmonth {
            color: #ffffff;
            background-color: #34495e;
            qproperty-icon: none;
        }
        
        QCalendarWidget QToolButton#qt_calendar_prevmonth:hover,
        QCalendarWidget QToolButton#qt_calendar_nextmonth:hover {
            background-color: #3498db;
            color: #ffffff;
        }
        
        /* Force white text on disabled days */
        QCalendarWidget QTableView::item:disabled {
            color: #7f8c8d;
            background-color: #2c3e50;
        }
        
        /* Today's date */
        QCalendarWidget QTableView::item:selected:active {
            background-color: #e74c3c;
            color: #ffffff;
            font-weight: bold;
        }
        
        /* Current month days vs other month days */
        QCalendarWidget QTableView::item:!selected {
            color: #ffffff;
        }
        
        /* Days from other months */
        QCalendarWidget QTableView::item:selected:!active {
            color: #95a5a6;
            background-color: #2c3e50;
        }
    """

def get_model3d_slider_style():
    """Slider style with groupbox matching colors"""
    return """
        QSlider::groove:horizontal {
            border: 1px solid #3498db;
            background: #34495e;
            height: 6px;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background: #3498db;
            border: 1px solid #3498db;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }
        
        QSlider::handle:horizontal:hover {
            background: #2980b9;
        }
        
        QSlider::sub-page:horizontal {
            background: #3498db;
            border-radius: 3px;
        }
    """

def get_model3d_spinbox_style():
    """Spin box style with WHITE TEXT"""
    return """
        QSpinBox, QDoubleSpinBox {
            background-color: #34495e;
            color: #ffffff;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 12px;
            font-weight: normal;
            min-height: 20px;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QSpinBox:hover, QDoubleSpinBox:hover {
            border: 1px solid #2980b9;
            background-color: #3d566e;
            color: #ffffff;
        }
        
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background-color: #3498db;
            border: none;
            width: 16px;
        }
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
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
    """

def get_model3d_progress_style():
    """Progress bar style for Model3D panel"""
    return """
        QProgressBar {
            border: 1px solid #3498db;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            height: 25px;
            background-color: #34495e;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #3498db;
            border-radius: 3px;
        }
    """

def get_model3d_scrollbar_style():
    """Scrollbar style matching groupbox colors"""
    return """
        QScrollBar:vertical {
            background-color: #34495e;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #3498db;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #2980b9;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            border: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QScrollBar:horizontal {
            background-color: #34495e;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #3498db;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #2980b9;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
            border: none;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    """

def get_model3d_info_label_style():
    """Info/description label style"""
    return """
        color: #bdc3c7;
        font-size: 12px;
        font-weight: normal;
        background-color: transparent;
    """

def get_model3d_status_label_style(status_type="available"):
    """Status label styles"""
    if status_type == "available":
        return "color: #27ae60; font-size: 11px; font-weight: normal; background-color: transparent;"
    elif status_type == "unavailable":
        return "color: #e74c3c; font-size: 11px; font-weight: normal; background-color: transparent;"
    elif status_type == "power":
        return "color: #3498db; font-weight: bold; font-size: 13px; background-color: transparent;"
    elif status_type == "energy":
        return "color: #2ecc71; font-weight: bold; font-size: 13px; background-color: transparent;"
    elif status_type == "efficiency":
        return "color: #f39c12; font-weight: bold; font-size: 13px; background-color: transparent;"
    else:
        return "color: #95a5a6; font-size: 11px; font-style: italic; background-color: transparent;"

def get_model3d_time_label_style():
    """Special style for time display label"""
    return """
        font-weight: bold;
        color: #3498db;
        font-size: 16px;
        background-color: transparent;
    """

def get_model3d_sun_info_label_style(label_type="sunrise"):
    """Sunrise/sunset label styles"""
    if label_type == "sunrise":
        return "color: #f39c12; font-weight: bold; background-color: transparent;"
    elif label_type == "sunset":
        return "color: #e74c3c; font-weight: bold; background-color: transparent;"
    else:
        return "font-size: 11px; color: #95a5a6; padding: 5px; background-color: transparent; font-style: italic;"

# ============================================================================
# EXPORT BUTTON STYLE
# ============================================================================

def get_model3d_export_button_style(is_dark_theme=False):
    """Export button style - larger for main export"""
    return """
        QPushButton {
            background-color: #3498db;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            text-align: center;
            min-height: 40px;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
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

def get_model3d_error_label_style(is_dark_theme=False):
    """Error label style"""
    return """
        QLabel {
            color: #e74c3c;
            font-size: 11px;
            padding: 10px;
            background-color: rgba(231, 76, 60, 0.1);
            border: 1px solid #e74c3c;
            border-radius: 4px;
        }
    """

