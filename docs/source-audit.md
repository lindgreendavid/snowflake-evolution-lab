# Source audit

Audited 2026-08-14.

## Primary empirical source

Bozdag, G. O. et al. “De novo evolution of macroscopic multicellularity.” *Nature* 617,
747–754 (2023). <https://doi.org/10.1038/s41586-023-06052-1>

The article reports an ongoing Multicellularity Long-Term Evolution Experiment with five replicate
populations in each of three metabolic treatments. After 600 daily selection rounds (about 3,000
cellular generations), all five anaerobic populations had evolved macroscopic size, whereas the
obligately aerobic and mixotrophic populations remained microscopic. The paper connects increased
cell length, reduced packing strain, and later branch entanglement to greater cluster size and
toughness.

The public source-data repository was checked at commit
`f65f8fa5f987b0979a83084b4348e153599bef79`. The figure-source workbook hash and selected sheets are
recorded in `data/provenance-v0.1.json`. The committed CSV values were transcribed from `Fig1b`,
`Fig1e`, and `Fig2d` and reconciled cell-for-cell with those sheets. PA2 day 400 has a published
aspect-ratio mean but no corresponding radius mean and remains missing.

## Context sources

- Pineau et al. report stable coexistence of small and large cluster-forming lineages over roughly
  4,300 generations: <https://doi.org/10.1038/s41559-024-02367-y>.
- MuLTEE work on genome duplication reports early tetraploidy in both mixotrophic and anaerobic
  populations; only anaerobic populations subsequently evolved macroscopic size:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC12256070/>.
- MuLTEE work on transport reports metabolically driven flows in large clusters and argues that
  these flows can relieve diffusion constraints: <https://pmc.ncbi.nlm.nih.gov/articles/PMC11213004/>.
- Jorge et al. present a general theoretical model in which spatial niche differences can permit
  multicellularity without a direct within-environment performance benefit:
  <https://doi.org/10.1038/s41559-026-03044-y>.

The last source is theory, not an empirical result from MuLTEE, and is presented as a separate idea
in the interactive explainer.

## v1 genome-duplication source

Tong, K. et al. “Genome duplication in a long-term multicellularity evolution experiment.”
*Nature* 639, 691–699 (2025). <https://doi.org/10.1038/s41586-025-08689-6>

The public source repository was audited at commit
`aa090bbd9163dda490a5ede716bdd063270e9cd6`. It contains engineered 2N/4N replicate-level cell and
cluster measurements plus longitudinal PA1–PA5 and PM1–PM5 phenotype, ploidy, and chromosome-copy
tables at compatible identities and time points. Exact hashes are recorded in
`data/provenance-v1.0.json`.

The v1 audit identified an important boundary: the selected tables contain no quantitative,
time-resolved entanglement endpoint. They can test the immediate phenotypic effect of engineered
tetraploidy and whether tetraploidy is sufficient across metabolic treatments, but they cannot fit
or validate a coupled genomic–entanglement threshold. The v1 protocol was narrowed accordingly.

## Licensing and reuse boundary

The analysis software and original website are MIT-licensed. The source measurements remain
attributed to their authors and canonical publication. Reuse of the upstream article, workbook,
or images remains subject to the upstream terms; this repository does not relicense them.
