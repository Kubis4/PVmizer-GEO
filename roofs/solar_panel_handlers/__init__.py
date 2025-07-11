"""
Solar Panel Handlers Package

This package provides solar panel placement handlers for different roof types.
All handlers inherit from BasePanelHandler and share common functionality.
"""

print("🔧 Loading solar panel handlers package...")

# Safe imports - each handler is imported independently
SolarPanelPlacementFlat = None
SolarPanelPlacementGable = None
SolarPanelPlacementHip = None
SolarPanelPlacementPyramid = None

# Import Flat handler
try:
    from .solar_panel_placement_flat import SolarPanelPlacementFlat
    print("✅ SolarPanelPlacementFlat imported")
except Exception as e:
    print(f"⚠️ SolarPanelPlacementFlat import failed: {e}")

# Import Gable handler
try:
    from .solar_panel_placement_gable import SolarPanelPlacementGable
    print("✅ SolarPanelPlacementGable imported")
except Exception as e:
    print(f"⚠️ SolarPanelPlacementGable import failed: {e}")
    import traceback
    traceback.print_exc()

# Import Hip handler
try:
    from .solar_panel_placement_hip import SolarPanelPlacementHip
    print("✅ SolarPanelPlacementHip imported")
except Exception as e:
    print(f"⚠️ SolarPanelPlacementHip import failed: {e}")

# Import Pyramid handler
try:
    from .solar_panel_placement_pyramid import SolarPanelPlacementPyramid
    print("✅ SolarPanelPlacementPyramid imported")
except Exception as e:
    print(f"⚠️ SolarPanelPlacementPyramid import failed: {e}")

# Version info
__version__ = "2.0.0"
__author__ = "Your Name"

# Export only successfully imported handlers
__all__ = []
if SolarPanelPlacementFlat:
    __all__.append('SolarPanelPlacementFlat')
if SolarPanelPlacementGable:
    __all__.append('SolarPanelPlacementGable')
if SolarPanelPlacementHip:
    __all__.append('SolarPanelPlacementHip')
if SolarPanelPlacementPyramid:
    __all__.append('SolarPanelPlacementPyramid')

print(f"📦 Available handlers: {__all__}")

# Safe factory function
def get_handler_for_roof(roof):
    """
    Factory function to get the appropriate handler for a roof type.
    """
    roof_type = type(roof).__name__.lower()
    
    handler_map = {}
    if SolarPanelPlacementFlat:
        handler_map['flatroof'] = SolarPanelPlacementFlat
    if SolarPanelPlacementGable:
        handler_map['gableroof'] = SolarPanelPlacementGable
    if SolarPanelPlacementHip:
        handler_map['hiproof'] = SolarPanelPlacementHip
    if SolarPanelPlacementPyramid:
        handler_map['pyramidroof'] = SolarPanelPlacementPyramid
    
    if roof_type in handler_map:
        return handler_map[roof_type](roof)
    else:
        available = list(handler_map.keys())
        raise ValueError(f"No handler available for roof type: {roof_type}. Available: {available}")

# Safe handler registry
HANDLER_REGISTRY = {}
if SolarPanelPlacementFlat:
    HANDLER_REGISTRY['flat'] = SolarPanelPlacementFlat
if SolarPanelPlacementGable:
    HANDLER_REGISTRY['gable'] = SolarPanelPlacementGable
if SolarPanelPlacementHip:
    HANDLER_REGISTRY['hip'] = SolarPanelPlacementHip
if SolarPanelPlacementPyramid:
    HANDLER_REGISTRY['pyramid'] = SolarPanelPlacementPyramid

def list_available_handlers():
    """Return list of available handler types"""
    return list(HANDLER_REGISTRY.keys())

def create_handler(roof_type, roof):
    """Create handler by string type name"""
    if roof_type.lower() in HANDLER_REGISTRY:
        return HANDLER_REGISTRY[roof_type.lower()](roof)
    else:
        available = list(HANDLER_REGISTRY.keys())
        raise ValueError(f"Unknown roof type: {roof_type}. Available: {available}")

print("🔧 Solar panel handlers package initialization complete")
