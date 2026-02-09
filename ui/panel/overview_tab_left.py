#!/usr/bin/env python3
"""
Overview Tab Left Panel - Analysis controls and export options
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QPushButton, 
                             QLabel, QComboBox)
from PyQt5.QtCore import pyqtSignal, Qt

from ui.panel.base_panel import BaseTabPanel


class OverviewTabPanel(BaseTabPanel):
    """Left panel for Overview tab - Analysis and export controls"""
    
    # Signals
    refresh_requested = pyqtSignal()
    export_requested = pyqtSignal(str)
    
    def __init__(self, main_window, parent=None):
        # Don't call super().__init__() - just QWidget
        QWidget.__init__(self, parent)
        self.main_window = main_window
        
        # Common state from BaseTabPanel
        self.current_month = 6
        self.current_day = 21
        self.current_hour = 12
        self.current_minute = 0
        self.latitude = 40.7128
        self.longitude = -74.0060
        self.weather_factor = 1.0
        
        # Setup UI
        self.setup_ui()
        print("✅ Overview Tab Panel initialized")
    
    def setup_ui(self):
        """Setup Overview tab panel UI - EXACT SAME STYLING as Model3DTabPanel"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop)
        
        # Apply EXACT SAME styling as Model3DTabPanel
        self.setStyleSheet("""
            QWidget {
                background-color: #34495e !important;
            }
            
            /* Group Boxes - EXACT MATCH */
            QGroupBox {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
                margin-top: 15px !important;
                padding-top: 15px !important;
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-bottom: 10px !important;
                font-weight: bold !important;
                font-size: 13px !important;
                color: #ffffff !important;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin !important;
                subcontrol-position: top center !important;
                padding: 4px 15px !important;
                margin-top: 1px !important;
                color: #5dade2 !important;
                background-color: #34495e !important;
                font-size: 20px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
            }
            
            /* Labels - EXACT MATCH */
            QLabel {
                color: #ffffff !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 12px !important;
                font-weight: normal !important;
            }
            
            /* Buttons - EXACT MATCH */
            QPushButton {
                background-color: #5dade2 !important;
                color: #ffffff !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 8px 12px !important;
                font-weight: bold !important;
                font-size: 13px !important;
                min-height: 32px !important;
                text-align: center !important;
            }
            
            QPushButton:hover {
                background-color: #3498db !important;
                border: 2px solid #3498db !important;
                color: #ffffff !important;
            }
            
            QPushButton:pressed {
                background-color: #2980b9 !important;
                border: 2px solid #2980b9 !important;
            }
            
            QPushButton:disabled {
                background-color: #7f8c8d !important;
                border: 2px solid #7f8c8d !important;
                color: #95a5a6 !important;
            }
            
            /* Export Button - Green override */
            QPushButton#exportButton {
                background-color: #27ae60 !important;
                border: 2px solid #27ae60 !important;
            }
            
            QPushButton#exportButton:hover {
                background-color: #229954 !important;
                border: 2px solid #229954 !important;
            }
            
            QPushButton#exportButton:pressed {
                background-color: #1e8449 !important;
                border: 2px solid #1e8449 !important;
            }
            
            /* ComboBoxes - EXACT MATCH */
            QComboBox {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                border: 2px solid #5dade2 !important;
                border-radius: 6px !important;
                padding: 6px !important;
                min-height: 30px !important;
                font-size: 13px !important;
            }
            
            QComboBox:focus {
                border: 2px solid #48a1d6 !important;
            }
            
            QComboBox::drop-down {
                border: none !important;
                background-color: #5dade2 !important;
                width: 25px !important;
                border-top-right-radius: 6px !important;
                border-bottom-right-radius: 6px !important;
            }
            
            QComboBox::down-arrow {
                image: none !important;
                border-left: 5px solid transparent !important;
                border-right: 5px solid transparent !important;
                border-top: 6px solid white !important;
                margin-right: 5px !important;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2c3e50 !important;
                color: #ffffff !important;
                selection-background-color: #5dade2 !important;
                selection-color: #ffffff !important;
                border: 2px solid #5dade2 !important;
            }
        """)
        
        # Data Control Group
        data_group = QGroupBox("📊 Data Control")
        data_group.setMaximumWidth(410)
        data_layout = QVBoxLayout(data_group)
        data_layout.setSpacing(10)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setMaximumWidth(390)
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        data_layout.addWidget(self.refresh_btn)
        
        # Auto-refresh info
        info_label = QLabel("Data refreshes automatically when switching to this tab")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        info_label.setWordWrap(True)
        info_label.setMaximumWidth(390)
        data_layout.addWidget(info_label)
        
        main_layout.addWidget(data_group)
        
        # Export Group
        export_group = QGroupBox("💾 Export Options")
        export_group.setMaximumWidth(410)
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(10)
        
        # Export format selection
        format_label = QLabel("Export Format:")
        export_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF Report", "Excel Spreadsheet", "JSON Data", "CSV Data"])
        self.format_combo.setMaximumWidth(390)
        export_layout.addWidget(self.format_combo)
        
        # Export button
        self.export_btn = QPushButton("📄 Export Data")
        self.export_btn.setObjectName("exportButton")
        self.export_btn.setMaximumWidth(390)
        self.export_btn.clicked.connect(self._on_export_clicked)
        export_layout.addWidget(self.export_btn)
        
        main_layout.addWidget(export_group)
        
        # Statistics Group
        stats_group = QGroupBox("📈 Quick Statistics")
        stats_group.setMaximumWidth(410)
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel(
            "Building: Not created\n"
            "Solar Power: 0.0 kW\n"
            "Environment Objects: 0"
        )
        self.stats_label.setStyleSheet("color: #b8c5ce; font-family: 'Courier New';")
        self.stats_label.setMaximumWidth(390)
        stats_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(stats_group)
        
        # Future Features Group
        future_group = QGroupBox("🚀 Coming Soon")
        future_group.setMaximumWidth(410)
        future_layout = QVBoxLayout(future_group)
        
        future_features = [
            "• Advanced analytics",
            "• Custom reports",
            "• Cloud synchronization",
            "• Comparison tools",
            "• Energy forecasting",
            "• Cost analysis"
        ]
        
        future_label = QLabel("\n".join(future_features))
        future_label.setStyleSheet("color: #7f8c8d;")
        future_label.setMaximumWidth(390)
        future_layout.addWidget(future_label)
        
        main_layout.addWidget(future_group)
        main_layout.addStretch()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click"""
        try:
            print("🔄 Refreshing overview data...")
            self.refresh_data()
            self.refresh_requested.emit()
            
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("✅ Data refreshed", 2000)
        except Exception as e:
            print(f"❌ Error refreshing data: {e}")
    
    def _on_export_clicked(self):
        """Handle export button click"""
        try:
            export_format = self.format_combo.currentText()
            print(f"💾 Exporting data as: {export_format}")
            self.export_requested.emit(export_format)
            
            # Show message (in real implementation, this would save a file)
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    f"Export as {export_format} - Feature coming soon!", 3000
                )
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
    
    def refresh_data(self):
        """Refresh overview data from main window"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                overview_tab = self.main_window.content_tabs.get_overview_tab()
                if overview_tab and hasattr(overview_tab, 'refresh_view'):
                    overview_tab.refresh_view()
                
                # Update quick stats
                if hasattr(self.main_window.content_tabs, 'is_building_created'):
                    building_created = self.main_window.content_tabs.is_building_created()
                    power, energy, efficiency = self.main_window.content_tabs.get_solar_performance()
                    env_stats = self.main_window.content_tabs.get_environment_statistics()
                    
                    total_objects = sum(env_stats.values()) if env_stats else 0
                    
                    stats_text = (
                        f"Building: {'Created' if building_created else 'Not created'}\n"
                        f"Solar Power: {power:.2f} kW\n"
                        f"Environment Objects: {total_objects}"
                    )
                    
                    self.stats_label.setText(stats_text)
        except Exception as e:
            print(f"❌ Error in refresh_data: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.main_window = None
        print("🧹 Overview Tab Panel cleaned up")
