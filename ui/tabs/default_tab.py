#!/usr/bin/env python3
"""
Default Tab - Interactive roof selection with animated dimension fields
Direct integration with ModelTab using create_building method
COMPLETE FIXED VERSION
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QGridLayout, QDoubleSpinBox, QScrollArea, QSizePolicy)
from PyQt5.QtCore import (pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, 
                          QParallelAnimationGroup, QRect, QSize, QTimer)
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen


class RoofTypeCard(QFrame):
    """Interactive roof type card with image and animation"""
    
    clicked = pyqtSignal(str)  # roof_type
    
    def __init__(self, roof_type, roof_name, icon_text, parent=None):
        super().__init__(parent)
        self.roof_type = roof_type
        self.roof_name = roof_name
        self.icon_text = icon_text
        self.is_selected = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup card UI"""
        self.setFixedSize(200, 200)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply styling
        self.setStyleSheet("""
            RoofTypeCard {
                background-color: #34495e;
                border: 3px solid #5dade2;
                border-radius: 12px;
            }
            RoofTypeCard:hover {
                background-color: #3d5a6e;
                border: 3px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon/Image placeholder
        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                font-size: 70px;
                background-color: transparent;
                color: #5dade2;
            }
        """)
        layout.addWidget(self.icon_label)
        
        # Roof name
        name_label = QLabel(self.roof_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background-color: transparent;
            }
        """)
        layout.addWidget(name_label)
        
        # Description
        descriptions = {
            'flat': 'Simple & Modern',
            'gable': 'Classic Design',
            'pyramid': 'Four-sided',
            'hip': 'All Slopes'
        }
        desc_label = QLabel(descriptions.get(self.roof_type, ''))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #b8c5ce;
                background-color: transparent;
            }
        """)
        layout.addWidget(desc_label)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.roof_type)
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                RoofTypeCard {
                    background-color: #3498db;
                    border: 3px solid #2980b9;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                RoofTypeCard {
                    background-color: #34495e;
                    border: 3px solid #5dade2;
                    border-radius: 12px;
                }
                RoofTypeCard:hover {
                    background-color: #3d5a6e;
                    border: 3px solid #3498db;
                }
            """)


class DimensionInputPanel(QFrame):
    """Animated dimension input panel"""
    
    generate_clicked = pyqtSignal(str, dict)  # roof_type, dimensions
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_roof_type = None
        self.setup_ui()
        
        # Initially hidden
        self.setMaximumHeight(0)
        self.setVisible(False)
        
    def setup_ui(self):
        """Setup dimension input UI"""
        self.setFixedWidth(860)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 2px solid #5dade2;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title Box
        title_frame = QFrame()
        title_frame.setFixedSize(780, 80)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid #5dade2;
                border-radius: 10px;
            }
        """)
        
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("📐 Roof Dimensions")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #5dade2;
                background-color: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title)
        layout.addWidget(title_frame, alignment=Qt.AlignCenter)
        
        # Input grid - HORIZONTAL LAYOUT
        input_layout = QHBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(20, 10, 20, 10)
        
        # Create three input fields
        self.length_input = self._create_dimension_input("Length (m):", 10.0, 100.0)
        self.width_input = self._create_dimension_input("Width (m):", 8.0, 100.0)
        self.height_input = self._create_dimension_input("Height (m):", 3.0, 50.0)
        
        input_layout.addLayout(self.length_input)
        input_layout.addLayout(self.width_input)
        input_layout.addLayout(self.height_input)
        
        layout.addLayout(input_layout)
        
        # Add spacing before button
        layout.addSpacing(30)
        
        # Generate button
        self.generate_btn = QPushButton("🏗️ Generate Roof Model")
        self.generate_btn.setFixedHeight(50)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #5dade2;
                color: #ffffff;
                border: 2px solid #5dade2;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3498db;
                border: 2px solid #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
                border: 2px solid #2980b9;
            }
        """)
        self.generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(self.generate_btn)
    
    def _create_dimension_input(self, label_text, default_value, max_value):
        """Create a dimension input field with label and arrows"""
        container = QVBoxLayout()
        container.setSpacing(15)
        
        # Label
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            color: #ffffff;
            background-color: transparent;
            font-size: 16px;
            font-weight: bold;
            padding-bottom: 5px;
        """)
        
        # Container for spinbox and arrow buttons
        spinbox_container = QHBoxLayout()
        spinbox_container.setSpacing(2)
        spinbox_container.setContentsMargins(0, 0, 0, 0)
        
        # SpinBox WITHOUT arrows
        spinbox = QDoubleSpinBox()
        spinbox.setRange(1.0, max_value)
        spinbox.setValue(default_value)
        spinbox.setDecimals(1)
        spinbox.setAlignment(Qt.AlignCenter)
        spinbox.setFixedWidth(195)
        spinbox.setFixedHeight(60)
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2c3e50;
                color: #ffffff;
                border: 2px solid #5dade2;
                border-radius: 8px;
                padding: 12px;
                font-size: 20px;
                font-weight: bold;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #3498db;
                background-color: #253545;
            }
        """)
        
        # Custom arrow buttons container
        arrows_widget = QWidget()
        arrows_widget.setFixedWidth(25)
        arrows_widget.setFixedHeight(60)
        arrows_widget.setStyleSheet("background-color: transparent;")
        arrows_layout = QVBoxLayout(arrows_widget)
        arrows_layout.setSpacing(2)
        arrows_layout.setContentsMargins(0, 0, 0, 0)
        
        # Up button
        up_btn = QPushButton()
        up_btn.setFixedSize(25, 29)
        up_btn.setStyleSheet("""
            QPushButton {
                background-color: #5dade2;
                border: none;
                border-radius: 4px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        
        # Create visible CSS triangle for up arrow
        up_arrow_widget = QWidget(up_btn)
        up_arrow_widget.setFixedSize(10, 6)
        up_arrow_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid white;
            }
        """)
        up_arrow_layout = QVBoxLayout(up_btn)
        up_arrow_layout.setContentsMargins(0, 0, 0, 0)
        up_arrow_layout.setAlignment(Qt.AlignCenter)
        up_arrow_layout.addWidget(up_arrow_widget)
        
        up_btn.clicked.connect(lambda: spinbox.stepUp())
        
        # Down button
        down_btn = QPushButton()
        down_btn.setFixedSize(25, 29)
        down_btn.setStyleSheet("""
            QPushButton {
                background-color: #5dade2;
                border: none;
                border-radius: 4px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        
        # Create visible CSS triangle for down arrow
        down_arrow_widget = QWidget(down_btn)
        down_arrow_widget.setFixedSize(10, 6)
        down_arrow_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid white;
            }
        """)
        down_arrow_layout = QVBoxLayout(down_btn)
        down_arrow_layout.setContentsMargins(0, 0, 0, 0)
        down_arrow_layout.setAlignment(Qt.AlignCenter)
        down_arrow_layout.addWidget(down_arrow_widget)
        
        down_btn.clicked.connect(lambda: spinbox.stepDown())
        
        arrows_layout.addWidget(up_btn)
        arrows_layout.addWidget(down_btn)
        
        # Add spinbox and arrows to container
        spinbox_container.addWidget(spinbox)
        spinbox_container.addWidget(arrows_widget)
        
        # Store reference
        if "Length" in label_text:
            self.length_spinbox = spinbox
        elif "Width" in label_text:
            self.width_spinbox = spinbox
        elif "Height" in label_text:
            self.height_spinbox = spinbox
        
        container.addWidget(label)
        container.addLayout(spinbox_container)
        
        return container
    
    def show_for_roof(self, roof_type):
        """Show panel with animation for specific roof type"""
        self.current_roof_type = roof_type
        
        # Show the widget first
        self.setVisible(True)
        
        # Animate expansion - 400px HEIGHT
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(350)
        self.animation.setStartValue(0)
        self.animation.setEndValue(400)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
    def hide_animated(self):
        """Hide panel with animation"""
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(350)
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(lambda: self.setVisible(False))
        self.animation.start()
    
    def _on_generate(self):
        """Handle generate button click"""
        if not self.current_roof_type:
            return
        
        dimensions = {
            'length': self.length_spinbox.value(),
            'width': self.width_spinbox.value(),
            'height': self.height_spinbox.value()
        }
        
        self.generate_clicked.emit(self.current_roof_type, dimensions)


class DefaultTab(QWidget):
    """Default tab - Interactive roof selection with direct ModelTab integration"""
    
    # Signals
    data_loaded = pyqtSignal()
    data_error = pyqtSignal(str)
    roof_selected = pyqtSignal(str, dict)  # roof_type, dimensions
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.model_tab = None  # Will be set by TabManager
        self.roof_cards = {}
        self.current_selected_card = None
        
        self.setup_ui()
        print("✅ Default Tab initialized")
    
    def setup_ui(self):
        """Setup Default tab UI with interactive roof cards"""
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 40, 30, 40)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # Title
        title = QLabel("🏠 Select Roof Type")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 28, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #5dade2;
                background-color: transparent;
                padding: 12px;
            }
        """)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Click on a roof type to configure dimensions")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #b8c5ce;
                background-color: transparent;
                font-size: 14px;
                padding-bottom: 15px;
            }
        """)
        main_layout.addWidget(subtitle)
        
        # Roof cards container - HORIZONTAL LAYOUT
        cards_container = QWidget()
        cards_container.setStyleSheet("background-color: transparent;")
        cards_container.setFixedWidth(860)  # EXACT: 4*200 + 3*20 = 860px
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setSpacing(20)  # Space between cards
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # Define roof types with icons
        roof_types = [
            ('flat', 'Flat Roof', '⬜'),
            ('gable', 'Gable Roof', '🏠'),
            ('pyramid', 'Pyramid Roof', '🔺'),
            ('hip', 'Hip Roof', '🏔️')
        ]
        
        # Create cards in horizontal row
        for roof_type, roof_name, icon in roof_types:
            card = RoofTypeCard(roof_type, roof_name, icon)
            card.clicked.connect(self._on_roof_card_clicked)
            self.roof_cards[roof_type] = card
            cards_layout.addWidget(card)
        
        main_layout.addWidget(cards_container)
        
        # Dimension input panel (initially hidden)
        self.dimension_panel = DimensionInputPanel()
        self.dimension_panel.generate_clicked.connect(self._on_generate_roof)
        main_layout.addWidget(self.dimension_panel, alignment=Qt.AlignHCenter)
        
        main_layout.addStretch()
        
        print("✅ Default Tab UI setup completed")
    
    def set_model_tab(self, model_tab):
        """
        Set reference to ModelTab - called by TabManager
        This connects the DefaultTab to the ModelTab for roof rendering
        """
        self.model_tab = model_tab
        print(f"✅ DefaultTab: ModelTab reference set")
        
        # Verify the model tab has create_building method
        if hasattr(model_tab, 'create_building'):
            print(f"✅ DefaultTab: ModelTab has create_building method")
        else:
            print(f"❌ DefaultTab: ModelTab missing create_building method")
        
        # Verify plotter exists
        if hasattr(model_tab, 'plotter') and model_tab.plotter:
            print(f"✅ DefaultTab: ModelTab plotter is available")
        else:
            print(f"⚠️ DefaultTab: ModelTab plotter not available")
        
        # Connect the roof_selected signal to render handler
        try:
            # Disconnect any previous connections
            self.roof_selected.disconnect()
        except:
            pass
        
        self.roof_selected.connect(self._handle_roof_selected_signal)
        print(f"✅ DefaultTab: roof_selected signal connected")
    
    def _handle_roof_selected_signal(self, roof_type, dimensions):
        """
        Handle the roof_selected signal by rendering in ModelTab
        This is the bridge between the signal and the actual rendering
        """
        try:
            print(f"🌉 DefaultTab: Handling roof_selected signal for {roof_type}")
            print(f"📐 Dimensions: {dimensions}")
            
            if not self.model_tab:
                print("❌ DefaultTab: ModelTab not available")
                return False
            
            # Check if model tab has create_building method
            if not hasattr(self.model_tab, 'create_building'):
                print("❌ DefaultTab: ModelTab has no create_building method")
                return False
            
            # Switch to Model tab first
            if not self._switch_to_model_tab():
                print("❌ DefaultTab: Failed to switch to model tab")
                return False
            
            # Wait for tab to be visible, then render
            QTimer.singleShot(200, lambda: self._render_roof_delayed(roof_type, dimensions))
            
            return True
            
        except Exception as e:
            print(f"❌ DefaultTab: Error handling roof_selected signal: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _switch_to_model_tab(self):
        """Switch to model tab"""
        try:
            if not hasattr(self.main_window, 'content_tabs'):
                print("❌ DefaultTab: content_tabs not found")
                return False
            
            content_tabs = self.main_window.content_tabs
            
            # Find model tab index
            model_tab_index = -1
            for i in range(content_tabs.count()):
                if content_tabs.widget(i) == self.model_tab:
                    model_tab_index = i
                    break
            
            if model_tab_index < 0:
                print("❌ DefaultTab: Model tab not found in content_tabs")
                return False
            
            # Switch to model tab
            content_tabs.setCurrentIndex(model_tab_index)
            print(f"✅ DefaultTab: Switched to model tab (index {model_tab_index})")
            
            # Force UI update
            content_tabs.update()
            content_tabs.repaint()
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            return True
            
        except Exception as e:
            print(f"❌ DefaultTab: Failed to switch to model tab: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _render_roof_delayed(self, roof_type, dimensions):
        """Render roof with proper camera positioning - COMPLETE FIX with cleanup"""
        try:
            print(f"🏗️ DefaultTab: Creating {roof_type} roof")
            print(f"📐 Dimensions: L={dimensions['length']}m, W={dimensions['width']}m, H={dimensions['height']}m")
            
            # Extract dimensions
            length = float(dimensions.get('length', 10.0))
            width = float(dimensions.get('width', 8.0))
            height = float(dimensions.get('height', 3.0))
            
            # Map hip to pyramid if not implemented
            actual_roof_type = roof_type
            if roof_type == 'hip':
                print(f"⚠️ Hip roof mapped to pyramid")
                actual_roof_type = 'pyramid'
            
            # CRITICAL: Complete cleanup before creating new building
            print("🧹 Starting complete cleanup...")
            
            # 1. Clear building actors
            if hasattr(self.model_tab, '_clear_building_actors'):
                self.model_tab._clear_building_actors()
                print(f"✅ Building actors cleared")
            
            # 2. Force garbage collection to ensure cleanup
            import gc
            gc.collect()
            print(f"✅ Garbage collection completed")
            
            # 3. Small delay to ensure cleanup is complete
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Create building points - CENTERED at origin
            half_length = length / 2
            half_width = width / 2
            
            points = [
                [-half_length, -half_width],
                [half_length, -half_width],
                [half_length, half_width],
                [-half_length, half_width]
            ]
            
            print(f"📍 Building points (centered): {points}")
            
            # Create building with explicit dimensions parameter
            success = self.model_tab.create_building(
                points=points,
                height=height,
                roof_type=actual_roof_type,
                roof_pitch=30.0,
                scale=1.0,
                dimensions={'length': length, 'width': width, 'height': height}
            )
            
            if success:
                print(f"✅ Building created successfully")
                
                # CRITICAL: Set camera after a delay
                QTimer.singleShot(300, lambda: self._set_camera_view(length, width, height))
                
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(
                        f"✅ {roof_type.capitalize()} roof created",
                        3000
                    )
            else:
                print(f"❌ Building creation failed")
            
            return success
            
        except Exception as e:
            print(f"❌ Error creating roof: {e}")
            import traceback
            traceback.print_exc()
            return False

    
    def _set_camera_view(self, length, width, height):
        """Set optimal camera view - CRITICAL FIX"""
        try:
            if not self.model_tab or not hasattr(self.model_tab, 'plotter'):
                print("❌ No plotter available for camera")
                return
            
            plotter = self.model_tab.plotter
            if not plotter:
                print("❌ Plotter is None")
                return
            
            # Calculate optimal camera position
            max_dim = max(length, width, height)
            distance = max_dim * 2.5
            
            # Camera position (from angle to see the roof)
            camera_pos = [
                distance * 0.7,   # X
                -distance * 0.7,  # Y
                distance * 0.6    # Z (elevated)
            ]
            
            # Look at center of building
            focal_point = [0, 0, height / 2]
            
            # Set camera
            plotter.camera_position = [
                camera_pos,
                focal_point,
                [0, 0, 1]  # Up vector
            ]
            
            print(f"📷 Camera set: pos={camera_pos}, focal={focal_point}")
            
            # Force render
            if hasattr(plotter, 'render'):
                plotter.render()
                print(f"✅ Plotter rendered")
            
            # Update display
            if hasattr(plotter, 'update'):
                plotter.update()
            
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
        except Exception as e:
            print(f"❌ Camera setup failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_roof_card_clicked(self, roof_type):
        """Handle roof card click"""
        print(f"🏠 Roof card clicked: {roof_type}")
        
        # Update card selection states
        for card_type, card in self.roof_cards.items():
            card.set_selected(card_type == roof_type)
        
        # Show dimension panel with animation
        if self.current_selected_card != roof_type:
            self.dimension_panel.show_for_roof(roof_type)
            self.current_selected_card = roof_type
        else:
            # Toggle off if clicking the same card
            self.dimension_panel.hide_animated()
            self.current_selected_card = None
            for card in self.roof_cards.values():
                card.set_selected(False)
    
    def _on_generate_roof(self, roof_type, dimensions):
        """Handle generate roof request"""
        try:
            print(f"📡 Default Tab: Generating {roof_type} roof with dimensions: {dimensions}")
            
            # Emit signal (which triggers _handle_roof_selected_signal)
            self.roof_selected.emit(roof_type, dimensions)
            
            return True
        except Exception as e:
            print(f"❌ Error generating roof: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def trigger_roof_selection(self, roof_type, dimensions):
        """Trigger roof selection signal (called from DefaultTabPanel if needed)"""
        try:
            print(f"📡 Default Tab: Emitting roof_selected signal for {roof_type}")
            self.roof_selected.emit(roof_type, dimensions)
            return True
        except Exception as e:
            print(f"❌ Error emitting roof_selected signal: {e}")
            return False
    
    def refresh_view(self):
        """Refresh the default view"""
        print("🔄 Default view refreshed")
        
        # Reset selections
        self.current_selected_card = None
        for card in self.roof_cards.values():
            card.set_selected(False)
        
        # Hide dimension panel
        if self.dimension_panel.isVisible():
            self.dimension_panel.hide_animated()
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Default tab cleaned up")
        
        # Stop any running animations
        if hasattr(self.dimension_panel, 'animation'):
            if self.dimension_panel.animation and self.dimension_panel.animation.state() == QPropertyAnimation.Running:
                self.dimension_panel.animation.stop()
