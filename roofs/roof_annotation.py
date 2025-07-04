from translations import _
import numpy as np
import pyvista as pv

class RoofAnnotation:
    def __init__(self, plotter, length, width, height, slope_angle=None, theme="light", center_origin=False, base_height=0.0):
        self.plotter = plotter
        self.length = length
        self.width = width
        self.height = height
        self.slope_angle = slope_angle
        self.center_origin = center_origin
        self.theme = theme
        self.base_height = base_height
        
        # Set annotation colors based on theme
        self.set_theme_colors()
    
    def set_theme(self, theme):
        """Update the theme for annotations"""
        self.theme = theme
        self.set_theme_colors()
        
    def set_theme_colors(self):
        """Set colors based on theme"""
        self.theme == "dark"
        self.line_color = "red"
        self.text_color = "black"
        self.point_color = "black"
        self.cardinal_color = "blue"  
        self.north_color = "#ff5050"

    
    def add_annotations(self):
        """Add all annotations to the roof visualization."""
        # Add dimension lines
        self.add_dimension_lines()
                            
        # Add cardinal points (N, E, S, W)
        self.add_cardinal_points()
    
    def add_dimension_lines(self):
        """Add dimension lines showing the roof dimensions."""
        # Offset for the dimension lines
        offset = 0.5
        
        if self.center_origin:
            # For pyramid roof with centered origin
            half_length = self.length / 2
            half_width = self.width / 2
            
            # Width dimension (along x-axis) - at base height level
            self.add_dimension_line(
                [-half_width, -half_length - offset, self.base_height], 
                [half_width, -half_length - offset, self.base_height], 
                f"{_('width_a')}: {self.width:.1f}m"
            )
            
            # Length dimension (along y-axis) - at base height level
            self.add_dimension_line(
                [half_width + offset, -half_length, self.base_height], 
                [half_width + offset, half_length, self.base_height], 
                f"{_('length_a')}: {self.length:.1f}m"
            )
            
            # Height dimension (along z-axis) - from base to top
            self.add_dimension_line(
                [-half_width, -half_length - offset, self.base_height], 
                [-half_width, -half_length - offset, self.base_height + self.height], 
                f"{_('height_a')}: {self.height:.1f}m"
            )
        else:
            # For standard origin (corner-based)
            # Width dimension (along x-axis) - at base height level
            self.add_dimension_line(
                [0, -offset, self.base_height], 
                [self.width, -offset, self.base_height], 
                f"{_('width_a')}: {self.width:.1f}m"
            )
            
            # Length dimension (along y-axis) - at base height level
            self.add_dimension_line(
                [self.width + offset, 0, self.base_height], 
                [self.width + offset, self.length, self.base_height], 
                f"{_('length_a')}: {self.length:.1f}m"
            )
            
            # Height dimension (along z-axis) - from base to top
            self.add_dimension_line(
                [0, -offset, self.base_height], 
                [0, -offset, self.base_height + self.height], 
                f"{_('height_a')}: {self.height:.1f}m"
            )
    
    def add_dimension_line(self, start_point, end_point, label_text):
        """Add a dimension line with text label."""
        # Create line between points
        line = pv.Line(start_point, end_point)
        self.plotter.add_mesh(line, color=self.line_color, line_width=2)
        
        # Add spheres at endpoints
        self.plotter.add_mesh(pv.Sphere(radius=0.05, center=start_point), color=self.point_color)
        self.plotter.add_mesh(pv.Sphere(radius=0.05, center=end_point), color=self.point_color)
        
        # Calculate midpoint for label
        midpoint = [
            (start_point[0] + end_point[0]) / 2,
            (start_point[1] + end_point[1]) / 2,
            (start_point[2] + end_point[2]) / 2
        ]
        
        # Create perpendicular offset vector for label placement
        offset = [0, 0, 0]
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        dz = end_point[2] - start_point[2]
        
        # Choose offset direction based on line orientation
        if abs(dx) > abs(dy) and abs(dx) > abs(dz):  # Mostly horizontal along x
            offset[1] = 0.2  # Offset in y direction
        elif abs(dy) > abs(dx) and abs(dy) > abs(dz):  # Mostly horizontal along y
            offset[0] = 0.2  # Offset in x direction
        else:  # Vertical (along z)
            if self.center_origin:
                offset[1] = 0.2  # For pyramid roof, offset height label in y
            else:
                offset[0] = 0.2  # For other roofs, offset height label in x
        
        # Apply offset to midpoint
        adjusted_midpoint = [
            midpoint[0] + offset[0],
            midpoint[1] + offset[1],
            midpoint[2] + offset[2]
        ]
        
        # Add text label
        self.plotter.add_point_labels(
            [adjusted_midpoint], 
            [label_text], 
            font_size=14, 
            point_color=self.point_color, 
            text_color=self.text_color,
            shape_opacity=0.3,
            shadow=True,
            always_visible=True,
            render=True
        )
    
    def add_cardinal_points(self):
        """Add cardinal points (N, E, S, W) around the roof."""
        # Offset distance from the roof
        offset = 1.5
        
        if self.center_origin:
            # For pyramid roof with centered origin
            half_length = self.length / 2
            half_width = self.width / 2
            
            # North (front) - at base height level
            north_point = [0, -half_length - offset, self.base_height]
            
            # East (right) - at base height level
            east_point = [half_width + offset, 0, self.base_height]
            
            # South (back) - at base height level
            south_point = [0, half_length + offset, self.base_height]
            
            # West (left) - at base height level
            west_point = [-half_width - offset, 0, self.base_height]
        else:
            # For standard origin (corner-based)
            # North (front) - at base height level
            north_point = [self.width/2, -offset, self.base_height]
            
            # East (right) - at base height level
            east_point = [self.width + offset, self.length/2, self.base_height]
            
            # South (back) - at base height level
            south_point = [self.width/2, self.length + offset, self.base_height]
            
            # West (left) - at base height level
            west_point = [-offset, self.length/2, self.base_height]
        
        # Add cardinal point labels
        # North in red
        self.plotter.add_point_labels(
            [north_point],
            [_('north')],
            font_size=14,
            point_color=self.north_color,
            text_color=self.north_color,
            shape_opacity=0.0
        )
        
        # Other cardinal points in blue
        self.plotter.add_point_labels(
            [east_point, south_point, west_point],
            [_('east'), _('south'), _('west')],  # Corrected order
            font_size=14,
            point_color=self.cardinal_color,
            text_color=self.cardinal_color,
            shape_opacity=0.0
        )