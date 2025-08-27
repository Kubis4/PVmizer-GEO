#!/usr/bin/env python3
"""
ui/panel/model_tab_left/environment_tab.py
Environment obstacles panel for adding trees and poles to the surroundings
CLEANED - No debug prints, no hardcoded styles
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

class EnvironmentTab(QWidget):
    """Environment obstacles tab for adding trees and poles"""
    
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
        self.debug_mode = False
        self.connection_verified = False
        self.signal_connected = False
        
        self.setup_ui()
        
        # Auto-check connection after initialization
        if self.debug_mode:
            QTimer.singleShot(1000, self._initial_connection_check)
    
    def setup_ui(self):
        """Setup environment tab UI"""
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
        debug_layout.addWidget(self.connection_status_label)
        
        # Debug buttons row 1
        debug_row1 = QHBoxLayout()
        
        # Test Connection Button
        test_conn_btn = QPushButton("🧪 Test Connection")
        test_conn_btn.setMinimumHeight(30)
        test_conn_btn.clicked.connect(self._test_connection)
        test_conn_btn.setToolTip("Test if environment system is connected")
        debug_row1.addWidget(test_conn_btn)
        
        # Fix Connection Button
        fix_conn_btn = QPushButton("🔧 Fix Connection")
        fix_conn_btn.setMinimumHeight(30)
        fix_conn_btn.clicked.connect(self._fix_connection)
        fix_conn_btn.setToolTip("Attempt to fix broken connection")
        debug_row1.addWidget(fix_conn_btn)
        
        debug_layout.addLayout(debug_row1)
        
        # Debug buttons row 2
        debug_row2 = QHBoxLayout()
        
        # Force Show Points Button
        force_show_btn = QPushButton("🔴 Force Red Spheres")
        force_show_btn.setMinimumHeight(30)
        force_show_btn.clicked.connect(self._force_show_points)
        force_show_btn.setToolTip("Force show red test spheres in 3D view")
        debug_row2.addWidget(force_show_btn)
        
        # Direct Render Test Button
        render_test_btn = QPushButton("🎯 Direct Render")
        render_test_btn.setMinimumHeight(30)
        render_test_btn.clicked.connect(self._direct_render_test)
        render_test_btn.setToolTip("Test direct rendering to plotter")
        debug_row2.addWidget(render_test_btn)
        
        debug_layout.addLayout(debug_row2)
        
        # Debug info button
        debug_info_btn = QPushButton("📊 Full Debug Info")
        debug_info_btn.setMinimumHeight(30)
        debug_info_btn.clicked.connect(self._show_full_debug_info)
        debug_info_btn.setToolTip("Show complete debug information")
        debug_layout.addWidget(debug_info_btn)
        
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
        tree_size_layout.addWidget(self.tree_size_value)
        
        size_layout.addLayout(tree_size_layout)
        
        # Pole height control
        pole_height_layout = QHBoxLayout()
        pole_height_label = QLabel("Pole Height:")
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
        buttons_layout.addWidget(clear_all_btn)
        
        management_layout.addLayout(buttons_layout)
        
        # Auto-populate button
        auto_populate_btn = QPushButton("🎲 Auto-Populate")
        auto_populate_btn.setMinimumHeight(35)
        auto_populate_btn.clicked.connect(lambda: self._auto_populate_scene())
        auto_populate_btn.setToolTip("Automatically add trees and poles")
        management_layout.addWidget(auto_populate_btn)
        
        layout.addWidget(management_group)
        self.management_group = management_group
    
    # ==================== DEBUG METHODS ====================
    
    def _initial_connection_check(self):
        """Check connection status on startup"""
        if self.debug_mode:
            self._test_connection()
    
    def _find_model_tab(self):
        """Find the model tab through various paths"""
        # Method 1: Through content_tabs
        if hasattr(self.main_window, 'content_tabs'):
            content_tabs = self.main_window.content_tabs
            
            # Check if content_tabs has model_tab
            if hasattr(content_tabs, 'model_tab'):
                return content_tabs.model_tab
            
            # Also check get_model_tab method
            if hasattr(content_tabs, 'get_model_tab'):
                model_tab = content_tabs.get_model_tab()
                if model_tab:
                    return model_tab
        
        # Method 2: Direct attribute
        if hasattr(self.main_window, 'model_tab'):
            return self.main_window.model_tab
        
        # Method 3: Through tab_manager
        if hasattr(self.main_window, 'tab_manager'):
            tab_manager = self.main_window.tab_manager
            if hasattr(tab_manager, 'model_tab'):
                return tab_manager.model_tab
        
        # Method 4: Through component_manager
        if hasattr(self.main_window, 'component_manager'):
            comp_mgr = self.main_window.component_manager
            if hasattr(comp_mgr, 'model_tab'):
                return comp_mgr.model_tab
        
        return None
    
    def _test_connection(self):
        """Test if the environment system is connected"""
        status_messages = []
        
        # Check signal
        if hasattr(self, 'environment_action_requested'):
            # Test signal emission
            test_received = [False]
            
            @pyqtSlot(str, dict)
            def test_receiver(action, params):
                if action == 'test_connection':
                    test_received[0] = True
            
            self.environment_action_requested.connect(test_receiver)
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
        """Attempt to fix broken connection"""
        try:
            # Find model tab using the fixed method
            model_tab = self._find_model_tab()
            
            if model_tab:
                # Try to connect
                if hasattr(model_tab, 'connect_environment_tab'):
                    result = model_tab.connect_environment_tab(self)
                    if result:
                        self._update_connection_status("Connected", "green")
                        QMessageBox.information(self, "Success", 
                                              "✅ Connection fixed successfully!")
                    else:
                        self._update_connection_status("Fix Failed", "orange")
                        QMessageBox.warning(self, "Failed", 
                                          "❌ Could not fix connection")
                else:
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
                        self._update_connection_status("Connected", "green")
                        QMessageBox.information(self, "Success", 
                                              "✅ Connection established dynamically!")
                    else:
                        QMessageBox.warning(self, "Failed", 
                                          "Could not establish connection")
            else:
                QMessageBox.critical(self, "Error", 
                                   "Cannot find model tab.\n"
                                   "Please ensure a building is created first.")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Fix failed: {str(e)}")
    
    def _force_show_points(self):
        """Force show attachment points with highly visible red spheres"""
        try:
            # Find model tab using the fixed method
            model_tab = self._find_model_tab()
            
            if not model_tab:
                QMessageBox.warning(self, "Error", 
                                   "Model tab not found.\n"
                                   "Please create a building first.")
                return
            
            if not hasattr(model_tab, 'plotter') or not model_tab.plotter:
                QMessageBox.warning(self, "Error", "3D plotter not found")
                return
            
            plotter = model_tab.plotter
            
            if not PYVISTA_AVAILABLE:
                QMessageBox.warning(self, "Error", "PyVista not available for rendering")
                return
            
            # Create highly visible test spheres
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
            
            # Add ground reference
            ground = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), 
                            i_size=20, j_size=20)
            plotter.add_mesh(
                ground,
                color='lightgray',
                opacity=0.5,
                name='test_ground'
            )
            
            # Force render
            plotter.render()
            
            # Reset camera
            plotter.reset_camera()
            
            QMessageBox.information(self, "Success", 
                                   "8 red spheres should now be visible in the 3D view")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")
    
    def _direct_render_test(self):
        """Test direct rendering to plotter"""
        try:
            # Find model tab using the fixed method
            model_tab = self._find_model_tab()
            
            if model_tab and hasattr(model_tab, 'plotter') and model_tab.plotter:
                plotter = model_tab.plotter
                
                if not PYVISTA_AVAILABLE:
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
                
                # Force render
                plotter.render()
                
                QMessageBox.information(self, "Success", 
                                      "A big yellow sphere should be visible at the center")
            else:
                QMessageBox.warning(self, "Error", "No plotter available")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Render failed: {str(e)}")
    
    def _show_full_debug_info(self):
        """Show complete debug information"""
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
        
        # Show in message box
        QMessageBox.information(self, "Debug Information", 
                               "\n".join(info))
    
    def _update_connection_status(self, status, color):
        """Update connection status label"""
        if hasattr(self, 'connection_status_label'):
            self.connection_status_label.setText(f"Connection: {status}")
    
    # ==================== ORIGINAL METHODS ====================
    
    def _on_tree_size_changed(self, value):
        """Handle tree size slider change"""
        self.tree_size_multiplier = value / 100.0
        self.tree_size_value.setText(f"{value}%")
    
    def _on_pole_height_changed(self, value):
        """Handle pole height slider change"""
        self.pole_height_multiplier = value / 100.0
        self.pole_height_value.setText(f"{value}%")
    
    def _select_tree_placement(self, tree_type):
        """Select tree type and show placement points"""
        try:
            self.current_placement_mode = f'tree_{tree_type}'
            
            # Show attachment points if not visible
            if not self.attachment_points_visible:
                self._toggle_attachment_points()
            
            # Emit signal
            self.environment_action_requested.emit('prepare_tree_placement', {
                'tree_type': tree_type,
                'size_multiplier': self.tree_size_multiplier
            })
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error selecting tree placement: {e}")
    
    def _add_multiple_trees(self, count):
        """Add multiple trees of mixed types"""
        try:
            self.environment_action_requested.emit('add_multiple_trees', {
                'count': count,
                'size_multiplier': self.tree_size_multiplier
            })
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error adding multiple trees: {e}")
    
    def _select_pole_placement(self):
        """Select pole and show placement points"""
        try:
            self.current_placement_mode = 'pole'
            
            # Show attachment points if not visible
            if not self.attachment_points_visible:
                self._toggle_attachment_points()
            
            # Emit signal
            self.environment_action_requested.emit('prepare_pole_placement', {
                'height_multiplier': self.pole_height_multiplier
            })
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error selecting pole placement: {e}")
    
    def _add_multiple_poles(self, count):
        """Add multiple poles"""
        try:
            self.environment_action_requested.emit('add_multiple_poles', {
                'count': count,
                'height_multiplier': self.pole_height_multiplier
            })
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error adding multiple poles: {e}")
    
    def _toggle_attachment_points(self):
        """Toggle visibility of attachment points"""
        try:
            self.attachment_points_visible = not self.attachment_points_visible
            
            if self.attachment_points_visible:
                self.toggle_points_btn.setText("📍 Hide Points")
                self.toggle_points_btn.setChecked(True)
            else:
                self.toggle_points_btn.setText("📍 Show Points")
                self.toggle_points_btn.setChecked(False)
            
            self.environment_action_requested.emit('toggle_attachment_points', {
                'visible': self.attachment_points_visible
            })
            
        except Exception as e:
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
                self.environment_action_requested.emit('clear_all_environment', {})
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error clearing environment: {e}")
    
    def _auto_populate_scene(self):
        """Automatically populate the scene with a mix of objects"""
        try:
            self.environment_action_requested.emit('auto_populate_scene', {
                'tree_size_multiplier': self.tree_size_multiplier,
                'pole_height_multiplier': self.pole_height_multiplier
            })
            
        except Exception as e:
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
            
        except Exception as e:
            pass

    def _check_roof_status(self):
        """Debug method to check actual roof status"""
        model_tab = self._find_model_tab()
        if model_tab:
            # Check current_roof
            if hasattr(model_tab, 'current_roof'):
                roof = model_tab.current_roof
                if roof:
                    pass
                else:
                    pass
            else:
                pass
            
            # Check for other roof references
            for attr in ['roof', 'active_roof', 'building_roof', 'current_building']:
                if hasattr(model_tab, attr):
                    obj = getattr(model_tab, attr)
                    if obj:
                        pass
