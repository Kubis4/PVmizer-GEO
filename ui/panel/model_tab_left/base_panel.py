#!/usr/bin/env python3
"""
panel/3D_model_tab/base_panel.py
Base panel class with common functionality for 3D model tab
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QTimer
import calendar
from datetime import datetime

# Import solar calculations with multiple fallback attempts
try:
    from solar_system.solar_calculations import SolarCalculations
except ImportError:
    try:
        from solar_system.solar_calculations import SolarCalculations
    except ImportError:
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            from solar_system.solar_calculations import SolarCalculations
        except ImportError:
            print("⚠️ Solar calculations module not found - using fallback calculations")
            SolarCalculations = None

# Import UI styles with fallback
try:
    from styles.ui_styles import UIStyles
except ImportError:
    try:
        from ...styles.ui_styles import UIStyles
    except ImportError:
        print("⚠️ UI styles not found - using fallback styles")
        # Fallback UIStyles class
        class UIStyles:
            GROUP_BOX_STYLE = """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                }
            """

class BasePanelWidget(QWidget):
    """Base class for 3D model tab panel widgets with common functionality"""
    
    # Common signals
    solar_parameter_changed = pyqtSignal(str, object)
    export_model_requested = pyqtSignal()
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Common state
        self.current_month = 6  # June (summer)
        self.current_day = 21   # Summer solstice
        self.current_hour = 12
        self.current_minute = 0
        self.latitude = 40.7128  # New York City
        self.longitude = -74.0060
        self.weather_factor = 1.0
        
        print("✅ BasePanelWidget initialized with styles import")
    
    def _get_current_time_decimal(self):
        """Get current time as decimal hours (e.g., 12.25 for 12:15)"""
        return self.current_hour + (self.current_minute / 60.0)
    
    def _get_day_of_year(self):
        """Convert month/day to day of year"""
        try:
            if SolarCalculations:
                return SolarCalculations.day_of_year_from_month_day(self.current_month, self.current_day)
            else:
                # Fallback calculation
                date_obj = datetime(2024, self.current_month, self.current_day)
                return date_obj.timetuple().tm_yday
        except ValueError:
            return 1
    
    def _get_model_tab(self):
        """Get model tab from tabs/ directory"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                tab_count = self.main_window.content_tabs.count()
                for i in range(tab_count):
                    tab_text = self.main_window.content_tabs.tabText(i).lower()
                    if 'model' in tab_text or '3d' in tab_text:
                        return self.main_window.content_tabs.widget(i)
                
                # If no model tab found, try last tab
                if tab_count > 0:
                    return self.main_window.content_tabs.widget(tab_count - 1)
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting model tab: {e}")
            return None
    
    def _get_current_roof(self):
        """Get current roof from roof manager or model tab"""
        try:
            # Try roof generation manager first
            if hasattr(self.main_window, 'roof_generation_manager'):
                roof_manager = self.main_window.roof_generation_manager
                if roof_manager and hasattr(roof_manager, 'current_roof'):
                    return roof_manager.current_roof
            
            # Try model tab
            model_tab = self._get_model_tab()
            if model_tab and hasattr(model_tab, 'current_roof'):
                return model_tab.current_roof
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting current roof: {e}")
            return None
    
    def _update_day_range(self):
        """Update day input range based on selected month"""
        try:
            if hasattr(self, 'month_combo') and hasattr(self, 'day_input') and hasattr(self, 'day_slider'):
                if self.month_combo and self.day_input and self.day_slider:
                    month = self.month_combo.currentIndex() + 1
                    
                    if SolarCalculations:
                        days_in_month = SolarCalculations.get_days_in_month(month)
                    else:
                        # Fallback
                        days_in_month = calendar.monthrange(2024, month)[1]
                    
                    # Update ranges
                    self.day_input.setMaximum(days_in_month)
                    self.day_slider.setMaximum(days_in_month)
                    
                    # Adjust current day if it's out of range
                    if self.day_input.value() > days_in_month:
                        self.day_input.setValue(days_in_month)
                        
        except Exception as e:
            print(f"❌ Error updating day range: {e}")
    
    def _update_sunrise_sunset_display(self):
        """Update sunrise/sunset display labels"""
        try:
            if hasattr(self, 'sunrise_label') and hasattr(self, 'sunset_label'):
                if self.sunrise_label and self.sunset_label:
                    day_of_year = self._get_day_of_year()
                    
                    if SolarCalculations:
                        start_time, end_time = SolarCalculations.get_time_range(self.latitude, day_of_year)
                    else:
                        # Fallback - get from model tab
                        model_tab = self._get_model_tab()
                        if model_tab and hasattr(model_tab, 'get_time_range'):
                            start_time, end_time = model_tab.get_time_range()
                        else:
                            start_time, end_time = 6.0, 18.0
                    
                    # Convert decimal hours to HH:MM format
                    sunrise_h = int(start_time)
                    sunrise_m = int((start_time - sunrise_h) * 60)
                    sunset_h = int(end_time)
                    sunset_m = int((end_time - sunset_h) * 60)
                    
                    self.sunrise_label.setText(f"🌅 Sunrise: {sunrise_h:02d}:{sunrise_m:02d}")
                    self.sunset_label.setText(f"🌇 Sunset: {sunset_h:02d}:{sunset_m:02d}")
                    
                    # Handle polar day/night
                    if start_time <= 0 and end_time >= 24:
                        self.sunrise_label.setText("🌅 Polar Day")
                        self.sunset_label.setText("🌇 No Sunset")
                    elif start_time >= 24 or end_time <= 0:
                        self.sunrise_label.setText("🌅 No Sunrise")
                        self.sunset_label.setText("🌇 Polar Night")
                        
        except Exception as e:
            print(f"❌ Error updating sunrise/sunset display: {e}")
