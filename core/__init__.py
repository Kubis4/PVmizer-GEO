"""
Core module for PVmizer GEO
Provides modular architecture for main window functionality
"""

from .window_manager import WindowManager
from .component_manager import ComponentManager
from .signal_manager import SignalManager
from .tab_manager import TabManager
from .building_manager import BuildingManager
from .canvas_manager import CanvasManager
from .debug_manager import DebugManager
from .event_manager import EventManager
from .initialization_manager import InitializationManager
from .roof_generation_manager import RoofGenerationManager

__all__ = [
    'WindowManager',
    'ComponentManager', 
    'SignalManager',
    'TabManager',
    'BuildingManager',
    'CanvasManager',
    'DebugManager',
    'EventManager',
    'InitializationManager',
    'RoofGenerationManager'
]