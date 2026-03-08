# Plastic DX/DY Sign and Transformation Study

COMPRESS FORCE is no longer the main blocker on this branch; this study isolates lever-arm sign/transformation semantics (DX, DY, L).

## Best candidate per family

| output | fixture_family | best_candidate | cross_family_winner | cross_family_winner_exists | max_rel_error | median_rel_error |
| --- | --- | --- | --- | --- | --- | --- |
| lever_DX | annular | B_centroid_without_explicit_sign_flip |  | False | 0.0014416176036070511 | 0.0002125861677639885 |
| lever_DX | snit | A_current_centroid_with_explicit_sign_flip |  | False | 0.00010136653969071949 | 7.170748223651667e-05 |
| lever_DX | tbeam | A_current_centroid_with_explicit_sign_flip |  | False | 0.46854915654070173 | 0.28261697637774774 |
| lever_DY | annular | A_current_centroid_with_explicit_sign_flip |  | False | 0.002499064091371146 | 0.0006937012685839397 |
| lever_DY | snit | A_current_centroid_with_explicit_sign_flip |  | False | 0.2548588073980012 | 0.07010418054351127 |
| lever_DY | tbeam | G_M_over_compress_surrogate_global |  | False | 0.612124108852428 | 0.3113884806132683 |
| lever_L | annular | A_current_centroid_with_explicit_sign_flip |  | False | 0.001898238768191539 | 0.000450144134676631 |
| lever_L | snit | A_current_centroid_with_explicit_sign_flip |  | False | 0.2548588073980012 | 0.07010418054351127 |
| lever_L | tbeam | H_M_over_compress_surrogate_local_then_global |  | False | 0.4761540769569567 | 0.3435284908913634 |

## Annular opposite-angle sign checks (0↔180, 90↔270, 45↔225)

| fixture | output | candidate | pair | ref_opposite_sign | calc_opposite_sign | match_ref_pattern |
| --- | --- | --- | --- | --- | --- | --- |
| section0 | lever_DX | A_current_centroid_with_explicit_sign_flip | 0_vs_180 | True | True | True |
| section0 | lever_DX | A_current_centroid_with_explicit_sign_flip | 45_vs_225 | True | True | True |
| section0 | lever_DX | A_current_centroid_with_explicit_sign_flip | 90_vs_270 | True | True | True |
| section0 | lever_DX | B_centroid_without_explicit_sign_flip | 0_vs_180 | True | True | True |
| section0 | lever_DX | B_centroid_without_explicit_sign_flip | 45_vs_225 | True | True | True |
| section0 | lever_DX | B_centroid_without_explicit_sign_flip | 90_vs_270 | True | True | True |
| section0 | lever_DX | C_comp_to_tens_local_then_global | 0_vs_180 | True | True | True |
| section0 | lever_DX | C_comp_to_tens_local_then_global | 45_vs_225 | True | True | True |
| section0 | lever_DX | C_comp_to_tens_local_then_global | 90_vs_270 | True | True | True |
| section0 | lever_DX | D_tens_to_comp_local_then_global | 0_vs_180 | True | True | True |
| section0 | lever_DX | D_tens_to_comp_local_then_global | 45_vs_225 | True | True | True |
| section0 | lever_DX | D_tens_to_comp_local_then_global | 90_vs_270 | True | True | True |
| section0 | lever_DX | E_comp_to_tens_direct_global_no_flip | 0_vs_180 | True | True | True |
| section0 | lever_DX | E_comp_to_tens_direct_global_no_flip | 45_vs_225 | True | True | True |
| section0 | lever_DX | E_comp_to_tens_direct_global_no_flip | 90_vs_270 | True | True | True |
| section0 | lever_DX | F_comp_to_tens_direct_global_with_flip | 0_vs_180 | True | True | True |
| section0 | lever_DX | F_comp_to_tens_direct_global_with_flip | 45_vs_225 | True | True | True |
| section0 | lever_DX | F_comp_to_tens_direct_global_with_flip | 90_vs_270 | True | True | True |
| section0 | lever_DX | G_M_over_compress_surrogate_global | 0_vs_180 | True | True | True |
| section0 | lever_DX | G_M_over_compress_surrogate_global | 45_vs_225 | True | True | True |
| section0 | lever_DX | G_M_over_compress_surrogate_global | 90_vs_270 | True | False | False |
| section0 | lever_DX | H_M_over_compress_surrogate_local_then_global | 0_vs_180 | True | True | True |
| section0 | lever_DX | H_M_over_compress_surrogate_local_then_global | 45_vs_225 | True | True | True |
| section0 | lever_DX | H_M_over_compress_surrogate_local_then_global | 90_vs_270 | True | True | True |
| section0 | lever_DY | A_current_centroid_with_explicit_sign_flip | 0_vs_180 | True | False | False |
| section0 | lever_DY | A_current_centroid_with_explicit_sign_flip | 45_vs_225 | True | True | True |
| section0 | lever_DY | A_current_centroid_with_explicit_sign_flip | 90_vs_270 | True | True | True |
| section0 | lever_DY | B_centroid_without_explicit_sign_flip | 0_vs_180 | True | False | False |
| section0 | lever_DY | B_centroid_without_explicit_sign_flip | 45_vs_225 | True | True | True |
| section0 | lever_DY | B_centroid_without_explicit_sign_flip | 90_vs_270 | True | True | True |
| section0 | lever_DY | C_comp_to_tens_local_then_global | 0_vs_180 | True | False | False |
| section0 | lever_DY | C_comp_to_tens_local_then_global | 45_vs_225 | True | True | True |
| section0 | lever_DY | C_comp_to_tens_local_then_global | 90_vs_270 | True | True | True |
| section0 | lever_DY | D_tens_to_comp_local_then_global | 0_vs_180 | True | False | False |
| section0 | lever_DY | D_tens_to_comp_local_then_global | 45_vs_225 | True | True | True |
| section0 | lever_DY | D_tens_to_comp_local_then_global | 90_vs_270 | True | True | True |
| section0 | lever_DY | E_comp_to_tens_direct_global_no_flip | 0_vs_180 | True | False | False |
| section0 | lever_DY | E_comp_to_tens_direct_global_no_flip | 45_vs_225 | True | True | True |
| section0 | lever_DY | E_comp_to_tens_direct_global_no_flip | 90_vs_270 | True | True | True |
| section0 | lever_DY | F_comp_to_tens_direct_global_with_flip | 0_vs_180 | True | False | False |
| section0 | lever_DY | F_comp_to_tens_direct_global_with_flip | 45_vs_225 | True | True | True |
| section0 | lever_DY | F_comp_to_tens_direct_global_with_flip | 90_vs_270 | True | True | True |
| section0 | lever_DY | G_M_over_compress_surrogate_global | 0_vs_180 | True | False | False |
| section0 | lever_DY | G_M_over_compress_surrogate_global | 45_vs_225 | True | True | True |
| section0 | lever_DY | G_M_over_compress_surrogate_global | 90_vs_270 | True | True | True |
| section0 | lever_DY | H_M_over_compress_surrogate_local_then_global | 0_vs_180 | True | False | False |
| section0 | lever_DY | H_M_over_compress_surrogate_local_then_global | 45_vs_225 | True | True | True |
| section0 | lever_DY | H_M_over_compress_surrogate_local_then_global | 90_vs_270 | True | True | True |
| section0 | lever_L | A_current_centroid_with_explicit_sign_flip | 0_vs_180 | False | False | True |
| section0 | lever_L | A_current_centroid_with_explicit_sign_flip | 45_vs_225 | False | False | True |
| section0 | lever_L | A_current_centroid_with_explicit_sign_flip | 90_vs_270 | False | False | True |
| section0 | lever_L | B_centroid_without_explicit_sign_flip | 0_vs_180 | False | False | True |
| section0 | lever_L | B_centroid_without_explicit_sign_flip | 45_vs_225 | False | False | True |
| section0 | lever_L | B_centroid_without_explicit_sign_flip | 90_vs_270 | False | False | True |
| section0 | lever_L | C_comp_to_tens_local_then_global | 0_vs_180 | False | False | True |
| section0 | lever_L | C_comp_to_tens_local_then_global | 45_vs_225 | False | False | True |
| section0 | lever_L | C_comp_to_tens_local_then_global | 90_vs_270 | False | False | True |
| section0 | lever_L | D_tens_to_comp_local_then_global | 0_vs_180 | False | False | True |
| section0 | lever_L | D_tens_to_comp_local_then_global | 45_vs_225 | False | False | True |
| section0 | lever_L | D_tens_to_comp_local_then_global | 90_vs_270 | False | False | True |
| section0 | lever_L | E_comp_to_tens_direct_global_no_flip | 0_vs_180 | False | False | True |
| section0 | lever_L | E_comp_to_tens_direct_global_no_flip | 45_vs_225 | False | False | True |
| section0 | lever_L | E_comp_to_tens_direct_global_no_flip | 90_vs_270 | False | False | True |
| section0 | lever_L | F_comp_to_tens_direct_global_with_flip | 0_vs_180 | False | False | True |
| section0 | lever_L | F_comp_to_tens_direct_global_with_flip | 45_vs_225 | False | False | True |
| section0 | lever_L | F_comp_to_tens_direct_global_with_flip | 90_vs_270 | False | False | True |
| section0 | lever_L | G_M_over_compress_surrogate_global | 0_vs_180 | False | False | True |
| section0 | lever_L | G_M_over_compress_surrogate_global | 45_vs_225 | False | False | True |
| section0 | lever_L | G_M_over_compress_surrogate_global | 90_vs_270 | False | False | True |
| section0 | lever_L | H_M_over_compress_surrogate_local_then_global | 0_vs_180 | False | False | True |
| section0 | lever_L | H_M_over_compress_surrogate_local_then_global | 45_vs_225 | False | False | True |
| section0 | lever_L | H_M_over_compress_surrogate_local_then_global | 90_vs_270 | False | False | True |
| sectioniv | lever_DX | A_current_centroid_with_explicit_sign_flip | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | A_current_centroid_with_explicit_sign_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | A_current_centroid_with_explicit_sign_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DX | B_centroid_without_explicit_sign_flip | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | B_centroid_without_explicit_sign_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | B_centroid_without_explicit_sign_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DX | C_comp_to_tens_local_then_global | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | C_comp_to_tens_local_then_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | C_comp_to_tens_local_then_global | 90_vs_270 | True | True | True |
| sectioniv | lever_DX | D_tens_to_comp_local_then_global | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | D_tens_to_comp_local_then_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | D_tens_to_comp_local_then_global | 90_vs_270 | True | True | True |
| sectioniv | lever_DX | E_comp_to_tens_direct_global_no_flip | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | E_comp_to_tens_direct_global_no_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | E_comp_to_tens_direct_global_no_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DX | F_comp_to_tens_direct_global_with_flip | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | F_comp_to_tens_direct_global_with_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | F_comp_to_tens_direct_global_with_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DX | G_M_over_compress_surrogate_global | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | G_M_over_compress_surrogate_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | G_M_over_compress_surrogate_global | 90_vs_270 | True | False | False |
| sectioniv | lever_DX | H_M_over_compress_surrogate_local_then_global | 0_vs_180 | True | True | True |
| sectioniv | lever_DX | H_M_over_compress_surrogate_local_then_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DX | H_M_over_compress_surrogate_local_then_global | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | A_current_centroid_with_explicit_sign_flip | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | A_current_centroid_with_explicit_sign_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | A_current_centroid_with_explicit_sign_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | B_centroid_without_explicit_sign_flip | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | B_centroid_without_explicit_sign_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | B_centroid_without_explicit_sign_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | C_comp_to_tens_local_then_global | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | C_comp_to_tens_local_then_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | C_comp_to_tens_local_then_global | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | D_tens_to_comp_local_then_global | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | D_tens_to_comp_local_then_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | D_tens_to_comp_local_then_global | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | E_comp_to_tens_direct_global_no_flip | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | E_comp_to_tens_direct_global_no_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | E_comp_to_tens_direct_global_no_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | F_comp_to_tens_direct_global_with_flip | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | F_comp_to_tens_direct_global_with_flip | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | F_comp_to_tens_direct_global_with_flip | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | G_M_over_compress_surrogate_global | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | G_M_over_compress_surrogate_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | G_M_over_compress_surrogate_global | 90_vs_270 | True | True | True |
| sectioniv | lever_DY | H_M_over_compress_surrogate_local_then_global | 0_vs_180 | True | False | False |
| sectioniv | lever_DY | H_M_over_compress_surrogate_local_then_global | 45_vs_225 | True | True | True |
| sectioniv | lever_DY | H_M_over_compress_surrogate_local_then_global | 90_vs_270 | True | True | True |
| sectioniv | lever_L | A_current_centroid_with_explicit_sign_flip | 0_vs_180 | False | False | True |
| sectioniv | lever_L | A_current_centroid_with_explicit_sign_flip | 45_vs_225 | False | False | True |
| sectioniv | lever_L | A_current_centroid_with_explicit_sign_flip | 90_vs_270 | False | False | True |
| sectioniv | lever_L | B_centroid_without_explicit_sign_flip | 0_vs_180 | False | False | True |
| sectioniv | lever_L | B_centroid_without_explicit_sign_flip | 45_vs_225 | False | False | True |
| sectioniv | lever_L | B_centroid_without_explicit_sign_flip | 90_vs_270 | False | False | True |
| sectioniv | lever_L | C_comp_to_tens_local_then_global | 0_vs_180 | False | False | True |
| sectioniv | lever_L | C_comp_to_tens_local_then_global | 45_vs_225 | False | False | True |
| sectioniv | lever_L | C_comp_to_tens_local_then_global | 90_vs_270 | False | False | True |
| sectioniv | lever_L | D_tens_to_comp_local_then_global | 0_vs_180 | False | False | True |
| sectioniv | lever_L | D_tens_to_comp_local_then_global | 45_vs_225 | False | False | True |
| sectioniv | lever_L | D_tens_to_comp_local_then_global | 90_vs_270 | False | False | True |
| sectioniv | lever_L | E_comp_to_tens_direct_global_no_flip | 0_vs_180 | False | False | True |
| sectioniv | lever_L | E_comp_to_tens_direct_global_no_flip | 45_vs_225 | False | False | True |
| sectioniv | lever_L | E_comp_to_tens_direct_global_no_flip | 90_vs_270 | False | False | True |
| sectioniv | lever_L | F_comp_to_tens_direct_global_with_flip | 0_vs_180 | False | False | True |
| sectioniv | lever_L | F_comp_to_tens_direct_global_with_flip | 45_vs_225 | False | False | True |
| sectioniv | lever_L | F_comp_to_tens_direct_global_with_flip | 90_vs_270 | False | False | True |
| sectioniv | lever_L | G_M_over_compress_surrogate_global | 0_vs_180 | False | False | True |
| sectioniv | lever_L | G_M_over_compress_surrogate_global | 45_vs_225 | False | False | True |
| sectioniv | lever_L | G_M_over_compress_surrogate_global | 90_vs_270 | False | False | True |
| sectioniv | lever_L | H_M_over_compress_surrogate_local_then_global | 0_vs_180 | False | False | True |
| sectioniv | lever_L | H_M_over_compress_surrogate_local_then_global | 45_vs_225 | False | False | True |
| sectioniv | lever_L | H_M_over_compress_surrogate_local_then_global | 90_vs_270 | False | False | True |
