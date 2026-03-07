# Plastic Solver Benchmark Summary

## Active benchmark mapping

- mapping: `case_d_manual_strength_plus_fe_fu`
- gamma_c: 1.9
- gamma_s: 1.5
- gamma_p: 1.5
- gamma_E: 1.5
- gamma_u: 1.5

| load_case | angles_checked | angles_with_reference | max_abs_err_Mx | max_abs_err_My | max_rel_err_Mx | max_rel_err_My | all_quadrant_ok | all_sign_ok_Mx | all_sign_ok_My | max_candidate_count | warning_match_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 16 | 3 | 37.71026223451224 | 22.637442973037764 | 0.06386307202584326 | 0.024675651812772797 | True | True | True | 2 | nan |
| 4 | 15 | 3 | 40.88389873827032 | 32.50221333783941 | 0.07473616156367238 | 0.03879934742490081 | True | True | True | 2 | nan |
| 101 | 5 | 3 | 68.89595289940098 | 40.72745938911248 | 0.014991720972103963 | 0.0063159015242715225 | True | True | True | 2 | nan |
| 102 | 5 | 3 | 65.75462416723713 | 38.422124174912824 | 0.01539127947362884 | 0.005885381437245393 | True | True | True | 2 | nan |
| 103 | 5 | 5 | 46.343057063527795 | 38.306369652109424 | 0.01544923061090369 | 0.005866392485544645 | True | True | True | 2 | nan |
| 104 | 5 | 3 | 26.148207402000935 | 38.306369652108515 | 0.014344290636897765 | 0.005866392485544505 | True | True | True | 2 | nan |
| 201 | 9 | 9 | 7.831133268846088 | 8.594211825672573 | 0.0050000850905670335 | 0.006124792013084018 | True | True | True | 2 | 1.0 |
| 202 | 9 | 9 | 3.627410417413671 | 3.390366268043749 | 0.00442413093193478 | 0.003877806551576975 | True | True | True | 2 | 1.0 |

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
| 101 | 0.0 | -4595.6 | -4664.495952899401 | 6448.4 | 6489.127459389112 | True | True | II | II | True | 68.89595289940098 | 40.72745938911248 | 0.014991720972103963 | 0.0063159015242715225 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 101 | 90.0 | 2714.6 | 2686.627881701185 | 0.0 | 1.0824674490095276e-12 | True | nan | axis | axis | nan | 27.972118298815076 | 1.0824674490095276e-12 | 0.010304324135716155 | nan | 2 | concrete_controls | sweep_continuation |
| 101 | 180.0 | -4595.6 | -4664.4959528993995 | -6448.4 | -6489.127459389112 | True | True | III | III | True | 68.89595289939916 | 40.72745938911248 | 0.014991720972103568 | 0.0063159015242715225 | 2 | concrete_controls | sweep_continuation |
| 102 | 0.0 | 4272.2 | 4337.954624167235 | 6528.4 | 6566.8221241749125 | True | True | I | I | True | 65.7546241672353 | 38.422124174912824 | 0.015391279473628413 | 0.005885381437245393 | 1 | concrete_controls | sweep_unique |
| 102 | 90.0 | 11308.3 | 11316.404059828963 | 0.0 | -3.552713678800501e-12 | True | nan | axis | axis | nan | 8.104059828963727 | 3.552713678800501e-12 | 0.0007166470494206669 | nan | 2 | concrete_controls | sweep_continuation |
| 102 | 180.0 | 4272.2 | 4337.954624167237 | -6528.4 | -6566.8221241749125 | True | True | IV | IV | True | 65.75462416723713 | 38.422124174912824 | 0.01539127947362884 | 0.005885381437245393 | 1 | concrete_controls | sweep_unique |
| 103 | 0.0 | 2999.7 | 3046.043057063525 | 6529.8 | 6568.106369652109 | True | True | I | I | True | 46.343057063525066 | 38.306369652108515 | 0.01544923061090278 | 0.005866392485544505 | 1 | concrete_controls | sweep_unique |
| 103 | 90.0 | 9869.1 | 9866.585549726706 | 0.0 | -3.164135620181696e-12 | True | nan | axis | axis | nan | 2.514450273294642 | 3.164135620181696e-12 | 0.00025478009882305805 | nan | 2 | concrete_controls | sweep_continuation |
| 103 | 180.0 | 2999.7 | 3046.0430570635276 | -6529.8 | -6568.106369652109 | True | True | IV | IV | True | 46.343057063527795 | 38.306369652108515 | 0.01544923061090369 | 0.005866392485544505 | 1 | concrete_controls | sweep_unique |
| 103 | 270.0 | -4223.3 | -4203.9094571870155 | 0.0 | -2.3009621937660183e-12 | True | nan | axis | axis | nan | 19.390542812984677 | 2.3009621937660183e-12 | 0.004591324985907862 | nan | 2 | concrete_controls | sweep_continuation |
| 103 | 360.0 | 2999.7 | 3046.043057063523 | 6529.8 | 6568.10636965211 | True | True | I | I | True | 46.34305706352325 | 38.306369652109424 | 0.015449230610902174 | 0.005866392485544645 | 1 | concrete_controls | sweep_unique |
| 104 | 0.0 | -1822.9 | -1849.048207402001 | 6529.8 | 6568.106369652109 | True | True | II | II | True | 26.148207402000935 | 38.306369652108515 | 0.014344290636897765 | 0.005866392485544505 | 1 | concrete_controls | sweep_unique |
| 104 | 90.0 | 4627.3 | 4632.42198977097 | 0.0 | 1.7763568394002505e-12 | True | nan | axis | axis | nan | 5.121989770969776 | 1.7763568394002505e-12 | 0.001106906786024199 | nan | 2 | concrete_controls | sweep_continuation |
| 104 | 180.0 | -1822.9 | -1849.0482074019983 | -6529.8 | -6568.106369652109 | True | True | III | III | True | 26.148207401998206 | 38.306369652108515 | 0.014344290636896267 | 0.005866392485544505 | 1 | concrete_controls | sweep_unique |
| 201 | 0.0 | 0.0 | 7.602465894875307e-14 | 1568.3 | 1559.7057881743276 | nan | True | axis | axis | nan | 7.602465894875307e-14 | 8.594211825672346 | nan | 0.005479953979259291 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 201 | 45.0 | 1115.7 | 1111.774234402984 | 1101.6 | 1094.8529291183866 | True | True | I | I | True | 3.9257655970161522 | 6.747070881613354 | 0.0035186569839707376 | 0.006124792013084018 | 2 | concrete_controls | sweep_continuation |
| 201 | 90.0 | 1566.2 | 1558.368866731154 | 0.0 | -5.2269362642144555e-14 | True | nan | axis | axis | nan | 7.831133268846088 | 5.2269362642144555e-14 | 0.0050000850905670335 | nan | 2 | concrete_controls | sweep_continuation |
| 201 | 135.0 | 1115.7 | 1111.774234402984 | -1101.6 | -1094.8529291183866 | True | True | IV | IV | True | 3.9257655970161522 | 6.747070881613354 | 0.0035186569839707376 | 0.006124792013084018 | 2 | concrete_controls | sweep_continuation |
| 201 | 180.0 | 0.0 | 1.3944016202513484e-13 | -1568.3 | -1559.7057881743274 | nan | True | axis | axis | nan | 1.3944016202513484e-13 | 8.594211825672573 | nan | 0.005479953979259436 | 2 | concrete_controls | sweep_continuation |
| 201 | 225.0 | -1115.7 | -1111.7742344029841 | -1101.6 | -1094.8529291183872 | True | True | III | III | True | 3.925765597015925 | 6.747070881612672 | 0.0035186569839705337 | 0.0061247920130833985 | 2 | concrete_controls | sweep_continuation |
| 201 | 270.0 | -1566.2 | -1558.3688667311542 | 0.0 | -1.4923392284757657e-13 | True | nan | axis | axis | nan | 7.831133268845861 | 1.4923392284757657e-13 | 0.005000085090566889 | nan | 2 | concrete_controls | sweep_continuation |
| 201 | 315.0 | -1115.7 | -1111.7742344029848 | 1101.6 | 1094.8529291183872 | True | True | II | II | True | 3.9257655970152427 | 6.747070881612672 | 0.0035186569839699227 | 0.0061247920130833985 | 2 | concrete_controls | sweep_continuation |
| 201 | 360.0 | 0.0 | -3.130985086287058e-13 | 1568.3 | 1559.7057881743274 | nan | True | axis | axis | nan | 3.130985086287058e-13 | 8.594211825672573 | nan | 0.005479953979259436 | 2 | concrete_controls | sweep_continuation |
| 202 | 0.0 | 0.0 | 3.6854341941513704e-14 | 874.3 | 870.9096337319562 | nan | True | axis | axis | nan | 3.6854341941513704e-14 | 3.390366268043749 | nan | 0.003877806551576975 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 202 | 45.0 | 617.0 | 614.2703112149964 | 619.2 | 616.8319668537008 | True | True | I | I | True | 2.7296887850036455 | 2.36803314629924 | 0.0044241309319345955 | 0.00382434293652978 | 2 | concrete_controls | sweep_continuation |
| 202 | 90.0 | 875.7 | 872.0725895825865 | 0.0 | 3.254582927666773e-15 | True | nan | axis | axis | nan | 3.6274104174135573 | 3.254582927666773e-15 | 0.004142298067161765 | nan | 2 | concrete_controls | sweep_continuation |
| 202 | 135.0 | 617.0 | 614.2703112149964 | -619.2 | -616.8319668537008 | True | True | IV | IV | True | 2.7296887850036455 | 2.36803314629924 | 0.0044241309319345955 | 0.00382434293652978 | 2 | concrete_controls | sweep_continuation |
| 202 | 180.0 | 0.0 | 8.015936146318722e-14 | -874.3 | -870.9096337319563 | nan | True | axis | axis | nan | 8.015936146318722e-14 | 3.3903662680436355 | nan | 0.003877806551576845 | 2 | concrete_controls | sweep_continuation |
| 202 | 225.0 | -617.0 | -614.2703112149962 | -619.2 | -616.8319668537008 | True | True | III | III | True | 2.729688785003759 | 2.36803314629924 | 0.00442413093193478 | 0.00382434293652978 | 2 | concrete_controls | sweep_continuation |
| 202 | 270.0 | -875.7 | -872.0725895825864 | 0.0 | -1.7247348091343383e-13 | True | nan | axis | axis | nan | 3.627410417413671 | 1.7247348091343383e-13 | 0.004142298067161894 | nan | 2 | concrete_controls | sweep_continuation |
| 202 | 315.0 | -617.0 | -614.2703112149965 | 619.2 | 616.8319668537008 | True | True | II | II | True | 2.729688785003532 | 2.36803314629924 | 0.004424130931934412 | 0.00382434293652978 | 2 | concrete_controls | sweep_continuation |
| 202 | 360.0 | 0.0 | -2.0938194054585198e-13 | 874.3 | 870.9096337319563 | nan | True | axis | axis | nan | 2.0938194054585198e-13 | 3.3903662680436355 | nan | 0.003877806551576845 | 2 | concrete_controls | sweep_continuation |

## Contribution study (cases A-D)

| mapping | gamma_c | gamma_s | gamma_p | gamma_E | gamma_u | max_rel_err_Mx | max_rel_err_My | mean_rel_force_strain_curvature | mean_rel_moment_transform | dominant_mismatch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| case_a_baseline | 1.5 | 1.15 | 1.15 | 1.0 | 1.0 | 0.5052710127545373 | 0.287739226470542 | 0.49426824671731673 | 0.44210516200945554 | largest mismatch appears already present in constitutive/equilibrium response |
| case_b_manual_strength | 1.9 | 1.5 | 1.5 | 1.0 | 1.0 | 0.14530651526963156 | 0.043809329162606256 | 0.5222545152600112 | 0.37673631038164573 | largest mismatch appears already present in constitutive/equilibrium response |
| case_c_manual_strength_plus_fe | 1.9 | 1.5 | 1.5 | 1.5 | 1.0 | 0.07473616156367238 | 0.03879934742490081 | 0.5331575511499034 | 0.3509714579539489 | largest mismatch appears already present in constitutive/equilibrium response |
| case_d_manual_strength_plus_fe_fu | 1.9 | 1.5 | 1.5 | 1.5 | 1.5 | 0.07473616156367238 | 0.03879934742490081 | 0.5331575511499034 | 0.3509714579539489 | largest mismatch appears already present in constitutive/equilibrium response |

## Type-6 prestress mapping study (Snit A-D, benchmark-only)

| mapping | family | max_rel_err_Mx | max_rel_err_My | max_rel_err_strain_prestressed | max_rel_err_compress_force | max_rel_err_kappa | delta_refined_minus_baseline_max_rel_err_Mx | delta_refined_minus_baseline_max_rel_err_My | delta_refined_minus_baseline_max_rel_err_strain_prestressed | delta_refined_minus_baseline_max_rel_err_compress_force | delta_refined_minus_baseline_max_rel_err_kappa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | snit_a | 0.014991720972103963 | 0.0063159015242715225 | 2.0160030930471287 | 1.8031324908629793 | 0.006461036076105418 | 0.007427895725931808 | -0.0062387189118689925 | 0.013011987315274975 | -0.059984050170085235 | 0.02204554612801725 |
| refined | snit_a | 0.02241961669803577 | 7.718261240252993e-05 | 2.0290150803624036 | 1.743148440692894 | 0.028506582204122666 | 0.007427895725931808 | -0.0062387189118689925 | 0.013011987315274975 | -0.059984050170085235 | 0.02204554612801725 |
| baseline | snit_b | 0.01539127947362884 | 0.005885381437245393 | 2.022349650925316 | 1.4649749670265655 | 0.01676810600236751 | 0.007479452822043332 | -0.004849516507998534 | 0.0005569727834089377 | -0.05522388997296446 | 0.009263010209352072 |
| refined | snit_b | 0.022870732295672172 | 0.0010358649292468588 | 2.022906623708725 | 1.409751077053601 | 0.026031116211719583 | 0.007479452822043332 | -0.004849516507998534 | 0.0005569727834089377 | -0.05522388997296446 | 0.009263010209352072 |
| baseline | snit_c | 0.01544923061090369 | 0.005866392485544645 | 2.020664219045916 | 1.4592662917457229 | 0.015128705477443249 | 0.007373837266845193 | -0.004820496043268797 | 0.003762706001971594 | -0.05503791645455469 | 0.011775653253308602 |
| refined | snit_c | 0.022823067877748883 | 0.0010458964422758478 | 2.0244269250478877 | 1.4042283752911682 | 0.02690435873075185 | 0.007373837266845193 | -0.004820496043268797 | 0.003762706001971594 | -0.05503791645455469 | 0.011775653253308602 |
| baseline | snit_d | 0.014344290636897765 | 0.005866392485544505 | 2.0054385067371756 | 1.4592662917457229 | 0.005985823876204029 | 0.009612267109583615 | -0.004820496043268657 | 0.011950745678348085 | -0.05503791645455469 | 0.021896779435906497 |
| refined | snit_d | 0.02395655774648138 | 0.0010458964422758478 | 2.0173892524155237 | 1.4042283752911682 | 0.027882603312110527 | 0.009612267109583615 | -0.004820496043268657 | 0.011950745678348085 | -0.05503791645455469 | 0.021896779435906497 |

## Output-semantics candidates and winners

Chosen winners (majority across fixture families):

- strain_mild: `strain_mild:max_tension`
- compress_force: `compress_force:concrete_plus_all_comp_steel`
- lever_L: `lever:total_comp_to_tension:L`
- lever_DX: `lever:total_comp_to_tension:DX`


## Semantic gap (before vs semantic-aligned benchmark comparison)

| group | max_rel_before | max_rel_after | delta |
| --- | --- | --- | --- |
| moments | 0.07473616156367238 | 0.07473616156367238 | 0.0 |
| strains | 2.022349650925316 | 2.022349650925316 | 0.0 |
| compression force | 1.8031324908629793 | 1.8031324908629793 | 0.0 |
| lever-arms | 1.9925804260392563 | 2.4179749321480672 | 0.4253945061088109 |

## Semantic-versus-constitutive conclusion for unresolved outputs

| output | cross_family_winner | family_winners | status | max_rel_error_reported | max_rel_error_semantic_aligned |
| --- | --- | --- | --- | --- | --- |
| strain_prestressed |  | strain_prestressed:governing_abs_signed, strain_prestressed:incremental_max_compression | family-specific winners only | 2.022349650925316 | 2.022349650925316 |
| lever_DY |  | lever:moment_over_compression:DY_from_Mx, lever:total_comp_to_tension:DY | family-specific winners only | 0.7568992182552471 | 2.4179749321480672 |

## Sub-1% readiness by fixture family and output group (after semantic alignment)

| fixture_family | output_group | max_rel_err | band |
| --- | --- | --- | --- |
| annular | compression force | 0.002895597231681938 | <1% |
| annular | curvature | 0.006173773436443466 | <1% |
| annular | lever-arms | 2.4179749321480672 | >5% |
| annular | moments | 0.006124792013084018 | <1% |
| annular | strains | 2.0127595977897648 | >5% |
| annular | warnings | nan | match=1.000 |
| snit | compression force | 1.8031324908629793 | >5% |
| snit | curvature | 0.01676810600236751 | 1-5% |
| snit | lever-arms | 1.4029629221542417 | >5% |
| snit | moments | 0.01544923061090369 | 1-5% |
| snit | strains | 2.022349650925316 | >5% |
| snit | warnings | nan | N/A |
| tbeam | compression force | nan | N/A |
| tbeam | curvature | nan | N/A |
| tbeam | lever-arms | nan | N/A |
| tbeam | moments | 0.07473616156367238 | >5% |
| tbeam | strains | nan | N/A |
| tbeam | warnings | nan | N/A |

Conclusion: largest mismatch appears already present in constitutive/equilibrium response

## Error delta vs prior artifact

- prior max_rel_err_Mx: 0.074736
- current max_rel_err_Mx: 0.074736
- delta max_rel_err_Mx: +0.000000
- prior max_rel_err_My: 0.038799
- current max_rel_err_My: 0.038799
- delta max_rel_err_My: +0.000000
