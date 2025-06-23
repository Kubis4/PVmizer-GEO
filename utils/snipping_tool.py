
#!/usr/bin/env python3
"""
Enhanced Snipping Tool - COMPLETE FIXED VERSION
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QCursor, QPainterPath, QFont
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QRectF, QPointF

class SnippingTool(QDialog):
    """Enhanced dialog for selecting an area of a screenshot with better UX"""
    snip_completed = pyqtSignal(QPixmap)
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Initialize variables
        self.pixmap = None
        self.start_point = QPoint()
        self.current_point = QPoint()
        self.is_selecting = False
        
        # Enhanced settings
        self.min_selection_size = 20  # Minimum selection size
        self.selection_color = QColor(0, 150, 255)  # Blue selection
        self.overlay_color = QColor(0, 0, 0, 120)  # Semi-transparent overlay
        
        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        # Set cursor
        self.setCursor(Qt.CrossCursor)
        
        # Hide initially
        self.hide()
        
        print("✓ Enhanced Snipping Tool initialized")
    
    def start_snipping(self, widget_to_snip):
        """Start the enhanced snipping process on the given widget"""
        try:
            print(f"📸 Enhanced Snipping: Starting on {widget_to_snip.__class__.__name__}")
            
            # Take a high-quality screenshot of the widget
            self.pixmap = widget_to_snip.grab()
            
            if self.pixmap.isNull():
                print("❌ Failed to capture widget screenshot")
                return
            
            print(f"✓ Widget screenshot captured: {self.pixmap.width()}x{self.pixmap.height()}")
            
            # Calculate position - place directly over the widget
            widget_rect = widget_to_snip.rect()
            widget_pos = widget_to_snip.mapToGlobal(QPoint(0, 0))
            
            # Set the size and position to match the widget exactly
            self.setGeometry(
                widget_pos.x(),
                widget_pos.y(),
                widget_rect.width(),
                widget_rect.height()
            )
            
            # Make sure the label is sized to match the pixmap
            self.label.setFixedSize(self.pixmap.size())
            
            # Create enhanced initial display
            self._create_initial_display()
            
            # Show the dialog
            self.show()
            self.raise_()
            self.activateWindow()
            
            print("✓ Enhanced snipping dialog shown")
            
        except Exception as e:
            print(f"❌ Error starting enhanced snipping: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_initial_display(self):
        """Create enhanced initial display with instructions"""
        try:
            # Start with a copy of the original
            display = self.pixmap.copy()
            
            # Create overlay
            overlay = QPixmap(display.size())
            overlay.fill(Qt.transparent)
            
            painter = QPainter(overlay)
            
            # Fill with semi-transparent overlay
            painter.setBrush(self.overlay_color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, 0, overlay.width(), overlay.height())
            
            # Add enhanced instruction text
            self._draw_instruction_text(painter, overlay.size())
            
            painter.end()
            
            # Combine original with overlay
            final_painter = QPainter(display)
            final_painter.drawPixmap(0, 0, overlay)
            final_painter.end()
            
            # Show the enhanced display
            self.label.setPixmap(display)
            
        except Exception as e:
            print(f"❌ Error creating initial display: {e}")
    
    def _draw_instruction_text(self, painter, size):
        """Draw enhanced instruction text"""
        try:
            # Main instruction
            main_font = QFont("Arial", 18, QFont.Bold)
            painter.setFont(main_font)
            
            main_text = "Drag to select map area"
            main_rect = painter.fontMetrics().boundingRect(main_text)
            main_x = (size.width() - main_rect.width()) / 2
            main_y = (size.height() / 2) + painter.fontMetrics().ascent()
            
            # Draw main text with shadow
            painter.setPen(QColor(0, 0, 0, 200))
            painter.drawText(QPointF(main_x + 3, main_y + 3), main_text)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(QPointF(main_x, main_y), main_text)
            
            # Subtitle instruction
            sub_font = QFont("Arial", 12)
            painter.setFont(sub_font)
            
            sub_text = "Enhanced centering enabled • ESC to cancel"
            sub_rect = painter.fontMetrics().boundingRect(sub_text)
            sub_x = (size.width() - sub_rect.width()) / 2
            sub_y = main_y + 40
            
            # Draw subtitle with shadow
            painter.setPen(QColor(0, 0, 0, 180))
            painter.drawText(QPointF(sub_x + 2, sub_y + 2), sub_text)
            painter.setPen(QColor(220, 220, 220))
            painter.drawText(QPointF(sub_x, sub_y), sub_text)
            
        except Exception as e:
            print(f"❌ Error drawing instruction text: {e}")
    
    def update_display(self):
        """Update the displayed pixmap with enhanced selection overlay"""
        try:
            if not self.pixmap:
                return
                
            # Get a clean copy of the original pixmap
            display = self.pixmap.copy()
            
            # Create overlay
            overlay = QPixmap(display.size())
            overlay.fill(Qt.transparent)
            
            painter = QPainter(overlay)
            
            if self.is_selecting and not self.start_point.isNull() and not self.current_point.isNull():
                # Get selection rectangle
                selection_rect = self.get_selection_rect()
                
                if selection_rect.width() > 5 and selection_rect.height() > 5:
                    # Create enhanced selection display
                    self._draw_selection_overlay(painter, selection_rect, overlay.size())
                else:
                    # Show initial overlay if selection too small
                    painter.setBrush(self.overlay_color)
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(0, 0, overlay.width(), overlay.height())
            
            painter.end()
            
            # Combine with original
            final_painter = QPainter(display)
            final_painter.drawPixmap(0, 0, overlay)
            final_painter.end()
            
            # Set the final display
            self.label.setPixmap(display)
            
        except Exception as e:
            print(f"❌ Error updating display: {e}")
    
    def _draw_selection_overlay(self, painter, selection_rect, overlay_size):
        """Draw enhanced selection overlay"""
        try:
            # Fill everything except the selection with semi-transparent overlay
            painter.setBrush(self.overlay_color)
            painter.setPen(Qt.NoPen)
            
            # Create paths
            full_path = QPainterPath()
            full_path.addRect(QRectF(0, 0, overlay_size.width(), overlay_size.height()))
            
            selection_path = QPainterPath()
            selection_path.addRect(QRectF(selection_rect))
            
            # Subtract selection from full area
            overlay_path = full_path.subtracted(selection_path)
            painter.drawPath(overlay_path)
            
            # Draw enhanced selection border
            self._draw_selection_border(painter, selection_rect)
            
            # Draw selection info
            self._draw_selection_info(painter, selection_rect)
            
        except Exception as e:
            print(f"❌ Error drawing selection overlay: {e}")
    
    def _draw_selection_border(self, painter, selection_rect):
        """Draw enhanced selection border"""
        try:
            # Main border
            painter.setPen(QPen(self.selection_color, 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection_rect)
            
            # Inner highlight
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            inner_rect = QRect(
                selection_rect.x() + 1,
                selection_rect.y() + 1,
                selection_rect.width() - 2,
                selection_rect.height() - 2
            )
            painter.drawRect(inner_rect)
            
            # Corner indicators
            corner_size = 8
            corner_color = QColor(255, 255, 255, 200)
            painter.setPen(QPen(corner_color, 2))
            
            # Top-left corner
            painter.drawLine(
                selection_rect.x(), selection_rect.y() + corner_size,
                selection_rect.x(), selection_rect.y()
            )
            painter.drawLine(
                selection_rect.x(), selection_rect.y(),
                selection_rect.x() + corner_size, selection_rect.y()
            )
            
            # Top-right corner
            painter.drawLine(
                selection_rect.right() - corner_size, selection_rect.y(),
                selection_rect.right(), selection_rect.y()
            )
            painter.drawLine(
                selection_rect.right(), selection_rect.y(),
                selection_rect.right(), selection_rect.y() + corner_size
            )
            
            # Bottom-right corner
            painter.drawLine(
                selection_rect.right(), selection_rect.bottom() - corner_size,
                selection_rect.right(), selection_rect.bottom()
            )
            painter.drawLine(
                selection_rect.right(), selection_rect.bottom(),
                selection_rect.right() - corner_size, selection_rect.bottom()
            )
            
            # Bottom-left corner
            painter.drawLine(
                selection_rect.x() + corner_size, selection_rect.bottom(),
                selection_rect.x(), selection_rect.bottom()
            )
            painter.drawLine(
                selection_rect.x(), selection_rect.bottom(),
                selection_rect.x(), selection_rect.bottom() - corner_size
            )
            
        except Exception as e:
            print(f"❌ Error drawing selection border: {e}")
    
    def _draw_selection_info(self, painter, selection_rect):
        """Draw enhanced selection information"""
        try:
            if selection_rect.width() < 50 or selection_rect.height() < 30:
                return
            
            width = selection_rect.width()
            height = selection_rect.height()
            
            # Format dimensions text
            dimensions_text = f"{width} × {height} px"
            
            # Set font
            info_font = QFont("Arial", 11, QFont.Bold)
            painter.setFont(info_font)
            
            # Calculate text position
            text_rect = painter.fontMetrics().boundingRect(dimensions_text)
            
            # Position at top of selection, centered
            text_x = selection_rect.x() + (selection_rect.width() - text_rect.width()) / 2
            text_y = selection_rect.y() + 25
            
            # Ensure text stays within selection bounds
            if text_x < selection_rect.x() + 5:
                text_x = selection_rect.x() + 5
            if text_x + text_rect.width() > selection_rect.right() - 5:
                text_x = selection_rect.right() - text_rect.width() - 5
            
            # Draw background for text
            bg_rect = QRect(
                int(text_x - 8),
                int(text_y - text_rect.height() - 4),
                text_rect.width() + 16,
                text_rect.height() + 8
            )
            
            painter.setBrush(QColor(0, 0, 0, 180))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(bg_rect, 4, 4)
            
            # Draw text
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(int(text_x), int(text_y), dimensions_text)
            
            # Draw quality indicator if selection is good size
            if width >= 100 and height >= 100:
                quality_text = "✓ Good size for enhanced centering"
                painter.setFont(QFont("Arial", 9))
                quality_rect = painter.fontMetrics().boundingRect(quality_text)
                
                quality_x = selection_rect.x() + (selection_rect.width() - quality_rect.width()) / 2
                quality_y = text_y + 20
                
                if quality_y < selection_rect.bottom() - 10:
                    painter.setPen(QColor(150, 255, 150))
                    painter.drawText(int(quality_x), int(quality_y), quality_text)
            
        except Exception as e:
            print(f"❌ Error drawing selection info: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press to start enhanced selection"""
        try:
            if event.button() == Qt.LeftButton:
                self.start_point = event.pos()
                self.current_point = event.pos()
                self.is_selecting = True
                self.update_display()
                print(f"✓ Enhanced selection started at {self.start_point.x()}, {self.start_point.y()}")
        except Exception as e:
            print(f"❌ Error in mouse press: {e}")
    
    def mouseMoveEvent(self, event):
        """Handle mouse move to update enhanced selection"""
        try:
            if self.is_selecting:
                self.current_point = event.pos()
                self.update_display()
        except Exception as e:
            print(f"❌ Error in mouse move: {e}")
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to complete enhanced selection"""
        try:
            if event.button() == Qt.LeftButton and self.is_selecting:
                self.current_point = event.pos()
                self.is_selecting = False
                
                # Get the selection rectangle
                selection_rect = self.get_selection_rect()
                
                print(f"✓ Enhanced selection completed: {selection_rect.width()}x{selection_rect.height()}")
                
                # Check if selection has valid size
                if selection_rect.width() >= self.min_selection_size and selection_rect.height() >= self.min_selection_size:
                    # Crop the selected portion from the original pixmap
                    selected_pixmap = self.pixmap.copy(selection_rect)
                    
                    print(f"✅ Enhanced snip completed: {selected_pixmap.width()}x{selected_pixmap.height()}")
                    
                    # Emit signal with the captured pixmap
                    self.snip_completed.emit(selected_pixmap)
                else:
                    print(f"⚠️ Selection too small: {selection_rect.width()}x{selection_rect.height()}")
                
                # Close the dialog
                self.accept()
                
        except Exception as e:
            print(f"❌ Error in mouse release: {e}")
    
    def keyPressEvent(self, event):
        """Handle enhanced key press events"""
        try:
            if event.key() == Qt.Key_Escape:
                print("✓ Enhanced snipping cancelled by user")
                self.reject()
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if self.is_selecting:
                    # Complete current selection
                    self.mouseReleaseEvent(type('MockEvent', (), {
                        'button': lambda: Qt.LeftButton
                    })())
        except Exception as e:
            print(f"❌ Error in key press: {e}")
    
    def get_selection_rect(self):
        """Get the enhanced selection rectangle"""
        try:
            return QRect(
                min(self.start_point.x(), self.current_point.x()),
                min(self.start_point.y(), self.current_point.y()),
                abs(self.start_point.x() - self.current_point.x()),
                abs(self.start_point.y() - self.current_point.y())
            )
        except Exception as e:
            print(f"❌ Error getting selection rect: {e}")
            return QRect()
    
    def closeEvent(self, event):
        """Handle enhanced close event"""
        try:
            print("✓ Enhanced snipping tool closed")
            super().closeEvent(event)
        except Exception as e:
            print(f"❌ Error in close event: {e}")