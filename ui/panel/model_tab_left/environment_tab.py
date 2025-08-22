#!/usr/bin/env python3
"""
ui/panel/model_tab_left/environment_tab.py
Environment obstacles panel for adding trees and poles to the surroundings
WITH COMPLETE DEBUG FEATURES - FULLY FIXED
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QGroupBox, QMessageBox, QSlider)
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QFont
import numpy as np

try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("⚠️ PyVista not available for direct rendering")

try:
    from styles.ui_styles import (
        get_model3d_groupbox_style,
        get_model3d_button_style
    )
    STYLES_AVAILABLE = True
except ImportError:
    STYLES_AVAILABLE = False
    print("⚠️ Styles not available for EnvironmentTab")

class EnvironmentTab(QWidget):
    """Environment obstacles tab for adding trees and poles - WITH DEBUG"""
    
    # Signals
    environment_action_requested = pyqtSignal(str, dict)  # action_type, parameters
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Control references
        self.tree_controls = {}
        self.pole_controls = {}
        self.size_controls = {}
        
        # Current settings
        self.tree_size_multiplier = 1.0
        self.pole_height_multiplier = 1.0
        self.attachment_points_visible = False
        self.current_placement_mode = None
        
        # Debug flags
        self.debug_mode = True
        self.connection_verified = False
        self.signal_connected = False  # Track if signal is connected
        
        self.setup_ui()
        self.apply_styles()
        
        print("✅ EnvironmentTab initialized")
        
        # Auto-check connection after initialization
        if self.debug_mode:
            QTimer.singleShot(1000, self._initial_connection_check)
    
    def setup_ui(self):
        """Setup environment tab UI"""
        # Set background
        self.setStyleSheet("background-color: #2c3e50;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Debug Section (at top for visibility)
        if self.debug_mode:
            self.setup_debug_section(layout)
        
        # Size Controls Section
        self.setup_size_controls(layout)
        
        # Trees Section
        self.setup_trees_section(layout)
        
        # Poles Section
        self.setup_poles_section(layout)
        
        # Environment Management Section
        self.setup_management_section(layout)
        
        # Add stretch to push everything up
        layout.addStretch()
    
    def setup_debug_section(self, layout):
        """Setup debug controls section"""
        debug_group = QGroupBox("🔧 DEBUG CONTROLS")
        debug_layout = QVBoxLayout(debug_group)
        debug_layout.setContentsMargins(8, 10, 8, 8)
        debug_layout.setSpacing(8)
        
        # Connection status label
        self.connection_status_label = QLabel("Connection: Not Checked")
        self.connection_status_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-weight: bold;
                padding: 5px;
                background-color: #34495e;
                border-radius: 3px;
            }
        """)
        debug_layout.addWidget(self.connection_status_label)
        
        # Debug buttons row 1
        debug_row1 = QHBoxLayout()
        
        # Test Connection Button
        test_conn_btn = QPushButton("🧪 Test Connection")
        test_conn_btn.setMinimumHeight(30)
        test_conn_btn.clicked.connect(self._test_connection)
        test_conn_btn.setToolTip("Test if environment system is connected")
        test_conn_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        debug_row1.addWidget(test_conn_btn)
        
        # Fix Connection Button
        fix_conn_btn = QPushButton("🔧 Fix Connection")
        fix_conn_btn.setMinimumHeight(30)
        fix_conn_btn.clicked.connect(self._fix_connection)
        fix_conn_btn.setToolTip("Attempt to fix broken connection")
        fix_conn_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        debug_row1.addWidget(fix_conn_btn)
        
        debug_layout.addLayout(debug_row1)
        
        # Debug buttons row 2
        debug_row2 = QHBoxLayout()
        
        # Force Show Points Button
        force_show_btn = QPushButton("🔴 Force Red Spheres")
        force_show_btn.setMinimumHeight(30)
        force_show_btn.clicked.connect(self._force_show_points)
        force_show_btn.setToolTip("Force show red test spheres in 3D view")
        force_show_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        debug_row2.addWidget(force_show_btn)
        
        # Direct Render Test Button
        render_test_btn = QPushButton("🎯 Direct Render")
        render_test_btn.setMinimumHeight(30)
        render_test_btn.clicked.connect(self._direct_render_test)
        render_test_btn.setToolTip("Test direct rendering to plotter")
        render_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        debug_row2.addWidget(render_test_btn)
        
        debug_layout.addLayout(debug_row2)
        
        # Debug info button
        debug_info_btn = QPushButton("📊 Full Debug Info")
        debug_info_btn.setMinimumHeight(30)
        debug_info_btn.clicked.connect(self._show_full_debug_info)
        debug_info_btn.setToolTip("Show complete debug information")
        debug_info_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
        """)
        debug_layout.addWidget(debug_info_btn)
        
        # Add debug group with special style
        debug_group.setStyleSheet("""
            QGroupBox {
                background-color: #2c3e50;
                border: 2px solid #e74c3c;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 10px;
                font-weight: bold;
                color: #e74c3c;
                font-size: 12px;
            }
            QGroupBox::title {
                color: #e74c3c;
                background-color: #2c3e50;
                padding: 2px 6px;
            }
        """)
        
        layout.addWidget(debug_group)
        self.debug_group = debug_group
    
    def setup_size_controls(self, layout):
        """Setup size control sliders"""
        size_group = QGroupBox("📏 Size Controls")
        size_layout = QVBoxLayout(size_group)
        size_layout.setContentsMargins(8, 10, 8, 8)
        size_layout.setSpacing(8)
        
        # Tree size control
        tree_size_layout = QHBoxLayout()
        tree_size_label = QLabel("Tree Size:")
        tree_size_label.setStyleSheet("color: #ecf0f1; font-weight: bold; min-width: 70px;")
        tree_size_layout.addWidget(tree_size_label)
        
        self.tree_size_slider = QSlider(Qt.Horizontal)
        self.tree_size_slider.setMinimum(50)
        self.tree_size_slider.setMaximum(200)
        self.tree_size_slider.setValue(100)
        self.tree_size_slider.setTickPosition(QSlider.TicksBelow)
        self.tree_size_slider.setTickInterval(50)
        self.tree_size_slider.valueChanged.connect(self._on_tree_size_changed)
        tree_size_layout.addWidget(self.tree_size_slider)
        
        self.tree_size_value = QLabel("100%")
        self.tree_size_value.setStyleSheet("color: #3498db; font-weight: bold; min-width: 40px;")
        tree_size_layout.addWidget(self.tree_size_value)
        
        size_layout.addLayout(tree_size_layout)
        
        # Pole height control
        pole_height_layout = QHBoxLayout()
        pole_height_label = QLabel("Pole Height:")
        pole_height_label.setStyleSheet("color: #ecf0f1; font-weight: bold; min-width: 70px;")
        pole_height_layout.addWidget(pole_height_label)
        
        self.pole_height_slider = QSlider(Qt.Horizontal)
        self.pole_height_slider.setMinimum(50)
        self.pole_height_slider.setMaximum(150)
        self.pole_height_slider.setValue(100)
        self.pole_height_slider.setTickPosition(QSlider.TicksBelow)
        self.pole_height_slider.setTickInterval(50)
        self.pole_height_slider.valueChanged.connect(self._on_pole_height_changed)
        pole_height_layout.addWidget(self.pole_height_slider)
        
        self.pole_height_value = QLabel("100%")
        self.pole_height_value.setStyleSheet("color: #3498db; font-weight: bold; min-width: 40px;")
        pole_height_layout.addWidget(self.pole_height_value)
        
        size_layout.addLayout(pole_height_layout)
        
        layout.addWidget(size_group)
        self.size_controls['group'] = size_group
    
    def setup_trees_section(self, layout):
        """Setup tree placement controls"""
        trees_group = QGroupBox("🌳 Trees")
        trees_layout = QVBoxLayout(trees_group)
        trees_layout.setContentsMargins(8, 10, 8, 8)
        trees_layout.setSpacing(8)
        
        # Tree type buttons
        tree_buttons_layout = QHBoxLayout()
        tree_buttons_layout.setSpacing(5)
        
        # Deciduous tree button
        deciduous_btn = QPushButton("🌳 Deciduous")
        deciduous_btn.setMinimumHeight(32)
        deciduous_btn.clicked.connect(lambda: self._select_tree_placement('deciduous'))
        deciduous_btn.setToolTip("Place a deciduous tree")
        self.tree_controls['deciduous_btn'] = deciduous_btn
        tree_buttons_layout.addWidget(deciduous_btn)
        
        # Pine tree button
        pine_btn = QPushButton("🌲 Pine")
        pine_btn.setMinimumHeight(32)
        pine_btn.clicked.connect(lambda: self._select_tree_placement('pine'))
        pine_btn.setToolTip("Place a pine tree")
        self.tree_controls['pine_btn'] = pine_btn
        tree_buttons_layout.addWidget(pine_btn)
        
        # Oak tree button
        oak_btn = QPushButton("🌰 Oak")
        oak_btn.setMinimumHeight(32)
        oak_btn.clicked.connect(lambda: self._select_tree_placement('oak'))
        oak_btn.setToolTip("Place a large oak tree")
        self.tree_controls['oak_btn'] = oak_btn
        tree_buttons_layout.addWidget(oak_btn)
        
        trees_layout.addLayout(tree_buttons_layout)
        
        # Quick add button
        add_multiple_btn = QPushButton("🌲 Add 5 Random Trees")
        add_multiple_btn.setMinimumHeight(30)
        add_multiple_btn.clicked.connect(lambda: self._add_multiple_trees(5))
        add_multiple_btn.setToolTip("Quickly add 5 trees of mixed types")
        trees_layout.addWidget(add_multiple_btn)
        
        layout.addWidget(trees_group)
        self.trees_group = trees_group
    
    def setup_poles_section(self, layout):
        """Setup utility pole controls"""
        poles_group = QGroupBox("🏗️ Utility Poles")
        poles_layout = QVBoxLayout(poles_group)
        poles_layout.setContentsMargins(8, 10, 8, 8)
        poles_layout.setSpacing(8)
        
        # Pole button
        single_pole_btn = QPushButton("🏗️ Add Utility Pole")
        single_pole_btn.setMinimumHeight(32)
        single_pole_btn.clicked.connect(lambda: self._select_pole_placement())
        single_pole_btn.setToolTip("Place a utility pole")
        self.pole_controls['single_btn'] = single_pole_btn
        poles_layout.addWidget(single_pole_btn)
        
        # Add multiple poles
        add_poles_btn = QPushButton("🏗️ Add 3 Poles")
        add_poles_btn.setMinimumHeight(30)
        add_poles_btn.clicked.connect(lambda: self._add_multiple_poles(3))
        add_poles_btn.setToolTip("Quickly add 3 utility poles")
        self.pole_controls['multiple_btn'] = add_poles_btn
        poles_layout.addWidget(add_poles_btn)
        
        layout.addWidget(poles_group)
        self.poles_group = poles_group
    
    def setup_management_section(self, layout):
        """Setup environment management controls"""
        management_group = QGroupBox("🔧 Management")
        management_layout = QVBoxLayout(management_group)
        management_layout.setContentsMargins(8, 10, 8, 8)
        management_layout.setSpacing(8)
        
        # Management buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        # Show/Hide attachment points
        self.toggle_points_btn = QPushButton("📍 Show Points")
        self.toggle_points_btn.setMinimumHeight(32)
        self.toggle_points_btn.setCheckable(True)
        self.toggle_points_btn.clicked.connect(lambda: self._toggle_attachment_points())
        self.toggle_points_btn.setToolTip("Show/hide placement points")
        buttons_layout.addWidget(self.toggle_points_btn)
        
        # Clear all environment
        clear_all_btn = QPushButton("🧹 Clear All")
        clear_all_btn.setMinimumHeight(32)
        clear_all_btn.clicked.connect(lambda: self._clear_all_environment())
        clear_all_btn.setToolTip("Remove all environment objects")
        clear_all_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e74c3c; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons_layout.addWidget(clear_all_btn)
        
        management_layout.addLayout(buttons_layout)
        
        # Auto-populate button
        auto_populate_btn = QPushButton("🎲 Auto-Populate")
        auto_populate_btn.setMinimumHeight(35)
        auto_populate_btn.clicked.connect(lambda: self._auto_populate_scene())
        auto_populate_btn.setToolTip("Automatically add trees and poles")
        auto_populate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        management_layout.addWidget(auto_populate_btn)
        
        layout.addWidget(management_group)
        self.management_group = management_group
    
    def apply_styles(self):
        """Apply dark theme styles"""
        if STYLES_AVAILABLE:
            # Apply group box styles (except debug group)
            for group in [self.trees_group, self.poles_group, 
                         self.management_group, self.size_controls.get('group')]:
                if group:
                    group.setStyleSheet(get_model3d_groupbox_style(True))
            
            # Apply button styles
            all_buttons = []
            all_buttons.extend(self.tree_controls.values())
            all_buttons.extend(self.pole_controls.values())
            
            for button in all_buttons:
                if isinstance(button, QPushButton) and not button.styleSheet():
                    button.setStyleSheet(get_model3d_button_style(True))
    
    # ==================== DEBUG METHODS ====================
    
    def _initial_connection_check(self):
        """Check connection status on startup"""
        if self.debug_mode:
            print("\n🔍 Initial connection check...")
            self._test_connection()
    
    def _find_model_tab(self):
        """Find the model tab through various paths"""
        print("\n🔍 Searching for model_tab...")
        
        # Method 1: Through content_tabs (YOUR ACTUAL STRUCTURE)
        if hasattr(self.main_window, 'content_tabs'):
            content_tabs = self.main_window.content_tabs
            print(f"  Found content_tabs: {type(content_tabs)}")
            
            # Check if content_tabs has model_tab
            if hasattr(content_tabs, 'model_tab'):
                print(f"  ✅ Found model_tab in content_tabs!")
                return content_tabs.model_tab
            
            # Also check get_model_tab method
            if hasattr(content_tabs, 'get_model_tab'):
                model_tab = content_tabs.get_model_tab()
                if model_tab:
                    print(f"  ✅ Found model_tab via get_model_tab()!")
                    return model_tab
        
        # Method 2: Direct attribute (unlikely but check anyway)
        if hasattr(self.main_window, 'model_tab'):
            print(f"  ✅ Found model_tab directly on main_window")
            return self.main_window.model_tab
        
        # Method 3: Through tab_manager
        if hasattr(self.main_window, 'tab_manager'):
            tab_manager = self.main_window.tab_manager
            if hasattr(tab_manager, 'model_tab'):
                print(f"  ✅ Found model_tab in tab_manager")
                return tab_manager.model_tab
        
        # Method 4: Through component_manager
        if hasattr(self.main_window, 'component_manager'):
            comp_mgr = self.main_window.component_manager
            if hasattr(comp_mgr, 'model_tab'):
                print(f"  ✅ Found model_tab in component_manager")
                return comp_mgr.model_tab
        
        print("  ❌ Could not find model_tab")
        return None
    
    def _test_connection(self):
        """Test if the environment system is connected - FIXED FOR YOUR STRUCTURE"""
        print("\n" + "="*60)
        print("🧪 TESTING ENVIRONMENT CONNECTION")
        print("="*60)
        
        status_messages = []
        
        # Check signal
        if hasattr(self, 'environment_action_requested'):
            print("📡 Signal exists: environment_action_requested")
            
            # Test signal emission
            test_received = [False]
            
            @pyqtSlot(str, dict)
            def test_receiver(action, params):
                if action == 'test_connection':
                    test_received[0] = True
                    print("  ✅ Test signal received by test receiver")
            
            self.environment_action_requested.connect(test_receiver)
            print("📤 Sending test signal...")
            self.environment_action_requested.emit('test_connection', {'test': True})
            self.environment_action_requested.disconnect(test_receiver)
            
            if test_received[0]:
                status_messages.append("✅ Signal can emit and receive")
                self.connection_verified = True
                self._update_connection_status("Signal OK", "orange")
            else:
                status_messages.append("⚠️ Signal exists but not working")
                self.connection_verified = False
                self._update_connection_status("Signal Error", "red")
        else:
            status_messages.append("❌ No signal exists")
            self._update_connection_status("No Signal", "red")
        
        # Find model tab using the fixed method
        model_tab = self._find_model_tab()
        if model_tab:
            status_messages.append(f"✅ Model tab found: {model_tab.__class__.__name__}")
            
            # Check for current roof
            if hasattr(model_tab, 'current_roof') and model_tab.current_roof:
                status_messages.append(f"✅ Current roof: {model_tab.current_roof.__class__.__name__}")
            else:
                status_messages.append("⚠️ No current roof - create a building first")
            
            # Check for plotter
            if hasattr(model_tab, 'plotter') and model_tab.plotter:
                status_messages.append("✅ Plotter available")
            else:
                status_messages.append("❌ No plotter in model tab")
            
            # Check if we're connected to model tab
            if hasattr(model_tab, 'environment_tab') and model_tab.environment_tab == self:
                status_messages.append("✅ Connected to model tab")
                self._update_connection_status("Connected", "green")
            else:
                status_messages.append("⚠️ Not connected to model tab")
                self._update_connection_status("Not Connected", "orange")
        else:
            status_messages.append("❌ Model tab not found")
        
        # Show summary
        for msg in status_messages:
            print(msg)
        
        print("="*60 + "\n")
        
        # Show message box with results
        if model_tab and self.connection_verified:
            QMessageBox.information(self, "Connection Test", 
                                   "✅ Environment system found!\n\n" + 
                                   "\n".join(status_messages))
        else:
            QMessageBox.warning(self, "Connection Test", 
                               "⚠️ Environment system needs connection!\n\n" + 
                               "\n".join(status_messages) + 
                               "\n\nClick 'Fix Connection' to attempt repair.")
    
    def _fix_connection(self):
        """Attempt to fix broken connection - FIXED FOR YOUR STRUCTURE"""
        print("\n🔧 Attempting to fix connection...")
        
        try:
            # Find model tab using the fixed method
            model_tab = self._find_model_tab()
            
            if model_tab:
                print(f"✅ Found model tab: {model_tab.__class__.__name__}")
                
                # Try to connect
                if hasattr(model_tab, 'connect_environment_tab'):
                    result = model_tab.connect_environment_tab(self)
                    if result:
                        print("✅ Connection fixed!")
                        self._update_connection_status("Connected", "green")
                        QMessageBox.information(self, "Success", 
                                              "✅ Connection fixed successfully!")
                    else:
                        print("❌ Connection fix failed")
                        self._update_connection_status("Fix Failed", "orange")
                        QMessageBox.warning(self, "Failed", 
                                          "❌ Could not fix connection")
                else:
                    print("⚠️ Model tab doesn't have connect_environment_tab method")
                    print("   Adding connection method dynamically...")
                    
                    # Try to add the connection dynamically
                    def connect_env_tab(env_tab):
                        model_tab.environment_tab = env_tab
                        if hasattr(env_tab, 'environment_action_requested'):
                            try:
                                env_tab.environment_action_requested.disconnect()
                            except:
                                pass
                            
                            # Create handler if it doesn't exist
                            if not hasattr(model_tab, '_handle_environment_tab_action'):
                                def handler(action, params):
                                    print(f"📡 Model tab received: {action}")
                                    if model_tab.current_roof:
                                        model_tab.current_roof.handle_environment_action(action, params)
                                        if model_tab.plotter:
                                            model_tab.plotter.render()
                                model_tab._handle_environment_tab_action = handler
                            
                            env_tab.environment_action_requested.connect(
                                model_tab._handle_environment_tab_action
                            )
                            return True
                        return False
                    
                    # Add method to model_tab
                    model_tab.connect_environment_tab = connect_env_tab
                    
                    # Try again
                    if model_tab.connect_environment_tab(self):
                        print("✅ Dynamic connection successful!")
                        self._update_connection_status("Connected", "green")
                        QMessageBox.information(self, "Success", 
                                              "✅ Connection established dynamically!")
                    else:
                        print("❌ Dynamic connection failed")
                        QMessageBox.warning(self, "Failed", 
                                          "Could not establish connection")
            else:
                print("❌ Cannot find model tab")
                QMessageBox.critical(self, "Error", 
                                   "Cannot find model tab.\n"
                                   "Please ensure a building is created first.")
                
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Fix failed: {str(e)}")
    
    def _force_show_points(self):
        """Force show attachment points with highly visible red spheres - FIXED"""
        print("\n🔴 FORCING ATTACHMENT POINTS DISPLAY")
        
        try:
            # Find model tab using the fixed method
            model_tab = self._find_model_tab()
            
            if not model_tab:
                print("❌ No model tab found")
                QMessageBox.warning(self, "Error", 
                                   "Model tab not found.\n"
                                   "Please create a building first.")
                return
            
            if not hasattr(model_tab, 'plotter') or not model_tab.plotter:
                print("❌ No plotter found")
                QMessageBox.warning(self, "Error", "3D plotter not found")
                return
            
            plotter = model_tab.plotter
            
            if not PYVISTA_AVAILABLE:
                print("❌ PyVista not available")
                QMessageBox.warning(self, "Error", "PyVista not available for rendering")
                return
            
            # Create highly visible test spheres
            print("Creating test spheres...")
            test_positions = [
                (5, 0, 1),    # Right
                (-5, 0, 1),   # Left
                (0, 5, 1),    # Front
                (0, -5, 1),   # Back
                (3, 3, 1),    # Corners
                (-3, 3, 1),
                (3, -3, 1),
                (-3, -3, 1)
            ]
            
            for i, (x, y, z) in enumerate(test_positions):
                sphere = pv.Sphere(center=(x, y, z), radius=0.5)
                plotter.add_mesh(
                    sphere,
                    color='red',
                    name=f'test_attachment_{i}',
                    opacity=1.0,
                    ambient=0.5,
                    diffuse=0.8
                )
                print(f"  Added red sphere at ({x}, {y}, {z})")
            
            # Add ground reference
            ground = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), 
                            i_size=20, j_size=20)
            plotter.add_mesh(
                ground,
                color='lightgray',
                opacity=0.5,
                name='test_ground'
            )
            print("  Added ground reference plane")
            
            # Force render
            plotter.render()
            print("✅ Forced render complete")
            
            # Reset camera
            plotter.reset_camera()
            print("✅ Camera reset")
            
            QMessageBox.information(self, "Success", 
                                   "8 red spheres should now be visible in the 3D view")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")
    
    def _direct_render_test(self):
        """Test direct rendering to plotter - FIXED"""
        print("\n🎯 DIRECT RENDER TEST")
        
        try:
            # Find model tab using the fixed method
            model_tab = self._find_model_tab()
            
            if model_tab and hasattr(model_tab, 'plotter') and model_tab.plotter:
                plotter = model_tab.plotter
                
                if not PYVISTA_AVAILABLE:
                    print("❌ PyVista not available")
                    QMessageBox.warning(self, "Error", "PyVista not available")
                    return
                
                # Add a big colorful sphere at origin
                sphere = pv.Sphere(center=(0, 0, 5), radius=2)
                actor = plotter.add_mesh(
                    sphere,
                    color='yellow',
                    name='big_test_sphere',
                    opacity=1.0
                )
                
                print(f"✅ Added big yellow sphere at (0, 0, 5)")
                print(f"   Actor: {actor}")
                
                # Force render
                plotter.render()
                print("✅ Render called")
                
                # Check renderer
                if hasattr(plotter, 'renderer'):
                    print(f"✅ Renderer exists: {plotter.renderer}")
                
                QMessageBox.information(self, "Success", 
                                      "A big yellow sphere should be visible at the center")
            else:
                print("❌ No plotter available")
                QMessageBox.warning(self, "Error", "No plotter available")
                
        except Exception as e:
            print(f"❌ Direct render failed: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Render failed: {str(e)}")
    
    def _show_full_debug_info(self):
        """Show complete debug information - FIXED"""
        print("\n" + "="*60)
        print("📊 FULL DEBUG INFORMATION")
        print("="*60)
        
        info = []
        
        # Check main window
        info.append(f"Main window exists: {self.main_window is not None}")
        
        # Check content_tabs
        if hasattr(self.main_window, 'content_tabs'):
            content_tabs = self.main_window.content_tabs
            info.append(f"Content tabs: {content_tabs.__class__.__name__}")
            
            # Check model tab through content_tabs
            if hasattr(content_tabs, 'model_tab'):
                model_tab = content_tabs.model_tab
                info.append(f"Model tab: {model_tab.__class__.__name__}")
                
                # Check plotter
                if hasattr(model_tab, 'plotter'):
                    info.append(f"Plotter: {type(model_tab.plotter)}")
                else:
                    info.append("Plotter: NOT FOUND")
                
                # Check current roof
                if hasattr(model_tab, 'current_roof') and model_tab.current_roof:
                    roof = model_tab.current_roof
                    info.append(f"Current roof: {roof.__class__.__name__}")
                    
                    # Check environment manager
                    if hasattr(roof, 'environment_manager'):
                        env_mgr = roof.environment_manager
                        info.append(f"Environment manager: {env_mgr.__class__.__name__}")
                        
                        # Check attachment points
                        if hasattr(env_mgr, 'environment_attachment_points'):
                            points = env_mgr.environment_attachment_points
                            info.append(f"Attachment points: {len(points)}")
                        else:
                            info.append("Attachment points: NOT FOUND")
                    else:
                        info.append("Environment manager: NOT FOUND")
                else:
                    info.append("Current roof: NONE")
            else:
                info.append("Model tab: NOT FOUND in content_tabs")
        else:
            info.append("Content tabs: NOT FOUND")
        
        # Check signal
        info.append(f"Signal exists: {hasattr(self, 'environment_action_requested')}")
        info.append(f"PyVista available: {PYVISTA_AVAILABLE}")
        
        # Print to console
        for line in info:
            print(f"  {line}")
        
        print("="*60 + "\n")
        
        # Show in message box
        QMessageBox.information(self, "Debug Information", 
                               "\n".join(info))
    
    def _update_connection_status(self, status, color):
        """Update connection status label"""
        if hasattr(self, 'connection_status_label'):
            color_map = {
                'green': '#27ae60',
                'red': '#e74c3c',
                'orange': '#f39c12'
            }
            bg_color = color_map.get(color, '#34495e')
            
            self.connection_status_label.setText(f"Connection: {status}")
            self.connection_status_label.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    font-weight: bold;
                    padding: 5px;
                    background-color: {bg_color};
                    border-radius: 3px;
                }}
            """)
    
    # ==================== ORIGINAL METHODS ====================
    
    def _on_tree_size_changed(self, value):
        """Handle tree size slider change"""
        self.tree_size_multiplier = value / 100.0
        self.tree_size_value.setText(f"{value}%")
        
        if self.debug_mode:
            print(f"🎚️ Tree size changed: {value}%")
    
    def _on_pole_height_changed(self, value):
        """Handle pole height slider change"""
        self.pole_height_multiplier = value / 100.0
        self.pole_height_value.setText(f"{value}%")
        
        if self.debug_mode:
            print(f"🎚️ Pole height changed: {value}%")
    
    def _select_tree_placement(self, tree_type):
        """Select tree type and show placement points"""
        try:
            if self.debug_mode:
                print(f"\n🌳 Selecting {tree_type} tree placement...")
            
            self.current_placement_mode = f'tree_{tree_type}'
            
            # Show attachment points if not visible
            if not self.attachment_points_visible:
                self._toggle_attachment_points()
            
            # Emit signal
            self.environment_action_requested.emit('prepare_tree_placement', {
                'tree_type': tree_type,
                'size_multiplier': self.tree_size_multiplier
            })
            
            print(f"✅ Selected {tree_type} tree for placement")
            
        except Exception as e:
            print(f"❌ Error selecting tree placement: {e}")
            QMessageBox.warning(self, "Error", f"Error selecting tree placement: {e}")
    
    def _add_multiple_trees(self, count):
        """Add multiple trees of mixed types"""
        try:
            if self.debug_mode:
                print(f"\n🌲 Adding {count} random trees...")
            
            self.environment_action_requested.emit('add_multiple_trees', {
                'count': count,
                'size_multiplier': self.tree_size_multiplier
            })
            print(f"✅ Requested {count} mixed trees")
            
        except Exception as e:
            print(f"❌ Error adding multiple trees: {e}")
            QMessageBox.warning(self, "Error", f"Error adding multiple trees: {e}")
    
    def _select_pole_placement(self):
        """Select pole and show placement points"""
        try:
            if self.debug_mode:
                print("\n🏗️ Selecting pole placement...")
            
            self.current_placement_mode = 'pole'
            
            # Show attachment points if not visible
            if not self.attachment_points_visible:
                self._toggle_attachment_points()
            
            # Emit signal
            self.environment_action_requested.emit('prepare_pole_placement', {
                'height_multiplier': self.pole_height_multiplier
            })
            
            print("✅ Selected pole for placement")
            
        except Exception as e:
            print(f"❌ Error selecting pole placement: {e}")
            QMessageBox.warning(self, "Error", f"Error selecting pole placement: {e}")
    
    def _add_multiple_poles(self, count):
        """Add multiple poles"""
        try:
            if self.debug_mode:
                print(f"\n🏗️ Adding {count} poles...")
            
            self.environment_action_requested.emit('add_multiple_poles', {
                'count': count,
                'height_multiplier': self.pole_height_multiplier
            })
            print(f"✅ Requested {count} poles")
            
        except Exception as e:
            print(f"❌ Error adding multiple poles: {e}")
            QMessageBox.warning(self, "Error", f"Error adding multiple poles: {e}")
    
    def _toggle_attachment_points(self):
        """Toggle visibility of attachment points"""
        try:
            self.attachment_points_visible = not self.attachment_points_visible
            
            if self.attachment_points_visible:
                self.toggle_points_btn.setText("📍 Hide Points")
                self.toggle_points_btn.setChecked(True)
                if self.debug_mode:
                    print("\n📍 Showing attachment points...")
            else:
                self.toggle_points_btn.setText("📍 Show Points")
                self.toggle_points_btn.setChecked(False)
                if self.debug_mode:
                    print("\n📍 Hiding attachment points...")
            
            self.environment_action_requested.emit('toggle_attachment_points', {
                'visible': self.attachment_points_visible
            })
            
            print(f"✅ Attachment points {'shown' if self.attachment_points_visible else 'hidden'}")
            
        except Exception as e:
            print(f"❌ Error toggling attachment points: {e}")
            QMessageBox.warning(self, "Error", f"Error toggling attachment points: {e}")
    
    def _clear_all_environment(self):
        """Clear all environment objects"""
        try:
            reply = QMessageBox.question(self, "Confirm Clear All", 
                                       "Are you sure you want to clear all environment objects?\n"
                                       "This will remove all trees and poles.",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                if self.debug_mode:
                    print("\n🧹 Clearing all environment objects...")
                
                self.environment_action_requested.emit('clear_all_environment', {})
                print("✅ Requested clear all environment")
                
        except Exception as e:
            print(f"❌ Error clearing environment: {e}")
            QMessageBox.warning(self, "Error", f"Error clearing environment: {e}")
    
    def _auto_populate_scene(self):
        """Automatically populate the scene with a mix of objects"""
        try:
            if self.debug_mode:
                print("\n🎲 Auto-populating scene...")
            
            self.environment_action_requested.emit('auto_populate_scene', {
                'tree_size_multiplier': self.tree_size_multiplier,
                'pole_height_multiplier': self.pole_height_multiplier
            })
            print("✅ Requested auto-populate scene")
            
        except Exception as e:
            print(f"❌ Error auto-populating scene: {e}")
            QMessageBox.warning(self, "Error", f"Error auto-populating scene: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Clear all references
            self.tree_controls.clear()
            self.pole_controls.clear()
            self.size_controls.clear()
            self.current_placement_mode = None
            self.main_window = None
            
            print("✅ EnvironmentTab cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    def _check_roof_status(self):
        """Debug method to check actual roof status"""
        print("\n🔍 CHECKING ROOF STATUS")
        
        model_tab = self._find_model_tab()
        if model_tab:
            print(f"Model tab found: {model_tab}")
            
            # Check current_roof
            if hasattr(model_tab, 'current_roof'):
                roof = model_tab.current_roof
                print(f"current_roof attribute: {roof}")
                if roof:
                    print(f"  Type: {type(roof).__name__}")
                    print(f"  Has handle_environment_action: {hasattr(roof, 'handle_environment_action')}")
                    print(f"  Has environment_manager: {hasattr(roof, 'environment_manager')}")
                else:
                    print("  current_roof is None!")
            else:
                print("No current_roof attribute!")
            
            # Check for other roof references
            for attr in ['roof', 'active_roof', 'building_roof', 'current_building']:
                if hasattr(model_tab, attr):
                    obj = getattr(model_tab, attr)
                    if obj:
                        print(f"Found {attr}: {type(obj).__name__}")
        
        print("="*50)
        