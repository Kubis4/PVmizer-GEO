from translations import _
import pyvista as pv
import numpy as np
import os, sys
from pathlib import Path
from roofs.roof_annotation import RoofAnnotation 

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # Try to find the file
    full_path = os.path.join(base_path, relative_path)
    if os.path.exists(full_path):
        return full_path
        
    # Try alternate paths if the first one doesn't exist
    alt_paths = [
        os.path.join(os.path.dirname(sys.executable), relative_path),
        os.path.join(os.path.dirname(__file__), relative_path)
    ]
    
    for path in alt_paths:
        if os.path.exists(path):
            return path
            
    # Return the original path even if it doesn't exist
    return full_path

class FlatRoof:
    def __init__(self, plotter=None, dimensions=None, theme="light"):
        """Vytvor plochú strechu na základe zadaných vstupných parametrov"""
        # Zobrazenie pomocného menu a výkonov= menu
        self.debug_text = None # Výkonové menu
        self.help_visible = True # Pomocné menu
        self.theme = theme 
        # Výška základne 
        self.base_height = 1.0  #1 meter
        
        # Ak sú parametre zadané použijeme tie, ak nie použijeme predvolené hodnoty
        if dimensions is None:
            self.length = 10.0   # 10m dĺžka v metroch
            self.width = 8.0     # 8m šírka v metroch
            self.height = 0.0    # výška v metroch nastavená 0, lebo používame parapetu
            self.parapet_height = 0.5  # 50 cm výška parapetu okolo strechy
            self.parapet_width = 0.3   # 30 cm hrúbka parapetu (nedá sa meniť uživateľom)

        else:
            # Handle different dimension formats
            if len(dimensions) >= 2:
                self.length, self.width = dimensions[0], dimensions[1]
                self.height = 0.0  # Default height at ground level
            if len(dimensions) >= 3:
                self.parapet_height = dimensions[2]
            else:
                self.parapet_height = 0.5  # Default parapet height
            if len(dimensions) >= 4:
                self.parapet_width = dimensions[3]
            else:
                self.parapet_width = 0.2  # Default parapet width
        
        # If a plotter is provided, use it; otherwise create a new one
        if plotter:
            self.plotter = plotter
            self.external_plotter = True
        else:
            self.plotter = pv.Plotter()
            self.external_plotter = False
            
        # Nahranie textur pre vizualne zobrazenie
        texture_dir = resource_path("PVmizer/textures") # Cesta k textúram
        self.wall_texture_file = os.path.join(texture_dir, "wall.jpg") # Textura steny
        self.brick_texture_file = os.path.join(texture_dir, "brick.jpg") # Textúra základne
        
        # Set theme-appropriate background
        self.set_plotter_background()
        
        try:
            # Create the roof
            self.create_flat_roof()
            
            # Initialize solar panel handler
            from solar_panel_handlers.solar_panel_flat import SolarPanelPlacementFlat
            self.solar_panel_handler = SolarPanelPlacementFlat(self)
            
            # Add key bindings for solar panel placement
            self.add_key_bindings()
            
            # Add help text
            self.add_help_text()
        except Exception as e:
            import traceback
            traceback.print_exc()

        # Set default camera view
        self.set_default_camera_view()
        
    def load_texture_safely(self, filename, default_color="#A9A9A9"):
        """Safely load a texture with fallback to color if loading fails"""
        # Extract just the filename without path
        base_filename = os.path.basename(filename)
        
        # Try multiple possible locations
        possible_paths = [
            filename,  # Original path
            resource_path(base_filename),  # Just filename with resource_path
            resource_path(f"PVmizer/textures/{base_filename}"),  # Try in PVmizer/textures
            resource_path(f"textures/{base_filename}")  # Try in textures dir
        ]
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    texture = pv.read_texture(path)
                    return texture, True
                except Exception as e:
                    print(f"Error loading texture from {path}: {e}")
        
        # If we get here, no texture was loaded
        return default_color, False

    def set_theme(self, theme):
        """Update the roof's theme and refresh visuals"""
        self.theme = theme
        self.set_plotter_background()
        
        # Update annotations if they exist (ADDED)
        if hasattr(self, 'annotator'):
            self.annotator.set_theme(theme)
        
    def set_plotter_background(self):
        """Set the plotter background based on current theme"""
        if hasattr(self, 'theme') and self.theme == "dark":
            self.plotter.set_background("darkgrey")
        else:
            self.plotter.set_background("lightgrey")
    
    def create_flat_roof(self):
        """Create a flat roof with parapet walls."""
        # Clear the plotter
        self.plotter.clear()
        
        # Define the base height for the building
        self.base_height = 1.0  # 1 meter building base height
        
        # Define the main roof surface (flat part) - AT BASE HEIGHT LEVEL
        roof_points = np.array([
            [0, 0, self.base_height],                # Front left
            [self.length, 0, self.base_height],      # Front right
            [self.length, self.width, self.base_height],  # Back right
            [0, self.width, self.base_height]        # Back left
        ])
        roof_faces = np.array([[4, 0, 1, 2, 3]])
        roof = pv.PolyData(roof_points, roof_faces)
        
        # Define texture coordinates for the roof
        roof_tcoords = np.array([
            [0, 0],  # Front left
            [2, 0],  # Front right
            [2, 2],  # Back right
            [0, 2]   # Back left
        ])
        roof.active_texture_coordinates = roof_tcoords
        
        # Create base walls (from ground level to base height)
        # Front base wall
        front_base_points = np.array([
            [0, 0, 0],                       # Bottom left
            [self.length, 0, 0],             # Bottom right
            [self.length, 0, self.base_height],  # Top right
            [0, 0, self.base_height]         # Top left
        ])
        front_base_faces = np.array([[4, 0, 1, 2, 3]])
        front_base = pv.PolyData(front_base_points, front_base_faces)
        
        # Right base wall
        right_base_points = np.array([
            [self.length, 0, 0],                      # Bottom front
            [self.length, self.width, 0],             # Bottom back
            [self.length, self.width, self.base_height],  # Top back
            [self.length, 0, self.base_height]        # Top front
        ])
        right_base_faces = np.array([[4, 0, 1, 2, 3]])
        right_base = pv.PolyData(right_base_points, right_base_faces)
        
        # Back base wall
        back_base_points = np.array([
            [self.length, self.width, 0],             # Bottom right
            [0, self.width, 0],                       # Bottom left
            [0, self.width, self.base_height],        # Top left
            [self.length, self.width, self.base_height]  # Top right
        ])
        back_base_faces = np.array([[4, 0, 1, 2, 3]])
        back_base = pv.PolyData(back_base_points, back_base_faces)
        
        # Left base wall
        left_base_points = np.array([
            [0, self.width, 0],                       # Bottom back
            [0, 0, 0],                                # Bottom front
            [0, 0, self.base_height],                 # Top front
            [0, self.width, self.base_height]         # Top back
        ])
        left_base_faces = np.array([[4, 0, 1, 2, 3]])
        left_base = pv.PolyData(left_base_points, left_base_faces)
        
        # Create outer parapet walls (now starting from base_height)
        # Front outer wall
        front_outer_points = np.array([
            [0, 0, self.base_height],                                # Bottom left
            [self.length, 0, self.base_height],                      # Bottom right
            [self.length, 0, self.base_height + self.parapet_height],  # Top right
            [0, 0, self.base_height + self.parapet_height]           # Top left
        ])
        front_outer_faces = np.array([[4, 0, 1, 2, 3]])
        front_outer = pv.PolyData(front_outer_points, front_outer_faces)
        
        # Right outer wall
        right_outer_points = np.array([
            [self.length, 0, self.base_height],                                # Bottom front
            [self.length, self.width, self.base_height],                       # Bottom back
            [self.length, self.width, self.base_height + self.parapet_height],   # Top back
            [self.length, 0, self.base_height + self.parapet_height]           # Top front
        ])
        right_outer_faces = np.array([[4, 0, 1, 2, 3]])
        right_outer = pv.PolyData(right_outer_points, right_outer_faces)
        
        # Back outer wall
        back_outer_points = np.array([
            [self.length, self.width, self.base_height],                       # Bottom right
            [0, self.width, self.base_height],                                 # Bottom left
            [0, self.width, self.base_height + self.parapet_height],           # Top left
            [self.length, self.width, self.base_height + self.parapet_height]    # Top right
        ])
        back_outer_faces = np.array([[4, 0, 1, 2, 3]])
        back_outer = pv.PolyData(back_outer_points, back_outer_faces)
        
        # Left outer wall
        left_outer_points = np.array([
            [0, self.width, self.base_height],                                 # Bottom back
            [0, 0, self.base_height],                                          # Bottom front
            [0, 0, self.base_height + self.parapet_height],                    # Top front
            [0, self.width, self.base_height + self.parapet_height]            # Top back
        ])
        left_outer_faces = np.array([[4, 0, 1, 2, 3]])
        left_outer = pv.PolyData(left_outer_points, left_outer_faces)
        
        # Create inner parapet walls (also starting from base_height)
        # Front inner wall
        front_inner_points = np.array([
            [self.parapet_width, self.parapet_width, self.base_height],                                # Bottom left
            [self.length - self.parapet_width, self.parapet_width, self.base_height],                  # Bottom right
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],  # Top right
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]           # Top left
        ])
        front_inner_faces = np.array([[4, 0, 1, 2, 3]])
        front_inner = pv.PolyData(front_inner_points, front_inner_faces)
        
        # Right inner wall
        right_inner_points = np.array([
            [self.length - self.parapet_width, self.parapet_width, self.base_height],                                # Bottom front
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height],                   # Bottom back
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],   # Top back
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]           # Top front
        ])
        right_inner_faces = np.array([[4, 0, 1, 2, 3]])
        right_inner = pv.PolyData(right_inner_points, right_inner_faces)
        
        # Back inner wall
        back_inner_points = np.array([
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height],                       # Bottom right
            [self.parapet_width, self.width - self.parapet_width, self.base_height],                                 # Bottom left
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],           # Top left
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]    # Top right
        ])
        back_inner_faces = np.array([[4, 0, 1, 2, 3]])
        back_inner = pv.PolyData(back_inner_points, back_inner_faces)
        
        # Left inner wall
        left_inner_points = np.array([
            [self.parapet_width, self.width - self.parapet_width, self.base_height],                                 # Bottom back
            [self.parapet_width, self.parapet_width, self.base_height],                                          # Bottom front
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],                    # Top front
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]            # Top back
        ])
        left_inner_faces = np.array([[4, 0, 1, 2, 3]])
        left_inner = pv.PolyData(left_inner_points, left_inner_faces)
        
        # Create parapet top surfaces (on top of the parapet walls)
        # Front parapet top
        front_top_points = np.array([
            [0, 0, self.base_height + self.parapet_height],                      # Outer front left
            [self.length, 0, self.base_height + self.parapet_height],            # Outer front right
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],  # Inner front right
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]  # Inner front left
        ])
        front_top_faces = np.array([[4, 0, 1, 2, 3]])
        front_top = pv.PolyData(front_top_points, front_top_faces)
        
        # Right parapet top
        right_top_points = np.array([
            [self.length, 0, self.base_height + self.parapet_height],            # Outer right front
            [self.length, self.width, self.base_height + self.parapet_height],   # Outer right back
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],  # Inner right back
            [self.length - self.parapet_width, self.parapet_width, self.base_height + self.parapet_height]  # Inner right front
        ])
        right_top_faces = np.array([[4, 0, 1, 2, 3]])
        right_top = pv.PolyData(right_top_points, right_top_faces)
        
        # Back parapet top
        back_top_points = np.array([
            [self.length, self.width, self.base_height + self.parapet_height],   # Outer back right
            [0, self.width, self.base_height + self.parapet_height],             # Outer back left
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height],  # Inner back left
            [self.length - self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]  # Inner back right
        ])
        back_top_faces = np.array([[4, 0, 1, 2, 3]])
        back_top = pv.PolyData(back_top_points, back_top_faces)
        
        # Left parapet top
        left_top_points = np.array([
            [0, self.width, self.base_height + self.parapet_height],             # Outer left back
            [0, 0, self.base_height + self.parapet_height],                      # Outer left front
            [self.parapet_width, self.parapet_width, self.base_height + self.parapet_height],  # Inner left front
            [self.parapet_width, self.width - self.parapet_width, self.base_height + self.parapet_height]  # Inner left back
        ])
        left_top_faces = np.array([[4, 0, 1, 2, 3]])
        left_top = pv.PolyData(left_top_points, left_top_faces)
        
        # Create a bottom floor surface
        floor_points = np.array([
            [0, 0, 0],                # Front left
            [self.length, 0, 0],      # Front right
            [self.length, self.width, 0],  # Back right
            [0, self.width, 0]        # Back left
        ])
        floor_faces = np.array([[4, 0, 1, 2, 3]])
        floor = pv.PolyData(floor_points, floor_faces)
        
        # Define texture coordinates
        # Standard texture coordinates for walls
        std_tcoords = np.array([
            [0, 0],  # Bottom left
            [2, 0],  # Bottom right
            [2, 0.5],  # Top right
            [0, 0.5]   # Top left
        ])
        
        # Base walls texture coordinates (taller than parapet)
        base_tcoords = np.array([
            [0, 0],   # Bottom left
            [3, 0],   # Bottom right
            [3, 1],   # Top right
            [0, 1]    # Top left
        ])
        
        # Apply texture coordinates to base walls
        front_base.active_texture_coordinates = base_tcoords
        right_base.active_texture_coordinates = base_tcoords
        back_base.active_texture_coordinates = base_tcoords
        left_base.active_texture_coordinates = base_tcoords
        
        # Apply texture coordinates to parapet walls
        front_outer.active_texture_coordinates = std_tcoords
        right_outer.active_texture_coordinates = std_tcoords
        back_outer.active_texture_coordinates = std_tcoords
        left_outer.active_texture_coordinates = std_tcoords
        
        front_inner.active_texture_coordinates = std_tcoords
        right_inner.active_texture_coordinates = std_tcoords
        back_inner.active_texture_coordinates = std_tcoords
        left_inner.active_texture_coordinates = std_tcoords
        
        # Texture coordinates for the tops
        top_tcoords = np.array([
            [0, 0],  # Outer corner 1
            [1, 0],  # Outer corner 2
            [0.9, 0.9],  # Inner corner 2
            [0.1, 0.9]   # Inner corner 1
        ])
        
        front_top.active_texture_coordinates = top_tcoords
        right_top.active_texture_coordinates = top_tcoords
        back_top.active_texture_coordinates = top_tcoords
        left_top.active_texture_coordinates = top_tcoords
        
        # Floor texture coordinates
        floor.active_texture_coordinates = roof_tcoords.copy()
        
        # Check if textures exist
        wall_texture, wall_texture_exists = self.load_texture_safely(self.wall_texture_file)
        brick_texture, brick_texture_exists = self.load_texture_safely(self.brick_texture_file)
        
        wall_texture = None
        brick_texture = None
        
        # Try to load wall texture
        if wall_texture_exists:
            try:
                wall_texture = pv.read_texture(str(self.wall_texture_file))
            except Exception as e:
                print(f"Error loading wall texture: {e}")
                wall_texture_exists = False
        
        # Try to load brick texture
        if brick_texture_exists:
            try:
                brick_texture = pv.read_texture(str(self.brick_texture_file))
            except Exception as e:
                print(f"Error loading brick texture: {e}")
                brick_texture_exists = False
        
        # Apply textures based on what's available
        if wall_texture_exists and brick_texture_exists:
            # Best case: both textures are available
            # Apply wall texture to roof and floor
            self.plotter.add_mesh(roof, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(floor, texture=wall_texture, show_edges=True)
            
            # Apply brick texture to base walls
            self.plotter.add_mesh(front_base, texture=brick_texture, show_edges=True)
            self.plotter.add_mesh(right_base, texture=brick_texture, show_edges=True)
            self.plotter.add_mesh(back_base, texture=brick_texture, show_edges=True)
            self.plotter.add_mesh(left_base, texture=brick_texture, show_edges=True)
            
            # Apply wall texture to parapet walls
            self.plotter.add_mesh(front_outer, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(right_outer, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_outer, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(left_outer, texture=wall_texture, show_edges=True)
            
            self.plotter.add_mesh(front_inner, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(right_inner, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_inner, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(left_inner, texture=wall_texture, show_edges=True)
            
            self.plotter.add_mesh(front_top, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(right_top, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_top, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(left_top, texture=wall_texture, show_edges=True)
        
        elif wall_texture_exists:  # Only wall texture is available
            # Apply wall texture to roof and floor
            self.plotter.add_mesh(roof, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(floor, texture=wall_texture, show_edges=True)
            
            # Use a brick color for base walls
            brick_color = '#9C2706'  # Brick red color
            
            self.plotter.add_mesh(front_base, color=brick_color, show_edges=True)
            self.plotter.add_mesh(right_base, color=brick_color, show_edges=True)
            self.plotter.add_mesh(back_base, color=brick_color, show_edges=True)
            self.plotter.add_mesh(left_base, color=brick_color, show_edges=True)
            
            # Apply wall texture to parapet walls
            self.plotter.add_mesh(front_outer, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(right_outer, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_outer, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(left_outer, texture=wall_texture, show_edges=True)
            
            self.plotter.add_mesh(front_inner, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(right_inner, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_inner, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(left_inner, texture=wall_texture, show_edges=True)
            
            self.plotter.add_mesh(front_top, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(right_top, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(back_top, texture=wall_texture, show_edges=True)
            self.plotter.add_mesh(left_top, texture=wall_texture, show_edges=True)
        
        elif brick_texture_exists:  # Only brick texture is available
            # Use colors for surfaces that would use wall texture
            concrete_color = '#A9A9A9'  # Dark gray color for concrete
            parapet_color = '#808080'   # Slightly different gray for parapet
            rim_color = '#707070'       # Even darker gray for the rim
            floor_color = '#909090'     # Floor color
            
            self.plotter.add_mesh(roof, color=concrete_color, show_edges=True)
            self.plotter.add_mesh(floor, color=floor_color, show_edges=True)
            
            # Apply brick texture to base walls
            self.plotter.add_mesh(front_base, texture=brick_texture, show_edges=True)
            self.plotter.add_mesh(right_base, texture=brick_texture, show_edges=True)
            self.plotter.add_mesh(back_base, texture=brick_texture, show_edges=True)
            self.plotter.add_mesh(left_base, texture=brick_texture, show_edges=True)
            
            # Use colors for parapet walls
            self.plotter.add_mesh(front_outer, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(right_outer, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(back_outer, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(left_outer, color=parapet_color, show_edges=True)
            
            self.plotter.add_mesh(front_inner, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(right_inner, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(back_inner, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(left_inner, color=parapet_color, show_edges=True)
            
            self.plotter.add_mesh(front_top, color=rim_color, show_edges=True)
            self.plotter.add_mesh(right_top, color=rim_color, show_edges=True)
            self.plotter.add_mesh(back_top, color=rim_color, show_edges=True)
            self.plotter.add_mesh(left_top, color=rim_color, show_edges=True)
        
        else:  # No textures available
            # Fall back to all colors
            concrete_color = '#A9A9A9'  # Dark gray color for concrete
            parapet_color = '#808080'   # Slightly different gray for parapet
            rim_color = '#707070'       # Even darker gray for the rim
            floor_color = '#909090'     # Floor color
            brick_color = '#9C2706'     # Brick red color for base
            
            self.plotter.add_mesh(roof, color=concrete_color, show_edges=True)
            self.plotter.add_mesh(floor, color=floor_color, show_edges=True)
            
            # Base walls with brick color
            self.plotter.add_mesh(front_base, color=brick_color, show_edges=True)
            self.plotter.add_mesh(right_base, color=brick_color, show_edges=True)
            self.plotter.add_mesh(back_base, color=brick_color, show_edges=True)
            self.plotter.add_mesh(left_base, color=brick_color, show_edges=True)
            
            # Parapet with wall color
            self.plotter.add_mesh(front_outer, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(right_outer, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(back_outer, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(left_outer, color=parapet_color, show_edges=True)
            
            self.plotter.add_mesh(front_inner, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(right_inner, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(back_inner, color=parapet_color, show_edges=True)
            self.plotter.add_mesh(left_inner, color=parapet_color, show_edges=True)
            
            self.plotter.add_mesh(front_top, color=rim_color, show_edges=True)
            self.plotter.add_mesh(right_top, color=rim_color, show_edges=True)
            self.plotter.add_mesh(back_top, color=rim_color, show_edges=True)
            self.plotter.add_mesh(left_top, color=rim_color, show_edges=True)
        
        # Store reference points - AT BASE HEIGHT LEVEL
        self.roof_points = {
            'bottom_left': np.array([self.parapet_width, self.parapet_width, self.base_height]),
            'bottom_right': np.array([self.length - self.parapet_width, self.parapet_width, self.base_height]),
            'top_right': np.array([self.length - self.parapet_width, self.width - self.parapet_width, self.base_height]),
            'top_left': np.array([self.parapet_width, self.width - self.parapet_width, self.base_height])
        }
        
        # Add coordinate axes
        self.plotter.add_axes()
    
        # Create annotations using the RoofAnnotation helper
        self.annotator = RoofAnnotation(
            self.plotter,
            self.width,
            self.length,
            self.parapet_height,  # Use positive parapet height
            slope_angle=0,
            theme=self.theme,
            center_origin=False,
            base_height=self.base_height   # Position at TOP of parapet
        )
        self.annotator.add_annotations()
        # Set camera position for a good view
        self.reset_camera()
        
        # Update the visualization
        self.plotter.update()
        
    def add_help_text(self):
        """Add help text to the visualization."""
        # Remove existing help text if any
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            self.plotter.remove_actor(self.help_text_actor)
        
        help_text = (
            f"{_('help_flat_roof_title')}\n"
            f"{_('help_place_center_panels')}\n"
            f"{_('help_place_north_panels')}\n"
            f"{_('help_place_south_panels')}\n"
            f"{_('help_place_east_panels')}\n"
            f"{_('help_place_west_panels')}\n"
            f"{_('help_clear_panels')}\n"
            f"\n"
            f"{_('help_view_controls_title')}\n"
            f"{_('help_reset_camera')}\n"
            f"{_('help_save_screenshot')}\n"
            f"{_('help_toggle_menu')}"
        )
        
        self.help_text_actor = self.plotter.add_text(
            help_text,
            position="upper_right",
            font_size=12,
            color="black"
        )
        self.help_visible = True

        
           
    def update_debug_text(self, text):
        """Update the debug text in the visualization."""
        # Remove existing text if any
        if hasattr(self, 'debug_text') and self.debug_text:
            self.plotter.remove_actor(self.debug_text)
        
        # Add new text
        self.debug_text = self.plotter.add_text(
            text, 
            position="upper_left", 
            font_size=12, 
            color="black"
        )
        self.plotter.render()
    
    def add_key_bindings(self):
        """Add key bindings for solar panel placement."""
        self.plotter.add_key_event("1", self.place_panels_center)
        self.plotter.add_key_event("2", self.place_panels_north)
        self.plotter.add_key_event("3", self.place_panels_south)
        self.plotter.add_key_event("4", self.place_panels_east)
        self.plotter.add_key_event("5", self.place_panels_west)
        self.plotter.add_key_event("c", self.clear_panels)
        self.plotter.add_key_event("C", self.clear_panels)
        self.plotter.add_key_event("h", self.toggle_help)
        self.plotter.add_key_event("H", self.toggle_help)
        self.plotter.add_key_event("r", self.reset_camera)
        self.plotter.add_key_event("R", self.reset_camera)
        self.plotter.add_key_event("s", self.save_roof_screenshot)
        self.plotter.add_key_event("S", self.save_roof_screenshot)
    
    def place_panels_center(self):
        """Place panels in the center of the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.place_panels(area="center")
            self.update_panels_debug_info("center")

    def place_panels_north(self):
        """Place panels in the north area of the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.place_panels(area="north")
            self.update_panels_debug_info("north")

    def place_panels_south(self):
        """Place panels in the south area of the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.place_panels(area="south")
            self.update_panels_debug_info("south")

    def place_panels_east(self):
        """Place panels in the east area of the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.place_panels(area="east")
            self.update_panels_debug_info("east")

    def place_panels_west(self):
        """Place panels in the west area of the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.place_panels(area="west")
            self.update_panels_debug_info("west")

    def clear_panels(self):
        """Clear all panels from the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.clear_panels()
            self.update_debug_text(f"{_('all_panels_cleared')}. {_('press_number_key')}")
    
    def toggle_help(self):
        """Toggle the help text on/off."""
        # Toggle visibility flag
        if hasattr(self, 'help_visible'):
            self.help_visible = not self.help_visible
        else:
            self.help_visible = True
        
        # Show or hide help based on visibility flag
        if self.help_visible:
            self.add_help_text()
        else:
            # Hide help text
            if hasattr(self, 'help_text_actor') and self.help_text_actor:
                self.plotter.remove_actor(self.help_text_actor)
                self.help_text_actor = None
                self.plotter.render()
    
    def update_panel_config(self, config):
        """Update solar panel configuration."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.update_panel_config(config)

    def add_solar_panels(self, side=None):
        """Add solar panels to the roof."""
        if hasattr(self, 'solar_panel_handler'):
            self.solar_panel_handler.add_panels(side)

    def reset_camera(self):
        """Reset camera to default position viewing the front of the roof."""
        # For flat roofs, use an absolute height value instead of multiplying by roof height
        camera_height = max(5.0, self.parapet_height * 10)  # Minimum 5m height or 10x parapet height
        
        self.plotter.camera_position = [
            (self.width*2.0, -self.length*1.2, camera_height),  # Position
            (self.width/2, self.length/2, self.parapet_height/2),  # Focal point (center of roof)
            (0, 0, 1)  # Up vector (must be a unit vector)
        ]
        self.plotter.reset_camera()

    def set_default_camera_view(self):
        """Set camera to the default position viewing the front of the roof."""
        # For flat roofs, use an absolute height value instead of multiplying by roof height
        camera_height = max(6.0, self.parapet_height * 12)  # Slightly higher than reset_camera
        
        self.plotter.camera_position = [
            (self.width*2.0, -self.length*1.0, camera_height),  # Position
            (self.width/2, self.length/2, self.parapet_height/2),  # Focal point (center of roof)
            (0, 0, 1)  # Up vector (must be a unit vector)
        ]
        self.plotter.reset_camera()

    
    def set_screenshot_directory(self, directory):
        """Set the directory where screenshots will be saved."""
        self.screenshot_directory = directory

    def save_roof_screenshot(self):
        """Save current roof view."""
        import os
        import datetime
        from pathlib import Path
        from PyQt5.QtCore import QTimer
        
        # Use the configured screenshot directory or default
        if hasattr(self, 'screenshot_directory') and self.screenshot_directory:
            snaps_dir = Path(self.screenshot_directory)
        else:
            # Default to RoofSnaps if no directory was provided
            snaps_dir = Path("RoofSnaps")
        
        # Ensure the directory exists
        snaps_dir.mkdir(exist_ok=True)
        
        # Generate a unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get the roof type from class name
        roof_type = self.__class__.__name__.lower()
        
        # Create filename
        filename = f"{roof_type}_{timestamp}.png"
        filepath = snaps_dir / filename
        
        # Save the screenshot
        try:
            self.plotter.screenshot(str(filepath))
            
            # Display a temporary success message using translation system
            message_actor = self.plotter.add_text(
                _('screenshot_saved').format(filename=filename), 
                position="lower_right",
                font_size=12,
                color="green",
                shadow=True
            )
            
            # Remove the message after 3 seconds
            def remove_message():
                try:
                    self.plotter.remove_actor(message_actor)
                    self.plotter.render()
                except:
                    pass  
            
            QTimer.singleShot(3000, remove_message)
            
            print(f"Screenshot saved to {filepath}")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            
            # Display error message with translation
            error_actor = self.plotter.add_text(
                _('screenshot_error'),  
                position="lower_right",
                font_size=12,
                color="red",
                shadow=True
            )
            
            # Remove error message after 3 seconds
            def remove_error():
                try:
                    self.plotter.remove_actor(error_actor)
                    self.plotter.render()
                except:
                    pass
            
            QTimer.singleShot(3000, remove_error)

        
    def update_panels_debug_info(self, area):
        if not hasattr(self, 'solar_panel_handler'):
            return
            
        perf_data = self.solar_panel_handler.get_performance_data()
        
        if not perf_data or 'panel_count' not in perf_data:
            self.update_debug_text(f"{_('no_panels_placed')} {_('in')} {_(area)} {_('area')}.")
            return
        
        # Initialize section states if not already done
        if not hasattr(self, 'debug_section_states'):
            self.debug_section_states = {
                "installation": False, 
                "orientation": False,
                "performance": False,
                "production": False
            }
        
        # Store the current area
        self.current_area = area
        
        # Generate basic info (always visible)
        area_name = _(area)
        panel_count = perf_data['panel_count']
        system_size = perf_data.get('system_power_kw', 0)
        
        debug_msg = f"{_('selected_area')}: {area_name} | "
        debug_msg += f"{_('panels')}: {panel_count} | "
        debug_msg += f"{_('system_size')}: {system_size:.2f}kWp\n\n"
        
        # Add keyboard shortcut info
        debug_msg += f"{_('press_keys_to_toggle')}:\n"
        
        # Generate sections with appropriate icons
        section_content = self._generate_debug_section_content(perf_data, area)
        
        # Add key-mappings to section headers (using F1-F4 keys)
        key_mappings = {
            "installation": "F1",
            "orientation": "F2",
            "performance": "F3", 
            "production": "F4"
        }
        
        for section_id, content in section_content.items():
            # Get section title and state
            section_title = self._get_section_title(section_id)
            is_expanded = self.debug_section_states.get(section_id, False)
            
            # Get key for this section
            key = key_mappings.get(section_id, "")
            
            # Create section header with toggle indicator
            toggle_icon = "[-]" if is_expanded else "[+]"
            section_header = f"{key}: {section_title} {toggle_icon}"
            
            # Add section header to message
            debug_msg += f"{section_header}\n"
            
            # If section is expanded, add the content
            if is_expanded:
                debug_msg += f"{content}\n"
        
        # Update the text display
        self.update_debug_text(debug_msg)
        
        # Add key events for toggling sections if not already added
        if not hasattr(self, '_debug_section_keys_added'):
            self._add_debug_section_key_events(key_mappings)
            self._debug_section_keys_added = True

    def _add_debug_section_key_events(self, key_mappings):
        """Add key event handlers for toggling debug sections"""
        for section_id, key in key_mappings.items():
            # Use lambda with default argument to capture the current section_id
            self.plotter.add_key_event(
                key, 
                lambda sid=section_id: self.toggle_debug_section(sid)
            )

    def toggle_debug_section(self, section_id):
        """Toggle the expansion state of a debug section"""
        if hasattr(self, 'debug_section_states'):
            if section_id in self.debug_section_states:
                # Toggle the state
                self.debug_section_states[section_id] = not self.debug_section_states[section_id]
                
                # Update the display
                if hasattr(self, 'current_area'):
                    self.update_panels_debug_info(self.current_area)

    def _get_section_title(self, section_id):
        """Return a user-friendly title for each section with an icon"""
        titles = {
            "installation": f" {_('installation_details')}",
            "orientation": f" {_('orientation_and_tilt')}",
            "performance": f" {_('performance_data')}",
            "production": f" {_('production_estimates')}"
        }
        return titles.get(section_id, section_id.title())

    def _generate_debug_section_content(self, perf_data, area):
        # Extract dimensions from performance data
        horizontal_length = perf_data.get('installation_width', 0) * 1000 
        vertical_length = perf_data.get('installation_length', 0) * 1000   
        
        # Get panel attributes
        panel_width = getattr(self.solar_panel_handler, 'panel_width', 0)
        panel_length = getattr(self.solar_panel_handler, 'panel_length', 0)
        panel_gap = getattr(self.solar_panel_handler, 'panel_spacing', 0)  
        panel_tilt = getattr(self.solar_panel_handler, 'panel_tilt', 0)
        panel_orientation = getattr(self.solar_panel_handler, 'panel_orientation', 180)
        orientation_factor = perf_data.get('orientation_factor', 1.0)
        
        # 1\. Installation section
        installation = f"  {_('installation_area')}: {horizontal_length:.0f}mm x {vertical_length:.0f}mm\n"
        installation += f"  {_('panel_dimensions')}: {panel_width}mm x {panel_length}mm\n"
        installation += f"  {_('panel_gap')}: {panel_gap}mm\n"
        
        # 2\. Orientation section
        orientation = ""
        if panel_tilt > 0:
            # Get orientation name (North, South, etc.)
            orientation_name = self._get_orientation_name(panel_orientation)
            orientation += f"  {_('panel_tilt')}: {panel_tilt:.1f}° {_('facing')} {_(orientation_name.lower())}\n"
            
            # Add efficiency ratings
            orientation_rating = self._get_efficiency_rating(orientation_factor)
            angle_factor = perf_data.get('angle_factor', 1.0)
            
            orientation += f"  {_('orientation_efficiency')}: {orientation_factor:.2f} {orientation_rating}\n"
            
            # Show loss percentage if not optimal
            if orientation_factor < 0.95:
                loss_percent = int((1 - orientation_factor) * 100)
                orientation += f"  {loss_percent}% {_('production_loss')}\n"
                
            orientation += f"  {_('tilt_efficiency')}: {angle_factor:.2f}\n"
            
            # Combined efficiency factors
            if 'combined_factor' in perf_data:
                combined_factor = perf_data['combined_factor']
                combined_loss = int((1 - combined_factor) * 100)
                orientation += f"  {_('combined_efficiency')}: {combined_factor:.2f}"
                
                if combined_loss > 5:
                    orientation += f" ({combined_loss}% {_('total_production_loss')})\n"
                else:
                    orientation += "\n"
        else:
            orientation += f"  {_('slope_angle')}: 0.0° ({_('flat_roof')})\n"
        
        # 3\. Performance section
        performance = f"  {_('panel_power')}: {perf_data.get('panel_power_w', 0)}W\n"
        performance += f"  {_('system_size')}: {perf_data.get('system_power_kw', 0):.2f}kWp\n"
        performance += f"  {_('performance_factor')}: {perf_data.get('combined_factor', perf_data.get('angle_factor', 0)):.2f}\n"
        
        # Add obstacle information if available
        if 'panels_skipped' in perf_data and perf_data['panels_skipped'] > 0:
            obstacle_count = perf_data.get('obstacle_count', 0)
            performance += f"  {_('obstacles_on_roof')}: {obstacle_count}\n"
            performance += f"  {_('panels_skipped')}: {perf_data['panels_skipped']}\n"
        
        # 4\. Production section
        production = ""
        # Annual production with comparison if not optimal
        current_annual = perf_data.get('annual_energy_kwh', 0)
        if orientation_factor < 0.98:
            optimal_annual = current_annual / orientation_factor
            production += f"  {_('est_annual_production')}: {current_annual:.0f}kWh "
            production += f"({_('optimal')}: {optimal_annual:.0f}kWh)\n"
        else:
            production += f"  {_('est_annual_production')}: {current_annual:.0f}kWh\n"
        
        # Daily production
        current_daily = perf_data.get('daily_energy_kwh', 0)
        if orientation_factor < 0.98:
            optimal_daily = current_daily / orientation_factor
            production += f"  {_('est_daily_production')}: {current_daily:.1f}kWh "
            production += f"({_('optimal')}: {optimal_daily:.1f}kWh)\n"
        else:
            production += f"  {_('est_daily_production')}: {current_daily:.1f}kWh\n"
        
        # Seasonal production data if available
        if 'seasonal_energy' in perf_data:
            seasonal = perf_data['seasonal_energy']
            production += f"\n  {_('seasonal_production')}:\n"
            production += f"  • {_('winter')}: {seasonal['winter']:.0f} kWh\n"
            production += f"  • {_('spring')}: {seasonal['spring']:.0f} kWh\n"
            production += f"  • {_('summer')}: {seasonal['summer']:.0f} kWh\n"
            production += f"  • {_('fall')}: {seasonal['fall']:.0f} kWh\n"
        
        # If orientation isn't optimal, add production impact details
        if orientation_factor < 0.98:
            optimal_annual = current_annual / orientation_factor
            optimal_daily = current_daily / orientation_factor
            annual_difference = optimal_annual - current_annual
            daily_difference = optimal_daily - current_daily
            percentage_loss = ((1 - orientation_factor) * 100)
            
            production += f"\n  {_('production_impact')}:\n"
            production += f"  • {_('annual')}: -{annual_difference:.0f}kWh ({percentage_loss:.0f}% {_('less')})\n"
            production += f"  • {_('daily')}: -{daily_difference:.1f}kWh ({percentage_loss:.0f}% {_('less')})\n"
        
        return {
            "installation": installation,
            "orientation": orientation,
            "performance": performance,
            "production": production
        }
    def _get_orientation_name(self, orientation_degrees):
        """Convert orientation in degrees to a direction name"""
        # Define cardinal directions using degrees
        cardinal_directions = {
            0: 'north',
            #45: 'northeast', 
            90: 'west',
            #135: 'southwest',
            180: 'south',
            #225: 'southeast',
            270: 'east',
            #315: 'northwest'
        }
        
        # Find the closest direction
        closest_orient = min(cardinal_directions.keys(), 
                    key=lambda x: abs((orientation_degrees - x) % 360))
        
        # Get the direction name and translate it
        direction_name = cardinal_directions[closest_orient]
        translated_direction = _(direction_name)
        
        # Return the translated direction (you can capitalize first letter if needed)
        return translated_direction.capitalize()

    def _get_efficiency_rating(self, efficiency_factor):
        """Return a visual rating based on efficiency factor"""
        if efficiency_factor >= 0.95:
            return "★★★★★"  # Excellent
        elif efficiency_factor >= 0.85:
            return "★★★★☆"  # Good
        elif efficiency_factor >= 0.75:
            return "★★★☆☆"  # Moderate
        elif efficiency_factor >= 0.65:
            return "★★☆☆☆"  # Poor
        else:
            return "★☆☆☆☆"  # Very poor
        
    def update_texts(self):
        """Update all text elements with current language"""
        # Update help text if it exists
        if hasattr(self, 'help_text_actor') and self.help_text_actor:
            # First remove the old help text
            self.plotter.remove_actor(self.help_text_actor)
            # Then regenerate it with the current language
            self.add_help_text()

        # Update the plotter
        self.plotter.update()
