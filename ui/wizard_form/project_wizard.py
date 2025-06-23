#!/usr/bin/env python3
"""
Enhanced Project Wizard with edit mode support
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QStackedWidget, QProgressBar, QLabel, QMessageBox,
                            QWidget, QFrame)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime

# Import our separate CSS styles and steps
try:
    from ui.styles.wizard_styles import WizardStyles
    from ui.wizard_form.project_steps import (BasicInfoStep, LocationStep, EnergyStep, 
                                TechnicalStep, SummaryStep)
except ImportError:
    # Fallback for direct execution
    from ui.styles.wizard_styles import WizardStyles
    from project_steps import (BasicInfoStep, LocationStep, EnergyStep, 
                               TechnicalStep, SummaryStep)

class ProjectWizard(QDialog):
    """Enhanced Project Creation/Edit Wizard"""
    
    project_created = pyqtSignal(dict)
    
    def __init__(self, parent=None, edit_mode=False, existing_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.edit_mode = edit_mode
        self.existing_data = existing_data or {}
        self.current_step = 0
        self.project_data = {}
        self.steps = []
        
        # Setup UI
        self.setWindowTitle("✏️ Edit Project" if edit_mode else "🚀 Create New Project")
        self.setModal(True)
        self.resize(750, 600)
        self.setMinimumSize(700, 550)
        
        self._setup_ui()
        self._create_steps()
        self._load_existing_data()
        self._apply_theme()
        self._update_step_display()
        
        # Apply theme after a brief delay to ensure all widgets are ready
        QTimer.singleShot(100, self._ensure_theme_applied)
    
    def _setup_ui(self):
        """Setup the wizard UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header section
        self._create_header_section(layout)
        
        # Progress section
        self._create_progress_section(layout)
        
        # Main content area
        self._create_content_section(layout)
        
        # Navigation section
        self._create_navigation_section(layout)
    
    def _create_header_section(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 15)
        header_layout.setSpacing(8)
        
        # Main title
        title_text = "✏️ Edit Solar Project" if self.edit_mode else "🚀 Create New Solar Project"
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_text = "Update project information" if self.edit_mode else "Setup your new solar installation project"
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setObjectName("subtitleLabel")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def _create_progress_section(self, layout):
        """Create progress section"""
        progress_frame = QFrame()
        progress_frame.setObjectName("progressFrame")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(25, 15, 25, 15)
        
        # Step indicator
        step_layout = QHBoxLayout()
        self.step_label = QLabel("Step 1 of 5: Basic Information")
        self.step_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.step_label.setObjectName("stepLabel")
        step_layout.addWidget(self.step_label)
        step_layout.addStretch()
        progress_layout.addLayout(step_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 5)
        self.progress_bar.setValue(1)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
    
    def _create_content_section(self, layout):
        """Create main content section"""
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        layout.addWidget(self.stack)
    
    def _create_navigation_section(self, layout):
        """Create navigation section"""
        nav_frame = QFrame()
        nav_frame.setObjectName("navFrame")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(25, 20, 25, 20)
        nav_layout.setSpacing(15)
        
        # Back button
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setEnabled(False)
        self.back_btn.setMinimumWidth(100)
        nav_layout.addWidget(self.back_btn)
        
        nav_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumWidth(100)
        nav_layout.addWidget(cancel_btn)
        
        # Next/Finish button
        next_text = "✅ Update Project" if self.edit_mode else "Next ➡️"
        self.next_btn = QPushButton(next_text)
        self.next_btn.clicked.connect(self._go_next)
        self.next_btn.setMinimumWidth(120)
        nav_layout.addWidget(self.next_btn)
        
        layout.addWidget(nav_frame)
    
    def _create_steps(self):
        """Create all wizard steps"""
        try:
            self.steps = [
                BasicInfoStep(self),
                LocationStep(self),
                EnergyStep(self),
                TechnicalStep(self),
                SummaryStep(self)
            ]
            
            # Add steps to stack widget
            for step in self.steps:
                self.stack.addWidget(step)
                
            print(f"✅ Created {len(self.steps)} wizard steps")
            
        except Exception as e:
            print(f"❌ Error creating wizard steps: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create wizard steps: {e}")
    
    def _load_existing_data(self):
        """Load existing project data if in edit mode"""
        if self.edit_mode and self.existing_data:
            try:
                print("📂 Loading existing project data into wizard...")
                for step in self.steps:
                    if hasattr(step, 'load_data'):
                        step.load_data(self.existing_data)
                print("✅ Successfully loaded existing project data")
            except Exception as e:
                print(f"⚠️ Error loading existing data: {e}")
    
    def _apply_theme(self):
        """Apply theme styling using separate CSS"""
        try:
            # Check if parent has dark theme
            dark_theme = False
            if self.parent_window and hasattr(self.parent_window, 'config'):
                dark_theme = getattr(self.parent_window.config, 'dark_theme', False)
            
            print(f"🎨 Applying {'dark' if dark_theme else 'light'} theme to wizard...")
            
            # Get styles from external module
            if dark_theme:
                self.setStyleSheet(WizardStyles.get_dark_theme())
            else:
                self.setStyleSheet(WizardStyles.get_light_theme())
            
            # Force dialog background
            self._force_dialog_background(dark_theme)
            
            # Apply theme to all steps
            self._apply_theme_to_all_steps(dark_theme)
            
            print("✅ Theme applied successfully")
            
        except Exception as e:
            print(f"⚠️ Error applying theme: {e}")    
    
    def _force_dialog_background(self, dark_theme):
        """Force dialog background using palette"""
        self.setAutoFillBackground(True)
        palette = self.palette()
        
        if dark_theme:
            palette.setColor(palette.Window, QColor("#2c3e50"))
            palette.setColor(palette.WindowText, QColor("#ecf0f1"))
        else:
            palette.setColor(palette.Window, QColor("#ffffff"))
            palette.setColor(palette.WindowText, QColor("#2c3e50"))
        
        self.setPalette(palette)
        
        # Also apply to stack widget
        if hasattr(self, 'stack'):
            self.stack.setAutoFillBackground(True)
            self.stack.setPalette(palette)
    
    def _apply_theme_to_all_steps(self, dark_theme):
        """Apply theme to all step widgets"""
        if not self.steps:
            return
        
        bg_color = QColor("#2c3e50") if dark_theme else QColor("#ffffff")
        text_color = QColor("#ecf0f1") if dark_theme else QColor("#2c3e50")
        
        for i, step in enumerate(self.steps):
            try:
                # Apply CSS theme from external module
                if dark_theme:
                    step.setStyleSheet(WizardStyles.get_dark_theme())
                else:
                    step.setStyleSheet(WizardStyles.get_light_theme())
                
                # Force background with palette
                step.setAutoFillBackground(True)
                step_palette = step.palette()
                step_palette.setColor(step_palette.Window, bg_color)
                step_palette.setColor(step_palette.WindowText, text_color)
                step.setPalette(step_palette)
                
                print(f"✅ Applied theme to step {i+1}: {step.__class__.__name__}")
                
            except Exception as e:
                print(f"⚠️ Error applying theme to step {i+1}: {e}")
    
    def _ensure_theme_applied(self):
        """Ensure theme is properly applied to all widgets"""
        try:
            self._apply_theme()
            # Force a repaint
            self.update()
            if hasattr(self, 'stack'):
                self.stack.update()
            print("🔄 Theme re-applied and widgets updated")
        except Exception as e:
            print(f"⚠️ Error in theme ensure: {e}")
    
    def _update_step_display(self):
        """Update step display and navigation"""
        if not self.steps:
            return
        
        try:
            # Update stack widget
            self.stack.setCurrentIndex(self.current_step)
            
            # Update progress
            self.progress_bar.setValue(self.current_step + 1)
            
            # Update step label
            step_names = [
                "Basic Information", "Location Details", "Energy Data",
                "Technical Details", "Review & Summary"
            ]
            step_name = step_names[self.current_step] if self.current_step < len(step_names) else "Unknown"
            self.step_label.setText(f"Step {self.current_step + 1} of {len(self.steps)}: {step_name}")
            
            # Update navigation buttons
            self.back_btn.setEnabled(self.current_step > 0)
            
            if self.current_step == len(self.steps) - 1:
                finish_text = "✅ Update Project" if self.edit_mode else "✅ Create Project"
                self.next_btn.setText(finish_text)
            else:
                self.next_btn.setText("Next ➡️")
            
            # Update summary if on last step
            if self.current_step == len(self.steps) - 1:
                self._update_summary()
            
        except Exception as e:
            print(f"⚠️ Error updating step display: {e}")
    
    def _update_summary(self):
        """Update summary step with collected data"""
        try:
            if len(self.steps) > 0:
                summary_step = self.steps[-1]
                if hasattr(summary_step, 'update_summary'):
                    # Collect all data
                    all_data = {}
                    for step in self.steps[:-1]:  # Exclude summary step itself
                        if hasattr(step, 'get_data'):
                            step_data = step.get_data()
                            all_data.update(step_data)
                    
                    summary_step.update_summary(all_data)
        except Exception as e:
            print(f"⚠️ Error updating summary: {e}")
    
    def _go_next(self):
        """Go to next step or finish wizard"""
        try:
            # Validate current step
            current_step_widget = self.steps[self.current_step]
            if hasattr(current_step_widget, 'validate') and not current_step_widget.validate():
                return
            
            # Collect data from current step
            if hasattr(current_step_widget, 'get_data'):
                step_data = current_step_widget.get_data()
                self.project_data.update(step_data)
            
            # Check if this is the last step
            if self.current_step == len(self.steps) - 1:
                self._finish_wizard()
                return
            
            # Move to next step
            self.current_step += 1
            self._update_step_display()
            
        except Exception as e:
            print(f"⚠️ Error going to next step: {e}")
            QMessageBox.warning(self, "Error", f"Error proceeding to next step: {e}")
    
    def _go_back(self):
        """Go to previous step"""
        try:
            if self.current_step > 0:
                self.current_step -= 1
                self._update_step_display()
        except Exception as e:
            print(f"⚠️ Error going back: {e}")
    
    def _finish_wizard(self):
        """Finish wizard and emit project data"""
        try:
            # Collect final data from all steps
            final_data = {}
            for step in self.steps[:-1]:  # Exclude summary step
                if hasattr(step, 'get_data'):
                    step_data = step.get_data()
                    final_data.update(step_data)
            
            # Add metadata
            if self.edit_mode:
                # Keep existing metadata but update modified date
                final_data['metadata'] = self.existing_data.get('metadata', {})
                final_data['metadata']['modified_date'] = datetime.now().isoformat()
            else:
                # Create new metadata
                final_data['metadata'] = {
                    "created_date": datetime.now().isoformat(),
                    "modified_date": datetime.now().isoformat(),
                    "version": "2.0.0",
                    "software": "PVmizer GEO",
                    "project_id": f"PVG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            
            # Add design data section if not exists
            if 'design_data' not in final_data:
                final_data['design_data'] = {
                    "roof_outline": [],
                    "solar_panels": [],
                    "system_calculations": {}
                }
            
            # Emit project data
            self.project_created.emit(final_data)
            
            # Show success message
            project_name = final_data.get('basic_info', {}).get('project_name', 'Untitled Project')
            action = "updated" if self.edit_mode else "created"
            QMessageBox.information(
                self, 
                f"Project {action.title()}", 
                f"Project '{project_name}' {action} successfully!"
            )
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            error_msg = f"Failed to {'update' if self.edit_mode else 'create'} project: {str(e)}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def showEvent(self, event):
        """Override showEvent to ensure proper theming"""
        super().showEvent(event)
        # Re-apply theme when dialog is shown
        QTimer.singleShot(50, self._ensure_theme_applied)

# Backward compatibility alias
ProjectDialog = ProjectWizard