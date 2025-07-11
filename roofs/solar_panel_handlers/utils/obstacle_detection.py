import numpy as np

class ObstacleDetector:
    """Handles obstacle detection and collision checking"""
    
    @staticmethod
    def check_panel_obstacle_intersection(panel_center, panel_width, panel_length, 
                                        orientation_vectors, obstacle):
        """Universal obstacle intersection checker"""
        try:
            # Handle different roof types and obstacle types
            if hasattr(obstacle, 'type') and obstacle.type == "Roof Window":
                return ObstacleDetector._check_window_intersection(
                    panel_center, panel_width, panel_length, orientation_vectors, obstacle
                )
            elif hasattr(obstacle, 'type') and obstacle.type == "Chimney":
                return ObstacleDetector._check_chimney_intersection(
                    panel_center, panel_width, panel_length, orientation_vectors, obstacle
                )
            else:
                return ObstacleDetector._check_generic_intersection(
                    panel_center, panel_width, panel_length, orientation_vectors, obstacle
                )
        except Exception as e:
            print(f"Error checking obstacle intersection: {e}")
            return True  # Be conservative
    
    @staticmethod
    def _check_window_intersection(panel_center, panel_width, panel_length, 
                                 orientation_vectors, obstacle):
        """Check intersection with roof windows"""
        try:
            window_pos = obstacle.position
            
            if hasattr(obstacle, 'dimensions'):
                window_width, window_length, window_height = obstacle.dimensions
            else:
                window_width, window_length = 1.0, 1.2
            
            # Minimal safety margins
            side_margin = 0.10    # 10cm
            top_margin = 0.05     # 5cm
            bottom_margin = 0.25  # 25cm
            
            # Get window normal
            window_normal = getattr(obstacle, 'normal_vector', np.array([0, 0, 1]))
            if np.linalg.norm(window_normal) < 0.001:
                window_normal = np.array([0, 0, 1])
            
            # Create coordinate system
            z_axis = window_normal / np.linalg.norm(window_normal)
            world_up = np.array([0, 0, 1])
            x_axis = np.cross(world_up, z_axis)
            if np.linalg.norm(x_axis) < 0.001:
                x_axis = np.array([1, 0, 0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            y_axis = np.cross(z_axis, x_axis)
            
            # Transform panel center to window's local space
            panel_local = np.array([
                np.dot(panel_center - window_pos, x_axis),
                np.dot(panel_center - window_pos, y_axis),
                np.dot(panel_center - window_pos, z_axis)
            ])
            
            # Calculate shadow
            roof_slope = np.arccos(abs(np.dot(z_axis, [0, 0, 1])))
            shadow_length = 0.3  # Base 30cm
            
            if roof_slope > 0.001:
                slope_shadow = np.tan(roof_slope) * window_height * 0.7
                shadow_length = max(shadow_length, slope_shadow)
                
                if roof_slope > np.radians(45):
                    shadow_length += 0.15
            
            # Check intersections
            if panel_local[1] < 0:  # Downslope
                shadow_width = window_width/2 + side_margin * 0.7
                if (abs(panel_local[0]) <= shadow_width + panel_width/2 and
                    abs(panel_local[1]) <= shadow_length + panel_length/2):
                    return True
            
            # Check direct vicinity
            half_width = window_width/2 + side_margin
            half_length_top = window_length/2 + top_margin
            half_length_bottom = window_length/2 + bottom_margin
            
            if panel_local[1] >= 0:  # Above window
                if (abs(panel_local[0]) <= half_width + panel_width/2 and
                    panel_local[1] <= half_length_top + panel_length/2):
                    return True
            else:  # Below window
                if (abs(panel_local[0]) <= half_width + panel_width/2 and
                    panel_local[1] >= -half_length_bottom - panel_length/2):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error in window intersection check: {e}")
            return True
    
    @staticmethod
    def _check_chimney_intersection(panel_center, panel_width, panel_length, 
                                  orientation_vectors, obstacle):
        """Check intersection with chimneys"""
        try:
            chimney_pos = obstacle.position
            
            if hasattr(obstacle, 'dimensions'):
                chimney_width, chimney_length, _ = obstacle.dimensions
            else:
                chimney_width = chimney_length = 0.6
            
            safety_margin = 0.15  # 15cm
            
            # Simple 2D distance check
            distance = np.linalg.norm(panel_center[:2] - chimney_pos[:2])
            panel_radius = np.sqrt(panel_width**2 + panel_length**2) / 2
            chimney_radius = np.sqrt(chimney_width**2 + chimney_length**2) / 2
            
            return distance < (panel_radius + chimney_radius + safety_margin)
            
        except Exception as e:
            print(f"Error in chimney intersection check: {e}")
            return True
    
    @staticmethod
    def _check_generic_intersection(panel_center, panel_width, panel_length, 
                                  orientation_vectors, obstacle):
        """Generic bounding box intersection check"""
        try:
            # Get obstacle bounds
            if hasattr(obstacle, 'get_bounds'):
                obstacle_bounds = obstacle.get_bounds()
            elif hasattr(obstacle, 'mesh') and hasattr(obstacle.mesh, 'bounds'):
                obstacle_bounds = obstacle.mesh.bounds
            else:
                return True  # Conservative
            
            # Calculate panel bounds
            half_width = panel_width / 2
            half_length = panel_length / 2
            
            panel_bounds = [
                panel_center[0] - half_width,  # min_x
                panel_center[0] + half_width,  # max_x
                panel_center[1] - half_length, # min_y
                panel_center[1] + half_length, # max_y
                panel_center[2] - 0.02,        # min_z
                panel_center[2] + 0.02         # max_z
            ]
            
            # AABB intersection test
            return not (panel_bounds[1] < obstacle_bounds[0] or
                       panel_bounds[0] > obstacle_bounds[1] or
                       panel_bounds[3] < obstacle_bounds[2] or
                       panel_bounds[2] > obstacle_bounds[3] or
                       panel_bounds[5] < obstacle_bounds[4] or
                       panel_bounds[4] > obstacle_bounds[5])
            
        except Exception as e:
            print(f"Error in generic intersection check: {e}")
            return True
