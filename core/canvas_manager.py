
"""
Canvas Management Module
Handles canvas operations, drawing, and measurements
"""

import numpy as np
from PyQt5.QtWidgets import QWidget


class CanvasManager:
    """Manages canvas operations and drawing functionality"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_points = []
    
    def get_drawing_points(self):
        """Get current drawing points"""
        try:
            if self.main_window._current_drawing_points:
                return self.main_window._current_drawing_points
            
            canvas = self._get_canvas()
            if canvas:
                for attr_name in ['get_drawing_points', 'points']:
                    if hasattr(canvas, attr_name):
                        attr = getattr(canvas, attr_name)
                        points = attr() if callable(attr) else attr
                        if points:
                            return points
            
            return []
        except Exception as e:
            print(f"❌ Error getting drawing points: {e}")
            return []
    
    def get_building_settings(self):
        """Get current building settings"""
        try:
            # Method 1: Get settings from left panel if available
            if self.main_window.left_panel and hasattr(self.main_window.left_panel, 'get_building_settings'):
                try:
                    settings = self.main_window.left_panel.get_building_settings()
                    print(f"🏗️ Got settings from left panel: {settings}")
                    return settings
                except Exception as e:
                    print(f"❌ Failed to get settings from left panel: {e}")
            
            # Method 2: Get settings from UI controls (if they exist)
            settings = {}
            
            try:
                if hasattr(self.main_window, 'wall_height_input') and self.main_window.wall_height_input:
                    settings['wall_height'] = self.main_window.wall_height_input.value()
                else:
                    settings['wall_height'] = 3.0
                    
                if hasattr(self.main_window, 'roof_type_combo') and self.main_window.roof_type_combo:
                    settings['roof_type'] = self.main_window.roof_type_combo.currentText()
                else:
                    settings['roof_type'] = 'Flat'
                    
                if hasattr(self.main_window, 'roof_pitch_input') and self.main_window.roof_pitch_input:
                    settings['roof_pitch'] = self.main_window.roof_pitch_input.value()
                else:
                    settings['roof_pitch'] = 15.0
                    
                # Add scale
                settings['scale'] = self.main_window._current_scale
                
                print(f"🏗️ Got settings from UI controls: {settings}")
                return settings
                
            except Exception as e:
                print(f"❌ Failed to get settings from UI controls: {e}")
            
            # Method 3: Fallback default settings
            default_settings = {
                'wall_height': 3.0, 
                'roof_type': 'Flat', 
                'roof_pitch': 15.0,
                'scale': self.main_window._current_scale
            }
            
            print(f"🏗️ Using default settings: {default_settings}")
            return default_settings
            
        except Exception as e:
            print(f"❌ Error getting building settings: {e}")
            return {'wall_height': 3.0, 'roof_type': 'Flat', 'roof_pitch': 15.0, 'scale': 0.05}
    
    def _get_canvas(self):
        """Get the active drawing canvas"""
        try:
            if self.main_window.content_tabs:
                for i in range(self.main_window.content_tabs.count()):
                    tab_widget = self.main_window.content_tabs.widget(i)
                    if tab_widget:
                        canvas = self._find_canvas_in_widget(tab_widget)
                        if canvas:
                            return canvas
            return None
        except Exception as e:
            print(f"❌ Error getting canvas: {e}")
            return None
    
    def _find_canvas_in_widget(self, widget):
        """Find canvas in a widget"""
        try:
            if self._is_canvas(widget):
                return widget
            
            for child in widget.findChildren(QWidget):
                if self._is_canvas(child):
                    return child
            
            return None
        except Exception as e:
            print(f"❌ Error finding canvas: {e}")
            return None
    
    def _is_canvas(self, widget):
        """Check if widget is a canvas"""
        return (hasattr(widget, 'get_drawing_points') or 
                'canvas' in str(type(widget)).lower() or
                hasattr(widget, 'points'))
    
    def process_captured_pixmap(self, pixmap):
        """Process captured pixmap"""
        try:
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'set_drawing_background'):
                return self.main_window.content_tabs.set_drawing_background(pixmap)
            return False
        except Exception as e:
            print(f"❌ Process pixmap failed: {e}")
            return False
    
    def update_measurements(self, points):
        """Update measurements based on points"""
        try:
            point_count = len(points) if points else 0
            
            self.main_window.current_measurements = {
                'points': point_count,
                'area': self._calculate_area(points),
                'perimeter': self._calculate_perimeter(points),
                'is_complete': True if point_count >= 3 else False
            }
            
            self._update_measurements_display()
            return True
        except Exception as e:
            print(f"❌ Update measurements failed: {e}")
            return False
    
    def _calculate_area(self, points):
        """Calculate area from points using shoelace formula"""
        try:
            if not points or len(points) < 3:
                return 0.0
            
            area = 0.0
            n = len(points)
            for i in range(n):
                j = (i + 1) % n
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            
            return abs(area) / 2.0 * (self.main_window._current_scale ** 2)
            
        except Exception as e:
            print(f"❌ Area calculation failed: {e}")
            return 0.0

    def _calculate_perimeter(self, points):
        """Calculate perimeter from points"""
        try:
            if not points or len(points) < 2:
                return 0.0
            
            perimeter = 0.0
            n = len(points)
            for i in range(n):
                j = (i + 1) % n
                dx = points[j][0] - points[i][0]
                dy = points[j][1] - points[i][1]
                perimeter += (dx*dx + dy*dy) ** 0.5
            
            return perimeter * self.main_window._current_scale
            
        except Exception as e:
            print(f"❌ Perimeter calculation failed: {e}")
            return 0.0
    
    def _update_measurements_display(self):
        """Update measurements display"""
        try:
            if hasattr(self.main_window, 'measurements_display') and self.main_window.measurements_display:
                measurements = self.main_window.current_measurements
                
                display_text = (
                    f"Points: {measurements['points']}\n"
                    f"Area: {measurements['area']:.2f} m²\n"
                    f"Perimeter: {measurements['perimeter']:.2f} m"
                )
                
                self.main_window.measurements_display.setText(display_text)
                
                # Enable generate button if polygon is complete
                if measurements['is_complete'] and hasattr(self.main_window, 'generate_btn'):
                    self.main_window.generate_btn.setEnabled(True)
            
        except Exception as e:
            print(f"❌ Update measurements display failed: {e}")
    
    def undo_last_point(self):
        """Undo last drawing point"""
        try:
            canvas = self._get_canvas()
            if canvas and hasattr(canvas, 'undo'):
                canvas.undo()
                self.update_measurements(self.get_drawing_points())
                return True
            return False
        except Exception as e:
            print(f"❌ Undo failed: {e}")
            return False
    
    def clear_drawing(self):
        """Clear current drawing"""
        try:
            # Reset workflow state in content tabs
            if self.main_window.content_tabs and hasattr(self.main_window.content_tabs, 'clear_drawing'):
                self.main_window.content_tabs.clear_drawing()
            
            # Reset measurements
            self.main_window.current_measurements = {
                'points': 0, 'area': 0.0, 'perimeter': 0.0, 'is_complete': False
            }
            
            if self.main_window.generate_btn:
                self.main_window.generate_btn.setEnabled(False)
            
            self._update_measurements_display()
            
            # Clear canvas
            canvas = self._get_canvas()
            if canvas:
                if hasattr(canvas, 'clear'):
                    canvas.clear()
                elif hasattr(canvas, 'points'):
                    canvas.points.clear()
                    if hasattr(canvas, 'update'):
                        canvas.update()
            
            return True
            
        except Exception as e:
            print(f"❌ Clear drawing failed: {e}")
            return False
    
    def is_drawing_complete(self):
        """Check if drawing is complete"""
        try:
            points = self.get_drawing_points()
            if not points or len(points) < 3:
                return False
            
            # Check if first and last points are close
            if len(points) >= 3:
                dx = points[0][0] - points[-1][0]
                dy = points[0][1] - points[-1][1]
                distance = (dx*dx + dy*dy) ** 0.5
                
                # If distance is small, consider it closed
                if distance < 10:  # Threshold in pixels
                    return True
            
            # Alternative: check if canvas has a specific flag
            canvas = self._get_canvas()
            if canvas:
                if hasattr(canvas, 'is_complete'):
                    return canvas.is_complete
                elif hasattr(canvas, 'is_polygon_complete'):
                    if callable(canvas.is_polygon_complete):
                        return canvas.is_polygon_complete()
                    else:
                        return canvas.is_polygon_complete
            
            return False
            
        except Exception as e:
            print(f"❌ Drawing completion check failed: {e}")
            return False
