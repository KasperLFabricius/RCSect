import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import app


def _sample_data():
    return {
        "analysis_settings": {"mode": "Plastic", "gamma_E": 1.0},
        "materials": {
            "concrete": {"f_ck": 30.0, "gamma_c": 1.45, "alpha_cc": 1.0, "E_c_GPa": 33.0},
            "mild_steel": {
                "f_yk": 500.0,
                "f_yk_t_MPa": 500.0,
                "f_yk_c_MPa": 500.0,
                "gamma_s": 1.15,
                "E_s_GPa": 200.0,
                "e_uk": 0.05,
                "include_hardening": False,
            },
            "prestressed_steel": {
                "f_p01k": 1500.0,
                "f_pk": 1700.0,
                "initial_strain": 0.0,
                "e_uk": 0.035,
                "gamma_p": 1.15,
                "E_p_GPa": 195.0,
            },
        },
        "geometry": {
            "concrete_outline": [
                {"id": 1, "x": -0.3, "y": -0.3},
                {"id": 2, "x": 0.3, "y": -0.3},
                {"id": 3, "x": 0.3, "y": 0.3},
                {"id": 4, "x": -0.3, "y": 0.3},
            ],
            "concrete_voids": [],
            "reinforcement_mild": [{"id": "S1", "x": 0.0, "y": 0.0, "area": 100.0}],
            "reinforcement_prestressed": [],
        },
        "load_cases": {
            "elastic": [],
            "plastic": [
                {"id": 1, "name": "LC", "P_target": 1000.0, "v_min": 0.0, "v_max": 10.0, "v_inc": 5.0}
            ],
        },
    }


def test_compute_results_uses_solve_angle_sweep_for_plastic_sequences(monkeypatch):
    calls = {"sweep": 0, "solve": 0, "angles": None}

    class FakePlasticSolver:
        def __init__(self, *args, **kwargs):
            pass

        def solve(self, *args, **kwargs):
            calls["solve"] += 1
            raise AssertionError("single-angle solve path should not be used for plastic sweep")

        def solve_angle_sweep(self, angle_values_deg, P_target):
            calls["sweep"] += 1
            calls["angles"] = list(angle_values_deg)
            return [{"Mx": -1.0, "My": 2.0, "N_calc": P_target} for _ in angle_values_deg]

    monkeypatch.setattr(app, "PlasticSolver", FakePlasticSolver)

    result = app._compute_results(_sample_data())

    assert calls["sweep"] == 1
    assert calls["solve"] == 0
    assert calls["angles"] == [0.0, 5.0, 10.0]

    plastic_rows = result["plastic"][0]["result"]
    assert [row["V"] for row in plastic_rows] == [0.0, 5.0, 10.0]
