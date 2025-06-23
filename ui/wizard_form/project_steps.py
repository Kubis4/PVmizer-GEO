#!/usr/bin/env python3
"""
Individual wizard steps for project creation - theme-aware version
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, 
                            QDoubleSpinBox, QCheckBox, QMessageBox, QScrollArea)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class BaseStep(QWidget):
    """Base class for wizard steps"""
    
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self._setup_ui()
    
    def _setup_ui(self):
        """Override in subclasses"""
        pass
    
    def validate(self):
        """Override in subclasses - return True if valid"""
        return True
    
    def get_data(self):
        """Override in subclasses - return dict of data"""
        return {}
    
    def load_data(self, project_data):
        """Override in subclasses - load existing data"""
        pass

class BasicInfoStep(BaseStep):
    """Basic project information step"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title_label = QLabel("📋 Basic Project Information")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Enter project name (e.g., Smith Family Solar)")
        form_layout.addRow("🏷️ Project Name*:", self.project_name)
        
        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("Enter client name")
        form_layout.addRow("👤 Client Name*:", self.client_name)
        
        self.project_type = QComboBox()
        self.project_type.addItems([
            "Residential Solar Installation",
            "Commercial Solar Installation", 
            "Industrial Solar Installation",
            "Solar Farm Development",
            "Roof Analysis Only",
            "Energy Audit"
        ])
        form_layout.addRow("🏗️ Project Type:", self.project_type)
        
        self.project_description = QTextEdit()
        self.project_description.setMaximumHeight(80)
        self.project_description.setPlaceholderText("Brief project description (optional)...")
        form_layout.addRow("📝 Description:", self.project_description)
        
        layout.addLayout(form_layout)
        
        # Info
        info_label = QLabel("💡 Tip: Choose a descriptive project name that will help you identify this project later.")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def validate(self):
        if not self.project_name.text().strip():
            QMessageBox.warning(self.wizard, "Validation Error", "Project name is required!")
            self.project_name.setFocus()
            return False
            
        if not self.client_name.text().strip():
            QMessageBox.warning(self.wizard, "Validation Error", "Client name is required!")
            self.client_name.setFocus()
            return False
        
        return True
    
    def get_data(self):
        return {
            "basic_info": {
                "project_name": self.project_name.text().strip(),
                "client_name": self.client_name.text().strip(),
                "description": self.project_description.toPlainText().strip(),
                "project_type": self.project_type.currentText()
            }
        }
    
    def load_data(self, project_data):
        basic = project_data.get('basic_info', {})
        self.project_name.setText(basic.get('project_name', ''))
        self.client_name.setText(basic.get('client_name', ''))
        self.project_description.setText(basic.get('description', ''))
        
        project_type = basic.get('project_type', '')
        index = self.project_type.findText(project_type)
        if index >= 0:
            self.project_type.setCurrentIndex(index)

class LocationStep(BaseStep):
    """Location information step"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title_label = QLabel("🌍 Location Information")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.address = QLineEdit()
        self.address.setPlaceholderText("Full property address")
        form_layout.addRow("🏠 Address*:", self.address)
        
        # City and ZIP in one row
        city_zip_layout = QHBoxLayout()
        self.city = QLineEdit()
        self.city.setPlaceholderText("City")
        city_zip_layout.addWidget(self.city)
        
        self.zip_code = QLineEdit()
        self.zip_code.setPlaceholderText("ZIP")
        self.zip_code.setMaximumWidth(100)
        city_zip_layout.addWidget(self.zip_code)
        
        form_layout.addRow("🏙️ City, ZIP:", city_zip_layout)
        
        layout.addLayout(form_layout)
        
        # Info
        info_label = QLabel("💡 Tip: Please provide the complete address for accurate solar analysis.")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def validate(self):
        if not self.address.text().strip():
            QMessageBox.warning(self.wizard, "Validation Error", "Address is required!")
            self.address.setFocus()
            return False
        return True
    
    def get_data(self):
        return {
            "location_info": {
                "address": self.address.text().strip(),
                "city": self.city.text().strip(),
                "zip_code": self.zip_code.text().strip()
            }
        }
    
    def load_data(self, project_data):
        location = project_data.get('location_info', {})
        self.address.setText(location.get('address', ''))
        self.city.setText(location.get('city', ''))
        self.zip_code.setText(location.get('zip_code', ''))

class EnergyStep(BaseStep):
    """Energy information step"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title_label = QLabel("⚡ Energy Information")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.annual_consumption = QDoubleSpinBox()
        self.annual_consumption.setRange(0, 999999)
        self.annual_consumption.setValue(12000)
        self.annual_consumption.setSuffix(" kWh/year")
        self.annual_consumption.setToolTip("Annual electricity consumption")
        form_layout.addRow("📊 Annual Consumption*:", self.annual_consumption)
        
        self.monthly_consumption = QDoubleSpinBox()
        self.monthly_consumption.setRange(0, 99999)
        self.monthly_consumption.setValue(1000)
        self.monthly_consumption.setSuffix(" kWh/month")
        form_layout.addRow("📅 Monthly Average:", self.monthly_consumption)
        
        self.peak_demand = QDoubleSpinBox()
        self.peak_demand.setRange(0, 9999)
        self.peak_demand.setValue(5.0)
        self.peak_demand.setSuffix(" kW")
        self.peak_demand.setToolTip("Peak power demand")
        form_layout.addRow("⚡ Peak Demand:", self.peak_demand)
        
        self.current_rate = QDoubleSpinBox()
        self.current_rate.setRange(0, 999)
        self.current_rate.setValue(0.12)
        self.current_rate.setSuffix(" €/kWh")
        self.current_rate.setDecimals(4)
        form_layout.addRow("💰 Electricity Rate*:", self.current_rate)
        
        layout.addLayout(form_layout)
        
        # Auto-calculate monthly from annual
        self.annual_consumption.valueChanged.connect(self._update_monthly)
        
        # Info
        info_label = QLabel("💡 Tip: You can find this information on your electricity bills. Annual consumption will auto-calculate monthly average.")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def _update_monthly(self):
        annual = self.annual_consumption.value()
        self.monthly_consumption.setValue(annual / 12)
    
    def validate(self):
        if self.annual_consumption.value() <= 0:
            QMessageBox.warning(self.wizard, "Validation Error", "Annual consumption must be greater than 0!")
            self.annual_consumption.setFocus()
            return False
        
        if self.current_rate.value() <= 0:
            QMessageBox.warning(self.wizard, "Validation Error", "Electricity rate must be greater than 0!")
            self.current_rate.setFocus()
            return False
        
        return True
    
    def get_data(self):
        return {
            "energy_info": {
                "annual_consumption_kwh": self.annual_consumption.value(),
                "monthly_consumption_kwh": self.monthly_consumption.value(),
                "peak_demand_kw": self.peak_demand.value(),
                "electricity_rate_per_kwh": self.current_rate.value()
            }
        }
    
    def load_data(self, project_data):
        energy = project_data.get('energy_info', {})
        self.annual_consumption.setValue(energy.get('annual_consumption_kwh', 12000))
        self.monthly_consumption.setValue(energy.get('monthly_consumption_kwh', 1000))
        self.peak_demand.setValue(energy.get('peak_demand_kw', 5.0))
        self.current_rate.setValue(energy.get('electricity_rate_per_kwh', 0.12))

class TechnicalStep(BaseStep):
    """Technical information step"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title_label = QLabel("🔧 Technical Information")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.roof_material = QComboBox()
        self.roof_material.addItems([
            "Asphalt Shingles",
            "Metal Roofing",
            "Tile Roofing",
            "Slate",
            "Concrete",
            "Membrane (Flat)",
            "Other"
        ])
        form_layout.addRow("🏠 Roof Material:", self.roof_material)
        
        self.roof_age = QSpinBox()
        self.roof_age.setRange(0, 100)
        self.roof_age.setValue(10)
        self.roof_age.setSuffix(" years")
        form_layout.addRow("📅 Roof Age:", self.roof_age)
        
        self.roof_condition = QComboBox()
        self.roof_condition.addItems([
            "Excellent",
            "Good", 
            "Fair",
            "Poor",
            "Needs Replacement"
        ])
        self.roof_condition.setCurrentText("Good")
        form_layout.addRow("✅ Roof Condition:", self.roof_condition)
        
        self.shading_concerns = QCheckBox("Significant shading present")
        form_layout.addRow("🌳 Shading:", self.shading_concerns)
        
        self.grid_connection = QCheckBox("Grid-tied system")
        self.grid_connection.setChecked(True)
        form_layout.addRow("🔌 Grid Connection:", self.grid_connection)
        
        layout.addLayout(form_layout)
        
        # Info
        info_label = QLabel("💡 Tip: Roof condition and shading will affect solar panel placement and efficiency calculations.")
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def get_data(self):
        return {
            "technical_info": {
                "roof_material": self.roof_material.currentText(),
                "roof_age_years": self.roof_age.value(),
                "roof_condition": self.roof_condition.currentText(),
                "has_shading": self.shading_concerns.isChecked(),
                "grid_connected": self.grid_connection.isChecked()
            }
        }
    
    def load_data(self, project_data):
        technical = project_data.get('technical_info', {})
        
        roof_material = technical.get('roof_material', '')
        index = self.roof_material.findText(roof_material)
        if index >= 0:
            self.roof_material.setCurrentIndex(index)
        
        self.roof_age.setValue(technical.get('roof_age_years', 10))
        
        roof_condition = technical.get('roof_condition', '')
        index = self.roof_condition.findText(roof_condition)
        if index >= 0:
            self.roof_condition.setCurrentIndex(index)
        
        self.shading_concerns.setChecked(technical.get('has_shading', False))
        self.grid_connection.setChecked(technical.get('grid_connected', True))

class SummaryStep(BaseStep):
    """Summary and confirmation step"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        title_label = QLabel("📋 Project Summary")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Scrollable summary area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.summary_label = QLabel("Project summary will appear here...")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.summary_label)
        layout.addWidget(scroll_area)
        
        # Confirmation
        confirm_label = QLabel("✅ Please review the information above and click 'Create Project' to proceed.")
        confirm_label.setObjectName("confirmLabel")
        confirm_label.setWordWrap(True)
        layout.addWidget(confirm_label)
    
    def update_summary(self, project_data):
        """Update summary with project data"""
        try:
            basic = project_data.get('basic_info', {})
            location = project_data.get('location_info', {})
            energy = project_data.get('energy_info', {})
            technical = project_data.get('technical_info', {})
            
            # Calculate some quick metrics
            annual_cost = energy.get('annual_consumption_kwh', 0) * energy.get('electricity_rate_per_kwh', 0)
            monthly_cost = annual_cost / 12
            
            # Check if parent has dark theme for text colors
            dark_theme = False
            if self.wizard.parent_window and hasattr(self.wizard.parent_window, 'config'):
                dark_theme = getattr(self.wizard.parent_window.config, 'dark_theme', False)
            
            # Set colors based on theme
            if dark_theme:
                text_color = "#ecf0f1"
                heading_color = "#3498db"
            else:
                text_color = "#2c3e50"
                heading_color = "#2c3e50"
            
            # Updated summary HTML with new organization
            summary_html = f"""
            <div style="color: {text_color}; padding: 15px; font-size: 13px; line-height: 1.4;">
            <h3 style="color: {heading_color}; margin-bottom: 15px;">{basic.get('project_name', 'Untitled Project')}</h3>
            
            <h4 style="color: #2ecc71;">📝 Description</h4>
            <p>{basic.get('description', 'No description provided.')}</p>
            
            <h4 style="color: #3498db;">📋 Project Details</h4>
            <ul>
                <li><b>Client:</b> {basic.get('client_name', 'N/A')}</li>
                <li><b>Type:</b> {basic.get('project_type', 'N/A')}</li>
                <li><b>Location:</b> {location.get('address', 'N/A')}</li>
                <li><b>City:</b> {location.get('city', 'N/A')} {location.get('zip_code', '')}</li>
            </ul>
            
            <h4 style="color: #e74c3c;">⚡ Energy Profile</h4>
            <ul>
                <li><b>Annual Consumption:</b> {energy.get('annual_consumption_kwh', 0):,.0f} kWh/year</li>
                <li><b>Monthly Average:</b> {energy.get('monthly_consumption_kwh', 0):,.0f} kWh/month</li>
                <li><b>Electricity Rate:</b> {energy.get('electricity_rate_per_kwh', 0):.4f} €/kWh</li>
                <li><b>Current Annual Cost:</b> {annual_cost:,.2f} €</li>
                <li><b>Current Monthly Cost:</b> {monthly_cost:,.2f} €</li>
            </ul>
            
            <h4 style="color: #9b59b6;">🔧 Technical Details</h4>
            <ul>
                <li><b>Roof Material:</b> {technical.get('roof_material', 'N/A')}</li>
                <li><b>Roof Age:</b> {technical.get('roof_age_years', 0)} years</li>
                <li><b>Roof Condition:</b> {technical.get('roof_condition', 'N/A')}</li>
                <li><b>Shading Issues:</b> {'Yes' if technical.get('has_shading', False) else 'No'}</li>
                <li><b>Grid Connected:</b> {'Yes' if technical.get('grid_connected', True) else 'No'}</li>
            </ul>
            </div>
            """
            
            self.summary_label.setText(summary_html)
            
        except Exception as e:
            self.summary_label.setText(f"<p style='color: red;'>Error generating summary: {e}</p>")