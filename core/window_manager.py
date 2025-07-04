"""
Window Management Module
Handles window setup, sizing, positioning, and maximization
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt


class WindowManager:
    """Manages window operations and display settings"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.maximization_attempts = 0
        self.max_attempts = 4
    
    def setup_initial_window_size(self):
        """Setup initial window size and position BEFORE showing"""
        try:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    initial_width = int(screen_geometry.width() * 0.9)
                    initial_height = int(screen_geometry.height() * 0.9)
                    x = (screen_geometry.width() - initial_width) // 2
                    y = (screen_geometry.height() - initial_height) // 2
                    self.main_window.setGeometry(x, y, initial_width, initial_height)
                else:
                    self.main_window.resize(1400, 900)
            else:
                self.main_window.resize(1400, 900)
                
            self.main_window.setMinimumSize(1200, 800)
            print("✅ Initial window size configured")
            
        except Exception as e:
            print(f"❌ Error setting window size: {e}")
            self.main_window.resize(1400, 900)
    
    def schedule_maximization_attempts(self):
        """Schedule multiple maximization attempts with delays"""
        QTimer.singleShot(50, self._attempt_maximization_1)
        QTimer.singleShot(200, self._attempt_maximization_2) 
        QTimer.singleShot(500, self._attempt_maximization_3)
        QTimer.singleShot(1000, self._final_maximization_check)
    
    def _attempt_maximization_1(self):
        """First maximization attempt"""
        try:
            if self.main_window.isVisible():
                self.main_window.showMaximized()
                print("🔧 Maximization attempt 1")
        except Exception as e:
            print(f"❌ Maximization attempt 1 failed: {e}")
    
    def _attempt_maximization_2(self):
        """Second maximization attempt"""
        try:
            if not self.main_window.isMaximized():
                self.main_window.showMaximized()
                print("🔧 Maximization attempt 2")
        except Exception as e:
            print(f"❌ Maximization attempt 2 failed: {e}")
    
    def _attempt_maximization_3(self):
        """Third maximization attempt"""
        try:
            if not self.main_window.isMaximized():
                self.main_window.setWindowState(Qt.WindowMaximized)
                self.main_window.showMaximized()
                self.main_window.update()
                self.main_window.repaint()
                print("🔧 Maximization attempt 3 (forced)")
        except Exception as e:
            print(f"❌ Maximization attempt 3 failed: {e}")
    
    def _final_maximization_check(self):
        """Final maximization check"""
        try:
            if not self.main_window.isMaximized():
                app = QApplication.instance()
                if app:
                    screen = app.primaryScreen()
                    if screen:
                        geometry = screen.availableGeometry()
                        self.main_window.setGeometry(geometry)
                
                self.main_window.setWindowState(Qt.WindowMaximized)
                self.main_window.showMaximized()
                print("🔧 Final maximization check")
            else:
                print("✅ Window properly maximized")
        except Exception as e:
            print(f"❌ Final maximization failed: {e}")
    
    def show_and_activate(self):
        """Show window and bring to front"""
        try:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            print("✅ Window shown and activated")
        except Exception as e:
            print(f"❌ Show and activate failed: {e}")