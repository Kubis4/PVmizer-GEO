"""
Configuration settings for solar panel handlers
"""

# Default panel specifications (in millimeters)
DEFAULT_PANEL_CONFIG = {
    'panel_width': 1000,
    'panel_length': 1600,
    'panel_gap': 50,
    'panel_power': 400,
    'edge_offset': 300,
    'panel_height': 10,
    'horizontal_edge_offset': 300,
    'vertical_edge_offset': 300
}

# Roof-specific configurations
ROOF_SPECIFIC_CONFIG = {
    'flat': {
        'panel_tilt': 0.0,
        'panel_orientation': 180.0,
        'row_spacing_factor': 1.0
    },
    'gable': {
        'min_slope_angle': 15,  # degrees
        'max_slope_angle': 60,  # degrees
        'panel_height': 0,      # ✅ ADDED: Smaller offset for gable roofs
        'panel_offset': 0       # ✅ ADDED: Minimal offset (5mm)
    },
    'hip': {
        'max_active_sides': 2,
        'triangular_sides': ['front', 'back'],
        'trapezoidal_sides': ['left', 'right']
    },
    'pyramid': {
        'max_active_sides': 2,
        'all_triangular': True
    }
}

# Performance calculation settings
PERFORMANCE_CONFIG = {
    'annual_yield_base': 1200,  # kWh per kWp per year
    'performance_ratio': 0.8,
    'optimal_tilt_angle': 35,   # degrees
    'optimal_orientation': 180  # degrees (south)
}

def get_default_config(roof_type=None):
    """Get default configuration for a roof type"""
    config = DEFAULT_PANEL_CONFIG.copy()
    
    if roof_type and roof_type.lower() in ROOF_SPECIFIC_CONFIG:
        config.update(ROOF_SPECIFIC_CONFIG[roof_type.lower()])
    
    return config
