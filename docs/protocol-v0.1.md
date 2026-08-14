# Snowflake Evolution Lab protocol v0.1

Status: frozen before the confirmatory calculations were run.

## Question

Across the five independently evolved anaerobic MuLTEE populations, is the association between
mean cellular aspect ratio and biomass-weighted mean cluster radius positive in every lineage over
the first 600 daily transfers?

## Scientific motivation

Bozdag et al. (2023) report that increasingly elongate cells first reduce packing strain and later
enable branch entanglement as snowflake yeast evolve macroscopic size. This study does not attempt
to rediscover or independently replicate that mechanistic result. It asks whether a simple,
lineage-level association is directionally reproducible in the public figure-source time series.

## Source and frozen identity

- Article: Bozdag et al., *Nature* 617, 747–754 (2023), DOI
  [10.1038/s41586-023-06052-1](https://doi.org/10.1038/s41586-023-06052-1).
- Public source repository:
  <https://github.com/ozanbozdag/De_novo_evolution_of_macroscopic_multicellularity>
- Upstream commit: `f65f8fa5f987b0979a83084b4348e153599bef79`.
- Workbook: `01_Source_data.xlsx`.
- SHA-256: `24827c20073969a7b6a0eaefb8540dbb874b3f8637d49ebd38ed75b5b92cfe80`.
- Sheets: `Fig1e` (cluster radius) and `Fig2d` (cellular aspect ratio).

Only the 65 paired population-by-time observations in those two source-data sheets are in scope.
PA2 day 400 has no radius value and is excluded pairwise, leaving 64 paired observations. The
common ancestor value at day 0 is retained because it is part of each published trajectory; a
prespecified sensitivity analysis excludes it.

## Variables

- Population: PA1, PA2, PA3, PA4, or PA5.
- Time: 0 through 600 daily transfers, at 50-transfer intervals.
- Cellular aspect ratio: published population mean, dimensionless.
- Cluster radius: published biomass-weighted mean radius, micrometres.

The population is the inferential unit (`n = 5`). Individual cells and clusters used to construct
the published means are not treated as independent replicates.

## Confirmatory analysis

For each population separately, calculate Spearman's rank correlation between cellular aspect
ratio and `log10(cluster radius)` across paired time points. The logarithm changes scale but not
ranks; it is retained so the same transformed values can be displayed and used in the Pearson
sensitivity analysis.

The confirmatory directional criterion passes if all five population-level Spearman correlations
are greater than zero. Under an explicitly limited null model in which the five independent
population-level signs are exchangeable and equally likely, five concordant positive signs have a
one-sided exact probability of `1 / 2^5 = 0.03125`. This sign calculation is descriptive evidence
of cross-line convergence, not a general population-level p-value for evolution.

Report every population-level coefficient, the median coefficient, the number of positive signs,
the paired-observation count, and the exact directional probability. Do not pool cell- or
cluster-level measurements to inflate the sample size.

## Prespecified sensitivity analyses

1. Repeat Spearman correlations after excluding the shared day-0 ancestor.
2. Calculate Pearson correlations between aspect ratio and `log10(radius)` within each lineage.
3. Calculate Kendall's tau within each lineage.

No sensitivity analysis can replace a failed confirmatory criterion.

## Exploratory analyses

- Identify the 50-transfer interval with the largest increase in `log10(radius)` for each lineage.
- Identify the interval with the largest increase in aspect ratio for each lineage.
- Report their temporal difference without a causal interpretation.
- Display treatment-level day-600 radii from source-data sheet `Fig1b` for context only.

These outputs are hypothesis-generating and have no pass/fail threshold.

## Interpretation boundary

A passing result supports directional concordance within these five selected anaerobic laboratory
populations and this published summary dataset. It does not establish that elongation alone causes
macroscopic size, that a universal geometric threshold exists, or that historical multicellular
lineages followed the same path. Time, accumulated mutations, changing selection, cell shape, and
cluster size all co-vary. The analysis cannot separate their causal contributions.

The interactive cluster is an explanatory geometry model, not microscopy, a forward evolutionary
prediction, or a reconstruction of unobserved ancestors.

## Versioning rule

This protocol remains labelled v0.1 even if the software later reaches v1.0.0. Any confirmatory
threshold, endpoint, or source change requires a new protocol and must not overwrite this file.
