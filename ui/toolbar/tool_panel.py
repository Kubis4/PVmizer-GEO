from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt

class ToolPanel(QWidget):
    """Panel containing all the tool buttons"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up layout
        layout = QVBoxLayout(self)
        self.setMaximumWidth(250)
        
        # Create title for sidebar
        title_label = QLabel("Roof Design Tools")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Create buttons for the sidebar
        self.google_maps_btn = self.create_button("Load Google Maps")
        self.capture_screenshot_btn = self.create_button("Capture Screenshot")
        self.clear_lines_btn = self.create_button("Clear Lines")
        self.preview_3d_btn = self.create_button("Generated 3D Model")
        self.export_btn = self.create_button("Export 3D Model")
        
        # Add buttons to layout
        layout.addWidget(self.google_maps_btn)
        layout.addWidget(self.capture_screenshot_btn)
        layout.addWidget(self.clear_lines_btn)
        layout.addWidget(self.preview_3d_btn)
        layout.addWidget(self.export_btn)
        
        # Add separator before instructions
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Update instructions for automatic connections
        instructions = QLabel(
            "Instructions:\n\n"
            "1\. Find a roof in Google Maps\n"
            "2\. Capture a screenshot\n"
            "3\. Click to draw roof outline\n"
            "4\. Points auto-connect when close\n"
            "5\. Generate 3D model from outline"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; margin-top: 10px;")
        layout.addWidget(instructions)
        
        # Initially disable some buttons
        self.clear_lines_btn.setEnabled(False)
        self.preview_3d_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def create_button(self, text):
        """Helper method to create a button with consistent styling"""
        button = QPushButton(text)
        button.setMinimumHeight(40)
        return button