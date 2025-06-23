#!/usr/bin/env python3
"""
Updated Left Control Panel - With expandable tips and improved functionality
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QStackedWidget, 
                            QSizePolicy, QGroupBox, QPushButton, QWidget)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont

# Import separated tab panels
from ui.panel.maps_tab_left import MapsTabPanel
from ui.panel.drawing_tab_left import DrawingTabPanel
from ui.panel.model_tab_left import Model3DTabPanel

class ExpandableTipsWidget(QWidget):
    """Expandable tips widget with smooth animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = False
        self.tips_content = None
        self.toggle_btn = None
        self.content_widget = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup expandable tips UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toggle button header
        self.toggle_btn = QPushButton("💡 Tips (Click to expand)")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self._toggle_expanded)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px 8px 0px 0px;
                color: #856404;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #fff2a8;
            }
            QPushButton:checked {
                border-radius: 8px 8px 0px 0px;
                border-bottom: none;
            }
        """)
        main_layout.addWidget(self.toggle_btn)
        
        # Content widget (initially hidden)
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-top: none;
                border-radius: 0px 0px 8px 8px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(12, 8, 12, 12)
        
        self.tips_content = QLabel("Ready to start.")
        self.tips_content.setWordWrap(True)
        self.tips_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.tips_content.setStyleSheet("""
            QLabel {
                color: #856404;
                background-color: transparent;
                font-size: 11px;
                line-height: 1.4;
                padding: 8px;
                font-weight: normal;
                border: none;
            }
        """)
        content_layout.addWidget(self.tips_content)
        
        main_layout.addWidget(self.content_widget)
        
        # Initially hide content
        self.content_widget.setMaximumHeight(0)
        self.content_widget.setVisible(False)
    
    def _toggle_expanded(self):
        """Toggle expanded state with animation"""
        self.expanded = self.toggle_btn.isChecked()
        
        if self.expanded:
            self.toggle_btn.setText("💡 Tips (Click to collapse)")
            self.content_widget.setVisible(True)
            self.content_widget.setMaximumHeight(300)  # Allow expansion
        else:
            self.toggle_btn.setText("💡 Tips (Click to expand)")
            self.content_widget.setMaximumHeight(0)
            QTimer.singleShot(200, lambda: self.content_widget.setVisible(False))
    
    def set_tips_text(self, text):
        """Set tips content text"""
        if self.tips_content:
            self.tips_content.setText(text)

class LeftControlPanel(QFrame):
    """Main Left Control Panel with separated tab components and expandable tips"""
    
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
        self.title_label = None
        self.tips_widget = None
        self.stacked_widget = None
        self.maps_tab = None
        self.drawing_tab = None
        self.model_3d_tab = None
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        
        print("✅ Left Control Panel initialized with expandable tips")
    
    def _setup_ui(self):
        """Setup main UI structure"""
        self.setObjectName("leftMenu")
        self.setMinimumWidth(360)
        self.setMaximumWidth(360)
        self.setFrameStyle(QFrame.StyledPanel)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Dynamic title label
        self.title_label = QLabel("PVmizer GEO")
        self.title_label.setObjectName("menuTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #2c3e50;
                padding: 12px;
                font-weight: bold;
                border-radius: 8px;
                border: 2px solid #3498db;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(self.title_label)
        
        # Tab-specific content stack
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create and add tab panels
        self.maps_tab = MapsTabPanel(self.main_window)
        self.drawing_tab = DrawingTabPanel(self.main_window)
        self.model_3d_tab = Model3DTabPanel(self.main_window)
        
        self.stacked_widget.addWidget(self.maps_tab)      # Index 0
        self.stacked_widget.addWidget(self.drawing_tab)   # Index 1
        self.stacked_widget.addWidget(self.model_3d_tab)  # Index 2
        
        main_layout.addWidget(self.stacked_widget)
        
        # Expandable tips section
        self.tips_widget = ExpandableTipsWidget()
        main_layout.addWidget(self.tips_widget)
        
        # Set initial state
        self.stacked_widget.setCurrentIndex(0)
        self._update_tips_content(0)
        
        print("✓ UI setup complete with expandable tips")
    
    def _connect_signals(self):
        """Connect signals from tab components to main panel signals"""
        try:
            # Maps tab signals
            if self.maps_tab and hasattr(self.maps_tab, 'snip_requested'):
                self.maps_tab.snip_requested.connect(self.snip_requested.emit)
            
            # Drawing tab signals
            if self.drawing_tab:
                if hasattr(self.drawing_tab, 'scale_changed'):
                    self.drawing_tab.scale_changed.connect(self.scale_changed.emit)
                if hasattr(self.drawing_tab, 'angle_snap_toggled'):
                    self.drawing_tab.angle_snap_toggled.connect(self.angle_snap_toggled.emit)
                if hasattr(self.drawing_tab, 'clear_drawing_requested'):
                    self.drawing_tab.clear_drawing_requested.connect(self.clear_drawing_requested.emit)
                if hasattr(self.drawing_tab, 'undo_requested'):
                    self.drawing_tab.undo_requested.connect(self.undo_requested.emit)
                if hasattr(self.drawing_tab, 'generate_model_requested'):
                    self.drawing_tab.generate_model_requested.connect(self.generate_model_requested.emit)
            
            # 3D model tab signals
            if self.model_3d_tab:
                if hasattr(self.model_3d_tab, 'building_parameter_changed'):
                    self.model_3d_tab.building_parameter_changed.connect(self.building_parameter_changed.emit)
                if hasattr(self.model_3d_tab, 'solar_parameter_changed'):
                    self.model_3d_tab.solar_parameter_changed.connect(self.solar_parameter_changed.emit)
                if hasattr(self.model_3d_tab, 'export_model_requested'):
                    self.model_3d_tab.export_model_requested.connect(self.export_model_requested.emit)
                if hasattr(self.model_3d_tab, 'animation_toggled'):
                    self.model_3d_tab.animation_toggled.connect(self.animation_toggled.emit)
            
            # Tab switching
            if hasattr(self.main_window, 'content_tabs'):
                content_tabs = self.main_window.content_tabs
                if hasattr(content_tabs, 'currentChanged'):
                    content_tabs.currentChanged.connect(self.switch_to_tab_content)
                    print("✓ Tab switching signal connected")
                    
        except Exception as e:
            print(f"❌ Error connecting signals: {e}")
    
    def _update_tips_content(self, tab_index):
        """Update tips content based on active tab"""
        if not self.tips_widget:
            return
        
        tips_texts = [
            """🗺️ Getting Started:
• Navigate to building location on map
• Adjust zoom for best detail
• Click 'Snip Screenshot' to capture area
• Use satellite view for best building visibility

📐 Pro Tips:
• Center building in view before snipping
• Higher zoom = more detailed measurements
• Satellite view shows building outlines clearly
• Good lighting helps with edge detection""",
            
            """✏️ Drawing Process:
• Set correct scale first (m/pixel)
• Click points to draw building outline
• Enable angle snap for 90° precision
• Minimum 3 points needed for polygon

📐 Pro Tips:
• Click accurately on building corners
• Work clockwise or counter-clockwise consistently
• Close polygon by clicking near first point
• Use Clear button to restart if needed
• Check scale before starting to draw""",
            
            """🏗️ 3D Model & Solar:
• Adjust building parameters with controls
• Generate 3D model from polygon first
• Fine-tune solar simulation settings
• Export model when satisfied with result

📐 Pro Tips:
• Wall height affects solar calculations significantly
• Roof type impacts energy generation potential
• Time/date settings change sun position
• Animation shows daily solar movement patterns
• Export includes all current settings"""
        ]
        
        if 0 <= tab_index < len(tips_texts):
            self.tips_widget.set_tips_text(tips_texts[tab_index])
    
    def _update_title(self, tab_index):
        """Update title based on active tab"""
        if self.title_label and 0 <= tab_index < len(self.tab_titles):
            self.title_label.setText(self.tab_titles[tab_index])
            print(f"✓ Title updated to: {self.tab_titles[tab_index]}")
    
    # Public API methods
    def switch_to_tab_content(self, tab_index):
        """Switch panel content based on active tab"""
        try:
            if self.stacked_widget and 0 <= tab_index < self.stacked_widget.count():
                self.stacked_widget.setCurrentIndex(tab_index)
                self.current_tab_index = tab_index
                
                # Update title and tips
                self._update_title(tab_index)
                self._update_tips_content(tab_index)
                
                print(f"✓ Left panel switched to tab {tab_index} - {self.tab_titles[tab_index] if tab_index < len(self.tab_titles) else 'Unknown'}")
                
                if tab_index == 1 and self.drawing_tab:  # Drawing tab
                    QTimer.singleShot(100, self.drawing_tab._check_completion)
                    
        except Exception as e:
            print(f"❌ Error switching left panel tab: {e}")
    
    def enable_generate_button(self):
        """Enable generate button when polygon is complete"""
        self.polygon_complete = True
        if self.drawing_tab and hasattr(self.drawing_tab, 'enable_generate_button'):
            self.drawing_tab.enable_generate_button()
    
    def disable_generate_button(self):
        """Disable generate button"""
        self.polygon_complete = False
        if self.drawing_tab and hasattr(self.drawing_tab, 'disable_generate_button'):
            self.drawing_tab.disable_generate_button()
    
    def update_polygon_info(self, measurements):
        """Update polygon information from external sources"""
        if self.drawing_tab and hasattr(self.drawing_tab, 'update_polygon_info'):
            self.drawing_tab.update_polygon_info(measurements)
    
    def reset_drawing_measurements(self):
        """Reset drawing measurements"""
        if self.drawing_tab and hasattr(self.drawing_tab, 'reset_measurements'):
            self.drawing_tab.reset_measurements()
    
    # Parameter getters (delegate to appropriate tab)
    def get_wall_height(self):
        """Get current wall height in meters"""
        if self.model_3d_tab and hasattr(self.model_3d_tab, 'get_wall_height'):
            return self.model_3d_tab.get_wall_height()
        return 3.0  # Default
    
    def get_roof_type(self):
        """Get current roof type"""
        if self.model_3d_tab and hasattr(self.model_3d_tab, 'get_roof_type'):
            return self.model_3d_tab.get_roof_type()
        return "flat"  # Default
    
    def get_roof_pitch(self):
        """Get current roof pitch in degrees"""
        if self.model_3d_tab and hasattr(self.model_3d_tab, 'get_roof_pitch'):
            return self.model_3d_tab.get_roof_pitch()
        return 30.0  # Default
    
    def get_scale_factor(self):
        """Get current scale factor"""
        if self.drawing_tab and hasattr(self.drawing_tab, 'get_scale_factor'):
            return self.drawing_tab.get_scale_factor()
        return 0.05  # Default
    
    def get_time_of_day(self):
        """Get current time of day"""
        if self.model_3d_tab and hasattr(self.model_3d_tab, 'get_time_of_day'):
            return self.model_3d_tab.get_time_of_day()
        return 12.0  # Default noon
    
    def get_day_of_year(self):
        """Get current day of year"""
        if self.model_3d_tab and hasattr(self.model_3d_tab, 'get_day_of_year'):
            return self.model_3d_tab.get_day_of_year()
        return 172  # Default summer solstice
    
    def is_angle_snap_enabled(self):
        """Check if angle snap is enabled"""
        if self.drawing_tab and hasattr(self.drawing_tab, 'is_angle_snap_enabled'):
            return self.drawing_tab.is_angle_snap_enabled()
        return True  # Default
    
    def get_current_measurements(self):
        """Get current polygon measurements"""
        if self.drawing_tab and hasattr(self.drawing_tab, 'get_current_measurements'):
            return self.drawing_tab.get_current_measurements()
        return {'points': 0, 'area': 0.0, 'perimeter': 0.0, 'is_complete': False}
    
    def is_polygon_complete(self):
        """Check if polygon is complete"""
        if self.drawing_tab and hasattr(self.drawing_tab, 'is_polygon_complete'):
            return self.drawing_tab.is_polygon_complete()
        return False
    
    # Cleanup
    def cleanup(self):
        """Cleanup resources"""
        try:
            print("🧹 Cleaning up Left Control Panel...")
            
            # Cleanup individual tabs
            if self.maps_tab and hasattr(self.maps_tab, 'cleanup'):
                self.maps_tab.cleanup()
            
            if self.drawing_tab and hasattr(self.drawing_tab, 'cleanup'):
                self.drawing_tab.cleanup()
            
            if self.model_3d_tab and hasattr(self.model_3d_tab, 'cleanup'):
                self.model_3d_tab.cleanup()
            
            # Clear references
            self.main_window = None
            self.title_label = None
            self.tips_widget = None
            self.stacked_widget = None
            self.maps_tab = None
            self.drawing_tab = None
            self.model_3d_tab = None
            
            print("✅ Left Control Panel cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during Left Control Panel cleanup: {e}")

    def connect_model_tab_to_left_panel(self):
        """Connect left panel controls to model tab"""
        try:
            # Get model tab
            if hasattr(self, 'content_tabs'):
                model_tab = self.content_tabs.widget(2)  # Model tab index
                
                # Get left panel 3D section
                if hasattr(self, 'left_panel') and hasattr(self.left_panel, 'model_3d_tab'):
                    left_panel_3d = self.left_panel.model_3d_tab
                    
                    # Connect parameter changes
                    left_panel_3d.building_parameter_changed.connect(
                        model_tab.update_building_parameter
                    )
                    
                    print("✅ Model tab connected to left panel")
                    
        except Exception as e:
            print(f"❌ Error connecting model tab to left panel: {e}")
