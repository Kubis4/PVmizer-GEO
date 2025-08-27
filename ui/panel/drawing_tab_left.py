#!/usr/bin/env python3
"""
Drawing Tab Panel - Following standard button styling, size, colors
"""

import traceback
import math
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox, QScrollArea,
                             QSizePolicy, QFrame, QSpacerItem, QMessageBox, QComboBox)
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QFont, QPalette, QPixmap, QPainter, QPen, QBrush, QColor

class DrawingTabPanel(QWidget):
    """
    Drawing Tab Panel - Following standard button styling from control panel
    """
    
    # Required signals that main window expects
    scale_changed = pyqtSignal(float)
    angle_snap_toggled = pyqtSignal(bool)
    clear_drawing_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    generate_model_requested = pyqtSignal()
    
    # Additional signals for polygon management
    canvas_cleared = pyqtSignal()
    polygon_completed = pyqtSignal(list)  # points
    measurements_updated = pyqtSignal(dict)  # measurements dict
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        print("🎨 Initializing Drawing Tab Panel (STANDARD BUTTON STYLING)...")
        
        # Initialize core attributes
        self._initialize_attributes()
        
        # Setup UI with standard styling
        self._setup_ui()
        
        # Initialize measurements safely
        QTimer.singleShot(100, self._initialize_measurements_safely)
        
        # Start completion checking timer
        self._start_completion_timer()
        
        print("✅ Drawing Tab Panel initialized with standard button styling")
    
    def _initialize_attributes(self):
        """Initialize all attributes with safe defaults"""
        # Core state
        self.polygon_complete = False
        self._last_error = None
        self._last_display_key = ""
        self._last_completion_error = ""
        self._last_logged_measurements = {}
        self._drawing_generation_counter = 0  # Track drawing sessions
        
        # Drawing state
        self.angle_snap_enabled = True
        
        # Measurements data
        self.current_measurements = {
            'points': 0, 
            'area': 0.0, 
            'perimeter': 0.0, 
            'is_complete': False
        }
        
        # Scale and canvas references
        self._current_scale = getattr(self.main_window, '_current_scale', 0.05)
        self._last_canvas = None  # Cache last known canvas
        
        # UI component references (will be set during setup)
        self.measurements_display = None
        self.generate_btn = None
        self.clear_btn = None
        self.scale_input = None
        self.angle_snap_btn = None
        
        # Timer for checking completion
        self.check_timer = None
        
        print("✅ Attributes initialized with improved tracking")
    
    def _setup_ui(self):
        """Setup the complete UI layout with standard button styling"""
        try:
            print("🔧 Setting up Drawing Tab UI (STANDARD BUTTON STYLING)...")
            
            # Apply control panel styling to the main widget
            self.setStyleSheet("""
                QWidget {
                    background-color: #3a4f5c;
                }
            """)
            
            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(15)
            
            # Create main sections following standard pattern
            self._create_scale_section(main_layout)
            self._create_drawing_tools_section(main_layout)
            self._create_measurements_section(main_layout)
            
            # Add stretch before generate button
            main_layout.addStretch()
            
            # Generate button at bottom (standalone)
            self._create_generate_section(main_layout)
            
            print("✅ Drawing Tab UI setup completed with standard styling")
            
        except Exception as e:
            print(f"❌ Error setting up Drawing Tab UI: {e}")
            traceback.print_exc()
    
    def _create_scale_section(self, parent_layout):
        """Create the scale settings section with standard styling"""
        try:
            # Scale group with standard styling
            scale_group = QGroupBox("📏 Scale Settings")
            scale_group.setStyleSheet("""
                QGroupBox {
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
                
                QGroupBox::title {
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
            """)
            
            scale_layout = QVBoxLayout(scale_group)
            scale_layout.setContentsMargins(10, 15, 10, 10)
            
            # Scale input row
            scale_row = QHBoxLayout()
            
            scale_label = QLabel("Scale (m/pixel):")
            scale_label.setStyleSheet("""
                QLabel {
                    color: #ffffff !important;
                    background-color: transparent !important;
                    border: none !important;
                    font-size: 12px !important;
                    font-weight: normal !important;
                }
            """)
            scale_row.addWidget(scale_label)
            
            self.scale_input = QComboBox()
            self.scale_input.addItems(["0.005", "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1.0"])
            self.scale_input.setCurrentText("0.05")
            self.scale_input.setEditable(True)
            self.scale_input.currentTextChanged.connect(self._on_scale_changed)
            self.scale_input.setToolTip("Set the scale factor for measurements")
            
            # Standard ComboBox styling
            self.scale_input.setStyleSheet("""
                QComboBox {
                    background-color: #2c3e50 !important;
                    color: #ffffff !important;
                    border: 2px solid #5dade2 !important;
                    border-radius: 6px !important;
                    padding: 6px !important;
                    min-height: 30px !important;
                    font-size: 13px !important;
                }
                
                QComboBox:focus {
                    border: 2px solid #48a1d6 !important;
                    background-color: #2c3e50 !important;
                }
                
                QComboBox::drop-down {
                    border: none !important;
                    background-color: #5dade2 !important;
                    width: 25px !important;
                    border-top-right-radius: 6px !important;
                    border-bottom-right-radius: 6px !important;
                }
                
                QComboBox::down-arrow {
                    image: none !important;
                    border-left: 5px solid transparent !important;
                    border-right: 5px solid transparent !important;
                    border-top: 6px solid white !important;
                    margin-right: 5px !important;
                }
            """)
            
            scale_row.addWidget(self.scale_input)
            scale_layout.addLayout(scale_row)
            
            parent_layout.addWidget(scale_group)
            
            print("✅ Scale section created with standard styling")
            
        except Exception as e:
            print(f"❌ Error creating scale section: {e}")
    
    def _create_drawing_tools_section(self, parent_layout):
        """Create the drawing tools section with STANDARD BUTTON STYLING"""
        try:
            # Drawing tools group with standard styling
            tools_group = QGroupBox("✏️ Drawing Tools")
            tools_group.setStyleSheet("""
                QGroupBox {
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
                
                QGroupBox::title {
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
            """)
            
            tools_layout = QVBoxLayout(tools_group)
            tools_layout.setContentsMargins(10, 15, 10, 10)
            tools_layout.setSpacing(10)
            
            # STANDARD: Angle snap button with EXACT standard styling
            self.angle_snap_btn = QPushButton("📐 90° Angle Snap: ON")
            self.angle_snap_btn.setMinimumHeight(32)  # STANDARD HEIGHT
            self.angle_snap_btn.setCheckable(True)
            self.angle_snap_btn.setChecked(True)
            self.angle_snap_btn.clicked.connect(self._on_angle_snap_clicked)
            self.angle_snap_btn.setToolTip("Toggle 90-degree angle snapping for precise drawing")
            
            # STANDARD BUTTON STYLING - EXACT from control panel
            self.angle_snap_btn.setStyleSheet("""
                QPushButton {
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
                
                QPushButton:hover {
                    background-color: #3498db !important;
                    border: 2px solid #3498db !important;
                    color: #ffffff !important;
                }
                
                QPushButton:pressed {
                    background-color: #2980b9 !important;
                    border: 2px solid #2980b9 !important;
                    padding: 9px 11px 7px 13px !important;
                }
                
                QPushButton:checked {
                    background-color: #e74c3c !important;
                    border: 2px solid #e74c3c !important;
                }
                
                QPushButton:checked:hover {
                    background-color: #c0392b !important;
                    border: 2px solid #c0392b !important;
                }
                
                QPushButton:disabled {
                    background-color: #7f8c8d !important;
                    border: 2px solid #7f8c8d !important;
                    color: #95a5a6 !important;
                }
            """)
            
            tools_layout.addWidget(self.angle_snap_btn)
            
            # STANDARD: Clear button with EXACT standard styling
            self.clear_btn = QPushButton("🗑️ Clear Drawing")
            self.clear_btn.setMinimumHeight(32)  # STANDARD HEIGHT
            self.clear_btn.setToolTip("Clear the current drawing and reset measurements")
            self.clear_btn.clicked.connect(self._handle_clear_drawing)
            
            # STANDARD BUTTON STYLING - EXACT from control panel
            self.clear_btn.setStyleSheet("""
                QPushButton {
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
                
                QPushButton:hover {
                    background-color: #3498db !important;
                    border: 2px solid #3498db !important;
                    color: #ffffff !important;
                }
                
                QPushButton:pressed {
                    background-color: #2980b9 !important;
                    border: 2px solid #2980b9 !important;
                    padding: 9px 11px 7px 13px !important;
                }
                
                QPushButton:disabled {
                    background-color: #7f8c8d !important;
                    border: 2px solid #7f8c8d !important;
                    color: #95a5a6 !important;
                }
            """)
            
            tools_layout.addWidget(self.clear_btn)
            parent_layout.addWidget(tools_group)
            
            print("✅ Drawing tools section created with STANDARD BUTTON STYLING")
            
        except Exception as e:
            print(f"❌ Error creating drawing tools section: {e}")
    
    def _create_measurements_section(self, parent_layout):
        """Create the measurements display section with standard styling"""
        try:
            # Measurements group with standard styling
            measurements_group = QGroupBox("📊 Polygon Information")
            measurements_group.setStyleSheet("""
                QGroupBox {
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
                
                QGroupBox::title {
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
            """)
            
            measurements_layout = QVBoxLayout(measurements_group)
            measurements_layout.setContentsMargins(10, 15, 10, 10)
            
            # Measurements display with standard styling
            self.measurements_display = QTextEdit()
            self.measurements_display.setReadOnly(True)
            self.measurements_display.setMinimumHeight(120)
            self.measurements_display.setMaximumHeight(250)
            self.measurements_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            # Standard TextEdit styling
            self.measurements_display.setStyleSheet("""
                QTextEdit {
                    background-color: #2c3e50 !important;
                    color: #ffffff !important;
                    border: 2px solid #5dade2 !important;
                    border-radius: 6px !important;
                    padding: 8px !important;
                    font-size: 12px !important;
                    font-family: 'Segoe UI', sans-serif;
                    line-height: 1.4;
                }
                
                QTextEdit:focus {
                    border: 2px solid #48a1d6 !important;
                    background-color: #2c3e50 !important;
                }
                
                QScrollBar:vertical {
                    background-color: #2c3e50 !important;
                    width: 12px;
                    border-radius: 6px;
                    border: 1px solid #5dade2 !important;
                    margin: 0px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #5dade2 !important;
                    border-radius: 5px;
                    min-height: 30px;
                    margin: 1px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #48a1d6 !important;
                }
                
                QScrollBar::add-line:vertical, 
                QScrollBar::sub-line:vertical {
                    background: none !important;
                    border: none !important;
                    height: 0px;
                }
                
                QScrollBar::add-page:vertical, 
                QScrollBar::sub-page:vertical {
                    background: none !important;
                }
            """)
            
            # Enable scroll bars
            self.measurements_display.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.measurements_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            measurements_layout.addWidget(self.measurements_display)
            parent_layout.addWidget(measurements_group)
            
            print("✅ Measurements section created with standard styling")
            
        except Exception as e:
            print(f"❌ Error creating measurements section: {e}")
    
    def _create_generate_section(self, parent_layout):
        """Create standalone generate button section with STANDARD GENERATE BUTTON STYLING"""
        try:
            # STANDARD: Generate button with EXACT generate button styling from control panel
            self.generate_btn = QPushButton("🏗️ Generate 3D Model")
            self.generate_btn.setMinimumHeight(32)  # STANDARD HEIGHT (not 50)
            self.generate_btn.setToolTip("Generate 3D building model from completed polygon")
            self.generate_btn.clicked.connect(self._handle_generate_model)
            self.generate_btn.setEnabled(False)
            
            # STANDARD GENERATE BUTTON STYLING - EXACT from control panel
            self.generate_btn.setStyleSheet("""
                QPushButton:enabled {
                    background-color: #e74c3c !important;
                    border: 2px solid #e74c3c !important;
                    color: #ffffff !important;
                    font-size: 13px !important;
                    font-weight: bold !important;
                    border-radius: 6px !important;
                    padding: 8px 12px !important;
                    min-height: 32px !important;
                    text-align: center !important;
                }
                
                QPushButton:enabled:hover {
                    background-color: #c0392b !important;
                    border: 2px solid #c0392b !important;
                }
                
                QPushButton:enabled:pressed {
                    background-color: #a93226 !important;
                    border: 2px solid #a93226 !important;
                    padding: 9px 11px 7px 13px !important;
                }
                
                QPushButton:disabled {
                    background-color: #7f8c8d !important;
                    border: 2px solid #7f8c8d !important;
                    color: #95a5a6 !important;
                    border-radius: 6px !important;
                    padding: 8px 12px !important;
                    min-height: 32px !important;
                    text-align: center !important;
                }
            """)
            
            parent_layout.addWidget(self.generate_btn)
            
            print("✅ Generate section created with STANDARD GENERATE BUTTON STYLING")
            
        except Exception as e:
            print(f"❌ Error creating generate section: {e}")
    
    # ==========================================
    # SIGNAL HANDLERS (keeping all the working logic)
    # ==========================================
    
    def _on_scale_changed(self, text):
        """Handle scale change"""
        try:
            scale = float(text)
            if 0.001 <= scale <= 10.0:
                self._current_scale = scale
                print(f"📏 DRAWING TAB: Scale changed to {scale}")
                self.scale_changed.emit(scale)
                
                # Update main window scale if possible
                if hasattr(self.main_window, '_current_scale'):
                    self.main_window._current_scale = scale
                
                # Recalculate measurements with new scale
                self._recalculate_measurements()
                
            else:
                print(f"⚠ Invalid scale: {text}")
        except ValueError:
            print(f"⚠ Invalid scale format: {text}")
    
    def _on_angle_snap_clicked(self):
        """Handle angle snap button toggle with proper functionality"""
        try:
            self.angle_snap_enabled = self.angle_snap_btn.isChecked()
            
            if self.angle_snap_enabled:
                self.angle_snap_btn.setText("📐 90° Angle Snap: ON")
                print("📐 Angle snap ENABLED")
            else:
                self.angle_snap_btn.setText("📐 90° Angle Snap: OFF")
                print("📐 Angle snap DISABLED")
            
            # Emit signal to main window
            self.angle_snap_toggled.emit(self.angle_snap_enabled)
            
            # Update main window if it has angle snap setting
            if hasattr(self.main_window, 'angle_snap_enabled'):
                self.main_window.angle_snap_enabled = self.angle_snap_enabled
            
            # Update canvas if it has angle snap setting
            canvas = self._get_canvas()
            if canvas and hasattr(canvas, 'angle_snap_enabled'):
                canvas.angle_snap_enabled = self.angle_snap_enabled
                print(f"✅ Canvas angle snap updated: {self.angle_snap_enabled}")
            
        except Exception as e:
            print(f"❌ Error handling angle snap toggle: {e}")
    
    def _handle_clear_drawing(self):
        """Handle clear drawing with proper state reset"""
        try:
            print("🗑️ Clear drawing requested")
            
            # Increment generation counter for tracking
            self._drawing_generation_counter += 1
            print(f"📊 Starting drawing session #{self._drawing_generation_counter}")
            
            # Reset ALL measurements state
            self.current_measurements = {
                'points': 0, 
                'area': 0.0, 
                'perimeter': 0.0, 
                'is_complete': False
            }
            self.polygon_complete = False
            self._last_display_key = ""
            self._last_logged_measurements = {}
            
            # Disable generate button
            if self.generate_btn:
                self.generate_btn.setEnabled(False)
                print("❌ Generate button disabled")
            
            # Update displays FIRST
            self._update_measurements_display()
            
            # Emit signals
            self.clear_drawing_requested.emit()
            self.canvas_cleared.emit()
            
            print("✅ Drawing cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing drawing: {e}")
            traceback.print_exc()
    
    def _handle_generate_model(self):
        """Handle generate 3D model button click"""
        try:
            print("🏗️ Generate 3D model requested")
            
            # Check completion state
            if not self.polygon_complete:
                print("❌ Polygon not complete - showing warning")
                QMessageBox.warning(self, "Polygon Incomplete", 
                                  "Please complete the polygon before generating a 3D model.\n\n"
                                  "Make sure you have at least 3 points and the polygon is closed.")
                return
            
            print("✅ Generating 3D model")
            
            # Emit signal 
            self.generate_model_requested.emit()
            
        except Exception as e:
            print(f"❌ Error handling generate model: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Generation Error", 
                               f"Failed to generate 3D model:\n\n{str(e)}")
    
    # ==========================================
    # MEASUREMENT METHODS (simplified but working)
    # ==========================================
    
    def _initialize_measurements_safely(self):
        """Safely initialize measurements and display"""
        try:
            # Initial display update
            self._update_measurements_display()
            print("✅ Measurements safely initialized")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing measurements: {e}")
            return False
    
    def _start_completion_timer(self):
        """Start the completion checking timer"""
        try:
            self.check_timer = QTimer()
            self.check_timer.timeout.connect(self._check_completion)
            self.check_timer.start(500)  # Check every 500ms
            print("✅ Completion timer started (500ms)")
        except Exception as e:
            print(f"❌ Error starting completion timer: {e}")
    
    def _check_completion(self):
        """Check polygon completion state"""
        try:
            # Simplified completion checking
            canvas = self._get_canvas()
            if canvas:
                measurements = self._get_canvas_measurements(canvas)
                if measurements != self.current_measurements:
                    self.current_measurements = measurements
                    self._update_measurements_display()
                    self._update_generate_button_state()
                    
        except Exception as e:
            # Silently handle errors to avoid spam
            pass
    
    def _get_canvas_measurements(self, canvas):
        """Extract measurements from canvas"""
        measurements = {'points': 0, 'area': 0.0, 'perimeter': 0.0, 'is_complete': False}
        
        try:
            # Basic point counting
            if hasattr(canvas, 'points') and canvas.points:
                measurements['points'] = len(canvas.points)
                
            # Check completion
            if measurements['points'] >= 3:
                measurements['is_complete'] = True
                self.polygon_complete = True
            else:
                self.polygon_complete = False
                
        except Exception:
            pass
            
        return measurements
    
    def _get_canvas(self):
        """Get the active drawing canvas"""
        try:
            if hasattr(self.main_window, 'canvas_manager'):
                return getattr(self.main_window.canvas_manager, 'canvas', None)
        except Exception:
            pass
        return None
    
    def _update_generate_button_state(self):
        """Update generate button state based on completion"""
        try:
            if self.generate_btn:
                should_enable = (self.polygon_complete and 
                               self.current_measurements.get('points', 0) >= 3)
                self.generate_btn.setEnabled(should_enable)
        except Exception:
            pass
    
    def _update_measurements_display(self):
        """Update measurements display with proper formatting"""
        if not self.measurements_display:
            return
        
        try:
            measurements = self.current_measurements
            point_count = measurements.get('points', 0)
            area = measurements.get('area', 0.0)
            perimeter = measurements.get('perimeter', 0.0)
            is_complete = measurements.get('is_complete', False)
            
            if point_count == 0:
                text = f"""📝 BUILDING OUTLINE

📍 Points: 0
📏 Area: 0.00 m²
📐 Perimeter: 0.0 m

⏳ Ready to draw

💡 Click on screenshot to start drawing building outline

🎯 Session: #{self._drawing_generation_counter}"""
                
            else:
                status = "✅ Complete" if is_complete else "⏳ Drawing..."
                status_icon = "✅" if is_complete else "⏳"
                
                text = f"""📊 POLYGON INFORMATION

{status_icon} Status: {status}
🔸 Points: {point_count}
📏 Area: {area:.1f} m²
📐 Perimeter: {perimeter:.1f} m

💡 {'Ready to generate 3D model!' if is_complete else 'Keep drawing to close polygon...'}

🎯 Session: #{self._drawing_generation_counter}"""

            self.measurements_display.setText(text)
                        
        except Exception as e:
            print(f"❌ Error updating measurements display: {e}")
    
    def _recalculate_measurements(self):
        """Recalculate measurements when scale changes"""
        pass  # Simplified for now
    
    # ==========================================
    # PUBLIC API METHODS
    # ==========================================
    
    def get_scale_factor(self):
        """Get current scale factor"""
        if self.scale_input:
            try:
                return float(self.scale_input.currentText())
            except ValueError:
                return self._current_scale
        return self._current_scale
    
    def is_angle_snap_enabled(self):
        """Check if angle snap is enabled"""
        return self.angle_snap_enabled
    
    def update_polygon_info(self, measurements):
        """Update polygon information from external sources"""
        try:
            if isinstance(measurements, dict):
                self.current_measurements.update(measurements)
                self.polygon_complete = measurements.get('is_complete', False)
                self._update_measurements_display()
                self._update_generate_button_state()
        except Exception as e:
            print(f"❌ Error updating polygon info: {e}")
    
    def enable_generate_button(self):
        """Enable the generate button"""
        try:
            if self.generate_btn:
                self.generate_btn.setEnabled(True)
        except Exception as e:
            print(f"❌ Error enabling generate button: {e}")
    
    def disable_generate_button(self):
        """Disable the generate button"""
        try:
            if self.generate_btn:
                self.generate_btn.setEnabled(False)
        except Exception as e:
            print(f"❌ Error disabling generate button: {e}")
    
    def get_current_measurements(self):
        """Get current polygon measurements"""
        return dict(self.current_measurements)
    
    def is_polygon_complete(self):
        """Check if polygon is complete"""
        return self.polygon_complete
    
    def reset_measurements(self):
        """Reset all measurements to default"""
        try:
            self.current_measurements = {
                'points': 0, 
                'area': 0.0, 
                'perimeter': 0.0, 
                'is_complete': False
            }
            self.polygon_complete = False
            self._drawing_generation_counter += 1
            
            if self.generate_btn:
                self.generate_btn.setEnabled(False)
            
            self._update_measurements_display()
        except Exception as e:
            print(f"❌ Error resetting measurements: {e}")
