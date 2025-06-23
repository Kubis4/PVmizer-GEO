#!/usr/bin/env python3
"""
Enhanced Drawing Area - Handles all mouse events and drawing operations
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QTransform, QPolygonF
import math

class EnhancedDrawingArea(QWidget):
    """Enhanced drawing area with right-click angle forcing and comprehensive drawing"""
    
    def __init__(self, parent_canvas):
        super().__init__()
        self.parent_canvas = parent_canvas
        self.background_pixmap = None
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
    
    # ===== BACKGROUND METHODS =====
    
    def set_background(self, pixmap):
        """Set background image"""
        self.background_pixmap = pixmap
        self.update()
    
    def clear_background(self):
        """Clear background image"""
        self.background_pixmap = None
        self.update()
    
    # ===== MOUSE EVENT HANDLERS =====
    
    def mousePressEvent(self, event):
        """Handle mouse press - add points, drag, or force angles"""
        if event.button() == Qt.LeftButton:
            # Check if clicking on existing point for dragging
            clicked_point_index = self._find_point_at_position(event.pos())
            
            if clicked_point_index is not None:
                # Start dragging existing point
                self.parent_canvas.dragging_point = clicked_point_index
                screen_point = self._drawing_to_screen(self.parent_canvas.points[clicked_point_index])
                self.parent_canvas.drag_offset = event.pos() - screen_point
                self.parent_canvas._update_status()
                self.setCursor(Qt.ClosedHandCursor)
                return
            
            # Not clicking on point - add new point (if not complete)
            if not self.parent_canvas.is_complete:
                draw_pos = self._screen_to_drawing(event.pos())
                
                # Apply right angle snapping if we have 2+ points
                if (len(self.parent_canvas.points) >= 2 and 
                    self.parent_canvas.angle_snap_enabled):
                    draw_pos = self.parent_canvas.snap_to_right_angle(
                        draw_pos, 
                        self.parent_canvas.points[-1], 
                        self.parent_canvas.points[-2]
                    )
                
                # Add new point
                self.parent_canvas.points.append(draw_pos)
                self.parent_canvas.is_drawing = True
                self.parent_canvas._update_status()
                self.update()
                print(f"✓ Point {len(self.parent_canvas.points)} added")
        
        elif event.button() == Qt.RightButton:
            # Right-click: Force right angle at clicked point
            clicked_point_index = self._find_point_at_position(event.pos())
            if clicked_point_index is not None and self.parent_canvas.is_complete:
                self.parent_canvas.force_right_angle_at_point(clicked_point_index)
        
        elif event.button() == Qt.MiddleButton:
            # Start panning
            self.parent_canvas.is_panning = True
            self.parent_canvas.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click - complete polygon and optionally generate 3D model"""
        if event.button() == Qt.LeftButton and len(self.parent_canvas.points) >= 3 and not self.parent_canvas.is_complete:
            # Complete the polygon
            self.parent_canvas.is_complete = True
            self.parent_canvas.is_drawing = False
            
            # Emit polygon completion signal
            if hasattr(self.parent_canvas, 'polygon_completed'):
                self.parent_canvas.polygon_completed.emit(self.parent_canvas.points.copy())
            
            # Check if auto-3D generation is enabled
            if getattr(self.parent_canvas, 'auto_generate_3d', False):
                # Auto-generate 3D model
                success = self.parent_canvas.create_3d_model(
                    source="double_click_auto",
                    emit_signal=True
                )
                
                if success:
                    print("✅ 3D model auto-generated from double-click")
                else:
                    print("⚠️ Auto 3D generation failed, polygon still complete")
            else:
                # Just complete polygon, no auto-generation
                print("✓ Polygon completed - Use 'Generate 3D Model' button for 3D visualization")
            
            self.parent_canvas._update_status()
            self.update()
            print(f"✓ Polygon completed with {len(self.parent_canvas.points)} points")
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement - pan, drag, or update preview"""
        if self.parent_canvas.is_panning:
            # Pan view
            delta = event.pos() - self.parent_canvas.last_pan_point
            self.parent_canvas.pan_offset += delta
            self.parent_canvas.last_pan_point = event.pos()
            self.update()
            
        elif self.parent_canvas.dragging_point is not None:
            # Drag point
            new_screen_pos = event.pos() - self.parent_canvas.drag_offset
            new_drawing_pos = self._screen_to_drawing(new_screen_pos)
            self.parent_canvas.points[self.parent_canvas.dragging_point] = new_drawing_pos
            self.update()
            
        else:
            # Update preview position
            mouse_pos = self._screen_to_drawing(event.pos())
            
            # Store original position before snapping
            self.parent_canvas.original_mouse_pos = mouse_pos
            
            # Apply right angle snapping to preview if enabled
            if (len(self.parent_canvas.points) >= 2 and 
                self.parent_canvas.angle_snap_enabled and
                not self.parent_canvas.is_complete):
                mouse_pos = self.parent_canvas.snap_to_right_angle(
                    mouse_pos,
                    self.parent_canvas.points[-1],
                    self.parent_canvas.points[-2]
                )
            
            self.parent_canvas.current_mouse_pos = mouse_pos
            
            # Update cursor based on what's under mouse
            if self._find_point_at_position(event.pos()) is not None:
                if self.parent_canvas.is_complete:
                    self.setCursor(Qt.PointingHandCursor)  # Different cursor for completed polygon
                else:
                    self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            
            if self.parent_canvas.is_drawing and not self.parent_canvas.is_complete:
                self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - stop dragging or panning"""
        if event.button() == Qt.LeftButton and self.parent_canvas.dragging_point is not None:
            self.parent_canvas.dragging_point = None
            self.parent_canvas._update_status()
            self.setCursor(Qt.ArrowCursor)
            
        elif event.button() == Qt.MiddleButton:
            self.parent_canvas.is_panning = False
            self.setCursor(Qt.ArrowCursor)
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        cursor_pos = event.pos()
        zoom_in = event.angleDelta().y() > 0
        factor = 1.15 if zoom_in else 1.0 / 1.15
        
        old_zoom = self.parent_canvas.zoom_factor
        self.parent_canvas.zoom_factor *= factor
        self.parent_canvas.zoom_factor = max(0.1, min(10.0, self.parent_canvas.zoom_factor))
        
        ratio = self.parent_canvas.zoom_factor / old_zoom
        new_x = int(cursor_pos.x() - (cursor_pos.x() - self.parent_canvas.pan_offset.x()) * ratio)
        new_y = int(cursor_pos.y() - (cursor_pos.y() - self.parent_canvas.pan_offset.y()) * ratio)
        self.parent_canvas.pan_offset = QPoint(new_x, new_y)
        
        self.update()
    
    # ===== COORDINATE CONVERSION =====
    
    def _find_point_at_position(self, screen_pos):
        """Find point index at screen position"""
        for i, point in enumerate(self.parent_canvas.points):
            point_screen = self._drawing_to_screen(point)
            distance = self._distance(screen_pos, point_screen)
            if distance <= self.parent_canvas.point_radius + 5:
                return i
        return None
    
    def _screen_to_drawing(self, screen_pos):
        """Convert screen coordinates to drawing coordinates"""
        x = (screen_pos.x() - self.parent_canvas.pan_offset.x()) / self.parent_canvas.zoom_factor
        y = (screen_pos.y() - self.parent_canvas.pan_offset.y()) / self.parent_canvas.zoom_factor
        return QPointF(x, y)
    
    def _drawing_to_screen(self, drawing_pos):
        """Convert drawing coordinates to screen coordinates"""
        x = int(drawing_pos.x() * self.parent_canvas.zoom_factor + self.parent_canvas.pan_offset.x())
        y = int(drawing_pos.y() * self.parent_canvas.zoom_factor + self.parent_canvas.pan_offset.y())
        return QPoint(x, y)
    
    def _distance(self, pos1, pos2):
        """Calculate distance between two points"""
        dx = pos1.x() - pos2.x()
        dy = pos1.y() - pos2.y()
        return math.sqrt(dx * dx + dy * dy)
    
    # ===== MAIN PAINT EVENT =====
    
    def paintEvent(self, event):
        """Main paint event - orchestrates all drawing"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background - CHANGED TO MEDIUM GREY
        painter.fillRect(self.rect(), QColor("#4A4A4A"))  # Medium grey background
        
        # Transform for zoom/pan
        transform = QTransform()
        transform.translate(self.parent_canvas.pan_offset.x(), self.parent_canvas.pan_offset.y())
        transform.scale(self.parent_canvas.zoom_factor, self.parent_canvas.zoom_factor)
        painter.setTransform(transform)
        
        # Draw background image
        if self.background_pixmap:
            painter.drawPixmap(0, 0, self.background_pixmap)
        
        # Reset transform for drawing overlays
        painter.resetTransform()
        
        # Draw polygon elements
        self._draw_polygon_consistently(painter)
    
    # ===== DRAWING METHODS =====
    
    def _draw_polygon_consistently(self, painter):
        """Main polygon drawing method - coordinates all drawing elements"""
        if not self.parent_canvas.points:
            return
        
        points = self.parent_canvas.points
        screen_points = [self._drawing_to_screen(p) for p in points]
        
        # Drawing order for proper layering:
        # 1\. Polygon fill (if complete)
        # 2\. All lines (completed and preview)
        # 3\. Right angle indicators
        # 4\. Dimension text
        # 5\. Points and numbers
        # 6\. Area text (if complete)
        
        # Step 1: Draw polygon fill if complete
        if self.parent_canvas.is_complete and len(screen_points) >= 3:
            self._draw_polygon_fill(painter, screen_points)
        
        # Step 2: Draw all lines
        self._draw_all_lines_consistently(painter, points, screen_points)
        
        # Step 3: Draw right angle indicators
        self._draw_right_angle_indicators(painter, points, screen_points)
        
        # Step 4: Draw dimension text
        self._draw_all_dimension_text(painter, points, screen_points)
        
        # Step 5: Draw points and numbers
        self._draw_points_and_numbers(painter, screen_points)
        
        # Step 6: Draw area if complete
        if self.parent_canvas.is_complete and len(points) >= 3:
            self._draw_area_text(painter, points, screen_points)
    
    def _draw_polygon_fill(self, painter, screen_points):
        """Draw polygon fill"""
        polygon = QPolygonF([QPointF(p.x(), p.y()) for p in screen_points])
        painter.setPen(QPen())
        painter.setBrush(QBrush(self.parent_canvas.polygon_fill))
        painter.drawPolygon(polygon)
    
    def _draw_all_lines_consistently(self, painter, points, screen_points):
        """Draw ALL lines with consistent styling"""
        
        # Create pens
        completed_pen = QPen(
            self.parent_canvas.completed_line_color,
            self.parent_canvas.line_width,
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        
        preview_pen = QPen(
            self.parent_canvas.preview_line_color,
            self.parent_canvas.line_width,
            Qt.DashLine, Qt.RoundCap, Qt.RoundJoin
        )
        
        snap_pen = QPen(
            self.parent_canvas.snap_line_color,
            self.parent_canvas.line_width,
            Qt.DashLine, Qt.RoundCap, Qt.RoundJoin
        )
        
        # Draw completed lines
        painter.setPen(completed_pen)
        for i in range(len(screen_points) - 1):
            painter.drawLine(screen_points[i], screen_points[i + 1])
        
        # Draw closing line if complete
        if self.parent_canvas.is_complete and len(screen_points) >= 3:
            painter.drawLine(screen_points[-1], screen_points[0])
        
        # Draw preview line to mouse if drawing
        elif (self.parent_canvas.is_drawing and 
              not self.parent_canvas.is_complete and 
              self.parent_canvas.current_mouse_pos and 
              len(screen_points) > 0):
            
            mouse_screen = self._drawing_to_screen(self.parent_canvas.current_mouse_pos)
            
            # Check if this would be a snapped right angle
            is_snapped = self._is_preview_snapped()
            
            # Use different color for snapped lines
            painter.setPen(snap_pen if is_snapped else preview_pen)
            painter.drawLine(screen_points[-1], mouse_screen)
            
            # Show preview closing line if >= 3 points
            if len(screen_points) >= 3:
                painter.setPen(QPen(QColor(255, 255, 0), 2, Qt.DashLine))  # Yellow dashed
                painter.drawLine(screen_points[0], mouse_screen)
    
    def _is_preview_snapped(self):
        """Check if preview line is snapped to right angle"""
        if (len(self.parent_canvas.points) >= 2 and 
            self.parent_canvas.angle_snap_enabled and
            self.parent_canvas.original_mouse_pos and
            self.parent_canvas.current_mouse_pos):
            
            # Compare original position with snapped position
            original_pos = self.parent_canvas.original_mouse_pos
            snapped_pos = self.parent_canvas.current_mouse_pos
            
            # If positions differ significantly, we have snapping
            distance_diff = math.sqrt(
                (original_pos.x() - snapped_pos.x()) ** 2 + 
                (original_pos.y() - snapped_pos.y()) ** 2
            )
            return distance_diff > 2  # 2 pixel threshold
        
        return False
    
    def _draw_right_angle_indicators(self, painter, points, screen_points):
        """Draw small squares at right angle corners"""
        if len(screen_points) < 3:
            return
        
        painter.setPen(QPen(self.parent_canvas.right_angle_color, 2))
        painter.setBrush(QBrush())
        
        size = self.parent_canvas.right_angle_size
        
        # Check angles at each vertex
        for i in range(len(points)):
            if len(points) < 3:
                continue
                
            # Get three consecutive points
            if self.parent_canvas.is_complete:
                # In complete polygon, check all angles including wrap-around
                p1 = points[(i - 1) % len(points)]
                p2 = points[i]
                p3 = points[(i + 1) % len(points)]
            else:
                # In incomplete polygon, only check internal angles
                if i == 0 or i == len(points) - 1:
                    continue
                p1 = points[i - 1]
                p2 = points[i]
                p3 = points[i + 1]
            
            # Check if this is a right angle
            if self._is_right_angle(p1, p2, p3):
                # Draw right angle indicator
                center = screen_points[i]
                self._draw_right_angle_square(painter, center, p1, p2, p3, size)
        
        # Draw preview right angle indicator if snapping
        if (self.parent_canvas.is_drawing and 
            not self.parent_canvas.is_complete and
            len(points) >= 2 and
            self.parent_canvas.current_mouse_pos and
            self.parent_canvas.angle_snap_enabled):
            
            # Check if preview would create right angle
            p1 = points[-2]
            p2 = points[-1]
            p3 = self.parent_canvas.current_mouse_pos
            
            if self._is_right_angle(p1, p2, p3):
                center = screen_points[-1]
                # Draw with lighter color for preview
                painter.setPen(QPen(QColor(255, 150, 150), 2))
                self._draw_right_angle_square(painter, center, p1, p2, p3, size)
    
    def _is_right_angle(self, p1, p2, p3):
        """Check if angle at p2 between p1-p2-p3 is approximately 90 degrees"""
        v1 = QPointF(p1.x() - p2.x(), p1.y() - p2.y())
        v2 = QPointF(p3.x() - p2.x(), p3.y() - p2.y())
        
        angle = self.parent_canvas.calculate_angle_between_vectors(v1, v2)
        return abs(angle - 90) <= self.parent_canvas.angle_tolerance
    
    def _draw_right_angle_square(self, painter, center_screen, p1, p2, p3, size):
        """Draw a small square to indicate right angle"""
        # Calculate vectors from center point
        v1 = QPointF(p1.x() - p2.x(), p1.y() - p2.y())
        v2 = QPointF(p3.x() - p2.x(), p3.y() - p2.y())
        
        # Normalize vectors
        v1_mag = math.sqrt(v1.x() ** 2 + v1.y() ** 2)
        v2_mag = math.sqrt(v2.x() ** 2 + v2.y() ** 2)
        
        if v1_mag == 0 or v2_mag == 0:
            return
        
        v1_norm = QPointF(v1.x() / v1_mag, v1.y() / v1_mag)
        v2_norm = QPointF(v2.x() / v2_mag, v2.y() / v2_mag)
        
        # Scale vectors for square size
        scale = size / self.parent_canvas.zoom_factor
        v1_scaled = QPointF(v1_norm.x() * scale, v1_norm.y() * scale)
        v2_scaled = QPointF(v2_norm.x() * scale, v2_norm.y() * scale)
        
        # Calculate square corners in drawing coordinates
        corner1 = QPointF(p2.x() + v1_scaled.x(), p2.y() + v1_scaled.y())
        corner2 = QPointF(p2.x() + v1_scaled.x() + v2_scaled.x(), p2.y() + v1_scaled.y() + v2_scaled.y())
        corner3 = QPointF(p2.x() + v2_scaled.x(), p2.y() + v2_scaled.y())
        
        # Convert to screen coordinates
        corner1_screen = self._drawing_to_screen(corner1)
        corner2_screen = self._drawing_to_screen(corner2)
        corner3_screen = self._drawing_to_screen(corner3)
        
        # Draw the square
        painter.drawLine(center_screen, corner1_screen)
        painter.drawLine(corner1_screen, corner2_screen)
        painter.drawLine(corner2_screen, corner3_screen)
        painter.drawLine(corner3_screen, center_screen)
    
    def _draw_all_dimension_text(self, painter, points, screen_points):
        """Draw ALL dimension text above lines"""
        
        # Completed segments
        for i in range(len(screen_points) - 1):
            self._draw_dimension_text(painter, points[i], points[i + 1], 
                                    screen_points[i], screen_points[i + 1])
        
        # Closing dimension if complete
        if self.parent_canvas.is_complete and len(screen_points) >= 3:
            self._draw_dimension_text(painter, points[-1], points[0], 
                                    screen_points[-1], screen_points[0])
        
        # Preview dimension to mouse
        elif (self.parent_canvas.is_drawing and 
              not self.parent_canvas.is_complete and 
              self.parent_canvas.current_mouse_pos and 
              len(screen_points) > 0):
            
            mouse_screen = self._drawing_to_screen(self.parent_canvas.current_mouse_pos)
            self._draw_dimension_text(painter, points[-1], self.parent_canvas.current_mouse_pos, 
                                    screen_points[-1], mouse_screen)
            
            # Preview closing dimension if >= 3 points
            if len(screen_points) >= 3:
                self._draw_dimension_text(painter, points[0], self.parent_canvas.current_mouse_pos, 
                                        screen_points[0], mouse_screen, preview_closing=True)
    
    def _draw_dimension_text(self, painter, point1, point2, screen1, screen2, preview_closing=False):
        """Draw dimension text above a line"""
        # Calculate distance
        dx = point2.x() - point1.x()
        dy = point2.y() - point1.y()
        pixel_dist = math.sqrt(dx * dx + dy * dy)
        real_dist = pixel_dist * self.parent_canvas.scale_factor
        
        # Format text
        if real_dist >= 1.0:
            text = f"{real_dist:.2f}m"
        else:
            text = f"{real_dist * 100:.0f}cm"
        
        # Add preview indicator
        if preview_closing:
            text = f"({text})"  # Parentheses for preview closing
        
        # Calculate line midpoint
        mid_x = (screen1.x() + screen2.x()) / 2
        mid_y = (screen1.y() + screen2.y()) / 2
        
        # Calculate perpendicular offset to place text ABOVE line
        line_angle = math.atan2(dy, dx)
        offset_distance = 20
        perp_angle = line_angle + math.pi/2
        
        text_x = int(mid_x + math.cos(perp_angle) * offset_distance)
        text_y = int(mid_y + math.sin(perp_angle) * offset_distance)
        
        # Draw text with background
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        text_rect = painter.fontMetrics().boundingRect(text)
        
        padding = 6
        bg_rect = text_rect.adjusted(-padding, -padding//2, padding, padding//2)
        bg_rect.moveCenter(QPoint(text_x, text_y))
        
        # Background color (lighter for preview)
        bg_color = self.parent_canvas.text_bg_color if not preview_closing else QColor(120, 120, 120)
        painter.setPen(QPen())
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush())
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        # White text
        painter.setPen(QPen(self.parent_canvas.text_color, 1))
        painter.drawText(text_x - text_rect.width() // 2, 
                        text_y + text_rect.height() // 2 - 1, text)
    
    def _draw_points_and_numbers(self, painter, screen_points):
        """Draw points with numbers"""
        for i, screen_point in enumerate(screen_points):
            # Highlight dragging point
            if i == self.parent_canvas.dragging_point:
                painter.setPen(QPen(QColor(255, 100, 100), 4))  # Red highlight
                painter.setBrush(QBrush())
                painter.drawEllipse(screen_point, self.parent_canvas.point_radius + 5, 
                                  self.parent_canvas.point_radius + 5)
            
            # Special highlight for completed polygon points (clickable for right angles)
            if self.parent_canvas.is_complete:
                painter.setPen(QPen(QColor(0, 200, 0), 4))  # Green highlight for clickable
                painter.setBrush(QBrush())
                painter.drawEllipse(screen_point, self.parent_canvas.point_radius + 3, 
                                  self.parent_canvas.point_radius + 3)
            
            # Point circle
            painter.setPen(QPen(QColor(0, 0, 0), 3))
            painter.setBrush(QBrush(self.parent_canvas.point_color))
            painter.drawEllipse(screen_point, self.parent_canvas.point_radius, 
                              self.parent_canvas.point_radius)
            
            # Number with background
            number_text = str(i + 1)
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            text_rect = painter.fontMetrics().boundingRect(number_text)
            
            padding_h, padding_v = 8, 6
            number_bg_rect = text_rect.adjusted(-padding_h, -padding_v, padding_h, padding_v)
            number_bg_rect.moveCenter(QPoint(screen_point.x(), 
                                           screen_point.y() - self.parent_canvas.point_radius - 20))
            
            # Dark grey background
            painter.setPen(QPen())
            painter.setBrush(QBrush(self.parent_canvas.number_bg_color))
            painter.drawRoundedRect(number_bg_rect, 5, 5)
            
            painter.setPen(QPen(QColor(40, 40, 40), 1))
            painter.setBrush(QBrush())
            painter.drawRoundedRect(number_bg_rect, 5, 5)
            
            # White text
            painter.setPen(QPen(self.parent_canvas.number_text_color, 1))
            text_x = number_bg_rect.center().x() - text_rect.width() // 2
            text_y = number_bg_rect.center().y() + text_rect.height() // 2 - 2
            painter.drawText(text_x, text_y, number_text)
    
    def _draw_area_text(self, painter, points, screen_points):
        """Draw area text in polygon center"""
        # Calculate area
        area = self.parent_canvas.calculate_polygon_area()
        
        # Find centroid
        centroid_x = sum(p.x() for p in screen_points) // len(screen_points)
        centroid_y = sum(p.y() for p in screen_points) // len(screen_points)
        
        # Draw area text
        area_text = f"Area: {area:.2f}m²"
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        text_rect = painter.fontMetrics().boundingRect(area_text)
        
        padding = 8
        bg_rect = text_rect.adjusted(-padding, -padding//2, padding, padding//2)
        bg_rect.moveCenter(QPoint(centroid_x, centroid_y))
        
        # Background
        painter.setPen(QPen())
        painter.setBrush(QBrush(self.parent_canvas.text_bg_color))
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush())
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        # White text
        painter.setPen(QPen(self.parent_canvas.text_color, 1))
        painter.drawText(centroid_x - text_rect.width() // 2, 
                        centroid_y + text_rect.height() // 2 - 1, area_text)