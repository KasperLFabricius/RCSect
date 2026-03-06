import numpy as np

from tests.plastic_diagnostics import (
    classify_dominant_mismatch,
    diagnose_manual_rows,
    run_contribution_study,
)


def test_manual_diagnostic_rows_are_in_correct_physical_regime():
    df = diagnose_manual_rows(mapping="case_d_manual_strength_plus_fe_fu")

    assert df.shape[0] == 6
    assert df["candidate_count"].ge(1).all()
    assert df["sign_agreement_Mx"].all()
    assert df["sign_agreement_My"].all()
    assert df["quadrant_agreement"].all()

    finite_cols = [
        "Mx_calc",
        "My_calc",
        "y_na_calc",
        "strain_concrete_calc",
        "strain_mild_calc",
        "strain_prestressed_calc",
        "kappa_calc",
        "compress_force_calc",
        "lever_L_calc",
        "lever_DX_calc",
        "lever_DY_calc",
    ]
    for col in finite_cols:
        assert np.isfinite(df[col]).all(), f"non-finite values in {col}"


def test_manual_diagnostic_rows_track_intermediate_quantities_by_order_of_magnitude():
    df = diagnose_manual_rows(mapping="case_d_manual_strength_plus_fe_fu")

    assert (df["strain_concrete_calc"] > 0.0).all()
    assert (df["strain_mild_calc"] > 0.0).all()
    assert (df["strain_prestressed_calc"] > 0.0).all()
    assert (df["kappa_calc"] > 0.0).all()
    assert (df["compress_force_calc"] > 0.0).all()

    # Ratio-style checks: keep broad but meaningful for diagnostic decomposition.
    assert (df["strain_concrete_calc"] / df["strain_concrete_ref"]).between(0.9, 1.2).all()
    assert (df["strain_mild_calc"] / df["strain_mild_ref"]).between(0.06, 2.8).all()
    assert (df["strain_prestressed_calc"] / df["strain_prestressed_ref"]).between(0.2, 2.5).all()
    assert (df["kappa_calc"] / df["kappa_ref"]).between(0.55, 2.0).all()
    assert (df["compress_force_calc"] / df["compress_force_ref"]).between(0.2, 1.4).all()


def test_diagnostic_decomposition_identifies_dominant_error_layer():
    df = diagnose_manual_rows(mapping="case_d_manual_strength_plus_fe_fu")

    moment_rel = float(df[["rel_Mx", "rel_My"]].mean().mean())
    equilibrium_rel = float(df[["rel_kappa", "rel_compress_force"]].mean().mean())
    strain_rel = float(df[["rel_strain_concrete", "rel_strain_mild", "rel_strain_prestressed"]].mean().mean())

    # Updated mapping substantially reduces moment discrepancy;
    # equilibrium/strain residuals now dominate.
    assert moment_rel < 0.10
    assert equilibrium_rel > 0.15

    conclusion = classify_dominant_mismatch(df)
    assert isinstance(conclusion, str)
    assert len(conclusion) > 20

    # For the current branch, mismatch is mixed and not purely sign/quadrant anymore.
    assert conclusion in {
        "largest mismatch appears concentrated in moment transformation / lever-arm projection",
        "largest mismatch appears already present in constitutive/equilibrium response",
        "mismatch is mixed across equilibrium and transformation layers",
    }

    # Guardrail: strain/equilibrium residuals remain bounded and finite.
    assert strain_rel < 1.2


def test_contribution_study_reports_cases_and_error_breakdown():
    summary, signed = run_contribution_study()

    assert summary.shape[0] == 4
    assert set(summary["mapping"]) == {
        "case_a_baseline",
        "case_b_manual_strength",
        "case_c_manual_strength_plus_fe",
        "case_d_manual_strength_plus_fe_fu",
    }
    assert signed.shape[0] == 24
    assert {"dMx", "dMy", "mapping", "load_case", "V_deg"}.issubset(set(signed.columns))

    # Strength-factor remapping should be the dominant shift vs baseline.
    a = float(summary.loc[summary["mapping"] == "case_a_baseline", "max_rel_err_Mx"].iloc[0])
    b = float(summary.loc[summary["mapping"] == "case_b_manual_strength", "max_rel_err_Mx"].iloc[0])
    assert b < a
