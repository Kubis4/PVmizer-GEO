#!/usr/bin/env python3
"""
ui/panel/model_tab_left/datetime_controls.py
Date and Time controls for Model3D panel with azimuth arc display
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

# Try to import solar calculations
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
        # Map 0-1440 minutes to 180-0 degrees (East to West)
        return 180 - (minutes / 1440) * 180
    
    def _time_from_angle(self, angle):
        """Convert angle to time in minutes"""
        # Map 180-0 degrees to 0-1440 minutes
        return int((180 - angle) / 180 * 1440)
    
    def _point_to_time(self, pos):
        """Convert mouse position to time"""
        center_x = self.width() // 2
        center_y = self.height() - 20
        
        # Calculate angle from mouse position
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
    """Date and time control widget with sunrise/sunset display"""
    
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
        
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Setup the date/time UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main group box
        self.group_box = QGroupBox("📅 Date & Time Control")
        layout.addWidget(self.group_box)
        
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.setSpacing(10)
        
        # Simple date control - Day and Month only
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setMinimumWidth(50)
        date_layout.addWidget(date_label)
        
        # Day spinner
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(QDate.currentDate().day())
        self.day_spin.setPrefix("")
        self.day_spin.setSuffix("")
        self.day_spin.valueChanged.connect(self._on_date_changed)
        self.day_spin.setMinimumWidth(50)
        self.day_spin.setMaximumWidth(60)
        date_layout.addWidget(self.day_spin)
        
        # Month combo box with full names
        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.month_combo.currentIndexChanged.connect(self._on_date_changed)
        date_layout.addWidget(self.month_combo)
        
        date_layout.addStretch()
        
        group_layout.addLayout(date_layout)
        
        # Large time display with compact sun info
        time_container = QWidget()
        time_container.setStyleSheet("background-color: #34495e; border-radius: 8px; padding: 5px;")
        time_layout = QVBoxLayout(time_container)
        time_layout.setSpacing(5)
        
        self.time_label = QLabel("12:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        time_layout.addWidget(self.time_label)
        
        # Compact sun position info - horizontal layout
        position_layout = QHBoxLayout()
        position_layout.setSpacing(10)
        
        # Azimuth with icon
        self.azimuth_label = QLabel("↻ 180°")
        self.azimuth_label.setAlignment(Qt.AlignCenter)
        position_layout.addWidget(self.azimuth_label)
        
        # Separator
        separator = QLabel("|")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        position_layout.addWidget(separator)
        
        # Elevation with icon
        self.elevation_label = QLabel("↑ 45°")
        self.elevation_label.setAlignment(Qt.AlignCenter)
        position_layout.addWidget(self.elevation_label)
        
        time_layout.addLayout(position_layout)
        
        group_layout.addWidget(time_container)
        
        # Arc slider for sun position
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
        
        # Day length display
        self.day_length_label = QLabel("☀️ Day Length: -- hours")
        self.day_length_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.day_length_label)
        
        # Animation control
        self.animation_btn = QPushButton("▶️ Animate Sun")
        self.animation_btn.setCheckable(True)
        self.animation_btn.toggled.connect(self._on_animation_toggled)
        group_layout.addWidget(self.animation_btn)
        
        # Initialize sunrise/sunset
        self._update_sun_times()
        self._calculate_sun_position()
        
        # Update hemisphere based on current latitude
        self._update_hemisphere()
    
    def apply_styling(self):
        """Apply custom styling from centralized styles"""
        if STYLES_AVAILABLE:
            # Apply styles to individual widgets
            self.group_box.setStyleSheet(get_model3d_groupbox_style())
            
            # Apply to all labels except special ones
            for label in self.findChildren(QLabel):
                if label not in [self.time_label, self.sunrise_label, self.sunset_label, 
                               self.day_length_label, self.azimuth_label, self.elevation_label]:
                    label.setStyleSheet(get_model3d_label_style())
            
            # Enhanced time label style - large but fits small screens
            self.time_label.setStyleSheet("""
                font-weight: bold;
                color: #3498db;
                font-size: 28px;
                background-color: transparent;
                padding: 2px;
            """)
            
            # Compact azimuth/elevation labels
            self.azimuth_label.setStyleSheet("color: #3498db; font-weight: bold; font-size: 14px; background-color: transparent;")
            self.elevation_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 14px; background-color: transparent;")
            
            # Sunrise/sunset labels - more compact
            sun_label_style = "font-size: 12px; font-weight: bold; background-color: transparent;"
            self.sunrise_label.setStyleSheet(sun_label_style + "color: #f39c12;")
            self.sunset_label.setStyleSheet(sun_label_style + "color: #e74c3c;")
            self.day_length_label.setStyleSheet("font-size: 11px; color: #95a5a6; background-color: transparent;")
            
            # Apply to spinbox and combobox
            self.day_spin.setStyleSheet(get_model3d_spinbox_style())
            self.month_combo.setStyleSheet(get_model3d_combobox_style())
            
            # Apply to button
            self.animation_btn.setStyleSheet(get_model3d_button_style("animate"))
        else:
            # Fallback styling
            self.setStyleSheet("""
                QGroupBox {
                    background-color: #34495e;
                    border: 1px solid #3498db;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 15px;
                    font-weight: bold;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    color: #3498db;
                    background-color: #34495e;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
                QSpinBox, QComboBox {
                    background-color: #34495e;
                    color: #ffffff;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 6px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-height: 28px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:checked {
                    background-color: #e74c3c;
                }
            """)
            
            # Enhanced time label
            self.time_label.setStyleSheet("""
                font-weight: bold;
                color: #3498db;
                font-size: 28px;
                background-color: transparent;
                padding: 2px;
            """)
    
    def _update_hemisphere(self):
        """Update hemisphere display based on latitude"""
        is_southern = self.latitude < 0
        self.arc_slider.set_hemisphere(is_southern)
    
    def _calculate_sun_position(self):
        """Calculate sun azimuth and elevation"""
        try:
            # Get current time and date
            decimal_hour = self.arc_slider.value() / 60.0
            day_of_year = self._get_day_of_year()
            
            # Solar calculations (simplified)
            solar_noon = 12.0
            hour_angle = 15.0 * (decimal_hour - solar_noon)  # degrees
            
            # Declination angle
            declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
            
            # Solar elevation angle
            lat_rad = math.radians(self.latitude)
            dec_rad = math.radians(declination)
            hour_rad = math.radians(hour_angle)
            
            elevation = math.asin(
                math.sin(lat_rad) * math.sin(dec_rad) + 
                math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hour_rad)
            )
            elevation_deg = math.degrees(elevation)
            
            # Azimuth calculation
            azimuth = math.atan2(
                -math.sin(hour_rad),
                math.tan(dec_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(hour_rad)
            )
            azimuth_deg = (math.degrees(azimuth) + 180) % 360
            
            # Update labels with compact format
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
        
        # Use current year
        year = QDate.currentDate().year()
        
        # Calculate day of year
        date = QDate(year, month, day)
        return date.dayOfYear()
    
    def _on_time_changed(self, value):
        """Handle time slider change"""
        # Convert minutes to decimal hours
        decimal_hour = value / 60.0
        
        # Update time label
        hours = int(decimal_hour)
        minutes = int((decimal_hour - hours) * 60)
        self.time_label.setText(f"{hours:02d}:{minutes:02d}")
        
        # Update sun position
        self._calculate_sun_position()
        
        # Emit signal
        self.time_changed.emit(decimal_hour)
    
    def _on_date_changed(self):
        """Handle date change"""
        # Validate day for the selected month
        month = self.month_combo.currentIndex() + 1
        max_day = calendar.monthrange(QDate.currentDate().year(), month)[1]
        
        if self.day_spin.value() > max_day:
            self.day_spin.setValue(max_day)
        
        # Update max day for spinner
        self.day_spin.setMaximum(max_day)
        
        # Calculate day of year
        day_of_year = self._get_day_of_year()
        
        # Update sunrise/sunset times
        self._update_sun_times()
        
        # Update sun position
        self._calculate_sun_position()
        
        # Emit signal
        self.date_changed.emit(day_of_year)
    
    def _update_sun_times(self):
        """Update sunrise and sunset time displays"""
        if not SOLAR_CALC_AVAILABLE:
            sunrise_minutes = 360  # 6:00 AM
            sunset_minutes = 1080  # 6:00 PM
            self.sunrise_label.setText("🌅 06:00")
            self.sunset_label.setText("🌇 18:00")
            self.day_length_label.setText("☀️ 12h 0m")
        else:
            try:
                # Get current day of year
                day_of_year = self._get_day_of_year()
                
                # Calculate sunrise and sunset
                sunrise, sunset = SolarCalculations.get_time_range(self.latitude, day_of_year)
                
                # Convert to minutes
                sunrise_minutes = int(sunrise * 60)
                sunset_minutes = int(sunset * 60)
                
                # Format times
                sunrise_str = SolarCalculations.format_time(sunrise)
                sunset_str = SolarCalculations.format_time(sunset)
                
                # Update labels - compact format
                self.sunrise_label.setText(f"🌅 {sunrise_str}")
                self.sunset_label.setText(f"🌇 {sunset_str}")
                
                # Calculate day length
                day_length = sunset - sunrise
                hours = int(day_length)
                minutes = int((day_length - hours) * 60)
                self.day_length_label.setText(f"☀️ {hours}h {minutes}m")
                
            except Exception as e:
                print(f"Error updating sun times: {e}")
                sunrise_minutes = 360  # 6:00 AM
                sunset_minutes = 1080  # 6:00 PM
                self.sunrise_label.setText("🌅 06:00")
                self.sunset_label.setText("🌇 18:00")
                self.day_length_label.setText("☀️ 12h 0m")
        
        # Update arc slider with sun times
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
    
    def _on_animation_toggled(self, checked):
        """Handle animation toggle"""
        self.animation_active = checked
        
        if checked:
            self.animation_btn.setText("⏸️ Stop Animation")
            self.animation_timer.start(100)  # Update every 100ms
        else:
            self.animation_btn.setText("▶️ Animate Sun")
            self.animation_timer.stop()
        
        self.animation_toggled.emit(checked)
    
    def _animate_time(self):
        """Animate time progression"""
        if not self.animation_active:
            return
        
        # Advance time by 6 minutes (0.1 hours)
        current_minutes = self.arc_slider.value()
        new_minutes = (current_minutes + 6) % 1440
        
        self.arc_slider.setValue(new_minutes)
    
    def get_current_date_time(self):
        """Get current date and time"""
        # Create date from controls
        year = QDate.currentDate().year()
        month = self.month_combo.currentIndex() + 1
        day = self.day_spin.value()
        
        # Validate day
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
        """Update theme (always dark for this panel)"""
        self.apply_styling()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        self.animation_active = False
