#!/usr/bin/env python3
"""
Enhanced Toolbar Manager - Dark Theme Only
PVmizer GEO - Professional geospatial design tool
"""
from PyQt5.QtWidgets import (QToolBar, QAction, QWidget, QSizePolicy, QMessageBox, 
                            QMenu, QToolButton, QFileDialog, QLabel, QFrame, 
                            QHBoxLayout, QVBoxLayout, QDialog, QPushButton, QScrollArea)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPalette, QColor
from PyQt5.QtCore import QSize, QUrl, Qt, QTimer, pyqtSignal
import json
import os
from datetime import datetime

# Import text content
try:
    from ui.toolbar.toolbar_texts import ToolbarTexts
except ImportError:
    ToolbarTexts = None

# Import styling
try:
    from ui.styles.toolbar_styles import ToolbarStyles
except ImportError:
    ToolbarStyles = None

# Import the separate ProjectWizard class
try:
    from ui.wizard_form.project_wizard import ProjectWizard
except ImportError:
    ProjectWizard = None

class ToolbarManager:
    """Enhanced toolbar manager with dark theme styling"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.settings_menu = None
        self.project_menu = None
        self.current_project = None
        self.project_display_label = None
        self.project_display_frame = None
        self.toolbar = None
        
        # Store references to menu actions for dynamic updates
        self.save_action = None
        self.save_as_action = None
        self.edit_action = None
        self.close_action = None
    
    def setup_toolbar(self):
        """Setup the enhanced toolbar"""
        self.toolbar = QToolBar("PVmizer GEO Quick Actions")
        self.toolbar.setIconSize(QSize(28, 28))
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Apply enhanced toolbar styling
        self._apply_toolbar_styling()
        
        self.main_window.addToolBar(self.toolbar)
        
        # LEFT SECTION - Navigation & Project
        home_btn = self._create_button("🏠 Home", "Return to home location", "primary")
        home_btn.clicked.connect(self._go_home)
        self.toolbar.addWidget(home_btn)
        
        self.toolbar.addSeparator()
        
        project_btn = self._create_dropdown_button("📁 Project", "Project management")
        self._setup_project_menu(project_btn)
        self.toolbar.addWidget(project_btn)
        
        # CENTER SECTION - SIMPLIFIED Single Container
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(left_spacer)
        
        self.project_display_frame = self._create_simple_project_display()
        self.toolbar.addWidget(self.project_display_frame)
        
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(right_spacer)
        
        # RIGHT SECTION - Settings & Actions
        settings_btn = self._create_dropdown_button("⚙️ Settings", "Application settings")
        self._setup_simplified_settings_menu(settings_btn)
        self.toolbar.addWidget(settings_btn)
        
        self.toolbar.addSeparator()
        
        help_btn = self._create_button("❓ Help", "Show help information", "help")
        help_btn.clicked.connect(self._show_help)
        self.toolbar.addWidget(help_btn)
        
        # Exit button
        exit_btn = self._create_button("✕ Exit", "Exit PVmizer GEO (Ctrl+Q)", "danger")
        exit_btn.clicked.connect(self._exit_application)
        self.toolbar.addWidget(exit_btn)
        
        self._setup_keyboard_shortcuts()
        self.update_project_display()
    
    def _apply_toolbar_styling(self):
        """Apply enhanced styling to the main toolbar"""
        try:
            if ToolbarStyles:
                self.toolbar.setStyleSheet(ToolbarStyles.get_toolbar_style(True))
        except Exception as e:
            pass
    
    def _create_button(self, text, tooltip, button_type="default"):
        """Create a styled button with FIXED width"""
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip)
        button.setFixedSize(120, 50)
        button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self._apply_button_styling(button, button_type)
        return button

    def _create_dropdown_button(self, text, tooltip):
        """Create a styled dropdown button with FIXED width"""
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip)
        button.setPopupMode(QToolButton.InstantPopup)
        button.setFixedSize(120, 50)
        button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self._apply_dropdown_styling(button)
        return button
    
    def _apply_button_styling(self, button, button_type):
        """Apply styling based on button type"""
        try:
            if not ToolbarStyles:
                return
            
            if button_type == "primary":
                button.setStyleSheet(ToolbarStyles.get_button_style(True))
            elif button_type == "danger":
                button.setStyleSheet(ToolbarStyles.get_exit_button_style(True))
            elif button_type == "help":
                button.setStyleSheet(ToolbarStyles.get_button_style(True))
            else:  # default
                button.setStyleSheet(ToolbarStyles.get_button_style(True))
        except Exception as e:
            pass
    
    def _apply_dropdown_styling(self, button):
        """Apply dropdown-specific styling"""
        try:
            if ToolbarStyles:
                button.setStyleSheet(ToolbarStyles.get_dropdown_button_style(True))
        except Exception as e:
            pass
    
    def _create_simple_project_display(self):
        """SIMPLIFIED: Create single container with just project name and client name"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.NoFrame)
        frame.setMinimumWidth(280)
        frame.setMaximumWidth(400)
        frame.setMinimumHeight(40)
        frame.setCursor(Qt.PointingHandCursor)
        
        # Simple layout
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(0)
        
        # Single label for project display
        self.project_display_label = QLabel("No Project Active")
        self.project_display_label.setAlignment(Qt.AlignCenter)
        self.project_display_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(self.project_display_label)
        
        # Apply simple elegant styling
        self._apply_simple_project_styling(frame)
        
        # Override mousePressEvent for the frame
        frame.mousePressEvent = self._project_frame_clicked
        
        return frame
    
    def _project_frame_clicked(self, event):
        """Handle mouse click on project frame"""
        if event.button() == Qt.LeftButton:
            self._show_project_info_dialog()
    
    def _apply_simple_project_styling(self, frame):
        """Apply simple, clean styling to project display"""
        try:
            if ToolbarStyles:
                base_style = ToolbarStyles.get_project_frame_style(True)
                hover_style = """
                    QFrame:hover { 
                        background-color: #34495e; 
                        border: 1px solid #3498db;
                    }
                """
                frame.setStyleSheet(base_style + hover_style)
        except Exception as e:
            pass
    
    def _setup_project_menu(self, button):
        """Setup project menu"""
        self.project_menu = QMenu(self.main_window)
        self._apply_menu_styling(self.project_menu)
        
        # New Project
        new_action = QAction("🆕 New Project", self.main_window)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_project)
        self.project_menu.addAction(new_action)
        
        # Load Project
        load_action = QAction("📂 Load Project", self.main_window)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._load_project)
        self.project_menu.addAction(load_action)
        
        self.project_menu.addSeparator()
        
        # Save actions
        self.save_action = QAction("💾 Save Project", self.main_window)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save_project)
        self.save_action.setEnabled(False)
        self.project_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("💾 Save As...", self.main_window)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._save_project_as)
        self.save_as_action.setEnabled(False)
        self.project_menu.addAction(self.save_as_action)
        
        self.project_menu.addSeparator()
        
        # Edit Project
        self.edit_action = QAction("📝 Edit Project", self.main_window)
        self.edit_action.triggered.connect(self._edit_current_project)
        self.edit_action.setEnabled(False)
        self.project_menu.addAction(self.edit_action)
        
        self.project_menu.addSeparator()
        
        # Export and Close
        export_menu = self.project_menu.addMenu("📤 Export")
        self._setup_export_menu(export_menu)
        
        self.close_action = QAction("❌ Close Project", self.main_window)
        self.close_action.triggered.connect(self._close_project)
        self.close_action.setEnabled(False)
        self.project_menu.addAction(self.close_action)
        
        button.setMenu(self.project_menu)
    
    def _setup_simplified_settings_menu(self, button):
        """Setup simplified settings menu"""
        self.settings_menu = QMenu(self.main_window)
        self._apply_menu_styling(self.settings_menu)
        
        # About
        about_action = QAction("📋 About", self.main_window)
        about_action.triggered.connect(self._show_about)
        self.settings_menu.addAction(about_action)
        
        button.setMenu(self.settings_menu)
    
    def _setup_export_menu(self, export_menu):
        """Setup export submenu"""
        self._apply_menu_styling(export_menu)
        
        data_action = QAction("📊 Export Project Data", self.main_window)
        data_action.triggered.connect(self._export_project_data)
        export_menu.addAction(data_action)
        
        model_action = QAction("🏗️ Export 3D Model", self.main_window)
        model_action.triggered.connect(self._export_3d_model)
        export_menu.addAction(model_action)
        
        report_action = QAction("📋 Export Report", self.main_window)
        report_action.triggered.connect(self._export_report)
        export_menu.addAction(report_action)
    
    def _apply_menu_styling(self, menu):
        """Apply enhanced menu styling"""
        try:
            if ToolbarStyles:
                menu.setStyleSheet(ToolbarStyles.get_menu_style(True))
        except Exception as e:
            pass
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = [
            ("Ctrl+N", self._new_project),
            ("Ctrl+O", self._load_project),
            ("Ctrl+S", self._save_project),
            ("Ctrl+Shift+S", self._save_project_as),
            ("Ctrl+Q", self._exit_application),
            ("F1", self._show_help),
        ]
        
        for shortcut, method in shortcuts:
            action = QAction(f"Shortcut {shortcut}", self.main_window)
            action.setShortcut(shortcut)
            action.triggered.connect(method)
            self.main_window.addAction(action)
    
    def update_project_display(self, project_name=None, client_name=None):
        """Update simple project display"""
        try:
            if self.project_display_label:
                if project_name and client_name:
                    # Truncate if too long for the simplified display
                    if len(project_name) > 15:
                        project_name = project_name[:12] + "..."
                    if len(client_name) > 15:
                        client_name = client_name[:12] + "..."
                    
                    display_text = f"{project_name} | {client_name}"
                    tooltip = f"Active Project: {project_name}\nClient: {client_name}\nClick for details"
                    
                elif project_name:
                    if len(project_name) > 30:
                        project_name = project_name[:27] + "..."
                    display_text = project_name
                    tooltip = f"Active Project: {project_name}\nClick for details"
                    
                else:
                    display_text = "No Project Active"
                    tooltip = "No project is currently loaded. Create or load a project to start working."
                
                self.project_display_label.setText(display_text)
                self.project_display_frame.setToolTip(tooltip)
        
        except Exception as e:
            pass
    
    def refresh_toolbar_theme(self):
        """Refresh toolbar styling when theme changes"""
        try:
            if self.toolbar:
                self._apply_toolbar_styling()
            
            # Refresh all buttons
            for widget in self.toolbar.findChildren(QToolButton):
                widget_text = widget.text()
                
                if "Project" in widget_text or "Settings" in widget_text:
                    self._apply_dropdown_styling(widget)
                elif "Exit" in widget_text:
                    self._apply_button_styling(widget, "danger")
                elif "Help" in widget_text:
                    self._apply_button_styling(widget, "help")
                elif "Home" in widget_text:
                    self._apply_button_styling(widget, "primary")
                else:
                    self._apply_button_styling(widget, "default")
            
            # Refresh simple project display
            if self.project_display_frame:
                self._apply_simple_project_styling(self.project_display_frame)
            
            # Refresh menus
            for menu in [self.project_menu, self.settings_menu]:
                if menu:
                    self._apply_menu_styling(menu)
            
        except Exception as e:
            pass
    
    # =======================================
    # **PROJECT MANAGEMENT METHODS**
    # =======================================
    
    def _new_project(self):
        """Create new project"""
        try:
            if ProjectWizard is None:
                QMessageBox.warning(self.main_window, "Feature Unavailable", 
                                   ToolbarTexts.get_feature_unavailable_text("wizard") if ToolbarTexts else "Project wizard unavailable.")
                return
            
            wizard = ProjectWizard(self.main_window, edit_mode=False)
            wizard.project_created.connect(self._on_project_created)
            wizard.exec_()
            
        except Exception as e:
            pass
    
    def _edit_current_project(self):
        """Edit current project"""
        try:
            if not self.current_project:
                QMessageBox.warning(self.main_window, "No Project", "No project is currently active.")
                return
            
            if ProjectWizard is None:
                QMessageBox.warning(self.main_window, "Feature Unavailable", 
                                   ToolbarTexts.get_feature_unavailable_text("wizard") if ToolbarTexts else "Project wizard unavailable.")
                return
            
            wizard = ProjectWizard(self.main_window, edit_mode=True, existing_data=self.current_project)
            wizard.project_created.connect(self._on_project_updated)
            wizard.exec_()
            
        except Exception as e:
            pass
    
    def _on_project_created(self, project_data):
        """Handle project creation"""
        try:
            self.current_project = project_data
            self._update_ui_for_active_project()
            self._auto_save_project()
            
        except Exception as e:
            pass
    
    def _on_project_updated(self, project_data):
        """Handle project update"""
        try:
            self.current_project = project_data
            self._update_ui_for_active_project()
            
            project_name = project_data['basic_info']['project_name']
            self.main_window.statusBar().showMessage(f"Project '{project_name}' updated")
            
        except Exception as e:
            pass
    
    def _load_project(self):
        """Load project from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Load PVmizer GEO Project",
                self._get_projects_directory(),
                "PVmizer Project Files (*.pvgeo);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                if self._validate_project_data(project_data):
                    self.current_project = project_data
                    self._update_ui_for_active_project()
                    
                    project_name = project_data['basic_info']['project_name']
                    self.main_window.statusBar().showMessage(f"Project '{project_name}' loaded")
                else:
                    QMessageBox.warning(self.main_window, "Invalid Project", 
                                       "The selected file is not a valid PVmizer GEO project.")
                    
        except Exception as e:
            QMessageBox.critical(self.main_window, "Load Error", f"Failed to load project: {str(e)}")
    
    def _save_project(self):
        """Save current project"""
        try:
            if not self.current_project:
                QMessageBox.warning(self.main_window, "No Project", "No project is currently active.")
                return
            
            if 'file_path' in self.current_project.get('metadata', {}):
                file_path = self.current_project['metadata']['file_path']
            else:
                self._save_project_as()
                return
            
            self._save_project_to_path(file_path)
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Save Error", f"Failed to save project: {str(e)}")
    
    def _save_project_as(self):
        """Save project with new name"""
        try:
            if not self.current_project:
                QMessageBox.warning(self.main_window, "No Project", "No project is currently active.")
                return
            
            project_name = self.current_project['basic_info']['project_name']
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            default_filename = f"{safe_name}.pvgeo"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save PVmizer GEO Project As",
                os.path.join(self._get_projects_directory(), default_filename),
                "PVmizer Project Files (*.pvgeo);;JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                self._save_project_to_path(file_path)
                
        except Exception as e:
            QMessageBox.critical(self.main_window, "Save Error", f"Failed to save project: {str(e)}")
    
    def _save_project_to_path(self, file_path):
        """Save project to specific path"""
        try:
            self.current_project['metadata']['last_saved'] = datetime.now().isoformat()
            self.current_project['metadata']['file_path'] = file_path
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_project, f, indent=2, ensure_ascii=False)
            
            self.main_window.statusBar().showMessage(f"Project saved to {os.path.basename(file_path)}")
            
        except Exception as e:
            raise Exception(f"Failed to save to {file_path}: {str(e)}")
    
    def _close_project(self):
        """Close current project"""
        try:
            if not self.current_project:
                return
            
            reply = QMessageBox.question(
                self.main_window,
                "Close Project",
                "Are you sure you want to close the current project?\nAny unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.current_project = None
                self.main_window.setWindowTitle("PVmizer GEO - Enhanced Building Designer")
                self.main_window.statusBar().showMessage("Project closed")
                self._update_project_menu_state(False)
                self.update_project_display()
                
        except Exception as e:
            pass
    
    def _show_project_info_dialog(self):
        """Show project information in a dialog with Edit button"""
        try:
            if not self.current_project:
                QMessageBox.information(self.main_window, "No Project", "No project is currently active.")
                return
            
            # Create custom dialog
            dialog = QDialog(self.main_window)
            dialog.setWindowTitle("Project Information")
            dialog.setMinimumWidth(500)
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            
            # Main layout
            layout = QVBoxLayout(dialog)
            
            # Format project info
            if ToolbarTexts:
                info_text = ToolbarTexts.format_project_info(self.current_project)
            else:
                info_text = "<p>Project information unavailable (ToolbarTexts not loaded).</p>"
            
            # Create a container widget with explicit ID for styling
            container = QWidget()
            container.setObjectName("container")
            container_layout = QVBoxLayout(container)
            
            # Add info label to container
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setTextFormat(Qt.RichText)
            info_label.setOpenExternalLinks(True)
            container_layout.addWidget(info_label)
            
            # Create scroll area and add container
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(container)
            scroll.setMinimumHeight(300)
            layout.addWidget(scroll)
            
            # Button layout
            button_layout = QHBoxLayout()
            
            # Edit button
            edit_button = QPushButton("📝 Edit Project")
            edit_button.setMinimumWidth(120)
            edit_button.clicked.connect(lambda: [dialog.accept(), self._edit_current_project()])
            
            # Close button
            close_button = QPushButton("✓ OK")
            close_button.setMinimumWidth(80)
            close_button.clicked.connect(dialog.accept)
            
            button_layout.addStretch()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)
            
            # Apply styling with direct background control
            try:
                if ToolbarStyles:
                    # Get styles and colors
                    dialog_style, bg_color, text_color = ToolbarStyles.get_dialog_style(True)
                    
                    # Apply dialog style
                    dialog.setStyleSheet(dialog_style)
                    
                    # Force background colors directly on widgets that might not inherit correctly
                    container.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")
                    scroll.setStyleSheet(f"background-color: {bg_color};")
                    
                    # Also set palette for container for double safety
                    palette = container.palette()
                    palette.setColor(QPalette.Window, QColor(bg_color))
                    palette.setColor(QPalette.WindowText, QColor(text_color))
                    container.setPalette(palette)
                    container.setAutoFillBackground(True)
                
            except Exception as e:
                pass
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            pass

    def _auto_save_project(self):
        """Auto-save project"""
        try:
            if not self.current_project:
                return
            
            projects_dir = self._get_projects_directory()
            os.makedirs(projects_dir, exist_ok=True)
            
            project_name = self.current_project['basic_info']['project_name']
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"autosave_{safe_name}_{timestamp}.pvgeo"
            
            file_path = os.path.join(projects_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_project, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            pass
    
    def _validate_project_data(self, data):
        """Validate project data"""
        try:
            required_keys = ['metadata', 'basic_info', 'energy_info', 'location_info']
            
            for key in required_keys:
                if key not in data:
                    return False
            
            if 'project_name' not in data['basic_info']:
                return False
                
            return True
            
        except Exception as e:
            return False
    
    def _update_ui_for_active_project(self):
        """Update UI for active project"""
        try:
            if self.current_project:
                basic_info = self.current_project['basic_info']
                project_name = basic_info['project_name']
                client_name = basic_info.get('client_name', '')
                
                self.main_window.setWindowTitle(f"PVmizer GEO - {project_name}")
                self.update_project_display(project_name, client_name)
                self._update_project_menu_state(True)
                self.main_window.statusBar().showMessage(f"Project '{project_name}' is active")
        
        except Exception as e:
            pass
    
    def _update_project_menu_state(self, project_active):
        """Update project menu state"""
        try:
            actions = [self.save_action, self.save_as_action, self.edit_action, self.close_action]
            
            for action in actions:
                if action:
                    action.setEnabled(project_active)
                    
        except Exception as e:
            pass
    
    def _get_projects_directory(self):
        """Get projects directory"""
        return os.path.join(os.path.expanduser("~"), ".pvmizer_geo", "projects")
    
    def get_current_project(self):
        """Get current project"""
        return self.current_project
    
    # =======================================
    # **EXPORT METHODS**
    # =======================================
    
    def _export_project_data(self):
        """Export project data"""
        try:
            if not self.current_project:
                QMessageBox.warning(self.main_window, "No Project", "No project is currently active.")
                return
            
            QMessageBox.information(
                self.main_window,
                "Export Project Data",
                ToolbarTexts.get_export_info_text("data") if ToolbarTexts else "Export feature not implemented yet."
            )
            
        except Exception as e:
            pass
    
    def _export_3d_model(self):
        """Export 3D model"""
        try:
            QMessageBox.information(
                self.main_window,
                "Export 3D Model",
                ToolbarTexts.get_export_info_text("model") if ToolbarTexts else "Export feature not implemented yet."
            )
        except Exception as e:
            pass
    
    def _export_report(self):
        """Export report"""
        try:
            QMessageBox.information(
                self.main_window,
                "Export Report",
                ToolbarTexts.get_export_info_text("report") if ToolbarTexts else "Export feature not implemented yet."
            )
        except Exception as e:
            pass
    
    # =======================================
    # **SETTINGS & APPLICATION METHODS**
    # =======================================
    
    def _go_home(self):
        """Navigate to home location"""
        try:
            if hasattr(self.main_window, 'content_tabs') and hasattr(self.main_window.content_tabs, 'satellite_view'):
                home_url = "https://www.google.com/maps/@48.3084263,18.0875649,15.96z/data=!3m1!1e3"
                self.main_window.content_tabs.satellite_view.setUrl(QUrl(home_url))
                self.main_window.statusBar().showMessage("Navigating to home location")
                
                self.main_window.content_tabs.setCurrentIndex(0)
                if hasattr(self.main_window, 'left_panel'):
                    self.main_window.left_panel.switch_to_tab_content(0)
            else:
                self.main_window.statusBar().showMessage("Satellite view not available")
        except Exception as e:
            pass
    
    def _exit_application(self):
        """Exit application"""
        try:
            unsaved_changes = bool(self.current_project)
            
            message = "Are you sure you want to exit PVmizer GEO?"
            if unsaved_changes:
                message += "\n\nYou have an active project. Make sure to save your work before exiting."
            
            reply = QMessageBox.question(
                self.main_window,
                "Exit PVmizer GEO",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if hasattr(self.main_window, 'config'):
                    try:
                        self.main_window.config.save_settings()
                    except Exception as e:
                        pass
                
                self.main_window.close()
                
                from PyQt5.QtWidgets import QApplication
                QApplication.quit()
            else:
                self.main_window.statusBar().showMessage("Exit cancelled")
                
        except Exception as e:
            self.main_window.close()
    
    def _create_styled_message_box(self, title, text, icon=QMessageBox.Information):
        """Create styled message box"""
        msg_box = QMessageBox(self.main_window)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        try:
            if ToolbarStyles:
                msg_box_style = """
                    QMessageBox {
                        background-color: #2c3e50; color: #ecf0f1;
                        border: 2px solid #34495e; border-radius: 8px;
                    }
                    QMessageBox QLabel {
                        color: #ecf0f1; font-size: 13px; padding: 10px;
                    }
                    QMessageBox QPushButton {
                        background-color: #3498db; color: white; border: none;
                        border-radius: 6px; padding: 8px 16px; min-width: 80px; font-weight: bold;
                    }
                    QMessageBox QPushButton:hover { background-color: #2980b9; }
                    QMessageBox QPushButton:pressed { background-color: #21618c; }
                """
                msg_box.setStyleSheet(msg_box_style)
        except Exception as e:
            pass
        
        return msg_box
    
    def _show_about(self):
        """Show about dialog"""
        try:
            if ToolbarTexts:
                enhanced_mode = getattr(self.main_window.config, 'enhanced_mode', False) if hasattr(self.main_window, 'config') else False
                project_active = bool(self.current_project)
                
                about_text = ToolbarTexts.get_about_text("Dark", enhanced_mode, project_active)
            else:
                about_text = "<h3>🌍 PVmizer GEO</h3><p>Professional geospatial design tool.</p>"
            
            msg_box = self._create_styled_message_box("About PVmizer GEO", about_text)
            msg_box.exec_()
            
        except Exception as e:
            pass
    
    def _show_help(self):
        """Show help dialog"""
        try:
            if ToolbarTexts:
                help_text = ToolbarTexts.get_help_text()
            else:
                help_text = "<h3>🌍 PVmizer GEO Help</h3><p>Help content unavailable.</p>"
            
            msg_box = self._create_styled_message_box("Help - PVmizer GEO", help_text)
            msg_box.exec_()
            
        except Exception as e:
            pass
