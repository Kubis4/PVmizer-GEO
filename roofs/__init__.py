"""
Roof visualization system with refactored architecture
Now uses Template Method pattern with Abstract Base Classes
"""

# Import the base class
from .base.base_roof import BaseRoof

# Import concrete roof implementations
from .concrete.flat_roof import FlatRoof
from .concrete.gable_roof import GableRoof
from .concrete.hip_roof import HipRoof
from .concrete.pyramid_roof import PyramidRoof

# For backward compatibility, export all roof types
__all__ = [
    'BaseRoof',
    'FlatRoof', 
    'GableRoof',
    'HipRoof',
    'PyramidRoof'
]