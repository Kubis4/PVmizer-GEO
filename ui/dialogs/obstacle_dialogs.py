from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QRadioButton, 
                            QLabel, QPushButton, QGroupBox, QLineEdit, 
                            QGridLayout, QMessageBox, QButtonGroup)
from PyQt5.QtCore import Qt

# Import the dialog styles
try:
    from ui.styles.dialog_styles import DialogStyles
    DIALOG_STYLES_AVAILABLE = True
except ImportError:
    DIALOG_STYLES_AVAILABLE = False

class RoofObstacleDialogs(QDialog):
   
    def __init__(self, parent=None):
        """Initialize the dialog"""
        super().__init__(parent)
        
        # Store results
        self.selected_type = None
        self.dimensions = None
        self.use_default = True
        
        # Default dimensions for different obstacle types (removed translations)
        self.default_dimensions = {
            'Chimney': (1, 1, 3),          # width, length, height
            'Roof Window': (1.0, 2, 0.15),  # width, length, height
            'Ventilation': (0.4, 0.4, 0.5)  # diameter, diameter, height
        }
        
        # Size limits based on obstacle type (in meters)
        self.size_limits = {
            'Chimney': {
                "width": (0.3, 2),    # min, max
                "length": (0.3, 2),
                "height": (0.5, 5)
            },
            'Roof Window': {
                "width": (0.4, 2.0),
                "length": (0.4, 2.5),
                "height": (0.05, 0.3)
            },
            'Ventilation': {
                "width": (0.1, 1.0),    # diameter
                "length": (0.1, 1.0),   # diameter (same as width)
                "height": (0.2, 1.0)
            }
        }
        
        # Setup UI
        self.setWindowTitle('Obstacle Properties')
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        
        # Apply centralized styling
        if DIALOG_STYLES_AVAILABLE:
            self.setStyleSheet(DialogStyles.get_dark_dialog_style())
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Title label
        title_label = DialogStyles.create_styled_label('Obstacle Selection & Properties', 'title') if DIALOG_STYLES_AVAILABLE else QLabel('Obstacle Selection & Properties')
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        description = DialogStyles.create_styled_label('Select an obstacle type and configure its dimensions.', 'description') if DIALOG_STYLES_AVAILABLE else QLabel('Select an obstacle type and configure its dimensions.')
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description)
        
        # Type selection group
        type_group = QGroupBox('🏗️ Select Obstacle Type')
        type_layout = QVBoxLayout()
        type_layout.setContentsMargins(15, 15, 15, 15)
        type_layout.setSpacing(10)
        type_group.setLayout(type_layout)
        main_layout.addWidget(type_group)
        
        # Radio buttons for obstacle types
        self.type_group = QButtonGroup(self)
        obstacle_types = ['Chimney', 'Roof Window', 'Ventilation']
        
        self.type_radios = {}
        for i, obs_type in enumerate(obstacle_types):
            radio = QRadioButton(obs_type)
            type_layout.addWidget(radio)
            self.type_group.addButton(radio, i)
            self.type_radios[obs_type] = radio
        
        # Default select first option
        self.type_radios['Chimney'].setChecked(True)
        
        # Connect the type selection to update dimensions
        self.type_group.buttonClicked.connect(self.update_dimension_labels)
        
        # Dimensions group
        dim_group = QGroupBox('📐 Dimensions')
        dim_layout = QVBoxLayout()
        dim_layout.setContentsMargins(15, 15, 15, 15)
        dim_layout.setSpacing(10)
        dim_group.setLayout(dim_layout)
        main_layout.addWidget(dim_group)
        
        # Radio buttons for default vs custom
        radio_layout = QVBoxLayout()
        dim_layout.addLayout(radio_layout)
        
        # Radio button group for default/custom selection
        self.dim_option_group = QButtonGroup(self)
        
        self.default_radio = QRadioButton('Use Default Dimensions')
        self.default_radio.setChecked(True)
        radio_layout.addWidget(self.default_radio)
        self.dim_option_group.addButton(self.default_radio)
        
        # Add default dimension label
        self.default_label = QLabel()
        radio_layout.addWidget(self.default_label)
        
        self.custom_radio = QRadioButton('Use Custom Dimensions')
        radio_layout.addWidget(self.custom_radio)
        self.dim_option_group.addButton(self.custom_radio)
        
        # Size limits label
        self.limits_label = QLabel()
        radio_layout.addWidget(self.limits_label)
        
        # Group for dimension input fields
        input_group = QGroupBox('📏 Custom Dimensions (meters)')
        input_layout = QGridLayout()
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        input_group.setLayout(input_layout)
        dim_layout.addWidget(input_group)
        
        # Width/Diameter input
        width_label = DialogStyles.create_styled_label('Width:', 'form') if DIALOG_STYLES_AVAILABLE else QLabel('Width:')
        self.width_label = width_label
        input_layout.addWidget(self.width_label, 0, 0)
        self.width_input = QLineEdit()
        self.width_input.setEnabled(False)  # Initially disabled
        self.width_input.setPlaceholderText("Enter width in meters")
        input_layout.addWidget(self.width_input, 0, 1)
        
        # Length input
        length_label = DialogStyles.create_styled_label('Length:', 'form') if DIALOG_STYLES_AVAILABLE else QLabel('Length:')
        self.length_label = length_label
        input_layout.addWidget(self.length_label, 1, 0)
        self.length_input = QLineEdit()
        self.length_input.setEnabled(False)  # Initially disabled
        self.length_input.setPlaceholderText("Enter length in meters")
        input_layout.addWidget(self.length_input, 1, 1)
        
        # Height input
        height_label = DialogStyles.create_styled_label('Height:', 'form') if DIALOG_STYLES_AVAILABLE else QLabel('Height:')
        input_layout.addWidget(height_label, 2, 0)
        self.height_input = QLineEdit()
        self.height_input.setEnabled(False)  # Initially disabled
        self.height_input.setPlaceholderText("Enter height in meters")
        input_layout.addWidget(self.height_input, 2, 1)
        
        # Connect radio buttons to enable/disable fields
        self.dim_option_group.buttonClicked.connect(self.toggle_input_fields)
        
        # Set initial values based on default selection (Chimney)
        self.update_dimension_labels()
        
        # Button box
        button_box = QDialogButtonBox()
        main_layout.addWidget(button_box)
        
        # Create and style the OK button
        self.ok_button = QPushButton('Place Obstacle')
        
        # Create and style the Cancel button (red)
        cancel_button = QPushButton('Cancel')
        cancel_button.setObjectName("cancel_button")
        
        # Add buttons to the button box
        button_box.addButton(self.ok_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)
        
        # Connect the buttons
        self.ok_button.clicked.connect(self.accept_with_validation)
        cancel_button.clicked.connect(self.reject)
    
    def update_dimension_labels(self):
        """Update dimension values based on selected obstacle type"""
        # Get the selected obstacle type
        for obs_type, radio in self.type_radios.items():
            if radio.isChecked():
                self.selected_type = obs_type
                break
        
        # Get default dimensions for this type
        if self.selected_type in self.default_dimensions:
            dims = self.default_dimensions[self.selected_type]
            
            # Special handling for ventilation (diameter vs width/length)
            if self.selected_type == 'Ventilation':
                self.width_label.setText('Diameter:')
                self.length_label.setText('Diameter:')
                self.length_input.setEnabled(False)  # Always disabled for ventilation
                
                # Update default label
                self.default_label.setText(f'Default: Diameter {dims[0]}m, Height {dims[2]}m')
            else:
                self.width_label.setText('Width:')
                self.length_label.setText('Length:')
                
                # Only enable length if custom dimensions and not ventilation
                should_enable = self.custom_radio.isChecked() and self.selected_type != 'Ventilation'
                self.length_input.setEnabled(should_enable)
                
                # Update default label
                self.default_label.setText(f'Default: {dims[0]}m × {dims[1]}m × {dims[2]}m (W×L×H)')
            
            # Update limit information
            limits = self.size_limits.get(
                self.selected_type, 
                {"width": (0.1, 2.0), "length": (0.1, 2.0), "height": (0.1, 5.0)}
            )
            
            # Different label for ventilation
            if self.selected_type == 'Ventilation':
                limit_text = f'Limits: Diameter {limits["width"][0]}-{limits["width"][1]}m, Height {limits["height"][0]}-{limits["height"][1]}m'
            else:
                limit_text = f'Limits: Width {limits["width"][0]}-{limits["width"][1]}m, Length {limits["length"][0]}-{limits["length"][1]}m, Height {limits["height"][0]}-{limits["height"][1]}m'
            
            self.limits_label.setText(limit_text)
            
            # Update input fields with default values
            self.width_input.setText(str(dims[0]))
            self.length_input.setText(str(dims[1]))
            self.height_input.setText(str(dims[2]))
    
    def toggle_input_fields(self, button):
        """Enable/disable input fields based on radio selection"""
        enabled = button == self.custom_radio
        
        # Enable/disable fields
        self.width_input.setEnabled(enabled)
        
        # Length is special case - only enabled for non-ventilation custom dimensions
        if self.selected_type == 'Ventilation':
            self.length_input.setEnabled(False)  # Always disabled for ventilation
        else:
            self.length_input.setEnabled(enabled)
            
        self.height_input.setEnabled(enabled)
    
    def accept_with_validation(self):
        """Validate inputs before accepting"""
        # Get the selected obstacle type again to be safe
        for obs_type, radio in self.type_radios.items():
            if radio.isChecked():
                self.selected_type = obs_type
                break
        
        # Get the appropriate size limits
        limits = self.size_limits.get(
            self.selected_type, 
            {"width": (0.1, 2.0), "length": (0.1, 2.0), "height": (0.1, 2.0)}
        )
        
        # Check if using default or custom
        self.use_default = self.default_radio.isChecked()
        
        if self.use_default:
            # Use default dimensions
            self.dimensions = self.default_dimensions.get(self.selected_type)
            self.accept()
        else:
            # Validate custom dimensions
            try:
                width = float(self.width_input.text())
                length = float(self.length_input.text())
                height = float(self.height_input.text())
                
                # Validate against limits
                dim_name = 'Diameter' if self.selected_type == 'Ventilation' else 'Width'
                
                if width < limits['width'][0] or width > limits['width'][1]:
                    QMessageBox.warning(
                        self, 
                        'Invalid Dimensions', 
                        f'{dim_name} must be between {limits["width"][0]} and {limits["width"][1]} meters.'
                    )
                    return
                
                if self.selected_type != 'Ventilation' and (length < limits['length'][0] or length > limits['length'][1]):
                    QMessageBox.warning(
                        self, 
                        'Invalid Dimensions', 
                        f'Length must be between {limits["length"][0]} and {limits["length"][1]} meters.'
                    )
                    return
                
                if height < limits['height'][0] or height > limits['height'][1]:
                    QMessageBox.warning(
                        self, 
                        'Invalid Dimensions', 
                        f'Height must be between {limits["height"][0]} and {limits["height"][1]} meters.'
                    )
                    return
                
                # For ventilation, enforce same width and length (diameter)
                if self.selected_type == 'Ventilation':
                    length = width
                
                # Store validated dimensions
                self.dimensions = (width, length, height)
                self.accept()
                
            except ValueError:
                QMessageBox.warning(
                    self, 
                    'Invalid Input', 
                    'Please enter valid numbers for all dimensions.'
                )
                return
    
    def get_selection(self):
        """Get the dialog results"""
        return self.selected_type, self.dimensions, self.use_default
    
    def show_selection_dialog(self, callback=None):
        # Show the dialog
        result = self.exec_()
        
        # Process results
        if result == QDialog.Accepted:
            type_selected, dimensions, _ = self.get_selection()
            if callback:
                callback(type_selected, dimensions)
            return type_selected, dimensions
        else:
            if callback:
                callback(None, None)
            return None, None
