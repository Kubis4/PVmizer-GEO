#!/usr/bin/env python3
"""
Left Control Panel - Simplified for Default, Model, and Overview Tabs
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QWidget, QScrollArea, 
                             QSizePolicy, QStackedWidget)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

# Import all three panels
from ui.panel.default_tab_left import DefaultTabPanel
from ui.panel.model_tab_left.model_3d_tab_panel import Model3DTabPanel
from ui.panel.overview_tab_left import OverviewTabPanel


class LeftControlPanel(QFrame):
    """Main Left Control Panel - Default, Model, and Overview Tabs"""

    # Signals
    solar_parameter_changed = pyqtSignal(str, object)
    animation_toggled = pyqtSignal(bool)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # State tracking
        self.current_tab_index = 0
        
        # Title
        self.panel_title = "PVmizer GEO"
        
        # UI components
        self.title_box = None
        self.title_label = None
        self.scroll_area = None
        self.stacked_widget = None
        self.default_tab = None
        self.model_3d_tab = None
        self.overview_tab = None
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup main UI structure with scrollable content"""
        self.setObjectName("leftMenu")
        
        # Panel width
        PANEL_WIDTH = 500
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
        
        # Title Box
        self.title_box = QWidget()
        self.title_box.setFixedHeight(75)
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
        
        self.title_label = QLabel(self.panel_title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("mainTitle")
        
        title_font = QFont("Segoe UI", 24, QFont.Bold)
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
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Stacked Widget for switching panels
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # Create all three tab panels
        self.default_tab = self._prepare_panel(DefaultTabPanel(self.main_window))
        self.model_3d_tab = self._prepare_panel(Model3DTabPanel(self.main_window))
        self.overview_tab = self._prepare_panel(OverviewTabPanel(self.main_window))
        
        # Add panels to stacked widget
        self.stacked_widget.addWidget(self.default_tab)      # Index 0
        self.stacked_widget.addWidget(self.model_3d_tab)     # Index 1
        self.stacked_widget.addWidget(self.overview_tab)     # Index 2
        
        # Set initial panel to Default
        self.stacked_widget.setCurrentIndex(0)
        
        # Set stacked widget as scroll area widget
        self.scroll_area.setWidget(self.stacked_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Apply comprehensive styling
        self._apply_comprehensive_styling()

    def _prepare_panel(self, panel_widget):
        """Prepare panel widget"""
        panel_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # Store reference
        if isinstance(panel_widget, DefaultTabPanel):
            self.default_tab_widget = panel_widget
        elif isinstance(panel_widget, Model3DTabPanel):
            self.model_3d_tab_widget = panel_widget
        elif isinstance(panel_widget, OverviewTabPanel):
            self.overview_tab_widget = panel_widget
        
        return panel_widget

    def switch_to_tab_content(self, tab_index):
        """Switch the left panel content based on the active tab
        
        Args:
            tab_index (int): 0 for Default, 1 for Model, 2 for Overview
        """
        try:
            self.current_tab_index = tab_index
            
            if self.stacked_widget:
                # Switch to the corresponding panel
                self.stacked_widget.setCurrentIndex(tab_index)
                
                # Update title and status
                if tab_index == 0:
                    print("🏠 Switched to Default panel")
                elif tab_index == 1:
                    print("🏗️ Switched to Model panel")
                elif tab_index == 2:
                    print("📊 Switched to Overview panel")
                    # Refresh overview data when switching to it
                    if hasattr(self, 'overview_tab_widget'):
                        if hasattr(self.overview_tab_widget, 'refresh_data'):
                            self.overview_tab_widget.refresh_data()
                    
        except Exception as e:
            print(f"❌ Error switching panel content: {e}")

    def _apply_comprehensive_styling(self):
        """Apply comprehensive styling with blue buttons and enhanced outlines"""
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
            
            /* Title Box */
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
            
            /* Group Boxes */
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
            
            /* Regular Labels */
            QFrame#leftMenu QWidget QLabel:not([objectName="mainTitle"]) {
                color: #ffffff !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 12px !important;
                font-weight: normal !important;
            }
            
            /* BUTTONS */
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
            
            QFrame#leftMenu QPushButton:disabled {
                background-color: #7f8c8d !important;
                border: 2px solid #7f8c8d !important;
                color: #95a5a6 !important;
            }
            
            /* Export Button - Green */
            QFrame#leftMenu QPushButton#exportButton {
                background-color: #27ae60 !important;
                border: 2px solid #27ae60 !important;
                color: #ffffff !important;
            }
            
            QFrame#leftMenu QPushButton#exportButton:hover {
                background-color: #229954 !important;
                border: 2px solid #229954 !important;
            }
            
            QFrame#leftMenu QPushButton#exportButton:pressed {
                background-color: #1e8449 !important;
                border: 2px solid #1e8449 !important;
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
            }
            
            QFrame#leftMenu QSpinBox::up-button, 
            QFrame#leftMenu QSpinBox::down-button,
            QFrame#leftMenu QDoubleSpinBox::up-button, 
            QFrame#leftMenu QDoubleSpinBox::down-button {
                background-color: #5dade2 !important;
                border: none !important;
                width: 20px !important;
            }
            
            QFrame#leftMenu QSpinBox::up-button:hover, 
            QFrame#leftMenu QSpinBox::down-button:hover,
            QFrame#leftMenu QDoubleSpinBox::up-button:hover, 
            QFrame#leftMenu QDoubleSpinBox::down-button:hover {
                background-color: #3498db !important;
            }
            
            QFrame#leftMenu QSpinBox::up-arrow,
            QFrame#leftMenu QDoubleSpinBox::up-arrow {
                image: none !important;
                border-left: 4px solid transparent !important;
                border-right: 4px solid transparent !important;
                border-bottom: 5px solid white !important;
                margin-top: 2px !important;
            }
            
            QFrame#leftMenu QSpinBox::down-arrow,
            QFrame#leftMenu QDoubleSpinBox::down-arrow {
                image: none !important;
                border-left: 4px solid transparent !important;
                border-right: 4px solid transparent !important;
                border-top: 5px solid white !important;
                margin-bottom: 2px !important;
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
            
            QFrame#leftMenu QComboBox QAbstractItemView {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                selection-background-color: #5dade2 !important;
                selection-color: #ffffff !important;
                border: 2px solid #5dade2 !important;
            }
        """)


    def _connect_signals(self):
        """Connect signals from tab panels"""
        try:
            # Model 3D tab signals
            if hasattr(self, 'model_3d_tab_widget'):
                if hasattr(self.model_3d_tab_widget, 'solar_parameter_changed'):
                    self.model_3d_tab_widget.solar_parameter_changed.connect(
                        self.solar_parameter_changed.emit
                    )
                if hasattr(self.model_3d_tab_widget, 'animation_toggled'):
                    self.model_3d_tab_widget.animation_toggled.connect(
                        self.animation_toggled.emit
                    )
        except Exception as e:
            print(f"Error connecting signals: {e}")

    def get_current_tab_index(self):
        """Get current active tab index"""
        return self.current_tab_index
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'default_tab_widget') and self.default_tab_widget:
                if hasattr(self.default_tab_widget, 'cleanup'):
                    self.default_tab_widget.cleanup()
            
            if hasattr(self, 'model_3d_tab_widget') and self.model_3d_tab_widget:
                if hasattr(self.model_3d_tab_widget, 'cleanup'):
                    self.model_3d_tab_widget.cleanup()
            
            if hasattr(self, 'overview_tab_widget') and self.overview_tab_widget:
                if hasattr(self.overview_tab_widget, 'cleanup'):
                    self.overview_tab_widget.cleanup()
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")
