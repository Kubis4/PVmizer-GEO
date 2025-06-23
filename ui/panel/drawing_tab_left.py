#!/usr/bin/env python3
"""
Drawing Tab Panel - FIXED VERSION with proper styling from reference
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
    Drawing Tab Panel - WITH CORRECTED STYLING from reference code
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
        
        print("🎨 Initializing Drawing Tab Panel (CORRECTED STYLING)...")
        
        # Initialize core attributes
        self._initialize_attributes()
        
        # Setup UI
        self._setup_ui()
        
        # Initialize measurements safely
        QTimer.singleShot(100, self._initialize_measurements_safely)
        
        # Start completion checking timer
        self._start_completion_timer()
        
        print("✅ Drawing Tab Panel initialized successfully (CORRECTED)")
    
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
        """Setup the complete UI layout without tips section"""
        try:
            print("🔧 Setting up Drawing Tab UI (CORRECTED STYLING)...")
            
            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(15)
            
            # Create main sections (NO TIPS SECTION)
            self._create_scale_section(main_layout)
            self._create_drawing_tools_section(main_layout)  # FIXED STYLING
            self._create_measurements_section(main_layout)   # FIXED STYLING
            
            # Add stretch before generate button
            main_layout.addStretch()
            
            # Generate button at bottom (standalone)
            self._create_generate_section(main_layout)  # FIXED STYLING
            
            print("✅ Drawing Tab UI setup completed with corrected styling")
            
        except Exception as e:
            print(f"❌ Error setting up Drawing Tab UI: {e}")
            traceback.print_exc()
    
    def _create_scale_section(self, parent_layout):
        """Create the scale settings section"""
        try:
            # Scale group
            scale_group = QGroupBox("📏 Scale Settings")
            scale_layout = QVBoxLayout(scale_group)
            scale_layout.setContentsMargins(10, 15, 10, 10)
            
            # Scale input row
            scale_row = QHBoxLayout()
            scale_row.addWidget(QLabel("Scale (m/pixel):"))
            
            self.scale_input = QComboBox()
            self.scale_input.addItems(["0.005", "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1.0"])
            self.scale_input.setCurrentText("0.05")
            self.scale_input.setEditable(True)
            self.scale_input.currentTextChanged.connect(self._on_scale_changed)
            self.scale_input.setToolTip("Set the scale factor for measurements")
            
            scale_row.addWidget(self.scale_input)
            scale_layout.addLayout(scale_row)
            
            parent_layout.addWidget(scale_group)
            
            print("✅ Scale section created")
            
        except Exception as e:
            print(f"❌ Error creating scale section: {e}")
    
    def _create_drawing_tools_section(self, parent_layout):
        """Create the drawing tools section with CORRECTED angle snap button styling"""
        try:
            # Drawing tools group
            tools_group = QGroupBox("✏️ Drawing Tools")
            tools_layout = QVBoxLayout(tools_group)
            tools_layout.setContentsMargins(10, 15, 10, 10)
            tools_layout.setSpacing(10)
            
            # CORRECTED: Angle snap button with EXACT styling from reference
            self.angle_snap_btn = QPushButton("📐 90° Angle Snap: ON")
            self.angle_snap_btn.setMinimumHeight(35)
            self.angle_snap_btn.setCheckable(True)
            self.angle_snap_btn.setChecked(True)
            self.angle_snap_btn.clicked.connect(self._on_angle_snap_clicked)
            self.angle_snap_btn.setToolTip("Toggle 90-degree angle snapping for precise drawing")
            
            # CORRECTED: EXACT style from reference code
            self.angle_snap_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px 12px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
                QPushButton:!checked {
                    background-color: #6c757d;
                }
                QPushButton:!checked:hover {
                    background-color: #5a6268;
                }
            """)
            
            tools_layout.addWidget(self.angle_snap_btn)
            
            # CORRECTED: Clear button with EXACT styling from reference
            self.clear_btn = QPushButton("🗑️ Clear Drawing")
            self.clear_btn.setMinimumHeight(35)
            self.clear_btn.setToolTip("Clear the current drawing and reset measurements")
            self.clear_btn.clicked.connect(self._handle_clear_drawing)
            
            # CORRECTED: EXACT style from reference code
            self.clear_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            
            tools_layout.addWidget(self.clear_btn)
            parent_layout.addWidget(tools_group)
            
            print("✅ Drawing tools section created with CORRECTED styling")
            
        except Exception as e:
            print(f"❌ Error creating drawing tools section: {e}")
    
    def _create_measurements_section(self, parent_layout):
        """Create the measurements display section with CORRECTED styling"""
        try:
            # Measurements group
            measurements_group = QGroupBox("📊 Polygon Information")
            measurements_layout = QVBoxLayout(measurements_group)
            measurements_layout.setContentsMargins(10, 15, 10, 10)
            
            # CORRECTED: Measurements display with EXACT styling from reference
            self.measurements_display = QTextEdit()
            self.measurements_display.setReadOnly(True)
            self.measurements_display.setMinimumHeight(120)
            self.measurements_display.setMaximumHeight(250)
            self.measurements_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            # CORRECTED: EXACT styling from reference code
            self.measurements_display.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 12px;
                    color: #2c3e50;
                    line-height: 1.4;
                }
                QScrollBar:vertical {
                    background: #f1f3f4;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #c1c1c1;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #a8a8a8;
                }
            """)
            
            # Enable scroll bars
            self.measurements_display.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.measurements_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            measurements_layout.addWidget(self.measurements_display)
            parent_layout.addWidget(measurements_group)
            
            print("✅ Measurements section created with CORRECTED styling")
            
        except Exception as e:
            print(f"❌ Error creating measurements section: {e}")
    
    def _create_generate_section(self, parent_layout):
        """Create standalone generate button section with CORRECTED styling"""
        try:
            # CORRECTED: Generate button with EXACT styling from reference
            self.generate_btn = QPushButton("🏗️ Generate 3D Model")
            self.generate_btn.setMinimumHeight(50)
            self.generate_btn.setToolTip("Generate 3D building model from completed polygon")
            self.generate_btn.clicked.connect(self._handle_generate_model)
            self.generate_btn.setEnabled(False)
            
            # CORRECTED: EXACT style from reference code
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 12px;
                    text-align: center;
                }
                QPushButton:hover:enabled {
                    background-color: #218838;
                }
                QPushButton:pressed:enabled {
                    background-color: #1e7e34;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                    color: #adb5bd;
                }
            """)
            
            parent_layout.addWidget(self.generate_btn)
            
            print("✅ Generate section created with CORRECTED styling")
            
        except Exception as e:
            print(f"❌ Error creating generate section: {e}")
    
    # ==========================================
    # SIGNAL HANDLERS (keeping all the working logic from reference)
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
        """CORRECTED: Handle angle snap button toggle with proper functionality"""
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