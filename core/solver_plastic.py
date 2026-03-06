import numpy as np
from scipy.optimize import brentq
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import triangulate
from core.geometry import split_compression_zone
import warnings


def _effective_prestress_eps0(bar: dict, default_eps0: float) -> float:
    """Resolve effective prestress initial strain for a bar."""
    eps0 = bar.get("eps0", None)
    if eps0 is None:
        return default_eps0
    try:
        eps0_f = float(eps0)
    except (TypeError, ValueError):
        return default_eps0
    return eps0_f if np.isfinite(eps0_f) else default_eps0


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
        default_eps0 = float(getattr(prestressed_steel, "initial_strain", 0.0) or 0.0) if prestressed_steel is not None else 0.0
        self.prestrain_default = default_eps0 if np.isfinite(default_eps0) else 0.0
        
        # Calculate full utilization force for W1/W2 warnings
        # Assuming gross net area * f_cd. Requires verification.
        self.gross_concrete_area = self.cs.base_concrete_poly.area
        self.N_c_util = self.gross_concrete_area * (self.concrete.f_cd * 1000.0) # in kN
        
    def solve(self, angle_v_deg: float, P_target: float):
        """
        Main solver routine. Rotates the section, determines the failure pivot,
        finds the neutral axis depth y_na, and calculates ultimate moments Mx and My.

        Axial-force convention:
        - P_target is external design axial force N_Ed, compression-positive.
        - N_calc is returned with the same compression-positive convention.
        - Prestress is internal and enters through prestressing initial strain eps0.
        """
        candidates = self._solve_candidates(angle_v_deg, P_target)
        if not candidates:
            raise RuntimeError(
                "Plastic solver failed to bracket neutral axis for "
                f"P_target={P_target}, angle V={angle_v_deg} deg. "
                "Check P sign convention (compression positive), or reduce |P_target|. "
                "Attempts: concrete_controls/steel_controls"
            )
        if len(candidates) == 1:
            return candidates[0]

        # Deterministic single-angle tie-breaker: choose lower absolute curvature.
        best = min(candidates, key=lambda c: (abs(c['kappa']), c['pivot']))
        return best

    def solve_angle_sweep(self, angle_values_deg, P_target: float):
        """
        Solve a sequence of angles with deterministic branch continuity.

        If multiple admissible candidates exist at an angle:
        - first angle: choose candidate with smaller |kappa|
        - subsequent angles: choose the candidate with minimum normalized
          jump from the previously accepted angle.
        """
        results = []
        prev = None
        for angle in angle_values_deg:
            candidates = self._solve_candidates(angle, P_target)
            if not candidates:
                raise RuntimeError(
                    "Plastic solver failed to find admissible candidate for "
                    f"P_target={P_target}, angle V={angle} deg"
                )

            if len(candidates) == 1:
                chosen = candidates[0]
            elif prev is None:
                chosen = min(candidates, key=lambda c: (abs(c['kappa']), c['pivot']))
            else:
                scale_m = max(abs(prev['Mx']), abs(prev['My']), 1.0)
                scale_y = max(self.y_top - self.y_bottom, 1e-3)
                scale_k = max(abs(prev['kappa']), 1e-5)

                def continuity_score(c):
                    return (
                        abs(c['Mx'] - prev['Mx']) / scale_m
                        + abs(c['My'] - prev['My']) / scale_m
                        + 0.5 * abs(c['y_na'] - prev['y_na']) / scale_y
                        + 0.5 * abs(c['kappa'] - prev['kappa']) / scale_k
                    )

                chosen = min(candidates, key=lambda c: (continuity_score(c), c['pivot']))

            results.append(chosen)
            prev = chosen

        return results

    def _solve_candidates(self, angle_v_deg: float, P_target: float):
        """Return all admissible plastic candidates for one (V, P_target) pair."""
        self._prepare_rotated_state(angle_v_deg)

        height = self.y_top - self.y_bottom
        candidates = []

        y_min_conc = self.y_bottom - 0.5 * height
        y_max_conc = self.y_top + 2.0 * height
        conc_candidate = self._solve_pivot_candidate(
            P_target=P_target,
            pivot='concrete_controls',
            y_min=y_min_conc,
            y_max=y_max_conc,
        )
        if conc_candidate is not None:
            candidates.append(self._assemble_solution(angle_v_deg, conc_candidate))

        y_min_steel = self.y_steel_min + 1e-4 * height
        y_max_steel = self.y_top + 2.0 * height
        steel_candidate = self._solve_pivot_candidate(
            P_target=P_target,
            pivot='steel_controls',
            y_min=y_min_steel,
            y_max=y_max_steel,
        )
        if steel_candidate is not None:
            candidates.append(self._assemble_solution(angle_v_deg, steel_candidate))

        return sorted(candidates, key=lambda c: c['pivot'])

    def _prepare_rotated_state(self, angle_v_deg: float):
        self.poly_rot, self.rebar_mild_rot, self.rebar_pre_rot = self.cs.get_rotated_system(angle_v_deg)

        default_eps0 = float(getattr(self.prestressed_steel, "initial_strain", 0.0) or 0.0) if self.prestressed_steel is not None else 0.0
        self.prestrain_default = default_eps0 if np.isfinite(default_eps0) else 0.0

        minx, miny, maxx, maxy = self.poly_rot.bounds
        self.y_top = maxy
        self.y_bottom = miny

        y_steels = [bar['y'] for bar in self.rebar_mild_rot]
        if self.rebar_pre_rot:
            y_steels.extend([bar['y'] for bar in self.rebar_pre_rot])
        self.y_steel_min = min(y_steels) if y_steels else miny

    def _assemble_solution(self, angle_v_deg: float, candidate: dict) -> dict:
        y_na_solution = candidate['y_na']
        kappa = candidate['kappa']
        pivot_type = candidate['pivot']
        forces_data = self._calculate_detailed_internal_forces(y_na_solution, kappa)
        
        # 1. Coordinate Transformations
        angle_rad = np.radians(self.cs.local_rotation_deg(angle_v_deg))
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # Transform local moments (x', y') back to global (x, y): R(phi).
        Mx_global = forces_data['Mx_rot'] * cos_a - forces_data['My_rot'] * sin_a
        My_global = forces_data['Mx_rot'] * sin_a + forces_data['My_rot'] * cos_a
        
        # [cite_start]2. Neutral Axis Intersections [cite: 760]
        intersection_y = y_na_solution / cos_a if abs(cos_a) > 1e-6 else float('inf')
        intersection_x = y_na_solution / sin_a if abs(sin_a) > 1e-6 else float('inf')

        # [cite_start]3. Maximum Strains [cite: 761]
        max_concrete_strain = kappa * (self.y_top - y_na_solution) * 1000.0 # per mille
        max_mild_strain = 0.0
        if self.rebar_mild_rot:
            max_mild_strain = max([kappa * (y_na_solution - bar['y']) for bar in self.rebar_mild_rot]) * 1000.0
        max_prestressed_strain = None
        if self.rebar_pre_rot:
            # Keep the same reporting convention as strain_mild: report the maximum
            # signed total strain among bars (tension-positive), in permille.
            max_prestressed_strain = (
                max(
                    [
                        kappa * (y_na_solution - bar['y']) + _effective_prestress_eps0(bar, self.prestrain_default)
                        for bar in self.rebar_pre_rot
                    ]
                )
                * 1000.0
            )

        # [cite_start]4. Lever Arm Calculations [cite: 762, 763, 773, 784]
        c_comp = forces_data['centroid_compression']
        c_tens = forces_data['centroid_tension']
        
        DX_rot = c_comp['x'] - c_tens['x'] if c_tens['x'] is not None else 0.0
        DY_rot = c_comp['y'] - c_tens['y'] if c_tens['y'] is not None else 0.0
        
        DX_global = DX_rot * cos_a - DY_rot * sin_a
        DY_global = DX_rot * sin_a + DY_rot * cos_a
        L = np.sqrt(DX_global**2 + DY_global**2)
        
        # [cite_start]5. Safety Warnings [cite: 766, 767]
        warning_flag = None
        if forces_data['compression_rebar_force'] > self.N_c_util:
            warning_flag = "W2"
        elif forces_data['compression_rebar_force'] > 0.5 * self.N_c_util:
            warning_flag = "W1"

        return {
            "angle_v_deg": float(angle_v_deg),
            "y_na": y_na_solution,
            "kappa": kappa,
            "pivot": pivot_type,
            "N_calc": self._to_compression_positive(forces_data['N_tot']),
            "Mx": Mx_global,
            "My": My_global,
            "na_intersect_x": intersection_x,
            "na_intersect_y": intersection_y,
            "strain_concrete": max_concrete_strain,
            "strain_mild": max_mild_strain,
            "strain_prestressed": max_prestressed_strain,
            "compress_force": forces_data['total_compression'],
            "lever_L": L,
            "lever_DX": DX_global,
            "lever_DY": DY_global,
            "warning": warning_flag,
            "residual_abs": candidate.get('residual_abs', abs(self._equilibrium_target(y_na_solution, candidate.get('P_target', 0.0), pivot_type))),
        }

    def _equilibrium_target(self, y_na: float, P_target: float, pivot: str) -> float:
        if abs(self.y_top - y_na) < 1e-9:
            return np.nan

        if pivot == 'concrete_controls':
            kappa = self.concrete.eps_cu2 / (self.y_top - y_na)
        else:
            kappa = self.mild_steel.eps_ud / (y_na - self.y_steel_min)
            
        forces = self._calculate_detailed_internal_forces(y_na, kappa)
        N_internal = self._to_compression_positive(forces['N_tot'])
        return N_internal - P_target

    @staticmethod
    def _to_compression_positive(N_internal_signed: float) -> float:
        """
        Convert solver internal resultant to compression-positive convention.

        Internal accumulation uses force sign from material stress:
        tension positive, compression negative. This helper converts to the
        external N_Ed convention where compression is positive.
        """
        return -N_internal_signed

    def _solve_pivot_candidate(self, P_target: float, pivot: str, y_min: float, y_max: float):
        bracket = self._find_bracket(P_target, pivot, y_min, y_max)
        if bracket is None:
            return None

        try:
            y_na = brentq(self._equilibrium_target, bracket[0], bracket[1], args=(P_target, pivot))
        except ValueError:
            return None

        if pivot == 'concrete_controls':
            if abs(self.y_top - y_na) < 1e-12:
                return None
            kappa = self.concrete.eps_cu2 / (self.y_top - y_na)
            eps_s_max = kappa * (y_na - self.y_steel_min)
            if eps_s_max > self.mild_steel.eps_ud:
                return None
        else:
            if abs(y_na - self.y_steel_min) < 1e-12:
                return None
            kappa = self.mild_steel.eps_ud / (y_na - self.y_steel_min)

        residual = self._equilibrium_target(y_na, P_target, pivot)
        return {
            'pivot': pivot,
            'y_na': y_na,
            'kappa': kappa,
            'P_target': P_target,
            'residual_abs': abs(residual),
        }

    def _find_bracket(self, P_target, pivot, y_min, y_max, n=80):
        y_values = np.linspace(y_min, y_max, n)
        f_values = [self._equilibrium_target(y, P_target, pivot) for y in y_values]

        for i in range(len(y_values) - 1):
            f_i = f_values[i]
            f_j = f_values[i + 1]
            if not np.isfinite(f_i) or not np.isfinite(f_j):
                continue
            if f_i * f_j < 0.0:
                return y_values[i], y_values[i + 1]

        return None

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
                geometric_eps = kappa * (y_na - bar['y'])
                total_eps = geometric_eps + _effective_prestress_eps0(bar, self.prestrain_default)
                sigma = self.prestressed_steel.stress(total_eps)
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
            if len(triangle.interiors) > 0:
                integrate_geom(triangle)
                return

            coords = list(triangle.exterior.coords)[:-1]
            if len(coords) != 3:
                integrate_geom(triangle)
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

        def integrate_geom(geom):
            if geom is None or geom.is_empty:
                return

            if isinstance(geom, MultiPolygon):
                for part in geom.geoms:
                    if not part.is_empty:
                        integrate_geom(part)
                return

            if isinstance(geom, Polygon):
                coords = list(geom.exterior.coords)[:-1]
                if len(coords) == 3 and len(geom.interiors) == 0:
                    integrate_triangle(geom)
                    return

                for tri in triangulate(geom):
                    tri_clip = tri.intersection(geom)
                    integrate_geom(tri_clip)

            for sub_geom in getattr(geom, "geoms", []):
                integrate_geom(sub_geom)

        integrate_geom(polygon)

        if I0 <= 1e-16:
            return 0.0, 0.0, 0.0, 0.0, 0.0

        F = -1000.0 * I0
        My = -1000.0 * Ix
        Mx = -1000.0 * Iy
        cx = Ix / I0
        cy = Iy / I0
        return F, Mx, My, cx, cy
