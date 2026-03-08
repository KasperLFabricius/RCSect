# Plastic Legacy Shift Summary

Phase-1 shift to direct legacy PCROSS families in benchmark fixture path.

## Global max relative error by output group

| output_group | max_rel_before | max_rel_after | band_after |
| --- | --- | --- | --- |
| moments | 0.0747361615636723 | 0.010566743050442712 | 1%-5% |
| strains | 2.022349650925316 | 2.0132519634680768 | >5% |
| kappa | 0.0167681060023675 | 0.0047956443531201095 | <1% |
| compress_force | 1.8031324908629796 | 1.7945786894858 | >5% |
| lever_arms | 1.9925804260392563 | 1.9946553346536684 | >5% |

## Family summaries

| family | output_group | max_rel_before | max_rel_after |
| --- | --- | --- | --- |
| annular | moments | 0.006124792013084 | 0.0011384064992120775 |
| annular | strains | 2.0127595977897648 | 2.0052583528373704 |
| annular | kappa | 0.0061737734364434 | 0.001495696648268048 |
| annular | compress_force | 0.0028955972316819 | 0.0007635971565132672 |
| annular | lever_arms | 1.9925804260392563 | 1.9946553346536684 |
| annular | warnings | 1.0 | 1.0 |
| snit | moments | 0.0154492306109036 | 0.010566743050442712 |
| snit | strains | 2.022349650925316 | 2.0132519634680768 |
| snit | kappa | 0.0167681060023675 | 0.0047956443531201095 |
| snit | compress_force | 1.8031324908629796 | 1.7945786894858 |
| snit | lever_arms | 0.7568992182552471 | 0.7556945659781411 |
| snit | warnings | nan | nan |
| tbeam | moments | 0.0747361615636723 | 0.00011251455858352603 |
| tbeam | strains | nan | nan |
| tbeam | kappa | nan | nan |
| tbeam | compress_force | nan | nan |
| tbeam | lever_arms | nan | nan |
| tbeam | warnings | nan | nan |
