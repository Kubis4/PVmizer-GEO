#!/usr/bin/env python3
"""
ui/panel/model_tab_left/datetime_controls.py
Fixed version with actual sun movement during animation
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QPushButton, QSpinBox, QComboBox)
from PyQt5.QtCore import pyqtSignal, Qt, QDate, QTimer, QRect, QPointF
from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor, QPainterPath
import math
import calendar

try:
    from styles.ui_styles import (
        get_model3d_groupbox_style,
        get_model3d_label_style,
        get_model3d_button_style,
        get_model3d_scrollbar_style,
        get_model3d_time_label_style,
        get_model3d_sun_info_label_style,
        get_model3d_spinbox_style,
        get_model3d_combobox_style
    )
    STYLES_AVAILABLE = True
except ImportError:
    STYLES_AVAILABLE = False
    print("⚠️ Styles not available for DateTimeControls")

try:
    from solar_system.solar_calculations import SolarCalculations
    SOLAR_CALC_AVAILABLE = True
except ImportError:
    SOLAR_CALC_AVAILABLE = False
    print("⚠️ SolarCalculations not available for sunrise/sunset")


class ArcSlider(QWidget):
    """Custom arc slider widget for sun position"""
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        
        self._minimum = 0
        self._maximum = 1440
        self._value = 720
        self._sunrise = 360  # 6:00 AM default
        self._sunset = 1080  # 6:00 PM default
        self._is_southern_hemisphere = False
        
        self._dragging = False
        self.setMouseTracking(True)
        
    def set_sun_times(self, sunrise_minutes, sunset_minutes):
        """Set sunrise and sunset times in minutes"""
        self._sunrise = sunrise_minutes
        self._sunset = sunset_minutes
        self.update()
        
    def set_hemisphere(self, is_southern):
        """Set whether we're in southern hemisphere"""
        self._is_southern_hemisphere = is_southern
        self.update()
        
    def setValue(self, value):
        """Set the current value"""
        if value != self._value:
            self._value = max(self._minimum, min(self._maximum, value))
            self.valueChanged.emit(self._value)
            self.update()
            
    def value(self):
        """Get the current value"""
        return self._value
    
    def paintEvent(self, event):
        """Paint the arc slider"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height - 20
        radius = min(width // 2 - 30, height - 40)
        
        # Draw horizon line
        painter.setPen(QPen(QColor("#34495e"), 2))
        painter.drawLine(20, center_y, width - 20, center_y)
        
        # Draw arc background
        painter.setPen(QPen(QColor("#34495e"), 8))
        painter.drawArc(center_x - radius, center_y - radius, 
                       radius * 2, radius * 2, 
                       0, 180 * 16)
        
        # Draw daylight arc (sunrise to sunset)
        if self._sunrise < self._sunset:
            start_angle = self._angle_from_time(self._sunrise)
            end_angle = self._angle_from_time(self._sunset)
            span_angle = end_angle - start_angle
            
            painter.setPen(QPen(QColor("#f39c12"), 6))
            painter.drawArc(center_x - radius, center_y - radius,
                           radius * 2, radius * 2,
                           int(start_angle * 16), int(span_angle * 16))
        
        # Draw sun position
        angle = self._angle_from_time(self._value)
        sun_x = center_x + radius * math.cos(math.radians(angle))
        sun_y = center_y - radius * math.sin(math.radians(angle))
        
        # Draw sun
        if self._sunrise <= self._value <= self._sunset:
            # Daytime - yellow sun
            painter.setBrush(QBrush(QColor("#f1c40f")))
            painter.setPen(QPen(QColor("#f39c12"), 2))
            painter.drawEllipse(QPointF(sun_x, sun_y), 12, 12)
        else:
            # Nighttime - moon
            painter.setBrush(QBrush(QColor("#95a5a6")))
            painter.setPen(QPen(QColor("#7f8c8d"), 2))
            painter.drawEllipse(QPointF(sun_x, sun_y), 10, 10)
        
        # Draw direction labels
        painter.setPen(QPen(QColor("#ffffff"), 1))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        
        # East
        painter.drawText(QRect(10, center_y - 20, 40, 20), 
                        Qt.AlignCenter, "E")
        # North/South (depending on hemisphere)
        middle_label = "N" if self._is_southern_hemisphere else "S"
        painter.drawText(QRect(center_x - 20, 5, 40, 20), 
                        Qt.AlignCenter, middle_label)
        # West
        painter.drawText(QRect(width - 50, center_y - 20, 40, 20), 
                        Qt.AlignCenter, "W")
        
    def _angle_from_time(self, minutes):
        """Convert time in minutes to angle (0-180 degrees)"""
        return 180 - (minutes / 1440) * 180
    
    def _time_from_angle(self, angle):
        """Convert angle to time in minutes"""
        return int((180 - angle) / 180 * 1440)
    
    def _point_to_time(self, pos):
        """Convert mouse position to time"""
        center_x = self.width() // 2
        center_y = self.height() - 20
        
        dx = pos.x() - center_x
        dy = center_y - pos.y()
        
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
            
        return self._time_from_angle(angle)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            new_value = self._point_to_time(event.pos())
            self.setValue(new_value)
            
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self._dragging:
            new_value = self._point_to_time(event.pos())
            self.setValue(new_value)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self._dragging = False


class DateTimeControls(QWidget):
    """Date and time control with working sun animation"""
    
    # Signals
    time_changed = pyqtSignal(float)  # Decimal time (0-24)
    date_changed = pyqtSignal(int)    # Day of year (1-365)
    animation_toggled = pyqtSignal(bool)
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.animation_active = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_time)
        
        # Animation settings - 20 minutes per step
        self.animation_step_minutes = 10  # 20 minutes per step
        self.animation_interval_ms = 500  # Update every 200ms
        
        # Reference to solar visualization
        self.solar_viz = None
        self.model_tab = None
        
        # Default location (Nitra, Slovakia)
        self.latitude = 48.3061
        self.longitude = 18.0764
        
        # Control references
        self.group_box = None
        self.day_spin = None
        self.month_combo = None
        self.arc_slider = None
        self.time_label = None
        self.azimuth_label = None
        self.elevation_label = None
        self.sunrise_label = None
        self.sunset_label = None
        self.day_length_label = None
        self.animation_btn = None
        self.time_container = None
        
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Setup the date/time UI with proper styling"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main group box - LIGHT BLUE BACKGROUND
        self.group_box = QGroupBox("📅 Date & Time Control")
        layout.addWidget(self.group_box)
        
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.setSpacing(10)
        
        # Date control
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setMinimumWidth(50)
        date_layout.addWidget(date_label)
        
        # Day spinner
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(QDate.currentDate().day())
        self.day_spin.valueChanged.connect(self._on_date_changed)
        self.day_spin.setMinimumWidth(50)
        self.day_spin.setMaximumWidth(60)
        date_layout.addWidget(self.day_spin)
        
        # Month combo box
        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.month_combo.currentIndexChanged.connect(self._on_date_changed)
        date_layout.addWidget(self.month_combo)
        
        date_layout.addStretch()
        group_layout.addLayout(date_layout)
        
        # Time display container - DARK BLUE BACKGROUND
        self.time_container = QWidget()
        time_layout = QVBoxLayout(self.time_container)
        time_layout.setSpacing(5)
        time_layout.setContentsMargins(10, 10, 10, 10)
        
        self.time_label = QLabel("12:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.time_label)
        
        # Sun position info
        position_layout = QHBoxLayout()
        position_layout.setSpacing(10)
        
        self.azimuth_label = QLabel("↻ 180°")
        self.azimuth_label.setAlignment(Qt.AlignCenter)
        position_layout.addWidget(self.azimuth_label)
        
        separator = QLabel("|")
        separator.setAlignment(Qt.AlignCenter)
        position_layout.addWidget(separator)
        
        self.elevation_label = QLabel("↑ 45°")
        self.elevation_label.setAlignment(Qt.AlignCenter)
        position_layout.addWidget(self.elevation_label)
        
        time_layout.addLayout(position_layout)
        group_layout.addWidget(self.time_container)
        
        # Arc slider
        self.arc_slider = ArcSlider()
        self.arc_slider.valueChanged.connect(self._on_time_changed)
        group_layout.addWidget(self.arc_slider)
        
        # Sunrise/Sunset display
        sun_info_layout = QHBoxLayout()
        
        self.sunrise_label = QLabel("🌅 --:--")
        sun_info_layout.addWidget(self.sunrise_label)
        
        sun_info_layout.addStretch()
        
        self.sunset_label = QLabel("🌇 --:--")
        sun_info_layout.addWidget(self.sunset_label)
        
        group_layout.addLayout(sun_info_layout)
        
        # Day length
        self.day_length_label = QLabel("☀️ Day Length: -- hours")
        self.day_length_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.day_length_label)
        
        # Animation control button
        self.animation_btn = QPushButton("▶️ Animate Sun (20min steps)")
        self.animation_btn.setCheckable(True)
        self.animation_btn.clicked.connect(self._on_animation_button_clicked)
        group_layout.addWidget(self.animation_btn)
        
        # Initialize
        self._update_sun_times()
        self._calculate_sun_position()
        self._update_hemisphere()
    
    def apply_styling(self):
        """Apply custom styling with inverted colors"""
        try:
            # Group box style - LIGHT BLUE BACKGROUND
            self.group_box.setStyleSheet("""
                QGroupBox {
                    background-color: #34495e;  /* Light blue (actually darker) */
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    color: #3498db;
                    background-color: #34495e;
                }
            """)
            
            # Time container style - DARK BLUE BACKGROUND
            self.time_container.setStyleSheet("""
                QWidget {
                    background-color: #2c3e50;  /* Dark blue */
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            
            # Time label
            self.time_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #3498db;
                    font-size: 28px;
                    background-color: transparent;
                    padding: 2px;
                }
            """)
            
            # Position labels
            self.azimuth_label.setStyleSheet("""
                QLabel {
                    color: #3498db;
                    font-weight: bold;
                    font-size: 14px;
                    background-color: transparent;
                }
            """)
            self.elevation_label.setStyleSheet("""
                QLabel {
                    color: #f39c12;
                    font-weight: bold;
                    font-size: 14px;
                    background-color: transparent;
                }
            """)
            
            # Separator
            for label in self.findChildren(QLabel):
                if label.text() == "|":
                    label.setStyleSheet("color: #7f8c8d; font-size: 14px; background-color: transparent;")
            
            # Sun info labels
            self.sunrise_label.setStyleSheet("color: #f39c12; font-size: 12px; font-weight: bold; background-color: transparent;")
            self.sunset_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-weight: bold; background-color: transparent;")
            self.day_length_label.setStyleSheet("color: #95a5a6; font-size: 11px; background-color: transparent;")
            
            # Date label
            for label in self.findChildren(QLabel):
                if label.text() == "Date:":
                    label.setStyleSheet("color: #ffffff; background-color: transparent;")
            
            # Button style
            self.animation_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:checked {
                    background-color: #e74c3c;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            
            # Spinbox and combobox
            self.day_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #2c3e50;
                    color: white;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 4px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #3498db;
                    border: none;
                    width: 16px;
                }
            """)
            
            self.month_combo.setStyleSheet("""
                QComboBox {
                    background-color: #2c3e50;
                    color: white;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 4px;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: #3498db;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid white;
                    margin-right: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2c3e50;
                    color: white;
                    selection-background-color: #3498db;
                }
            """)
            
        except Exception as e:
            print(f"⚠️ Error applying styling: {e}")
    
    def _on_animation_button_clicked(self):
        """Handle animation button click"""
        checked = self.animation_btn.isChecked()
        self._on_animation_toggled(checked)
    
    def _on_animation_toggled(self, checked):
        """Handle animation toggle - DO NOT USE ANIMATION MODE"""
        print(f"🎬 Animation button toggled: {checked}")
        self.animation_active = checked
        
        # Try to get references if not set
        if not self.solar_viz or not self.model_tab:
            self._find_references()
        
        if checked:
            print(f"▶️ Starting animation with {self.animation_step_minutes}-minute steps...")
            
            # DO NOT START ANIMATION MODE - WE WANT THE SUN TO MOVE!
            # Just start the timer
            
            self.animation_btn.setText("⏸️ Stop Animation")
            self.animation_timer.start(self.animation_interval_ms)
            print(f"✅ Animation started: {self.animation_step_minutes} min/step, {self.animation_interval_ms}ms interval")
        else:
            print("⏸️ Stopping animation...")
            
            self.animation_btn.setText("▶️ Animate Sun (20min steps)")
            self.animation_timer.stop()
            print("✅ Animation stopped")
        
        # Emit signal
        self.animation_toggled.emit(checked)
    
    def _find_references(self):
        """Find solar visualization and model tab references"""
        try:
            # Try to find model tab through main window
            if hasattr(self.main_window, 'content_tabs'):
                for i in range(self.main_window.content_tabs.count()):
                    tab = self.main_window.content_tabs.widget(i)
                    if hasattr(tab, 'solar_visualization'):
                        self.solar_viz = tab.solar_visualization
                        self.model_tab = tab
                        print("✅ Found solar visualization and model tab references")
                        return
            
            # Alternative: Try through parent hierarchy
            parent = self.parent()
            while parent:
                if hasattr(parent, 'model_tab'):
                    self.model_tab = parent.model_tab
                    if hasattr(parent.model_tab, 'solar_visualization'):
                        self.solar_viz = parent.model_tab.solar_visualization
                        print("✅ Found references through parent")
                        return
                parent = parent.parent()
                
            print("⚠️ Could not find solar visualization or model tab")
            
        except Exception as e:
            print(f"⚠️ Error finding references: {e}")
    
    def _animate_time(self):
        """Animate time and actually move the sun"""
        if not self.animation_active:
            return
        
        # Get current time in minutes
        current_minutes = self.arc_slider.value()
        
        # Advance by 20 minutes
        new_minutes = (current_minutes + self.animation_step_minutes) % 1440
        
        # Update arc slider (this will trigger _on_time_changed)
        self.arc_slider.setValue(new_minutes)
        
        # Calculate decimal hour
        decimal_hour = new_minutes / 60.0
        
        # IMPORTANT: Update the sun directly without animation mode
        if self.solar_viz:
            # Set time and force visual update
            self.solar_viz.current_hour = decimal_hour
            self.solar_viz.create_realistic_sun()
            self.solar_viz.calculate_solar_performance()
        elif self.model_tab:
            # Fallback to model tab update
            self.model_tab.update_solar_time(decimal_hour)
        
        # Debug output every hour
        if new_minutes % 60 == 0:
            hours = new_minutes // 60
            print(f"⏰ Animation time: {hours:02d}:00 - Sun is moving!")
    
    def set_solar_viz(self, solar_viz):
        """Set reference to solar visualization"""
        self.solar_viz = solar_viz
        print("✅ Solar visualization reference set")
    
    def set_model_tab(self, model_tab):
        """Set reference to model tab"""
        self.model_tab = model_tab
        print("✅ Model tab reference set")
    
    def _update_hemisphere(self):
        """Update hemisphere display based on latitude"""
        is_southern = self.latitude < 0
        self.arc_slider.set_hemisphere(is_southern)
    
    def _calculate_sun_position(self):
        """Calculate sun azimuth and elevation"""
        try:
            decimal_hour = self.arc_slider.value() / 60.0
            day_of_year = self._get_day_of_year()
            
            solar_noon = 12.0
            hour_angle = 15.0 * (decimal_hour - solar_noon)
            
            declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
            
            lat_rad = math.radians(self.latitude)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)
            
            elevation = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad) + 
                math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
            )
            elevation_deg = math.degrees(elevation)
            
            azimuth = math.atan2(
                -math.sin(hour_rad),
                math.tan(dec_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(hour_rad)
            )
            azimuth_deg = (math.degrees(azimuth) + 180) % 360
            
            self.azimuth_label.setText(f"↻ {azimuth_deg:.0f}°")
            self.elevation_label.setText(f"↑ {elevation_deg:.0f}°")
            
        except Exception as e:
            print(f"Error calculating sun position: {e}")
            self.azimuth_label.setText("↻ --°")
            self.elevation_label.setText("↑ --°")
    
    def _get_day_of_year(self):
        """Calculate day of year from day and month"""
        day = self.day_spin.value()
        month = self.month_combo.currentIndex() + 1
        year = QDate.currentDate().year()
        date = QDate(year, month, day)
        return date.dayOfYear()
    
    def _on_time_changed(self, value):
        """Handle time slider change"""
        decimal_hour = value / 60.0
        
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        self.time_label.setText(f"{hours:02d}:{minutes:02d}")
        
        self._calculate_sun_position()
        
        # Emit signal for sun update
        self.time_changed.emit(decimal_hour)
    
    def _on_date_changed(self):
        """Handle date change"""
        month = self.month_combo.currentIndex() + 1
        max_day = calendar.monthrange(QDate.currentDate().year(), month)[1]
        
        if self.day_spin.value() > max_day:
            self.day_spin.setValue(max_day)
        
        self.day_spin.setMaximum(max_day)
        
        day_of_year = self._get_day_of_year()
        
        self._update_sun_times()
        self._calculate_sun_position()
        
        self.date_changed.emit(day_of_year)
    
    def _update_sun_times(self):
        """Update sunrise and sunset time displays"""
        if not SOLAR_CALC_AVAILABLE:
            sunrise_minutes = 360
            sunset_minutes = 1080
            self.sunrise_label.setText("🌅 06:00")
            self.sunset_label.setText("🌇 18:00")
            self.day_length_label.setText("☀️ 12h 0m")
        else:
            try:
                day_of_year = self._get_day_of_year()
                
                sunrise, sunset = SolarCalculations.get_time_range(self.latitude, day_of_year, self.longitude)
                
                sunrise_minutes = int(sunrise * 60)
                sunset_minutes = int(sunset * 60)
                
                sunrise_str = SolarCalculations.format_time(sunrise)
                sunset_str = SolarCalculations.format_time(sunset)
                
                self.sunrise_label.setText(f"🌅 {sunrise_str}")
                self.sunset_label.setText(f"🌇 {sunset_str}")
                
                day_length = sunset - sunrise
                hours = int(day_length)
                minutes = int((day_length - hours) * 60)
                self.day_length_label.setText(f"☀️ {hours}h {minutes}m")
                
            except Exception as e:
                print(f"Error updating sun times: {e}")
                sunrise_minutes = 360
                sunset_minutes = 1080
                self.sunrise_label.setText("🌅 06:00")
                self.sunset_label.setText("🌇 18:00")
                self.day_length_label.setText("☀️ 12h 0m")
        
        self.arc_slider.set_sun_times(sunrise_minutes, sunset_minutes)
    
    def set_location(self, latitude, longitude):
        """Update location for sunrise/sunset calculations"""
        self.latitude = latitude
        self.longitude = longitude
        self._update_sun_times()
        self._calculate_sun_position()
        self._update_hemisphere()
    
    def set_time(self, hour):
        """Set time to specific hour"""
        self.arc_slider.setValue(int(hour * 60))
    
    def get_current_date_time(self):
        """Get current date and time"""
        year = QDate.currentDate().year()
        month = self.month_combo.currentIndex() + 1
        day = self.day_spin.value()
        
        max_day = calendar.monthrange(year, month)[1]
        if day > max_day:
            day = max_day
            
        date = QDate(year, month, day)
        
        return {
            'date': date,
            'day_of_year': date.dayOfYear(),
            'decimal_hour': self.arc_slider.value() / 60.0
        }
    
    def update_theme(self, is_dark_theme):
        """Update theme"""
        self.apply_styling()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        self.animation_active = False
