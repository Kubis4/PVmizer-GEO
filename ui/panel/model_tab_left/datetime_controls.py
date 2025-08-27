#!/usr/bin/env python3
"""
ui/panel/model_tab_left/datetime_controls.py
Complete enhanced visual styling with crash prevention and proper formatting
UPDATED: Azimuth first, Time middle, Elevation right
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QPushButton, QSpinBox, QComboBox)
from PyQt5.QtCore import pyqtSignal, Qt, QDate, QTimer, QRect, QPointF
from PyQt5.QtGui import (QFont, QPainter, QPen, QBrush, QColor, QRadialGradient, 
                         QLinearGradient, QPolygonF)
import math
import calendar
import time

try:
    from solar_system.solar_calculations import SolarCalculations
    SOLAR_CALC_AVAILABLE = True
except ImportError:
    SOLAR_CALC_AVAILABLE = False


class ArcSlider(QWidget):
    """Enhanced arc slider with crash prevention and proper throttling"""
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(180)
        self.setMaximumHeight(180)
        
        self._minimum = 0
        self._maximum = 1440
        self._value = 720
        self._sunrise = 360
        self._sunset = 1080
        self._is_southern_hemisphere = False
        
        self._dragging = False
        self._last_update = 0
        self._last_emit = 0
        self._update_interval = 0.033  # ~30fps limit
        self._emit_interval = 0.05     # Limit signal emissions to 20fps
        
        # Crash prevention flags
        self._in_paint_event = False
        self._in_mouse_event = False
        self._update_queued = False
        
        # Enable mouse tracking for smoother interaction
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        
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
        """Set value with smart throttling and crash prevention"""
        try:
            current_time = time.time()
            
            # Prevent recursive calls
            if self._in_mouse_event:
                return
                
            # Throttle updates during dragging
            if self._dragging and current_time - self._last_update < self._update_interval:
                return
                
            if value != self._value:
                self._value = max(self._minimum, min(self._maximum, value))
                
                # Throttle signal emissions to prevent cascade crashes
                if current_time - self._last_emit >= self._emit_interval:
                    try:
                        self.valueChanged.emit(self._value)
                        self._last_emit = current_time
                    except Exception as e:
                        pass
                
                # Queue update instead of immediate update
                if not self._update_queued:
                    self._update_queued = True
                    self.update()
                
                self._last_update = current_time
                
        except Exception as e:
            pass
            
    def value(self):
        """Get the current value"""
        return self._value
    
    def paintEvent(self, event):
        """Paint with crash prevention"""
        try:
            # Prevent recursive paint events
            if self._in_paint_event:
                return
                
            self._in_paint_event = True
            self._update_queued = False
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Use transparent background to match container
            widget_rect = self.rect()
            painter.fillRect(widget_rect, QColor(0, 0, 0, 0))
            
            # Cache frequently used values
            width = self.width()
            height = self.height()
            center_x = width // 2
            center_y = height - 45
            radius = min(width // 2 - 40, height - 80)
            
            # Validate dimensions to prevent crashes
            if radius <= 0 or width <= 0 or height <= 0:
                return
                
            # Draw enhanced horizon line (ground) with gradient
            ground_gradient = QLinearGradient(25, center_y, width - 25, center_y)
            ground_gradient.setColorAt(0, QColor("#34495e"))
            ground_gradient.setColorAt(0.5, QColor("#2c3e50"))
            ground_gradient.setColorAt(1, QColor("#34495e"))
            painter.setPen(QPen(QBrush(ground_gradient), 3))
            painter.drawLine(25, center_y, width - 25, center_y)
            
            # Draw sky gradient background arc
            sky_gradient = QLinearGradient(center_x, center_y - radius, center_x, center_y)
            sky_gradient.setColorAt(0, QColor("#3498db"))
            sky_gradient.setColorAt(0.7, QColor("#5dade2"))
            sky_gradient.setColorAt(1, QColor("#85c1e9"))
            painter.setPen(QPen(QBrush(sky_gradient), 10))
            painter.drawArc(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2, 
                           0, 180 * 16)
            
            # Draw ENHANCED SUN TRAJECTORY with safe calculations
            if self._sunrise < self._sunset:
                try:
                    start_angle = self._angle_from_time(self._sunrise)
                    end_angle = self._angle_from_time(self._sunset)
                    span_angle = end_angle - start_angle
                    
                    # Validate angles
                    if not (0 <= start_angle <= 180) or not (0 <= end_angle <= 180):
                        start_angle = max(0, min(180, start_angle))
                        end_angle = max(0, min(180, end_angle))
                        span_angle = end_angle - start_angle
                    
                    # Draw bright sun trajectory path
                    trajectory_gradient = QLinearGradient(center_x, center_y - radius, center_x, center_y)
                    trajectory_gradient.setColorAt(0, QColor("#ffd700"))
                    trajectory_gradient.setColorAt(0.3, QColor("#ffed4e"))
                    trajectory_gradient.setColorAt(0.6, QColor("#ffa500"))
                    trajectory_gradient.setColorAt(1, QColor("#ff6347"))
                    
                    painter.setPen(QPen(QBrush(trajectory_gradient), 12))
                    painter.drawArc(center_x - radius, center_y - radius,
                                   radius * 2, radius * 2,
                                   int(start_angle * 16), int(span_angle * 16))
                    
                    # Add glow effect
                    glow_gradient = QLinearGradient(center_x, center_y - radius, center_x, center_y)
                    glow_gradient.setColorAt(0, QColor(255, 215, 0, 100))
                    glow_gradient.setColorAt(0.5, QColor(255, 237, 78, 80))
                    glow_gradient.setColorAt(1, QColor(255, 99, 71, 60))
                    
                    painter.setPen(QPen(QBrush(glow_gradient), 18))
                    painter.drawArc(center_x - radius, center_y - radius,
                                   radius * 2, radius * 2,
                                   int(start_angle * 16), int(span_angle * 16))
                    
                    # Draw night arc sections
                    night_color = QColor("#2c3e50")
                    if self._sunrise > 0:
                        painter.setPen(QPen(night_color, 6))
                        painter.drawArc(center_x - radius, center_y - radius,
                                       radius * 2, radius * 2,
                                       0, int(start_angle * 16))
                    
                    if self._sunset < 1440:
                        painter.setPen(QPen(night_color, 6))
                        painter.drawArc(center_x - radius, center_y - radius,
                                       radius * 2, radius * 2,
                                       int(end_angle * 16), int((180 - end_angle) * 16))
                except Exception as e:
                    pass
            
            # Draw sunrise and sunset markers with safe calculations
            if self._sunrise < self._sunset:
                try:
                    # Calculate sunrise position
                    sunrise_angle = self._angle_from_time(self._sunrise)
                    if 0 <= sunrise_angle <= 180:
                        sunrise_x = center_x + radius * math.cos(math.radians(sunrise_angle))
                        sunrise_y = center_y - radius * math.sin(math.radians(sunrise_angle))
                        
                        # Enhanced sunrise marker
                        sunrise_glow = QRadialGradient(QPointF(sunrise_x, sunrise_y), 20)
                        sunrise_glow.setColorAt(0, QColor(255, 150, 100, 180))
                        sunrise_glow.setColorAt(1, QColor(255, 150, 100, 0))
                        painter.setBrush(QBrush(sunrise_glow))
                        painter.setPen(QPen(Qt.NoPen))
                        painter.drawEllipse(QPointF(sunrise_x, sunrise_y), 20, 20)
                        
                        painter.setBrush(QBrush(QColor("#ff9649")))
                        painter.setPen(QPen(QColor("#e67e22"), 3))
                        painter.drawEllipse(QPointF(sunrise_x, sunrise_y), 12, 12)
                    
                    # Calculate sunset position
                    sunset_angle = self._angle_from_time(self._sunset)
                    if 0 <= sunset_angle <= 180:
                        sunset_x = center_x + radius * math.cos(math.radians(sunset_angle))
                        sunset_y = center_y - radius * math.sin(math.radians(sunset_angle))
                        
                        # Enhanced sunset marker
                        sunset_glow = QRadialGradient(QPointF(sunset_x, sunset_y), 20)
                        sunset_glow.setColorAt(0, QColor(255, 100, 100, 180))
                        sunset_glow.setColorAt(1, QColor(255, 100, 100, 0))
                        painter.setBrush(QBrush(sunset_glow))
                        painter.setPen(QPen(Qt.NoPen))
                        painter.drawEllipse(QPointF(sunset_x, sunset_y), 20, 20)
                        
                        painter.setBrush(QBrush(QColor("#e74c3c")))
                        painter.setPen(QPen(QColor("#c0392b"), 3))
                        painter.drawEllipse(QPointF(sunset_x, sunset_y), 12, 12)
                        
                except Exception as e:
                    pass
            
            # Draw current sun/moon position with safe calculations
            try:
                angle = self._angle_from_time(self._value)
                if 0 <= angle <= 180:
                    sun_x = center_x + radius * math.cos(math.radians(angle))
                    sun_y = center_y - radius * math.sin(math.radians(angle))
                    
                    if self._sunrise <= self._value <= self._sunset:
                        # SMALLER daytime sun
                        sun_glow = QRadialGradient(QPointF(sun_x, sun_y), 25)
                        sun_glow.setColorAt(0, QColor(255, 220, 100, 150))
                        sun_glow.setColorAt(0.5, QColor(255, 200, 50, 100))
                        sun_glow.setColorAt(0.8, QColor(255, 180, 30, 50))
                        sun_glow.setColorAt(1, QColor(255, 180, 30, 0))
                        painter.setBrush(QBrush(sun_glow))
                        painter.setPen(QPen(Qt.NoPen))
                        painter.drawEllipse(QPointF(sun_x, sun_y), 25, 25)
                        
                        # Draw sun rays
                        painter.setPen(QPen(QColor("#ffd700"), 2))
                        for i in range(8):
                            ray_angle = i * 45
                            ray_start_x = sun_x + 7 * math.cos(math.radians(ray_angle))
                            ray_start_y = sun_y + 7 * math.sin(math.radians(ray_angle))
                            ray_end_x = sun_x + 18 * math.cos(math.radians(ray_angle))
                            ray_end_y = sun_y + 18 * math.sin(math.radians(ray_angle))
                            painter.drawLine(QPointF(ray_start_x, ray_start_y), QPointF(ray_end_x, ray_end_y))
                        
                        # Sun body
                        sun_body_gradient = QRadialGradient(QPointF(sun_x, sun_y), 8)
                        sun_body_gradient.setColorAt(0, QColor("#fff5b4"))
                        sun_body_gradient.setColorAt(0.6, QColor("#ffd32c"))
                        sun_body_gradient.setColorAt(1, QColor("#f39c12"))
                        painter.setBrush(QBrush(sun_body_gradient))
                        painter.setPen(QPen(QColor("#e67e22"), 2))
                        painter.drawEllipse(QPointF(sun_x, sun_y), 14, 14)
                        
                        # Bright center
                        painter.setBrush(QBrush(QColor("#ffffff")))
                        painter.setPen(QPen(Qt.NoPen))
                        painter.drawEllipse(QPointF(sun_x - 1, sun_y - 1), 4, 4)
                    else:
                        # Enhanced nighttime moon
                        moon_glow = QRadialGradient(QPointF(sun_x, sun_y), 18)
                        moon_glow.setColorAt(0, QColor(200, 200, 255, 100))
                        moon_glow.setColorAt(1, QColor(200, 200, 255, 0))
                        painter.setBrush(QBrush(moon_glow))
                        painter.setPen(QPen(Qt.NoPen))
                        painter.drawEllipse(QPointF(sun_x, sun_y), 18, 18)
                        
                        moon_gradient = QRadialGradient(QPointF(sun_x - 2, sun_y - 2), 6)
                        moon_gradient.setColorAt(0, QColor("#f8f9fa"))
                        moon_gradient.setColorAt(1, QColor("#dee2e6"))
                        painter.setBrush(QBrush(moon_gradient))
                        painter.setPen(QPen(QColor("#adb5bd"), 1))
                        painter.drawEllipse(QPointF(sun_x, sun_y), 12, 12)
                        
                        # Moon craters
                        painter.setBrush(QBrush(QColor("#ced4da")))
                        painter.setPen(QPen(Qt.NoPen))
                        painter.drawEllipse(QPointF(sun_x + 2, sun_y - 1), 2, 2)
                        painter.drawEllipse(QPointF(sun_x - 2, sun_y + 2), 1, 1)
                        
            except Exception as e:
                pass
            
            # Draw direction labels with safe calculations
            try:
                painter.setPen(QPen(QColor("#ffffff"), 2))
                font = QFont("Arial", 11, QFont.Bold)
                painter.setFont(font)
                
                label_distance = 25
                
              
                # East label
                east_x = center_x + radius + label_distance
                east_y = center_y
                painter.drawText(QRect(east_x - 12, east_y - 10, 25, 20), 
                                Qt.AlignCenter, "E")
                
                # West label
                west_x = center_x - radius - label_distance
                west_y = center_y
                painter.drawText(QRect(west_x - 12, west_y - 10, 25, 20), 
                                Qt.AlignCenter, "W")
                
                # North/South label
                middle_label = "N" if self._is_southern_hemisphere else "S"
                south_x = center_x
                south_y = center_y - radius - label_distance
                painter.drawText(QRect(south_x - 12, south_y - 10, 25, 20), 
                                Qt.AlignCenter, middle_label)
                                
            except Exception as e:
                pass
                
        except Exception as e:
            pass
        finally:
            self._in_paint_event = False
    
    def mousePressEvent(self, event):
        """Handle mouse press with crash prevention"""
        try:
            if event.button() == Qt.LeftButton and not self._in_mouse_event:
                self._in_mouse_event = True
                self._dragging = True
                new_value = self._point_to_time(event.pos())
                self._value = new_value
                
                # Emit signal safely
                try:
                    self.valueChanged.emit(self._value)
                except Exception as e:
                    pass
                    
                self.update()
        except Exception as e:
            pass
        finally:
            self._in_mouse_event = False
            
    def mouseMoveEvent(self, event):
        """Handle mouse movement with crash prevention and throttling"""
        try:
            if self._dragging and not self._in_mouse_event:
                current_time = time.time()
                
                # Throttle mouse move events aggressively
                if current_time - self._last_update < self._update_interval:
                    return
                    
                self._in_mouse_event = True
                new_value = self._point_to_time(event.pos())
                
                # Only update if value changed significantly
                if abs(new_value - self._value) > 5:  # Increased threshold
                    self._value = new_value
                    
                    # Throttle signal emissions
                    if current_time - self._last_emit >= self._emit_interval:
                        try:
                            self.valueChanged.emit(self._value)
                            self._last_emit = current_time
                        except Exception as e:
                            pass
                    
                    self.update()
                    self._last_update = current_time
                    
        except Exception as e:
            pass
        finally:
            self._in_mouse_event = False
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release with crash prevention"""
        try:
            self._dragging = False
            self._in_mouse_event = False
            
            # Final update with current value
            try:
                self.valueChanged.emit(self._value)
            except Exception as e:
                pass
                
        except Exception as e:
            pass
    
    def _angle_from_time(self, minutes):
        """Convert time in minutes to angle with bounds checking"""
        try:
            minutes = max(0, min(1440, minutes))
            return 180 - (minutes / 1440) * 180
        except Exception:
            return 90  # Default to noon
    
    def _time_from_angle(self, angle):
        """Convert angle to time with bounds checking"""
        try:
            angle = max(0, min(180, angle))
            return int((180 - angle) / 180 * 1440)
        except Exception:
            return 720  # Default to noon
    
    def _point_to_time(self, pos):
        """Convert mouse position to time with safe calculations"""
        try:
            center_x = self.width() // 2
            center_y = self.height() - 45
            
            dx = pos.x() - center_x
            dy = center_y - pos.y()
            
            # Avoid division by zero and invalid calculations
            if dx == 0 and dy == 0:
                return self._value
                
            angle = math.degrees(math.atan2(dy, dx))
            angle = max(0, min(180, angle))
            
            return self._time_from_angle(angle)
            
        except Exception as e:
            return self._value  # Return current value on error
    
    def wheelEvent(self, event):
        """Handle wheel for fine control"""
        try:
            delta = event.angleDelta().y()
            step = 15 if delta > 0 else -15
            new_value = max(0, min(1440, self._value + step))
            self.setValue(new_value)
            event.accept()
        except Exception as e:
            pass
            
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        try:
            if event.key() == Qt.Key_Left:
                self.setValue(max(0, self._value - 30))
            elif event.key() == Qt.Key_Right:
                self.setValue(min(1440, self._value + 30))
            elif event.key() == Qt.Key_Home:
                self.setValue(self._sunrise)
            elif event.key() == Qt.Key_End:
                self.setValue(self._sunset)
            else:
                super().keyPressEvent(event)
        except Exception as e:
            pass


class DateTimeControls(QWidget):
    """Enhanced date and time control with proper container styling and crash prevention"""
    
    # Signals
    time_changed = pyqtSignal(float)  # Decimal time (0-24)
    date_changed = pyqtSignal(int)    # Day of year (1-365)
    animation_toggled = pyqtSignal(bool)
    camera_movement_detected = pyqtSignal()  # Signal for camera movement
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.animation_active = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_time)
        
        # Camera movement detection
        self.camera_movement_timer = QTimer()
        self.camera_movement_timer.timeout.connect(self._check_camera_movement)
        self.last_camera_position = None
        self.camera_check_interval = 100  # Check every 100ms
        
        # Animation settings
        self.animation_step_minutes = 15
        self.animation_interval_ms = 1000  # 1 second per step
        
        # Reference to solar systems
        self.solar_viz = None
        self.solar_simulation = None
        self.model_tab = None
        
        # Default location (Nitra, Slovakia)
        self.latitude = 48.3061
        self.longitude = 18.0764
        
        # Performance optimization
        self._last_update = 0
        self._update_throttle = 0.1
        self._last_sun_update = 0
        
        # Control references
        self.group_box = None
        self.day_spin = None
        self.month_combo = None
        self.arc_slider = None
        self.time_label = None
        self.azimuth_label = None
        self.elevation_label = None
        self.azimuth_desc = None
        self.elevation_desc = None
        self.sunrise_label = None
        self.sunset_label = None
        self.day_length_label = None
        self.animation_btn = None
        self.time_container = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup date/time UI with UPDATED ORDER: Azimuth | Time | Elevation"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Main group box
        self.group_box = QGroupBox("📅 Date & Time Control")
        layout.addWidget(self.group_box)
        
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.setSpacing(8)
        
        # Enhanced date control with better styling
        date_layout = QHBoxLayout()
        date_label = QLabel("📅 Date:")
        date_label.setMinimumWidth(60)
        date_layout.addWidget(date_label)
        
        # Day spinner with enhanced styling
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(QDate.currentDate().day())
        self.day_spin.valueChanged.connect(self._on_date_changed)
        self.day_spin.setMinimumWidth(55)
        self.day_spin.setMaximumWidth(65)
        date_layout.addWidget(self.day_spin)
        
        # Month combo box with enhanced styling
        self.month_combo = QComboBox()
        months = ["🌨️ January", "❄️ February", "🌸 March", "🌷 April", "🌺 May", "☀️ June",
                  "🌞 July", "🌻 August", "🍂 September", "🍁 October", "🌧️ November", "⛄ December"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.month_combo.currentIndexChanged.connect(self._on_date_changed)
        self.month_combo.setMinimumWidth(140)
        date_layout.addWidget(self.month_combo)
        
        date_layout.addStretch()
        group_layout.addLayout(date_layout)
        
        # TIME CONTAINER - UPDATED ORDER: Azimuth | Time | Elevation
        self.time_container = QWidget()
        self.time_container.setObjectName("timeContainer")
        self.time_container.setFixedHeight(100)  # Perfect height
        
        time_layout = QHBoxLayout(self.time_container)
        time_layout.setSpacing(15)  # Small spacing between sections
        time_layout.setContentsMargins(0, 10, 0, 10)  # Only top/bottom margins
        
        # LEFT SECTION: Azimuth (FIRST)
        azimuth_section = QVBoxLayout()
        azimuth_section.setSpacing(2)
        azimuth_section.setAlignment(Qt.AlignCenter)
        
        # Azimuth description - GRAY text
        self.azimuth_desc = QLabel("Azimuth")
        self.azimuth_desc.setAlignment(Qt.AlignCenter)
        self.azimuth_desc.setMinimumWidth(80)
        self.azimuth_desc.setStyleSheet("""
            font-size: 13px; 
            font-weight: normal; 
            font-family: Arial; 
            color: #95a5a6;
            background: transparent;
        """)
        azimuth_section.addWidget(self.azimuth_desc)
        
        # Azimuth value with compass icon
        self.azimuth_label = QLabel("🧭 289°")
        self.azimuth_label.setAlignment(Qt.AlignCenter)
        self.azimuth_label.setMinimumWidth(80)
        self.azimuth_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            font-family: Arial; 
            color: #ffffff;
            background: transparent;
        """)
        azimuth_section.addWidget(self.azimuth_label)
        
        time_layout.addLayout(azimuth_section)
        
        # MIDDLE SECTION: Time (SECOND - in the middle)
        time_section = QVBoxLayout()
        time_section.setSpacing(0)
        time_section.setAlignment(Qt.AlignCenter)
        
        # BIG YELLOW TIME - centered in middle
        self.time_label = QLabel("08:09")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setMinimumWidth(100)
        self.time_label.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            font-family: Arial; 
            color: #f1c40f;
            background: transparent;
        """)
        time_section.addWidget(self.time_label)
        
        time_layout.addLayout(time_section)
        
        # RIGHT SECTION: Elevation (THIRD)
        elevation_section = QVBoxLayout()
        elevation_section.setSpacing(2)
        elevation_section.setAlignment(Qt.AlignCenter)
        
        # Elevation description - GRAY text
        self.elevation_desc = QLabel("Elevation")
        self.elevation_desc.setAlignment(Qt.AlignCenter)
        self.elevation_desc.setMinimumWidth(80)
        self.elevation_desc.setStyleSheet("""
            font-size: 13px; 
            font-weight: normal; 
            font-family: Arial; 
            color: #95a5a6;
            background: transparent;
        """)
        elevation_section.addWidget(self.elevation_desc)
        
        # Elevation value with triangle icon
        self.elevation_label = QLabel("📐 28°")
        self.elevation_label.setAlignment(Qt.AlignCenter)
        self.elevation_label.setMinimumWidth(80)
        self.elevation_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            font-family: Arial; 
            color: #ffffff;
            background: transparent;
        """)
        elevation_section.addWidget(self.elevation_label)
        
        time_layout.addLayout(elevation_section)
        
        group_layout.addWidget(self.time_container)
        
        # Enhanced arc slider with 180px HEIGHT - exactly like your image
        self.arc_slider = ArcSlider()
        self.arc_slider.valueChanged.connect(self._on_time_changed)
        group_layout.addWidget(self.arc_slider)
        
        # Enhanced sunrise/sunset display - exactly like your image
        sun_info_layout = QHBoxLayout()
        sun_info_layout.setContentsMargins(10, 5, 10, 5)
        
        self.sunrise_label = QLabel("🌅 06:02")
        self.sunrise_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: bold; 
            font-family: Arial; 
            color: #f39c12;
        """)
        sun_info_layout.addWidget(self.sunrise_label)
        
        sun_info_layout.addStretch()
        
        self.sunset_label = QLabel("🌇 19:35")
        self.sunset_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: bold; 
            font-family: Arial; 
            color: #e74c3c;
        """)
        sun_info_layout.addWidget(self.sunset_label)
        
        group_layout.addLayout(sun_info_layout)
        
        # Enhanced day length display - exactly like your image
        self.day_length_label = QLabel("☀️ 13h 33m")
        self.day_length_label.setAlignment(Qt.AlignCenter)
        self.day_length_label.setStyleSheet("""
            font-size: 12px; 
            font-weight: normal; 
            font-family: Arial; 
            color: #ecf0f1;
        """)
        group_layout.addWidget(self.day_length_label)
        
        # Enhanced animation control button - blue style like your image
        self.animation_btn = QPushButton("▶ Animate Sun (15min steps)")
        self.animation_btn.setCheckable(True)
        self.animation_btn.clicked.connect(self._on_animation_button_clicked)
        self.animation_btn.setMinimumHeight(40)
        self.animation_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 8px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                font-family: Arial;
                padding: 8px;
            }
            QPushButton:checked {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:checked:hover {
                background-color: #c0392b;
            }
        """)
        group_layout.addWidget(self.animation_btn)
        
        # Initialize
        self._update_sun_times()
        self._calculate_sun_position()
        self._update_hemisphere()
        
        # Connect camera movement detection signal
        self.camera_movement_detected.connect(self._pause_animation_for_camera)
        
    def set_solar_viz(self, solar_viz):
        """Set reference to solar visualization"""
        self.solar_viz = solar_viz
    
    def set_solar_simulation(self, solar_sim):
        """Set reference to enhanced solar simulation"""
        self.solar_simulation = solar_sim
    
    def set_model_tab(self, model_tab):
        """Set reference to model tab"""
        self.model_tab = model_tab
        if model_tab:
            if hasattr(model_tab, 'solar_simulation'):
                self.solar_simulation = model_tab.solar_simulation
            if hasattr(model_tab, 'solar_visualization'):
                self.solar_viz = model_tab.solar_visualization
    
    def _on_animation_button_clicked(self):
        """Handle animation button click"""
        checked = self.animation_btn.isChecked()
        self._on_animation_toggled(checked)
    
    def _on_animation_toggled(self, checked):
        """Handle animation toggle with camera movement detection"""
        try:
            self.animation_active = checked
            
            if not self.solar_viz and not self.solar_simulation:
                self._find_references()
            
            if checked:
                self.animation_btn.setText("⏸️ Stop Animation")
                self.animation_timer.start(self.animation_interval_ms)
                # Start camera movement monitoring
                self.camera_movement_timer.start(self.camera_check_interval)
                self._store_camera_position()
            else:
                self.animation_btn.setText("▶️ Animate Sun (15min steps)")
                self.animation_timer.stop()
                # Stop camera movement monitoring
                self.camera_movement_timer.stop()
            
            self.animation_toggled.emit(checked)
        except Exception as e:
            pass
    
    def _store_camera_position(self):
        """Store current camera position for movement detection"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'plotter'):
                plotter = self.model_tab.plotter
                if hasattr(plotter, 'camera_position'):
                    self.last_camera_position = plotter.camera_position
                elif hasattr(plotter, 'camera'):
                    camera = plotter.camera
                    if hasattr(camera, 'position'):
                        self.last_camera_position = list(camera.position)
        except Exception as e:
            pass
    
    def _check_camera_movement(self):
        """Check if camera has moved and pause animation if needed"""
        try:
            if not self.animation_active or not self.model_tab:
                return
                
            if hasattr(self.model_tab, 'plotter'):
                plotter = self.model_tab.plotter
                current_position = None
                
                if hasattr(plotter, 'camera_position'):
                    current_position = plotter.camera_position
                elif hasattr(plotter, 'camera'):
                    camera = plotter.camera
                    if hasattr(camera, 'position'):
                        current_position = list(camera.position)
                
                if current_position and self.last_camera_position:
                    # Check if camera moved significantly
                    distance = sum((a - b) ** 2 for a, b in zip(current_position, self.last_camera_position)) ** 0.5
                    if distance > 0.1:  # Threshold for camera movement
                        self.camera_movement_detected.emit()
                        self.last_camera_position = current_position
                    else:
                        self.last_camera_position = current_position
                        
        except Exception as e:
            pass
    
    def _pause_animation_for_camera(self):
        """Pause animation when camera movement is detected"""
        try:
            if self.animation_active:
                # Temporarily stop animation
                self.animation_timer.stop()
                
                # Resume after a short delay (500ms)
                QTimer.singleShot(500, self._resume_animation_after_camera)
        except Exception as e:
            pass
    
    def _resume_animation_after_camera(self):
        """Resume animation after camera movement stops"""
        try:
            if self.animation_active:
                self.animation_timer.start(self.animation_interval_ms)
        except Exception as e:
            pass
    
    def _find_references(self):
        """Find solar system references"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                for i in range(self.main_window.content_tabs.count()):
                    tab = self.main_window.content_tabs.widget(i)
                    if hasattr(tab, 'solar_simulation'):
                        self.solar_simulation = tab.solar_simulation
                    if hasattr(tab, 'solar_visualization'):
                        self.solar_viz = tab.solar_visualization
                    if hasattr(tab, 'model_tab'):
                        self.model_tab = tab
                        return
            
            parent = self.parent()
            while parent:
                if hasattr(parent, 'model_tab'):
                    self.model_tab = parent.model_tab
                    if hasattr(parent.model_tab, 'solar_simulation'):
                        self.solar_simulation = parent.model_tab.solar_simulation
                    if hasattr(parent.model_tab, 'solar_visualization'):
                        self.solar_viz = parent.model_tab.solar_visualization
                    return
                parent = parent.parent()
                
        except Exception as e:
            pass
    
    def _animate_time(self):
        """Animation step with camera movement awareness"""
        try:
            if not self.animation_active:
                return
            
            current_minutes = self.arc_slider.value()
            # Ensure we increment by exactly 15 minutes
            new_minutes = current_minutes + self.animation_step_minutes
            
            # Handle day rollover
            if new_minutes >= 1440:
                new_minutes = new_minutes % 1440
            
            self.arc_slider.setValue(new_minutes)
            
            decimal_hour = new_minutes / 60.0
            self._update_solar_systems(decimal_hour)
            
        except Exception as e:
            pass
    
    def _on_time_changed(self, value):
        """Time change handler with proper solar updates"""
        try:
            decimal_hour = value / 60.0
            
            hours = int(decimal_hour)
            minutes = int((decimal_hour - hours) * 60)
            self.time_label.setText(f"{hours:02d}:{minutes:02d}")
            
            self._calculate_sun_position()
            self._update_solar_systems(decimal_hour)
            
            self.time_changed.emit(decimal_hour)
        except Exception as e:
            pass
    
    def _update_solar_systems(self, decimal_hour):
        """Update both solar visualization and simulation"""
        try:
            if self.solar_simulation:
                self.solar_simulation.set_time(decimal_hour)
                
                if self.model_tab and hasattr(self.model_tab, 'current_roof'):
                    roof = self.model_tab.current_roof
                    if roof:
                        if not hasattr(roof, 'solar_simulation') or roof.solar_simulation != self.solar_simulation:
                            roof.set_solar_simulation(self.solar_simulation)
                        
                        if hasattr(roof, 'rotation_angle'):
                            self.solar_simulation.update_for_building_rotation(roof.rotation_angle)
            
            if self.solar_viz:
                self.solar_viz.current_hour = decimal_hour
                
                sun_pos = self.solar_viz.calculate_sun_position() if hasattr(self.solar_viz, 'calculate_sun_position') else None
                if sun_pos and hasattr(self.solar_viz, 'model_tab'):
                    if hasattr(self.solar_viz.model_tab, 'unified_sun_system'):
                        solar_settings = {
                            'sunshafts_enabled': True,
                            'weather_factor': getattr(self.solar_viz, 'weather_factor', 1.0),
                            'current_hour': decimal_hour
                        }
                        self.solar_viz.model_tab.unified_sun_system.create_unified_sun(sun_pos, solar_settings)
                        
                        if hasattr(self.solar_viz.model_tab, 'current_roof'):
                            roof = self.solar_viz.model_tab.current_roof
                            if hasattr(roof, 'set_sun_position_for_lighting'):
                                roof.set_sun_position_for_lighting(sun_pos)
                                
        except Exception as e:
            pass
    
    def _on_date_changed(self):
        """Handle date change"""
        try:
            month = self.month_combo.currentIndex() + 1
            max_day = calendar.monthrange(QDate.currentDate().year(), month)[1]
            
            if self.day_spin.value() > max_day:
                self.day_spin.setValue(max_day)
            
            self.day_spin.setMaximum(max_day)
            
            day_of_year = self._get_day_of_year()
            
            self._update_sun_times()
            self._calculate_sun_position()
            
            if self.solar_simulation:
                self.solar_simulation.set_date(day_of_year)
            if self.solar_viz:
                self.solar_viz.current_day = day_of_year
            
            self.date_changed.emit(day_of_year)
        except Exception as e:
            pass
    
    def _update_hemisphere(self):
        """Update hemisphere display based on latitude"""
        try:
            is_southern = self.latitude < 0
            self.arc_slider.set_hemisphere(is_southern)
        except Exception as e:
            pass
    
    def _calculate_sun_position(self):
        """Calculate sun azimuth and elevation"""
        try:
            current_time = time.time()
            if current_time - self._last_update < self._update_throttle:
                return
            
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
            
            self.azimuth_label.setText(f"🧭 {azimuth_deg:.0f}°")
            self.elevation_label.setText(f"📐 {elevation_deg:.0f}°")
            
            self._last_update = current_time
            
        except Exception as e:
            self.azimuth_label.setText("🧭 --°")
            self.elevation_label.setText("📐 --°")
    
    def _get_day_of_year(self):
        """Calculate day of year from day and month"""
        try:
            day = self.day_spin.value()
            month = self.month_combo.currentIndex() + 1
            year = QDate.currentDate().year()
            date = QDate(year, month, day)
            return date.dayOfYear()
        except Exception:
            return 1
    
    def _update_sun_times(self):
        """Update sunrise and sunset time displays"""
        try:
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
                    sunrise_minutes = 360
                    sunset_minutes = 1080
                    self.sunrise_label.setText("🌅 06:00")
                    self.sunset_label.setText("🌇 18:00")
                    self.day_length_label.setText("☀️ 12h 0m")
            
            self.arc_slider.set_sun_times(sunrise_minutes, sunset_minutes)
        except Exception as e:
            pass
    
    def set_location(self, latitude, longitude):
        """Update location for sunrise/sunset calculations"""
        try:
            self.latitude = latitude
            self.longitude = longitude
            self._update_sun_times()
            self._calculate_sun_position()
            self._update_hemisphere()
            
            if self.solar_simulation:
                self.solar_simulation.set_location(latitude, longitude)
            if self.solar_viz:
                self.solar_viz.latitude = latitude
                self.solar_viz.longitude = longitude
        except Exception as e:
            pass
    
    def set_time(self, hour):
        """Set time to specific hour"""
        try:
            self.arc_slider.setValue(int(hour * 60))
        except Exception as e:
            pass
    
    def get_current_date_time(self):
        """Get current date and time"""
        try:
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
        except Exception as e:
            return {
                'date': QDate.currentDate(),
                'day_of_year': 1,
                'decimal_hour': 12.0
            }
    
    def update_theme(self, is_dark_theme):
        """Update theme - no hardcoded styles"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.animation_timer:
                self.animation_timer.stop()
                self.animation_timer = None
            if self.camera_movement_timer:
                self.camera_movement_timer.stop()
                self.camera_movement_timer = None
            self.animation_active = False
        except Exception as e:
            pass
