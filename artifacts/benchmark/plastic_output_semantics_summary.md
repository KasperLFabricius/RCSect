# Plastic output semantics study

## Candidate metrics by fixture family

| fixture_family | output | candidate | count | max_rel_error | median_rel_error | median_signed_error | sign_agreement_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| annular | compress_force | compress_force:concrete_plus_all_comp_steel | 18 | 0.0007635971565132672 | 0.0003793824910628122 | 0.656226576983272 | 1.0 |
| annular | compress_force | compress_force:concrete_plus_comp_rebar | 18 | 0.0007635971565132672 | 0.0003793824910628122 | 0.656226576983272 | 1.0 |
| annular | compress_force | compress_force:total_compression_abs | 18 | 0.0007635971565132672 | 0.0003793824910628783 | 0.6562265769830447 | 1.0 |
| annular | compress_force | compress_force:concrete_only | 18 | 0.5445276129502772 | 0.5152015172635941 | -1537.847879741786 | 1.0 |
| annular | lever_DX | lever:concrete_comp_to_tension:DX | 18 | 1.0040155733174383 | 1.0 | 1.3944832735128566e-17 | 0.42857142857142855 |
| annular | lever_DX | lever:total_comp_to_tension:DX | 18 | 1.00970637393027 | 1.0 | 1.3029447923501348e-17 | 0.5 |
| annular | lever_DY | lever:moment_over_compression:DY_from_Mx | 18 | 0.01673549740630647 | 0.005444119768875782 | 1.0535355752835208e-17 | 1.0 |
| annular | lever_DY | lever:moment_over_compression:DY_from_Mx_negated | 18 | 1.9945558802311245 | 1.9854145471535598 | -1.0535355752835208e-17 | 0.0 |
| annular | lever_DY | lever:moment_over_compression:DY_from_My | 18 | 453284190099.6776 | 1.9807920655894902 | 0.004285614813838753 | 0.5 |
| annular | lever_DY | lever:moment_over_compression:DY_from_My_negated | 18 | 453284190099.6776 | 1.9807920655894902 | -0.004285614813838809 | 0.5 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY_local | 18 | 454699788555.02246 | 1.9858725053406587 | 0.003864627014394273 | 0.6666666666666666 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY_local_negated | 18 | 454699788555.02246 | 1.985872505340659 | -0.00386462701439437 | 0.3333333333333333 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY_negated | 18 | 454699788555.02246 | 2.390235017974833 | -0.3982949468064997 | 0.5 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY | 18 | 454699788555.02246 | 2.3902350179748333 | 0.3982949468064997 | 0.5 |
| annular | lever_DY | lever:total_comp_to_tension:DY_local | 18 | 460906650147.57983 | 1.997500935908629 | 0.0005385640579509271 | 0.6666666666666666 |
| annular | lever_DY | lever:total_comp_to_tension:DY_local_negated | 18 | 460906650147.57983 | 1.9975009359086293 | -0.0005385640579509549 | 0.3333333333333333 |
| annular | lever_DY | lever:total_comp_to_tension:DY | 18 | 460906650147.57983 | 2.411943777231553 | 0.4037027249192139 | 0.5 |
| annular | lever_DY | lever:total_comp_to_tension:DY_negated | 18 | 460906650147.57983 | 2.411943777231553 | -0.4037027249192139 | 0.5 |
| annular | lever_L | lever:total_comp_to_tension:L | 18 | 0.001898238768191539 | 0.0004501441346765711 | -5.206119267808784e-05 | 1.0 |
| annular | lever_L | lever:moment_over_total_compression:L | 18 | 0.016737114751241747 | 0.014386943808808627 | -0.005955224883671145 | 1.0 |
| annular | lever_L | lever:concrete_comp_to_tension:L | 18 | 0.01947092864489448 | 0.015713414523601 | -0.006300211444977638 | 1.0 |
| annular | strain_mild | strain_mild:max_compression | 18 | 0.5931401143053997 | 0.5674426389977265 | 3.8540327548260245 | 1.0 |
| annular | strain_mild | strain_mild:governing_abs_signed | 18 | 2.0052583528373704 | 2.0035022568181367 | 13.52068232359466 | 0.0 |
| annular | strain_mild | strain_mild:max_tension | 18 | 2.0052583528373704 | 2.0035022568181367 | 13.52068232359466 | 0.0 |
| snit | compress_force | compress_force:concrete_only | 14 | 1.791092062477927 | 1.4360408280622607 | 10381.857166476115 | 1.0 |
| snit | compress_force | compress_force:concrete_plus_all_comp_steel | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| snit | compress_force | compress_force:concrete_plus_comp_rebar | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| snit | compress_force | compress_force:total_compression_abs | 14 | 1.7945786894858 | 1.4522660296995331 | 10499.157261712775 | 1.0 |
| snit | lever_DX | lever:total_comp_to_tension:DX | 5 | 0.00011545310330168719 | 0.0001019861450513666 | -1.019861450513666e-16 | nan |
| snit | lever_DX | lever:concrete_comp_to_tension:DX | 5 | 0.00012289965549316725 | 0.00010647197493345748 | -1.0647197493345748e-16 | nan |
| snit | lever_DY | lever:moment_over_compression:DY_from_Mx | 5 | 0.7556945659781411 | 0.4461002226598369 | -0.24145378910868576 | 1.0 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_local | 5 | 0.9999999999999999 | 0.9999999999999999 | -0.7459999999999999 | 1.0 |
| snit | lever_DY | lever:total_comp_to_tension:DY_local | 5 | 0.9999999999999999 | 0.9999999999999999 | -0.7459999999999999 | 1.0 |
| snit | lever_DY | lever:moment_over_compression:DY_from_My | 5 | 1.0 | 0.9999999999999999 | -0.7459999999999999 | 1.0 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_local_negated | 5 | 1.0000000000000004 | 1.0000000000000002 | -0.7460000000000001 | 0.0 |
| snit | lever_DY | lever:moment_over_compression:DY_from_My_negated | 5 | 1.0000000000000004 | 1.0000000000000002 | -0.7460000000000001 | 0.0 |
| snit | lever_DY | lever:total_comp_to_tension:DY_local_negated | 5 | 1.0000000000000004 | 1.0000000000000002 | -0.7460000000000001 | 0.0 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY | 5 | 1.3907061335692499 | 0.7862230727379053 | -0.1290669194928067 | 0.8 |
| snit | lever_DY | lever:total_comp_to_tension:DY | 5 | 1.4047534180200494 | 0.7796166452226255 | -0.12184231569789805 | 0.8 |
| snit | lever_DY | lever:moment_over_compression:DY_from_Mx_negated | 5 | 1.7922422727288532 | 1.553899777340163 | -1.2505462108913141 | 0.0 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_negated | 5 | 1.9913510154894285 | 1.2137769272620949 | -1.255045342789006 | 0.2 |
| snit | lever_DY | lever:total_comp_to_tension:DY_negated | 5 | 2.0017169424613783 | 1.2203833547773744 | -1.2618763888398052 | 0.2 |
| snit | lever_L | lever:moment_over_total_compression:L | 5 | 0.7556945659781411 | 0.4461002226598369 | -0.24145378910868576 | 1.0 |
| snit | lever_L | lever:total_comp_to_tension:L | 5 | 0.938860757029832 | 0.5952465819799505 | -0.28809934567829604 | 1.0 |
| snit | lever_L | lever:concrete_comp_to_tension:L | 5 | 0.9459360942517768 | 0.6092938664307502 | -0.2948982313524831 | 1.0 |
| snit | strain_mild | strain_mild:max_tension | 14 | 35136741679.59043 | 1.9832757977569646 | -0.21436579395035923 | 0.0 |
| snit | strain_mild | strain_mild:max_compression | 14 | 35136741679.59075 | 1.9752189929902226 | -0.3950437985980445 | 0.4166666666666667 |
| snit | strain_mild | strain_mild:governing_abs_signed | 14 | 35136741679.59075 | 1.9824637548748036 | -0.3950437985980445 | 0.16666666666666666 |
| snit | strain_prestressed | strain_prestressed:incremental_max_compression | 14 | 1.22658529680141 | 0.9655275875482525 | 5.503507249025039 | 0.9285714285714286 |
| snit | strain_prestressed | strain_prestressed:governing_incremental_bar_incremental_strain | 14 | 1.2453015830666592 | 0.9655275875482525 | 5.503507249025039 | 0.8571428571428571 |
| snit | strain_prestressed | strain_prestressed:incremental_governing_abs_signed | 14 | 1.2453015830666592 | 0.9655275875482525 | 5.503507249025039 | 0.8571428571428571 |
| snit | strain_prestressed | strain_prestressed:incremental_max_tension | 14 | 1.2453015830666592 | 0.9657817897196413 | 5.504956201401955 | 0.7857142857142857 |
| snit | strain_prestressed | strain_prestressed:compressive_side_total | 13 | 2.0111833204000704 | 2.0006153068464982 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:stress_equivalent_governing_abs_signed | 14 | 2.0111833204000704 | 2.0006153068464982 | 11.404956201401955 | 0.0 |
| snit | strain_prestressed | strain_prestressed:stress_equivalent_max_compression | 14 | 2.0111833204000704 | 2.0006153068464982 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:stress_equivalent_max_tension | 14 | 2.0111833204000704 | 2.0006153068464982 | 11.404956201401955 | 0.0 |
| snit | strain_prestressed | strain_prestressed:max_compression | 14 | 2.0132519634680768 | 2.0006153068464982 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:governing_incremental_bar_total_strain | 14 | 2.0132519634680768 | 2.000869509017887 | 11.403507249025038 | 0.0 |
| snit | strain_prestressed | strain_prestressed:governing_abs_signed | 14 | 2.0132519634680768 | 2.0011237111892757 | 11.404956201401955 | 0.0 |
| snit | strain_prestressed | strain_prestressed:max_tension | 14 | 2.0132519634680768 | 2.0011237111892757 | 11.404956201401955 | 0.0 |
| snit | strain_prestressed | strain_prestressed:tensile_side_total | 3 | 2.0132519634680768 | 2.0115353493004253 | 15.099389726010575 | 0.0 |
| tbeam | compress_force | compress_force:total_compression_abs | 6 | 0.31614681184644977 | 0.27190007085287815 | -1063.452853699985 | 1.0 |
| tbeam | compress_force | compress_force:concrete_plus_all_comp_steel | 6 | 0.3161468118464499 | 0.27190007085287815 | -1063.452853699985 | 1.0 |
| tbeam | compress_force | compress_force:concrete_plus_comp_rebar | 6 | 0.3161468118464499 | 0.27190007085287815 | -1063.452853699985 | 1.0 |
| tbeam | compress_force | compress_force:concrete_only | 6 | 0.5254807465666251 | 0.4890305829384147 | -1949.6293421856615 | 1.0 |
| tbeam | lever_DX | lever:total_comp_to_tension:DX | 6 | 0.664972597336139 | 0.6285000207523634 | -0.4471982031488532 | 1.0 |
| tbeam | lever_DX | lever:concrete_comp_to_tension:DX | 6 | 0.6743352143588748 | 0.6431572287207638 | -0.45768811575603036 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY | 6 | 0.18566068957314075 | 0.06530856727151402 | -0.028616260629365203 | 1.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY | 6 | 0.26141406194484124 | 0.15034431163365475 | -0.0655746115267962 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_local | 6 | 0.27504692643551754 | 0.16654663951473433 | -0.07477361940724658 | 1.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_local | 6 | 0.3560511767511125 | 0.24652212041910393 | -0.11022428877865623 | 1.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_My | 6 | 0.45554173122498165 | 0.3268397359343136 | -0.14641484478884495 | 1.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_Mx | 6 | 0.7216532887357949 | 0.5397478138685992 | -0.23454538721316265 | 1.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_Mx_negated | 6 | 1.599266346362403 | 1.4602521861314008 | -0.6339546127868374 | 0.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_My_negated | 6 | 1.8071730867172122 | 1.6731602640656864 | -0.739024082852233 | 0.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_local_negated | 6 | 1.8572357385386924 | 1.7534778795808958 | -0.7765787438456327 | 0.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_negated | 6 | 1.914406974680917 | 1.849655688366345 | -0.8028439978610633 | 0.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_local_negated | 6 | 1.9379336738522863 | 1.8334533604852656 | -0.8113468281914902 | 0.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_negated | 6 | 2.0052729110176455 | 1.9346914327284859 | -0.8398106713800444 | 0.0 |
| tbeam | lever_L | lever:total_comp_to_tension:L | 6 | 0.4451324776071514 | 0.3935602994757313 | -0.31482721665925917 | 1.0 |
| tbeam | lever_L | lever:concrete_comp_to_tension:L | 6 | 0.48613368194409695 | 0.4395582069617994 | -0.351357727227367 | 1.0 |
| tbeam | lever_L | lever:moment_over_total_compression:L | 6 | 0.6314240665024342 | 0.5375510976354396 | -0.44259029764801 | 1.0 |
| tbeam | strain_mild | strain_mild:max_tension | 6 | 0.921789805875865 | 0.7385101325287684 | -6.496119844162587 | 1.0 |
| tbeam | strain_mild | strain_mild:governing_abs_signed | 6 | 2.109505592794873 | 1.383663023281882 | -11.717337302342372 | 0.0 |
| tbeam | strain_mild | strain_mild:max_compression | 6 | 2.109505592794873 | 1.383663023281882 | -11.717337302342372 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:tensile_side_total | 1 | 0.676309013497533 | 0.676309013497533 | -8.430191853246749 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:governing_abs_signed | 6 | 0.7576934663593857 | 0.64586759039138 | -7.0361526799249114 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:max_tension | 6 | 0.7576934663593857 | 0.64586759039138 | -7.0361526799249114 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:stress_equivalent_governing_abs_signed | 6 | 0.7576934663593857 | 0.6458675903913801 | -7.036152679924912 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:stress_equivalent_max_tension | 6 | 0.7576934663593857 | 0.6458675903913801 | -7.036152679924912 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:compressive_side_total | 6 | 0.7684852513920246 | 0.6546535175969279 | -7.132370582371001 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:governing_incremental_bar_total_strain | 6 | 0.7684852513920246 | 0.6546535175969279 | -7.132370582371001 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:max_compression | 6 | 0.7684852513920246 | 0.6546535175969279 | -7.132370582371001 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:stress_equivalent_max_compression | 6 | 0.7684852513920246 | 0.6546535175969279 | -7.132370582371001 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:incremental_max_tension | 6 | 1.054319715220529 | 1.011779352442608 | -11.03615267992491 | 0.16666666666666666 |
| tbeam | strain_prestressed | strain_prestressed:governing_incremental_bar_incremental_strain | 6 | 1.0635261453092 | 1.0189163093007032 | -11.132370582371001 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:incremental_governing_abs_signed | 6 | 1.0635261453092 | 1.0189163093007032 | -11.132370582371001 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:incremental_max_compression | 6 | 1.0635261453092 | 1.0189163093007032 | -11.132370582371001 | 0.0 |

## Chosen winners

- strain_mild: `strain_mild:max_tension`
- lever_L: `lever:total_comp_to_tension:L`
- lever_DX: `lever:total_comp_to_tension:DX`


## Family-specific winners for unresolved outputs

| fixture_family | output | candidate | max_rel_error | median_rel_error | median_signed_error | sign_agreement_rate |
| --- | --- | --- | --- | --- | --- | --- |
| annular | lever_DY | lever:moment_over_compression:DY_from_Mx | 0.01673549740630647 | 0.005444119768875782 | 1.0535355752835208e-17 | 1.0 |
| snit | lever_DY | lever:moment_over_compression:DY_from_Mx | 0.7556945659781411 | 0.4461002226598369 | -0.24145378910868576 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY | 0.18566068957314075 | 0.06530856727151402 | -0.028616260629365203 | 1.0 |
| snit | strain_prestressed | strain_prestressed:incremental_max_compression | 1.22658529680141 | 0.9655275875482525 | 5.503507249025039 | 0.9285714285714286 |
| tbeam | strain_prestressed | strain_prestressed:tensile_side_total | 0.676309013497533 | 0.676309013497533 | -8.430191853246749 | 1.0 |

## Semantic-versus-constitutive conclusion

| output | cross_family_winner | family_winners | status | max_rel_error_reported | max_rel_error_semantic_aligned |
| --- | --- | --- | --- | --- | --- |
| strain_prestressed |  | strain_prestressed:incremental_max_compression, strain_prestressed:tensile_side_total | family-specific winners only | 2.0132519634680768 | 2.0132519634680768 |
| lever_DY |  | lever:moment_over_compression:DY_from_Mx, lever:total_comp_to_tension:DY | family-specific winners only | 0.7556945659781411 | 2.42050482258475 |