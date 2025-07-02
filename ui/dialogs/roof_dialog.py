import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("Warning: PyVista not available. 3D visualization will be disabled.")


class RoofDimensionDialog(QDialog):
    """Dialog for entering roof dimensions before creating a 3D model"""

    def __init__(self, roof_type, parent=None):
        super().__init__(parent)
        self.roof_type = roof_type
        self.dimensions = None

        # Set up dialog UI
        self.setWindowTitle(f"{roof_type} Roof Dimensions")
        self.setMinimumWidth(450)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel(f"Enter Dimensions for {self.roof_type} Roof")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        # Description based on roof type
        description = QLabel(self.get_roof_description())
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-size: 12px; color: #CCCCCC; margin-bottom: 20px;")
        layout.addWidget(description)

        # Form layout for dimensions
        form_layout = QFormLayout()
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(10)

        self.length_input = QLineEdit()
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()

        # Add input validation (integers only)
        validator = QIntValidator(1, 100)
        self.length_input.setValidator(validator)
        self.width_input.setValidator(validator)
        self.height_input.setValidator(validator)

        # Set placeholders for better UX
        self.length_input.setPlaceholderText("Enter length (e.g., 10)")
        self.width_input.setPlaceholderText("Enter width (e.g., 8)")
        self.height_input.setPlaceholderText("Enter height (e.g., 5)")

        # Add inputs to form layout
        form_layout.addRow(self._styled_label("Length (m):"), self.length_input)
        form_layout.addRow(self._styled_label("Width (m):"), self.width_input)
        form_layout.addRow(self._styled_label("Height (m):"), self.height_input)

        # Group box for dimensions
        dimensions_group = QGroupBox("📐 Roof Dimensions")
        dimensions_group.setLayout(form_layout)
        dimensions_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #E0E0E0;
                background-color: #34495e;
                border: 1px solid #495057;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #3398db;
                background-color: #2c3e50;
                border-radius: 4px;
            }
        """)
        layout.addWidget(dimensions_group)

        # Buttons
        button_box = QDialogButtonBox()
        ok_button = QPushButton("Create 3D Model")
        cancel_button = QPushButton("Cancel")

        # Style buttons
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        # Add buttons to the button box
        button_box.addButton(ok_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)

        # Connect buttons to actions
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(button_box)

    def get_roof_description(self):
        """Return a description based on the roof type"""
        descriptions = {
            "Flat": (
                "A Flat Roof is a horizontal roof with a slight slope "
                "for drainage. It is commonly used in modern buildings."
            ),
            "Gable": (
                "A Gable Roof is a classic roof shape with two sloping sides "
                "that meet at a ridge. It's simple, cost-effective, and provides good ventilation."
            ),
            "Hip": (
                "A Hip Roof has slopes on all four sides, making it more stable "
                "and resistant to wind compared to a gable roof."
            ),
            "Pyramid": (
                "A Pyramid Roof is a type of hip roof with all sides meeting "
                "at a single point, commonly used for smaller structures or decorative purposes."
            ),
        }
        return descriptions.get(self.roof_type, "No description available for this roof type.")

    def _styled_label(self, text):
        """Helper to create styled QLabel"""
        label = QLabel(text)
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E0E0E0;")
        return label

    def apply_styles(self):
        """Apply consistent dialog styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                border: 1px solid #495057;
                border-radius: 10px;
            }
        """)

    def validate_and_accept(self):
        """Validate inputs and accept dialog"""
        try:
            length = float(self.length_input.text())
            width = float(self.width_input.text())
            height = float(self.height_input.text())
            self.dimensions = {"length": length, "width": width, "height": height}
            self.accept()
        except ValueError:
            error_message = QLabel("❌ Please enter valid numerical values for all dimensions.")
            error_message.setStyleSheet("color: #e74c3c; font-weight: bold;")
            error_message.setAlignment(Qt.AlignCenter)
            self.layout().addWidget(error_message)
