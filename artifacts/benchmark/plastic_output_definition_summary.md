# Plastic output-definition candidate study

Family-specific candidate scoring for unresolved outputs.

## Candidate metrics by family/output

| fixture_family | output | candidate | count | max_rel_error | median_rel_error | median_signed_error | sign_agreement_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| annular | compress_force | compress_force:concrete_plus_comp_mild | 18 | 0.0007635971565132672 | 0.0003793824910628122 | 0.656226576983272 | 1.0 |
| annular | compress_force | compress_force:concrete_plus_comp_mild_plus_comp_prestress | 18 | 0.0007635971565132672 | 0.0003793824910628122 | 0.656226576983272 | 1.0 |
| annular | compress_force | compress_force:full_compression_resultant_abs | 18 | 0.0007635971565132672 | 0.0003793824910628783 | 0.6562265769830447 | 1.0 |
| annular | compress_force | compress_force:total_compression_abs | 18 | 0.0007635971565132672 | 0.0003793824910628783 | 0.6562265769830447 | 1.0 |
| annular | compress_force | compress_force:concrete_only | 18 | 0.5445276129502772 | 0.5152015172635941 | -1537.847879741786 | 1.0 |
| snit | compress_force | compress_force:concrete_only | 14 | 1.791092062477927 | 1.4360408280622607 | 10381.857166476115 | 1.0 |
| snit | compress_force | compress_force:concrete_plus_comp_mild | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| snit | compress_force | compress_force:concrete_plus_comp_mild_plus_comp_prestress | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| snit | compress_force | compress_force:full_compression_resultant_abs | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| snit | compress_force | compress_force:total_compression_abs | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| annular | lever_DX | lever:reported:DX | 18 | 0.0014416176036070511 | 0.0002125861677639885 | 1.0182817776081351e-17 | 1.0 |
| annular | lever_DX | lever:centroid_concrete_to_tension:dx | 18 | 1.0040155733174383 | 1.0 | 2.3583573660696334e-18 | 0.5714285714285714 |
| annular | lever_DX | lever:centroid_concrete_to_tension:dx_negated | 18 | 1.0040155733174383 | 1.0 | 1.3944832735128566e-17 | 0.42857142857142855 |
| annular | lever_DX | lever:moment_over_compress_local:DX_from_My_local | 18 | 1.0096145171327233 | 1.0 | 3.011291224618204e-18 | 0.42857142857142855 |
| annular | lever_DX | lever:centroid_total:dx | 18 | 1.00970637393027 | 1.0 | 5.711765691944165e-18 | 0.5 |
| annular | lever_DX | lever:centroid_total:dx_negated | 18 | 1.00970637393027 | 1.0 | 1.3029447923501348e-17 | 0.5 |
| annular | lever_DX | lever:moment_over_compress_global:DX_from_My | 18 | 1.9946553346536684 | 1.9832628852487584 | -1.0331136589812167e-17 | 0.0 |
| snit | lever_DX | lever:reported:DX | 5 | 0.00010748498804273532 | 8.872660627433818e-05 | 7.170748223651667e-17 | nan |
| snit | lever_DX | lever:centroid_total:dx | 5 | 0.00011545310330168719 | 0.0001019861450513666 | 1.019861450513666e-16 | nan |
| snit | lever_DX | lever:centroid_total:dx_negated | 5 | 0.00011545310330168719 | 0.0001019861450513666 | -1.019861450513666e-16 | nan |
| snit | lever_DX | lever:centroid_concrete_to_tension:dx | 5 | 0.00012289965549316725 | 0.00010647197493345748 | 1.0647197493345748e-16 | nan |
| snit | lever_DX | lever:centroid_concrete_to_tension:dx_negated | 5 | 0.00012289965549316725 | 0.00010647197493345748 | -1.0647197493345748e-16 | nan |
| snit | lever_DX | lever:moment_over_compress_local:DX_from_My_local | 5 | 0.00021672028926989786 | 0.00015172626103656764 | 1.5172626103656763e-16 | nan |
| snit | lever_DX | lever:moment_over_compress_global:DX_from_My | 5 | 0.00021672028926989786 | 0.0001984501465906359 | 1.12615620240343e-16 | nan |
| annular | lever_DY | lever:reported:DY | 18 | 0.002499064091371146 | 0.0006937012685839397 | 1.8023071861446066e-17 | 1.0 |
| annular | lever_DY | lever:moment_over_compress_global:DY_from_Mx | 18 | 0.01673549740630647 | 0.005444119768875782 | 1.0535355752835208e-17 | 1.0 |
| annular | lever_DY | lever:moment_over_compress_local:DY_from_Mx_local | 18 | 453284190099.6776 | 2.3967819276926736 | -0.39810202179127663 | 0.5 |
| annular | lever_DY | lever:centroid_concrete_to_tension:dy | 18 | 454699788555.02246 | 2.390235017974833 | -0.3982949468064997 | 0.5 |
| annular | lever_DY | lever:centroid_concrete_to_tension:dy_negated | 18 | 454699788555.02246 | 2.3902350179748333 | 0.3982949468064997 | 0.5 |
| annular | lever_DY | lever:centroid_total:dy | 18 | 460906650147.57983 | 2.411943777231553 | -0.4037027249192139 | 0.5 |
| annular | lever_DY | lever:centroid_total:dy_negated | 18 | 460906650147.57983 | 2.411943777231553 | 0.4037027249192139 | 0.5 |
| snit | lever_DY | lever:reported:DY | 5 | 0.2548588073980012 | 0.07010418054351127 | -0.03744437148058 | 1.0 |
| snit | lever_DY | lever:moment_over_compress_global:DY_from_Mx | 5 | 0.5264131359907772 | 0.23261532421263356 | -0.17353103186262464 | 1.0 |
| snit | lever_DY | lever:centroid_concrete_to_tension:dy_negated | 5 | 1.3907061335692499 | 0.7862230727379053 | -0.1290669194928067 | 0.8 |
| snit | lever_DY | lever:centroid_total:dy_negated | 5 | 1.4047534180200494 | 0.7796166452226255 | -0.12184231569789805 | 0.8 |
| snit | lever_DY | lever:moment_over_compress_local:DY_from_Mx_local | 5 | 1.7922422727288532 | 1.5641323185082772 | -1.2635308022738414 | 0.2 |
| snit | lever_DY | lever:centroid_concrete_to_tension:dy | 5 | 1.9913510154894285 | 1.2137769272620949 | -1.255045342789006 | 0.2 |
| snit | lever_DY | lever:centroid_total:dy | 5 | 2.0017169424613783 | 1.2203833547773744 | -1.2618763888398052 | 0.2 |
| annular | lever_L | lever:centroid_total:L | 18 | 0.001898238768191539 | 0.0004501441346765711 | -5.206119267808784e-05 | 1.0 |
| annular | lever_L | lever:reported:L | 18 | 0.001898238768191539 | 0.000450144134676631 | -5.206119267808784e-05 | 1.0 |
| annular | lever_L | lever:moment_over_compress_local:L | 18 | 0.016737114751241625 | 0.014386943808808488 | -0.00595522488367109 | 1.0 |
| annular | lever_L | lever:centroid_concrete_to_tension:L | 18 | 0.01947092864489448 | 0.015713414523600942 | -0.006300211444977638 | 1.0 |
| snit | lever_L | lever:reported:L | 5 | 0.2548588073980012 | 0.07010418054351127 | 0.0012104444352719623 | 1.0 |
| snit | lever_L | lever:moment_over_compress_local:L | 5 | 0.5264131359907772 | 0.23261532421263356 | -0.17353103186262464 | 1.0 |
| snit | lever_L | lever:centroid_total:L | 5 | 0.938860757029832 | 0.5952465819799505 | -0.28809934567829604 | 1.0 |
| snit | lever_L | lever:centroid_concrete_to_tension:L | 5 | 0.9459360942517768 | 0.6092938664307502 | -0.2948982313524831 | 1.0 |
| annular | strain_mild | strain_mild:max_compressive_total | 18 | 0.5931401143053997 | 0.5674426389977265 | 3.8540327548260245 | 1.0 |
| annular | strain_mild | strain_mild:nearest_extreme_compression_total | 18 | 0.5931401143053997 | 0.5674426389977265 | 3.8540327548260245 | 1.0 |
| annular | strain_mild | strain_mild:force_governing_total | 18 | 2.00525835283737 | 1.4980372291646993 | 10.027048305585911 | 0.2777777777777778 |
| annular | strain_mild | strain_mild:abs_strain_governing_total | 18 | 2.0052583528373704 | 2.0035022568181367 | 13.52068232359466 | 0.0 |
| annular | strain_mild | strain_mild:max_tensile_total | 18 | 2.0052583528373704 | 2.0035022568181367 | 13.52068232359466 | 0.0 |
| annular | strain_mild | strain_mild:nearest_extreme_tension_total | 18 | 2.0052583528373704 | 2.0035022568181367 | 13.52068232359466 | 0.0 |
| snit | strain_mild | strain_mild:max_tensile_total | 14 | 35136741679.59043 | 1.9832757977569646 | -0.21436579395035923 | 0.0 |
| snit | strain_mild | strain_mild:nearest_extreme_tension_total | 14 | 35136741679.59043 | 1.9832757977569646 | -0.21436579395035923 | 0.0 |
| snit | strain_mild | strain_mild:max_compressive_total | 14 | 35136741679.59075 | 1.9752189929902226 | -0.3950437985980445 | 0.4166666666666667 |
| snit | strain_mild | strain_mild:nearest_extreme_compression_total | 14 | 35136741679.59075 | 1.9752189929902226 | -0.3950437985980445 | 0.4166666666666667 |
| snit | strain_mild | strain_mild:abs_strain_governing_total | 14 | 35136741679.59075 | 1.9824637548748036 | -0.3950437985980445 | 0.16666666666666666 |
| snit | strain_mild | strain_mild:force_governing_total | 14 | 35136741679.59075 | 1.9824637548748036 | -0.3950437985980445 | 0.3333333333333333 |
| snit | strain_prestressed | strain_prestressed:max_compressive_incremental | 14 | 1.22658529680141 | 0.9655275875482525 | 5.503507249025039 | 0.9285714285714286 |
| snit | strain_prestressed | strain_prestressed:abs_strain_governing_incremental | 14 | 1.2453015830666592 | 0.9655275875482525 | 5.503507249025039 | 0.8571428571428571 |
| snit | strain_prestressed | strain_prestressed:force_governing_incremental | 14 | 1.2453015830666592 | 0.9655275875482525 | 5.503507249025039 | 0.8571428571428571 |
| snit | strain_prestressed | strain_prestressed:max_tensile_incremental | 14 | 1.2453015830666592 | 0.9657817897196413 | 5.504956201401955 | 0.7857142857142857 |
| snit | strain_prestressed | strain_prestressed:max_compressive_total | 14 | 2.0132519634680768 | 2.0006153068464982 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:nearest_extreme_compression_total | 14 | 2.0132519634680768 | 2.0006153068464982 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:force_governing_total | 14 | 2.0132519634680768 | 2.000869509017887 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:abs_strain_governing_total | 14 | 2.0132519634680768 | 2.0011237111892757 | 11.404956201401955 | 0.0 |
| snit | strain_prestressed | strain_prestressed:max_tensile_total | 14 | 2.0132519634680768 | 2.0011237111892757 | 11.404956201401955 | 0.0 |
| snit | strain_prestressed | strain_prestressed:nearest_extreme_tension_total | 14 | 2.0132519634680768 | 2.0011237111892757 | 11.404956201401955 | 0.0 |

## Best candidate by family and cross-family winner status

| output | fixture_family | best_candidate | max_rel_error | median_rel_error | sign_agreement_rate | cross_family_winner | cross_family_winner_exists |
| --- | --- | --- | --- | --- | --- | --- | --- |
| compress_force | annular | compress_force:concrete_plus_comp_mild | 0.0007635971565132672 | 0.0003793824910628122 | 1.0 |  | False |
| compress_force | snit | compress_force:concrete_only | 1.791092062477927 | 1.4360408280622607 | 1.0 |  | False |
| lever_DX | annular | lever:reported:DX | 0.0014416176036070511 | 0.0002125861677639885 | 1.0 |  | False |
| lever_DX | snit | lever:reported:DX | 0.00010748498804273532 | 8.872660627433818e-05 | nan |  | False |
| lever_DY | annular | lever:reported:DY | 0.002499064091371146 | 0.0006937012685839397 | 1.0 |  | False |
| lever_DY | snit | lever:reported:DY | 0.2548588073980012 | 0.07010418054351127 | 1.0 |  | False |
| lever_L | annular | lever:centroid_total:L | 0.001898238768191539 | 0.0004501441346765711 | 1.0 |  | False |
| lever_L | snit | lever:reported:L | 0.2548588073980012 | 0.07010418054351127 | 1.0 |  | False |
| strain_mild | annular | strain_mild:max_compressive_total | 0.5931401143053997 | 0.5674426389977265 | 1.0 |  | False |
| strain_mild | snit | strain_mild:max_tensile_total | 35136741679.59043 | 1.9832757977569646 | 0.0 |  | False |
| strain_prestressed | snit | strain_prestressed:max_compressive_incremental | 1.22658529680141 | 0.9655275875482525 | 0.9285714285714286 |  | False |

No cross-family winner: compress_force, lever_DX, lever_DY, lever_L, strain_mild, strain_prestressed
