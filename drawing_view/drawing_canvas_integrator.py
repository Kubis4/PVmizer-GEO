#!/usr/bin/env python3
"""
FIXED Drawing Canvas Integrator - Handles QPointF properly and provides complete functionality
"""
from PyQt5.QtCore import QObject, pyqtSignal

class DrawingCanvasIntegrator(QObject):
    """Fixed integrator that properly handles QPointF objects and all canvas operations"""
    
    # Helper signals for main window
    status_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, main_window, left_panel, canvas_manager, model_generator):
        super().__init__()
        
        self.main_window = main_window
        self.left_panel = left_panel
        self.canvas_manager = canvas_manager
        self.model_generator = model_generator
        
        # State tracking
        self.current_scale = 0.05
        self.angle_snap_enabled = True
        self.drawing_status = {
            'boundary_complete': False,
            'boundary_points': 0,
            'ridge_lines': 0,
            'area_sqm': 0,
            'perimeter': 0,
            'ready_for_generation': False
        }
        
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup all drawing-related signal connections"""
        try:
            # ===== LEFT PANEL TO CANVAS CONNECTIONS =====
            if hasattr(self.left_panel, 'scale_changed'):
                self.left_panel.scale_changed.connect(self.handle_scale_change)
            
            if hasattr(self.left_panel, 'angle_snap_toggled'):
                self.left_panel.angle_snap_toggled.connect(self.handle_angle_snap_toggle)
            
            if hasattr(self.left_panel, 'clear_drawing_requested'):
                self.left_panel.clear_drawing_requested.connect(self.handle_clear_drawing)
            
            if hasattr(self.left_panel, 'undo_requested'):
                self.left_panel.undo_requested.connect(self.handle_undo_request)
            
            if hasattr(self.left_panel, 'generate_model_requested'):
                self.left_panel.generate_model_requested.connect(self.generate_enhanced_model)
            
            if hasattr(self.left_panel, 'export_model_requested'):
                self.left_panel.export_model_requested.connect(self.handle_export_request)
            
            # Additional view controls
            if hasattr(self.left_panel, 'zoom_fit_requested'):
                self.left_panel.zoom_fit_requested.connect(self.handle_zoom_fit)
            
            if hasattr(self.left_panel, 'zoom_reset_requested'):
                self.left_panel.zoom_reset_requested.connect(self.handle_zoom_reset)
            
            if hasattr(self.left_panel, 'background_opacity_changed'):
                self.left_panel.background_opacity_changed.connect(self.handle_opacity_change)
            
            if hasattr(self.left_panel, 'force_right_angle_requested'):
                self.left_panel.force_right_angle_requested.connect(self.handle_force_right_angle)
            
            # ===== CANVAS MANAGER CONNECTIONS =====
            if hasattr(self.canvas_manager, 'boundary_completed'):
                self.canvas_manager.boundary_completed.connect(self.handle_boundary_completed)
            
            if hasattr(self.canvas_manager, 'area_calculated'):
                self.canvas_manager.area_calculated.connect(self.handle_area_calculated)
            
            if hasattr(self.canvas_manager, 'drawing_completed'):
                self.canvas_manager.drawing_completed.connect(self.handle_drawing_completed)
            
        except Exception as e:
            pass
    
    # =======================================
    # **DRAWING CONTROL HANDLERS**
    # =======================================
    
    def handle_scale_change(self, scale_factor):
        """Handle scale change from left panel"""
        try:
            self.current_scale = scale_factor
            
            # Apply to canvas manager
            success = False
            
            if hasattr(self.canvas_manager, 'set_canvas_scale'):
                self.canvas_manager.set_canvas_scale(scale_factor)
                success = True
            
            canvas = self.get_current_canvas()
            if canvas:
                if hasattr(canvas, 'set_scale'):
                    canvas.set_scale(scale_factor)
                    success = True
                elif hasattr(canvas, 'scale_factor'):
                    canvas.scale_factor = scale_factor
                    canvas.update()
                    success = True
            
            if success:
                self.status_updated.emit(f"Scale set to {scale_factor} m/pixel")
                
        except Exception as e:
            self.error_occurred.emit(f"Error handling scale change: {e}")
    
    def handle_angle_snap_toggle(self, enabled):
        """Handle angle snap toggle from left panel"""
        try:
            self.angle_snap_enabled = enabled
            
            # Apply to canvas
            success = False
            
            canvas = self.get_current_canvas()
            if canvas:
                if hasattr(canvas, 'set_angle_snap'):
                    canvas.set_angle_snap(enabled)
                    success = True
                elif hasattr(canvas, 'angle_snap_enabled'):
                    canvas.angle_snap_enabled = enabled
                    success = True
            
            if success:
                status = "enabled" if enabled else "disabled"
                self.status_updated.emit(f"90° angle snap {status}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error handling angle snap: {e}")
    
    def handle_undo_request(self):
        """Handle undo request from left panel"""
        try:
            # Try different undo methods
            success = False
            
            canvas = self.get_current_canvas()
            if canvas:
                if hasattr(canvas, 'undo_point'):
                    canvas.undo_point()
                    success = True
                elif hasattr(canvas, 'undo_last_point'):
                    canvas.undo_last_point()
                    success = True
                elif hasattr(canvas, 'remove_last_point'):
                    canvas.remove_last_point()
                    success = True
            
            if success:
                self.status_updated.emit("Last point removed")
                self._update_measurements_after_change()
            else:
                self.status_updated.emit("Nothing to undo")
                
        except Exception as e:
            self.error_occurred.emit(f"Error handling undo: {e}")
    
    def handle_clear_drawing(self):
        """Handle clear drawing request from left panel"""
        try:
            # Try different clear methods
            success = False
            
            if hasattr(self.canvas_manager, 'clear_drawing'):
                self.canvas_manager.clear_drawing()
                success = True
            else:
                canvas = self.get_current_canvas()
                if canvas:
                    if hasattr(canvas, 'clear_all'):
                        canvas.clear_all()
                        success = True
                    elif hasattr(canvas, 'clear_drawing'):
                        canvas.clear_drawing()
                        success = True
            
            if success:
                self.status_updated.emit("Drawing cleared")
                
                # Disable generate button
                if hasattr(self.left_panel, 'drawing_tab'):
                    if hasattr(self.left_panel.drawing_tab, 'disable_generate_button'):
                        self.left_panel.drawing_tab.disable_generate_button()
                
                # Reset drawing status
                self.drawing_status = {
                    'boundary_complete': False,
                    'boundary_points': 0,
                    'ridge_lines': 0,
                    'area_sqm': 0,
                    'perimeter': 0,
                    'ready_for_generation': False
                }
                
                self.update_left_panel_status()
                
        except Exception as e:
            self.error_occurred.emit(f"Error handling clear drawing: {e}")
    
    # =======================================
    # **VIEW CONTROL HANDLERS**
    # =======================================
    
    def handle_zoom_fit(self):
        """Handle zoom fit request"""
        try:
            canvas = self.get_current_canvas()
            if canvas:
                if hasattr(canvas, 'zoom_fit'):
                    canvas.zoom_fit()
                    self.status_updated.emit("View fitted to content")
                elif hasattr(canvas, 'fit_view'):
                    canvas.fit_view()
                    self.status_updated.emit("View fitted to content")
            
        except Exception as e:
            pass
    
    def handle_zoom_reset(self):
        """Handle zoom reset request"""
        try:
            canvas = self.get_current_canvas()
            if canvas:
                # Reset zoom properties
                if hasattr(canvas, 'zoom_factor'):
                    canvas.zoom_factor = 1.0
                if hasattr(canvas, 'pan_offset'):
                    canvas.pan_offset.setX(0)
                    canvas.pan_offset.setY(0)
                if hasattr(canvas, 'scale'):
                    canvas.scale = 1.0
                
                # Update canvas
                canvas.update()
                self.status_updated.emit("View reset to default")
            
        except Exception as e:
            pass
    
    def handle_opacity_change(self, opacity):
        """Handle background opacity change"""
        try:
            canvas = self.get_current_canvas()
            if canvas:
                # Set opacity property
                if hasattr(canvas, 'background_opacity'):
                    canvas.background_opacity = opacity
                elif hasattr(canvas, '_background_opacity'):
                    canvas._background_opacity = opacity
                else:
                    # Add the property if it doesn't exist
                    canvas._background_opacity = opacity
                
                canvas.update()
                self.status_updated.emit(f"Background opacity: {opacity:.0%}")
            
        except Exception as e:
            pass
    
    def handle_force_right_angle(self, point_index):
        """Handle force right angle request"""
        try:
            canvas = self.get_current_canvas()
            if canvas:
                if hasattr(canvas, 'force_right_angle_at_point'):
                    success = canvas.force_right_angle_at_point(point_index)
                    if success:
                        self.status_updated.emit(f"Right angle forced at point {point_index + 1}")
                        self.update_left_panel_status()
                    else:
                        self.status_updated.emit("Failed to force right angle")
            
        except Exception as e:
            pass
    
    # =======================================
    # **MODEL GENERATION**
    # =======================================
    
    def generate_enhanced_model(self):
        """Generate enhanced 3D model"""
        try:
            # Get drawing points from canvas
            points = []
            canvas = self.get_current_canvas()
            
            if canvas and hasattr(canvas, 'points'):
                points = canvas.points.copy()
            elif hasattr(self.canvas_manager, 'get_drawing_points'):
                points = self.canvas_manager.get_drawing_points()
            
            if not points or len(points) < 3:
                error_msg = f"Need at least 3 points to generate model. Found {len(points)} points."
                self.error_occurred.emit(error_msg)
                return False
            
            # Convert QPointF objects to safe format
            safe_points = []
            for point in points:
                if hasattr(point, 'x') and hasattr(point, 'y'):
                    safe_points.append((point.x(), point.y()))
                elif isinstance(point, (tuple, list)) and len(point) >= 2:
                    safe_points.append((float(point[0]), float(point[1])))
            
            if len(safe_points) < 3:
                error_msg = "Invalid point data for model generation"
                self.error_occurred.emit(error_msg)
                return False
            
            # Use canvas manager method if available
            if hasattr(self.canvas_manager, 'generate_model_from_button'):
                success = self.canvas_manager.generate_model_from_button()
                if success:
                    self.status_updated.emit("3D model generated!")
                    return True
                else:
                    self.error_occurred.emit("Model generation failed")
                    return False
            
            # Fallback: Try to generate directly
            if canvas and hasattr(canvas, 'create_3d_model'):
                success = canvas.create_3d_model(points)
                if success:
                    self.status_updated.emit("3D model generated!")
                    return True
            
            self.error_occurred.emit("No model generation method found")
            return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error in model generation: {e}")
            return False
    
    def handle_export_request(self):
        """Handle export request"""
        try:
            if self.model_generator and hasattr(self.model_generator, 'export_model'):
                self.model_generator.export_model()
                self.status_updated.emit("Export initiated...")
            else:
                self.error_occurred.emit("Export functionality not available")
                
        except Exception as e:
            self.error_occurred.emit(f"Error handling export: {e}")
    
    # =======================================
    # **STATUS AND STATE MANAGEMENT**
    # =======================================
    
    def handle_boundary_completed(self, boundary_points):
        """Handle boundary completion - FIXED QPointF handling"""
        try:
            # Convert QPointF objects to safe format for counting
            point_count = 0
            valid_points = []
            
            if boundary_points:
                for point in boundary_points:
                    if point is not None:
                        point_count += 1
                        # Convert QPointF to tuple for measurements
                        if hasattr(point, 'x') and hasattr(point, 'y'):
                            valid_points.append((point.x(), point.y()))
                        elif isinstance(point, (tuple, list)) and len(point) >= 2:
                            valid_points.append((float(point[0]), float(point[1])))
            
            self.drawing_status.update({
                'boundary_complete': point_count >= 3,
                'boundary_points': point_count,
                'ready_for_generation': point_count >= 3
            })
            
            # Enable generate button if we have enough points
            if point_count >= 3:
                if hasattr(self.left_panel, 'drawing_tab'):
                    if hasattr(self.left_panel.drawing_tab, 'enable_generate_button'):
                        self.left_panel.drawing_tab.enable_generate_button()
            
            # Calculate area safely
            if len(valid_points) >= 3:
                area = self._safe_calculate_area(valid_points)
                perimeter = self._safe_calculate_perimeter(valid_points)
                
                self.drawing_status.update({
                    'area_sqm': area,
                    'perimeter': perimeter
                })
            
            self.update_left_panel_status()
            
        except Exception as e:
            # Silent error handling - don't spam logs
            pass
    
    def handle_area_calculated(self, area_sqm, area_text):
        """Handle area calculation"""
        try:
            self.drawing_status.update({
                'area_sqm': area_sqm,
                'area_text': area_text
            })
            
            # Update left panel if method exists
            if hasattr(self.left_panel, 'update_area_display'):
                self.left_panel.update_area_display(area_sqm, area_text)
            
            self.update_left_panel_status()
            
        except Exception as e:
            pass
    
    def handle_drawing_completed(self, drawing_points):
        """Handle drawing completion"""
        try:
            # Convert points safely
            point_count = 0
            if drawing_points:
                for point in drawing_points:
                    if point is not None:
                        point_count += 1
            
            self.drawing_status.update({
                'drawing_complete': True,
                'total_points': point_count,
                'ready_for_generation': point_count >= 3
            })
            
            # Enable generate button
            if point_count >= 3:
                if hasattr(self.left_panel, 'drawing_tab'):
                    if hasattr(self.left_panel.drawing_tab, 'enable_generate_button'):
                        self.left_panel.drawing_tab.enable_generate_button()
            
            self.update_left_panel_status()
            
        except Exception as e:
            pass
    
    def update_left_panel_status(self):
        """Update left panel with current status"""
        try:
            # Update polygon info if available
            if hasattr(self.left_panel, 'update_polygon_info'):
                measurements = {
                    'points': self.drawing_status.get('boundary_points', 0),
                    'area': self.drawing_status.get('area_sqm', 0),
                    'perimeter': self.drawing_status.get('perimeter', 0),
                    'is_complete': self.drawing_status.get('boundary_complete', False)
                }
                self.left_panel.update_polygon_info(measurements)
            
            # Update drawing progress if available
            if hasattr(self.left_panel, 'update_drawing_progress'):
                status_parts = []
                
                if self.drawing_status.get('boundary_points', 0) > 0:
                    status_parts.append(f"Boundary: {self.drawing_status['boundary_points']} points")
                
                if self.drawing_status.get('ridge_lines', 0) > 0:
                    status_parts.append(f"Ridges: {self.drawing_status['ridge_lines']}")
                
                if self.drawing_status.get('area_sqm', 0) > 0:
                    status_parts.append(f"Area: {self.drawing_status['area_sqm']:.1f}m²")
                
                status_text = ", ".join(status_parts) if status_parts else "No drawing"
                self.left_panel.update_drawing_progress(status_text)
                
        except Exception as e:
            pass
    
    def _update_measurements_after_change(self):
        """Update measurements after point changes"""
        try:
            canvas = self.get_current_canvas()
            if canvas and hasattr(canvas, 'points'):
                points = canvas.points
                
                # Convert points safely
                valid_points = []
                for point in points:
                    if hasattr(point, 'x') and hasattr(point, 'y'):
                        valid_points.append((point.x(), point.y()))
                
                # Update UI
                if hasattr(self.left_panel, 'update_polygon_info'):
                    measurements = {
                        'points': len(valid_points),
                        'is_complete': len(valid_points) >= 3,
                        'area': self._safe_calculate_area(valid_points),
                        'perimeter': self._safe_calculate_perimeter(valid_points)
                    }
                    
                    self.left_panel.update_polygon_info(measurements)
                
                # Update button state
                if len(valid_points) >= 3:
                    if hasattr(self.left_panel, 'drawing_tab'):
                        if hasattr(self.left_panel.drawing_tab, 'enable_generate_button'):
                            self.left_panel.drawing_tab.enable_generate_button()
                else:
                    if hasattr(self.left_panel, 'drawing_tab'):
                        if hasattr(self.left_panel.drawing_tab, 'disable_generate_button'):
                            self.left_panel.drawing_tab.disable_generate_button()
                            
        except Exception as e:
            pass
    
    def _safe_calculate_area(self, points):
        """Safely calculate polygon area"""
        try:
            if len(points) < 3:
                return 0.0
            
            area = 0.0
            for i in range(len(points)):
                j = (i + 1) % len(points)
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            
            area = abs(area) / 2.0
            # Apply scale factor
            real_area = area * (self.current_scale ** 2)
            return real_area
            
        except Exception as e:
            return 0.0
    
    def _safe_calculate_perimeter(self, points):
        """Safely calculate polygon perimeter"""
        try:
            if len(points) < 2:
                return 0.0
            
            perimeter = 0.0
            for i in range(len(points)):
                j = (i + 1) % len(points)
                dx = points[j][0] - points[i][0]
                dy = points[j][1] - points[i][1]
                distance = (dx * dx + dy * dy) ** 0.5
                perimeter += distance
            
            # Apply scale factor
            real_perimeter = perimeter * self.current_scale
            return real_perimeter
            
        except Exception as e:
            return 0.0
    
    # =======================================
    # **UTILITY METHODS**
    # =======================================
    
    def get_current_canvas(self):
        """Get the current drawing canvas"""
        try:
            # Try canvas manager first
            if hasattr(self.canvas_manager, 'get_canvas'):
                canvas = self.canvas_manager.get_canvas()
                if canvas:
                    return canvas
            
            if hasattr(self.canvas_manager, 'drawing_canvas'):
                return self.canvas_manager.drawing_canvas
            
            return None
            
        except Exception as e:
            return None
    
    def get_drawing_status(self):
        """Get current drawing status"""
        return self.drawing_status.copy()
    
    def get_current_scale(self):
        """Get current scale factor"""
        return self.current_scale
    
    def get_status(self):
        """Get integrator status for debugging"""
        return {
            'scale': self.current_scale,
            'angle_snap': self.angle_snap_enabled,
            'drawing_status': self.drawing_status,
            'connections_active': True
        }
    
    def set_drawing_mode(self, mode):
        """Set drawing mode"""
        try:
            canvas = self.get_current_canvas()
            if canvas and hasattr(canvas, 'set_drawing_mode'):
                canvas.set_drawing_mode(mode)
                self.status_updated.emit(f"Drawing mode: {mode}")
        except Exception as e:
            pass
    
    def cleanup(self):
        """Cleanup integrator resources"""
        try:
            self.drawing_status.clear()
            self.current_scale = 0.05
            self.angle_snap_enabled = True
        except Exception as e:
            pass