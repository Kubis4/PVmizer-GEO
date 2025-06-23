#!/usr/bin/env python3
"""
Enhanced Snipping Manager - COMPLETE FIXED VERSION
"""
import traceback
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap

class SnippingManager:
    """Enhanced snipping manager with perfect integration"""
    
    def __init__(self, content_tab_widget):
        self.content_tab_widget = content_tab_widget
        self.main_window = content_tab_widget.main_window
        print("✓ Enhanced Snipping Manager initialized")
    
    def start_snipping(self):
        """Start snipping process with enhanced integration"""
        try:
            print("📸 Enhanced SnippingManager: Starting snipping process...")
            
            # Check if we're on the Google Maps tab
            if self.content_tab_widget.currentIndex() != 0:
                print("⚠ Not on Google Maps tab - switching first")
                QMessageBox.information(self.main_window, "Screenshot", 
                                      "Please navigate to the Google Maps tab first.")
                self.content_tab_widget.setCurrentIndex(0)
                return False
            
            # Clear previous screenshot with enhanced method
            self._clear_previous_screenshot()
            
            # Show enhanced status message
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "Click and drag to select an area to capture - Enhanced centering enabled!")
            
            # Process events
            QApplication.processEvents()
            
            # Get the widget to snip
            widget_to_snip = self._get_snipping_target()
            if not widget_to_snip:
                print("❌ No suitable widget found for snipping")
                return False
            
            # Create or reuse enhanced snipping tool
            if not hasattr(self.content_tab_widget, 'snipping_tool') or self.content_tab_widget.snipping_tool is None:
                try:
                    from utils.snipping_tool import SnippingTool
                    self.content_tab_widget.snipping_tool = SnippingTool(self.main_window)
                    
                    # Connect to enhanced handler
                    self.content_tab_widget.snipping_tool.snip_completed.connect(self.on_snip_completed)
                    print("✓ Enhanced snipping tool created and connected")
                    
                except ImportError as e:
                    print(f"❌ Cannot import snipping tool: {e}")
                    QMessageBox.warning(self.main_window, "Error", 
                                      "Snipping tool not available")
                    return False
            
            # Start snipping
            self.content_tab_widget.snipping_tool.start_snipping(widget_to_snip)
            print("✓ Enhanced snipping started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error in enhanced snipping manager: {e}")
            traceback.print_exc()
            return False
    
    def _get_snipping_target(self):
        """Get the correct widget to snip with enhanced detection"""
        try:
            # Method 1: Try to get Google Maps tab content
            maps_tab = self.content_tab_widget.widget(0)  # Index 0 = Google Maps
            if maps_tab:
                print("✓ Found Google Maps tab for enhanced snipping")
                return maps_tab
            
            # Method 2: Try satellite_view if it exists
            if hasattr(self.content_tab_widget, 'satellite_view'):
                print("✓ Found satellite_view for snipping")
                return self.content_tab_widget.satellite_view
            
            # Method 3: Search for QWebEngineView in maps tab
            if maps_tab:
                try:
                    from PyQt5.QtWebEngineWidgets import QWebEngineView
                    web_views = maps_tab.findChildren(QWebEngineView)
                    if web_views:
                        print("✓ Found web view for snipping")
                        return web_views[0]
                except ImportError:
                    print("⚠️ QWebEngineView not available")
            
            # Method 4: Use the entire content tab widget as fallback
            print("⚠ Using content tab widget as snipping target")
            return self.content_tab_widget
            
        except Exception as e:
            print(f"❌ Error getting snipping target: {e}")
            return None
    
    def on_snip_completed(self, pixmap):
        """ENHANCED: Handle completed snip with perfect processing"""
        print(f"📸 ENHANCED SnippingManager: Snip completed! Size: {pixmap.width()}x{pixmap.height()}")
        
        try:
            if pixmap.isNull():
                print("❌ Received null pixmap")
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage("Screenshot capture cancelled")
                return
            
            # Store original image size in config
            if hasattr(self.main_window, 'config'):
                self.main_window.config.original_image_size = (pixmap.width(), pixmap.height())
                print(f"✓ Image size stored: {pixmap.width()}x{pixmap.height()}")
            
            # ENHANCED: Transfer to drawing canvas with perfect centering
            background_set = self._transfer_to_drawing_canvas_enhanced(pixmap)
            
            # Switch to drawing tab with enhancement
            self._switch_to_drawing_tab_enhanced()
            
            # Forward signal to content tab widget for other listeners
            self.content_tab_widget.snip_completed.emit(pixmap)
            
            # Update status based on success
            if background_set:
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(
                        "✅ Screenshot captured with perfect centering! Start drawing the building outline.", 6000)
                print("✅ ENHANCED screenshot processing completed successfully")
            else:
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(
                        "Screenshot captured but centering failed. Check drawing tab.", 5000)
                print("⚠ Screenshot captured but enhanced processing failed")
                
        except Exception as e:
            print(f"❌ Error in enhanced snip processing: {e}")
            traceback.print_exc()
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"Error processing screenshot: {e}", 3000)
    
    def _transfer_to_drawing_canvas_enhanced(self, pixmap):
        """ENHANCED: Transfer screenshot with perfect centering and enhancement"""
        try:
            print("🖼️ ENHANCED: Transferring screenshot with perfect centering...")
            
            # Method 1: Enhanced canvas manager (PRIORITY)
            if hasattr(self.main_window, 'canvas_manager') and self.main_window.canvas_manager:
                canvas_manager = self.main_window.canvas_manager
                print("📋 Found canvas manager - using enhanced method")
                
                # Use the enhanced set_background_image method
                try:
                    result = canvas_manager.set_background_image(pixmap)
                    if result:
                        print("✅ ENHANCED: Background set via canvas_manager with perfect centering!")
                        return True
                    else:
                        print("⚠️ Canvas manager enhanced method returned False")
                except Exception as e:
                    print(f"⚠ Enhanced canvas manager method failed: {e}")
                
                # Fallback: Try to get canvas directly and apply enhanced processing
                try:
                    canvas = canvas_manager.get_canvas()
                    if canvas:
                        # Create enhanced pixmap manually if canvas manager failed
                        enhanced_pixmap = self._create_manual_enhanced_pixmap(pixmap)
                        if self._set_canvas_background_enhanced(canvas, enhanced_pixmap):
                            return True
                except Exception as e:
                    print(f"⚠ Direct canvas enhanced method failed: {e}")
            
            # Method 2: Direct search in drawing tab with enhancement
            drawing_tab = self.content_tab_widget.widget(1)  # Index 1 = Drawing tab
            if drawing_tab:
                print("📝 Searching drawing tab for canvas with enhancement...")
                canvas = self._find_canvas_in_widget(drawing_tab)
                if canvas:
                    enhanced_pixmap = self._create_manual_enhanced_pixmap(pixmap)
                    if self._set_canvas_background_enhanced(canvas, enhanced_pixmap):
                        return True
            
            # Method 3: Global search with enhancement
            print("🌐 Global search for canvas with enhancement...")
            canvas = self._find_canvas_globally()
            if canvas:
                enhanced_pixmap = self._create_manual_enhanced_pixmap(pixmap)
                if self._set_canvas_background_enhanced(canvas, enhanced_pixmap):
                    return True
            
            # Method 4: Store enhanced version in drawing tab for later use
            if drawing_tab:
                print("💾 Storing enhanced screenshot in drawing tab as fallback...")
                enhanced_pixmap = self._create_manual_enhanced_pixmap(pixmap)
                drawing_tab.screenshot_pixmap = enhanced_pixmap
                drawing_tab.background_image = enhanced_pixmap
                drawing_tab.enhanced_screenshot = enhanced_pixmap
                return True
            
            print("❌ No suitable method found for enhanced transfer")
            return False
            
        except Exception as e:
            print(f"❌ Error in enhanced transfer: {e}")
            traceback.print_exc()
            return False
    
    def _create_manual_enhanced_pixmap(self, original_pixmap):
        """Create manually enhanced and centered pixmap"""
        try:
            from PyQt5.QtGui import QPainter, QColor
            from PyQt5.QtCore import Qt
            
            print("🎨 Creating manual enhanced pixmap...")
            
            # Default canvas size (will be improved by actual canvas detection)
            canvas_width, canvas_height = 1000, 700
            
            # Try to get better canvas size
            try:
                if hasattr(self.main_window, 'content_tabs'):
                    drawing_tab = self.main_window.content_tabs.widget(1)
                    if drawing_tab:
                        size = drawing_tab.size()
                        if size.width() > 200 and size.height() > 200:
                            canvas_width = int(size.width() * 0.95)
                            canvas_height = int(size.height() * 0.95)
            except:
                pass
            
            # Calculate scaling
            target_width = int(canvas_width * 0.8)
            target_height = int(canvas_height * 0.8)
            
            scale_x = target_width / original_pixmap.width()
            scale_y = target_height / original_pixmap.height()
            scale = min(scale_x, scale_y, 1.0)
            
            # Scale image if needed
            if scale < 1.0:
                scaled_pixmap = original_pixmap.scaled(
                    int(original_pixmap.width() * scale),
                    int(original_pixmap.height() * scale),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            else:
                scaled_pixmap = original_pixmap
            
            # Create canvas-sized pixmap
            canvas_pixmap = QPixmap(canvas_width, canvas_height)
            canvas_pixmap.fill(QColor(245, 245, 245, 30))
            
            # Calculate center
            x_center = (canvas_width - scaled_pixmap.width()) // 2
            y_center = (canvas_height - scaled_pixmap.height()) // 2
            
            # Draw enhanced image
            painter = QPainter(canvas_pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            
            # Draw with transparency
            painter.setOpacity(0.85)
            painter.drawPixmap(x_center, y_center, scaled_pixmap)
            
            painter.end()
            
            print(f"✓ Manual enhanced pixmap created: {canvas_width}x{canvas_height}")
            return canvas_pixmap
            
        except Exception as e:
            print(f"❌ Error creating manual enhanced pixmap: {e}")
            return original_pixmap
    
    def _set_canvas_background_enhanced(self, canvas, pixmap):
        """Set background on canvas with enhanced methods"""
        try:
            print(f"🎨 ENHANCED: Setting background on {canvas.__class__.__name__}")
            
            # Method 1: Enhanced set_background_image
            if hasattr(canvas, 'set_background_image'):
                try:
                    result = canvas.set_background_image(pixmap)
                    if result:
                        print("✅ ENHANCED: Background set via set_background_image()")
                        return True
                except Exception as e:
                    print(f"⚠ Enhanced set_background_image failed: {e}")
            
            # Method 2: Direct enhanced assignment
            try:
                canvas.background_pixmap = pixmap
                canvas.background_image = pixmap
                canvas.screenshot_image = pixmap
                canvas.enhanced_background = pixmap
                
                # Force updates
                if hasattr(canvas, 'update'):
                    canvas.update()
                if hasattr(canvas, 'repaint'):
                    canvas.repaint()
                
                print("✅ ENHANCED: Background set via direct enhanced assignment")
                return True
            except Exception as e:
                print(f"⚠ Enhanced direct assignment failed: {e}")
            
            # Method 3: Drawing area enhancement
            if hasattr(canvas, 'drawing_area'):
                try:
                    drawing_area = canvas.drawing_area
                    drawing_area.background_pixmap = pixmap
                    drawing_area.enhanced_background = pixmap
                    
                    if hasattr(drawing_area, 'update'):
                        drawing_area.update()
                    
                    print("✅ ENHANCED: Background set via drawing area")
                    return True
                except Exception as e:
                    print(f"⚠ Enhanced drawing area failed: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ Error in enhanced background setting: {e}")
            return False
    
    def _switch_to_drawing_tab_enhanced(self):
        """Enhanced switch to drawing tab with better timing"""
        try:
            # Switch tab widget
            self.content_tab_widget.setCurrentIndex(1)
            print("✅ ENHANCED: Switched to drawing tab")
            
            # Update left panel with delay for better synchronization
            if hasattr(self.main_window, 'left_panel'):
                QTimer.singleShot(100, lambda: self.main_window.left_panel.switch_to_tab_content(1))
                print("✅ ENHANCED: Left panel update scheduled")
            
            # Force refresh after switch
            QTimer.singleShot(200, self._force_drawing_tab_refresh)
                
        except Exception as e:
            print(f"❌ Error in enhanced tab switching: {e}")
    
    def _force_drawing_tab_refresh(self):
        """Force refresh of drawing tab after switch"""
        try:
            drawing_tab = self.content_tab_widget.widget(1)
            if drawing_tab and hasattr(drawing_tab, 'update'):
                drawing_tab.update()
                print("✓ Drawing tab forced refresh")
        except Exception as e:
            print(f"⚠️ Error forcing drawing tab refresh: {e}")
    
    def _clear_previous_screenshot(self):
        """Enhanced clearing of previous screenshot"""
        try:
            print("🧹 ENHANCED: Clearing previous screenshot...")
            
            # Method 1: Enhanced canvas manager clearing
            if hasattr(self.main_window, 'canvas_manager') and self.main_window.canvas_manager:
                canvas_manager = self.main_window.canvas_manager
                
                try:
                    canvas_manager.clear_previous_screenshot()
                    print("✅ ENHANCED: Canvas cleared via canvas manager")
                    return
                except Exception as e:
                    print(f"⚠ Enhanced canvas manager clear failed: {e}")
            
            # Method 2: Enhanced direct canvas clearing
            drawing_tab = self.content_tab_widget.widget(1)
            if drawing_tab:
                canvas = self._find_canvas_in_widget(drawing_tab)
                if canvas:
                    self._clear_canvas_enhanced(canvas)
                    return
            
            print("⚠ No canvas found for enhanced clearing")
            
        except Exception as e:
            print(f"❌ Error in enhanced clearing: {e}")
    
    def _clear_canvas_enhanced(self, canvas):
        """Enhanced canvas clearing"""
        try:
            # Clear enhanced background attributes
            enhanced_attrs = [
                'background_pixmap', 'background_image', 'screenshot_image',
                'enhanced_background', 'enhanced_screenshot'
            ]
            
            for attr in enhanced_attrs:
                if hasattr(canvas, attr):
                    setattr(canvas, attr, None)
            
            # Clear drawing data
            if hasattr(canvas, 'points'):
                canvas.points = []
            if hasattr(canvas, 'is_complete'):
                canvas.is_complete = False
            
            # Enhanced clear methods
            clear_methods = ['clear_background', 'clear_canvas', 'clear']
            for method in clear_methods:
                if hasattr(canvas, method):
                    try:
                        getattr(canvas, method)()
                        break
                    except:
                        continue
            
            # Force updates
            if hasattr(canvas, 'update'):
                canvas.update()
            if hasattr(canvas, 'repaint'):
                canvas.repaint()
            
            print("✅ ENHANCED: Canvas cleared successfully")
            
        except Exception as e:
            print(f"❌ Error in enhanced canvas clearing: {e}")
    
    # Keep existing helper methods
    def _find_canvas_in_widget(self, parent_widget):
        """Find canvas in widget hierarchy"""
        try:
            for child in parent_widget.findChildren(QWidget):
                class_name = child.__class__.__name__.lower()
                
                if (hasattr(child, 'set_background_image') or
                    hasattr(child, 'background_pixmap') or
                    hasattr(child, 'points') or
                    'canvas' in class_name or
                    'drawing' in class_name):
                    
                    print(f"🎯 Found potential canvas: {child.__class__.__name__}")
                    return child
            
            return None
        except Exception as e:
            print(f"❌ Error finding canvas in widget: {e}")
            return None
    
    def _find_canvas_globally(self):
        """Find canvas anywhere in main window"""
        try:
            for widget in self.main_window.findChildren(QWidget):
                class_name = widget.__class__.__name__.lower()
                
                if (hasattr(widget, 'set_background_image') and
                    hasattr(widget, 'points') and
                    ('canvas' in class_name or 'drawing' in class_name)):
                    
                    print(f"🌐 Found global canvas: {widget.__class__.__name__}")
                    return widget
            
            return None
        except Exception as e:
            print(f"❌ Error in global canvas search: {e}")
            return None