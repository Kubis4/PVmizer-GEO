# tab_utilities.py
#!/usr/bin/env python3
"""
Tab Utilities - Helper methods for tab management
"""
from PyQt5.QtWidgets import QMainWindow, QWidget

class TabUtilities:
    """Utility methods for tab management and drawing points"""
    
    def __init__(self, content_tab_widget):
        self.content_tab_widget = content_tab_widget
        self.main_window = content_tab_widget.main_window
    
    def get_drawing_points(self):
        """Get points from the drawing canvas"""
        points = []
        try:
            if hasattr(self.main_window, 'canvas_manager'):
                canvas_manager = self.main_window.canvas_manager
                
                if hasattr(canvas_manager, 'get_points'):
                    points = canvas_manager.get_points()
                elif hasattr(canvas_manager, 'get_canvas'):
                    canvas = canvas_manager.get_canvas()
                    if canvas and hasattr(canvas, 'points'):
                        points = canvas.points
                elif hasattr(canvas_manager, '_canvas_instance'):
                    canvas = canvas_manager._canvas_instance
                    if canvas and hasattr(canvas, 'points'):
                        points = canvas.points
            
            if not points and hasattr(self.content_tab_widget, 'drawing_tab'):
                for child in self.content_tab_widget.drawing_tab.findChildren(QWidget):
                    if hasattr(child, 'points') and child.points:
                        points = child.points
                        break
                    elif hasattr(child, 'get_points'):
                        points = child.get_points()
                        if points:
                            break
            
            if points and len(points) > 0:
                formatted_points = []
                for point in points:
                    if hasattr(point, 'x') and hasattr(point, 'y'):
                        formatted_points.append((point.x(), point.y()))
                    elif isinstance(point, (list, tuple)) and len(point) >= 2:
                        formatted_points.append((float(point[0]), float(point[1])))
                
                return formatted_points
                
        except Exception as e:
            print(f"Error getting drawing points: {e}")
        
        return points
    
    def get_current_tab_name(self):
        """Get the name of the current tab"""
        current_index = self.content_tab_widget.currentIndex()
        return self.content_tab_widget.tabText(current_index)
    
    def switch_to_maps_tab(self):
        """Switch to Google Maps tab"""
        self.content_tab_widget.setCurrentIndex(0)
    
    def switch_to_drawing_tab(self):
        """Switch to Drawing tab"""
        self.content_tab_widget.setCurrentIndex(1)
    
    def switch_to_model_tab(self):
        """Switch to 3D Model tab"""
        self.content_tab_widget.setCurrentIndex(2)
    
    def replace_model_tab(self, new_model_widget):
        """Replace the 3D model tab with new widget"""
        try:
            # Find the 3D model tab
            for i in range(self.content_tab_widget.count()):
                tab_text = self.content_tab_widget.tabText(i)
                if "3D Model" in tab_text or "🏗️" in tab_text:
                    print(f"Replacing tab {i}: {tab_text}")
                    self.content_tab_widget.removeTab(i)
                    self.content_tab_widget.insertTab(i, new_model_widget, "🏗️ 3D Model & Solar")
                    return True
                        
            # If not found, add as new tab
            print("3D Model tab not found, adding new tab")
            self.content_tab_widget.addTab(new_model_widget, "🏗️ 3D Model & Solar")
            return True
            
        except Exception as e:
            print(f"Error replacing model tab: {e}")
            return False