#!/usr/bin/env python3
"""
Maps Tab Panel - Screenshot tools only (no info text)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QSizePolicy)
from PyQt5.QtCore import pyqtSignal

class MapsTabPanel(QWidget):
    """Maps tab panel with screenshot tools only - no info text"""
    
    # Signals
    snip_requested = pyqtSignal()
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
        print("✅ Maps Tab Panel initialized (button only)")
    
    def setup_ui(self):
        """Setup Maps tab UI with button only"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Screenshot Tools Group
        self._create_screenshot_section(main_layout)
        
        # Add stretch to center content
        main_layout.addStretch()
        
        print("✅ Maps Tab UI setup completed (button only)")
    
    def _create_screenshot_section(self, parent_layout):
        """Create screenshot section with button only"""
        try:
            # Screenshot group
            screenshot_group = QGroupBox("📸 Screenshot Tools")
            screenshot_layout = QVBoxLayout(screenshot_group)
            screenshot_layout.setContentsMargins(10, 15, 10, 10)
            screenshot_layout.setSpacing(10)
            
            # Snip Screenshot button only
            self.snip_btn = QPushButton("📸 Snip Screenshot")
            self.snip_btn.setMinimumHeight(35)
            self.snip_btn.clicked.connect(self._emit_snip_requested)
            self.snip_btn.setToolTip("Capture a screenshot of the map area for building outline drawing")
            
            # Apply button styling
            self.snip_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px 12px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            
            screenshot_layout.addWidget(self.snip_btn)
            
            # REMOVED: No info label/text under the button
            
            parent_layout.addWidget(screenshot_group)
            
            print("✅ Screenshot section created (button only)")
            
        except Exception as e:
            print(f"❌ Error creating screenshot section: {e}")
    
    def _emit_snip_requested(self):
        """Handle snip screenshot request"""
        print("📸 MAPS TAB: Snip screenshot requested")
        self.snip_requested.emit()
        
        try:
            # Try multiple methods to start snipping
            snipping_methods = [
                lambda: self._try_snip_via_main_window(),
                lambda: self._try_snip_via_content_tabs(),
                lambda: self._try_snip_via_snipping_manager(),
                lambda: self._try_snip_via_screenshot_manager(),
            ]
            
            for method in snipping_methods:
                try:
                    if method():
                        return
                except Exception as e:
                    print(f"⚠ Snipping method failed: {e}")
                    continue
            
            print("❌ No snipping method succeeded - signal emitted only")
                    
        except Exception as e:
            print(f"❌ Error in snip request: {e}")
    
    def _try_snip_via_main_window(self):
        """Try snipping via main window handle"""
        if hasattr(self.main_window, '_handle_snip_request'):
            self.main_window._handle_snip_request()
            print("✓ Snip via main window")
            return True
        return False
    
    def _try_snip_via_content_tabs(self):
        """Try snipping via content tabs manager"""
        if hasattr(self.main_window, 'content_tabs'):
            content_tabs = self.main_window.content_tabs
            if hasattr(content_tabs, 'snipping_manager'):
                content_tabs.snipping_manager.start_snipping()
                print("✓ Snip via content tabs")
                return True
        return False
    
    def _try_snip_via_snipping_manager(self):
        """Try snipping via main window snipping manager"""
        if hasattr(self.main_window, 'snipping_manager'):
            self.main_window.snipping_manager.start_snipping()
            print("✓ Snip via snipping manager")
            return True
        return False
    
    def _try_snip_via_screenshot_manager(self):
        """Try snipping via screenshot manager"""
        if hasattr(self.main_window, 'screenshot_manager'):
            self.main_window.screenshot_manager.start_snipping()
            print("✓ Snip via screenshot manager")
            return True
        return False
    
    def apply_theme(self, is_dark_theme=False):
        """Apply theme"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            print("🧹 Cleaning up Maps Tab Panel...")
            self.main_window = None
            self.snip_btn = None
            print("✅ Maps Tab Panel cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")