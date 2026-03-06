"""Generate reproducible plastic benchmark artifacts, including row diagnostics."""

from __future__ import annotations

from pathlib import Path

from tests.benchmark_compare import BenchmarkSweepSpec, run_benchmark_sweeps, summarize_benchmark
from tests.pcross_benchmark_fixture import LOAD_CASE_3, LOAD_CASE_4, build_pcross_tbeam_solver
from tests.plastic_diagnostics import classify_dominant_mismatch, diagnose_manual_rows, diagnostics_markdown


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


def main() -> None:
    out_dir = Path("artifacts") / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)

    solver = build_pcross_tbeam_solver(prestress_eps0=0.004)
    specs = [
        BenchmarkSweepSpec(load_case=3, p_target=LOAD_CASE_3.P_target, angles_deg=LOAD_CASE_3.angles_deg),
        BenchmarkSweepSpec(load_case=4, p_target=LOAD_CASE_4.P_target, angles_deg=LOAD_CASE_4.angles_deg),
    ]
    detail = run_benchmark_sweeps(solver, specs)
    summary = summarize_benchmark(detail)
    row_diag = diagnose_manual_rows()
    conclusion = classify_dominant_mismatch(row_diag)

    detail_csv = out_dir / "plastic_benchmark_detail.csv"
    summary_csv = out_dir / "plastic_benchmark_summary.csv"
    summary_md = out_dir / "plastic_benchmark_summary.md"
    row_diag_csv = out_dir / "plastic_row_diagnostics.csv"
    row_diag_md = out_dir / "plastic_row_diagnostics.md"

    detail.to_csv(detail_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    row_diag.to_csv(row_diag_csv, index=False)

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
    md += _markdown_table(summary)
    md += "\n\n## Referenced rows\n\n"
    md += "Signed errors (abs/rel) are primary benchmark metrics. "
    md += "Magnitude-only errors remain in CSV as secondary diagnostics.\n\n"
    md += _markdown_table(referenced)
    md += "\n\nConclusion: " + conclusion + "\n"
    summary_md.write_text(md, encoding="utf-8")
    row_diag_md.write_text(diagnostics_markdown(row_diag), encoding="utf-8")

    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {row_diag_csv}")
    print(f"Wrote {row_diag_md}")


if __name__ == "__main__":
    main()
