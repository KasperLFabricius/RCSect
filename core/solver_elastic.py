import numpy as np
from scipy.optimize import root
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import split, triangulate


def integrate_concrete_zone(geom, eps0, kx, ky, Ec_eff_kN_m2):
    """
    Integrate concrete compression resultants over a geometry where concrete is active.

    Compression-positive convention:
      N += sigma * dA
      Mx += sigma * y * dA
      My += sigma * x * dA
    """
    N_c = 0.0
    Mx_c = 0.0
    My_c = 0.0
    max_sigma_c = 0.0

    tri_qp = [
        (2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 1.0 / 6.0, 2.0 / 3.0),
    ]

    def integrate_triangle(triangle: Polygon):
        nonlocal N_c, Mx_c, My_c, max_sigma_c
        if len(triangle.interiors) > 0:
            for tri in triangulate(triangle):
                tri_clip = tri.intersection(triangle)
                integrate_geom(tri_clip)
            return

        coords = list(triangle.exterior.coords)[:-1]
        if len(coords) != 3:
            integrate_geom(triangle)
            return

        (x1, y1), (x2, y2), (x3, y3) = coords
        det_j = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        if det_j <= 0.0:
            return

        area = 0.5 * det_j
        weight = area / 3.0

        for l1, l2, l3 in tri_qp:
            x = l1 * x1 + l2 * x2 + l3 * x3
            y = l1 * y1 + l2 * y2 + l3 * y3
            eps = eps0 + kx * y + ky * x
            sigma = Ec_eff_kN_m2 * eps if eps > 0.0 else 0.0
            if sigma <= 0.0:
                continue

            N_c += sigma * weight
            Mx_c += sigma * y * weight
            My_c += sigma * x * weight
            max_sigma_c = max(max_sigma_c, sigma)

    def integrate_geom(g):
        if g is None or g.is_empty:
            return

        if isinstance(g, MultiPolygon):
            for part in g.geoms:
                integrate_geom(part)
            return

        if isinstance(g, Polygon):
            coords = list(g.exterior.coords)[:-1]
            if len(coords) == 3 and len(g.interiors) == 0:
                integrate_triangle(g)
                return

            for tri in triangulate(g):
                tri_clip = tri.intersection(g)
                integrate_geom(tri_clip)

        for part in getattr(g, "geoms", []):
            integrate_geom(part)

    integrate_geom(geom)
    return N_c, Mx_c, My_c, max_sigma_c


class ElasticSolver:
    def __init__(self, cross_section, E_c: float, E_s: float):
        self.cs = cross_section
        self.E_c = E_c
        self.E_s = E_s

    def solve_combined_loads(self, P_l, Mx_l, My_l, n_l, P_s, Mx_s, My_s, n_s):
        """
        Executes the 4-step ECROSS algorithm for combined long and short term loads.
        """
        # Step 1: Long-term state (Es/Ec = n_l)
        self.alpha_s = n_l
        res_long = self._solve_cracked_section(P_l, Mx_l, My_l)
        s1 = res_long["steel_stresses"]

        # Step 2: Fictitious reduction and internal forces
        reduction_factor = (1.0 - (n_s / n_l))
        s2 = {bar_id: stress * reduction_factor for bar_id, stress in s1.items()}

        N_neu = 0.0
        Mx_neu = 0.0
        My_neu = 0.0

        for bar in self.cs.rebar_mild:
            A_m2 = bar['area'] * 1e-6
            F_bar = -s2[bar['id']] * A_m2
            N_neu += F_bar
            Mx_neu += F_bar * bar['y']
            My_neu += F_bar * bar['x']

        # Step 3: Combined loads minus fictitious forces (Es/Ec = n_s)
        self.alpha_s = n_s
        P_comb = P_l + P_s - N_neu
        Mx_comb = Mx_l + Mx_s - Mx_neu
        My_comb = My_l + My_s - My_neu

        res_comb = self._solve_cracked_section(P_comb, Mx_comb, My_comb)
        s3 = res_comb["steel_stresses"]  # This is RST1

        # Step 4: Final Summation
        total_stresses = {bar_id: s2[bar_id] + s3[bar_id] for bar_id in s1}

        return {
            "max_concrete": res_comb["max_concrete_compression"],
            "RST_total": total_stresses,
            "LONG_s1": s1,
            "RST1_s3": s3,
            "DIF": {bar_id: total_stresses[bar_id] - s1[bar_id] for bar_id in s1},
            "na_LONG": {
                "eps0": float(res_long["eps0"]),
                "kx": float(res_long["kx"]),
                "ky": float(res_long["ky"]),
            },
            "na_RST1": {
                "eps0": float(res_comb["eps0"]),
                "kx": float(res_comb["kx"]),
                "ky": float(res_comb["ky"]),
            },
        }

    def _compression_zone(self, eps0, kx, ky):
        concrete_polygon = self.cs.base_concrete_poly
        if concrete_polygon is None or concrete_polygon.is_empty:
            return concrete_polygon

        a = ky
        b = kx
        c = eps0

        minx, miny, maxx, maxy = concrete_polygon.bounds
        width = maxx - minx
        height = maxy - miny
        margin = 10.0 * max(width, height) + 1.0

        big_box = box(minx - margin, miny - margin, maxx + margin, maxy + margin)

        if abs(a) < 1e-18 and abs(b) < 1e-18:
            return concrete_polygon if c > 0.0 else Polygon()

        if abs(b) > 1e-12:
            x1 = minx - margin
            x2 = maxx + margin
            y1 = -(a * x1 + c) / b
            y2 = -(a * x2 + c) / b
            na_line = LineString([(x1, y1), (x2, y2)])
        else:
            y1 = miny - margin
            y2 = maxy + margin
            x1 = -(b * y1 + c) / a
            x2 = -(b * y2 + c) / a
            na_line = LineString([(x1, y1), (x2, y2)])

        pieces = split(big_box, na_line)
        compression_half = None
        for piece in pieces.geoms:
            cent = piece.centroid
            if a * cent.x + b * cent.y + c > 0.0:
                compression_half = piece
                break

        if compression_half is None:
            return Polygon()

        return concrete_polygon.intersection(compression_half)

    def _area_moments(self, geom):
        I0 = 0.0
        Ix = 0.0
        Iy = 0.0
        Ixx = 0.0
        Iyy = 0.0
        Ixy = 0.0

        tri_qp = [
            (2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0),
            (1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0),
            (1.0 / 6.0, 1.0 / 6.0, 2.0 / 3.0),
        ]

        def integrate_triangle(triangle: Polygon):
            nonlocal I0, Ix, Iy, Ixx, Iyy, Ixy
            if len(triangle.interiors) > 0:
                for tri in triangulate(triangle):
                    tri_clip = tri.intersection(triangle)
                    integrate_geom(tri_clip)
                return

            coords = list(triangle.exterior.coords)[:-1]
            if len(coords) != 3:
                integrate_geom(triangle)
                return

            (x1, y1), (x2, y2), (x3, y3) = coords
            det_j = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
            if det_j <= 0.0:
                return

            area = 0.5 * det_j
            weight = area / 3.0

            for l1, l2, l3 in tri_qp:
                x = l1 * x1 + l2 * x2 + l3 * x3
                y = l1 * y1 + l2 * y2 + l3 * y3
                I0 += weight
                Ix += x * weight
                Iy += y * weight
                Ixx += x * x * weight
                Iyy += y * y * weight
                Ixy += x * y * weight

        def integrate_geom(g):
            if g is None or g.is_empty:
                return

            if isinstance(g, MultiPolygon):
                for part in g.geoms:
                    integrate_geom(part)
                return

            if isinstance(g, Polygon):
                coords = list(g.exterior.coords)[:-1]
                if len(coords) == 3 and len(g.interiors) == 0:
                    integrate_triangle(g)
                    return

                for tri in triangulate(g):
                    tri_clip = tri.intersection(g)
                    integrate_geom(tri_clip)

            for part in getattr(g, "geoms", []):
                integrate_geom(part)

        integrate_geom(geom)
        return I0, Ix, Iy, Ixx, Iyy, Ixy

    def _initial_guess(self, P, Mx, My):
        if self.alpha_s <= 0.0:
            raise ValueError("alpha_s must be positive to compute elastic transformed section.")

        Es_kN_m2 = self.E_s * 1000.0
        Ec_eff_kN_m2 = Es_kN_m2 / self.alpha_s

        concrete = self.cs.base_concrete_poly
        I0, Ix, Iy, Ixx, Iyy, Ixy = self._area_moments(concrete)

        K = Ec_eff_kN_m2 * np.array([
            [I0, Iy, Ix],
            [Iy, Iyy, Ixy],
            [Ix, Ixy, Ixx],
        ], dtype=float)

        for bar in self.cs.rebar_mild:
            A = bar['area'] * 1e-6
            x = bar['x']
            y = bar['y']
            K += Es_kN_m2 * A * np.array([
                [1.0, y, x],
                [y, y * y, x * y],
                [x, x * y, x * x],
            ], dtype=float)

        rhs = np.array([P, Mx, My], dtype=float)

        try:
            return np.linalg.solve(K, rhs)
        except np.linalg.LinAlgError:
            minx, miny, maxx, maxy = concrete.bounds
            L = max(maxx - minx, maxy - miny, 1e-6)
            A = max(concrete.area, 1e-9)
            eps0 = P / (Ec_eff_kN_m2 * A)
            kx = Mx / (Ec_eff_kN_m2 * A * L * L)
            ky = My / (Ec_eff_kN_m2 * A * L * L)
            return np.array([eps0, kx, ky], dtype=float)

    def _solve_cracked_section(self, P_target, Mx_target, My_target):
        if self.alpha_s <= 0.0:
            raise ValueError("alpha_s must be > 0.")

        Es_kN_m2 = self.E_s * 1000.0
        Ec_eff_kN_m2 = Es_kN_m2 / self.alpha_s

        def section_response(eps0, kx, ky):
            compression_zone = self._compression_zone(eps0, kx, ky)
            N_c, Mx_c, My_c, max_sigma_c = integrate_concrete_zone(
                compression_zone, eps0, kx, ky, Ec_eff_kN_m2
            )

            N_s = 0.0
            Mx_s = 0.0
            My_s = 0.0
            steel_stresses = {}

            for bar in self.cs.rebar_mild:
                x = bar['x']
                y = bar['y']
                A_m2 = bar['area'] * 1e-6
                eps = eps0 + kx * y + ky * x

                sigma_s = -Es_kN_m2 * eps  # tension-positive
                F_s = Es_kN_m2 * eps * A_m2  # compression-positive

                steel_stresses[bar['id']] = sigma_s
                N_s += F_s
                Mx_s += F_s * y
                My_s += F_s * x

            return {
                "N": N_c + N_s,
                "Mx": Mx_c + Mx_s,
                "My": My_c + My_s,
                "steel_stresses": steel_stresses,
                "max_concrete_compression": max_sigma_c,
            }

        def residual(u):
            eps0, kx, ky = u
            resp = section_response(eps0, kx, ky)
            return np.array([
                resp["N"] - P_target,
                resp["Mx"] - Mx_target,
                resp["My"] - My_target,
            ], dtype=float)

        x0 = self._initial_guess(P_target, Mx_target, My_target)
        sol = root(residual, x0, method="lm", options={"maxfev": 2000})

        if not sol.success:
            x1 = np.array([x0[0], 5.0 * x0[1], 5.0 * x0[2]], dtype=float)
            sol = root(residual, x1, method="lm", options={"maxfev": 2000})

        if not sol.success:
            res_norm = float(np.linalg.norm(residual(sol.x)))
            raise RuntimeError(
                "Cracked elastic solve failed for "
                f"P={P_target}, Mx={Mx_target}, My={My_target}; residual norm={res_norm:.6e}"
            )

        eps0, kx, ky = sol.x
        resp = section_response(eps0, kx, ky)

        x_int = -eps0 / ky if abs(ky) > 1e-12 else float("inf")
        y_int = -eps0 / kx if abs(kx) > 1e-12 else float("inf")

        return {
            "steel_stresses": resp["steel_stresses"],
            "max_concrete_compression": resp["max_concrete_compression"],
            "na_intersect_x": x_int,
            "na_intersect_y": y_int,
            "eps0": eps0,
            "kx": kx,
            "ky": ky,
            "converged": bool(sol.success),
        }
