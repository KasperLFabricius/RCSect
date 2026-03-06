import pytest

from core.geometry import CrossSection


def test_get_rotated_system_preserves_prestress_metadata_eps0():
    section = CrossSection(
        concrete_outline=[
            {"id": 1, "x": -0.2, "y": -0.2},
            {"id": 2, "x": 0.2, "y": -0.2},
            {"id": 3, "x": 0.2, "y": 0.2},
            {"id": 4, "x": -0.2, "y": 0.2},
        ],
        concrete_voids=[],
        rebar_mild=[],
        rebar_prestressed=[
            {"id": "P1", "x": 0.05, "y": -0.08, "area": 180.0, "eps0": 0.0032, "tag": "kept"}
        ],
    )

    _, _, rotated_pre = section.get_rotated_system(angle_v_deg=17.0)

    assert len(rotated_pre) == 1
    assert rotated_pre[0]["eps0"] == pytest.approx(0.0032)
    assert rotated_pre[0]["tag"] == "kept"
