#!/usr/bin/env python3
"""
Enhanced Project Wizard with edit mode support - Dark theme only
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
    """Enhanced Project Creation/Edit Wizard - Dark theme only"""
    
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
        
        # Navigation buttons
        self._create_navigation_section(layout)
    
    def _create_header_section(self, layout):
        """Create wizard header with title"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title = QLabel("✏️ Edit Project" if self.edit_mode else "🚀 Create New Project")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("", 16, QFont.Bold))
        header_layout.addWidget(title)
        
        layout.addWidget(header_frame)
    
    def _create_progress_section(self, layout):
        """Create progress bar and step indicator"""
        progress_frame = QFrame()
        progress_frame.setFixedHeight(80)
        progress_layout = QVBoxLayout(progress_frame)
        
        # Step label
        self.step_label = QLabel("Step 1 of 5: Basic Information")
        self.step_label.setAlignment(Qt.AlignCenter)
        self.step_label.setFont(QFont("", 12))
        progress_layout.addWidget(self.step_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(1)
        self.progress_bar.setMaximum(5)
        self.progress_bar.setValue(1)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
    
    def _create_content_section(self, layout):
        """Create main content area with stacked widget"""
        # Content frame with border
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Stacked widget for steps
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        layout.addWidget(content_frame)
    
    def _create_navigation_section(self, layout):
        """Create navigation buttons"""
        nav_frame = QFrame()
        nav_frame.setFixedHeight(60)
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        
        # Cancel button
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        nav_layout.addWidget(self.cancel_btn)
        
        nav_layout.addStretch()
        
        # Back button
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        # Next/Finish button
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self.next_btn)
        
        layout.addWidget(nav_frame)
    
    def _create_steps(self):
        """Create wizard steps"""
        try:
            # Create step instances
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
            # Create a fallback empty widget if step creation fails
            fallback = QWidget()
            self.stack.addWidget(fallback)
            self.steps = [fallback]
    
    def _load_existing_data(self):
        """Load existing project data if in edit mode"""
        if not self.edit_mode or not self.existing_data:
            return
            
        try:
            # Load data into each step
            for step in self.steps:
                if hasattr(step, 'load_data'):
                    step.load_data(self.existing_data)
            print("✅ Successfully loaded existing project data")
        except Exception as e:
            print(f"⚠️ Error loading existing data: {e}")
    
    def _apply_theme(self):
        """Apply dark theme styling only"""
        try:
            print("🎨 Applying dark theme to wizard...")
            
            # Always use dark theme
            self.setStyleSheet(WizardStyles.get_dark_theme())
            
            # Force dialog background to dark
            self._force_dialog_background()
            
            # Apply theme to all steps
            self._apply_theme_to_all_steps()
            
            print("✅ Dark theme applied successfully")
            
        except Exception as e:
            print(f"⚠️ Error applying theme: {e}")    
    
    def _force_dialog_background(self):
        """Force dark dialog background"""
        self.setAutoFillBackground(True)
        palette = self.palette()
        
        # Always use dark theme colors
        palette.setColor(palette.Window, QColor("#2c3e50"))
        palette.setColor(palette.WindowText, QColor("#ecf0f1"))
        
        self.setPalette(palette)
        
        # Also apply to stack widget
        if hasattr(self, 'stack'):
            self.stack.setAutoFillBackground(True)
            self.stack.setPalette(palette)
    
    def _apply_theme_to_all_steps(self):
        """Apply dark theme to all step widgets"""
        if not self.steps:
            return
        
        # Always use dark theme colors
        bg_color = QColor("#2c3e50")
        text_color = QColor("#ecf0f1")
        
        for i, step in enumerate(self.steps):
            try:
                # Always apply dark theme CSS
                step.setStyleSheet(WizardStyles.get_dark_theme())
                
                # Force background with palette
                step.setAutoFillBackground(True)
                step_palette = step.palette()
                step_palette.setColor(step_palette.Window, bg_color)
                step_palette.setColor(step_palette.WindowText, text_color)
                step.setPalette(step_palette)
                
                print(f"✅ Applied dark theme to step {i+1}: {step.__class__.__name__}")
                
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
            
            # Update next/finish button
            is_last_step = self.current_step >= len(self.steps) - 1
            self.next_btn.setText("✅ Finish" if is_last_step else "Next ➡️")
            
            print(f"📍 Updated display for step {self.current_step + 1}")
            
        except Exception as e:
            print(f"⚠️ Error updating step display: {e}")
    
    def _go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_display()
            self._ensure_theme_applied()
    
    def _go_next(self):
        """Go to next step or finish"""
        try:
            # Validate current step
            current_step_widget = self.steps[self.current_step]
            if hasattr(current_step_widget, 'validate_step'):
                if not current_step_widget.validate_step():
                    return
            
            # Collect data from current step
            if hasattr(current_step_widget, 'get_data'):
                step_data = current_step_widget.get_data()
                if step_data:
                    self.project_data.update(step_data)
            
            # Check if this is the last step
            if self.current_step >= len(self.steps) - 1:
                self._finish_wizard()
            else:
                # Go to next step
                self.current_step += 1
                self._update_step_display()
                self._ensure_theme_applied()
                
        except Exception as e:
            print(f"❌ Error in go_next: {e}")
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")
    
    def _finish_wizard(self):
        """Finish the wizard and emit project data"""
        try:
            # Collect data from all steps
            final_data = {}
            
            for i, step in enumerate(self.steps):
                if hasattr(step, 'get_data'):
                    step_data = step.get_data()
                    if step_data:
                        final_data.update(step_data)
            
            # Add metadata
            final_data['_metadata'] = {
                'created_at': datetime.now().isoformat() if not self.edit_mode else self.existing_data.get('_metadata', {}).get('created_at'),
                'modified_at': datetime.now().isoformat(),
                'version': '1.0',
                'wizard_type': 'edit' if self.edit_mode else 'create'
            }
            
            # Emit signal with project data
            self.project_created.emit(final_data)
            
            # Show success message
            action = "updated" if self.edit_mode else "created"
            project_name = final_data.get('basic_info', {}).get('project_name', 'Unnamed Project')
            QMessageBox.information(self, "Success", f"Project '{project_name}' {action} successfully!")
            
            self.accept()
            
        except Exception as e:
            print(f"❌ Error finishing wizard: {e}")
            QMessageBox.critical(self, "Error", f"Failed to complete project: {e}")
    
    def get_current_data(self):
        """Get current project data for validation"""
        return self.project_data.copy()
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.project_data:
            reply = QMessageBox.question(
                self, 
                "Confirm Exit",
                "You have unsaved changes. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if not (event.modifiers() & Qt.ControlModifier):
                self._go_next()
        else:
            super().keyPressEvent(event)