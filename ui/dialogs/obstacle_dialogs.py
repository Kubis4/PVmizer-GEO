from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QRadioButton, 
                            QLabel, QPushButton, QGroupBox, QLineEdit, 
                            QGridLayout, QMessageBox, QButtonGroup)
from PyQt5.QtCore import Qt
from translations import _

class RoofObstacleDialogs(QDialog):
   
    def __init__(self, parent=None):
        """Initialize the dialog"""
        super().__init__(parent)
        
        # Store results
        self.selected_type = None
        self.dimensions = None
        self.use_default = True
        
        # Default dimensions for different obstacle types
        self.default_dimensions = {
            _('chimney'): (1, 1, 3),          # width, length, height
            _('roof_window'): (1.0, 2, 0.15),  # width, length, height
            _('ventilation'): (0.4, 0.4, 0.5)  # diameter, diameter, height
        }
        
        # Size limits based on obstacle type (in meters)
        self.size_limits = {
            _('chimney'): {
                "width": (0.3, 2),    # min, max
                "length": (0.3, 2),
                "height": (0.5, 5)
            },
            _('roof_window'): {
                "width": (0.4, 2.0),
                "length": (0.4, 2.5),
                "height": (0.05, 0.3)
            },
            _('ventilation'): {
                "width": (0.1, 1.0),    # diameter
                "length": (0.1, 1.0),   # diameter (same as width)
                "height": (0.2, 1.0)
            }
        }
        
        # Setup UI
        self.setWindowTitle(_('obstacle_properties'))
        self.setMinimumWidth(450)
        
        # ✅ CRITICAL: Apply centralized styling
        self._apply_dialog_styling()
        
        self.setup_ui()
    
    def _apply_dialog_styling(self):
        """Apply centralized dialog styling"""
        try:
            from ui.styles.dialog_styles import DialogStyles
            
            # Try to detect current theme from main window
            theme = "dark"  # Default to dark
            if hasattr(self.parent(), 'main_window') and hasattr(self.parent().main_window, 'theme_manager'):
                theme = self.parent().main_window.theme_manager.current_theme
            elif hasattr(self.parent(), 'theme_manager'):
                theme = self.parent().theme_manager.current_theme
            
            # Apply appropriate style
            if theme == "dark":
                style = DialogStyles.get_dark_dialog_style()
            else:
                style = DialogStyles.get_light_dialog_style()
            
            self.setStyleSheet(style)
            print("✅ Applied centralized dialog styling to obstacle dialog")
            
        except ImportError:
            print("⚠️ Dialog styles not available, using default styling")
        except Exception as e:
            print(f"❌ Error applying dialog styling: {e}")
    
    def setup_ui(self):
        """Set up the dialog UI"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Title label
        title_label = QLabel(_('obstacle_selection_properties'))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Type selection group
        type_group = QGroupBox(_('select_obstacle_type'))
        type_layout = QVBoxLayout()
        type_group.setLayout(type_layout)
        main_layout.addWidget(type_group)
        
        # Radio buttons for obstacle types
        self.type_group = QButtonGroup(self)
        obstacle_types = [_('chimney'), _('roof_window'), _('ventilation')]
        
        self.type_radios = {}
        for i, obs_type in enumerate(obstacle_types):
            radio = QRadioButton(obs_type)
            type_layout.addWidget(radio)
            self.type_group.addButton(radio, i)
            self.type_radios[obs_type] = radio
        
        # Default select first option
        self.type_radios[_('chimney')].setChecked(True)
        
        # Connect the type selection to update dimensions
        self.type_group.buttonClicked.connect(self.update_dimension_labels)
        
        # Dimensions group
        dim_group = QGroupBox(_('dimensions'))
        dim_layout = QVBoxLayout()
        dim_group.setLayout(dim_layout)
        main_layout.addWidget(dim_group)
        
        # Radio buttons for default vs custom
        radio_layout = QVBoxLayout()
        dim_layout.addLayout(radio_layout)
        
        # Radio button group for default/custom selection
        self.dim_option_group = QButtonGroup(self)
        
        self.default_radio = QRadioButton(_('use_default_dimensions'))
        self.default_radio.setChecked(True)
        radio_layout.addWidget(self.default_radio)
        self.dim_option_group.addButton(self.default_radio)
        
        # Add default dimension label
        self.default_label = QLabel()
        self.default_label.setStyleSheet("color: gray; margin-left: 20px;")
        radio_layout.addWidget(self.default_label)
        
        self.custom_radio = QRadioButton(_('use_custom_dimensions'))
        radio_layout.addWidget(self.custom_radio)
        self.dim_option_group.addButton(self.custom_radio)
        
        # Size limits label
        self.limits_label = QLabel()
        self.limits_label.setStyleSheet("color: gray; margin-left: 20px;")
        radio_layout.addWidget(self.limits_label)
        
        # Group for dimension input fields
        input_group = QGroupBox(_('custom_dimensions_meters'))
        input_layout = QGridLayout()
        input_group.setLayout(input_layout)
        dim_layout.addWidget(input_group)
        
        # Width/Diameter input
        self.width_label = QLabel(_('width'))
        input_layout.addWidget(self.width_label, 0, 0)
        self.width_input = QLineEdit()
        self.width_input.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.width_input, 0, 1)
        
        # Length input
        self.length_label = QLabel(_('length'))
        input_layout.addWidget(self.length_label, 1, 0)
        self.length_input = QLineEdit()
        self.length_input.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.length_input, 1, 1)
        
        # Height input
        input_layout.addWidget(QLabel(_('height')), 2, 0)
        self.height_input = QLineEdit()
        self.height_input.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.height_input, 2, 1)
        
        # Connect radio buttons to enable/disable fields
        self.dim_option_group.buttonClicked.connect(self.toggle_input_fields)
        
        # Set initial values based on default selection (Chimney)
        self.update_dimension_labels()
        
        # Replace horizontal button layout with a QDialogButtonBox
        button_box = QDialogButtonBox()
        main_layout.addWidget(button_box)
        
        # Create and style the OK button
        self.ok_button = QPushButton(_('place_obstacle'))
        self.ok_button.setMinimumWidth(120)
        self.ok_button.setMinimumHeight(40)
        self.ok_button.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # Create and style the Cancel button (red)
        cancel_button = QPushButton(_('cancel'))
        cancel_button.setMinimumHeight(40)
        cancel_button.setMinimumWidth(120)
        cancel_button.setStyleSheet("background-color: #d9534f; color: white; font-size: 12px;")
        
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
            if self.selected_type == _('ventilation'):
                self.width_label.setText(_('diameter'))
                self.length_label.setText(_('diameter'))
                self.length_label.setStyleSheet("color: gray;")
                self.length_input.setEnabled(False)  # Always disabled for ventilation
                
                # Update default label
                self.default_label.setText(
                    _('default_ventilation_format').format(
                        diameter=dims[0],
                        height=dims[2]
                    )
                )
            else:
                self.width_label.setText(_('width'))
                self.length_label.setText(_('length'))
                self.length_label.setStyleSheet("")
                
                # Only enable length if custom dimensions and not ventilation
                should_enable = self.custom_radio.isChecked() and self.selected_type != _('ventilation')
                self.length_input.setEnabled(should_enable)
                
                # Update default label
                self.default_label.setText(
                    _('default_dimensions_format').format(
                        width=dims[0],
                        length=dims[1],
                        height=dims[2]
                    )
                )
            
            # Update limit information
            limits = self.size_limits.get(
                self.selected_type, 
                {"width": (0.1, 2.0), "length": (0.1, 2.0), "height": (0.1, 5.0)}
            )
            
            # Different label for ventilation
            if self.selected_type == _('ventilation'):
                limit_text = _('ventilation_limits_format').format(
                    min_diameter=limits['width'][0],
                    max_diameter=limits['width'][1],
                    min_height=limits['height'][0],
                    max_height=limits['height'][1]
                )
            else:
                limit_text = _('size_limits_format').format(
                    min_width=limits['width'][0],
                    max_width=limits['width'][1],
                    min_length=limits['length'][0],
                    max_length=limits['length'][1],
                    min_height=limits['height'][0],
                    max_height=limits['height'][1]
                )
            
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
        if self.selected_type == _('ventilation'):
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
                dim_name = _('diameter') if self.selected_type == _('ventilation') else _('width')
                
                if width < limits['width'][0] or width > limits['width'][1]:
                    QMessageBox.warning(
                        self, 
                        _('invalid_dimensions'), 
                        _('dimension_range_error').format(
                            dimension=dim_name,
                            min=limits['width'][0],
                            max=limits['width'][1]
                        )
                    )
                    return
                
                if self.selected_type != _('ventilation') and (length < limits['length'][0] or length > limits['length'][1]):
                    QMessageBox.warning(
                        self, 
                        _('invalid_dimensions'), 
                        _('dimension_range_error').format(
                            dimension=_('length'),
                            min=limits['length'][0],
                            max=limits['length'][1]
                        )
                    )
                    return
                
                if height < limits['height'][0] or height > limits['height'][1]:
                    QMessageBox.warning(
                        self, 
                        _('invalid_dimensions'), 
                        _('dimension_range_error').format(
                            dimension=_('height'),
                            min=limits['height'][0],
                            max=limits['height'][1]
                        )
                    )
                    return
                
                # For ventilation, enforce same width and length (diameter)
                if self.selected_type == _('ventilation'):
                    length = width
                
                # Store validated dimensions
                self.dimensions = (width, length, height)
                self.accept()
                
            except ValueError:
                QMessageBox.warning(
                    self, 
                    _('invalid_input'), 
                    _('enter_valid_numbers')
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
