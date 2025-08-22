#!/usr/bin/env python3
"""
Updated Left Control Panel - Blue buttons, centered titles, scrollable content
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
        
        # Tab titles
        self.tab_titles = [
            "PVmizer GEO",      # Maps tab (main view)
            "Drawing Tools",    # Drawing tab
            "3D Model View"     # 3D Model tab
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
        
        print("✅ Left Control Panel initialized")
    
    def _setup_ui(self):
        """Setup main UI structure with scrollable content"""
        self.setObjectName("leftMenu")
        
        # Panel width
        PANEL_WIDTH = 450
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
        
        # Title Box with light blue border
        self.title_box = QWidget()
        self.title_box.setFixedHeight(50)
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
        title_font = QFont("Arial", 16, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                padding: 5px;
            }
        """)
        title_layout.addWidget(self.title_label)
        main_layout.addWidget(self.title_box)
        
        # Scroll Area for controls
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Controls Container with light blue border and centered title
        self.controls_box = QGroupBox("Maps Controls")
        self.controls_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        controls_layout = QVBoxLayout(self.controls_box)
        controls_layout.setContentsMargins(10, 20, 10, 10)
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
        """Apply comprehensive styling with blue buttons and centered titles"""
        self.setStyleSheet(self.styleSheet() + """
            /* Main background */
            * {
                background-color: #3a4f5c;
            }
            
            /* Scroll Area */
            QScrollArea {
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
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Main Controls Container - Centered title between lines */
            QGroupBox {
                background-color: #34495e;
                border: 2px solid #5dade2;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 25px;
                padding-left: 10px;
                padding-right: 10px;
                padding-bottom: 10px;
                font-weight: bold;
                font-size: 13px;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 15px;
                margin-top: -12px;
                color: #5dade2;
                background-color: #34495e;
                font-size: 14px;
            }
            
            /* Nested Group Boxes - Centered titles */
            QGroupBox QGroupBox {
                background-color: transparent;
                border: 2px solid #5dade2;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
            }
            
            QGroupBox QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                margin-top: -10px;
                color: #5dade2;
                background-color: #34495e;
                font-size: 13px;
            }
            
            /* Time container */
            QWidget#timeContainer {
                background-color: #2c3e50;
                border: 2px solid #5dade2;
                border-radius: 8px;
                padding: 10px;
            }
            
            /* Time Label - Light blue */
            QLabel#timeLabel {
                color: #5dade2 !important;
                font-size: 32px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
            
            /* Regular Labels */
            QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            
            /* Description labels - gray */
            QLabel[objectName="descriptionLabel"],
            QLabel.description {
                color: #7f8c8d;
                font-size: 11px;
                background-color: transparent;
                border: none !important;
            }
            
            /* Buttons - Beautiful blue like in screenshots */
            QPushButton {
                background-color: #5dade2;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                min-height: 40px;
                text-align: center;
            }
            
            QPushButton:hover {
                background-color: #48a1d6;
            }
            
            QPushButton:pressed {
                background-color: #3498db;
                padding: 13px 11px 11px 13px;
            }
            
            QPushButton:checked {
                background-color: #e74c3c;
            }
            
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #95a5a6;
            }
            
            /* Weather Buttons - Circular */
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
            }
            
            QPushButton#weatherButton:hover {
                background-color: rgba(93, 173, 226, 0.2);
                border: 2px solid #48a1d6;
            }
            
            QPushButton#weatherButton:checked {
                background-color: #5dade2;
                border: 2px solid #48a1d6;
            }
            
            /* SpinBoxes and DoubleSpinBoxes */
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
            
            /* Text fields - NO BORDERS */
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #2c3e50;
                color: #ffffff;
                border: none !important;
                border-radius: 6px;
                padding: 8px;
                min-height: 28px;
                font-size: 13px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                background-color: #253545;
                border: none !important;
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
            
            /* Arc Slider */
            ArcSlider {
                background-color: #34495e;
                border: 2px solid #5dade2;
                border-radius: 8px;
            }
            
            /* Special labels */
            QLabel[objectName="sunriseLabel"] {
                color: #f39c12;
                font-weight: bold;
                font-size: 13px;
                border: none !important;
            }
            
            QLabel[objectName="sunsetLabel"] {
                color: #e74c3c;
                font-weight: bold;
                font-size: 13px;
                border: none !important;
            }
        """)
    
    def _update_title(self, tab_index):
        """Update main title and controls box title"""
        if 0 <= tab_index < len(self.tab_titles):
            if self.title_label:
                self.title_label.setText(self.tab_titles[tab_index])
            
            # Update controls box title
            if self.controls_box:
                titles = ["Maps Controls", "Drawing Controls", "3D Model Controls"]
                self.controls_box.setTitle(titles[tab_index])
    
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
            
            print("✅ All tab panel signals connected successfully")
            
        except Exception as e:
            print(f"❌ Error connecting tab panel signals: {e}")
    
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
                
                print(f"✓ Left panel switched to tab {tab_index}")
                
                if tab_index == 1 and hasattr(self, 'drawing_tab_widget'):
                    QTimer.singleShot(100, self.drawing_tab_widget._check_completion)
                    
        except Exception as e:
            print(f"❌ Error switching left panel tab: {e}")
    
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
