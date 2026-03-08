"""Generate reproducible plastic benchmark artifacts, including row diagnostics."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from tests.benchmark_compare import BenchmarkSweepSpec, run_benchmark_sweeps, summarize_benchmark
from tests.pcross_benchmark_fixture import (
    BENCHMARK_MAPPINGS,
    DEFAULT_BENCHMARK_MAPPING,
    EMBEDDED_BENCHMARK_CASES,
    LOAD_CASE_3,
    LOAD_CASE_4,
    build_pcross_tbeam_solver,
)
from tests.plastic_diagnostics import (
    choose_semantic_winners,
    choose_semantic_winners_by_family,
    classify_dominant_mismatch,
    diagnose_manual_rows,
    diagnostics_markdown,
    run_contribution_study,
    run_output_semantics_study,
    run_output_definition_study,
    run_zone_partition_study,
    run_type6_prestress_mapping_study,
    run_strain_definition_study,
    run_dxdy_sign_transformation_study,
)


def _markdown_table(df):
    if df.empty:
        return "_No rows_"
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for h in headers:
            v = row[h]
            vals.append("" if v is None else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def _prior_summary_if_available(summary_csv: Path):
    """Load prior committed summary (HEAD) when available, else working-tree file."""
    try:
        import io
        import subprocess
        import pandas as pd

        rel = summary_csv.as_posix()
        proc = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return pd.read_csv(io.StringIO(proc.stdout))
    except Exception:
        pass

    if not summary_csv.exists():
        return None
    try:
        import pandas as pd

        return pd.read_csv(summary_csv)
    except Exception:
        return None


def _max_rel_errors(df):
    if df is None or df.empty:
        return (None, None)
    return (float(df["max_rel_err_Mx"].max()), float(df["max_rel_err_My"].max()))



def _max_rel(df, cols):
    vals = []
    for c in cols:
        if c in df.columns:
            v = df[c].dropna()
            if not v.empty:
                vals.append(float(v.max()))
    return max(vals) if vals else None


def _band(v):
    if v is None:
        return "N/A"
    if v < 0.01:
        return "<1%"
    if v <= 0.05:
        return "1-5%"
    return ">5%"


def _output_group_summary(detail):
    family_map = {
        3: "tbeam", 4: "tbeam",
        101: "snit", 102: "snit", 103: "snit", 104: "snit",
        201: "annular", 202: "annular",
    }
    detail = detail.copy()
    detail["fixture_family"] = detail["load_case"].map(lambda lc: family_map.get(int(lc), f"lc_{int(lc)}"))

    groups = {
        "moments": ["rel_err_Mx", "rel_err_My"],
        "strains": ["rel_err_strain_concrete", "rel_err_strain_mild", "rel_err_strain_prestressed"],
        "curvature": ["rel_err_kappa"],
        "compression force": ["rel_err_compress_force"],
        "lever-arms": ["rel_err_L", "rel_err_DX", "rel_err_DY"],
    }

    rows = []
    for family, fam_df in detail[detail["Mx_ref"].notna()].groupby("fixture_family"):
        for gname, cols in groups.items():
            m = _max_rel(fam_df, cols)
            rows.append({
                "fixture_family": family,
                "output_group": gname,
                "max_rel_err": m,
                "band": _band(m),
            })

        warn = fam_df["warning_ref"].notna()
        rows.append({
            "fixture_family": family,
            "output_group": "warnings",
            "max_rel_err": None,
            "band": f"match={float(fam_df.loc[warn, 'warning_est_match'].mean()):.3f}" if warn.any() else "N/A",
        })

    import pandas as pd
    return pd.DataFrame(rows).sort_values(["fixture_family", "output_group"]).reset_index(drop=True)



def _semantic_gap_table(before_detail, after_detail):
    import pandas as pd

    rows = []
    groups = {
        "moments": ["rel_err_Mx", "rel_err_My"],
        "strains": ["rel_err_strain_concrete", "rel_err_strain_mild", "rel_err_strain_prestressed"],
        "compression force": ["rel_err_compress_force"],
        "lever-arms": ["rel_err_L", "rel_err_DX", "rel_err_DY"],
    }
    for name, cols in groups.items():
        b = _max_rel(before_detail[before_detail["Mx_ref"].notna()], cols)
        a = _max_rel(after_detail[after_detail["Mx_ref"].notna()], cols)
        rows.append({
            "group": name,
            "max_rel_before": b,
            "max_rel_after": a,
            "delta": (a - b) if b is not None and a is not None else None,
        })
    return pd.DataFrame(rows)




def _prior_csv_if_available(path: Path):
    try:
        import io
        import subprocess
        import pandas as pd

        rel = path.as_posix()
        proc = subprocess.run(["git", "show", f"HEAD:{rel}"], check=False, capture_output=True, text=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return pd.read_csv(io.StringIO(proc.stdout))
    except Exception:
        return None
    return None


def _legacy_shift_rows(before_detail, after_detail):
    rows = []
    groups = {
        "moments": ["rel_err_Mx", "rel_err_My"],
        "strains": ["rel_err_strain_concrete", "rel_err_strain_mild", "rel_err_strain_prestressed"],
        "kappa": ["rel_err_kappa"],
        "compress_force": ["rel_err_compress_force"],
        "lever_arms": ["rel_err_L", "rel_err_DX", "rel_err_DY"],
    }
    for name, cols in groups.items():
        b = _max_rel(before_detail[before_detail["Mx_ref"].notna()], cols) if before_detail is not None else None
        a = _max_rel(after_detail[after_detail["Mx_ref"].notna()], cols)
        rows.append({"family": "all", "output_group": name, "max_rel_before": b, "max_rel_after": a})

    def family_col(df):
        mp = {3:"tbeam",4:"tbeam",101:"snit",102:"snit",103:"snit",104:"snit",201:"annular",202:"annular"}
        d = df.copy()
        d["family"] = d["load_case"].map(lambda lc: mp.get(int(lc), f"lc_{int(lc)}"))
        return d

    ad = family_col(after_detail[after_detail["Mx_ref"].notna()])
    bd = family_col(before_detail[before_detail["Mx_ref"].notna()]) if before_detail is not None else None
    for fam, grp in ad.groupby("family"):
        for name, cols in groups.items():
            b = _max_rel(bd[bd["family"]==fam], cols) if bd is not None else None
            a = _max_rel(grp, cols)
            rows.append({"family": fam, "output_group": name, "max_rel_before": b, "max_rel_after": a})
        warn_after = float(grp["warning_est_match"].mean()) if "warning_est_match" in grp.columns else None
        warn_before = None
        if bd is not None and "warning_est_match" in bd.columns:
            warn_before = float(bd[bd["family"]==fam]["warning_est_match"].mean())
        rows.append({"family": fam, "output_group": "warnings", "max_rel_before": warn_before, "max_rel_after": warn_after})
    import pandas as pd
    return pd.DataFrame(rows)

def _ambiguous_output_conclusion(
    semantics_summary,
    cross_family_winners: dict[str, str],
    family_winners,
    baseline_detail,
    aligned_detail,
):
    import pandas as pd

    rows = []
    for output, col in [("strain_prestressed", "rel_err_strain_prestressed"), ("lever_DY", "rel_err_DY")]:
        cross = cross_family_winners.get(output)
        fam_rows = family_winners[family_winners["output"] == output] if not family_winners.empty else pd.DataFrame()
        unique_fam = sorted(fam_rows["candidate"].unique().tolist()) if not fam_rows.empty else []
        baseline_max = float(baseline_detail[col].dropna().max()) if col in baseline_detail.columns and baseline_detail[col].notna().any() else None
        aligned_max = float(aligned_detail[col].dropna().max()) if col in aligned_detail.columns and aligned_detail[col].notna().any() else None

        if cross:
            status = "cross-family winner exists"
        elif len(unique_fam) >= 2:
            status = "family-specific winners only"
        elif len(unique_fam) == 1:
            status = "single-family signal only"
        else:
            status = "no candidate materially improves fit"

        rows.append(
            {
                "output": output,
                "cross_family_winner": cross,
                "family_winners": ", ".join(unique_fam) if unique_fam else None,
                "status": status,
                "max_rel_error_reported": baseline_max,
                "max_rel_error_semantic_aligned": aligned_max,
            }
        )
    return pd.DataFrame(rows)

def main() -> None:
    out_dir = Path("artifacts") / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)

    active_mapping = BENCHMARK_MAPPINGS[DEFAULT_BENCHMARK_MAPPING]
    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    specs = [
        BenchmarkSweepSpec(load_case=3, p_target=LOAD_CASE_3.P_target, angles_deg=LOAD_CASE_3.angles_deg),
        BenchmarkSweepSpec(load_case=4, p_target=LOAD_CASE_4.P_target, angles_deg=LOAD_CASE_4.angles_deg),
    ]
    summary_csv = out_dir / "plastic_benchmark_summary.csv"
    prior_summary = _prior_summary_if_available(summary_csv)

    detail_frames = [run_benchmark_sweeps(solver, specs)]
    for key in ["snit_a", "snit_b", "snit_c", "snit_d", "section0", "sectioniv"]:
        case = EMBEDDED_BENCHMARK_CASES[key]
        detail_frames.append(
            run_benchmark_sweeps(
                case.solver_builder(),
                [BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)],
                reference_rows=case.reference_rows,
            )
        )

    import pandas as pd
    detail = pd.concat(detail_frames, ignore_index=True)

    aligned_frames = [run_benchmark_sweeps(solver, specs, semantic_profile="semantic_aligned")]
    for key in ["snit_a", "snit_b", "snit_c", "snit_d", "section0", "sectioniv"]:
        case = EMBEDDED_BENCHMARK_CASES[key]
        aligned_frames.append(
            run_benchmark_sweeps(
                case.solver_builder(),
                [BenchmarkSweepSpec(load_case=case.load_case, p_target=case.load.P_target, angles_deg=case.load.angles_deg)],
                reference_rows=case.reference_rows,
                semantic_profile="semantic_aligned",
            )
        )
    detail_aligned = pd.concat(aligned_frames, ignore_index=True)

    summary = summarize_benchmark(detail)
    row_diag = diagnose_manual_rows(mapping=DEFAULT_BENCHMARK_MAPPING)
    contribution_summary, contribution_signed = run_contribution_study()
    type6_study = run_type6_prestress_mapping_study()
    semantics_detail, semantics_summary = run_output_semantics_study()
    definition_detail, definition_summary, definition_winners = run_output_definition_study()
    strain_detail, strain_summary, strain_winners = run_strain_definition_study()
    dxdy_detail, dxdy_summary, dxdy_winners, annular_pairs = run_dxdy_sign_transformation_study()
    zone_partition = run_zone_partition_study()
    semantic_winners = choose_semantic_winners(semantics_summary)
    family_winners = choose_semantic_winners_by_family(semantics_summary)
    grouped_readiness = _output_group_summary(detail_aligned)
    semantic_gap = _semantic_gap_table(detail, detail_aligned)
    ambiguous_conclusion = _ambiguous_output_conclusion(semantics_summary, semantic_winners, family_winners, detail, detail_aligned)
    conclusion = classify_dominant_mismatch(row_diag)

    detail_csv = out_dir / "plastic_benchmark_detail.csv"
    summary_md = out_dir / "plastic_benchmark_summary.md"
    row_diag_csv = out_dir / "plastic_row_diagnostics.csv"
    row_diag_md = out_dir / "plastic_row_diagnostics.md"
    contribution_csv = out_dir / "plastic_benchmark_contribution_summary.csv"
    contribution_signed_csv = out_dir / "plastic_benchmark_contribution_signed_errors.csv"
    type6_study_csv = out_dir / "plastic_type6_mapping_study.csv"
    grouped_readiness_csv = out_dir / "plastic_sub1_readiness.csv"
    semantics_detail_csv = out_dir / "plastic_output_semantics_study.csv"
    semantics_family_csv = out_dir / "plastic_output_semantics_family_study.csv"
    semantics_summary_md = out_dir / "plastic_output_semantics_summary.md"
    semantics_family_md = out_dir / "plastic_output_semantics_family_summary.md"
    definition_detail_csv = out_dir / "plastic_output_definition_study.csv"
    definition_summary_md = out_dir / "plastic_output_definition_summary.md"
    zone_partition_csv = out_dir / "plastic_zone_partition_study.csv"
    zone_partition_md = out_dir / "plastic_zone_partition_summary.md"
    strain_detail_csv = out_dir / "plastic_strain_definition_study.csv"
    strain_summary_md = out_dir / "plastic_strain_definition_summary.md"
    dxdy_detail_csv = out_dir / "plastic_dxdy_sign_transformation_study.csv"
    dxdy_summary_md = out_dir / "plastic_dxdy_sign_transformation_summary.md"
    annular_pair_csv = out_dir / "plastic_annular_dxdy_pair_checks.csv"

    legacy_shift_csv = out_dir / "plastic_legacy_shift.csv"
    legacy_shift_md = out_dir / "plastic_legacy_shift_summary.md"

    prior_detail = _prior_csv_if_available(detail_csv)
    legacy_shift = _legacy_shift_rows(prior_detail, detail)
    legacy_shift.to_csv(legacy_shift_csv, index=False)

    bands = legacy_shift[legacy_shift["family"] == "all"].copy()
    def _bucket(v):
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            return "N/A"
        if v < 0.01:
            return "<1%"
        if v <= 0.05:
            return "1%-5%"
        return ">5%"
    bands["band_after"] = bands["max_rel_after"].map(_bucket)

    md_shift = "# Plastic Legacy Shift Summary\n\n"
    md_shift += "Phase-1 shift to direct legacy PCROSS families in benchmark fixture path.\n\n"
    md_shift += "## Global max relative error by output group\n\n" + _markdown_table(bands[["output_group","max_rel_before","max_rel_after","band_after"]]) + "\n\n"
    md_shift += "## Family summaries\n\n" + _markdown_table(legacy_shift[legacy_shift["family"] != "all"]) + "\n"
    legacy_shift_md.write_text(md_shift)

    detail.to_csv(detail_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    row_diag.to_csv(row_diag_csv, index=False)
    contribution_summary.to_csv(contribution_csv, index=False)
    contribution_signed.to_csv(contribution_signed_csv, index=False)
    type6_study.to_csv(type6_study_csv, index=False)
    grouped_readiness.to_csv(grouped_readiness_csv, index=False)
    semantics_detail.to_csv(semantics_detail_csv, index=False)
    family_winners.to_csv(semantics_family_csv, index=False)
    definition_detail.to_csv(definition_detail_csv, index=False)
    zone_partition.to_csv(zone_partition_csv, index=False)
    strain_detail.to_csv(strain_detail_csv, index=False)
    dxdy_detail.to_csv(dxdy_detail_csv, index=False)
    annular_pairs.to_csv(annular_pair_csv, index=False)

    referenced = detail[detail["Mx_ref"].notna()][
        [
            "load_case",
            "V_deg",
            "Mx_ref",
            "Mx_calc",
            "My_ref",
            "My_calc",
            "sign_agreement_Mx",
            "sign_agreement_My",
            "quadrant_expected",
            "quadrant_calc",
            "quadrant_agreement",
            "abs_err_Mx",
            "abs_err_My",
            "rel_err_Mx",
            "rel_err_My",
            "candidate_count",
            "pivot",
            "selected_branch",
        ]
    ]

    md = "# Plastic Solver Benchmark Summary\n\n"
    md += "## Active benchmark mapping\n\n"
    md += (
        f"- mapping: `{active_mapping.name}`\n"
        f"- gamma_c: {active_mapping.gamma_c}\n"
        f"- gamma_s: {active_mapping.gamma_s}\n"
        f"- gamma_p: {active_mapping.gamma_p}\n"
        f"- gamma_E: {active_mapping.gamma_E}\n"
        f"- gamma_u: {active_mapping.gamma_u}\n\n"
    )
    md += _markdown_table(summary)
    md += "\n\n## Referenced rows\n\n"
    md += "Signed errors (abs/rel) are primary benchmark metrics. "
    md += "Magnitude-only errors remain in CSV as secondary diagnostics.\n\n"
    md += _markdown_table(referenced)
    md += "\n\n## Contribution study (cases A-D)\n\n"
    md += _markdown_table(contribution_summary)
    md += "\n\n## Type-6 prestress mapping study (Snit A-D, benchmark-only)\n\n"
    md += _markdown_table(type6_study)
    md += "\n\n## Output-semantics candidates and winners\n\n"
    md += "Chosen winners (majority across fixture families):\n\n"
    for k, v in semantic_winners.items():
        md += f"- {k}: `{v}`\n"
    md += "\n\n## Semantic gap (before vs semantic-aligned benchmark comparison)\n\n"
    md += _markdown_table(semantic_gap)
    md += "\n\n## Semantic-versus-constitutive conclusion for unresolved outputs\n\n"
    md += _markdown_table(ambiguous_conclusion)
    md += "\n\n## Sub-1% readiness by fixture family and output group (after semantic alignment)\n\n"
    md += _markdown_table(grouped_readiness)
    md += "\n\nConclusion: " + conclusion + "\n"

    strain_summary = strain_winners[["output", "fixture_family", "best_candidate", "cross_family_winner", "cross_family_winner_exists", "max_rel_error", "median_rel_error"]]
    md_strain = "# Plastic Strain Definition Study\n\n"
    md_strain += "COMPRESS FORCE is no longer the main blocker on this branch; this study isolates remaining strain output semantics.\n\n"
    md_strain += "## Best candidate per family\n\n" + _markdown_table(strain_summary) + "\n\n"
    md_strain += "## Candidate score summary\n\n" + _markdown_table(strain_summary if strain_summary.empty else strain_summary) + "\n"
    strain_summary_md.write_text(md_strain)

    dxdy_family = dxdy_winners[["output", "fixture_family", "best_candidate", "cross_family_winner", "cross_family_winner_exists", "max_rel_error", "median_rel_error"]]
    md_dxdy = "# Plastic DX/DY Sign and Transformation Study\n\n"
    md_dxdy += "COMPRESS FORCE is no longer the main blocker on this branch; this study isolates lever-arm sign/transformation semantics (DX, DY, L).\n\n"
    md_dxdy += "## Best candidate per family\n\n" + _markdown_table(dxdy_family) + "\n\n"
    md_dxdy += "## Annular opposite-angle sign checks (0↔180, 90↔270, 45↔225)\n\n" + _markdown_table(annular_pairs) + "\n"
    dxdy_summary_md.write_text(md_dxdy)

    prior_mx, prior_my = _max_rel_errors(prior_summary)
    cur_mx, cur_my = _max_rel_errors(summary)
    md += "\n## Error delta vs prior artifact\n\n"
    if prior_mx is None or prior_my is None:
        md += "No prior summary artifact was readable; deltas unavailable.\n"
    else:
        md += f"- prior max_rel_err_Mx: {prior_mx:.6f}\n"
        md += f"- current max_rel_err_Mx: {cur_mx:.6f}\n"
        md += f"- delta max_rel_err_Mx: {cur_mx - prior_mx:+.6f}\n"
        md += f"- prior max_rel_err_My: {prior_my:.6f}\n"
        md += f"- current max_rel_err_My: {cur_my:.6f}\n"
        md += f"- delta max_rel_err_My: {cur_my - prior_my:+.6f}\n"

    summary_md.write_text(md, encoding="utf-8")
    row_diag_md.write_text(diagnostics_markdown(row_diag), encoding="utf-8")

    sem_md = "# Plastic output semantics study\n\n"
    sem_md += "## Candidate metrics by fixture family\n\n"
    sem_md += _markdown_table(semantics_summary)
    sem_md += "\n\n## Chosen winners\n\n"
    if semantic_winners:
        for k, v in semantic_winners.items():
            sem_md += f"- {k}: `{v}`\n"
    else:
        sem_md += "No consistent winner across families.\n"
    sem_md += "\n\n## Family-specific winners for unresolved outputs\n\n"
    sem_md += _markdown_table(family_winners)
    sem_md += "\n\n## Semantic-versus-constitutive conclusion\n\n"
    sem_md += _markdown_table(ambiguous_conclusion)
    semantics_summary_md.write_text(sem_md, encoding="utf-8")
    semantics_family_md.write_text(_markdown_table(ambiguous_conclusion), encoding="utf-8")


    def_md = "# Plastic output-definition candidate study\n\n"
    def_md += "Family-specific candidate scoring for unresolved outputs.\n\n"
    def_md += "## Candidate metrics by family/output\n\n"
    def_md += _markdown_table(definition_summary)
    def_md += "\n\n## Best candidate by family and cross-family winner status\n\n"
    def_md += _markdown_table(definition_winners)
    if not definition_winners.empty:
        unresolved = definition_winners[definition_winners["cross_family_winner_exists"] == False]["output"].drop_duplicates().tolist()
        if unresolved:
            def_md += "\n\nNo cross-family winner: " + ", ".join(unresolved) + "\n"
    definition_summary_md.write_text(def_md, encoding="utf-8")


    zone_md = "# Plastic zone-partition study\n\n"
    zone_md += "Compare force-sign versus zone-based reconstruction for compression force and lever components.\n\n"
    if not zone_partition.empty:
        fam = (
            zone_partition.groupby("fixture_family")
            .agg(
                compress_zone_max_rel=("compress_force_zone_rel_error", "max"),
                compress_sign_max_rel=("compress_force_force_sign_rel_error", "max"),
                DX_zone_max_rel=("DX_zone_rel_error", "max"),
                DX_sign_max_rel=("DX_force_sign_rel_error", "max"),
                DY_zone_max_rel=("DY_zone_rel_error", "max"),
                DY_sign_max_rel=("DY_force_sign_rel_error", "max"),
            )
            .reset_index()
        )
        zone_md += "## Family summary\n\n" + _markdown_table(fam) + "\n\n"
        zone_md += "## Row detail\n\n" + _markdown_table(zone_partition) + "\n"
    else:
        zone_md += "No zone-partition rows available.\n"
    zone_partition_md.write_text(zone_md, encoding="utf-8")

    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {row_diag_csv}")
    print(f"Wrote {row_diag_md}")
    print(f"Wrote {contribution_csv}")
    print(f"Wrote {contribution_signed_csv}")
    print(f"Wrote {type6_study_csv}")
    print(f"Wrote {grouped_readiness_csv}")
    print(f"Wrote {semantics_detail_csv}")
    print(f"Wrote {semantics_family_csv}")
    print(f"Wrote {semantics_summary_md}")
    print(f"Wrote {semantics_family_md}")
    print(f"Wrote {definition_detail_csv}")
    print(f"Wrote {definition_summary_md}")
    print(f"Wrote {zone_partition_csv}")
    print(f"Wrote {zone_partition_md}")


if __name__ == "__main__":
    main()
