#!/usr/bin/env python3
"""
PVmizer GEO - Main Application Entry Point
Enhanced Building Designer with 3D Visualization

This is the main entry point for the PVmizer GEO application.
Handles Qt environment setup, VTK configuration, and application initialization.
"""
# Add this to track dialog sources
import sys
from PyQt5.QtWidgets import QMessageBox

# Override QMessageBox to track sources
original_warning = QMessageBox.warning
original_critical = QMessageBox.critical
original_information = QMessageBox.information

def debug_warning(parent, title, message, buttons=QMessageBox.Ok):
    print(f"🚨 WARNING DIALOG FROM: {parent.__class__.__name__ if parent else 'Unknown'}")
    print(f"   Title: {title}")
    print(f"   Message: {message}")
    import traceback
    traceback.print_stack(limit=10)
    return original_warning(parent, title, message, buttons)

def debug_critical(parent, title, message, buttons=QMessageBox.Ok):
    print(f"🚨 CRITICAL DIALOG FROM: {parent.__class__.__name__ if parent else 'Unknown'}")
    print(f"   Title: {title}")
    print(f"   Message: {message}")
    import traceback
    traceback.print_stack(limit=10)
    return original_critical(parent, title, message, buttons)

# Replace QMessageBox methods
QMessageBox.warning = debug_warning
QMessageBox.critical = debug_critical


import os
import sys
import traceback
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_environment():
    """Setup environment variables and Qt configuration"""
    print("🔧 Setting up application environment...")
    
    # Qt WebEngine settings (for Google Maps)
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu --disable-dev-shm-usage"
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.accessibility.*=false"
    
    # VTK settings to prevent external windows
    os.environ['VTK_SILENCE_GET_VOID_POINTER_WARNINGS'] = '1'
    os.environ['VTK_DEBUG_LEAKS'] = '0'
    os.environ['VTK_USE_OFFSCREEN_RENDERING'] = '0'
    
    # High DPI settings
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    
    print("✅ Environment configured successfully")

def setup_qt_message_handler():
    """Setup Qt message handler to reduce noise"""
    from PyQt5.QtCore import qInstallMessageHandler, QtDebugMsg, QtInfoMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg
    
    def silent_message_handler(mode, context, message):
        """Custom Qt message handler - only show important messages"""
        if mode == QtCriticalMsg or mode == QtFatalMsg:
            print(f"🚨 Qt CRITICAL: {message}")
        elif mode == QtWarningMsg and any(keyword in message.lower() for keyword in ['vtk', 'opengl', 'webengine']):
            # Show VTK, OpenGL, and WebEngine warnings as they're important for our app
            print(f"⚠️ Qt WARNING: {message}")
        # Suppress debug and info messages
    
    qInstallMessageHandler(silent_message_handler)
    print("✅ Qt message handler configured")

def check_dependencies():
    """Check for required and optional dependencies"""
    print("🔍 Checking dependencies...")
    
    required_deps = {
        'PyQt5': 'PyQt5',
        'PyQt5.QtWebEngineWidgets': 'PyQt5.QtWebEngineWidgets'
    }
    
    optional_deps = {
        'vtk': 'VTK (for 3D visualization)',
        'numpy': 'NumPy (for calculations)',
        'models.solar_simulation': 'Solar Simulation (for solar analysis)'
    }
    
    # Check required dependencies
    missing_required = []
    for dep_name, dep_desc in required_deps.items():
        try:
            __import__(dep_name)
            print(f"✅ {dep_desc}")
        except ImportError:
            print(f"❌ {dep_desc} - REQUIRED")
            missing_required.append(dep_desc)
    
    if missing_required:
        print(f"🚨 Missing required dependencies: {', '.join(missing_required)}")
        print("Please install with: pip install PyQt5 PyQtWebEngine")
        return False
    
    # Check optional dependencies
    available_optional = []
    for dep_name, dep_desc in optional_deps.items():
        try:
            __import__(dep_name)
            print(f"✅ {dep_desc}")
            available_optional.append(dep_name)
        except ImportError:
            print(f"⚠️ {dep_desc} - Optional (some features may be limited)")
    
    print(f"✅ Dependency check completed - {len(available_optional)}/{len(optional_deps)} optional features available")
    return True

def create_application():
    """Create and configure the QApplication"""
    print("🎨 Creating Qt application...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QIcon, QPixmap
        
        # Create application with proper attributes
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("PVmizer GEO")
        app.setApplicationVersion("1.0.0")
        app.setApplicationDisplayName("PVmizer GEO - Enhanced Building Designer")
        app.setOrganizationName("PVmizer")
        app.setOrganizationDomain("pvmizer.com")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Set application icon if available
        try:
            icon_path = current_dir / "resources" / "icons" / "app_icon.png"
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                print("✅ Application icon loaded")
        except Exception as icon_error:
            print(f"⚠️ Could not load application icon: {icon_error}")
        
        print("✅ Qt application created successfully")
        return app
        
    except ImportError as e:
        print(f"❌ Failed to create Qt application: {e}")
        print("Please install PyQt5: pip install PyQt5")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating application: {e}")
        traceback.print_exc()
        return None

def create_main_window():
    """Create and configure the main window"""
    print("🏠 Creating main window...")
    
    try:
        from core.main_window import MainWindow
        
        window = MainWindow()
        
        # Set window properties
        window.setWindowTitle("PVmizer GEO - Enhanced Building Designer")
        
        print("✅ Main window created successfully")
        return window
        
    except ImportError as e:
        print(f"❌ Failed to import MainWindow: {e}")
        print("Check that core/main_window.py exists and is properly configured")
        return None
    except Exception as e:
        print(f"❌ Error creating main window: {e}")
        traceback.print_exc()
        return None

def setup_exception_handler():
    """Setup global exception handler"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            print("\n🛑 Application interrupted by user")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print(f"\n🚨 Uncaught exception: {exc_type.__name__}: {exc_value}")
        print("📋 Traceback:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        # Try to show error dialog if Qt is available
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            app = QApplication.instance()
            if app:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Application Error")
                msg.setText(f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}")
                msg.setDetailedText(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        except:
            pass  # Qt not available or already shut down
    
    sys.excepthook = handle_exception
    print("✅ Exception handler configured")

def main():
    """Main application entry point"""
    print("🚀 Starting PVmizer GEO application...")
    print("=" * 50)
    
    try:
        # Setup environment and error handling
        setup_environment()
        setup_exception_handler()
        
        # Check dependencies
        if not check_dependencies():
            print("❌ Dependency check failed - cannot continue")
            return 1
        
        # Setup Qt message handler (after PyQt5 is confirmed to be available)
        setup_qt_message_handler()
        
        # Create Qt application
        app = create_application()
        if not app:
            print("❌ Failed to create Qt application")
            return 1
        
        # Create main window
        window = create_main_window()
        if not window:
            print("❌ Failed to create main window")
            return 1
        
        # Show window
        print("📱 Showing main window...")
        window.show()
        
        # Center on screen if possible
        try:
            screen = app.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                window_geometry = window.frameGeometry()
                window_geometry.moveCenter(screen_geometry.center())
                window.move(window_geometry.topLeft())
                print("✅ Window centered on screen")
        except Exception as center_error:
            print(f"⚠️ Could not center window: {center_error}")
        
        print("🎯 Application ready - entering event loop...")
        print("=" * 50)
        
        # Start event loop
        exit_code = app.exec_()
        
        print("🏁 Application event loop finished")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Fatal error in main(): {e}")
        traceback.print_exc()
        return 1
    finally:
        print("🧹 Cleaning up...")
        
        # Cleanup
        try:
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.quit()
        except:
            pass

def run_tests():
    """Run basic tests to verify installation"""
    print("🧪 Running basic tests...")
    
    # Test Qt
    try:
        from PyQt5.QtWidgets import QApplication, QWidget
        from PyQt5.QtCore import QTimer
        
        app = QApplication([])
        widget = QWidget()
        widget.setWindowTitle("Test Window")
        widget.resize(200, 100)
        widget.show()
        
        # Close after 1 second
        QTimer.singleShot(1000, app.quit)
        app.exec_()
        
        print("✅ Qt test passed")
    except Exception as e:
        print(f"❌ Qt test failed: {e}")
        return False
    
    # Test VTK
    try:
        import vtk
        print(f"✅ VTK test passed - Version: {vtk.vtkVersion.GetVTKVersion()}")
    except ImportError:
        print("⚠️ VTK not available - 3D features will be limited")
    
    return True

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            sys.exit(0 if run_tests() else 1)
        elif sys.argv[1] == "--help":
            print("PVmizer GEO")
            print("Usage:")
            print("  python main.py        - Start the application")
            print("  python main.py --test - Run basic tests")
            print("  python main.py --help - Show this help")
            sys.exit(0)
    
    # Run the application
    sys.exit(main())