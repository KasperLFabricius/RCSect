# Plastic Solver Benchmark Summary

| load_case | angles_checked | angles_with_reference | max_abs_err_Mx | max_abs_err_My | max_rel_err_Mx | max_rel_err_My | all_quadrant_ok | all_sign_ok_Mx | all_sign_ok_My | max_candidate_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 16 | 3 | 444.27183855548327 | 462.58713433528555 | 0.6357639361125977 | 0.5018302607238941 | True | True | True | 2 |
| 4 | 15 | 3 | 223.97396772025417 | 250.98627118732463 | 0.327974766027609 | 0.2806824772839685 | True | True | True | 2 |

## Referenced rows

Signed errors (abs/rel) are primary benchmark metrics. Magnitude-only errors (abs_mag_err_*) are secondary diagnostics.

| load_case | V_deg | Mx_ref | Mx_calc | My_ref | My_calc | sign_agreement_Mx | sign_agreement_My | quadrant_expected | quadrant_calc | quadrant_agreement | abs_err_Mx | abs_err_My | rel_err_Mx | rel_err_My | abs_mag_err_Mx | abs_mag_err_My | candidate_count | pivot | selected_branch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2.0 | 544.3 | 253.08929319284945 | 921.8 | 459.2128656647144 | True | True | I | I | True | 291.2107068071505 | 462.58713433528555 | 0.535018752171873 | 0.5018302607238941 | 291.2107068071505 | 462.58713433528555 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 3 | 5.0 | 619.0 | 253.8070074187964 | 917.4 | 459.0625169807591 | True | True | I | I | True | 365.1929925812036 | 458.3374830192409 | 0.5899725243638184 | 0.49960484305563646 | 365.1929925812036 | 458.3374830192409 | 2 | concrete_controls | sweep_continuation |
| 3 | 8.0 | 698.8 | 254.52816144451668 | 905.8 | 458.8729593660445 | True | True | I | I | True | 444.27183855548327 | 446.92704063395547 | 0.6357639361125977 | 0.4934058739610902 | 444.27183855548327 | 446.92704063395547 | 2 | concrete_controls | sweep_continuation |
| 4 | 5.0 | 437.0 | 376.1926356711496 | 894.2 | 643.2137288126754 | True | True | I | I | True | 60.80736432885038 | 250.98627118732463 | 0.13914728679370797 | 0.2806824772839685 | 60.80736432885038 | 250.98627118732463 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 4 | 10.0 | 561.4 | 430.6304539975448 | 869.8 | 641.1818469327995 | True | True | I | I | True | 130.76954600245517 | 228.6181530672004 | 0.23293470965880866 | 0.2628399092517825 | 130.76954600245517 | 228.6181530672004 | 2 | concrete_controls | sweep_continuation |
| 4 | 15.0 | 682.9 | 458.9260322797458 | 837.7 | 638.6396514725539 | True | True | I | I | True | 223.97396772025417 | 199.0603485274462 | 0.327974766027609 | 0.23762725143541386 | 223.97396772025417 | 199.0603485274462 | 2 | concrete_controls | sweep_continuation |