#!/usr/bin/env python3
"""
Default Tab Left Panel - Information and guidance for roof selection
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from ui.panel.base_panel import BaseTabPanel


class DefaultTabPanel(BaseTabPanel):
    """Left panel for Default tab - Guidance and information"""
    
    # Signals
    roof_selected = pyqtSignal(str, dict)
    
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
        print("✅ Default Tab Panel initialized")
    
    def setup_ui(self):
        """Setup Default tab panel UI with guidance and information"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop)
        
        # Apply styling with IMPROVED TEXT VISIBILITY
        self.setStyleSheet("""
            QWidget {
                background-color: #34495e !important;
            }
            
            /* Group Boxes */
            QGroupBox {
                background-color: #34495e !important;
                border: 2px solid #5dade2 !important;
                border-radius: 8px !important;
                margin-top: 15px !important;
                padding-top: 20px !important;
                padding-left: 12px !important;
                padding-right: 12px !important;
                padding-bottom: 12px !important;
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
                font-size: 18px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
            }
            
            /* Labels - IMPROVED VISIBILITY */
            QLabel {
                color: #ecf0f1 !important;
                background-color: transparent !important;
                border: none !important;
                font-size: 13px !important;
                font-weight: normal !important;
                line-height: 1.5 !important;
            }
        """)
        
        # Quick Start Guide
        guide_group = QGroupBox("🚀 Quick Start Guide")
        guide_group.setMaximumWidth(480)
        guide_layout = QVBoxLayout(guide_group)
        guide_layout.setSpacing(8)
        guide_layout.setContentsMargins(15, 22, 15, 15)  # Extra padding to show numbers
        
        steps = [
            "1.  Click on a roof type card",
            "2.  Enter building dimensions",
            "3.  Click 'Generate Roof Model'",
            "4.  View your 3D model in the Model tab",
            "5.  Analyze solar performance"
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("color: #ecf0f1; font-size: 13px; padding: 4px 5px; font-weight: 500;")
            step_label.setMaximumWidth(450)
            guide_layout.addWidget(step_label)
        
        main_layout.addWidget(guide_group)
        
        # Roof Types Information
        roof_types_group = QGroupBox("🏠 Roof Types")
        roof_types_group.setMaximumWidth(480)
        roof_types_layout = QVBoxLayout(roof_types_group)
        roof_types_layout.setSpacing(10)
        roof_types_layout.setContentsMargins(15, 22, 15, 15)
        
        roof_descriptions = [
            ("⬜ Flat Roof", "Simple, modern design ideal for urban buildings. Easy maintenance and installation."),
            ("🏠 Gable Roof", "Classic triangular design. Excellent water drainage and traditional aesthetics."),
            ("🔺 Pyramid Roof", "Four-sided sloped design. Great for square buildings and wind resistance."),
            ("🏔️ Hip Roof", "All sides slope downward. Superior stability and weather protection.")
        ]
        
        for title, description in roof_descriptions:
            # Title
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #5dade2; font-size: 14px; font-weight: bold; padding-top: 3px; padding-left: 3px;")
            title_label.setMaximumWidth(450)
            roof_types_layout.addWidget(title_label)
            
            # Description
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #d5dbdb; font-size: 12px; padding-bottom: 6px; padding-left: 3px;")
            desc_label.setWordWrap(True)
            desc_label.setMaximumWidth(450)
            roof_types_layout.addWidget(desc_label)
        
        main_layout.addWidget(roof_types_group)
        
        # Tips & Recommendations
        tips_group = QGroupBox("💡 Tips & Recommendations")
        tips_group.setMaximumWidth(480)
        tips_layout = QVBoxLayout(tips_group)
        tips_layout.setSpacing(6)
        tips_layout.setContentsMargins(15, 22, 15, 15)
        
        tips = [
            "📏  Accurate dimensions lead to better solar analysis",
            "☀️  Consider your location's sun exposure",
            "🌡️  Different roof types affect thermal performance",
            "⚡  Flat roofs typically offer more panel space",
            "🔧  You can modify settings in the Model tab later"
        ]
        
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setStyleSheet("color: #ecf0f1; font-size: 12px; padding: 3px 5px;")
            tip_label.setWordWrap(True)
            tip_label.setMaximumWidth(450)
            tips_layout.addWidget(tip_label)
        
        main_layout.addWidget(tips_group)
        
        # Features Overview
        features_group = QGroupBox("✨ Available Features")
        features_group.setMaximumWidth(480)
        features_layout = QVBoxLayout(features_group)
        features_layout.setSpacing(6)
        features_layout.setContentsMargins(15, 22, 15, 15)
        
        features = [
            "🏗️  3D roof model generation",
            "☀️  Real-time solar simulation",
            "📊  Performance analytics",
            "🌳  Environment object placement",
            "📈  Energy production estimates",
            "💾  Export capabilities"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("color: #ecf0f1; font-size: 12px; padding: 3px 5px;")
            feature_label.setMaximumWidth(450)
            features_layout.addWidget(feature_label)
        
        main_layout.addWidget(features_group)
        main_layout.addStretch()
    
    def cleanup(self):
        """Cleanup resources"""
        self.main_window = None
        print("🧹 Default Tab Panel cleaned up")
