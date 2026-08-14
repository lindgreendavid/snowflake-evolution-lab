# Snowflake Evolution Lab

> When snowflake yeast evolve larger clusters, does cellular elongation track that transition in
> the same direction across every independently evolved anaerobic lineage?

Part of the [Lab Notes research portfolio](https://blog-interactive.lindgreendavid.workers.dev/).

**Interactive laboratory:** <https://lindgreendavid.github.io/snowflake-evolution-lab/>

## Result in one sentence

The frozen directional criterion passed: cellular aspect ratio and biomass-weighted mean cluster
radius were positively associated within all five anaerobic lineages (Spearman ρ 0.923–0.967;
median 0.956), but the coarse trajectories do not identify a universal causal threshold.

## Interactive experience

Replay each published trajectory from transfer 0 to 600, compare cluster radius with aspect ratio,
inspect the day-600 metabolic-treatment contrast, and switch between colony, packing, and fracture
views. Published mean radius and cell aspect ratio drive the animation. Five fixed seeds give the
replicates visually distinct but reproducible topologies; branch contacts, fractures, and the
packing-relief cue are explicitly modelled rather than measured. The model is not microscopy or a
forward evolutionary simulation. Its complete mapping is documented in the
[animation model specification](docs/animation-model-v0.1.md).

## Evidence

The analysis uses the `Fig1e` and `Fig2d` sheets of the public source workbook for Bozdag et al.
(2023), pinned to upstream commit `f65f8fa5f987b0979a83084b4348e153599bef79`. There are five
biological inference units and 64 paired population-time means; PA2 radius at day 400 is missing
and is not imputed. See the [source audit](docs/source-audit.md).

## Reproduce the analysis

```bash
python -m pip install -e '.[dev]'
snowflake-evolution
python scripts/build_site_data.py
pytest
```

The generated report and browser data must match the committed artifacts exactly.

## Scientific boundary

The study is a transparent reanalysis of published MuLTEE figure-source data. Association through
time does not establish that elongation alone caused larger size. This is not an independent
wet-lab replication, and laboratory yeast do not reproduce the historical origins of animals,
plants, fungi, or other multicellular lineages.

Read the [frozen protocol](docs/protocol-v0.1.md), [research report](docs/research-report-v0.1.md),
and [machine-readable provenance](data/provenance-v0.1.json).

## Citation and licence

The original analysis software and website are available under the [MIT licence](LICENSE). Cite
this software using [CITATION.cff](CITATION.cff) and cite the primary paper for the measurements.
Upstream data retain their original attribution and terms.
