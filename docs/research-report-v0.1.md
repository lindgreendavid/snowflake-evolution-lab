# Cellular geometry and cluster size across five MuLTEE lineages

## Result

The frozen directional criterion passed. Each of the five anaerobic populations had a positive
within-line Spearman association between mean cellular aspect ratio and biomass-weighted mean
cluster radius over 600 transfers. Coefficients ranged from 0.923 to 0.967; the median was 0.956.
All five signs were positive, corresponding to 0.03125 under the protocol's limited equal-sign
null calculation.

## Reproduction

The input contains 65 population-by-time rows. One published radius value is missing (PA2 at day
400), so the analysis uses 64 paired observations. PA1, PA3, PA4, and PA5 contribute 13 time
points; PA2 contributes 12. No missing value is imputed.

Excluding the shared day-0 ancestor leaves every lineage positive, with Spearman coefficients from
0.902 to 0.958. Pearson correlations on log-radius range from 0.893 to 0.981, and Kendall tau-b
ranges from 0.821 to 0.872. These prespecified sensitivities agree directionally with the primary
summary.

## What the result means

The result is a compact cross-line reproducibility check of a relationship already motivated and
mechanistically investigated by the source paper. It shows that the published trajectory summaries
do not depend on a single anaerobic lineage for their directional cell-shape/size association.

It is not an independent replication: the values come from the authors' source workbook. It also
does not estimate a general evolutionary effect from five randomly sampled populations.

## What did not simplify

The exploratory intervals with the largest aspect-ratio increase and the largest log-radius
increase do not align consistently. Radius leads in PA1, PA2, and PA5; aspect ratio leads in PA3
and PA4 under this coarse 50-transfer comparison. The ordering is therefore unsuitable as evidence
for a universal temporal threshold. Measurement spacing, accumulated mutations, and protocol
changes further prevent a causal interpretation.

## Conclusion

Cell elongation and cluster size rise together, in the same rank direction, across all five
published anaerobic trajectories. The strong association is compatible with the source paper's
mechanical account, but it cannot by itself prove causation or identify a universal transition
point. A future preregistered study would need finer temporal measurements or an independently
constructed intervention to distinguish competing threshold mechanisms.
