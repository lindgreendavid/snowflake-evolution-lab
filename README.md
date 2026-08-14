# Snowflake Evolution Lab

> Genome duplication makes snowflake yeast cells and clusters larger—but is it sufficient for the
> later evolution of macroscopic multicellularity?

Part of the [Lab Notes research portfolio](https://blog-interactive.lindgreendavid.workers.dev/).

**Interactive laboratory:** <https://lindgreendavid.github.io/snowflake-evolution-lab/>

## Stable v1.0 result

Engineered tetraploidy increased 24-hour cluster radius in both tested genetic backgrounds, but
all evolved PA and PM populations were already approximately tetraploid while only PA became
macroscopic. At transfer 1,000, mean PA radius was 8.859× mean PM radius. Whole-genome duplication
helps; it is not sufficient for the later macroscopic phenotype.

The historical frozen v0.1 analysis remains unchanged: cell aspect ratio and cluster radius were
positively associated within all five anaerobic lineages (Spearman ρ 0.923–0.967; median 0.956).

## Interactive experience

Replay the original transfer 0–600 morphology trajectories, then open the v1 genome explorer to
compare engineered 2N/4N effects and inspect chromosome copy number, G1 peak, and cluster radius
through transfer 1,000. Published summaries drive the displays. The colony animation remains an
explanatory model—not microscopy or a forward evolutionary simulation—and its full mapping is
documented in the [current animation model specification](docs/animation-model-v1.0.1.md). The
historical [v0.1 specification](docs/animation-model-v0.1.md) remains available unchanged.

## Evidence

The v1 analysis uses the public source tables for Tong et al. (2025), pinned to upstream commit
`aa090bbd9163dda490a5ede716bdd063270e9cd6`, with exact SHA-256 verification. Inference is performed
on four biological replicate strains per engineered group, not on thousands of segmented cells or
clusters as if they were independent. The longitudinal check follows PA1–PA5 and PM1–PM5 through
transfer 1,000. See the [source audit](docs/source-audit.md).

## Reproduce the analysis

```bash
python -m pip install -e '.[dev]'
snowflake-evolution
python scripts/build_site_data.py
pytest
```

To regenerate the compact v1 inputs from the authors' repository, clone their pinned commit and run
`python scripts/import_v1_sources.py /path/to/WGD_in_MuLTEE`. The importer refuses files whose
hashes do not match the frozen provenance. Generated reports and browser data must match the
committed artifacts exactly.

## Scientific boundary

This is a transparent reanalysis of published MuLTEE data. The selected public tables do not
contain a quantitative, time-resolved entanglement endpoint joined to each genome and morphology
observation, so this project does not estimate an entanglement threshold. It is not an independent
wet-lab replication, and laboratory yeast do not reproduce the historical origins of animals,
plants, fungi, or other multicellular lineages.

Read the [frozen v1.0 protocol](docs/protocol-v1.0.md),
[v1.0 research report](docs/research-report-v1.0.md), and
[machine-readable provenance](data/provenance-v1.0.json). Historical v0.1 study artifacts remain
available and unchanged.

## Citation and licence

The original analysis software and website are available under the [MIT licence](LICENSE). Cite
this software using [CITATION.cff](CITATION.cff) and cite the primary paper for the measurements.
Upstream data retain their original attribution and terms.
