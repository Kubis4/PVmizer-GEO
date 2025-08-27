#!/usr/bin/env python3
"""
Updated Left Control Panel - Blue buttons, centered titles, scrollable content
CLEANED - Properly sized title with beautiful font
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QStackedWidget, 
                            QSizePolicy, QGroupBox, QPushButton, QWidget,
                            QScrollArea)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

# Import separated tab panels
from ui.panel.maps_tab_left import MapsTabPanel
from ui.panel.drawing_tab_left import DrawingTabPanel
from ui.panel.model_tab_left.model_3d_tab_panel import Model3DTabPanel

class LeftControlPanel(QFrame):
    """Main Left Control Panel with blue buttons and scrollable content"""

    # Consolidated signals from all tabs
    scale_changed = pyqtSignal(float)
    angle_snap_toggled = pyqtSignal(bool)
    clear_drawing_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    generate_model_requested = pyqtSignal()
    snip_requested = pyqtSignal()
    export_model_requested = pyqtSignal()
    building_parameter_changed = pyqtSignal(str, object)
    solar_parameter_changed = pyqtSignal(str, object)
    animation_toggled = pyqtSignal(bool)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # State tracking
        self.polygon_complete = False
        self.current_tab_index = 0
        
        # Tab titles - Clear and readable
        self.tab_titles = [
            "PVmizer GEO",          # Maps tab (main view)
            "Drawing Tools",        # Drawing tab
            "3D Model View"         # 3D Model tab
        ]
        
        # UI components
        self.title_box = None
        self.title_label = None
        self.controls_box = None
        self.scroll_area = None
        self.stacked_widget = None
        self.maps_tab = None
        self.drawing_tab = None
        self.model_3d_tab = None
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup main UI structure with scrollable content"""
        self.setObjectName("leftMenu")
        
        # Panel width - INCREASED to better accommodate 3D model tabs
        PANEL_WIDTH = 500  # Increased from 450 to 500
        self.setFixedWidth(PANEL_WIDTH)
        self.setFrameStyle(QFrame.NoFrame)
        
        # Main panel background
        self.setStyleSheet("""
            QFrame#leftMenu {
                background-color: #3a4f5c;
                border: none;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignTop)
        
        # Title Box with light blue border - MODERATELY BIGGER TEXT
        self.title_box = QWidget()
        self.title_box.setFixedHeight(75)  # Moderate increase from 65 to 75
        self.title_box.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border: 2px solid #5dade2;
                border-radius: 8px;
            }
        """)
        
        title_layout = QVBoxLayout(self.title_box)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignCenter)
        
        self.title_label = QLabel("PVmizer GEO")
        self.title_label.setAlignment(Qt.AlignCenter)
        # MODERATE SIZE INCREASE with original beautiful font
        title_font = QFont("Segoe UI", 24, QFont.Bold)  # Nice readable size with system font
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #5dade2;
                background-color: transparent;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(self.title_label)
        main_layout.addWidget(self.title_box)
        
        # Scroll Area for controls
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Controls Container - REMOVED TITLE
        self.controls_box = QWidget()  # Changed from QGroupBox to QWidget
        self.controls_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        controls_layout = QVBoxLayout(self.controls_box)
        controls_layout.setContentsMargins(10, 10, 10, 10)  # Adjusted margins
        controls_layout.setSpacing(0)
        controls_layout.setAlignment(Qt.AlignTop)
        
        # Stacked widget for different tab contents
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Create tab panels
        self.maps_tab = self._prepare_panel(MapsTabPanel(self.main_window))
        self.drawing_tab = self._prepare_panel(DrawingTabPanel(self.main_window))
        self.model_3d_tab = self._prepare_panel(Model3DTabPanel(self.main_window))
        
        self.stacked_widget.addWidget(self.maps_tab)
        self.stacked_widget.addWidget(self.drawing_tab)
        self.stacked_widget.addWidget(self.model_3d_tab)
        
        controls_layout.addWidget(self.stacked_widget)
        
        # Set the controls box as the scroll area widget
        self.scroll_area.setWidget(self.controls_box)
        main_layout.addWidget(self.scroll_area)
        
        # Apply comprehensive styling
        self._apply_comprehensive_styling()

    def _prepare_panel(self, panel_widget):
        """Prepare panel widget"""
        panel_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # Store reference
        if isinstance(panel_widget, MapsTabPanel):
            self.maps_tab_widget = panel_widget
        elif isinstance(panel_widget, DrawingTabPanel):
            self.drawing_tab_widget = panel_widget
        elif isinstance(panel_widget, Model3DTabPanel):
            self.model_3d_tab_widget = panel_widget
        
        return panel_widget

    def _apply_comprehensive_styling(self):
        """Apply comprehensive styling with blue buttons, enhanced outlines and properly centered titles"""
        # Clear existing styles first
        self.setStyleSheet("")
        
        # Apply new comprehensive styling with high specificity
        self.setStyleSheet("""
            /* Main Frame Background */
            QFrame#leftMenu {
                background-color: #3a4f5c !important;
                border: none !important;
            }
            
            /* Universal Background Override */
            QFrame#leftMenu * {
                background-color: #3a4f5c;
            }
            
            /* Title Box - BEAUTIFUL BIGGER BLUE TEXT */
            QFrame#leftMenu QWidget {
                background-color: #34495e;
            }
            
            QFrame#leftMenu QLabel {
                color: #5dade2 !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 24px !important;
                font-weight: bold !important;
                padding: 8px;
            }
            
            /* Scroll Area */
            QFrame#leftMenu QScrollArea {
                background-color: transparent !important;
                border: none !important;
            }
            
            QFrame#leftMenu QScrollBar:vertical {
                background-color: #2c3e50 !important;
                width: 12px;
                border-radius: 6px;
                border: 1px solid #5dade2 !important;
                margin: 0px;
            }
            
            QFrame#leftMenu QScrollBar::handle:vertical {
                background-color: #5dade2 !important;
                border-radius: 5px;
                min-height: 30px;
                margin: 1px;
            }
            
            QFrame#leftMenu QScrollBar::handle:vertical:hover {
                background-color: #48a1d6 !important;
            }
            
            QFrame#leftMenu QScrollBar::add-line:vertical, 
            QFrame#leftMenu QScrollBar::sub-line:vertical {
                background: none !important;
                border: none !important;
                height: 0px;
            }
            
            QFrame#leftMenu QScrollBar::add-page:vertical, 
            QFrame#leftMenu QScrollBar::sub-page:vertical {
                background: none !important;
            }
            
            /* Group Boxes - TITLES ON BORDER LINES - FIXED POSITIONING */
            QFrame#leftMenu QGroupBox {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
                margin-top: 15px !important;
                padding-top: 15px !important;
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-bottom: 10px !important;
                font-weight: bold !important;
                font-size: 13px !important;
                color: #ffffff !important;
            }
            
            QFrame#leftMenu QGroupBox::title {
                subcontrol-origin: margin !important;
                subcontrol-position: top center !important;
                padding: 4px 15px !important;
                margin-top: 1px !important;
                color: #5dade2 !important;
                background-color: #34495e !important;
                font-size: 20px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
            }
            
            /* Nested Group Boxes */
            QFrame#leftMenu QGroupBox QGroupBox {
                background-color: transparent !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
                margin-top: 15px !important;
                padding-top: 15px !important;
            }
            
            QFrame#leftMenu QGroupBox QGroupBox::title {
                subcontrol-origin: margin !important;
                subcontrol-position: top center !important;
                padding: 4px 10px !important;
                margin-top: -8px !important;
                color: #5dade2 !important;
                background-color: #34495e !important;
                font-size: 13px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
            }
            
            /* Time Container */
            QFrame#leftMenu QWidget#timeContainer {
                background-color: #2c3e50 !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
                padding: 10px !important;
            }
            
            /* Time Label - YELLOW */
            QFrame#leftMenu QLabel#timeLabel {
                color: #f1c40f !important;
                font-size: 32px !important;
                font-weight: bold !important;
                background-color: transparent !important;
                border: none !important;
            }
            
            /* Regular Labels - Reset to White but EXCLUDE main title */
            QFrame#leftMenu QWidget QLabel:not([objectName="mainTitle"]) {
                color: #ffffff !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 12px !important;
                font-weight: normal !important;
            }
            
            /* Description Labels */
            QFrame#leftMenu QLabel[objectName="descriptionLabel"],
            QFrame#leftMenu QLabel.description {
                color: #7f8c8d !important;
                font-size: 11px !important;
                background-color: transparent !important;
                border: none !important;
            }
            
            /* BUTTONS - WHOLE BUTTON CHANGES COLOR */
            QFrame#leftMenu QPushButton {
                background-color: #5dade2 !important;
                color: #ffffff !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 8px 12px !important;
                font-weight: bold !important;
                font-size: 13px !important;
                min-height: 32px !important;
                text-align: center !important;
            }
            
            QFrame#leftMenu QPushButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
                color: #ffffff !important;
            }
            
            QFrame#leftMenu QPushButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
                padding: 9px 11px 7px 13px !important;
            }
            
            QFrame#leftMenu QPushButton:checked {
                background-color: #e74c3c !important;
                border: 2px solid #e74c3c !important;
            }
            
            QFrame#leftMenu QPushButton:checked:hover {
                background-color: #c0392b !important;
                border: 2px solid #c0392b !important;
            }
            
            QFrame#leftMenu QPushButton:disabled {
                background-color: #7f8c8d !important;
                border: 2px solid #7f8c8d !important;
                color: #95a5a6 !important;
            }
            
            /* Focus States */
            QFrame#leftMenu QPushButton:focus {
                border: 3px solid #2980b9 !important;
                outline: none !important;
            }
            
            /* Generate Button - Red */
            QFrame#leftMenu QPushButton#generateButton:enabled {
                background-color: #e74c3c !important;
                border: 2px solid #e74c3c !important;
                color: #ffffff !important;
                font-size: 13px !important;
                font-weight: bold !important;
            }
            
            QFrame#leftMenu QPushButton#generateButton:enabled:hover {
                background-color: #c0392b !important;
                border: 2px solid #c0392b !important;
            }
            
            QFrame#leftMenu QPushButton#generateButton:enabled:pressed {
                background-color: #a93226 !important;
                border: 2px solid #a93226 !important;
            }
            
            /* Export Button - Green */
            QFrame#leftMenu QPushButton#exportButton {
                background-color: #27ae60 !important;
                border: 2px solid #27ae60 !important;
                color: #ffffff !important;
                font-size: 13px !important;
                font-weight: bold !important;
            }
            
            QFrame#leftMenu QPushButton#exportButton:hover {
                background-color: #229954 !important;
                border: 2px solid #229954 !important;
            }
            
            QFrame#leftMenu QPushButton#exportButton:pressed {
                background-color: #1e8449 !important;
                border: 2px solid #1e8449 !important;
            }
            
            /* Weather Buttons - Circular */
            QFrame#leftMenu QPushButton#weatherButton {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 27px !important;
                font-size: 24px !important;
                padding: 0px !important;
                min-width: 54px !important;
                max-width: 54px !important;
                min-height: 54px !important;
                max-height: 54px !important;
            }
            
            QFrame#leftMenu QPushButton#weatherButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
            }
            
            QFrame#leftMenu QPushButton#weatherButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
            }
            
            QFrame#leftMenu QPushButton#weatherButton:checked {
                background-color: #5dade2 !important;
                border: 2px solid #5dade2 !important;
            }
            
            QFrame#leftMenu QPushButton#weatherButton:checked:hover {
                background-color: #48a1d6 !important;
                border: 2px solid #48a1d6 !important;
            }
            
            /* Small Buttons */
            QFrame#leftMenu QPushButton.smallButton {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 5px !important;
                padding: 6px 10px !important;
                font-size: 12px !important;
                font-weight: bold !important;
                min-height: 28px !important;
            }
            
            QFrame#leftMenu QPushButton.smallButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
            }
            
            QFrame#leftMenu QPushButton.smallButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
            }
            
            /* Toggle Buttons */
            QFrame#leftMenu QPushButton.toggleButton {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 8px !important;
                font-weight: bold !important;
                font-size: 12px !important;
                min-height: 30px !important;
            }
            
            QFrame#leftMenu QPushButton.toggleButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
            }
            
            QFrame#leftMenu QPushButton.toggleButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
            }
            
            QFrame#leftMenu QPushButton.toggleButton:checked {
                background-color: #5dade2 !important;
                border: 2px solid #5dade2 !important;
                color: #ffffff !important;
            }
            
            QFrame#leftMenu QPushButton.toggleButton:checked:hover {
                background-color: #48a1d6 !important;
                border: 2px solid #48a1d6 !important;
            }
            
            /* SpinBoxes */
            QFrame#leftMenu QSpinBox, 
            QFrame#leftMenu QDoubleSpinBox {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 6px !important;
                min-height: 30px !important;
                font-size: 13px !important;
            }
            
            QFrame#leftMenu QSpinBox:focus, 
            QFrame#leftMenu QDoubleSpinBox:focus {
                border: 2px solid #48a1d6 !important;
                background-color: #2c3e50 !important;
            }
            
            QFrame#leftMenu QSpinBox::up-button, 
            QFrame#leftMenu QSpinBox::down-button,
            QFrame#leftMenu QDoubleSpinBox::up-button, 
            QFrame#leftMenu QDoubleSpinBox::down-button {
                background-color: #5dade2 !important;
                border: none !important;
                width: 20px !important;
            }
            
            /* ComboBoxes */
            QFrame#leftMenu QComboBox {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 6px !important;
                min-height: 30px !important;
                font-size: 13px !important;
            }
            
            QFrame#leftMenu QComboBox:focus {
                border: 2px solid #48a1d6 !important;
                background-color: #2c3e50 !important;
            }
            
            QFrame#leftMenu QComboBox::drop-down {
                border: none !important;
                background-color: #5dade2 !important;
                width: 25px !important;
                border-top-right-radius: 6px !important;
                border-bottom-right-radius: 6px !important;
            }
            
            QFrame#leftMenu QComboBox::down-arrow {
                image: none !important;
                border-left: 5px solid transparent !important;
                border-right: 5px solid transparent !important;
                border-top: 6px solid white !important;
                margin-right: 5px !important;
            }
            
            /* Text Fields */
            QFrame#leftMenu QLineEdit, 
            QFrame#leftMenu QTextEdit, 
            QFrame#leftMenu QPlainTextEdit {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 6px !important;
                padding: 8px !important;
                min-height: 28px !important;
                font-size: 13px !important;
            }
            
            QFrame#leftMenu QLineEdit:focus, 
            QFrame#leftMenu QTextEdit:focus, 
            QFrame#leftMenu QPlainTextEdit:focus {
                background-color: #253545 !important;
                border: none !important;
            }
            
            /* Checkboxes */
            QFrame#leftMenu QCheckBox {
                color: #ffffff !important;
                spacing: 8px !important;
                font-size: 13px !important;
                background-color: transparent !important;
            }
            
            QFrame#leftMenu QCheckBox::indicator {
                width: 20px !important;
                height: 20px !important;
                border-radius: 4px !important;
                border: 2px solid #5dade2 !important;
                background-color: #2c3e50 !important;
            }
            
            QFrame#leftMenu QCheckBox::indicator:checked {
                background-color: #5dade2 !important;
                border: 2px solid #48a1d6 !important;
            }
            
            /* Progress Bars */
            QFrame#leftMenu QProgressBar {
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                text-align: center !important;
                font-weight: bold !important;
                min-height: 25px !important;
            }
            
            QFrame#leftMenu QProgressBar::chunk {
                background-color: #5dade2 !important;
                border-radius: 4px !important;
            }
            
            /* Tab Widget */
            QFrame#leftMenu QTabWidget::pane {
                border: 2px solid #5dade2 !important;
                background-color: #34495e !important;
                border-radius: 8px !important;
                border-top-left-radius: 0px !important;
            }
            
            QFrame#leftMenu QTabBar::tab {
                background-color: #34495e !important;
                color: #b8c5ce !important;
                border: 2px solid #5dade2 !important;
                border-bottom: none !important;
                padding: 10px 20px !important;
                margin-right: 3px !important;
                border-top-left-radius: 8px !important;
                border-top-right-radius: 8px !important;
                font-size: 13px !important;
            }
            
            QFrame#leftMenu QTabBar::tab:selected {
                background-color: #5dade2 !important;
                color: #ffffff !important;
                font-weight: bold !important;
            }
            
            /* Arc Slider - BLUE COLORS */
            QFrame#leftMenu ArcSlider {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
            }
            
            QFrame#leftMenu ArcSlider::arc {
                color: #5dade2 !important;
                background-color: #5dade2 !important;
            }
            
            QFrame#leftMenu ArcSlider::handle {
                background-color: #5dade2 !important;
                border: 2px solid #48a1d6 !important;
            }
            
            QFrame#leftMenu ArcSlider::handle:hover {
                background-color: #3498db !important;
                border: 2px solid #2980b9 !important;
            }
            
            /* Special Labels */
            QFrame#leftMenu QLabel[objectName="sunriseLabel"] {
                color: #f39c12 !important;
                font-weight: bold !important;
                font-size: 13px !important;
                border: none !important;
            }
            
            QFrame#leftMenu QLabel[objectName="sunsetLabel"] {
                color: #e74c3c !important;
                font-weight: bold !important;
                font-size: 13px !important;
                border: none !important;
            }
            
            /* Stacked Widget */
            QFrame#leftMenu QStackedWidget {
                background-color: transparent !important;
                border: none !important;
            }
        """)

    def _update_title(self, tab_index):
        """Update main title with properly sized, beautiful text to show active tab"""
        if 0 <= tab_index < len(self.tab_titles):
            if self.title_label:
                # Set the title with proper styling
                self.title_label.setText(self.tab_titles[tab_index])
                # Add object name for styling exclusion
                self.title_label.setObjectName("mainTitle")

    def _connect_signals(self):
        """Connect signals from tab panels to main panel signals"""
        try:
            # Maps tab signals
            if hasattr(self, 'maps_tab_widget'):
                if hasattr(self.maps_tab_widget, 'snip_requested'):
                    self.maps_tab_widget.snip_requested.connect(self.snip_requested.emit)
            
            # Drawing tab signals
            if hasattr(self, 'drawing_tab_widget'):
                if hasattr(self.drawing_tab_widget, 'angle_snap_toggled'):
                    self.drawing_tab_widget.angle_snap_toggled.connect(self.angle_snap_toggled.emit)
                if hasattr(self.drawing_tab_widget, 'clear_drawing_requested'):
                    self.drawing_tab_widget.clear_drawing_requested.connect(self.clear_drawing_requested.emit)
                if hasattr(self.drawing_tab_widget, 'undo_requested'):
                    self.drawing_tab_widget.undo_requested.connect(self.undo_requested.emit)
                if hasattr(self.drawing_tab_widget, 'generate_model_requested'):
                    self.drawing_tab_widget.generate_model_requested.connect(self.generate_model_requested.emit)
            
            # Model 3D tab signals
            if hasattr(self, 'model_3d_tab_widget'):
                if hasattr(self.model_3d_tab_widget, 'solar_parameter_changed'):
                    self.model_3d_tab_widget.solar_parameter_changed.connect(self.solar_parameter_changed.emit)
                if hasattr(self.model_3d_tab_widget, 'animation_toggled'):
                    self.model_3d_tab_widget.animation_toggled.connect(self.animation_toggled.emit)
            
        except Exception as e:
            pass

    # Public API methods
    def switch_to_tab_content(self, tab_index):
        """Switch panel content based on active tab"""
        try:
            if self.stacked_widget and 0 <= tab_index < self.stacked_widget.count():
                self.stacked_widget.setCurrentIndex(tab_index)
                self.current_tab_index = tab_index
                
                self._update_title(tab_index)
                
                # Reset scroll position
                if self.scroll_area:
                    self.scroll_area.verticalScrollBar().setValue(0)
                
                if tab_index == 1 and hasattr(self, 'drawing_tab_widget'):
                    QTimer.singleShot(100, self.drawing_tab_widget._check_completion)
                    
        except Exception as e:
            pass

    def enable_generate_button(self):
        """Enable generate button when polygon is complete"""
        self.polygon_complete = True
        if hasattr(self, 'drawing_tab_widget') and hasattr(self.drawing_tab_widget, 'enable_generate_button'):
            self.drawing_tab_widget.enable_generate_button()

    def disable_generate_button(self):
        """Disable generate button"""
        self.polygon_complete = False
        if hasattr(self, 'drawing_tab_widget') and hasattr(self.drawing_tab_widget, 'disable_generate_button'):
            self.drawing_tab_widget.disable_generate_button()

    def update_polygon_info(self, measurements):
        """Update polygon information from external sources"""
        if hasattr(self, 'drawing_tab_widget') and hasattr(self.drawing_tab_widget, 'update_polygon_info'):
            self.drawing_tab_widget.update_polygon_info(measurements)

    def reset_drawing_measurements(self):
        """Reset drawing measurements"""
        if hasattr(self, 'drawing_tab_widget') and hasattr(self.drawing_tab_widget, 'reset_measurements'):
            self.drawing_tab_widget.reset_measurements()

    def get_current_tab_index(self):
        """Get current active tab index"""
        return self.current_tab_index
