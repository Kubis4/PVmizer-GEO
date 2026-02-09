#!/usr/bin/env python3
"""
Overview Tab - Project overview and analysis with dark theme matching the app
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QGridLayout, QFrame, QScrollArea)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class OverviewTab(QWidget):
    """Overview tab - Project statistics and analysis with dark theme"""
    
    # Signals
    analysis_requested = pyqtSignal(str)
    export_requested = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Data storage
        self.building_data = None
        self.model_data = None
        self.roof_data = None
        
        self.setup_ui()
        print("✅ Overview Tab initialized")
    
    def setup_ui(self):
        """Setup Overview tab UI with dark theme matching the app"""
        # Apply dark theme to entire tab
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title with dark theme
        title = QLabel("📊 Project Overview")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            color: #5dade2;
            background-color: transparent;
            padding: 10px;
        """)
        main_layout.addWidget(title)
        
        # Scroll area for content with dark theme
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #34495e;
                width: 12px;
                border-radius: 6px;
                border: 1px solid #5dade2;
            }
            QScrollBar::handle:vertical {
                background-color: #5dade2;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3498db;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Building Information Group
        building_group = self._create_building_info_group()
        content_layout.addWidget(building_group)
        
        # Solar Performance Group
        solar_group = self._create_solar_performance_group()
        content_layout.addWidget(solar_group)
        
        # Environment Statistics Group
        env_group = self._create_environment_stats_group()
        content_layout.addWidget(env_group)
        
        # Placeholder for future features
        future_group = self._create_future_features_group()
        content_layout.addWidget(future_group)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        print("✅ Overview Tab UI setup completed")
    
    def _create_building_info_group(self):
        """Create building information group with dark theme"""
        group = QGroupBox("🏗️ Building Information")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #34495e;
                color: #ffffff;
                border: 2px solid #5dade2;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                padding-left: 10px;
                padding-right: 10px;
                padding-bottom: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 4px 15px;
                color: #5dade2;
                background-color: #34495e;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 10)
        
        # Labels with dark theme
        self.roof_type_label = QLabel("Roof Type: Not set")
        self.roof_type_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.dimensions_label = QLabel("Dimensions: Not set")
        self.dimensions_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.area_label = QLabel("Area: Not set")
        self.area_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.created_label = QLabel("Created: Not set")
        self.created_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        # Add to layout
        layout.addWidget(self.roof_type_label, 0, 0)
        layout.addWidget(self.dimensions_label, 1, 0)
        layout.addWidget(self.area_label, 2, 0)
        layout.addWidget(self.created_label, 3, 0)
        
        return group
    
    def _create_solar_performance_group(self):
        """Create solar performance group with dark theme"""
        group = QGroupBox("☀️ Solar Performance")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #34495e;
                color: #ffffff;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                padding-left: 10px;
                padding-right: 10px;
                padding-bottom: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 4px 15px;
                color: #f39c12;
                background-color: #34495e;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 10)
        
        # Labels with dark theme
        self.power_label = QLabel("Current Power: 0.0 kW")
        self.power_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.energy_label = QLabel("Daily Energy: 0.0 kWh")
        self.energy_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.efficiency_label = QLabel("Efficiency: 0.0%")
        self.efficiency_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        # Add to layout
        layout.addWidget(self.power_label, 0, 0)
        layout.addWidget(self.energy_label, 1, 0)
        layout.addWidget(self.efficiency_label, 2, 0)
        
        return group
    
    def _create_environment_stats_group(self):
        """Create environment statistics group with dark theme"""
        group = QGroupBox("🌳 Environment Objects")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #34495e;
                color: #ffffff;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                padding-left: 10px;
                padding-right: 10px;
                padding-bottom: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 4px 15px;
                color: #27ae60;
                background-color: #34495e;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 10)
        
        # Labels with dark theme
        self.trees_label = QLabel("Trees: 0")
        self.trees_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.poles_label = QLabel("Poles: 0")
        self.poles_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        self.obstacles_label = QLabel("Total Obstacles: 0")
        self.obstacles_label.setStyleSheet("color: #ecf0f1; background-color: transparent; font-size: 13px;")
        
        # Add to layout
        layout.addWidget(self.trees_label, 0, 0)
        layout.addWidget(self.poles_label, 1, 0)
        layout.addWidget(self.obstacles_label, 2, 0)
        
        return group
    
    def _create_future_features_group(self):
        """Create future features placeholder with dark theme"""
        group = QGroupBox("🚀 Coming Soon")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #34495e;
                color: #ffffff;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                padding-left: 10px;
                padding-right: 10px;
                padding-bottom: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 4px 15px;
                color: #9b59b6;
                background-color: #34495e;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        features = [
            "📈 Detailed solar analysis charts",
            "📊 Energy production graphs",
            "💰 Cost-benefit analysis",
            "🗺️ Shadow analysis maps",
            "📄 Automated report generation",
            "☁️ Weather integration",
            "📱 Export to mobile formats"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setStyleSheet("""
                color: #b8c5ce;
                background-color: transparent;
                padding: 5px;
                font-size: 12px;
            """)
            layout.addWidget(label)
        
        return group
    
    def update_building_data(self, building_info):
        """Update building information display"""
        try:
            self.building_data = building_info
            
            if isinstance(building_info, dict):
                # Update roof type
                roof_type = building_info.get('roof_type', 'Unknown')
                self.roof_type_label.setText(f"Roof Type: {roof_type.capitalize()}")
                
                # Update dimensions
                dimensions = building_info.get('dimensions', {})
                if dimensions:
                    dim_text = f"Length: {dimensions.get('length', 0):.2f}m, Width: {dimensions.get('width', 0):.2f}m, Height: {dimensions.get('height', 0):.2f}m"
                    self.dimensions_label.setText(f"Dimensions: {dim_text}")
                    
                    # Calculate area
                    area = dimensions.get('length', 0) * dimensions.get('width', 0)
                    self.area_label.setText(f"Area: {area:.2f} m²")
                
                # Update created time
                created_at = building_info.get('created_at', 'Unknown')
                if hasattr(created_at, 'strftime'):
                    created_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
                    self.created_label.setText(f"Created: {created_str}")
            
            print("✅ Building data updated in Overview tab")
            
        except Exception as e:
            print(f"❌ Error updating building data: {e}")
    
    def update_model_data(self, model_info):
        """Update model information display"""
        try:
            self.model_data = model_info
            print("✅ Model data updated in Overview tab")
        except Exception as e:
            print(f"❌ Error updating model data: {e}")
    
    def update_roof_data(self, roof_object):
        """Update roof information display"""
        try:
            self.roof_data = roof_object
            print("✅ Roof data updated in Overview tab")
        except Exception as e:
            print(f"❌ Error updating roof data: {e}")
    
    def update_solar_performance(self, power, energy, efficiency):
        """Update solar performance display"""
        try:
            self.power_label.setText(f"Current Power: {power:.2f} kW")
            self.energy_label.setText(f"Daily Energy: {energy:.2f} kWh")
            self.efficiency_label.setText(f"Efficiency: {efficiency:.1f}%")
        except Exception as e:
            print(f"❌ Error updating solar performance: {e}")
    
    def update_environment_stats(self, stats):
        """Update environment statistics display"""
        try:
            if isinstance(stats, dict):
                total_trees = (stats.get('deciduous_trees', 0) + 
                              stats.get('pine_trees', 0) + 
                              stats.get('oak_trees', 0))
                poles = stats.get('poles', 0)
                total = total_trees + poles
                
                self.trees_label.setText(f"Trees: {total_trees}")
                self.poles_label.setText(f"Poles: {poles}")
                self.obstacles_label.setText(f"Total Obstacles: {total}")
        except Exception as e:
            print(f"❌ Error updating environment stats: {e}")
    
    def refresh_view(self):
        """Refresh the overview view with latest data"""
        try:
            # Get solar performance from main window
            if hasattr(self.main_window, 'content_tabs'):
                power, energy, efficiency = self.main_window.content_tabs.get_solar_performance()
                self.update_solar_performance(power, energy, efficiency)
                
                # Get environment stats
                stats = self.main_window.content_tabs.get_environment_statistics()
                self.update_environment_stats(stats)
            
            print("🔄 Overview view refreshed")
        except Exception as e:
            print(f"❌ Error refreshing overview: {e}")
    
    def reset(self):
        """Reset overview data"""
        self.building_data = None
        self.model_data = None
        self.roof_data = None
        
        # Reset labels
        self.roof_type_label.setText("Roof Type: Not set")
        self.dimensions_label.setText("Dimensions: Not set")
        self.area_label.setText("Area: Not set")
        self.created_label.setText("Created: Not set")
        
        self.power_label.setText("Current Power: 0.0 kW")
        self.energy_label.setText("Daily Energy: 0.0 kWh")
        self.efficiency_label.setText("Efficiency: 0.0%")
        
        self.trees_label.setText("Trees: 0")
        self.poles_label.setText("Poles: 0")
        self.obstacles_label.setText("Total Obstacles: 0")
        
        print("✅ Overview tab reset")
    
    def cleanup(self):
        """Cleanup resources"""
        self.reset()
        print("🧹 Overview tab cleaned up")
