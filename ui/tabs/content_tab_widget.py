#!/usr/bin/env python3
"""
Content Tab Widget - Default, Model, and Overview Tabs with Full Integration
"""
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QMessageBox, QApplication
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap
import time
import numpy as np
from datetime import datetime

try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

from .model_tab import ModelTab
from .default_tab import DefaultTab
from .overview_tab import OverviewTab

from utils.pyvista_integration import PyVistaIntegration
from utils.solar_event_handlers import SolarEventHandlers
from utils.tab_utilities import TabUtilities


class ContentTabWidget(QTabWidget):
    """Content Tab Widget - Default, Model, and Overview Tabs with Full Integration"""
    
    # Signals
    building_generated = pyqtSignal(object)
    sun_position_changed = pyqtSignal(float, float)
    roof_selected = pyqtSignal(str, dict)  # roof_type, dimensions
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Workflow state tracking
        self.building_created = False
        
        # Debug mode
        self.debug_mode = True
        
        # Initialize utility components
        self._initialize_utilities()
        
        # Create tabs
        self._create_tabs()
        
        # Connect signals
        self._connect_signals()
        
        # Setup tab change handling
        self.currentChanged.connect(self._on_tab_changed)
        
        # Schedule debugging
        if self.debug_mode:
            QTimer.singleShot(2000, self._debug_workflow_state)
    
    def _initialize_utilities(self):
        """Initialize utility components"""
        try:
            self.pyvista_integration = PyVistaIntegration(self)
            if self.debug_mode:
                print("✅ PyVistaIntegration initialized")
        except Exception as e:
            self.pyvista_integration = None
            if self.debug_mode:
                print(f"❌ PyVistaIntegration failed: {e}")
            
        try:
            self.solar_handlers = SolarEventHandlers(self)
            if self.debug_mode:
                print("✅ SolarEventHandlers initialized")
        except Exception as e:
            self.solar_handlers = None
            if self.debug_mode:
                print(f"❌ SolarEventHandlers failed: {e}")
            
        try:
            self.tab_utilities = TabUtilities(self)
            if self.debug_mode:
                print("✅ TabUtilities initialized")
        except Exception as e:
            self.tab_utilities = None
            if self.debug_mode:
                print(f"❌ TabUtilities failed: {e}")
    
    def _create_tabs(self):
        """Create Default, Model, and Overview tabs"""
        # Tab 0: Default Tab (formerly Maps)
        self.default_tab = DefaultTab(self.main_window)
        self.addTab(self.default_tab, "🏠 Default")
        if self.debug_mode:
            print("✅ Default tab created (Tab 0)")
        
        # Tab 1: Model Tab
        self.model_tab = ModelTab(self.main_window)
        self.addTab(self.model_tab, "🏗️ Model")
        if self.debug_mode:
            print("✅ Model tab created (Tab 1)")
        
        # Tab 2: Overview Tab (Future feature)
        self.overview_tab = OverviewTab(self.main_window)
        self.addTab(self.overview_tab, "📊 Overview")
        if self.debug_mode:
            print("✅ Overview tab created (Tab 2)")
    
    def _connect_signals(self):
        """Connect signals from all tabs"""
        signal_count = 0
        
        # Default tab signals
        if self.default_tab:
            try:
                if hasattr(self.default_tab, 'data_loaded'):
                    self.default_tab.data_loaded.connect(self._on_default_data_loaded)
                    signal_count += 1
                if hasattr(self.default_tab, 'data_error'):
                    self.default_tab.data_error.connect(self._on_default_error)
                    signal_count += 1
                if hasattr(self.default_tab, 'roof_selected'):
                    self.default_tab.roof_selected.connect(self._on_roof_selected)
                    signal_count += 1
                if self.debug_mode:
                    print("✅ Default tab signals connected")
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Default tab signals failed: {e}")
        
        # Model tab signals
        if self.model_tab:
            try:
                if hasattr(self.model_tab, 'building_generated'):
                    self.model_tab.building_generated.connect(self._on_building_generated)
                    signal_count += 1
                if hasattr(self.model_tab, 'model_updated'):
                    self.model_tab.model_updated.connect(self._on_model_updated)
                    signal_count += 1
                if hasattr(self.model_tab, 'view_changed'):
                    self.model_tab.view_changed.connect(self._on_view_changed)
                    signal_count += 1
                if hasattr(self.model_tab, 'roof_generated'):
                    self.model_tab.roof_generated.connect(self._on_roof_generated)
                    signal_count += 1
                if self.debug_mode:
                    print("✅ Model tab signals connected")
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Model tab signals failed: {e}")
        
        # Overview tab signals
        if self.overview_tab:
            try:
                if hasattr(self.overview_tab, 'analysis_requested'):
                    self.overview_tab.analysis_requested.connect(self._on_analysis_requested)
                    signal_count += 1
                if hasattr(self.overview_tab, 'export_requested'):
                    self.overview_tab.export_requested.connect(self._on_export_requested)
                    signal_count += 1
                if self.debug_mode:
                    print("✅ Overview tab signals connected")
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Overview tab signals failed: {e}")
        
        if self.debug_mode:
            print(f"📊 Total signals connected: {signal_count}")
    
    def _on_tab_changed(self, index):
        """Handle tab change - Update left panel accordingly"""
        try:
            if self.debug_mode:
                print(f"🔍 Tab changed to {index}")
            
            # Update left panel content based on tab
            if hasattr(self.main_window, 'left_panel'):
                if hasattr(self.main_window.left_panel, 'switch_to_tab_content'):
                    self.main_window.left_panel.switch_to_tab_content(index)
            
            # Update status bar based on active tab
            if hasattr(self.main_window, 'statusBar'):
                if index == 0:  # Default tab
                    self.main_window.statusBar().showMessage(
                        "🏠 Select a roof type from the left panel to begin modeling"
                    )
                elif index == 1:  # Model tab
                    self.main_window.statusBar().showMessage(
                        "🏗️ Adjust building parameters and explore the 3D model"
                    )
                elif index == 2:  # Overview tab
                    self.main_window.statusBar().showMessage(
                        "📊 View project overview and analysis"
                    )
            
            # Refresh views
            if index == 0 and self.default_tab:
                if hasattr(self.default_tab, 'refresh_view'):
                    self.default_tab.refresh_view()
            elif index == 1 and self.model_tab:
                if hasattr(self.model_tab, 'refresh_view'):
                    self.model_tab.refresh_view()
            elif index == 2 and self.overview_tab:
                if hasattr(self.overview_tab, 'refresh_view'):
                    self.overview_tab.refresh_view()
                        
        except Exception as e:
            print(f"Error in tab change handler: {e}")
    
    def _debug_workflow_state(self):
        """Debug current workflow state"""
        try:
            print("🔍 === WORKFLOW STATE DEBUG ===")
            print(f"Building created: {self.building_created}")
            print(f"Current tab: {self.currentIndex()}")
            print(f"Tab count: {self.count()}")
            print(f"Tab 0 name: {self.tabText(0)}")
            print(f"Tab 1 name: {self.tabText(1)}")
            print(f"Tab 2 name: {self.tabText(2)}")
            print("🔍 === WORKFLOW STATE DEBUG END ===")
            
        except Exception as e:
            print(f"❌ Workflow debug failed: {e}")
    
    # ============================================================================
    # SIGNAL HANDLERS
    # ============================================================================
    
    def _on_default_data_loaded(self):
        """Handle default tab data loaded"""
        if self.debug_mode:
            print("✅ Default data loaded successfully")
    
    def _on_default_error(self, error):
        """Handle default tab error"""
        if self.debug_mode:
            print(f"❌ Default tab error: {error}")
    
    def _on_roof_selected(self, roof_type, dimensions):
        """Handle roof selection from default tab"""
        try:
            if self.debug_mode:
                print(f"🏠 Roof selected: {roof_type} with dimensions: {dimensions}")
            
            # Render the roof model
            self.render_roof_model(roof_type, dimensions)
            
        except Exception as e:
            print(f"Error handling roof selection: {e}")
    
    def _on_building_generated(self, building_info):
        """Handle building generation"""
        try:
            if self.debug_mode:
                print("🎯 BUILDING GENERATED - Updating workflow state")
            
            # Update workflow state
            self.building_created = True
            
            # Emit the signal
            self.building_generated.emit(building_info)
            
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "🏗️ 3D building model generated successfully!", 5000
                )
            
            # Enable export button if available
            if (hasattr(self.main_window, 'left_panel') and 
                hasattr(self.main_window.left_panel, 'export_btn')):
                if self.main_window.left_panel.export_btn:
                    self.main_window.left_panel.export_btn.setEnabled(True)
            
            # Update overview tab with building data
            if self.overview_tab and hasattr(self.overview_tab, 'update_building_data'):
                self.overview_tab.update_building_data(building_info)
            
            if self.debug_mode:
                print("✅ Workflow state updated after building generation")
                print(f"   - Building created: {self.building_created}")
            
        except Exception as e:
            print(f"Error handling building generation: {e}")
    
    def _on_model_updated(self, model_info):
        """Handle model update"""
        if self.debug_mode:
            print(f"✅ Model updated: {model_info}")
        
        # Update overview tab
        if self.overview_tab and hasattr(self.overview_tab, 'update_model_data'):
            self.overview_tab.update_model_data(model_info)
    
    def _on_view_changed(self, view_type):
        """Handle view change"""
        if self.debug_mode:
            print(f"✅ View changed to: {view_type}")
    
    def _on_roof_generated(self, roof_object):
        """Handle roof generation"""
        if self.debug_mode:
            print(f"✅ Roof generated: {roof_object}")
        
        # Update overview tab
        if self.overview_tab and hasattr(self.overview_tab, 'update_roof_data'):
            self.overview_tab.update_roof_data(roof_object)
    
    def _on_analysis_requested(self, analysis_type):
        """Handle analysis request from overview tab"""
        if self.debug_mode:
            print(f"📊 Analysis requested: {analysis_type}")
    
    def _on_export_requested(self, export_format):
        """Handle export request from overview tab"""
        if self.debug_mode:
            print(f"💾 Export requested: {export_format}")
    
    # ============================================================================
    # ROOF RENDERING
    # ============================================================================
    
    def render_roof_model(self, roof_type, dimensions):
        """Render roof model in the 3D view"""
        try:
            if self.debug_mode:
                print(f"🏠 Rendering {roof_type} roof with dimensions: {dimensions}")
            
            if self.model_tab and hasattr(self.model_tab, 'render_roof'):
                # Switch to model tab first
                self.setCurrentIndex(1)
                
                # Small delay to ensure tab is fully switched
                QTimer.singleShot(100, lambda: self._execute_roof_render(roof_type, dimensions))
                
                return True
            else:
                if self.debug_mode:
                    print("❌ Model tab or render_roof method not available")
                return False
                
        except Exception as e:
            print(f"❌ Error rendering roof model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _execute_roof_render(self, roof_type, dimensions):
        """Execute the actual roof rendering after tab switch"""
        try:
            # Render the roof
            success = self.model_tab.render_roof(roof_type, dimensions)
            
            if success:
                self.building_created = True
                
                # Update status
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(
                        f"🏠 {roof_type} roof model generated successfully!", 3000
                    )
                
                if self.debug_mode:
                    print(f"✅ {roof_type} roof model rendered successfully")
                
                return True
            else:
                if self.debug_mode:
                    print(f"❌ Failed to render {roof_type} roof")
                
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(
                        f"❌ Failed to generate {roof_type} roof", 3000
                    )
                
                return False
                
        except Exception as e:
            print(f"❌ Error executing roof render: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ============================================================================
    # TAB ACCESS METHODS
    # ============================================================================
    
    def get_default_tab(self):
        """Get default tab"""
        return self.default_tab
    
    def get_model_tab(self):
        """Get model tab"""
        return self.model_tab
    
    def get_overview_tab(self):
        """Get overview tab"""
        return self.overview_tab
    
    def switch_to_default_tab(self):
        """Switch to default tab"""
        self.setCurrentIndex(0)
        if self.debug_mode:
            print("🏠 Switched to Default tab")
    
    def switch_to_model_tab(self):
        """Switch to model tab"""
        self.setCurrentIndex(1)
        if self.debug_mode:
            print("🏗️ Switched to Model tab")
    
    def switch_to_overview_tab(self):
        """Switch to overview tab"""
        self.setCurrentIndex(2)
        if self.debug_mode:
            print("📊 Switched to Overview tab")
    
    # ============================================================================
    # STATE QUERY METHODS
    # ============================================================================
    
    def has_building(self):
        """Check if building exists"""
        try:
            if self.model_tab:
                return self.model_tab.has_building()
            return False
        except Exception as e:
            return False
    
    def is_building_created(self):
        """Check if building has been created"""
        return self.building_created
    
    # ============================================================================
    # WORKFLOW CONTROL
    # ============================================================================
    
    def reset_workflow_state(self):
        """Reset all workflow states (useful for new project)"""
        self.building_created = False
        
        # Switch back to default tab
        self.setCurrentIndex(0)
        
        # Clear model tab
        if self.model_tab:
            if hasattr(self.model_tab, 'cleanup'):
                self.model_tab.cleanup()
        
        # Clear overview tab
        if self.overview_tab:
            if hasattr(self.overview_tab, 'reset'):
                self.overview_tab.reset()
        
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(
                "Workflow reset. Ready for new model.", 2000
            )
        
        if self.debug_mode:
            print("✅ Workflow state reset")
    
    # ============================================================================
    # MODEL TAB UTILITIES
    # ============================================================================
    
    def get_model_plotter(self):
        """Get the plotter from the model tab"""
        try:
            if hasattr(self, 'model_tab'):
                if hasattr(self.model_tab, 'get_plotter'):
                    return self.model_tab.get_plotter()
                
                if hasattr(self.model_tab, 'plotter'):
                    return self.model_tab.plotter
                
                for attr_name in ['pv_widget', 'pyvista_widget', 'vtk_widget']:
                    if hasattr(self.model_tab, attr_name):
                        return getattr(self.model_tab, attr_name)
            
            return None
        except Exception as e:
            print(f"❌ Error getting model plotter: {e}")
            return None
    
    def refresh_model_view(self):
        """Refresh the model view"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'refresh_view'):
                self.model_tab.refresh_view()
                if self.debug_mode:
                    print("✅ Model view refreshed")
        except Exception as e:
            print(f"❌ Error refreshing model view: {e}")
    
    # ============================================================================
    # BUILDING CREATION
    # ============================================================================
    
    def create_building(self, points, height=3.0, roof_type='flat', roof_pitch=30.0, scale=0.05):
        """Create 3D building from points"""
        try:
            if self.model_tab:
                success = self.model_tab.create_building(
                    points=points,
                    height=height,
                    roof_type=roof_type,
                    roof_pitch=roof_pitch,
                    scale=scale
                )
                
                if success:
                    self.building_created = True
                    self.setCurrentIndex(1)  # Switch to model tab
                    
                    if self.debug_mode:
                        print("✅ Building created successfully")
                    
                return success
            return False
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Error creating building: {e}")
            return False
    
    # ============================================================================
    # SOLAR SYSTEM INTEGRATION
    # ============================================================================
    
    def update_solar_time(self, decimal_time):
        """Update solar time in model tab"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'update_solar_time'):
                self.model_tab.update_solar_time(decimal_time)
        except Exception as e:
            print(f"❌ Error updating solar time: {e}")
    
    def update_solar_day(self, day_of_year):
        """Update solar day in model tab"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'update_solar_day'):
                self.model_tab.update_solar_day(day_of_year)
        except Exception as e:
            print(f"❌ Error updating solar day: {e}")
    
    def set_location(self, latitude, longitude):
        """Set location for solar calculations"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'set_location'):
                self.model_tab.set_location(latitude, longitude)
        except Exception as e:
            print(f"❌ Error setting location: {e}")
    
    def set_weather_factor(self, factor):
        """Set weather factor"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'set_weather_factor'):
                self.model_tab.set_weather_factor(factor)
        except Exception as e:
            print(f"❌ Error setting weather factor: {e}")
    
    def toggle_solar_effects(self, shadows=None, sunshafts=None):
        """Toggle solar effects"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'toggle_solar_effects'):
                self.model_tab.toggle_solar_effects(shadows, sunshafts)
        except Exception as e:
            print(f"❌ Error toggling solar effects: {e}")
    
    def set_quality_level(self, quality):
        """Set quality level"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'set_quality_level'):
                self.model_tab.set_quality_level(quality)
        except Exception as e:
            print(f"❌ Error setting quality level: {e}")
    
    def handle_animation_toggle(self, enabled):
        """Handle animation toggle"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'handle_animation_toggle'):
                self.model_tab.handle_animation_toggle(enabled)
        except Exception as e:
            print(f"❌ Error handling animation toggle: {e}")
    
    # ============================================================================
    # ENVIRONMENT INTEGRATION
    # ============================================================================
    
    def connect_environment_tab(self, environment_tab):
        """Connect environment tab to model tab"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'connect_environment_tab'):
                return self.model_tab.connect_environment_tab(environment_tab)
            return False
        except Exception as e:
            print(f"❌ Error connecting environment tab: {e}")
            return False
    
    def add_environment_object(self, object_type, parameters=None):
        """Add environment object"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'add_environment_object'):
                return self.model_tab.add_environment_object(object_type, parameters)
            return False
        except Exception as e:
            print(f"❌ Error adding environment object: {e}")
            return False
    
    def clear_environment_objects(self):
        """Clear all environment objects"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'clear_environment_objects'):
                return self.model_tab.clear_environment_objects()
            return False
        except Exception as e:
            print(f"❌ Error clearing environment objects: {e}")
            return False
    
    def get_environment_statistics(self):
        """Get environment statistics"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'get_environment_statistics'):
                return self.model_tab.get_environment_statistics()
            return {}
        except Exception as e:
            print(f"❌ Error getting environment statistics: {e}")
            return {}
    
    # ============================================================================
    # SOLAR PERFORMANCE
    # ============================================================================
    
    def get_solar_performance(self):
        """Get solar performance metrics"""
        try:
            if self.model_tab and hasattr(self.model_tab, 'get_solar_performance'):
                return self.model_tab.get_solar_performance()
            return (0.0, 0.0, 0.0)
        except Exception as e:
            print(f"❌ Error getting solar performance: {e}")
            return (0.0, 0.0, 0.0)
    
    # ============================================================================
    # CLEANUP
    # ============================================================================
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.debug_mode:
                print("🧹 Cleaning up ContentTabWidget...")
            
            # Cleanup default tab
            if hasattr(self, 'default_tab') and self.default_tab:
                if hasattr(self.default_tab, 'cleanup'):
                    self.default_tab.cleanup()
            
            # Cleanup model tab
            if hasattr(self, 'model_tab') and self.model_tab:
                if hasattr(self.model_tab, 'cleanup'):
                    self.model_tab.cleanup()
            
            # Cleanup overview tab
            if hasattr(self, 'overview_tab') and self.overview_tab:
                if hasattr(self.overview_tab, 'cleanup'):
                    self.overview_tab.cleanup()
            
            # Cleanup utilities
            if hasattr(self, 'pyvista_integration') and self.pyvista_integration:
                if hasattr(self.pyvista_integration, 'cleanup'):
                    self.pyvista_integration.cleanup()
            
            if hasattr(self, 'solar_handlers') and self.solar_handlers:
                if hasattr(self.solar_handlers, 'cleanup'):
                    self.solar_handlers.cleanup()
            
            if hasattr(self, 'tab_utilities') and self.tab_utilities:
                if hasattr(self.tab_utilities, 'cleanup'):
                    self.tab_utilities.cleanup()
            
            if self.debug_mode:
                print("✅ ContentTabWidget cleanup completed")
                
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
