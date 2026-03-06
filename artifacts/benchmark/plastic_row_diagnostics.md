# Plastic Row Diagnostics

Six embedded manual rows with signed and intermediate-quantity decomposition.

| load_case | V_deg | Mx_ref | Mx_calc | rel_Mx | My_ref | My_calc | rel_My | kappa_ref | kappa_calc | rel_kappa | compress_force_ref | compress_force_calc | rel_compress_force | lever_DX_ref | lever_DX_calc | rel_lever_DX | sign_agreement_Mx | sign_agreement_My | quadrant_agreement | candidate_count | pivot | selection_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2.0 | 544.3 | 509.53932989633347 | 0.06386307202584326 | 921.8 | 903.2711600960753 | 0.020100715886227683 | 0.006404 | 0.0051691718874041 | 0.19282137923108994 | 3933.8 | 2588.1126900832314 | 0.34208330619674837 | 0.611 | 0.42794174811790736 | 0.2996043402325575 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 3 | 5.0 | 619.0 | 586.4309265454029 | 0.05261562755185308 | 917.4 | 894.7625570269622 | 0.024675651812772797 | 0.005805 | 0.0049599605303650976 | 0.14557096806802802 | 3775.6 | 2581.9610860988646 | 0.3161454904918782 | 0.7476 | 0.45487832394620953 | 0.39154852334642926 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 3 | 8.0 | 698.8 | 661.0897377654877 | 0.05396431344377826 | 905.8 | 884.3046102184842 | 0.023730834380123394 | 0.005229 | 0.004785241282759105 | 0.08486492966932395 | 3638.1 | 2592.0619715370904 | 0.28752316551576634 | 0.8627 | 0.4798565847022968 | 0.4437735195290405 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 4 | 5.0 | 437.0 | 404.34029739667517 | 0.07473616156367238 | 894.2 | 869.5729652822912 | 0.0275408574342528 | 0.007745 | 0.004446170312630075 | 0.42593023723304396 | 4986.2 | 3354.013911327899 | 0.3273406780057159 | 0.5244 | 0.3938145268592954 | 0.24901882749943663 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 4 | 10.0 | 561.4 | 520.5161012617297 | 0.07282489978316765 | 869.8 | 846.6413277323888 | 0.02662528428099691 | 0.006482 | 0.004200251606795678 | 0.3520130196242397 | 4506.2 | 3357.3935185591963 | 0.25493907981021785 | 0.6762 | 0.4261532596797349 | 0.3697822246676503 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |
| 4 | 15.0 | 682.9 | 645.3570570934979 | 0.05497575473202819 | 837.7 | 805.1977866621606 | 0.03879934742490081 | 0.005153 | 0.0040279169710343106 | 0.21833553832052963 | 4126.7 | 3337.4406418499684 | 0.19125678099935334 | 0.781 | 0.460628802608119 | 0.4102063987091946 | True | True | True | 2 | concrete_controls | single_min_abs_kappa |

## Grouped discrepancy summary

| group | mean_rel |
| --- | --- |
| force/strain/curvature level | 0.37336714650357444 |
| moment/transformation level | 0.4569911409625945 |

Conclusion: largest mismatch appears already present in constitutive/equilibrium response
