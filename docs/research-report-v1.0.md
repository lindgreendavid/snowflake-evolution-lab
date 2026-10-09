# Genome duplication helps—but does not finish—the transition

## Result

The frozen v1.0 evaluation gate passed. Experimentally induced tetraploidy increased 24-hour
biomass-weighted mean cluster radius in both tested backgrounds, while the longitudinal comparison
showed that tetraploidy was not sufficient for the later macroscopic phenotype.

| Background | 2N radius (µm) | 4N radius (µm) | Difference (µm) | 95% bootstrap interval | Ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| PA | 20.157 | 27.299 | +7.142 | [6.751, 7.538] | 1.354× |
| PM | 25.890 | 42.897 | +17.007 | [15.976, 18.318] | 1.657× |

Each comparison uses four biological replicate strains per ploidy group. The exact one-sided
permutation probability is 1/70 = 0.0143 for each background and 0.0286 after Holm correction
across the two primary tests. The source measurements comprise 39,329 segmented cells and 17,227
24-hour clusters; measurements are aggregated within biological replicate before inference.

## Sufficiency check

All 40 evolved population-time G1 peaks were at least 3.489N. Yet the anaerobic PA lines were much
larger than the mixotrophic PM lines: their mean-radius ratio was 6.669 at transfer 600 and 8.859
at transfer 1,000. At transfer 1,000, all five PA populations exceeded 300 µm, whereas the largest
PM population was 53.226 µm. Genome duplication therefore supplied an immediate size-related
advantage but did not, by itself, produce the macroscopic outcome.

## Interpretation

The intervention and longitudinal observations answer different questions. The engineered 2N/4N
contrast supports an immediate effect of whole-genome duplication on cell geometry and cluster
radius in these strains. The evolved-population comparison rejects a simple sufficiency claim:
additional evolved changes distinguish PA from PM after genome duplication had become widespread.

The authors' mechanical account—cell elongation, packing relief, and branch entanglement—remains a
well-supported explanation in the primary experimental work. The selected public tables do not,
however, provide a quantitative time-resolved entanglement endpoint joined to every genome and
morphology observation. This reanalysis therefore does not estimate an entanglement threshold or
claim that a coupled genomic-mechanical threshold has been measured.

## Reproducibility and scope

The source repository is pinned to commit `aa090bbd9163dda490a5ede716bdd063270e9cd6`, and every input
file is verified by SHA-256 before derivation. Exact permutation tests enumerate all 70 possible
four-versus-four allocations. Bootstrap intervals use 20,000 deterministic resamples with seed
20250814. The full protocol, provenance, compact derived data, analysis code, tests, and
machine-readable result are committed with this report.

This is a reproducible reanalysis of published experimental-evolution data, not an independent
wet-lab replication and not evidence for a universal law of multicellular evolution.

## Amendment 1 (2026-10-09): exact small-sample audit

Post-hoc and not preregistered (`src/snowflake_evolution_lab/smallsample.py`, `reports/post-release-small-sample.json`; all
results reported). The frozen v1.0 results are unchanged.

- The percentile-bootstrap intervals above, resampling only four replicate means per group, are narrower than exact
  permutation-inversion intervals: PA 6.455 to 7.923 µm (bootstrap 6.751 to 7.538) and PM 15.649 to 19.210 µm
  (bootstrap 15.976 to 18.318). Both still exclude zero; no conclusion changes.
- The gate passes on the preregistered one-sided test. The smallest attainable two-sided probability with 4 v 4 is
  0.0286 (2/70) in each background, and its Holm adjustment across the two backgrounds is 0.0571.
- Evolved lines, exact two-sided permutation probability for five PA v five PM populations: transfer 200, 0.325;
  transfer 400, 0.095; transfer 600, 0.0079 (complete separation: smallest PA 95.7 µm, largest PM 67.7 µm); transfer 1,000,
  0.0079 (smallest PA 319.6 µm, largest PM 53.2 µm). The divergence emerges between transfers 400 and 600.

