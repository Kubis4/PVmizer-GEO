from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                           QDialogButtonBox, QMessageBox, QGroupBox, 
                           QRadioButton, QComboBox, QLabel, QCheckBox,
                           QPushButton, QStyledItemDelegate)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont

# Import the dialog styles
try:
    from ui.styles.dialog_styles import DialogStyles
    DIALOG_STYLES_AVAILABLE = True
except ImportError:
    DIALOG_STYLES_AVAILABLE = False

def show_solar_panel_dialog(parent=None, is_flat_roof=False):
    # Define maximum dimension constants
    MAX_LENGTH = 2500  # mm, maximum realistic panel length
    MAX_WIDTH = 1500   # mm, maximum realistic panel width
    MAX_POWER = 800    # W, maximum realistic panel power

    dialog = QDialog(parent)
    dialog.setWindowTitle("Solar Panel Settings")
    dialog.setMinimumWidth(500)
    dialog.setMinimumHeight(600)
    
    # Apply dialog styling
    if DIALOG_STYLES_AVAILABLE:
        dialog.setStyleSheet(DialogStyles.get_dark_dialog_style())
    
    # Create layout with consistent spacing and margins
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)

    # Title
    title = DialogStyles.create_styled_label("Solar Panel Configuration", "title") if DIALOG_STYLES_AVAILABLE else QLabel("Solar Panel Configuration")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    # Description
    description = DialogStyles.create_styled_label("Configure your solar panel specifications and mounting options.", "description") if DIALOG_STYLES_AVAILABLE else QLabel("Configure your solar panel specifications and mounting options.")
    description.setWordWrap(True)
    description.setAlignment(Qt.AlignCenter)
    layout.addWidget(description)
    
    # Create group for panel selection
    selection_group = QGroupBox("🔋 Panel Selection")
    selection_layout = QVBoxLayout(selection_group)
    
    # Radio buttons for selection mode
    predefined_radio = QRadioButton("Use Predefined Panel")
    custom_radio = QRadioButton("Custom Panel Dimensions")
    predefined_radio.setChecked(True)
    
    selection_layout.addWidget(predefined_radio)
    
    # Panel model dropdown
    panel_form = QFormLayout()
    panel_combo = QComboBox()
    
    # Create a custom model to support category headers
    panel_model = QStandardItemModel()
    panel_combo.setModel(panel_model)
    
    # Custom delegate for better category styling
    class CategoryDelegate(QStyledItemDelegate):
        def paint(self, painter, option, index):
            is_category = index.data(Qt.UserRole)
            if is_category:
                option.font.setBold(True)
                # Set category background color
                option.palette.setColor(option.palette.Highlight, Qt.darkBlue)
                option.palette.setColor(option.palette.HighlightedText, Qt.white)
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
        # Set category styling
        item.setBackground(Qt.darkGray)
        item.setForeground(Qt.white)
        panel_model.appendRow(item)
    
    # Function to add a panel item
    def add_panel(name, index):
        item = QStandardItem(name)
        item.setData(index, Qt.UserRole + 1)  # Store panel index
        normal_font = QFont()
        normal_font.setBold(False)  
        item.setFont(normal_font)
        panel_model.appendRow(item)
        return index + 1
    
    # Add panels organized by categories
    panel_index = 0
    
    # PREMIUM PANELS
    add_category("Premium Panels")
    panel_index = add_panel("SunPower - Maxeon 6 AC (1835×1017 mm, 440W)", panel_index)
    panel_index = add_panel("LG - NeON R (1700×1016 mm, 380W)", panel_index)
    panel_index = add_panel("Panasonic - EverVolt (1765×1048 mm, 370W)", panel_index)
    panel_index = add_panel("REC - Alpha Pure (1721×1016 mm, 405W)", panel_index)
    panel_index = add_panel("REC - Alpha Pure-R (1730×1118 mm, 430W)", panel_index)
    panel_index = add_panel("SunPower - Maxeon 6 (2066×1160 mm, 535W)", panel_index)
    panel_index = add_panel("Meyer Burger - White (1767×1041 mm, 390W)", panel_index)
    panel_index = add_panel("Winaico - WSP-MX PERC (1739×1048 mm, 385W)", panel_index)
    
    # HIGH-EFFICIENCY PANELS
    add_category("High-Efficiency Panels")
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
    add_category("Economy Panels")
    panel_index = add_panel("Risen Energy - RSM40-8 (1690×996 mm, 335W)", panel_index)
    panel_index = add_panel("JA Solar - JAM60S10 (1689×996 mm, 340W)", panel_index)
    panel_index = add_panel("Axitec - AC-320MH (1675×997 mm, 320W)", panel_index)
    panel_index = add_panel("Vikram Solar - Somera (1692×1002 mm, 345W)", panel_index)
    panel_index = add_panel("Talesun - TP672M (1708×1002 mm, 350W)", panel_index)
    panel_index = add_panel("Znshine - ZXM6-HLD72 (1689×996 mm, 325W)", panel_index)
    panel_index = add_panel("GCL - M6/72H (1696×1005 mm, 335W)", panel_index)
    panel_index = add_panel("Seraphim - SRP-340-BMA (1684×1002 mm, 340W)", panel_index)
    
    # COMPACT PANELS
    add_category("Compact Panels")
    panel_index = add_panel("First Solar - Series 6 (1200×1200 mm, 420W)", panel_index)
    panel_index = add_panel("Solaria - PowerXT (1621×959 mm, 360W)", panel_index)
    panel_index = add_panel("Solarwatt - Vision 60M (1680×1001 mm, 360W)", panel_index)
    panel_index = add_panel("SunPower - A-Series AC (1690×1046 mm, 390W)", panel_index)
    panel_index = add_panel("REC - N-Peak 2 (1730×1041 mm, 365W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 4m (1722×1031 mm, 375W)", panel_index)
    
    # COMMERCIAL/LARGE FORMAT PANELS
    add_category("Commercial Panels")
    panel_index = add_panel("Canadian Solar - HiKu6 (2108×1048 mm, 490W)", panel_index)
    panel_index = add_panel("JinkoSolar - Eagle 78TR (2465×1134 mm, 635W)", panel_index)
    panel_index = add_panel("Trina Solar - Vertex S+ (2384×1096 mm, 585W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 6 (2382×1134 mm, 595W)", panel_index)
    panel_index = add_panel("JA Solar - DeepBlue 3.0 (2285×1134 mm, 605W)", panel_index)
    panel_index = add_panel("Canadian Solar - BiHiKu7 (2278×1134 mm, 620W)", panel_index)
    panel_index = add_panel("Jinko - Tiger Pro 72HC (2274×1134 mm, 590W)", panel_index)
    
    # SPECIALIZED TECHNOLOGY PANELS
    add_category("Specialized Technology Panels")
    panel_index = add_panel("Phono Solar - TwinPlus (1722×1133 mm, 455W)", panel_index)
    panel_index = add_panel("Waaree - Bifacial (2094×1038 mm, 440W)", panel_index)
    panel_index = add_panel("Aptos Solar - DNA-120 (1754×1098 mm, 390W)", panel_index)
    panel_index = add_panel("LONGi - Hi-MO 5m Bifacial (1895×1096 mm, 460W)", panel_index)
    panel_index = add_panel("JA Solar - JAB60S10 Bifacial (1726×1024 mm, 370W)", panel_index)
    panel_index = add_panel("First Solar - Series 6 CuRe (1202×1200 mm, 445W)", panel_index)
    panel_index = add_panel("Jolywood - Niwa (1724×1035 mm, 380W)", panel_index)
    panel_index = add_panel("Trina - Vertex S+ All-Black (1762×1134 mm, 425W)", panel_index)
    
    form_label = DialogStyles.create_styled_label("Panel Model:", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Model:")
    panel_form.addRow(form_label, panel_combo)
    selection_layout.addLayout(panel_form)
    
    # Show panel specs
    specs_label = QLabel("Length: 1835 mm, Width: 1017 mm, Power: 440W")
    selection_layout.addWidget(specs_label)
    
    # Add custom panel option
    selection_layout.addWidget(custom_radio)
    
    # Add a note about maximum dimensions for custom panels
    max_dimensions_note = QLabel(f"Maximum dimensions: {MAX_LENGTH}×{MAX_WIDTH} mm, Maximum power: {MAX_POWER}W")
    max_dimensions_note.setWordWrap(True)
    selection_layout.addWidget(max_dimensions_note)
    
    selection_group.setLayout(selection_layout)
    layout.addWidget(selection_group)
    
    # Create group for basic panel dimensions
    panel_group = QGroupBox("📐 Panel Dimensions")
    form_layout = QFormLayout(panel_group)
    form_layout.setContentsMargins(15, 15, 15, 15)
    form_layout.setSpacing(12)
    
    # Panel length input (in mm)
    length_input = QLineEdit("1835")
    length_input.setPlaceholderText("Enter length in mm (e.g., 1835)")
    length_label = DialogStyles.create_styled_label("Panel Length (mm):", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Length (mm):")
    form_layout.addRow(length_label, length_input)
    
    # Panel width input (in mm)
    width_input = QLineEdit("1017")
    width_input.setPlaceholderText("Enter width in mm (e.g., 1017)")
    width_label = DialogStyles.create_styled_label("Panel Width (mm):", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Width (mm):")
    form_layout.addRow(width_label, width_input)
    
    # Panel power input (in W)
    power_input = QLineEdit("440")
    power_input.setPlaceholderText("Enter power in watts (e.g., 440)")
    power_label = DialogStyles.create_styled_label("Panel Power (W):", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Power (W):")
    form_layout.addRow(power_label, power_input)
    
    # Panel gap input (in mm)
    gap_input = QLineEdit("50")
    gap_input.setPlaceholderText("Enter gap in mm (e.g., 50)")
    gap_label = DialogStyles.create_styled_label("Panel Gap (mm):", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Gap (mm):")
    form_layout.addRow(gap_label, gap_input)
    
    # Invert dimensions checkbox
    invert_checkbox = QCheckBox("Invert Dimensions (Rotate 90°)")
    form_layout.addRow("", invert_checkbox)
    
    # Add an explanation label for the invert option
    invert_explanation = QLabel("Check this to swap length and width values for different panel orientation.")
    invert_explanation.setWordWrap(True)
    form_layout.addRow("", invert_explanation)
    
    # Show effective dimensions after inversion
    effective_dimensions_label = QLabel()
    effective_label = DialogStyles.create_styled_label("Effective Dimensions:", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Effective Dimensions:")
    form_layout.addRow(effective_label, effective_dimensions_label)
    
    panel_group.setLayout(form_layout)
    layout.addWidget(panel_group)
    
    # Add separate flat roof mounting options
    tilt_input = None
    orientation_combo = None
    
    if is_flat_roof:
        # Create separate group for mounting options
        mounting_group = QGroupBox("🔧 Mounting Options")
        mounting_layout = QFormLayout(mounting_group)
        mounting_layout.setContentsMargins(15, 15, 15, 15)
        mounting_layout.setSpacing(12)
        
        # Panel tilt input (only for flat roofs)
        tilt_input = QLineEdit("15.0")
        tilt_input.setPlaceholderText("Enter tilt angle in degrees (0-45)")
        tilt_label = DialogStyles.create_styled_label("Panel Tilt (°):", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Tilt (°):")
        mounting_layout.addRow(tilt_label, tilt_input)
        
        # Orientation dropdown
        orientation_combo = QComboBox()
        
        # Define directions with their corresponding angles
        directions = [
            ('North', 0),
            ('East', 90), 
            ('South', 180),
            ('West', 270),  
        ]
        
        # Add directions to the dropdown
        for direction, angle in directions:
            display_text = f"{direction} ({angle}°)"
            orientation_combo.addItem(display_text, angle)
        
        # Default to South as it's typically optimal for northern hemisphere
        south_index = [d[0] for d in directions].index('South')
        orientation_combo.setCurrentIndex(south_index)
        
        orientation_label = DialogStyles.create_styled_label("Panel Orientation:", "form") if DIALOG_STYLES_AVAILABLE else QLabel("Panel Orientation:")
        mounting_layout.addRow(orientation_label, orientation_combo)
        
        mounting_group.setLayout(mounting_layout)
        layout.addWidget(mounting_group)
    
    # Panel dimensions dictionary (in millimeters with power)
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
    
    # Connect signals (same as before)
    def update_dimensions(index):
        if panel_combo.itemData(index, Qt.UserRole):
            return
        
        model_index = panel_model.index(index, 0)
        panel_index = model_index.data(Qt.UserRole + 1)
        
        if predefined_radio.isChecked() and panel_index is not None:
            panel = panel_dimensions[panel_index]
            length_input.setText(str(panel["length"]))
            width_input.setText(str(panel["width"]))
            power_input.setText(str(panel["power"]))
            specs_label.setText(f"Length: {panel['length']} mm, Width: {panel['width']} mm, Power: {panel['power']}W")
            update_effective_dimensions()
    
    def toggle_custom():
        is_predefined = predefined_radio.isChecked()
        
        panel_combo.setEnabled(is_predefined)
        specs_label.setEnabled(is_predefined)
        
        length_input.setReadOnly(is_predefined)
        width_input.setReadOnly(is_predefined)
        power_input.setReadOnly(is_predefined)
        
        if is_predefined:
            index = panel_combo.currentIndex()
            model_index = panel_model.index(index, 0)
            panel_index = model_index.data(Qt.UserRole + 1)
            
            if panel_index is not None:
                current_panel = panel_dimensions[panel_index]
                specs_label.setText(f"Length: {current_panel['length']} mm, Width: {current_panel['width']} mm, Power: {current_panel['power']}W")
        else:
            specs_label.setText("Enter custom dimensions below")
        
        update_effective_dimensions()
    
    def update_effective_dimensions():
        try:
            current_length = float(length_input.text())
            current_width = float(width_input.text())
            
            if invert_checkbox.isChecked():
                effective_dimensions_label.setText(f"{current_width} × {current_length} mm (Inverted)")
            else:
                effective_dimensions_label.setText(f"{current_length} × {current_width} mm")
        except ValueError:
            effective_dimensions_label.setText("Invalid dimensions")
    
    # Connect signals
    panel_combo.currentIndexChanged.connect(update_dimensions)
    predefined_radio.toggled.connect(toggle_custom)
    custom_radio.toggled.connect(toggle_custom)
    invert_checkbox.toggled.connect(update_effective_dimensions)
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
    
    # Buttons with styling
    button_box = QDialogButtonBox()
    ok_button = QPushButton("Create Solar Configuration")
    cancel_button = QPushButton("Cancel")
    cancel_button.setObjectName("cancel_button")

    button_box.addButton(ok_button, QDialogButtonBox.AcceptRole)
    button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)

    layout.addWidget(button_box)
    
    # Connect buttons to actions
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    
    # Execute dialog (same validation logic as before)
    if dialog.exec_() == QDialog.Accepted:
        try:
            panel_length = float(length_input.text())
            panel_width = float(width_input.text())
            panel_power = float(power_input.text())
            panel_gap = float(gap_input.text())
            
            if panel_length <= 0 or panel_width <= 0 or panel_gap < 0 or panel_power <= 0:
                QMessageBox.warning(parent, "Invalid Input", "All values must be positive numbers.")
                return None
            
            if panel_length > MAX_LENGTH or panel_width > MAX_WIDTH:
                QMessageBox.warning(parent, "Invalid Dimensions", f"Panel dimensions too large. Maximum: {MAX_LENGTH}×{MAX_WIDTH} mm")
                return None

            if panel_power > MAX_POWER:
                QMessageBox.warning(parent, "Invalid Input", f"Panel power too high. Maximum: {MAX_POWER}W")
                return None
            
            if invert_checkbox.isChecked():
                panel_length, panel_width = panel_width, panel_length
            
            panel_model_name = "Custom"
            if predefined_radio.isChecked():
                index = panel_combo.currentIndex()
                if not panel_combo.itemData(index, Qt.UserRole):
                    panel_model_name = panel_combo.currentText()
            
            config = {
                'panel_length': panel_length,
                'panel_width': panel_width,
                'panel_gap': panel_gap,
                'panel_power': panel_power,
                'panel_model': panel_model_name,
                'dimensions_inverted': invert_checkbox.isChecked()
            }
            
            if is_flat_roof and tilt_input and orientation_combo:
                panel_tilt = float(tilt_input.text())
                panel_orientation = orientation_combo.currentData()
                
                directions = [('North', 0), ('East', 90), ('South', 180), ('West', 270)]
                direction_name = directions[orientation_combo.currentIndex()][0]
                
                if panel_tilt < 0 or panel_tilt > 45:
                    QMessageBox.warning(parent, "Invalid Input", "Tilt angle must be between 0 and 45 degrees.")
                    return None
                
                config['panel_tilt'] = panel_tilt
                config['panel_orientation'] = panel_orientation
                config['orientation_direction'] = direction_name
            
            return config
            
        except ValueError:
            QMessageBox.warning(parent, "Invalid Input", "Please enter valid numeric values for all fields.")
            return None
    else:
        return None
