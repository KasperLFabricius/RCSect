# Unified PCROSS Output Rule Study

Cross-family candidate scoring for tbeam/snit/annular to determine whether one global reported-output rule is supported.

## Candidate global summary

| output | candidate | count | family_coverage | global_max_rel_error | global_median_rel_error | global_sign_agreement_rate | worst_family_max_rel_error | worst_family_median_rel_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lever_DX | lever:centroid_concrete_to_tension:dx | 23 | 2 | 1.0040155733174383 | 0.9978593041505848 | 0.5714285714285714 | 1.0040155733174383 | 1.0 |
| lever_DX | lever:centroid_concrete_to_tension:dx_negated | 23 | 2 | 1.0040155733174383 | 0.9978593041505849 | 0.42857142857142855 | 1.0040155733174383 | 1.0 |
| lever_DX | lever:moment_over_compress_local:DX_from_My_local | 23 | 2 | 1.0096145171327233 | 0.9963098308158721 | 0.42857142857142855 | 1.0096145171327233 | 1.0 |
| lever_DX | lever:centroid_total:dx | 23 | 2 | 1.00970637393027 | 0.9962061070744825 | 0.5 | 1.00970637393027 | 1.0 |
| lever_DX | lever:centroid_total:dx_negated | 23 | 2 | 1.00970637393027 | 0.9962061070744826 | 0.5 | 1.00970637393027 | 1.0 |
| lever_DX | lever:moment_over_compress_global:DX_from_My | 23 | 2 | 1.9946553346536684 | 1.9689036769156782 | 0.0 | 1.9946553346536684 | 1.9832628852487584 |
| lever_DX | lever:reported:DX | 23 | 2 | 2.005152788661694 | 1.985410015473373 | 0.0 | 2.005152788661694 | 1.9997975057431232 |
| lever_DY | lever:reported:DY | 23 | 2 | 0.2548588073980012 | 0.0010668017159145189 | 1.0 | 0.2548588073980012 | 0.07010418054351127 |
| lever_DY | lever:moment_over_compress_global:DY_from_Mx | 23 | 2 | 0.5264131359907772 | 0.011202256206586103 | 1.0 | 0.5264131359907772 | 0.23261532421263356 |
| lever_DY | lever:moment_over_compress_local:DY_from_Mx_local | 23 | 2 | 453284190099.6776 | 1.9832645025936935 | 0.4117647058823529 | 453284190099.6776 | 2.3967819276926736 |
| lever_DY | lever:centroid_concrete_to_tension:dy_negated | 23 | 2 | 454699788555.02246 | 1.9805290713551056 | 0.5882352941176471 | 454699788555.02246 | 2.3902350179748333 |
| lever_DY | lever:centroid_concrete_to_tension:dy | 23 | 2 | 454699788555.02246 | 1.9839672469962222 | 0.4117647058823529 | 454699788555.02246 | 2.390235017974833 |
| lever_DY | lever:centroid_total:dy_negated | 23 | 2 | 460906650147.57983 | 1.999306298731416 | 0.5882352941176471 | 460906650147.57983 | 2.411943777231553 |
| lever_DY | lever:centroid_total:dy | 23 | 2 | 460906650147.57983 | 1.9999767331902032 | 0.4117647058823529 | 460906650147.57983 | 2.411943777231553 |
| strain_mild | strain_mild:max_tensile_total | 32 | 2 | 35136741679.59043 | 1.9956663967683044 | 0.0 | 35136741679.59043 | 2.0035022568181367 |
| strain_mild | strain_mild:nearest_extreme_tension_total | 32 | 2 | 35136741679.59043 | 1.9956663967683044 | 0.0 | 35136741679.59043 | 2.0035022568181367 |
| strain_mild | strain_mild:max_compressive_total | 32 | 2 | 35136741679.59075 | 0.5863777814523744 | 0.7666666666666667 | 35136741679.59075 | 1.9752189929902226 |
| strain_mild | strain_mild:nearest_extreme_compression_total | 32 | 2 | 35136741679.59075 | 0.5863777814523744 | 0.7666666666666667 | 35136741679.59075 | 1.9752189929902226 |
| strain_mild | strain_mild:force_governing_total | 32 | 2 | 35136741679.59075 | 1.79174158816131 | 0.3 | 35136741679.59075 | 1.9824637548748036 |
| strain_mild | strain_mild:abs_strain_governing_total | 32 | 2 | 35136741679.59075 | 1.9956663967683044 | 0.06666666666666667 | 35136741679.59075 | 2.0035022568181367 |
| strain_prestressed | strain_prestressed:max_compressive_incremental | 14 | 1 | 1.22658529680141 | 0.9655275875482525 | 0.9285714285714286 | 1.22658529680141 | 0.9655275875482525 |
| strain_prestressed | strain_prestressed:abs_strain_governing_incremental | 14 | 1 | 1.2453015830666592 | 0.9655275875482525 | 0.8571428571428571 | 1.2453015830666592 | 0.9655275875482525 |
| strain_prestressed | strain_prestressed:force_governing_incremental | 14 | 1 | 1.2453015830666592 | 0.9655275875482525 | 0.8571428571428571 | 1.2453015830666592 | 0.9655275875482525 |
| strain_prestressed | strain_prestressed:max_tensile_incremental | 14 | 1 | 1.2453015830666592 | 0.9657817897196413 | 0.7857142857142857 | 1.2453015830666592 | 0.9657817897196413 |
| strain_prestressed | strain_prestressed:max_compressive_total | 14 | 1 | 2.0132519634680768 | 2.0006153068464982 | 0.0 | 2.0132519634680768 | 2.0006153068464982 |
| strain_prestressed | strain_prestressed:nearest_extreme_compression_total | 14 | 1 | 2.0132519634680768 | 2.0006153068464982 | 0.0 | 2.0132519634680768 | 2.0006153068464982 |
| strain_prestressed | strain_prestressed:force_governing_total | 14 | 1 | 2.0132519634680768 | 2.000869509017887 | 0.0 | 2.0132519634680768 | 2.000869509017887 |
| strain_prestressed | strain_prestressed:abs_strain_governing_total | 14 | 1 | 2.0132519634680768 | 2.0011237111892757 | 0.0 | 2.0132519634680768 | 2.0011237111892757 |
| strain_prestressed | strain_prestressed:max_tensile_total | 14 | 1 | 2.0132519634680768 | 2.0011237111892757 | 0.0 | 2.0132519634680768 | 2.0011237111892757 |
| strain_prestressed | strain_prestressed:nearest_extreme_tension_total | 14 | 1 | 2.0132519634680768 | 2.0011237111892757 | 0.0 | 2.0132519634680768 | 2.0011237111892757 |

## Winner assessment

| output | best_candidate | best_worst_family_max_rel_error | best_global_max_rel_error | best_global_median_rel_error | best_family_coverage | runner_up_candidate | runner_up_worst_family_max_rel_error | single_global_winner_exists | remaining_gap_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lever_DX | lever:centroid_concrete_to_tension:dx | 1.0040155733174383 | 1.0040155733174383 | 0.9978593041505848 | 2 | lever:centroid_concrete_to_tension:dx_negated | 1.0040155733174383 | False | likely constitutive/model-form mismatch or family-specific legacy behavior |
| lever_DY | lever:reported:DY | 0.2548588073980012 | 0.2548588073980012 | 0.0010668017159145189 | 2 | lever:moment_over_compress_global:DY_from_Mx | 0.5264131359907772 | True | output-definition mismatch (global winner supported) |
| strain_mild | strain_mild:max_tensile_total | 35136741679.59043 | 35136741679.59043 | 1.9956663967683044 | 2 | strain_mild:nearest_extreme_tension_total | 35136741679.59043 | False | likely constitutive/model-form mismatch or family-specific legacy behavior |
| strain_prestressed | strain_prestressed:max_compressive_incremental | 1.22658529680141 | 1.22658529680141 | 0.9655275875482525 | 1 | strain_prestressed:abs_strain_governing_incremental | 1.2453015830666592 | False | likely constitutive/model-form mismatch or family-specific legacy behavior |
