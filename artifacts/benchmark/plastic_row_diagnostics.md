# Plastic Row Diagnostics

Six embedded manual rows with signed and intermediate-quantity decomposition.

| load_case | V_deg | Mx_ref | Mx_calc | rel_Mx | My_ref | My_calc | rel_My | kappa_ref | kappa_calc | rel_kappa | compress_force_ref | compress_force_calc | rel_compress_force | lever_DX_ref | lever_DX_calc | rel_lever_DX | sign_agreement_Mx | sign_agreement_My | quadrant_agreement | candidate_count | pivot | selection_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2.0 | 544.3 | 544.3200679101092 | 3.686920835792607e-05 | 921.8 | 921.763526635461 | 3.956754669017799e-05 | 0.006404 | 0.005333645439842746 | 0.1671384385005081 | 3933.8 | 1647.3158998318117 | 0.5812405562479507 | 0.611 | 1.0137419512548271 | 0.6591521297133014 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 3 | 5.0 | 619.0 | 619.0024192066255 | 3.908249798898546e-06 | 917.4 | 917.3824451398692 | 1.913544814776351e-05 | 0.005805 | 0.005106092784931947 | 0.12039745306943206 | 3775.6 | 1638.4526689212976 | 0.566041776427244 | 0.7476 | 1.0060803278744554 | 0.34574682701238013 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 3 | 8.0 | 698.8 | 698.8487182591655 | 6.971702799874861e-05 | 905.8 | 905.8172974562534 | 1.9096330595560975e-05 | 0.005229 | 0.004922960389452992 | 0.05852736862631632 | 3638.1 | 2165.8713264873036 | 0.4046696554555115 | 0.8627 | 0.9149779305100981 | 0.06059804162524412 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 4 | 5.0 | 437.0 | 437.0010829423129 | 2.4781288624834973e-06 | 894.2 | 894.2301231850167 | 3.36873015172125e-05 | 0.007745 | 0.0046200769256144105 | 0.40347618778380756 | 4986.2 | 2470.1859919947574 | 0.504595485140035 | 0.5244 | 0.5397090465799528 | 0.029193452669627768 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 4 | 10.0 | 561.4 | 561.3368343268112 | 0.00011251455858352603 | 869.8 | 869.8052994572581 | 6.0927308095666316e-06 | 0.006482 | 0.004363411592030858 | 0.3268417784586767 | 4506.2 | 2456.135392876771 | 0.4549431021976896 | 0.6762 | 0.5204762228965496 | 0.23029248314618517 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 4 | 15.0 | 682.9 | 682.9452481894003 | 6.625888036367553e-05 | 837.7 | 837.7453501236408 | 5.4136473249119476e-05 | 0.005153 | 0.004170407354704841 | 0.19068361057542374 | 4126.7 | 2438.304071584468 | 0.40913948879626133 | 0.781 | 0.4979559171713357 | 0.36241239798804653 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |

## Grouped discrepancy summary

| group | mean_rel |
| --- | --- |
| force/strain/curvature level | 0.4409335003853533 |
| moment/transformation level | 0.18338846781569204 |

Conclusion: largest mismatch appears already present in constitutive/equilibrium response
