# v1.0.0 release audit

Audit date: 2026-08-14
Audited implementation commit: `520035e`

## Sources checked

- Tong et al. (2025), *Genome duplication in a long-term multicellularity evolution
  experiment*, Nature, DOI 10.1038/s41586-025-08689-6.
- Authors' public source repository `ktong25/WGD_in_MuLTEE`, pinned to commit
  `aa090bbd9163dda490a5ede716bdd063270e9cd6`.
- Bozdag et al. (2023), *De novo evolution of macroscopic multicellularity*, Nature, DOI
  10.1038/s41586-023-06052-1.
- Six selected source tables verified against the SHA-256 values frozen in
  `data/provenance-v1.0.json`.

## Reproduction executed

- Rebuilt the v0.1 and v1.0 machine-readable reports and all browser datasets.
- Enumerated all 70 possible four-versus-four allocations for each primary test.
- Repeated 20,000 deterministic independent-group bootstrap resamples.
- Ran lint, formatting, static typing, 18 tests, the 95% coverage gate, source/wheel builds,
  JavaScript syntax validation, and whitespace validation.
- Result: all checks passed; test coverage was 97.85%.
- Inspected the interactive site at desktop width and 390 px mobile width; exercised condition,
  lineage, and transfer controls; observed no browser console errors or body-level overflow.

## Cross-artifact consistency

- Product version is 1.0.0 in package metadata, citation metadata, changelog, README, website, and
  v1 result.
- The historical v0.1 report remains frozen at product version 0.1.1.
- The report, README, website, and machine-readable result use the same primary estimates,
  probabilities, longitudinal ratios, and evidence boundary.

## Deviations and remaining limits

- The source tables were inspected before the v1 protocol was frozen to establish compatibility.
  The protocol is therefore a prospective implementation contract, not a blinded preregistration.
- The selected public tables do not expose a joined quantitative time-resolved entanglement
  endpoint. No entanglement threshold is estimated.
- The work is a reanalysis of source-author data, not an independent wet-lab replication.
- The engineered comparison contains four biological replicate strains per group. Cell and cluster
  records are aggregated within replicate and are not treated as independent inference units.
