from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                           QDialogButtonBox, QMessageBox, QGroupBox, 
                           QRadioButton, QComboBox, QLabel, QCheckBox, QApplication,
                           QPushButton, QStyledItemDelegate)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont
from translations import _

def show_solar_panel_dialog(parent=None, is_flat_roof=False):
    # Define maximum dimension constants at the beginning
    MAX_LENGTH = 2500  # mm, maximum realistic panel length
    MAX_WIDTH = 1500   # mm, maximum realistic panel width
    MAX_POWER = 800    # W, maximum realistic panel power

    dialog = QDialog(parent)
    dialog.setWindowTitle(_("solar_panel_settings"))
    dialog.setMinimumWidth(450)  # Slightly wider for category labels
    
    # Create layout
    layout = QVBoxLayout(dialog)
    
    # Create group for panel selection
    selection_group = QGroupBox(_("panel_selection"))
    selection_layout = QVBoxLayout(selection_group)
    
    # Radio buttons for selection mode
    predefined_radio = QRadioButton(_("predefined_panel"))
    custom_radio = QRadioButton(_("custom_panel"))
    predefined_radio.setChecked(True)
    
    selection_layout.addWidget(predefined_radio)
    
    # Panel model dropdown
    panel_form = QFormLayout()
    panel_combo = QComboBox()
    
    # Create a custom model to support category headers
    panel_model = QStandardItemModel()
    panel_combo.setModel(panel_model)
    
    # Custom delegate to make category headers non-selectable and styled differently
    class CategoryDelegate(QStyledItemDelegate):
        def paint(self, painter, option, index):
            is_category = index.data(Qt.UserRole)
            if is_category:
                option.font.setBold(True)
                # Removed blue outline by omitting palette color setting
            super().paint(painter, option, index)

    panel_combo.setItemDelegate(CategoryDelegate())
    
    # Function to add a category header
    def add_category(name):
        item = QStandardItem(name)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        item.setData(True, Qt.UserRole)  # Mark as category
        bold_font = QFont()
        bold_font.setBold(True)
        item.setFont(bold_font)
        item.setBackground(Qt.lightGray)
        panel_model.appendRow(item)
    
    # Function to add a panel item - explicitly setting normal non-bold font
    def add_panel(name, index):
        item = QStandardItem(name)
        item.setData(index, Qt.UserRole + 1)  # Store panel index
        # Explicitly set normal font to ensure non-bold text
        normal_font = QFont()
        normal_font.setBold(False)  
        item.setFont(normal_font)
        panel_model.appendRow(item)
        return index + 1
    
    # Add panels organized by categories
    panel_index = 0
    
    # PREMIUM PANELS
    add_category(_("premium_panels"))
    panel_index = add_panel("SunPower - Maxeon 6 AC (1835×1017 mm, 440W)", panel_index)
    panel_index = add_panel("LG - NeON R (1700×1016 mm, 380W)", panel_index)
    panel_index = add_panel("Panasonic - EverVolt (1765×1048 mm, 370W)", panel_index)
    panel_index = add_panel("REC - Alpha Pure (1721×1016 mm, 405W)", panel_index)
    panel_index = add_panel("REC - Alpha Pure-R (1730×1118 mm, 430W)", panel_index)
    panel_index = add_panel("SunPower - Maxeon 6 (2066×1160 mm, 535W)", panel_index)
    panel_index = add_panel("Meyer Burger - White (1767×1041 mm, 390W)", panel_index)
    panel_index = add_panel("Winaico - WSP-MX PERC (1739×1048 mm, 385W)", panel_index)
    
    # HIGH-EFFICIENCY PANELS
    add_category(_("high_efficiency_panels"))
    panel_index = add_panel("Jinko Solar - Tiger Neo (1722×1134 mm, 455W)", panel_index)
    panel_index = add_panel("Trina Solar - Vertex S (1762×1046 mm, 410W)", panel_index)
    panel_index = add_panel("Q CELLS - Q.PEAK DUO ML-G10+ (1879×1045 mm, 400W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 5 (2094×1038 mm, 455W)", panel_index)
    panel_index = add_panel("Silfab - SIL-380 (1765×1040 mm, 380W)", panel_index)
    panel_index = add_panel("Hyundai - HiE-S400VG (1719×1016 mm, 400W)", panel_index)
    panel_index = add_panel("Mission Solar - MSE370SQ10T (1731×1048 mm, 370W)", panel_index)
    panel_index = add_panel("Suntech - Ultra V (1722×1134 mm, 455W)", panel_index)
    panel_index = add_panel("QCELLS - Q.ANTUM DUO Z (1840×1030 mm, 380W)", panel_index)
    
    # ECONOMY PANELS
    add_category(_("economy_panels"))
    panel_index = add_panel("Risen Energy - RSM40-8 (1690×996 mm, 335W)", panel_index)
    panel_index = add_panel("JA Solar - JAM60S10 (1689×996 mm, 340W)", panel_index)
    panel_index = add_panel("Axitec - AC-320MH (1675×997 mm, 320W)", panel_index)
    panel_index = add_panel("Vikram Solar - Somera (1692×1002 mm, 345W)", panel_index)
    panel_index = add_panel("Talesun - TP672M (1708×1002 mm, 350W)", panel_index)
    panel_index = add_panel("Znshine - ZXM6-HLD72 (1689×996 mm, 325W)", panel_index)
    panel_index = add_panel("GCL - M6/72H (1696×1005 mm, 335W)", panel_index)
    panel_index = add_panel("Seraphim - SRP-340-BMA (1684×1002 mm, 340W)", panel_index)
    
    # COMPACT PANELS
    add_category(_("compact_panels"))
    panel_index = add_panel("First Solar - Series 6 (1200×1200 mm, 420W)", panel_index)
    panel_index = add_panel("Solaria - PowerXT (1621×959 mm, 360W)", panel_index)
    panel_index = add_panel("Solarwatt - Vision 60M (1680×1001 mm, 360W)", panel_index)
    panel_index = add_panel("SunPower - A-Series AC (1690×1046 mm, 390W)", panel_index)
    panel_index = add_panel("REC - N-Peak 2 (1730×1041 mm, 365W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 4m (1722×1031 mm, 375W)", panel_index)
    
    # COMMERCIAL/LARGE FORMAT PANELS
    add_category(_("commercial_panels"))
    panel_index = add_panel("Canadian Solar - HiKu6 (2108×1048 mm, 490W)", panel_index)
    panel_index = add_panel("JinkoSolar - Eagle 78TR (2465×1134 mm, 635W)", panel_index)
    panel_index = add_panel("Trina Solar - Vertex S+ (2384×1096 mm, 585W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 6 (2382×1134 mm, 595W)", panel_index)
    panel_index = add_panel("JA Solar - DeepBlue 3.0 (2285×1134 mm, 605W)", panel_index)
    panel_index = add_panel("Canadian Solar - BiHiKu7 (2278×1134 mm, 620W)", panel_index)
    panel_index = add_panel("Jinko - Tiger Pro 72HC (2274×1134 mm, 590W)", panel_index)
    
    # SPECIALIZED TECHNOLOGY PANELS
    add_category(_("specialized_technology_panels"))
    panel_index = add_panel("Phono Solar - TwinPlus (1722×1133 mm, 455W)", panel_index)
    panel_index = add_panel("Waaree - Bifacial (2094×1038 mm, 440W)", panel_index)
    panel_index = add_panel("Aptos Solar - DNA-120 (1754×1098 mm, 390W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 5m Bifacial (1895×1096 mm, 460W)", panel_index)
    panel_index = add_panel("JA Solar - JAB60S10 Bifacial (1726×1024 mm, 370W)", panel_index)
    panel_index = add_panel("First Solar - Series 6 CuRe (1202×1200 mm, 445W)", panel_index)
    panel_index = add_panel("Jolywood - Niwa (1724×1035 mm, 380W)", panel_index)
    panel_index = add_panel("Trina - Vertex S+ All-Black (1762×1134 mm, 425W)", panel_index)
    
    panel_form.addRow(_("panel_model"), panel_combo)
    selection_layout.addLayout(panel_form)
    
    # Show panel specs
    specs_label = QLabel(f"{_('length_a')}: 1835 mm, {_('width_a')}: 1017 mm, {_('power')}: 440W")
    selection_layout.addWidget(specs_label)
    
    # Add custom panel option
    selection_layout.addWidget(custom_radio)
    
    # Add a note about maximum dimensions for custom panels
    max_dimensions_note = QLabel(f"{_('max_dimensions')}: {MAX_LENGTH}×{MAX_WIDTH} mm, {_('max_power')}: {MAX_POWER}W")
    max_dimensions_note.setStyleSheet("color: gray; font-size: 10px; margin-left: 20px;")
    max_dimensions_note.setWordWrap(True)
    selection_layout.addWidget(max_dimensions_note)
    
    selection_group.setLayout(selection_layout)
    layout.addWidget(selection_group)
    
    # Create group for basic panel dimensions
    panel_group = QGroupBox(_("panel_dimensions"))
    form_layout = QFormLayout(panel_group)
    
    # Panel length input (in mm)
    length_input = QLineEdit("1835")
    form_layout.addRow(_("panel_length") + " (mm)", length_input)
    
    # Panel width input (in mm)
    width_input = QLineEdit("1017")
    form_layout.addRow(_("panel_width") + " (mm)", width_input)
    
    # Panel power input (in W)
    power_input = QLineEdit("440")
    form_layout.addRow(_("panel_power") + " (W)", power_input)
    
    # Panel gap input (in mm)
    gap_input = QLineEdit("50")
    form_layout.addRow(_("panel_gap") + " (mm)", gap_input)
    
    # ADD INVERT DIMENSIONS CHECKBOX
    invert_checkbox = QCheckBox(_("invert_dimensions"))
    form_layout.addRow("", invert_checkbox)
    
    # Add an explanation label for the invert option
    invert_explanation = QLabel(_("dimensions_explanation"))
    invert_explanation.setWordWrap(True)
    form_layout.addRow("", invert_explanation)
    
    # Show effective dimensions after inversion
    effective_dimensions_label = QLabel()
    effective_dimensions_label.setStyleSheet("color: red;")
    form_layout.addRow(_("effective_dimensions"), effective_dimensions_label)
    
    panel_group.setLayout(form_layout)
    layout.addWidget(panel_group)
    
    # Add separate flat roof mounting options
    tilt_input = None
    orientation_combo = None
    
    if is_flat_roof:
        # Create separate group for mounting options
        mounting_group = QGroupBox(_("mounting_options"))
        mounting_layout = QFormLayout(mounting_group)
        
        # Panel tilt input (only for flat roofs)
        tilt_input = QLineEdit("15.0")
        mounting_layout.addRow(_("panel_tilt") + " (°)", tilt_input)
        
        # Replace numeric orientation input with direction dropdown
        orientation_combo = QComboBox()
        
        # Define directions with their corresponding angles
        # Define directions with their corresponding angles
        directions = [
            ('North', 0),
            #('Northeast', 45),
            ('East', 90), 
            #('Southwest', 135),  
            ('South', 180),
            #('Southeast', 225), 
            ('West', 270),  
            #('Northwest', 315)
    ]
        
        # Add directions to the dropdown using just the translated name
        for direction, angle in directions:
            # Only show translated direction name with angle
            display_text = f"{_(direction)} ({angle}°)"
            orientation_combo.addItem(display_text, angle)
        
        # Default to South as it's typically optimal for northern hemisphere
        south_index = [d[0] for d in directions].index('South')
        orientation_combo.setCurrentIndex(south_index)
        
        mounting_layout.addRow(_("panel_orientation"), orientation_combo)
        
        mounting_group.setLayout(mounting_layout)
        layout.addWidget(mounting_group)
    
    # Panel dimensions dictionary (now in millimeters with power)
    panel_dimensions = {
        # PREMIUM PANELS
        0: {"length": 1835, "width": 1017, "power": 440},  # SunPower Maxeon 6 AC
        1: {"length": 1700, "width": 1016, "power": 380},  # LG NeON R
        2: {"length": 1765, "width": 1048, "power": 370},  # Panasonic EverVolt
        3: {"length": 1721, "width": 1016, "power": 405},  # REC Alpha Pure
        4: {"length": 1730, "width": 1118, "power": 430},  # REC Alpha Pure-R
        5: {"length": 2066, "width": 1160, "power": 535},  # SunPower Maxeon 6
        6: {"length": 1767, "width": 1041, "power": 390},  # Meyer Burger White
        7: {"length": 1739, "width": 1048, "power": 385},  # Winaico WSP-MX PERC
        
        # HIGH-EFFICIENCY PANELS
        8: {"length": 1722, "width": 1134, "power": 455},  # Jinko Tiger Neo
        9: {"length": 1762, "width": 1046, "power": 410},  # Trina Vertex S
        10: {"length": 1879, "width": 1045, "power": 400}, # Q CELLS Q.PEAK DUO
        11: {"length": 2094, "width": 1038, "power": 455}, # LONGi Hi-MO 5
        12: {"length": 1765, "width": 1040, "power": 380}, # Silfab SIL-380
        13: {"length": 1719, "width": 1016, "power": 400}, # Hyundai HiE-S400VG
        14: {"length": 1731, "width": 1048, "power": 370}, # Mission Solar MSE370SQ10T
        15: {"length": 1722, "width": 1134, "power": 455}, # Suntech Ultra V
        16: {"length": 1840, "width": 1030, "power": 380}, # QCELLS Q.ANTUM DUO Z
        
        # ECONOMY PANELS
        17: {"length": 1690, "width": 996, "power": 335},  # Risen Energy RSM40-8
        18: {"length": 1689, "width": 996, "power": 340},  # JA Solar JAM60S10
        19: {"length": 1675, "width": 997, "power": 320},  # Axitec AC-320MH
        20: {"length": 1692, "width": 1002, "power": 345}, # Vikram Solar Somera
        21: {"length": 1708, "width": 1002, "power": 350}, # Talesun TP672M
        22: {"length": 1689, "width": 996, "power": 325},  # Znshine ZXM6-HLD72
        23: {"length": 1696, "width": 1005, "power": 335}, # GCL M6/72H
        24: {"length": 1684, "width": 1002, "power": 340}, # Seraphim SRP-340-BMA
        
        # COMPACT PANELS
        25: {"length": 1200, "width": 1200, "power": 420}, # First Solar Series 6
        26: {"length": 1621, "width": 959, "power": 360},  # Solaria PowerXT
        27: {"length": 1680, "width": 1001, "power": 360}, # Solarwatt Vision 60M
        28: {"length": 1690, "width": 1046, "power": 390}, # SunPower A-Series AC
        29: {"length": 1730, "width": 1041, "power": 365}, # REC N-Peak 2
        30: {"length": 1722, "width": 1031, "power": 375}, # LONGi Hi-MO 4m
        
        # COMMERCIAL/LARGE FORMAT PANELS
        31: {"length": 2108, "width": 1048, "power": 490}, # Canadian Solar HiKu6
        32: {"length": 2465, "width": 1134, "power": 635}, # JinkoSolar Eagle 78TR
        33: {"length": 2384, "width": 1096, "power": 585}, # Trina Vertex S+
        34: {"length": 2382, "width": 1134, "power": 595}, # LONGi Hi-MO 6
        35: {"length": 2285, "width": 1134, "power": 605}, # JA Solar DeepBlue 3.0
        36: {"length": 2278, "width": 1134, "power": 620}, # Canadian Solar BiHiKu7
        37: {"length": 2274, "width": 1134, "power": 590}, # Jinko Tiger Pro 72HC
        
        # SPECIALIZED TECHNOLOGY PANELS
        38: {"length": 1722, "width": 1133, "power": 455}, # Phono Solar TwinPlus
        39: {"length": 2094, "width": 1038, "power": 440}, # Waaree Bifacial
        40: {"length": 1754, "width": 1098, "power": 390}, # Aptos Solar DNA-120
        41: {"length": 1895, "width": 1096, "power": 460}, # LONGi Hi-MO 5m Bifacial
        42: {"length": 1726, "width": 1024, "power": 370}, # JA Solar JAB60S10 Bifacial
        43: {"length": 1202, "width": 1200, "power": 445}, # First Solar Series 6 CuRe
        44: {"length": 1724, "width": 1035, "power": 380}, # Jolywood Niwa
        45: {"length": 1762, "width": 1134, "power": 425}, # Trina Vertex S+ All-Black
    }
    
    # Connect signals
    def update_dimensions(index):
        # Skip category headers (which are not selectable anyway)
        if panel_combo.itemData(index, Qt.UserRole):
            return
        
        # Get real panel index from the model
        model_index = panel_model.index(index, 0)
        panel_index = model_index.data(Qt.UserRole + 1)
        
        if predefined_radio.isChecked() and panel_index is not None:
            panel = panel_dimensions[panel_index]
            length_input.setText(str(panel["length"]))
            width_input.setText(str(panel["width"]))
            power_input.setText(str(panel["power"]))
            specs_label.setText(f"{_('length_a')}: {panel['length']} mm, {_('width_a')}: {panel['width']} mm, {_('power')}: {panel['power']}W")
            update_effective_dimensions()
    
    def toggle_custom():
        is_predefined = predefined_radio.isChecked()
        
        # Enable/disable dropdown and specs based on selection
        panel_combo.setEnabled(is_predefined)
        specs_label.setEnabled(is_predefined)
        
        # Make dimension fields read-only and gray when predefined is selected
        length_input.setReadOnly(is_predefined)
        width_input.setReadOnly(is_predefined)
        power_input.setReadOnly(is_predefined)
        
        # Get the current theme-appropriate background color
        # First try to get from parent window
        current_theme = "light"  # Default to light theme
        
        # Try different ways to access the theme
        if hasattr(dialog, 'parent') and dialog.parent():
            parent = dialog.parent()
            if hasattr(parent, 'theme'):
                current_theme = parent.theme
        
        # If not found, try application settings
        if current_theme == "light" and QApplication.instance():
            from PyQt5.QtCore import QSettings
            settings = QSettings("YourCompany", "AppName")
            if settings.contains("theme"):
                current_theme = settings.value("theme", "light")
        
        # Set theme-appropriate colors
        if current_theme == "dark":
            disabled_bg = "#3d3d3d"  # Dark gray for dark theme
            disabled_text = "#e0e0e0"  # Light text color for readability
        else:
            disabled_bg = "#f0f0f0"  # Light gray for light theme
            disabled_text = "#000000"  # Dark text for light theme
        
        # Change appearance based on selection
        if is_predefined:
            # Gray out the input fields with theme-appropriate colors
            disabled_style = f"background-color: {disabled_bg}; color: {disabled_text};"
            length_input.setStyleSheet(disabled_style)
            width_input.setStyleSheet(disabled_style)
            power_input.setStyleSheet(disabled_style)
            
            # Get the model index for the current panel
            index = panel_combo.currentIndex()
            model_index = panel_model.index(index, 0)
            panel_index = model_index.data(Qt.UserRole + 1)
            
            if panel_index is not None:
                current_panel = panel_dimensions[panel_index]
                specs_label.setText(f"{_('length_a')}: {current_panel['length']} mm, {_('width_a')}: {current_panel['width']} mm, {_('power')}: {current_panel['power']}W")

        else:
            # Restore normal appearance
            length_input.setStyleSheet("")
            width_input.setStyleSheet("")
            power_input.setStyleSheet("")
            specs_label.setText(_("enter_custom_dimensions"))
        
        # Update effective dimensions
        update_effective_dimensions()
    
    def toggle_invert():
        # Update effective dimensions label
        update_effective_dimensions()
    
    def update_effective_dimensions():
        try:
            current_length = float(length_input.text())
            current_width = float(width_input.text())
            
            if invert_checkbox.isChecked():
                effective_dimensions_label.setText(
                    f"{current_width} × {current_length} mm ({_('inverted')})")
            else:
                effective_dimensions_label.setText(
                    f"{current_length} × {current_width} mm")
        except ValueError:
            effective_dimensions_label.setText(_("invalid_dimensions"))
    
    panel_combo.currentIndexChanged.connect(update_dimensions)
    predefined_radio.toggled.connect(toggle_custom)
    custom_radio.toggled.connect(toggle_custom)
    invert_checkbox.toggled.connect(toggle_invert)
    length_input.textChanged.connect(update_effective_dimensions)
    width_input.textChanged.connect(update_effective_dimensions)
    
    # Select first non-category item
    for i in range(panel_model.rowCount()):
        if not panel_model.item(i).data(Qt.UserRole):
            panel_combo.setCurrentIndex(i)
            break
    
    # Initial update
    toggle_custom()
    update_effective_dimensions()
    
    # Create custom buttons with larger size and red cancel button
    button_box = QDialogButtonBox()

    # Create and style OK button
    ok_button = QPushButton(_("OK"))
    ok_button.setMinimumHeight(40)
    ok_button.setMinimumWidth(120)
    ok_button.setStyleSheet("font-weight: bold; font-size: 12px;")

    # Create and style Cancel button (red)
    cancel_button = QPushButton(_("cancel"))
    cancel_button.setMinimumHeight(40)
    cancel_button.setMinimumWidth(120)
    cancel_button.setStyleSheet("background-color: #d9534f; color: white; font-size: 12px;")

    # Add buttons to the button box
    button_box.addButton(ok_button, QDialogButtonBox.AcceptRole)
    button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)

    layout.addWidget(button_box)
    
    # Connect buttons to actions
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    
    # Execute dialog
    if dialog.exec_() == QDialog.Accepted:
        try:
            # Get basic values (now in mm)
            panel_length = float(length_input.text())
            panel_width = float(width_input.text())
            panel_power = float(power_input.text())
            panel_gap = float(gap_input.text())
            
            # Validate positive values
            if panel_length <= 0 or panel_width <= 0 or panel_gap < 0 or panel_power <= 0:
                QMessageBox.warning(parent, _("invalid_input"), 
                                   _("positive_values_required"))
                return None
            
            # Add maximum dimension validation
            if panel_length > MAX_LENGTH or panel_width > MAX_WIDTH:
                QMessageBox.warning(parent, _("invalid_dimensions"), 
                                  _("panel_dimensions_too_large") + 
                                  f" (Max: {MAX_LENGTH}×{MAX_WIDTH} mm)")
                return None

            if panel_power > MAX_POWER:
                QMessageBox.warning(parent, _("invalid_input"), 
                                  _("panel_power_too_high") + f" (Max: {MAX_POWER}W)")
                return None
            
            # Check if dimensions should be inverted and swap if needed
            if invert_checkbox.isChecked():
                # Swap length and width directly in the config
                panel_length, panel_width = panel_width, panel_length
            
            # Get panel model name
            panel_model_name = "Custom"
            if predefined_radio.isChecked():
                index = panel_combo.currentIndex()
                if not panel_combo.itemData(index, Qt.UserRole):  # Not a category
                    panel_model_name = panel_combo.currentText()
            
            # Create config dictionary (all values in mm)
            config = {
                'panel_length': panel_length,
                'panel_width': panel_width,
                'panel_gap': panel_gap,
                'panel_power': panel_power,
                'panel_model': panel_model_name,
                'dimensions_inverted': invert_checkbox.isChecked()  # Keep this flag for informational purposes
            }
            
            # Add flat roof specific values if available
            if is_flat_roof and tilt_input and orientation_combo:
                panel_tilt = float(tilt_input.text())
                
                # Get orientation angle from combo box's userData
                panel_orientation = orientation_combo.currentData()
                
                # Get the original English direction name for this index
                direction_name = directions[orientation_combo.currentIndex()][0]
                
                # Validate tilt angle
                if panel_tilt < 0 or panel_tilt > 45:
                    QMessageBox.warning(parent, _("invalid_input"),
                                      _("tilt_angle_range"))
                    return None
                
                # Add to config
                config['panel_tilt'] = panel_tilt
                config['panel_orientation'] = panel_orientation
                config['orientation_direction'] = direction_name
            
            return config
            
        except ValueError:
            QMessageBox.warning(parent, _("invalid_input"),
                              _("numeric_values_required"))
            return None
    else:
        return None