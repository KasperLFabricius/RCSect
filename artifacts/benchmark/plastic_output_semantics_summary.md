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
| annular | lever_DY | lever:concrete_comp_to_tension:DY_negated | 18 | 453674784390.3724 | 2.3876280325911674 | -0.39745009195237624 | 0.5 |
| annular | lever_DY | lever:concrete_comp_to_tension:DY | 18 | 453674784390.3724 | 2.3876280325911683 | 0.39745009195237624 | 0.5 |
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
| snit | lever_DX | lever:total_comp_to_tension:DX | 5 | 0.00014246103806207018 | 9.603880941579598e-05 | -9.372112819470386e-17 | nan |
| snit | lever_DX | lever:concrete_comp_to_tension:DX | 5 | 0.00014722904646363299 | 9.951901493906289e-05 | -9.724097266596604e-17 | nan |
| snit | lever_DY | lever:concrete_comp_to_tension:DY | 5 | 1.3889843711032042 | 0.7868218213493994 | -0.12912558556545095 | 0.8 |
| snit | lever_DY | lever:total_comp_to_tension:DY | 5 | 1.402944820342888 | 0.7802514018615208 | -0.12195264276897122 | 0.8 |
| snit | lever_DY | lever:concrete_comp_to_tension:DY_negated | 5 | 1.9927485075389393 | 1.2131781786506008 | -1.2544262367247212 | 0.2 |
| snit | lever_DY | lever:total_comp_to_tension:DY_negated | 5 | 2.0030396461246416 | 1.2197485981384792 | -1.2612200504751876 | 0.2 |
| snit | lever_L | lever:moment_over_total_compression:L | 5 | 0.7568992182552471 | 0.4469953814486658 | -0.2414352804124057 | 1.0 |
| snit | lever_L | lever:total_comp_to_tension:L | 5 | 0.9409981042959045 | 0.5970551796571119 | -0.28897470695404215 | 1.0 |
| snit | lever_L | lever:concrete_comp_to_tension:L | 5 | 0.9480343205169545 | 0.611015628896796 | -0.29573156438604925 | 1.0 |
| snit | strain_mild | strain_mild:max_tension | 14 | 7182060326.653316 | 1.9241558931445124 | -0.18663787187535116 | 0.0 |
| snit | strain_mild | strain_mild:max_compression | 14 | 7182060326.653635 | 1.8377354875553746 | -0.36754709751107495 | 0.4166666666666667 |
| snit | strain_mild | strain_mild:governing_abs_signed | 14 | 7182060326.653635 | 1.845002557990503 | -0.36754709751107495 | 0.16666666666666666 |
| snit | strain_prestressed | strain_prestressed:max_compression | 14 | 2.0227068649281725 | 2.0054385067371756 | 11.430999488401898 | 0.0 |
| snit | strain_prestressed | strain_prestressed:governing_abs_signed | 14 | 2.0227068649281725 | 2.005948476592272 | 11.432452902488924 | 0.0 |
| snit | strain_prestressed | strain_prestressed:max_tension | 14 | 2.0227068649281725 | 2.005948476592272 | 11.432452902488924 | 0.0 |
| tbeam | compress_force | compress_force:concrete_plus_all_comp_steel | 6 | 0.34208330619674837 | 0.30183432800382226 | -1171.2226976709694 | 1.0 |
| tbeam | compress_force | compress_force:concrete_plus_comp_rebar | 6 | 0.34208330619674837 | 0.30183432800382226 | -1171.2226976709694 | 1.0 |
| tbeam | compress_force | compress_force:total_compression_abs | 6 | 0.34208330619674837 | 0.30183432800382226 | -1171.2226976709694 | 1.0 |
| tbeam | compress_force | compress_force:concrete_only | 6 | 0.562808520531405 | 0.5304848524187307 | -2112.798729446881 | 1.0 |
| tbeam | lever_DX | lever:total_comp_to_tension:DX | 6 | 0.6607819449404893 | 0.6337559734517312 | -0.4507711039248005 | 1.0 |
| tbeam | lever_DX | lever:concrete_comp_to_tension:DX | 6 | 0.6671174977052292 | 0.6378756871628706 | -0.45378572828914876 | 1.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY | 6 | 0.17674671474674844 | 0.05651947967833057 | -0.022192503853879803 | 1.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY | 6 | 0.24013178585289693 | 0.12454616389277812 | -0.054466973536274305 | 1.0 |
| tbeam | lever_DY | lever:concrete_comp_to_tension:DY_negated | 6 | 1.9478910808974894 | 1.875453836107222 | -0.8140330264637257 | 0.0 |
| tbeam | lever_DY | lever:total_comp_to_tension:DY_negated | 6 | 2.0257785336992002 | 1.9497250537014852 | -0.8463074961461202 | 0.0 |
| tbeam | lever_L | lever:total_comp_to_tension:L | 6 | 0.4394356087642418 | 0.38825459919822525 | -0.3102796018351006 | 1.0 |
| tbeam | lever_L | lever:concrete_comp_to_tension:L | 6 | 0.4720562648940914 | 0.4241807861253153 | -0.3388733245027217 | 1.0 |
| tbeam | lever_L | lever:moment_over_total_compression:L | 6 | 0.6346127354579325 | 0.5341167080086606 | -0.4422200281361085 | 1.0 |
| tbeam | strain_mild | strain_mild:max_tension | 6 | 0.9316872318065439 | 0.7570713365090618 | -6.6752979991142425 | 1.0 |
| tbeam | strain_mild | strain_mild:governing_abs_signed | 6 | 2.112721738336721 | 1.3846859068381696 | -11.726020454716148 | 0.0 |
| tbeam | strain_mild | strain_mild:max_compression | 6 | 2.112721738336721 | 1.3846859068381696 | -11.726020454716148 | 0.0 |
| tbeam | strain_prestressed | strain_prestressed:governing_abs_signed | 6 | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:max_tension | 6 | 0.7649048389292071 | 0.6559657326041044 | -7.146305469807341 | 1.0 |
| tbeam | strain_prestressed | strain_prestressed:max_compression | 6 | 0.7753279008470509 | 0.6644525640599257 | -7.239237876310198 | 1.0 |

## Chosen winners

- strain_mild: `strain_mild:max_tension`
- compress_force: `compress_force:concrete_plus_all_comp_steel`
- lever_L: `lever:total_comp_to_tension:L`
- lever_DX: `lever:total_comp_to_tension:DX`
