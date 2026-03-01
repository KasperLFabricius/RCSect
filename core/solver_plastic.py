import numpy as np
from scipy.optimize import brentq
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import triangulate
from core.geometry import split_compression_zone
import warnings

class PlasticSolver:
    """
    Calculates the ultimate flexural capacity of a cross section 
    for a given axial load P and neutral axis angle V.
    """
    def __init__(self, cross_section, concrete, mild_steel, prestressed_steel=None):
        self.cs = cross_section
        self.concrete = concrete
        self.mild_steel = mild_steel
        self.prestressed_steel = prestressed_steel
        
        # Calculate full utilization force for W1/W2 warnings
        # Assuming gross net area * f_cd. Requires verification.
        self.gross_concrete_area = self.cs.base_concrete_poly.area
        self.N_c_util = self.gross_concrete_area * (self.concrete.f_cd * 1000.0) # in kN
        
    def solve(self, angle_v_deg: float, P_target: float):
        """
        Main solver routine. Rotates the section, determines the failure pivot,
        finds the neutral axis depth y_na, and calculates ultimate moments Mx and My.
        """
        self.poly_rot, self.rebar_mild_rot, self.rebar_pre_rot = self.cs.get_rotated_system(angle_v_deg)
        
        minx, miny, maxx, maxy = self.poly_rot.bounds
        self.y_top = maxy
        self.y_bottom = miny
        
        y_steels = [bar['y'] for bar in self.rebar_mild_rot]
        if self.rebar_pre_rot:
            y_steels.extend([bar['y'] for bar in self.rebar_pre_rot])
        
        self.y_steel_min = min(y_steels) if y_steels else miny
        
        try:
            y_na_solution = brentq(
                self._equilibrium_target, 
                a=self.y_steel_min - 0.1, 
                b=self.y_top + 10.0, 
                args=(P_target, 'concrete_controls')
            )
            pivot_type = 'concrete_controls'
            kappa = self.concrete.eps_cu2 / (self.y_top - y_na_solution)
            
            eps_s_max = kappa * (y_na_solution - self.y_steel_min)
            if eps_s_max > self.mild_steel.eps_ud:
                raise ValueError("Steel ruptured before concrete crushed.")
                
        except ValueError:
            y_na_solution = brentq(
                self._equilibrium_target, 
                a=self.y_steel_min + 0.001, 
                b=self.y_top + 10.0, 
                args=(P_target, 'steel_controls')
            )
            pivot_type = 'steel_controls'
            kappa = self.mild_steel.eps_ud / (y_na_solution - self.y_steel_min)

        forces_data = self._calculate_detailed_internal_forces(y_na_solution, kappa)
        
        # 1. Coordinate Transformations
        angle_rad = np.radians(angle_v_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        Mx_global = forces_data['Mx_rot'] * cos_a + forces_data['My_rot'] * sin_a
        My_global = -forces_data['Mx_rot'] * sin_a + forces_data['My_rot'] * cos_a
        
        # [cite_start]2. Neutral Axis Intersections [cite: 760]
        intersection_y = y_na_solution / cos_a if abs(cos_a) > 1e-6 else float('inf')
        intersection_x = -y_na_solution / sin_a if abs(sin_a) > 1e-6 else float('inf')

        # [cite_start]3. Maximum Strains [cite: 761]
        max_concrete_strain = kappa * (self.y_top - y_na_solution) * 1000.0 # per mille
        max_mild_strain = 0.0
        if self.rebar_mild_rot:
            max_mild_strain = max([kappa * (y_na_solution - bar['y']) for bar in self.rebar_mild_rot]) * 1000.0

        # [cite_start]4. Lever Arm Calculations [cite: 762, 763, 773, 784]
        c_comp = forces_data['centroid_compression']
        c_tens = forces_data['centroid_tension']
        
        DX_rot = c_comp['x'] - c_tens['x'] if c_tens['x'] is not None else 0.0
        DY_rot = c_comp['y'] - c_tens['y'] if c_tens['y'] is not None else 0.0
        
        DX_global = DX_rot * cos_a + DY_rot * sin_a
        DY_global = -DX_rot * sin_a + DY_rot * cos_a
        L = np.sqrt(DX_global**2 + DY_global**2)
        
        # [cite_start]5. Safety Warnings [cite: 766, 767]
        warning_flag = None
        if forces_data['compression_rebar_force'] > self.N_c_util:
            warning_flag = "W2"
        elif forces_data['compression_rebar_force'] > 0.5 * self.N_c_util:
            warning_flag = "W1"

        return {
            "y_na": y_na_solution,
            "kappa": kappa,
            "pivot": pivot_type,
            "N_calc": forces_data['N_tot'],
            "Mx": Mx_global,
            "My": My_global,
            "na_intersect_x": intersection_x,
            "na_intersect_y": intersection_y,
            "strain_concrete": max_concrete_strain,
            "strain_mild": max_mild_strain,
            "compress_force": forces_data['total_compression'],
            "lever_L": L,
            "lever_DX": DX_global,
            "lever_DY": DY_global,
            "warning": warning_flag
        }

    def _equilibrium_target(self, y_na: float, P_target: float, pivot: str) -> float:
        if pivot == 'concrete_controls':
            kappa = self.concrete.eps_cu2 / (self.y_top - y_na)
        else:
            kappa = self.mild_steel.eps_ud / (y_na - self.y_steel_min)
            
        forces = self._calculate_detailed_internal_forces(y_na, kappa)
        return forces['N_tot'] - P_target

    def _calculate_detailed_internal_forces(self, y_na: float, kappa: float):
        N_tot = 0.0
        Mx_rot = 0.0
        My_rot = 0.0
        
        total_compression = 0.0
        total_tension = 0.0
        comp_rebar_force = 0.0
        
        sum_x_comp, sum_y_comp = 0.0, 0.0
        sum_x_tens, sum_y_tens = 0.0, 0.0

        # --- MILD STEEL ---
        for bar in self.rebar_mild_rot:
            eps = kappa * (y_na - bar['y']) # Tension is positive
            sigma = self.mild_steel.stress(eps)
            force = sigma * bar['area'] * 1e-6 
            
            N_tot += force
            Mx_rot += force * bar['y']
            My_rot += force * bar['x']
            
            if force < 0: # Compression
                abs_f = abs(force)
                total_compression += abs_f
                comp_rebar_force += abs_f
                sum_x_comp += abs_f * bar['x']
                sum_y_comp += abs_f * bar['y']
            else:
                total_tension += force
                sum_x_tens += force * bar['x']
                sum_y_tens += force * bar['y']
                
        # --- PRESTRESSED STEEL ---
        if self.prestressed_steel:
            for bar in self.rebar_pre_rot:
                eps = kappa * (y_na - bar['y'])
                sigma = self.prestressed_steel.stress(eps)
                force = sigma * bar['area'] * 1e-6
                
                N_tot += force
                Mx_rot += force * bar['y']
                My_rot += force * bar['x']
                
                if force < 0:
                    abs_f = abs(force)
                    total_compression += abs_f
                    comp_rebar_force += abs_f
                    sum_x_comp += abs_f * bar['x']
                    sum_y_comp += abs_f * bar['y']
                else:
                    total_tension += force
                    sum_x_tens += force * bar['x']
                    sum_y_tens += force * bar['y']
                
        # --- CONCRETE ---
        y_c2 = y_na + (self.concrete.eps_c2 / kappa) if kappa != 0 else y_na
        poly_parabola, poly_rect = split_compression_zone(self.poly_rot, y_na, y_c2)
        
        if poly_rect is not None and not poly_rect.is_empty:
            area = poly_rect.area
            centroid = poly_rect.centroid
            force = -(self.concrete.f_cd * area * 1000.0) # Negative for compression
            abs_f = abs(force)
            
            N_tot += force
            Mx_rot += force * centroid.y
            My_rot += force * centroid.x
            
            total_compression += abs_f
            sum_x_comp += abs_f * centroid.x
            sum_y_comp += abs_f * centroid.y
            
        if poly_parabola is not None and not poly_parabola.is_empty:
            F_p, Mxp_p, Myp_p, cx, cy = self._integrate_parabola(poly_parabola, y_na, kappa)
            abs_f = abs(F_p)
            
            N_tot += F_p
            Mx_rot += Mxp_p
            My_rot += Myp_p
            
            total_compression += abs_f
            sum_x_comp += abs_f * cx
            sum_y_comp += abs_f * cy

        # Centroid Resolutions
        c_comp = {'x': sum_x_comp / total_compression if total_compression > 0 else 0.0,
                  'y': sum_y_comp / total_compression if total_compression > 0 else 0.0}
        c_tens = {'x': sum_x_tens / total_tension if total_tension > 0 else None,
                  'y': sum_y_tens / total_tension if total_tension > 0 else None}

        return {
            'N_tot': N_tot,
            'Mx_rot': Mx_rot,
            'My_rot': My_rot,
            'total_compression': total_compression,
            'compression_rebar_force': comp_rebar_force,
            'centroid_compression': c_comp,
            'centroid_tension': c_tens
        }

    def _integrate_parabola(self, polygon, y_na, kappa):
        """
        Numerically integrates the EC2 parabolic compression block over a polygon.

        Returns:
            F (kN): negative for compression
            Mx (kNm): accumulated with Mx += force * y
            My (kNm): accumulated with My += force * x
            cx, cy (m): stress-resultant centroid coordinates
        """
        if kappa <= 0:
            raise ValueError("Parabolic integration requires kappa > 0.")

        if polygon is None or polygon.is_empty:
            return 0.0, 0.0, 0.0, 0.0, 0.0

        if isinstance(polygon, Polygon):
            polygon_parts = [polygon]
        elif isinstance(polygon, MultiPolygon):
            polygon_parts = [part for part in polygon.geoms if not part.is_empty]
        else:
            polygon_parts = [
                geom for geom in getattr(polygon, "geoms", [])
                if isinstance(geom, (Polygon, MultiPolygon)) and not geom.is_empty
            ]

        # 6-point Dunavant rule (degree 4) on reference triangle.
        tri_qp = [
            (0.445948490915965, 0.445948490915965, 0.111690794839005),
            (0.445948490915965, 0.108103018168070, 0.111690794839005),
            (0.108103018168070, 0.445948490915965, 0.111690794839005),
            (0.091576213509771, 0.091576213509771, 0.054975871827661),
            (0.091576213509771, 0.816847572980459, 0.054975871827661),
            (0.816847572980459, 0.091576213509771, 0.054975871827661),
        ]

        I0, Ix, Iy = 0.0, 0.0, 0.0

        def integrate_triangle(triangle: Polygon):
            nonlocal I0, Ix, Iy
            coords = list(triangle.exterior.coords)
            if len(coords) < 4:
                return
            (x1, y1), (x2, y2), (x3, y3) = coords[0], coords[1], coords[2]

            det_j = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
            if det_j <= 0.0:
                return

            for l1, l2, weight in tri_qp:
                l3 = 1.0 - l1 - l2
                x = l1 * x1 + l2 * x2 + l3 * x3
                y = l1 * y1 + l2 * y2 + l3 * y3
                eps_c = kappa * (y - y_na)
                sigma = self.concrete.stress(eps_c)
                if sigma <= 0.0:
                    continue

                dA = det_j * weight
                I0 += sigma * dA
                Ix += sigma * x * dA
                Iy += sigma * y * dA

        for part in polygon_parts:
            for tri in triangulate(part):
                inside = tri.intersection(part)
                if inside.is_empty:
                    continue

                if isinstance(inside, Polygon):
                    for sub_tri in triangulate(inside):
                        clipped = sub_tri.intersection(inside)
                        if isinstance(clipped, Polygon) and not clipped.is_empty:
                            integrate_triangle(clipped)
                elif isinstance(inside, MultiPolygon):
                    for inside_part in inside.geoms:
                        if inside_part.is_empty:
                            continue
                        for sub_tri in triangulate(inside_part):
                            clipped = sub_tri.intersection(inside_part)
                            if isinstance(clipped, Polygon) and not clipped.is_empty:
                                integrate_triangle(clipped)

        if I0 <= 1e-16:
            return 0.0, 0.0, 0.0, 0.0, 0.0

        F = -1000.0 * I0
        My = -1000.0 * Ix
        Mx = -1000.0 * Iy
        cx = Ix / I0
        cy = Iy / I0
        return F, Mx, My, cx, cy
