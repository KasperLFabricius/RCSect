"""Generate reproducible plastic benchmark artifacts, including row diagnostics."""

from __future__ import annotations

from pathlib import Path

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
    classify_dominant_mismatch,
    diagnose_manual_rows,
    diagnostics_markdown,
    run_contribution_study,
    run_type6_prestress_mapping_study,
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
    summary = summarize_benchmark(detail)
    row_diag = diagnose_manual_rows(mapping=DEFAULT_BENCHMARK_MAPPING)
    contribution_summary, contribution_signed = run_contribution_study()
    type6_study = run_type6_prestress_mapping_study()
    grouped_readiness = _output_group_summary(detail)
    conclusion = classify_dominant_mismatch(row_diag)

    detail_csv = out_dir / "plastic_benchmark_detail.csv"
    summary_md = out_dir / "plastic_benchmark_summary.md"
    row_diag_csv = out_dir / "plastic_row_diagnostics.csv"
    row_diag_md = out_dir / "plastic_row_diagnostics.md"
    contribution_csv = out_dir / "plastic_benchmark_contribution_summary.csv"
    contribution_signed_csv = out_dir / "plastic_benchmark_contribution_signed_errors.csv"
    type6_study_csv = out_dir / "plastic_type6_mapping_study.csv"
    grouped_readiness_csv = out_dir / "plastic_sub1_readiness.csv"

    detail.to_csv(detail_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    row_diag.to_csv(row_diag_csv, index=False)
    contribution_summary.to_csv(contribution_csv, index=False)
    contribution_signed.to_csv(contribution_signed_csv, index=False)
    type6_study.to_csv(type6_study_csv, index=False)
    grouped_readiness.to_csv(grouped_readiness_csv, index=False)

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
    md += "\n\n## Sub-1% readiness by fixture family and output group\n\n"
    md += _markdown_table(grouped_readiness)
    md += "\n\nConclusion: " + conclusion + "\n"

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

    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {row_diag_csv}")
    print(f"Wrote {row_diag_md}")
    print(f"Wrote {contribution_csv}")
    print(f"Wrote {contribution_signed_csv}")
    print(f"Wrote {type6_study_csv}")
    print(f"Wrote {grouped_readiness_csv}")


if __name__ == "__main__":
    main()
