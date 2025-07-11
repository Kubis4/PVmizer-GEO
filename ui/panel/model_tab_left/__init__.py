#!/usr/bin/env python3
"""
panel/3D_model_tab/__init__.py
3D Model Tab Panel Package - Complete with styles/ import
"""

from .datetime_controls import DateTimeControls
from .location_controls import LocationControls
from .modifications_tab import ModificationsTab

# Import UI styles from styles/ folder with fallback
try:
    from styles.ui_styles import UIStyles
    print("✅ UI styles imported from styles/ folder")
except ImportError:
    try:
        from ...styles.ui_styles import UIStyles
        print("✅ UI styles imported with relative path")
    except ImportError:
        print("⚠️ UI styles not found in styles/ folder - modules will use fallback styles")
        UIStyles = None

__all__ = [
    'Model3DTabPanel',
    'DateTimeControls',
    'LocationControls',
    'SolarEffectsControls',
    'ModificationsTab',
]

__version__ = '1.0.0'
__author__ = 'Solar Panel Team'
__description__ = '3D Model Tab Panel with Solar Simulation Controls - Updated for styles/ folder'

print("✅ 3D Model Tab Panel package initialized with styles/ import")
