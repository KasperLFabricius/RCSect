import numpy as np

from tests.plastic_diagnostics import (
    classify_dominant_mismatch,
    diagnose_manual_rows,
    run_contribution_study,
    run_output_semantics_study,
    run_type6_prestress_mapping_study,
    choose_semantic_winners,
    choose_semantic_winners_by_family,
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
    # Legacy-reported strains are signed governing-absolute values.
    assert (df["strain_mild_calc"].abs() > 0.0).all()
    assert (df["strain_prestressed_calc"].abs() > 0.0).all()
    assert (df["kappa_calc"] > 0.0).all()
    assert (df["compress_force_calc"] > 0.0).all()

    # Ratio-style checks: keep broad but meaningful for diagnostic decomposition.
    assert (df["strain_concrete_calc"] / df["strain_concrete_ref"]).between(0.9, 1.2).all()
    assert ((df["strain_mild_calc"].abs()) / df["strain_mild_ref"]).between(0.06, 2.8).all()
    assert ((df["strain_prestressed_calc"].abs()) / df["strain_prestressed_ref"]).between(0.005, 2.5).all()
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

    row_a = summary.loc[summary["mapping"] == "case_a_baseline"].iloc[0]
    row_b = summary.loc[summary["mapping"] == "case_b_manual_strength"].iloc[0]
    row_c = summary.loc[summary["mapping"] == "case_c_manual_strength_plus_fe"].iloc[0]
    row_d = summary.loc[summary["mapping"] == "case_d_manual_strength_plus_fe_fu"].iloc[0]

    # Strength-factor remapping should improve both Mx and My vs baseline.
    assert float(row_b["max_rel_err_Mx"]) < float(row_a["max_rel_err_Mx"])
    assert float(row_b["max_rel_err_My"]) < float(row_a["max_rel_err_My"])

    # FE remapping should improve or at least not materially worsen vs case B.
    assert float(row_c["max_rel_err_Mx"]) <= float(row_b["max_rel_err_Mx"]) + 1e-3
    assert float(row_c["max_rel_err_My"]) <= float(row_b["max_rel_err_My"]) + 1e-3

    # With figure-consistent diagrams FU can change top-row fit; guard against regressions.
    assert float(row_d["max_rel_err_Mx"]) <= float(row_c["max_rel_err_Mx"]) + 1e-3
    assert float(row_d["max_rel_err_My"]) <= float(row_c["max_rel_err_My"]) + 1e-3


from tests.benchmark_compare import BenchmarkSweepSpec, run_benchmark_sweeps
from tests.pcross_benchmark_fixture import EMBEDDED_BENCHMARK_CASES


def test_extended_annular_diagnostics_intermediate_columns_present():
    for key in ["section0", "sectioniv"]:
        case = EMBEDDED_BENCHMARK_CASES[key]
        df = run_benchmark_sweeps(
            case.solver_builder(),
            [BenchmarkSweepSpec(case.load_case, case.load.P_target, case.load.angles_deg)],
            reference_rows=case.reference_rows,
        )
        refs = df[df["Mx_ref"].notna()]
        for col in [
            "strain_concrete_calc",
            "strain_mild_calc",
            "kappa_calc",
            "compress_force_calc",
            "L_calc",
            "DX_calc",
            "DY_calc",
            "warning_ref",
        ]:
            assert col in refs.columns
            assert refs[col].notna().any()


def test_type6_mapping_study_reports_before_after_metrics_for_snit_ad():
    study = run_type6_prestress_mapping_study()

    assert set(study["mapping"]) == {"baseline", "refined"}
    assert set(study["family"]) == {"snit_a", "snit_b", "snit_c", "snit_d"}
    for col in [
        "max_rel_err_Mx",
        "max_rel_err_My",
        "max_rel_err_strain_prestressed",
        "max_rel_err_compress_force",
        "max_rel_err_kappa",
    ]:
        assert study[col].notna().all()

    # Refined mapping is benchmark-only and should remain narrow: no dramatic regressions.
    refined = study[study["mapping"] == "refined"]
    assert (refined["delta_refined_minus_baseline_max_rel_err_Mx"] < 0.02).all()
    assert (refined["delta_refined_minus_baseline_max_rel_err_My"] < 0.02).all()


def test_output_semantics_study_produces_candidate_scores_and_partial_winners():
    detail, summary = run_output_semantics_study()

    assert not detail.empty
    assert not summary.empty
    assert {"fixture_family", "output", "candidate", "max_rel_error", "median_rel_error", "sign_agreement_rate"}.issubset(summary.columns)
    assert set(summary["fixture_family"]) == {"tbeam", "snit", "annular"}

    winners = choose_semantic_winners(summary)
    # We should only lock in semantics when at least two families agree.
    assert winners.get("compress_force") in {
        None,
        "compress_force:total_compression_abs",
        "compress_force:concrete_plus_all_comp_steel",
        "compress_force:concrete_plus_comp_rebar",
    }
    assert winners.get("lever_DY") in {None, "lever:moment_over_compression:DY_from_Mx"}
    assert "strain_prestressed" not in winners

    prest = summary[summary["output"] == "strain_prestressed"]["candidate"]
    assert "strain_prestressed:incremental_governing_abs_signed" in set(prest)
    assert "strain_prestressed:stress_equivalent_governing_abs_signed" in set(prest)

    dy = summary[summary["output"] == "lever_DY"]["candidate"]
    assert "lever:moment_over_compression:DY_from_Mx" in set(dy)
    assert "lever:total_comp_to_tension:DY_local" in set(dy)


def test_output_semantics_family_winner_study_for_ambiguous_outputs():
    _, summary = run_output_semantics_study()
    family = choose_semantic_winners_by_family(summary)

    assert not family.empty
    assert set(family["output"]) == {"strain_prestressed", "lever_DY"}
    assert set(family["fixture_family"]) == {"tbeam", "snit", "annular"}
    assert family["sign_agreement_rate"].between(0.0, 1.0).all()


def test_semantic_aligned_profile_is_available_in_benchmark_sweeps():
    case = EMBEDDED_BENCHMARK_CASES["section0"]
    base = run_benchmark_sweeps(
        case.solver_builder(),
        [BenchmarkSweepSpec(case.load_case, case.load.P_target, case.load.angles_deg)],
        reference_rows=case.reference_rows,
    )
    aligned = run_benchmark_sweeps(
        case.solver_builder(),
        [BenchmarkSweepSpec(case.load_case, case.load.P_target, case.load.angles_deg)],
        reference_rows=case.reference_rows,
        semantic_profile="semantic_aligned",
    )

    assert (base["semantic_profile"] == "reported").all()
    assert (aligned["semantic_profile"] == "semantic_aligned").all()
    assert aligned["rel_err_compress_force"].notna().all()
    assert aligned["rel_err_L"].notna().all()
    assert aligned["rel_err_DY"].notna().any()
