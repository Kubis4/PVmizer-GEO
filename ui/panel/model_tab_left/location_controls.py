#!/usr/bin/env python3
"""
ui/panel/model_tab_left/location_controls.py
CLEANED - No hardcoded styles
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QComboBox, QPushButton, QDoubleSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt

class LocationControls(QWidget):
    """Location settings control widget with weather"""
    
    # Signals
    location_changed = pyqtSignal(float, float)  # latitude, longitude
    weather_changed = pyqtSignal(float)
    
    # Predefined locations with coordinates
    LOCATIONS = {
        "Nitra, Slovakia": (48.3061, 18.0764),
        "New York, USA": (40.7128, -74.0060),
        "London, UK": (51.5074, -0.1278),
        "Paris, France": (48.8566, 2.3522),
        "Berlin, Germany": (52.5200, 13.4050),
        "Tokyo, Japan": (35.6762, 139.6503),
        "Sydney, Australia": (-33.8688, 151.2093),
        "Dubai, UAE": (25.2048, 55.2708),
        "Singapore": (1.3521, 103.8198),
        "Mumbai, India": (19.0760, 72.8777),
        "São Paulo, Brazil": (-23.5505, -46.6333),
        "Cairo, Egypt": (30.0444, 31.2357),
        "Moscow, Russia": (55.7558, 37.6173),
        "Beijing, China": (39.9042, 116.4074),
        "Los Angeles, USA": (34.0522, -118.2437),
        "Toronto, Canada": (43.6532, -79.3832),
        "Mexico City, Mexico": (19.4326, -99.1332),
        "Rome, Italy": (41.9028, 12.4964),
        "Madrid, Spain": (40.4168, -3.7038),
        "Stockholm, Sweden": (59.3293, 18.0686)
    }
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Set default location to Nitra
        self.current_location = self.LOCATIONS["Nitra, Slovakia"]
        self.current_weather = 1.0  # Clear sky
        
        # Control references
        self.group_box = None
        self.preset_combo = None
        self.lat_spin = None
        self.lon_spin = None
        self.weather_buttons = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the location UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main group box
        self.group_box = QGroupBox("🌍 Location & Weather Settings")
        layout.addWidget(self.group_box)
        
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.setSpacing(10)
        
        # Preset locations
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Location:")
        preset_label.setMinimumWidth(60)
        preset_layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        # Add locations in sorted order, but keep Nitra first
        locations_list = ["Nitra, Slovakia"] + sorted([loc for loc in self.LOCATIONS.keys() if loc != "Nitra, Slovakia"])
        self.preset_combo.addItems(locations_list)
        self.preset_combo.setCurrentIndex(0)  # Set to Nitra
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)
        preset_layout.addWidget(self.preset_combo)
        
        group_layout.addLayout(preset_layout)
        
        # Coordinates display
        coords_layout = QHBoxLayout()
        coords_layout.setSpacing(15)
        
        # Latitude
        lat_layout = QVBoxLayout()
        lat_label = QLabel("Latitude:")
        self.lat_label = lat_label  # Store reference
        lat_layout.addWidget(lat_label)
        
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90.0, 90.0)
        self.lat_spin.setDecimals(4)
        self.lat_spin.setValue(48.3061)  # Nitra latitude
        self.lat_spin.setSuffix("°")
        self.lat_spin.valueChanged.connect(self._on_location_changed)
        lat_layout.addWidget(self.lat_spin)
        
        coords_layout.addLayout(lat_layout)
        
        # Longitude
        lon_layout = QVBoxLayout()
        lon_label = QLabel("Longitude:")
        self.lon_label = lon_label  # Store reference
        lon_layout.addWidget(lon_label)
        
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180.0, 180.0)
        self.lon_spin.setDecimals(4)
        self.lon_spin.setValue(18.0764)  # Nitra longitude
        self.lon_spin.setSuffix("°")
        self.lon_spin.valueChanged.connect(self._on_location_changed)
        lon_layout.addWidget(self.lon_spin)
        
        coords_layout.addLayout(lon_layout)
        coords_layout.addStretch()
        
        group_layout.addLayout(coords_layout)
        
        # Weather control with icon buttons
        weather_label = QLabel("Weather Conditions:")
        group_layout.addWidget(weather_label)
        
        weather_buttons_layout = QHBoxLayout()
        weather_buttons_layout.setSpacing(5)
        
        # Weather conditions
        weather_conditions = [
            ("☀️", "Clear Sky", 1.0),
            ("⛅", "Partly Cloudy", 0.8),
            ("☁️", "Cloudy", 0.6),
            ("🌧️", "Light Rain", 0.4),
            ("⛈️", "Storm", 0.2)
        ]
        
        for emoji, tooltip, factor in weather_conditions:
            btn = QPushButton(emoji)
            btn.setToolTip(tooltip)
            btn.setCheckable(True)
            btn.setFixedSize(55, 55)
            btn.setObjectName("weatherButton")  # For styling
            btn.clicked.connect(lambda checked, f=factor, b=btn: self._on_weather_selected(f, b))
            
            weather_buttons_layout.addWidget(btn)
            self.weather_buttons.append(btn)
        
        # Set default to clear sky
        self.weather_buttons[0].setChecked(True)
        
        weather_buttons_layout.addStretch()
        group_layout.addLayout(weather_buttons_layout)
    
    def _on_location_changed(self):
        """Handle location change"""
        lat = self.lat_spin.value()
        lon = self.lon_spin.value()
        self.current_location = (lat, lon)
        self.location_changed.emit(lat, lon)
    
    def _on_preset_selected(self, preset):
        """Handle preset location selection"""
        if preset in self.LOCATIONS:
            lat, lon = self.LOCATIONS[preset]
            # Block signals to prevent double emission
            self.lat_spin.blockSignals(True)
            self.lon_spin.blockSignals(True)
            
            self.lat_spin.setValue(lat)
            self.lon_spin.setValue(lon)
            
            self.lat_spin.blockSignals(False)
            self.lon_spin.blockSignals(False)
            
            # Now emit the signal once
            self.current_location = (lat, lon)
            self.location_changed.emit(lat, lon)
    
    def _on_weather_selected(self, weather_factor, button):
        """Handle weather button selection"""
        # Uncheck all other buttons
        for btn in self.weather_buttons:
            if btn != button:
                btn.setChecked(False)
        
        # Ensure the clicked button stays checked
        button.setChecked(True)
        
        # Update weather
        self.current_weather = weather_factor
        self.weather_changed.emit(weather_factor)
    
    def get_location(self):
        """Get current location coordinates"""
        return self.current_location
    
    def set_location(self, location_name):
        """Set location by name"""
        if location_name in self.LOCATIONS:
            self.preset_combo.setCurrentText(location_name)
    
    def get_weather_factor(self):
        """Get current weather factor"""
        return self.current_weather
    
    def update_theme(self, is_dark_theme):
        """Update theme - no hardcoded styles"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        pass
