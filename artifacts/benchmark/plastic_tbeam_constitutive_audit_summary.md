# T-beam Constitutive Audit

This audit checks whether benchmark strain references are close to any solved bar strain (total / incremental / legacy-converted).

## Row-level best gaps

| load_case | V_deg | strain_mild_ref_permille | strain_prestressed_ref_permille | best_mild_gap_total | best_mild_gap_legacy | best_prestress_gap_total | best_prestress_gap_legacy | best_prestress_gap_incremental | best_prestress_gap_incremental_legacy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.0 | 2.0 | 5.024 | 8.553 | 2.3661229925602534 | 1.7998268934295583 | 4.689096231827667 | 12.387121121541918 | 8.689096231827667 | 8.387121121541918 |
| 3.0 | 5.0 | 7.82 | 10.612 | 5.4035842592578405 | 4.596584393476147 | 6.663929938615578 | 14.48886601191095 | 10.663929938615578 | 10.48886601191095 |
| 3.0 | 8.0 | 10.324 | 12.465 | 8.114920401546344 | 7.102009707032931 | 8.430191853246749 | 16.39018516062465 | 12.430191853246749 | 12.390185160624652 |
| 4.0 | 5.0 | 2.929 | 6.998 | 1.075729505815463 | 0.05035045079220524 | 3.378129367113263 | 10.553444035126219 | 7.378129367113263 | 6.553444035126219 |
| 4.0 | 10.0 | 9.144 | 11.161 | 7.588655429067333 | 5.896741001839112 | 7.408375421234245 | 14.792392823347047 | 11.408375421234245 | 10.792392823347047 |
| 4.0 | 15.0 | 16.551 | 16.003 | 15.25654307705144 | 13.306384250964424 | 12.12536854214925 | 19.70793052197343 | 16.12536854214925 | 15.707930521973433 |

## Narrow constitutive variant study

| variant | max_rel_err_strain_mild | max_rel_err_strain_prestressed | max_rel_err_Mx | max_rel_err_My | max_rel_err_kappa | max_rel_err_compress_force | delta_vs_baseline_max_rel_err_strain_mild | delta_vs_baseline_max_rel_err_strain_prestressed | delta_vs_baseline_max_rel_err_Mx | delta_vs_baseline_max_rel_err_My | delta_vs_baseline_max_rel_err_kappa | delta_vs_baseline_max_rel_err_compress_force |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.8039625551908903 | 0.993998007270329 | 0.00011251455858352603 | 5.4136473249119476e-05 | 0.40347618778380756 | 0.5812405562479507 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| mild_perfect_plastic | 0.8039625551908903 | 0.993998007270329 | 0.00011251455858352603 | 5.4136473249119476e-05 | 0.40347618778380756 | 0.5812405562479507 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| mild_perfect_plastic_plus_prestress_soft | 0.8039625551908903 | 0.993998007270329 | 0.00011251455858352603 | 5.4136473249119476e-05 | 0.40347618778380756 | 0.5812405562479507 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prestress_soft_post_yield | 0.8039625551908903 | 0.993998007270329 | 0.00011251455858352603 | 5.4136473249119476e-05 | 0.40347618778380756 | 0.5812405562479507 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
