import numpy as np
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import triangulate


TRI_QP = [
    (2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0),
    (1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0),
    (1.0 / 6.0, 1.0 / 6.0, 2.0 / 3.0),
]


def area_moments(geom):
    I0 = 0.0
    Ix = 0.0
    Iy = 0.0
    Ixx = 0.0
    Iyy = 0.0
    Ixy = 0.0

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

        for l1, l2, l3 in TRI_QP:
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
            return

        for part in getattr(g, "geoms", []):
            integrate_geom(part)

    integrate_geom(geom)
    return I0, Ix, Iy, Ixx, Iyy, Ixy


def centroid_and_principal_axes(geom):
    A, Ix, Iy, Ixx, Iyy, Ixy = area_moments(geom)
    if A <= 0.0:
        raise ValueError("Section area must be positive.")

    cx = Iy / A
    cy = Ix / A

    Ixx_c = Ixx - A * cy * cy
    Iyy_c = Iyy - A * cx * cx
    Ixy_c = Ixy - A * cx * cy

    inertia_c = np.array([[Ixx_c, Ixy_c], [Ixy_c, Iyy_c]], dtype=float)
    _, eigvecs = np.linalg.eigh(inertia_c)

    v1 = eigvecs[:, 0]
    v2 = eigvecs[:, 1]

    return {
        "A": float(A),
        "cx": float(cx),
        "cy": float(cy),
        "v1": (float(v1[0]), float(v1[1])),
        "v2": (float(v2[0]), float(v2[1])),
    }
