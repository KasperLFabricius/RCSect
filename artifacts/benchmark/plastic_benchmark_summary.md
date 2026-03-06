# Plastic Solver Benchmark Summary

| load_case | angles_checked | angles_with_reference | max_abs_err_Mx | max_abs_err_My | max_rel_err_Mx | max_rel_err_My | all_quadrant_ok | all_sign_ok_Mx | all_sign_ok_My | max_candidate_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 16 | 3 | 253.18316185673166 | 249.1475884711275 | 0.4009680651340087 | 0.2719356169980264 | True | True | True | 2 |
| 4 | 15 | 3 | 284.4949828811772 | 248.50161583774002 | 0.5052710127545373 | 0.287739226470542 | True | True | True | 2 |

## Referenced rows

Signed errors (abs/rel) are primary benchmark metrics. Magnitude-only errors remain in CSV as secondary diagnostics.

| load_case | V_deg | Mx_ref | Mx_calc | My_ref | My_calc | sign_agreement_Mx | sign_agreement_My | quadrant_expected | quadrant_calc | quadrant_agreement | abs_err_Mx | abs_err_My | rel_err_Mx | rel_err_My | candidate_count | pivot | selected_branch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2.0 | 544.3 | 762.5469178524409 | 921.8 | 1170.710341876811 | True | True | I | I | True | 218.2469178524409 | 248.91034187681112 | 0.4009680651340087 | 0.270026406896085 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 3 | 5.0 | 619.0 | 856.618957028381 | 917.4 | 1166.5475884711275 | True | True | I | I | True | 237.61895702838103 | 249.1475884711275 | 0.3838755363947997 | 0.27158010515710435 | 2 | concrete_controls | sweep_continuation |
| 3 | 8.0 | 698.8 | 951.9831618567316 | 905.8 | 1152.1192818768122 | True | True | I | I | True | 253.18316185673166 | 246.31928187681228 | 0.3623113363719686 | 0.2719356169980264 | 2 | concrete_controls | sweep_continuation |
| 4 | 5.0 | 437.0 | 657.8034325737328 | 894.2 | 1142.70161583774 | True | True | I | I | True | 220.80343257373283 | 248.50161583774002 | 0.5052710127545373 | 0.27790384235936033 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 4 | 10.0 | 561.4 | 817.7378223632347 | 869.8 | 1112.1322117129782 | True | True | I | I | True | 256.33782236323475 | 242.33221171297828 | 0.4566045998632611 | 0.2786068196286253 | 2 | concrete_controls | sweep_continuation |
| 4 | 15.0 | 682.9 | 967.3949828811772 | 837.7 | 1078.739150014373 | True | True | I | I | True | 284.4949828811772 | 241.03915001437304 | 0.4165983055808716 | 0.287739226470542 | 2 | concrete_controls | sweep_continuation |

Conclusion: largest mismatch appears already present in constitutive/equilibrium response

## Error delta vs prior artifact

- prior max_rel_err_Mx: 0.635764
- current max_rel_err_Mx: 0.505271
- delta max_rel_err_Mx: -0.130493
- prior max_rel_err_My: 0.501830
- current max_rel_err_My: 0.287739
- delta max_rel_err_My: -0.214091
