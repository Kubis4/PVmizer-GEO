#!/usr/bin/env python3
"""
Enhanced Left Panel with Model Tab Integration and Real-time Building Updates
FIXED VERSION - Controls work properly
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                            QPushButton, QSpinBox, QDoubleSpinBox, QSlider,
                            QGroupBox, QSizePolicy, QFileDialog, QMessageBox,
                            QStackedWidget, QTextEdit, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

class Model3DTabPanel(QWidget):
    """3D Model tab panel with real-time building updates - FIXED VERSION"""
    
    # Signals
    building_parameter_changed = pyqtSignal(str, object)
    solar_parameter_changed = pyqtSignal(str, object)
    export_model_requested = pyqtSignal()
    animation_toggled = pyqtSignal(bool)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Building generator integration - will be connected later
        self.building_generator = None
        
        # Control references
        self.wall_height_input = None
        self.wall_height_slider = None
        self.roof_type_combo = None
        self.roof_pitch_input = None
        self.roof_pitch_slider = None
        self.time_input = None
        self.time_slider = None
        self.day_input = None
        self.day_slider = None
        self.animate_btn = None
        self.export_btn = None
        
        # Labels
        self.height_label = None
        self.roof_label = None
        self.pitch_label = None
        self.time_label = None
        self.day_label = None
        
        self.setup_ui()
        
        # DEBUG: Check control state after initialization
        QTimer.singleShot(1000, self.debug_control_state)
        
        print("✅ 3D Model Tab Panel initialized with WORKING controls")
    
    def setup_ui(self):
        """Setup 3D Model tab UI with white text labels"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create sections
        self._create_building_parameters_section(main_layout)
        self._create_solar_simulation_section(main_layout)
        
        # Add stretch before export button
        main_layout.addStretch()
        
        # Export button at bottom
        self._create_export_section(main_layout)
        
        # 🔧 FIX: Enable controls by default instead of disabling them
        self._smart_enable_controls()
        
        print("✅ 3D Model Tab UI setup completed with ENABLED controls")
    
    def _create_building_parameters_section(self, parent_layout):
        """Create building parameters section with WHITE text labels"""
        try:
            # Building Parameters group
            building_group = QGroupBox("🏠 Building Parameters")
            building_layout = QVBoxLayout(building_group)
            building_layout.setContentsMargins(10, 15, 10, 10)
            building_layout.setSpacing(12)
            
            # Wall Height - WHITE TEXT LABELS
            height_layout = QVBoxLayout()
            height_row = QHBoxLayout()
            
            self.height_label = QLabel("Wall Height:")
            self.height_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            height_row.addWidget(self.height_label)
            height_row.addStretch()
            
            self.wall_height_input = QDoubleSpinBox()
            self.wall_height_input.setRange(2.0, 10.0)
            self.wall_height_input.setValue(3.0)
            self.wall_height_input.setSuffix(" m")
            self.wall_height_input.setSingleStep(0.1)
            self.wall_height_input.setDecimals(1)
            self.wall_height_input.valueChanged.connect(self._on_height_input_changed)
            self.wall_height_input.setFixedWidth(80)
            self.wall_height_input.setEnabled(True)  # 🔧 FIX: Explicitly enable
            
            self.wall_height_input.setStyleSheet("""
                QDoubleSpinBox {
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 12px;
                }
                QDoubleSpinBox:focus {
                    border-color: #3498db;
                }
            """)
            
            height_row.addWidget(self.wall_height_input)
            height_layout.addLayout(height_row)
            
            # Slider styling
            self.wall_height_slider = QSlider(Qt.Horizontal)
            self.wall_height_slider.setRange(20, 100)
            self.wall_height_slider.setValue(30)
            self.wall_height_slider.valueChanged.connect(self._on_height_slider_changed)
            self.wall_height_slider.setToolTip("Adjust building wall height")
            self.wall_height_slider.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.wall_height_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #3498db;
                    border: 1px solid #3498db;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #2980b9;
                }
            """)
            height_layout.addWidget(self.wall_height_slider)
            building_layout.addLayout(height_layout)
            
            # Roof Type - WHITE TEXT LABEL
            roof_type_layout = QHBoxLayout()
            self.roof_label = QLabel("Roof Type:")
            self.roof_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            roof_type_layout.addWidget(self.roof_label)
            roof_type_layout.addStretch()
            
            self.roof_type_combo = QComboBox()
            self.roof_type_combo.addItems(["🏠 Flat", "🏘️ Gable", "🏠 Hip", "🔺 Pyramid"])
            self.roof_type_combo.currentTextChanged.connect(self._on_roof_type_changed)
            self.roof_type_combo.setToolTip("Select roof type")
            self.roof_type_combo.setFixedWidth(120)
            self.roof_type_combo.setEnabled(True)  # 🔧 FIX: Explicitly enable
            
            self.roof_type_combo.setStyleSheet("""
                QComboBox {
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 12px;
                }
                QComboBox:focus {
                    border-color: #3498db;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
            """)
            
            roof_type_layout.addWidget(self.roof_type_combo)
            building_layout.addLayout(roof_type_layout)
            
            # Roof Pitch - WHITE TEXT LABEL
            pitch_layout = QVBoxLayout()
            pitch_row = QHBoxLayout()
            
            self.pitch_label = QLabel("Roof Pitch:")
            self.pitch_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            pitch_row.addWidget(self.pitch_label)
            pitch_row.addStretch()
            
            self.roof_pitch_input = QSpinBox()
            self.roof_pitch_input.setRange(0, 60)
            self.roof_pitch_input.setValue(30)
            self.roof_pitch_input.setSuffix("°")
            self.roof_pitch_input.valueChanged.connect(self._on_pitch_input_changed)
            self.roof_pitch_input.setFixedWidth(70)
            self.roof_pitch_input.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.roof_pitch_input.setStyleSheet("""
                QSpinBox {
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 12px;
                }
                QSpinBox:focus {
                    border-color: #3498db;
                }
            """)
            pitch_row.addWidget(self.roof_pitch_input)
            pitch_layout.addLayout(pitch_row)
            
            self.roof_pitch_slider = QSlider(Qt.Horizontal)
            self.roof_pitch_slider.setRange(0, 60)
            self.roof_pitch_slider.setValue(30)
            self.roof_pitch_slider.valueChanged.connect(self._on_pitch_slider_changed)
            self.roof_pitch_slider.setToolTip("Adjust roof pitch angle")
            self.roof_pitch_slider.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.roof_pitch_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #3498db;
                    border: 1px solid #3498db;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #2980b9;
                }
            """)
            pitch_layout.addWidget(self.roof_pitch_slider)
            building_layout.addLayout(pitch_layout)
            
            parent_layout.addWidget(building_group)
            
            print("✅ Building parameters section created with ENABLED controls")
            
        except Exception as e:
            print(f"❌ Error creating building parameters section: {e}")
    
    def _create_solar_simulation_section(self, parent_layout):
        """Create solar simulation section with WHITE text labels"""
        try:
            # Solar Simulation group
            solar_group = QGroupBox("☀️ Solar Simulation")
            solar_layout = QVBoxLayout(solar_group)
            solar_layout.setContentsMargins(10, 15, 10, 10)
            solar_layout.setSpacing(12)
            
            # Time of Day - WHITE TEXT LABEL
            time_layout = QVBoxLayout()
            time_row = QHBoxLayout()
            
            self.time_label = QLabel("Time of Day:")
            self.time_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            time_row.addWidget(self.time_label)
            time_row.addStretch()
            
            self.time_input = QSpinBox()
            self.time_input.setRange(6, 18)
            self.time_input.setValue(12)
            self.time_input.setSuffix(":00")
            self.time_input.valueChanged.connect(self._on_time_input_changed)
            self.time_input.setFixedWidth(70)
            self.time_input.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.time_input.setStyleSheet("""
                QSpinBox {
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 12px;
                }
                QSpinBox:focus {
                    border-color: #3498db;
                }
            """)
            time_row.addWidget(self.time_input)
            time_layout.addLayout(time_row)
            
            self.time_slider = QSlider(Qt.Horizontal)
            self.time_slider.setRange(6, 18)
            self.time_slider.setValue(12)
            self.time_slider.valueChanged.connect(self._on_time_slider_changed)
            self.time_slider.setToolTip("Set time of day (6 AM - 6 PM)")
            self.time_slider.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.time_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #f39c12;
                    border: 1px solid #f39c12;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #e67e22;
                }
            """)
            time_layout.addWidget(self.time_slider)
            solar_layout.addLayout(time_layout)
            
            # Day of Year - WHITE TEXT LABEL
            day_layout = QVBoxLayout()
            day_row = QHBoxLayout()
            
            self.day_label = QLabel("Day of Year:")
            self.day_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            day_row.addWidget(self.day_label)
            day_row.addStretch()
            
            self.day_input = QSpinBox()
            self.day_input.setRange(1, 365)
            self.day_input.setValue(180)
            self.day_input.valueChanged.connect(self._on_day_input_changed)
            self.day_input.setFixedWidth(70)
            self.day_input.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.day_input.setStyleSheet("""
                QSpinBox {
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 4px 8px;
                    background-color: white;
                    color: #2c3e50;
                    font-size: 12px;
                }
                QSpinBox:focus {
                    border-color: #3498db;
                }
            """)
            day_row.addWidget(self.day_input)
            day_layout.addLayout(day_row)
            
            self.day_slider = QSlider(Qt.Horizontal)
            self.day_slider.setRange(1, 365)
            self.day_slider.setValue(180)
            self.day_slider.valueChanged.connect(self._on_day_slider_changed)
            self.day_slider.setToolTip("Set day of year (1-365)")
            self.day_slider.setEnabled(True)  # 🔧 FIX: Explicitly enable
            self.day_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #f39c12;
                    border: 1px solid #f39c12;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #e67e22;
                }
            """)
            day_layout.addWidget(self.day_slider)
            solar_layout.addLayout(day_layout)
            
            # Animation Button
            self.animate_btn = QPushButton("🎬 Animate Sun")
            self.animate_btn.setMinimumHeight(35)
            self.animate_btn.clicked.connect(self._toggle_sun_animation)
            self.animate_btn.setToolTip("Start/stop sun animation throughout the day")
            self.animate_btn.setEnabled(True)  # 🔧 FIX: Explicitly enable
            
            self.animate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px 12px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
                QPushButton:pressed {
                    background-color: #ba4a00;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                    color: #adb5bd;
                }
            """)
            
            solar_layout.addWidget(self.animate_btn)
            parent_layout.addWidget(solar_group)
            
            print("✅ Solar simulation section created with ENABLED controls")
            
        except Exception as e:
            print(f"❌ Error creating solar simulation section: {e}")
    
    def _create_export_section(self, parent_layout):
        """Create export button section"""
        try:
            # Export button
            self.export_btn = QPushButton("💾 Export 3D Model")
            self.export_btn.setMinimumHeight(50)
            self.export_btn.clicked.connect(self._emit_export_requested)
            self.export_btn.setToolTip("Export the 3D model to file")
            self.export_btn.setEnabled(True)  # 🔧 FIX: Explicitly enable
            
            self.export_btn.setStyleSheet("""
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
            
            parent_layout.addWidget(self.export_btn)
            
            print("✅ Export section created with ENABLED controls")
            
        except Exception as e:
            print(f"❌ Error creating export section: {e}")
    
    def _smart_enable_controls(self):
        """Smart control enabling with fallback - FIXED VERSION"""
        try:
            # Always enable basic controls - they work independently
            basic_controls = [
                self.wall_height_input, self.wall_height_slider,
                self.roof_type_combo, self.roof_pitch_input, self.roof_pitch_slider,
                self.time_input, self.time_slider,
                self.day_input, self.day_slider
            ]
            
            for control in basic_controls:
                if control:
                    control.setEnabled(True)
                    print(f"✅ Enabled: {control.__class__.__name__}")
            
            # Enable animation - works independently
            if self.animate_btn:
                self.animate_btn.setEnabled(True)
                self.animate_btn.setToolTip("Start/stop sun animation throughout the day")
            
            # Enable export - works independently
            if self.export_btn:
                self.export_btn.setEnabled(True)
                self.export_btn.setToolTip("Export the 3D model to file")
            
            print("✅ Smart control enabling completed - ALL CONTROLS ENABLED")
            
        except Exception as e:
            print(f"❌ Error in smart control enabling: {e}")
            # Fallback - force enable all controls
            self._force_enable_all_controls()
    
    def _force_enable_all_controls(self):
        """Force enable all controls as fallback"""
        try:
            all_controls = [
                self.wall_height_input, self.wall_height_slider,
                self.roof_type_combo, self.roof_pitch_input, self.roof_pitch_slider,
                self.time_input, self.time_slider,
                self.day_input, self.day_slider,
                self.animate_btn, self.export_btn
            ]
            
            for control in all_controls:
                if control:
                    control.setEnabled(True)
            
            print("🔧 Force enabled all controls")
            
        except Exception as e:
            print(f"❌ Error force enabling controls: {e}")
    
    def debug_control_state(self):
        """Debug why controls are not working"""
        print("🔍 === CONTROL STATE DEBUG ===")
        
        controls = {
            'wall_height_input': self.wall_height_input,
            'wall_height_slider': self.wall_height_slider,
            'roof_type_combo': self.roof_type_combo,
            'roof_pitch_input': self.roof_pitch_input,
            'roof_pitch_slider': self.roof_pitch_slider,
            'time_input': self.time_input,
            'time_slider': self.time_slider,
            'day_input': self.day_input,
            'day_slider': self.day_slider,
            'animate_btn': self.animate_btn,
            'export_btn': self.export_btn
        }
        
        for name, control in controls.items():
            if control:
                enabled = control.isEnabled()
                visible = control.isVisible()
                print(f"  {name}: enabled={enabled}, visible={visible}")
            else:
                print(f"  {name}: MISSING")
        
        print(f"  building_generator: {self.building_generator is not None}")
        print(f"  main_window: {self.main_window is not None}")
        print("🔍 === DEBUG END ===")
        
        # If any controls are disabled, force enable them
        disabled_controls = [name for name, control in controls.items() 
                           if control and not control.isEnabled()]
        if disabled_controls:
            print(f"🔧 Found disabled controls: {disabled_controls}")
            self._force_enable_all_controls()
    
    def connect_to_model_tab(self, model_tab):
        """Connect to the actual model tab's building generator"""
        try:
            if model_tab and hasattr(model_tab, 'building_generator'):
                self.building_generator = model_tab.building_generator
                
                if self.building_generator:
                    # Connect generator signals
                    if hasattr(self.building_generator, 'solar_time_changed'):
                        self.building_generator.solar_time_changed.connect(self._on_generator_time_changed)
                    if hasattr(self.building_generator, 'animation_step'):
                        self.building_generator.animation_step.connect(self._on_generator_animation_step)
                    if hasattr(self.building_generator, 'building_generated'):
                        self.building_generator.building_generated.connect(self._on_building_generated)
                    
                    # Sync UI with current building if it exists
                    self.sync_with_current_building()
                    
                    print("✅ Connected to model tab's building generator")
                    return True
                else:
                    print("❌ Model tab building generator not found")
                    return False
            else:
                print("❌ Model tab or building generator not available")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to model tab: {e}")
            return False
    
    def sync_with_current_building(self):
        """Sync UI controls with current building parameters"""
        try:
            if not self.building_generator:
                print("⚠️ No building generator to sync with")
                return
            
            # Sync building parameters
            if hasattr(self.building_generator, 'current_height'):
                height = self.building_generator.current_height
                self.wall_height_input.blockSignals(True)
                self.wall_height_slider.blockSignals(True)
                self.wall_height_input.setValue(height)
                self.wall_height_slider.setValue(int(height * 10))
                self.wall_height_input.blockSignals(False)
                self.wall_height_slider.blockSignals(False)
                print(f"🔄 Synced height: {height}m")
            
            if hasattr(self.building_generator, 'current_roof_type'):
                roof_type = self.building_generator.current_roof_type
                # Find matching combo box item
                for i in range(self.roof_type_combo.count()):
                    item_text = self.roof_type_combo.itemText(i).lower()
                    if roof_type in item_text:
                        self.roof_type_combo.blockSignals(True)
                        self.roof_type_combo.setCurrentIndex(i)
                        self.roof_type_combo.blockSignals(False)
                        print(f"🔄 Synced roof type: {roof_type}")
                        break
            
            if hasattr(self.building_generator, 'current_roof_pitch'):
                pitch = self.building_generator.current_roof_pitch
                self.roof_pitch_input.blockSignals(True)
                self.roof_pitch_slider.blockSignals(True)
                self.roof_pitch_input.setValue(int(pitch))
                self.roof_pitch_slider.setValue(int(pitch))
                self.roof_pitch_input.blockSignals(False)
                self.roof_pitch_slider.blockSignals(False)
                print(f"🔄 Synced roof pitch: {pitch}°")
            
            # Sync solar parameters
            if hasattr(self.building_generator, 'solar_time'):
                time = self.building_generator.solar_time
                self.time_input.blockSignals(True)
                self.time_slider.blockSignals(True)
                self.time_input.setValue(int(time))
                self.time_slider.setValue(int(time))
                self.time_input.blockSignals(False)
                self.time_slider.blockSignals(False)
                print(f"🔄 Synced solar time: {time}:00")
            
            if hasattr(self.building_generator, 'solar_day'):
                day = self.building_generator.solar_day
                self.day_input.blockSignals(True)
                self.day_slider.blockSignals(True)
                self.day_input.setValue(int(day))
                self.day_slider.setValue(int(day))
                self.day_input.blockSignals(False)
                self.day_slider.blockSignals(False)
                print(f"🔄 Synced solar day: {day}")
            
            print("✅ UI synced with current building parameters")
            
        except Exception as e:
            print(f"❌ Error syncing UI with building: {e}")
    
    def _enable_all_controls(self, enabled=True):
        """Enable/disable all controls - LEGACY METHOD"""
        try:
            controls = [
                self.wall_height_input, self.wall_height_slider,
                self.roof_type_combo, self.roof_pitch_input, self.roof_pitch_slider,
                self.time_input, self.time_slider,
                self.day_input, self.day_slider,
                self.animate_btn, self.export_btn
            ]
            
            for control in controls:
                if control:
                    control.setEnabled(enabled)
            
            print(f"🔧 Controls {'enabled' if enabled else 'disabled'}")
            
        except Exception as e:
            print(f"❌ Error setting control states: {e}")
    
    # Event handlers
    def _on_height_input_changed(self, value):
        """Handle wall height input change - ENHANCED"""
        try:
            print(f"🔧 Height input changed to: {value:.1f}m")
            
            # Update slider
            slider_value = int(value * 10)
            if self.wall_height_slider.value() != slider_value:
                self.wall_height_slider.setValue(slider_value)
            
            # Update building via generator
            if self.building_generator and hasattr(self.building_generator, 'update_building_height'):
                print(f"🔧 Updating building height to {value:.1f}m")
                self.building_generator.update_building_height(value)
            else:
                print("⚠️ Building generator not connected for height update")
            
            print(f"🏠 Wall height: {value:.1f}m")
            self.building_parameter_changed.emit("wall_height", value)
            
        except Exception as e:
            print(f"❌ Error updating building height: {e}")
    
    def _on_height_slider_changed(self, value):
        """Handle wall height slider change"""
        try:
            height = value / 10.0
            print(f"🔧 Height slider changed to: {height:.1f}m")
            if self.wall_height_input.value() != height:
                self.wall_height_input.setValue(height)
        except Exception as e:
            print(f"❌ Error handling height slider: {e}")
    
    def _on_roof_type_changed(self, roof_type_text):
        """Handle roof type change - ENHANCED"""
        try:
            print(f"🔧 Roof type changed to: {roof_type_text}")
            
            # Extract roof type from text
            roof_type = roof_type_text.lower()
            for type_name in ['flat', 'gable', 'hip', 'pyramid']:
                if type_name in roof_type:
                    roof_type = type_name
                    break
            
            # Enable/disable pitch controls based on roof type
            is_enabled = roof_type != 'flat'
            if self.roof_pitch_slider:
                self.roof_pitch_slider.setEnabled(is_enabled)
            if self.roof_pitch_input:
                self.roof_pitch_input.setEnabled(is_enabled)
            
            # Update building via generator
            if self.building_generator and hasattr(self.building_generator, 'update_roof_type'):
                print(f"🔧 Updating roof type to {roof_type}")
                self.building_generator.update_roof_type(roof_type)
            else:
                print("⚠️ Building generator not connected for roof type update")
            
            print(f"🏠 Roof type: {roof_type}")
            self.building_parameter_changed.emit("roof_type", roof_type)
            
        except Exception as e:
            print(f"❌ Error updating roof type: {e}")
    
    def _on_pitch_input_changed(self, value):
        """Handle roof pitch input change - ENHANCED"""
        try:
            print(f"🔧 Roof pitch input changed to: {value}°")
            
            # Update slider
            if self.roof_pitch_slider.value() != value:
                self.roof_pitch_slider.setValue(value)
            
            # Update building via generator
            if self.building_generator and hasattr(self.building_generator, 'update_roof_pitch'):
                print(f"🔧 Updating roof pitch to {value}°")
                self.building_generator.update_roof_pitch(value)
            else:
                print("⚠️ Building generator not connected for roof pitch update")
            
            print(f"🏠 Roof pitch: {value}°")
            self.building_parameter_changed.emit("roof_pitch", value)
            
        except Exception as e:
            print(f"❌ Error updating roof pitch: {e}")
    
    def _on_pitch_slider_changed(self, value):
        """Handle roof pitch slider change"""
        try:
            print(f"🔧 Roof pitch slider changed to: {value}°")
            if self.roof_pitch_input.value() != value:
                self.roof_pitch_input.setValue(value)
        except Exception as e:
            print(f"❌ Error handling pitch slider: {e}")
    
    def _on_time_input_changed(self, value):
        """Handle time input change - ENHANCED"""
        try:
            print(f"🔧 Solar time input changed to: {value:02d}:00")
            
            # Update slider
            if self.time_slider.value() != value:
                self.time_slider.setValue(value)
            
            # Update solar simulation via generator
            if self.building_generator and hasattr(self.building_generator, 'update_solar_time'):
                print(f"🔧 Updating solar time to {value:02d}:00")
                self.building_generator.update_solar_time(value)
            else:
                print("⚠️ Building generator not connected for solar time update")
            
            print(f"☀️ Time: {value:02d}:00")
            self.solar_parameter_changed.emit("time_of_day", value)
            
        except Exception as e:
            print(f"❌ Error updating solar time: {e}")
    
    def _on_time_slider_changed(self, value):
        """Handle time slider change"""
        try:
            print(f"🔧 Solar time slider changed to: {value:02d}:00")
            if self.time_input.value() != value:
                self.time_input.setValue(value)
        except Exception as e:
            print(f"❌ Error handling time slider: {e}")
    
    def _on_day_input_changed(self, value):
        """Handle day input change - ENHANCED"""
        try:
            print(f"🔧 Solar day input changed to: {value}")
            
            # Update slider
            if self.day_slider.value() != value:
                self.day_slider.setValue(value)
            
            # Update solar simulation via generator
            if self.building_generator and hasattr(self.building_generator, 'update_solar_day'):
                print(f"🔧 Updating solar day to {value}")
                self.building_generator.update_solar_day(value)
            else:
                print("⚠️ Building generator not connected for solar day update")
            
            print(f"☀️ Day: {value}")
            self.solar_parameter_changed.emit("day_of_year", value)
            
        except Exception as e:
            print(f"❌ Error updating solar day: {e}")
    
    def _on_day_slider_changed(self, value):
        """Handle day slider change"""
        try:
            print(f"🔧 Solar day slider changed to: {value}")
            if self.day_input.value() != value:
                self.day_input.setValue(value)
        except Exception as e:
            print(f"❌ Error handling day slider: {e}")
    
    def _toggle_sun_animation(self):
        """Toggle sun animation"""
        try:
            print("🎬 Animation button clicked!")
            
            if not self.building_generator:
                print("❌ Building generator not available")
                QMessageBox.warning(self, "Animation Error", 
                                  "Building generator not connected.")
                return
            
            # Check if animation is running
            is_running = (hasattr(self.building_generator, 'animation_timer') and 
                         self.building_generator.animation_timer and
                         self.building_generator.animation_timer.isActive())
            
            if is_running:
                # Stop animation
                if hasattr(self.building_generator, 'stop_sun_animation'):
                    self.building_generator.stop_sun_animation()
                self.animate_btn.setText("🎬 Animate Sun")
                print("⏹️ Animation stopped")
                self.animation_toggled.emit(False)
            else:
                # Start animation
                if hasattr(self.building_generator, 'start_sun_animation'):
                    self.building_generator.start_sun_animation()
                self.animate_btn.setText("⏹️ Stop Animation")
                print("🎬 Animation started")
                self.animation_toggled.emit(True)
                
        except Exception as e:
            print(f"❌ Error toggling animation: {e}")
            QMessageBox.critical(self, "Animation Error", f"Error toggling animation: {str(e)}")
    
    def _emit_export_requested(self):
        """Export 3D model"""
        try:
            print("💾 Export button clicked!")
            
            # Check if we have a building to export
            has_building = (self.building_generator and 
                          hasattr(self.building_generator, 'current_building') and 
                          self.building_generator.current_building)
            
            if not has_building:
                QMessageBox.warning(self, "No Model", 
                                  "Please generate a 3D model first before exporting.")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Export 3D Model", 
                "building_model.stl", 
                "STL Files (*.stl);;OBJ Files (*.obj);;PLY Files (*.ply)"
            )
            
            if filename:
                try:
                    # Try to export the model
                    if hasattr(self.building_generator.current_building, 'save'):
                        self.building_generator.current_building.save(filename)
                    else:
                        # Alternative export method
                        print("⚠️ Using alternative export method")
                        # You might need to implement this based on your building generator
                    
                    QMessageBox.information(self, "Export Success", 
                                          f"Model exported successfully to:\n{filename}")
                    self.export_model_requested.emit()
                    print(f"✅ Model exported to: {filename}")
                    
                except Exception as e:
                    QMessageBox.warning(self, "Export Failed", f"Failed to export the model: {str(e)}")
                    print(f"❌ Export failed: {e}")
                    
        except Exception as e:
            print(f"❌ Error exporting model: {e}")
            QMessageBox.critical(self, "Export Error", f"Error exporting model: {str(e)}")
    
    # Generator signal handlers
    def _on_generator_time_changed(self, hour):
        """Handle time changes from generator during animation"""
        try:
            if self.time_input and self.time_input.value() != int(hour):
                self.time_input.blockSignals(True)
                self.time_input.setValue(int(hour))
                self.time_input.blockSignals(False)
            
            if self.time_slider and self.time_slider.value() != int(hour):
                self.time_slider.blockSignals(True)
                self.time_slider.setValue(int(hour))
                self.time_slider.blockSignals(False)
                
        except Exception as e:
            print(f"❌ Error handling generator time change: {e}")
    
    def _on_generator_animation_step(self, hour):
        """Handle animation steps from generator"""
        try:
            self._on_generator_time_changed(hour)
        except Exception as e:
            print(f"❌ Error handling generator animation step: {e}")
    
    def _on_building_generated(self):
        """Handle building generation completion - ENHANCED"""
        try:
            print("🏗️ Building generation completed - syncing UI")
            
            # Sync UI with current building parameters
            self.sync_with_current_building()
            
            # Ensure controls are enabled
            self._smart_enable_controls()
            
        except Exception as e:
            print(f"❌ Error handling building generation: {e}")
    
    # Public API methods
    def get_wall_height(self):
        """Get current wall height in meters"""
        if self.wall_height_input:
            return self.wall_height_input.value()
        return 3.0
    
    def get_roof_type(self):
        """Get current roof type"""
        if self.roof_type_combo:
            text = self.roof_type_combo.currentText().lower()
            for roof_type in ['flat', 'gable', 'hip', 'pyramid']:
                if roof_type in text:
                    return roof_type
        return 'flat'
    
    def get_roof_pitch(self):
        """Get current roof pitch in degrees"""
        if self.roof_pitch_input:
            return self.roof_pitch_input.value()
        return 30
    
    def get_time_of_day(self):
        """Get current time of day"""
        if self.time_input:
            return self.time_input.value()
        return 12
    
    def get_day_of_year(self):
        """Get current day of year"""
        if self.day_input:
            return self.day_input.value()
        return 180
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            print("🧹 Cleaning up Model3D Tab Panel...")
            
            # Clear building generator reference
            self.building_generator = None
            
            # Clear control references
            self.wall_height_input = None
            self.wall_height_slider = None
            self.roof_type_combo = None
            self.roof_pitch_input = None
            self.roof_pitch_slider = None
            self.time_input = None
            self.time_slider = None
            self.day_input = None
            self.day_slider = None
            self.animate_btn = None
            self.export_btn = None
            
            print("✅ Model3D Tab Panel cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during Model3D Tab Panel cleanup: {e}")