# Plastic output semantics study

## Candidate metrics by fixture family

| fixture_family | output | candidate | count | max_rel_error | median_rel_error | median_signed_error | sign_agreement_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| annular | compress_force | compress_force:concrete_plus_all_comp_steel | 18 | 0.002895597231681938 | 0.0023620797428610223 | -7.548075263993496 | 1.0 |
| annular | compress_force | compress_force:concrete_plus_comp_rebar | 18 | 0.002895597231681938 | 0.0023620797428610223 | -7.548075263993496 | 1.0 |
| annular | compress_force | compress_force:total_compression_abs | 18 | 0.002895597231681938 | 0.0023620797428610223 | -7.548075263993496 | 1.0 |
| annular | compress_force | compress_force:concrete_only | 18 | 0.5445937442585428 | 0.5151136937420462 | -1538.969495567078 | 1.0 |
| annular | lever_DX | lever:concrete_comp_to_tension:DX | 18 | 1.0037841333045119 | 1.0 | 2.337111650012364e-17 | 0.5 |
| annular | lever_DX | lever:total_comp_to_tension:DX | 18 | 1.010668524188792 | 1.0 | 1.0645326881673481e-17 | 0.42857142857142855 |
| annular | lever_DY | lever:moment_over_compression:DY_from_Mx | 18 | 0.018941372944166368 | 0.0065028467986320655 | 1.8269701708461458e-17 | 1.0 |
| annular | lever_DY | lever:moment_over_compression:DY_from_Mx_negated | 18 | 1.9934971532013686 | 1.9844401927607898 | -1.8269701708461458e-17 | 0.0 |
| annular | lever_DY | lever:moment_over_compression:DY_from_My | 18 | 452416933241.66425 | 1.9783760358841223 | 0.004933603961079128 | 0.5833333333333334 |
| annular | lever_DY | lever:moment_over_compression:DY_from_My_negated | 18 | 452416933241.66425 | 1.9783760358841223 | -0.004933603961079211 | 0.4166666666666667 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY_local | 18 | 453674784390.3724 | 1.9838661007501313 | 0.0044952505947083304 | 0.6666666666666666 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY_local_negated | 18 | 453674784390.3724 | 1.9838661007501317 | -0.004495250594708497 | 0.3333333333333333 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY_negated | 18 | 453674784390.3724 | 2.3876280325911674 | -0.39745009195237624 | 0.5 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY | 18 | 453674784390.3724 | 2.3876280325911683 | 0.39745009195237624 | 0.5 |
| annular | lever_DY | lever:total_comp_to_tension:DY_local | 18 | 460010611879.3256 | 1.9950233424863384 | 0.0009377834710503907 | 0.6666666666666666 |
| annular | lever_DY | lever:total_comp_to_tension:DY_local_negated | 18 | 460010611879.3256 | 1.9950233424863388 | -0.0009377834710504879 | 0.3333333333333333 |
| annular | lever_DY | lever:total_comp_to_tension:DY | 18 | 460010611879.3256 | 2.4097575955335366 | 0.402964594403379 | 0.5 |
| annular | lever_DY | lever:total_comp_to_tension:DY_negated | 18 | 460010611879.3256 | 2.4097575955335366 | -0.402964594403379 | 0.5 |
| annular | lever_L | lever:total_comp_to_tension:L | 18 | 0.0034449597657089143 | 0.0021461781359532546 | -0.0009893881206744504 | 1.0 |
| annular | lever_L | lever:moment_over_total_compression:L | 18 | 0.018941372944166368 | 0.016010069866296335 | -0.0066192607247504975 | 1.0 |
| annular | lever_L | lever:concrete_comp_to_tension:L | 18 | 0.022016323079742266 | 0.017829699024057063 | -0.007325215609627733 | 1.0 |
| annular | strain_mild | strain_mild:max_compression | 18 | 0.5935347139966172 | 0.567850721668719 | 3.8573438175933097 | 1.0 |
| annular | strain_mild | strain_mild:governing_abs_signed | 18 | 2.0127595977897648 | 2.0109092186457103 | 13.577274555102113 | 0.0 |
| annular | strain_mild | strain_mild:max_tension | 18 | 2.0127595977897648 | 2.0109092186457103 | 13.577274555102113 | 0.0 |
| snit | compress_force | compress_force:concrete_only | 14 | 1.8024198133547624 | 1.445311235572527 | 10448.877577571584 | 1.0 |
| snit | compress_force | compress_force:total_compression_abs | 14 | 1.8031324908629793 | 1.4592662917457229 | 10549.765656175703 | 1.0 |
| snit | compress_force | compress_force:concrete_plus_all_comp_steel | 14 | 1.80313249086298 | 1.4592662917457229 | 10549.765656175703 | 1.0 |
| snit | compress_force | compress_force:concrete_plus_comp_rebar | 14 | 1.80313249086298 | 1.4592662917457229 | 10549.765656175703 | 1.0 |
| snit | lever_DX | lever:total_comp_to_tension:DX | 5 | 0.00017552767775070856 | 0.00012261269759171635 | -8.296159511938419e-17 | nan |
| snit | lever_DX | lever:concrete_comp_to_tension:DX | 5 | 0.00018188512081133214 | 0.00013035297364142072 | -8.772334329690054e-17 | nan |
| snit | lever_DY | lever:moment_over_compression:DY_from_Mx | 5 | 0.7568992182552471 | 0.44699550028768853 | -0.2414464474931527 | 1.0 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_local | 5 | 1.0000000000000002 | 0.9999999999999999 | -0.7460000000000001 | 0.6 |
| snit | lever_DY | lever:total_comp_to_tension:DY_local | 5 | 1.0000000000000002 | 0.9999999999999999 | -0.7460000000000001 | 0.6 |
| snit | lever_DY | lever:moment_over_compression:DY_from_My | 5 | 1.0000000000000002 | 1.0 | -0.7460000000000001 | 0.6 |
| snit | lever_DY | lever:moment_over_compression:DY_from_My_negated | 5 | 1.0000000000000004 | 1.0 | -0.7459999999999999 | 0.4 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_local_negated | 5 | 1.0000000000000004 | 1.0000000000000002 | -0.7459999999999999 | 0.4 |
| snit | lever_DY | lever:total_comp_to_tension:DY_local_negated | 5 | 1.0000000000000004 | 1.0000000000000002 | -0.7459999999999999 | 0.4 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY | 5 | 1.3890023066884993 | 0.7868218213493994 | -0.12916079785913315 | 0.8 |
| snit | lever_DY | lever:total_comp_to_tension:DY | 5 | 1.4029629221542417 | 0.7802514018615208 | -0.121986718132859 | 0.8 |
| snit | lever_DY | lever:moment_over_compression:DY_from_Mx_negated | 5 | 1.7930575934820765 | 1.5530044997123114 | -1.2505535525068474 | 0.0 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_negated | 5 | 1.9925442338594792 | 1.2131781786506008 | -1.2544262367247212 | 0.2 |
| snit | lever_DY | lever:total_comp_to_tension:DY_negated | 5 | 2.002837008139282 | 1.2197485981384792 | -1.2612200504751876 | 0.2 |
| snit | lever_L | lever:moment_over_total_compression:L | 5 | 0.7568992182552471 | 0.44699550028768853 | -0.2414464474931527 | 1.0 |
| snit | lever_L | lever:total_comp_to_tension:L | 5 | 0.9409981042959045 | 0.5970370778457582 | -0.28896594567734696 | 1.0 |
| snit | lever_L | lever:concrete_comp_to_tension:L | 5 | 0.9480343205169545 | 0.6109976933115006 | -0.29572288356276627 | 1.0 |
| snit | strain_mild | strain_mild:max_tension | 14 | 7182060326.653316 | 1.9241558931445124 | -0.18663787187535116 | 0.0 |
| snit | strain_mild | strain_mild:max_compression | 14 | 7182060326.653635 | 1.8377354875553746 | -0.36754709751107495 | 0.4166666666666667 |
| snit | strain_mild | strain_mild:governing_abs_signed | 14 | 7182060326.653635 | 1.845002557990503 | -0.36754709751107495 | 0.16666666666666666 |
| snit | strain_prestressed | strain_prestressed:incremental_max_compression | 14 | 1.2356829842586496 | 0.9703507874389298 | 5.530999488401899 | 0.9285714285714286 |
| snit | strain_prestressed | strain_prestressed:governing_incremental_bar_incremental_strain | 14 | 1.2544304528121497 | 0.9703507874389298 | 5.530999488401899 | 0.8571428571428571 |
| snit | strain_prestressed | strain_prestressed:incremental_governing_abs_signed | 14 | 1.2544304528121497 | 0.9703507874389298 | 5.530999488401899 | 0.8571428571428571 |
| snit | strain_prestressed | strain_prestressed:incremental_max_tension | 14 | 1.2544304528121497 | 0.9706057723664782 | 5.532452902488925 | 0.7857142857142857 |
| snit | strain_prestressed | strain_prestressed:compressive_side_total | 13 | 2.0160030930471287 | 2.0054385067371756 | 11.430999488401898 | 0.0 |
| snit | strain_prestressed | strain_prestressed:stress_equivalent_governing_abs_signed | 14 | 2.0160030930471287 | 2.0054385067371756 | 11.432452902488924 | 0.0 |
| snit | strain_prestressed | strain_prestressed:stress_equivalent_max_compression | 14 | 2.0160030930471287 | 2.0054385067371756 | 11.430999488401898 | 0.0 |
| snit | strain_prestressed | strain_prestressed:stress_equivalent_max_tension | 14 | 2.0160030930471287 | 2.0054385067371756 | 11.432452902488924 | 0.0 |
| snit | strain_prestressed | strain_prestressed:max_compression | 14 | 2.022349650925316 | 2.0054385067371756 | 11.430999488401898 | 0.0 |
| snit | strain_prestressed | strain_prestressed:governing_incremental_bar_total_strain | 14 | 2.022349650925316 | 2.005693491664724 | 11.430999488401898 | 0.0 |
| snit | strain_prestressed | strain_prestressed:governing_abs_signed | 14 | 2.022349650925316 | 2.005948476592272 | 11.432452902488924 | 0.0 |
| snit | strain_prestressed | strain_prestressed:max_tension | 14 | 2.022349650925316 | 2.005948476592272 | 11.432452902488924 | 0.0 |
| snit | strain_prestressed | strain_prestressed:tensile_side_total | 3 | 2.022349650925316 | 2.020664219045916 | 15.167622381939871 | 0.0 |
| tbeam | compress_force | compress_force:concrete_plus_all_comp_steel | 6 | 0.34208330619674837 | 0.30183432800382226 | -1171.2226976709694 | 1.0 |
| tbeam | compress_force | compress_force:concrete_plus_comp_rebar | 6 | 0.34208330619674837 | 0.30183432800382226 | -1171.2226976709694 | 1.0 |
| tbeam | compress_force | compress_force:total_compression_abs | 6 | 0.34208330619674837 | 0.30183432800382226 | -1171.2226976709694 | 1.0 |
| tbeam | compress_force | compress_force:concrete_only | 6 | 0.562808520531405 | 0.5304848524187307 | -2112.798729446881 | 1.0 |
| tbeam | lever_DX | lever:total_comp_to_tension:DX | 6 | 0.6607819449404893 | 0.6337559734517312 | -0.4507711039248005 | 1.0 |
| tbeam | lever_DX | lever:concrete_comp_to_tension:DX | 6 | 0.6671174977052292 | 0.6378756871628706 | -0.45378572828914876 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY | 6 | 0.17674671474674844 | 0.05651947967833057 | -0.022192503853879803 | 1.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY | 6 | 0.24013178585289693 | 0.12454616389277812 | -0.054466973536274305 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_local | 6 | 0.27417480305929526 | 0.15080735946212748 | -0.06785007628897449 | 1.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_local | 6 | 0.3474415783795221 | 0.22004055308638076 | -0.0985304346176728 | 1.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_My | 6 | 0.4566169939390627 | 0.32119667114816997 | -0.14398893997185352 | 1.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_Mx | 6 | 0.7356848270856451 | 0.5503497137553619 | -0.2391271780784624 | 1.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_Mx_negated | 6 | 1.589969825034652 | 1.4496502862446379 | -0.6293728219215375 | 0.0 |
| tbeam | lever_DY | lever:moment_over_compression:DY_from_My_negated | 6 | 1.8221617489741968 | 1.67880332885183 | -0.7420535777982455 | 0.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_local_negated | 6 | 1.892475370945544 | 1.7799594469136193 | -0.7884889874863183 | 0.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_negated | 6 | 1.9478910808974894 | 1.875453836107222 | -0.8140330264637257 | 0.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_local_negated | 6 | 1.9641111419095139 | 1.8491926405378725 | -0.8191456467965708 | 0.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_negated | 6 | 2.0257785336992002 | 1.9497250537014852 | -0.8463074961461202 | 0.0 |
| tbeam | lever_L | lever:total_comp_to_tension:L | 6 | 0.4394356087642418 | 0.38825459919822525 | -0.3102796018351006 | 1.0 |
| tbeam | lever_L | lever:concrete_comp_to_tension:L | 6 | 0.4720562648940914 | 0.4241807861253153 | -0.3388733245027217 | 1.0 |
| tbeam | lever_L | lever:moment_over_total_compression:L | 6 | 0.6346127354579325 | 0.5341167080086606 | -0.4422200281361085 | 1.0 |
| tbeam | strain_mild | strain_mild:max_tension | 6 | 0.9316872318065439 | 0.7570713365090618 | -6.6752979991142425 | 1.0 |
| tbeam | strain_mild | strain_mild:governing_abs_signed | 6 | 2.112721738336721 | 1.3846859068381696 | -11.726020454716148 | 0.0 |
| tbeam | strain_mild | strain_mild:max_compression | 6 | 2.112721738336721 | 1.3846859068381696 | -11.726020454716148 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:governing_abs_signed | 6 | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:max_tension | 6 | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:stress_equivalent_governing_abs_signed | 6 | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:stress_equivalent_max_tension | 6 | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:compressive_side_total | 6 | 0.7753279008470509 | 0.6644525640599257 | -7.239237876310198 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:governing_incremental_bar_total_strain | 6 | 0.7753279008470509 | 0.6644525640599257 | -7.239237876310198 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:max_compression | 6 | 0.7753279008470509 | 0.6644525640599257 | -7.239237876310198 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:stress_equivalent_max_compression | 6 | 0.7753279008470509 | 0.6644525640599257 | -7.239237876310198 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:incremental_max_tension | 6 | 1.0711011673370854 | 1.0214491481099301 | -11.146305469807341 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:governing_incremental_bar_incremental_strain | 6 | 1.0799610536127038 | 1.0283480542330201 | -11.239237876310199 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:incremental_governing_abs_signed | 6 | 1.0799610536127038 | 1.0283480542330201 | -11.239237876310199 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:incremental_max_compression | 6 | 1.0799610536127038 | 1.0283480542330201 | -11.239237876310199 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:tensile_side_total | 0 | nan | nan | nan | nan |

## Chosen winners

- strain_mild: `strain_mild:max_tension`
- compress_force: `compress_force:concrete_plus_all_comp_steel`
- lever_L: `lever:total_comp_to_tension:L`
- lever_DX: `lever:total_comp_to_tension:DX`


## Family-specific winners for unresolved outputs

| fixture_family | output | candidate | max_rel_error | median_rel_error | median_signed_error | sign_agreement_rate |
| --- | --- | --- | --- | --- | --- | --- |
| annular | lever_DY | lever:moment_over_compression:DY_from_Mx | 0.018941372944166368 | 0.0065028467986320655 | 1.8269701708461458e-17 | 1.0 |
| snit | lever_DY | lever:moment_over_compression:DY_from_Mx | 0.7568992182552471 | 0.44699550028768853 | -0.2414464474931527 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY | 0.17674671474674844 | 0.05651947967833057 | -0.022192503853879803 | 1.0 |
| snit | strain_prestressed | strain_prestressed:incremental_max_compression | 1.2356829842586496 | 0.9703507874389298 | 5.530999488401899 | 0.9285714285714286 |
| tbeam | strain_prestressed | strain_prestressed:governing_abs_signed | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |

## Semantic-versus-constitutive conclusion

| output | cross_family_winner | family_winners | status | max_rel_error_reported | max_rel_error_semantic_aligned |
| --- | --- | --- | --- | --- | --- |
| strain_prestressed |  | strain_prestressed:governing_abs_signed, strain_prestressed:incremental_max_compression | family-specific winners only | 2.022349650925316 | 2.022349650925316 |
| lever_DY |  | lever:moment_over_compression:DY_from_Mx, lever:total_comp_to_tension:DY | family-specific winners only | 0.7568992182552471 | 2.4179749321480672 |