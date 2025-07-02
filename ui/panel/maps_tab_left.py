from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox, QFrame, QDialog
)
from PyQt5.QtCore import pyqtSignal
from ui.dialogs.roof_dialog import RoofDimensionDialog  # Import RoofDimensionDialog class


class MapsTabPanel(QWidget):
    """Maps tab panel with screenshot tools and roof type buttons"""

    # Signals
    snip_requested = pyqtSignal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.roof_buttons = {}  # Store roof buttons for connections
        self.setup_ui()
        print("✅ Maps Tab Panel initialized")

    def setup_ui(self):
        """Setup Maps tab UI with buttons"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Screenshot Tools Group
        self._create_screenshot_section(main_layout)

        # Roof Types Section
        self._create_roof_types_section(main_layout)

        # Add stretch to center content
        main_layout.addStretch()

        print("✅ Maps Tab UI setup completed")

    def _create_screenshot_section(self, parent_layout):
        """Create screenshot section with button"""
        # Screenshot group
        screenshot_group = QGroupBox("📸 Screenshot Tools")
        screenshot_layout = QVBoxLayout(screenshot_group)
        screenshot_layout.setContentsMargins(10, 15, 10, 10)
        screenshot_layout.setSpacing(10)

        # Snip Screenshot button
        self.snip_btn = QPushButton("📸 Snip Screenshot")
        self.snip_btn.setMinimumHeight(40)
        self.snip_btn.setToolTip(
            "Capture a screenshot of the map area for building outline drawing"
        )

        # Apply button styling
        self.snip_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        # Connect the button
        self.snip_btn.clicked.connect(self._emit_snip_requested)

        screenshot_layout.addWidget(self.snip_btn)
        parent_layout.addWidget(screenshot_group)

    def _create_roof_types_section(self, parent_layout):
        """Create roof types section with buttons"""
        # Roof Types group
        roof_types_group = QGroupBox("🏠 Roof Types")
        roof_types_layout = QVBoxLayout(roof_types_group)
        roof_types_layout.setContentsMargins(10, 15, 10, 10)
        roof_types_layout.setSpacing(15)

        # Roof types and descriptions
        roof_types = [
            ("Gable", "🏠", "Traditional triangular roof design"),
            ("Hip", "🏘️", "Roof with slopes on all four sides"),
            ("Flat", "🏢", "Modern flat roof design"),
            ("Pyramid", "🗻", "Four-sided roof with a peak at the top"),
        ]

        for roof_type, icon, description in roof_types:
            # Wrapper frame for button and description
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.setSpacing(5)

            # Button for roof type
            btn = QPushButton(f"{icon} {roof_type} Roof")
            btn.setMinimumHeight(40)
            btn.setToolTip(description)

            # Apply button styling
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 12px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)

            # Connect button to dialog opening
            btn.clicked.connect(lambda _, rt=roof_type: self._show_roof_dialog(rt))

            # Description label
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
            desc_label.setWordWrap(True)

            # Add button and description to layout
            frame_layout.addWidget(btn)
            frame_layout.addWidget(desc_label)

            # Add frame to the roof types layout
            roof_types_layout.addWidget(frame)

            # Store button for further use
            self.roof_buttons[roof_type] = btn

        parent_layout.addWidget(roof_types_group)

    def _emit_snip_requested(self):
        """Handle snip screenshot request"""
        print("📸 Snip screenshot requested")
        self.snip_requested.emit()

    def _show_roof_dialog(self, roof_type):
        """Open the roof dimension dialog for the selected roof type"""
        print(f"🏠 Opening {roof_type} Roof Dialog...")
        dialog = RoofDimensionDialog(roof_type, self)
        if dialog.exec_() == QDialog.Accepted:
            dimensions = dialog.dimensions
            print(f"✅ {roof_type} Roof dimensions confirmed: {dimensions}")

            # Access ContentTabWidget from the main window
            if hasattr(self.main_window, 'content_tabs'):
                self.main_window.content_tabs.render_roof_model(roof_type, dimensions)
            else:
                print("❌ ContentTabWidget not found in main window")
        else:
            print(f"❌ {roof_type} Roof dialog canceled")

    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up Maps Tab Panel...")
        self.main_window = None
        self.snip_btn = None
        self.roof_buttons.clear()