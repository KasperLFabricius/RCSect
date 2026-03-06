# Plastic Solver Benchmark Summary

## Active benchmark mapping

- mapping: `case_d_manual_strength_plus_fe_fu`
- gamma_c: 1.9
- gamma_s: 1.5
- gamma_p: 1.5
- gamma_E: 1.5
- gamma_u: 1.5

| load_case | angles_checked | angles_with_reference | max_abs_err_Mx | max_abs_err_My | max_rel_err_Mx | max_rel_err_My | all_quadrant_ok | all_sign_ok_Mx | all_sign_ok_My | max_candidate_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 16 | 3 | 37.71026223451224 | 22.637442973037764 | 0.06386307202584326 | 0.024675651812772797 | True | True | True | 2 |
| 4 | 15 | 3 | 40.88389873827032 | 32.50221333783941 | 0.07473616156367238 | 0.03879934742490081 | True | True | True | 2 |

## Referenced rows

Signed errors (abs/rel) are primary benchmark metrics. Magnitude-only errors remain in CSV as secondary diagnostics.

| load_case | V_deg | Mx_ref | Mx_calc | My_ref | My_calc | sign_agreement_Mx | sign_agreement_My | quadrant_expected | quadrant_calc | quadrant_agreement | abs_err_Mx | abs_err_My | rel_err_Mx | rel_err_My | candidate_count | pivot | selected_branch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2.0 | 544.3 | 509.53932989633347 | 921.8 | 903.2711600960753 | True | True | I | I | True | 34.760670103666484 | 18.528839903924677 | 0.06386307202584326 | 0.020100715886227683 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 3 | 5.0 | 619.0 | 586.4309265454029 | 917.4 | 894.7625570269622 | True | True | I | I | True | 32.56907345459706 | 22.637442973037764 | 0.05261562755185308 | 0.024675651812772797 | 2 | concrete_controls | sweep_continuation |
| 3 | 8.0 | 698.8 | 661.0897377654877 | 905.8 | 884.3046102184842 | True | True | I | I | True | 37.71026223451224 | 21.49538978151577 | 0.05396431344377826 | 0.023730834380123394 | 2 | concrete_controls | sweep_continuation |
| 4 | 5.0 | 437.0 | 404.34029739667517 | 894.2 | 869.5729652822912 | True | True | I | I | True | 32.65970260332483 | 24.627034717708852 | 0.07473616156367238 | 0.0275408574342528 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 4 | 10.0 | 561.4 | 520.5161012617297 | 869.8 | 846.6413277323888 | True | True | I | I | True | 40.88389873827032 | 23.15867226761111 | 0.07282489978316765 | 0.02662528428099691 | 2 | concrete_controls | sweep_continuation |
| 4 | 15.0 | 682.9 | 645.3570570934979 | 837.7 | 805.1977866621606 | True | True | I | I | True | 37.54294290650205 | 32.50221333783941 | 0.05497575473202819 | 0.03879934742490081 | 2 | concrete_controls | sweep_continuation |

## Contribution study (cases A-D)

| mapping | gamma_c | gamma_s | gamma_p | gamma_E | gamma_u | max_rel_err_Mx | max_rel_err_My | mean_rel_force_strain_curvature | mean_rel_moment_transform | dominant_mismatch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| case_a_baseline | 1.5 | 1.15 | 1.15 | 1.0 | 1.0 | 0.5052710127545373 | 0.287739226470542 | 0.3313521793378177 | 0.5850555610618049 | largest mismatch appears already present in constitutive/equilibrium response |
| case_b_manual_strength | 1.9 | 1.5 | 1.5 | 1.0 | 1.0 | 0.14530651526963156 | 0.043809329162606256 | 0.36917508492392803 | 0.5057434217418959 | largest mismatch appears already present in constitutive/equilibrium response |
| case_c_manual_strength_plus_fe | 1.9 | 1.5 | 1.5 | 1.5 | 1.0 | 0.07473616156367238 | 0.03879934742490081 | 0.37336714650357444 | 0.4569911409625945 | largest mismatch appears already present in constitutive/equilibrium response |
| case_d_manual_strength_plus_fe_fu | 1.9 | 1.5 | 1.5 | 1.5 | 1.5 | 0.07473616156367238 | 0.03879934742490081 | 0.37336714650357444 | 0.4569911409625945 | largest mismatch appears already present in constitutive/equilibrium response |

Conclusion: largest mismatch appears already present in constitutive/equilibrium response

## Error delta vs prior artifact

- prior max_rel_err_Mx: 0.505271
- current max_rel_err_Mx: 0.074736
- delta max_rel_err_Mx: -0.430535
- prior max_rel_err_My: 0.287739
- current max_rel_err_My: 0.038799
- delta max_rel_err_My: -0.248940
