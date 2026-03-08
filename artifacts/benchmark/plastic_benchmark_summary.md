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
| 3 | 16 | 3 | 0.048718259165525524 | 0.03647336453900607 | 6.971702799874861e-05 | 3.956754669017799e-05 | True | True | True | 2 | nan |
| 4 | 15 | 3 | 0.06316567318879152 | 0.04535012364078739 | 0.00011251455858352603 | 5.4136473249119476e-05 | True | True | True | 2 | nan |
| 101 | 5 | 3 | 46.80167134819749 | 25.613826079800674 | 0.01018401761428268 | 0.003972121158706141 | True | True | True | 2 | nan |
| 102 | 5 | 3 | 44.914988082660784 | 24.44899690081911 | 0.010513315875347781 | 0.0037450212763953054 | True | True | True | 2 | nan |
| 103 | 5 | 5 | 31.697059128413002 | 24.354257846668588 | 0.010566743050442712 | 0.003729709615404543 | True | True | True | 2 | nan |
| 104 | 5 | 3 | 17.31191030522541 | 24.354257846668588 | 0.009496906196294591 | 0.003729709615404543 | True | True | True | 2 | nan |
| 201 | 9 | 9 | 0.3173633786834671 | 1.5893348515382968 | 0.0002844522530101883 | 0.001013412517718738 | True | True | True | 2 | 1.0 |
| 202 | 9 | 9 | 0.7384464734489029 | 0.348204921917727 | 0.0011384064992120775 | 0.000562346450125528 | True | True | True | 2 | 1.0 |

## Referenced rows

Signed errors (abs/rel) are primary benchmark metrics. Magnitude-only errors remain in CSV as secondary diagnostics.

| load_case | V_deg | Mx_ref | Mx_calc | My_ref | My_calc | sign_agreement_Mx | sign_agreement_My | quadrant_expected | quadrant_calc | quadrant_agreement | abs_err_Mx | abs_err_My | rel_err_Mx | rel_err_My | candidate_count | pivot | selected_branch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2.0 | 544.3 | 544.3200679101092 | 921.8 | 921.763526635461 | True | True | I | I | True | 0.020067910109219156 | 0.03647336453900607 | 3.686920835792607e-05 | 3.956754669017799e-05 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 3 | 5.0 | 619.0 | 619.0024192066255 | 917.4 | 917.3824451398692 | True | True | I | I | True | 0.0024192066255182 | 0.017554860130758243 | 3.908249798898546e-06 | 1.913544814776351e-05 | 2 | concrete_controls | sweep_continuation |
| 3 | 8.0 | 698.8 | 698.8487182591655 | 905.8 | 905.8172974562534 | True | True | I | I | True | 0.048718259165525524 | 0.01729745625345913 | 6.971702799874861e-05 | 1.9096330595560975e-05 | 2 | concrete_controls | sweep_continuation |
| 4 | 5.0 | 437.0 | 437.0010829423129 | 894.2 | 894.2301231850167 | True | True | I | I | True | 0.0010829423129052884 | 0.030123185016691423 | 2.4781288624834973e-06 | 3.36873015172125e-05 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 4 | 10.0 | 561.4 | 561.3368343268112 | 869.8 | 869.8052994572581 | True | True | I | I | True | 0.06316567318879152 | 0.0052994572581610555 | 0.00011251455858352603 | 6.0927308095666316e-06 | 2 | concrete_controls | sweep_continuation |
| 4 | 15.0 | 682.9 | 682.9452481894003 | 837.7 | 837.7453501236408 | True | True | I | I | True | 0.04524818940035402 | 0.04535012364078739 | 6.625888036367553e-05 | 5.4136473249119476e-05 | 2 | concrete_controls | sweep_continuation |
| 101 | 0.0 | -4595.6 | -4642.401671348194 | 6448.4 | 6474.0138260798 | True | True | II | II | True | 46.80167134819385 | 25.613826079800674 | 0.010184017614281888 | 0.003972121158706141 | 1 | concrete_controls | sweep_unique |
| 101 | 90.0 | 2714.6 | 2698.348260679407 | 0.0 | 1.3877787807814457e-12 | True | nan | axis | axis | nan | 16.25173932059306 | 1.3877787807814457e-12 | 0.0059867897003584546 | nan | 2 | concrete_controls | sweep_continuation |
| 101 | 180.0 | -4595.6 | -4642.401671348198 | -6448.4 | -6474.0138260798 | True | True | III | III | True | 46.80167134819749 | 25.613826079800674 | 0.01018401761428268 | 0.003972121158706141 | 1 | concrete_controls | sweep_unique |
| 102 | 0.0 | 4272.2 | 4317.114988082661 | 6528.4 | 6552.848996900819 | True | True | I | I | True | 44.914988082660784 | 24.44899690081911 | 0.010513315875347781 | 0.0037450212763953054 | 1 | concrete_controls | sweep_unique |
| 102 | 90.0 | 11308.3 | 11317.082079517508 | 0.0 | 2.0539125955565396e-12 | True | nan | axis | axis | nan | 8.782079517508464 | 2.0539125955565396e-12 | 0.0007766047520412851 | nan | 2 | concrete_controls | sweep_continuation |
| 102 | 180.0 | 4272.2 | 4317.114988082655 | -6528.4 | -6552.848996900819 | True | True | IV | IV | True | 44.91498808265533 | 24.44899690081911 | 0.010513315875346502 | 0.0037450212763953054 | 1 | concrete_controls | sweep_unique |
| 103 | 0.0 | 2999.7 | 3031.39705912841 | 6529.8 | 6554.154257846669 | True | True | I | I | True | 31.697059128410274 | 24.354257846668588 | 0.010566743050441803 | 0.003729709615404543 | 1 | concrete_controls | sweep_unique |
| 103 | 90.0 | 9869.1 | 9876.466505427212 | 0.0 | 1.942890293094024e-12 | True | nan | axis | axis | nan | 7.36650542721145 | 1.942890293094024e-12 | 0.0007464211961791298 | nan | 2 | concrete_controls | sweep_continuation |
| 103 | 180.0 | 2999.7 | 3031.397059128413 | -6529.8 | -6554.154257846669 | True | True | IV | IV | True | 31.697059128413002 | 24.354257846668588 | 0.010566743050442712 | 0.003729709615404543 | 1 | concrete_controls | sweep_unique |
| 103 | 270.0 | -4223.3 | -4208.724095274303 | 0.0 | -2.189141230487035e-12 | True | nan | axis | axis | nan | 14.575904725697 | 2.189141230487035e-12 | 0.0034513069698333056 | nan | 2 | concrete_controls | sweep_continuation |
| 103 | 360.0 | 2999.7 | 3031.3970591284083 | 6529.8 | 6554.154257846669 | True | True | I | I | True | 31.697059128408455 | 24.354257846668588 | 0.010566743050441196 | 0.003729709615404543 | 1 | concrete_controls | sweep_unique |
| 104 | 0.0 | -1822.9 | -1840.2119103052255 | 6529.8 | 6554.154257846669 | True | True | II | II | True | 17.31191030522541 | 24.354257846668588 | 0.009496906196294591 | 0.003729709615404543 | 1 | concrete_controls | sweep_unique |
| 104 | 90.0 | 4627.3 | 4631.736834380787 | 0.0 | 1.7208456881689926e-12 | True | nan | axis | axis | nan | 4.436834380786422 | 1.7208456881689926e-12 | 0.0009588387138906969 | nan | 2 | concrete_controls | sweep_continuation |
| 104 | 180.0 | -1822.9 | -1840.2119103052232 | -6529.8 | -6554.154257846669 | True | True | III | III | True | 17.311910305223137 | 24.354257846668588 | 0.009496906196293344 | 0.003729709615404543 | 1 | concrete_controls | sweep_unique |
| 201 | 0.0 | 0.0 | 1.9081062389321048e-14 | 1568.3 | 1566.7106651484617 | nan | True | axis | axis | nan | 1.9081062389321048e-14 | 1.5893348515382968 | nan | 0.001013412517718738 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 201 | 45.0 | 1115.7 | 1116.017363378683 | 1101.6 | 1100.5726242426379 | True | True | I | I | True | 0.31736337868301234 | 1.0273757573620514 | 0.0002844522530097807 | 0.0009326214209895166 | 2 | concrete_controls | sweep_continuation |
| 201 | 90.0 | 1566.2 | 1566.0194606937537 | 0.0 | -4.821141075096581e-14 | True | nan | axis | axis | nan | 0.1805393062463736 | 4.821141075096581e-14 | 0.00011527219144832946 | nan | 2 | concrete_controls | sweep_continuation |
| 201 | 135.0 | 1115.7 | 1116.017363378683 | -1101.6 | -1100.5726242426379 | True | True | IV | IV | True | 0.31736337868301234 | 1.0273757573620514 | 0.0002844522530097807 | 0.0009326214209895166 | 2 | concrete_controls | sweep_continuation |
| 201 | 180.0 | 0.0 | 7.951221465910085e-14 | -1568.3 | -1566.7106651484617 | nan | True | axis | axis | nan | 7.951221465910085e-14 | 1.5893348515382968 | nan | 0.001013412517718738 | 2 | concrete_controls | sweep_continuation |
| 201 | 225.0 | -1115.7 | -1116.017363378683 | -1101.6 | -1100.5726242426383 | True | True | III | III | True | 0.31736337868301234 | 1.0273757573615967 | 0.0002844522530097807 | 0.0009326214209891038 | 2 | concrete_controls | sweep_continuation |
| 201 | 270.0 | -1566.2 | -1566.0194606937537 | 0.0 | -1.7554508435234567e-13 | True | nan | axis | axis | nan | 0.1805393062463736 | 1.7554508435234567e-13 | 0.00011527219144832946 | nan | 2 | concrete_controls | sweep_continuation |
| 201 | 315.0 | -1115.7 | -1116.0173633786835 | 1101.6 | 1100.572624242638 | True | True | II | II | True | 0.3173633786834671 | 1.027375757361824 | 0.0002844522530101883 | 0.0009326214209893103 | 2 | concrete_controls | sweep_continuation |
| 201 | 360.0 | 0.0 | -2.296492580690767e-13 | 1568.3 | 1566.7106651484617 | nan | True | axis | axis | nan | 2.296492580690767e-13 | 1.5893348515382968 | nan | 0.001013412517718738 | 2 | concrete_controls | sweep_continuation |
| 202 | 0.0 | 0.0 | 4.882133655845955e-14 | 874.3 | 874.2233575886175 | nan | True | axis | axis | nan | 4.882133655845955e-14 | 0.07664241138240868 | nan | 8.766145645934883e-05 | 2 | concrete_controls | sweep_seed_min_abs_kappa |
| 202 | 45.0 | 617.0 | 616.2976031899861 | 619.2 | 619.5482049219175 | True | True | I | I | True | 0.7023968100138518 | 0.34820492191749963 | 0.0011384064992120775 | 0.0005623464501251609 | 2 | concrete_controls | sweep_continuation |
| 202 | 90.0 | 875.7 | 874.9615535265513 | 0.0 | -1.6804822530089362e-14 | True | nan | axis | axis | nan | 0.7384464734487892 | 1.6804822530089362e-14 | 0.0008432642154262752 | nan | 2 | concrete_controls | sweep_continuation |
| 202 | 135.0 | 617.0 | 616.2976031899861 | -619.2 | -619.5482049219175 | True | True | IV | IV | True | 0.7023968100138518 | 0.34820492191749963 | 0.0011384064992120775 | 0.0005623464501251609 | 2 | concrete_controls | sweep_continuation |
| 202 | 180.0 | 0.0 | 3.964276873387676e-14 | -874.3 | -874.2233575886177 | nan | True | axis | axis | nan | 3.964276873387676e-14 | 0.076642411382295 | nan | 8.76614564592188e-05 | 2 | concrete_controls | sweep_continuation |
| 202 | 225.0 | -617.0 | -616.2976031899861 | -619.2 | -619.5482049219178 | True | True | III | III | True | 0.7023968100138518 | 0.348204921917727 | 0.0011384064992120775 | 0.000562346450125528 | 2 | concrete_controls | sweep_continuation |
| 202 | 270.0 | -875.7 | -874.9615535265511 | 0.0 | -1.3431189583539547e-13 | True | nan | axis | axis | nan | 0.7384464734489029 | 1.3431189583539547e-13 | 0.000843264215426405 | nan | 2 | concrete_controls | sweep_continuation |
| 202 | 315.0 | -617.0 | -616.2976031899863 | 619.2 | 619.5482049219175 | True | True | II | II | True | 0.7023968100137381 | 0.34820492191749963 | 0.0011384064992118932 | 0.0005623464501251609 | 2 | concrete_controls | sweep_continuation |
| 202 | 360.0 | 0.0 | -1.368799213332869e-13 | 874.3 | 874.2233575886174 | nan | True | axis | axis | nan | 1.368799213332869e-13 | 0.07664241138252237 | nan | 8.766145645947887e-05 | 2 | concrete_controls | sweep_continuation |

## Contribution study (cases A-D)

| mapping | gamma_c | gamma_s | gamma_p | gamma_E | gamma_u | max_rel_err_Mx | max_rel_err_My | mean_rel_force_strain_curvature | mean_rel_moment_transform | dominant_mismatch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| case_a_baseline | 1.5 | 1.15 | 1.15 | 1.0 | 1.0 | 0.4944897000059521 | 0.3285567559107331 | 0.6551514910132793 | 0.4174292934222179 | largest mismatch appears already present in constitutive/equilibrium response |
| case_b_manual_strength | 1.9 | 1.5 | 1.5 | 1.0 | 1.0 | 0.08478032450529795 | 0.02443691746026194 | 0.6757060374854993 | 0.20392525517133478 | largest mismatch appears already present in constitutive/equilibrium response |
| case_c_manual_strength_plus_fe | 1.9 | 1.5 | 1.5 | 1.5 | 1.0 | 0.0011256193420316049 | 0.0007582363712795589 | 0.6787650366555935 | 0.17690491414439613 | largest mismatch appears already present in constitutive/equilibrium response |
| case_d_manual_strength_plus_fe_fu | 1.9 | 1.5 | 1.5 | 1.5 | 1.5 | 0.00011251455858352603 | 5.4136473249119476e-05 | 0.5207763322849823 | 0.1768865083212662 | largest mismatch appears already present in constitutive/equilibrium response |

## Type-6 prestress mapping study (Snit A-D, benchmark-only)

| mapping | family | max_rel_err_Mx | max_rel_err_My | max_rel_err_strain_prestressed | max_rel_err_compress_force | max_rel_err_kappa | delta_refined_minus_baseline_max_rel_err_Mx | delta_refined_minus_baseline_max_rel_err_My | delta_refined_minus_baseline_max_rel_err_strain_prestressed | delta_refined_minus_baseline_max_rel_err_compress_force | delta_refined_minus_baseline_max_rel_err_kappa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | snit_a | 0.01018401761428268 | 0.003972121158706141 | 0.011183320400070586 | 0.0002824346720739666 | 0.0047956443531201095 | 0.016918140811793114 | -0.001511184253065474 | 0.012895489089203975 | 1.7318331568146907 | 0.013646590865892724 |
| refined | snit_a | 0.027102158426075794 | 0.0024609369056406666 | 0.02407880948927456 | 1.7321155914867647 | 0.018442235219012833 | 0.016918140811793114 | -0.001511184253065474 | 0.012895489089203975 | 1.7318331568146907 | 0.013646590865892724 |
| baseline | snit_b | 0.010513315875347781 | 0.0037450212763953054 | 0.01325196346807663 | 0.000678907122670108 | 0.0035976880592358037 | 0.01710567501482288 | -0.0025987612161223307 | 0.0011027420442914597 | 0.001531393090314439 | 0.013943935513588931 |
| refined | snit_b | 0.027618990890170662 | 0.0011462600602729744 | 0.01435470551236809 | 0.0022103002129845468 | 0.017541623572824735 | 0.01710567501482288 | -0.0025987612161223307 | 0.0011027420442914597 | 0.001531393090314439 | 0.013943935513588931 |
| baseline | snit_c | 0.010566743050442712 | 0.003729709615404543 | 0.5027932566454604 | 0.0009262566290863856 | 0.0029254952840037035 | 0.017008932818037118 | -0.0025971241389157558 | -0.002623595595254602 | 0.005497826800633912 | 0.0145133537863632 |
| refined | snit_c | 0.02757567586847983 | 0.0011325854764887874 | 0.5001696610502058 | 0.006424083429720298 | 0.017438849070366903 | 0.017008932818037118 | -0.0025971241389157558 | -0.002623595595254602 | 0.005497826800633912 | 0.0145133537863632 |
| baseline | snit_d | 0.009496906196294591 | 0.003729709615404543 | 0.0013551702961003566 | 0.00022669366505645986 | 0.0035267671616845066 | 0.01917809020287658 | -0.0025971241389157558 | 0.011097179658275015 | -0.00019083673732827927 | 0.014537490902520139 |
| refined | snit_d | 0.02867499639917117 | 0.0011325854764887874 | 0.012452349954375372 | 3.58569277281806e-05 | 0.018064258064204645 | 0.01917809020287658 | -0.0025971241389157558 | 0.011097179658275015 | -0.00019083673732827927 | 0.014537490902520139 |

## Output-semantics candidates and winners

Chosen winners (majority across fixture families):

- strain_mild: `strain_mild:max_tension`
- lever_L: `lever:total_comp_to_tension:L`
- lever_DX: `lever:total_comp_to_tension:DX`


## Semantic gap (before vs semantic-aligned benchmark comparison)

| group | max_rel_before | max_rel_after | delta |
| --- | --- | --- | --- |
| moments | 0.010566743050442712 | 0.010566743050442712 | 0.0 |
| strains | 2.5172367057585783 | 2.5172367057585783 | 0.0 |
| compression force | 0.0009262566290863856 | 1.7945786894858 | 1.7936524328567136 |
| lever-arms | 2.001441617603607 | 2.42050482258475 | 0.4190632049811427 |

## Semantic-versus-constitutive conclusion for unresolved outputs

| output | cross_family_winner | family_winners | status | max_rel_error_reported | max_rel_error_semantic_aligned |
| --- | --- | --- | --- | --- | --- |
| strain_prestressed |  | strain_prestressed:incremental_max_compression, strain_prestressed:tensile_side_total | family-specific winners only | 0.5027932566454604 | 0.5027932566454604 |
| lever_DY |  | lever:moment_over_compression:DY_from_Mx, lever:total_comp_to_tension:DY | family-specific winners only | 0.2548588073980012 | 2.42050482258475 |

## Sub-1% readiness by fixture family and output group (after semantic alignment)

| fixture_family | output_group | max_rel_err | band |
| --- | --- | --- | --- |
| annular | compression force | 0.0007635971565132672 | <1% |
| annular | curvature | 0.001495696648268048 | <1% |
| annular | lever-arms | 2.42050482258475 | >5% |
| annular | moments | 0.0011384064992120775 | <1% |
| annular | strains | 1.4514925034569215 | >5% |
| annular | warnings | nan | match=1.000 |
| snit | compression force | 1.7945786894858 | >5% |
| snit | curvature | 0.0047956443531201095 | <1% |
| snit | lever-arms | 1.4047534180200494 | >5% |
| snit | moments | 0.010566743050442712 | 1-5% |
| snit | strains | 2.5172367057585783 | >5% |
| snit | warnings | nan | N/A |
| tbeam | compression force | nan | N/A |
| tbeam | curvature | nan | N/A |
| tbeam | lever-arms | nan | N/A |
| tbeam | moments | 0.00011251455858352603 | <1% |
| tbeam | strains | nan | N/A |
| tbeam | warnings | nan | N/A |

Conclusion: largest mismatch appears already present in constitutive/equilibrium response

## Error delta vs prior artifact

- prior max_rel_err_Mx: 0.010567
- current max_rel_err_Mx: 0.010567
- delta max_rel_err_Mx: +0.000000
- prior max_rel_err_My: 0.003972
- current max_rel_err_My: 0.003972
- delta max_rel_err_My: +0.000000
