# Snowflake Evolution Lab protocol v1.0

Status: frozen after a source-compatibility audit and before implementation of the v1 analysis.
The source article and public tables were necessarily inspected to establish feasibility. This is
therefore a prespecified reproduction plan, not a blinded preregistration.

## Question

Does experimentally reconstructed whole-genome duplication increase cell volume, cell elongation,
and cluster radius in snowflake yeast, and is tetraploidy by itself sufficient to explain the later
evolution of macroscopic size?

## Scientific motivation

The completed v0.1 study found that cell elongation and cluster radius increased together in all
five anaerobic MuLTEE lines, but could not distinguish causal contributions. Tong et al. (2025)
provide a second public dataset with two complementary evidence layers:

1. engineered diploid and tetraploid strains in anaerobic and mixotrophic backgrounds; and
2. time-resolved ploidy, chromosome copy number, cell morphology, and cluster size for PA1–PA5
   and PM1–PM5.

The intervention estimates the immediate phenotypic effect of genome duplication in the engineered
backgrounds. The longitudinal contrast asks whether the genome state that helps initially is enough
to account for macroscopic size across metabolic treatments.

## Frozen source identity

- Article: Tong et al., *Nature* 639, 691–699 (2025), DOI
  [10.1038/s41586-025-08689-6](https://doi.org/10.1038/s41586-025-08689-6).
- Public source repository: <https://github.com/ktong25/WGD_in_MuLTEE>
- Upstream commit: `aa090bbd9163dda490a5ede716bdd063270e9cd6`.
- Exact source-file hashes are recorded in `data/provenance-v1.0.json`.
- Engineered-strain source tables: `Fig3bcf_raw_EDFig5de.csv` and
  `Fig3e_raw_EDFig5bc.csv`.
- Longitudinal source tables: `Fig1cde_evo.csv`, `Fig2b.csv`, and `Fig2d.csv`.

## Units and transformations

### Engineered intervention

The biological inference unit is the engineered replicate strain (`n = 4` per condition-ploidy
cell). Individual segmented cells and clusters are aggregated within replicate before inference.

- Cell volume and aspect ratio are replicate means after applying the source authors' documented
  condition-by-ploidy aspect-ratio filters.
- Cluster radius is calculated separately within each 24-hour replicate as the radius of the
  volume-weighted mean cluster volume, exactly following the source analysis:

```text
weighted radius = (weighted_mean(volume, weights=volume) / (4π/3))^(1/3)
```

### Longitudinal contrast

The biological inference units are the five independently evolving lines per metabolic treatment.
The joined observations are t0, t200, t400, t600, and t1000 where available. G1 nuclear-DNA peak is
the source authors' ploidy proxy. Whole-chromosome copy numbers are displayed as published.

## Confirmatory intervention criterion

For each metabolic condition (PA anaerobic and PM mixotrophic), calculate the tetraploid-minus-
diploid difference between replicate means for:

1. 24-hour biomass-weighted mean cluster radius (primary endpoint);
2. mean cell volume; and
3. mean cell aspect ratio.

For every condition-outcome pair, report group means, absolute difference, relative ratio, a
deterministic percentile bootstrap 95% confidence interval for the difference (20,000 independent
two-group replicate resamples; seed 20250814), and a one-sided exact permutation probability over
all `choose(8, 4) = 70` allocations.

The confirmatory criterion passes only if both primary cluster-radius differences are positive and
their Holm-adjusted one-sided exact permutation probabilities are at most 0.05. Cell volume and
aspect ratio are prespecified mechanistic secondary endpoints and cannot rescue a failed primary
criterion.

## Sufficiency test

The statement “tetraploidy alone is sufficient for macroscopic size” is rejected if all of the
following source-grounded conditions hold:

1. every evolved PM and PA line-time G1 peak from t200 through t1000 is at least 3.4N;
2. at t1000 the mean PA cluster radius is at least five times the mean PM cluster radius; and
3. the maximum t1000 PM radius remains below 100 µm while at least four of five PA radii exceed
   300 µm.

These thresholds are operational tests for this dataset, not universal biological definitions.
Passing rejects sufficiency under the two studied metabolic treatments; it does not imply that
oxygen state alone caused the divergence.

## Sensitivity and descriptive outputs

- Report the sufficiency ratio at t600 as well as t1000.
- Report every lineage and time point rather than only treatment averages.
- Calculate per-observation whole-chromosome aneuploidy burden as
  `sum(abs(copy_number - 4))` across chromosomes I–XVI for evolved isolates.
- Do not infer a quantitative entanglement score: no time-resolved entanglement measurement is
  present in the selected public tables.

## Interpretation boundary

The engineered comparison supports an immediate ploidy-associated phenotype in the tested genetic
backgrounds. The longitudinal contrast demonstrates that tetraploidy is not sufficient across the
two metabolic treatments. Neither layer proves that genome duplication was necessary, identifies a
universal threshold, estimates an entanglement effect, or independently replicates the wet-lab
experiment. The data and code originate from the source authors.

## Versioning rule

The historical v0.1 protocol and outputs remain unchanged. Any endpoint, filter, threshold, source,
or inferential-unit change requires a new study version and must not overwrite this document.
