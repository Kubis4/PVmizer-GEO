"""
Utility modules for solar panel handlers.

This package contains shared utilities used by all panel handlers:
- Resource loading and texture management
- Performance calculations  
- Obstacle detection algorithms
"""

from .solar_panel_utils import (
    resource_path,
    load_panel_texture,
    PanelGeometry
)

from .panel_performance import PerformanceCalculator

from .obstacle_detection import ObstacleDetector

__all__ = [
    'resource_path',
    'load_panel_texture', 
    'PanelGeometry',
    'PerformanceCalculator',
    'ObstacleDetector'
]