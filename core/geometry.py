import numpy as np
from shapely.geometry import Polygon, box
from shapely.affinity import rotate

class CrossSection:
    """
    Manages the physical geometry of the concrete section and reinforcement.
    Handles coordinate transformations for neutral axis alignment.
    """
    def __init__(self, concrete_outline: list, concrete_voids: list, 
                 rebar_mild: list, rebar_prestressed: list):
        
        # Define the base concrete polygon with any potential voids
        self.base_concrete_poly = Polygon(
            [(pt['x'], pt['y']) for pt in concrete_outline],
            [[(pt['x'], pt['y']) for pt in void] for void in concrete_voids]
        )
        
        self.rebar_mild = rebar_mild
        self.rebar_prestressed = rebar_prestressed

    def get_rotated_system(self, angle_v_deg: float):
        """
        Returns a new snapshot of the geometry rotated from global to solver-local axes.

        Sign convention used in the plastic solver path:
        - V is the angle between the neutral axis and global +Y axis.
        - Positive V is counter-clockwise.
        - Local +X' is aligned with the neutral axis and +Y' is normal to it.

        The local system is built by rotating global coordinates by
        phi = (V - 90 deg), so the neutral axis becomes y' = const.
        """
        # Shapely rotates counter-clockwise by default.
        rotation_angle = self.local_rotation_deg(angle_v_deg)
        
        # Rotate concrete polygon around the origin (0,0)
        rotated_poly = rotate(self.base_concrete_poly, rotation_angle, origin=(0, 0))
        
        # Rotate mild reinforcement
        rotated_mild = self._rotate_bars(self.rebar_mild, rotation_angle)
        
        # Rotate prestressed reinforcement
        rotated_pre = self._rotate_bars(self.rebar_prestressed, rotation_angle)
        
        return rotated_poly, rotated_mild, rotated_pre

    @staticmethod
    def local_rotation_deg(angle_v_deg: float) -> float:
        """Rotation angle (global -> local) used by the plastic solver."""
        return float(angle_v_deg) - 90.0

    def _rotate_bars(self, bars: list, angle_deg: float) -> list:
        """Helper method to rotate a list of bar dictionaries."""
        angle_rad = np.radians(angle_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        rotated_bars = []
        for bar in bars:
            x_rot = bar['x'] * cos_a - bar['y'] * sin_a
            y_rot = bar['x'] * sin_a + bar['y'] * cos_a
            rotated_bar = dict(bar)
            rotated_bar['x'] = x_rot
            rotated_bar['y'] = y_rot
            rotated_bars.append(rotated_bar)
        return rotated_bars

def split_compression_zone(rotated_poly: Polygon, y_na: float, y_c2: float = None):
    """
    Slices the rotated concrete polygon to isolate the active compression zone.
    If y_c2 (depth of transition strain) is provided, it splits the zone into 
    the parabolic part and the rectangular part for exact integration.
    """
    bounds = rotated_poly.bounds  # (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = bounds
    
    # If the neutral axis is above the entire section, there is no compression
    if y_na >= maxy:
        return None, None
        
    # The entire zone above the neutral axis
    compression_box = box(minx - 1, y_na, maxx + 1, maxy + 1)
    compression_zone = rotated_poly.intersection(compression_box)
    
    if compression_zone.is_empty:
        return None, None

    if y_c2 is None or y_c2 >= maxy:
        # Entire compression zone is parabolic (max strain < eps_c2)
        return compression_zone, None
    elif y_c2 <= y_na:
        # Entire compression zone is rectangular (extremely rare, theoretical)
        return None, compression_zone
    else:
        # Split into parabolic block (y_na to y_c2) and rectangular block (y_c2 to maxy)
        parabola_box = box(minx - 1, y_na, maxx + 1, y_c2)
        rect_box = box(minx - 1, y_c2, maxx + 1, maxy + 1)
        
        poly_parabola = compression_zone.intersection(parabola_box)
        poly_rect = compression_zone.intersection(rect_box)
        
        return poly_parabola, poly_rect
