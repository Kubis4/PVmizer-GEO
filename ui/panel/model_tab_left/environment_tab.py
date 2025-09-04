#!/usr/bin/env python3
"""
ui/panel/model_tab_left/environment_tab.py
Environment obstacles panel for adding trees and poles to the surroundings
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QGroupBox, QMessageBox, QSlider)
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
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
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup environment tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
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
        self.tree_controls['deciduous_btn'] = deciduous_btn
        tree_buttons_layout.addWidget(deciduous_btn)
        
        # Pine tree button
        pine_btn = QPushButton("🌲 Pine")
        pine_btn.setMinimumHeight(32)
        pine_btn.clicked.connect(lambda: self._select_tree_placement('pine'))
        self.tree_controls['pine_btn'] = pine_btn
        tree_buttons_layout.addWidget(pine_btn)
        
        # Oak tree button
        oak_btn = QPushButton("🌰 Oak")
        oak_btn.setMinimumHeight(32)
        oak_btn.clicked.connect(lambda: self._select_tree_placement('oak'))
        self.tree_controls['oak_btn'] = oak_btn
        tree_buttons_layout.addWidget(oak_btn)
        
        trees_layout.addLayout(tree_buttons_layout)
        
        # Quick add button
        add_multiple_btn = QPushButton("🌲 Add 5 Random Trees")
        add_multiple_btn.setMinimumHeight(30)
        add_multiple_btn.clicked.connect(lambda: self._add_multiple_trees(5))
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
        self.pole_controls['single_btn'] = single_pole_btn
        poles_layout.addWidget(single_pole_btn)
        
        # Add multiple poles
        add_poles_btn = QPushButton("🏗️ Add 3 Poles")
        add_poles_btn.setMinimumHeight(30)
        add_poles_btn.clicked.connect(lambda: self._add_multiple_poles(3))
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
        buttons_layout.addWidget(self.toggle_points_btn)
        
        # Clear all environment
        clear_all_btn = QPushButton("🧹 Clear All")
        clear_all_btn.setMinimumHeight(32)
        clear_all_btn.clicked.connect(lambda: self._clear_all_environment())
        buttons_layout.addWidget(clear_all_btn)
        
        management_layout.addLayout(buttons_layout)
        
        # Auto-populate button
        auto_populate_btn = QPushButton("🎲 Auto-Populate")
        auto_populate_btn.setMinimumHeight(35)
        auto_populate_btn.clicked.connect(lambda: self._auto_populate_scene())
        management_layout.addWidget(auto_populate_btn)
        
        layout.addWidget(management_group)
        self.management_group = management_group
    
    def _update_button_states(self):
        """Update button states based on current placement mode"""
        try:
            # Reset all button states
            for btn_name, btn in self.tree_controls.items():
                if btn_name.endswith('_btn'):
                    btn.setStyleSheet("")
            
            if 'single_btn' in self.pole_controls:
                self.pole_controls['single_btn'].setStyleSheet("")
            
            # Highlight active button
            if self.current_placement_mode:
                active_style = "background-color: #3498db; color: white; font-weight: bold;"
                
                if self.current_placement_mode.startswith('tree_'):
                    tree_type = self.current_placement_mode.replace('tree_', '')
                    btn_name = f'{tree_type}_btn'
                    if btn_name in self.tree_controls:
                        self.tree_controls[btn_name].setStyleSheet(active_style)
                
                elif self.current_placement_mode == 'pole':
                    if 'single_btn' in self.pole_controls:
                        self.pole_controls['single_btn'].setStyleSheet(active_style)
        
        except Exception as e:
            pass
    
    # ==================== METHODS ====================
    
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
            self._update_button_states()
            
            # Show attachment points if not visible
            if not self.attachment_points_visible:
                self.attachment_points_visible = True
                self.toggle_points_btn.setText("📍 Hide Points")
                self.toggle_points_btn.setChecked(True)
                
                # Emit signal to show points
                self.environment_action_requested.emit('toggle_attachment_points', {
                    'visible': True
                })
            
            # Emit signal to prepare placement
            self.environment_action_requested.emit('prepare_tree_placement', {
                'tree_type': tree_type,
                'size_multiplier': self.tree_size_multiplier
            })
            
            # Show user instruction
            QMessageBox.information(self, "Tree Placement", 
                                f"{tree_type.title()} tree selected!\n"
                                "Now RIGHT-CLICK on black dots to place trees.\n"
                                "(Points will hide automatically after placement)")
            
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
            self._update_button_states()
            
            # Show attachment points if not visible
            if not self.attachment_points_visible:
                self.attachment_points_visible = True
                self.toggle_points_btn.setText("📍 Hide Points")
                self.toggle_points_btn.setChecked(True)
                
                # Emit signal to show points
                self.environment_action_requested.emit('toggle_attachment_points', {
                    'visible': True
                })
            
            # Emit signal to prepare placement
            self.environment_action_requested.emit('prepare_pole_placement', {
                'height_multiplier': self.pole_height_multiplier
            })
            
            # Show user instruction
            QMessageBox.information(self, "Pole Placement", 
                                "Utility pole selected!\n"
                                "Now RIGHT-CLICK on black dots to place poles.\n"
                                "(Points will hide automatically after placement)")
            
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
                # Clear placement mode
                self.current_placement_mode = None
                self._update_button_states()
                
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
    
    def handle_placement_completed(self):
        """Handle when placement is completed (called from environment manager)"""
        try:
            # Reset button state
            self.attachment_points_visible = False
            self.toggle_points_btn.setText("📍 Show Points")
            self.toggle_points_btn.setChecked(False)
            
            # Clear placement mode
            self.current_placement_mode = None
            self._update_button_states()
            
        except Exception as e:
            pass

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Clear placement mode
            self.current_placement_mode = None
            
            # Clear all references
            self.tree_controls.clear()
            self.pole_controls.clear()
            self.size_controls.clear()
            self.main_window = None
            
        except Exception as e:
            pass
