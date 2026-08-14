# Animation model specification v1.0.1

## Purpose and evidence boundary

The evolution chamber is an explanatory geometry model, not microscopy, a mechanical simulation,
or an observed topology time series. Published population means control cell aspect ratio and
cluster radius at the 13 sampled transfers. Everything spatial—the number and location of displayed
cells, tree shape, local crowding, fracture position, and retained contact—is deterministic model
output.

The five fixed population seeds are recognition devices. They must not be interpreted as measured
architectural differences among PA1–PA5. The frozen v0.1 and v1.0 analyses and their numerical
results are unchanged by this interface release.

| Visual layer | Meaning | Evidence status |
| --- | --- | --- |
| Cell aspect ratio | Interpolated from published population means | Measured at sampled transfers |
| Display scale | Log mapping of published mean cluster radius | Measured input, illustrative scale |
| Clonal tree | Balanced, collision-aware deterministic layout | Modelled recognition seed |
| Pale junction collar | Intact parent–daughter connection | Biological category; location modelled |
| Warm packing halo | Relative local model crowding after relief | Explanatory cue, not measured stress |
| Coral subtree and red gap | Component after one cut junction | Deterministic stress test |
| Gold dashed contact | Cross-component steric proximity | Modelled retention, never a bond |

## Biological semantics

Snowflake yeast grow as clonal trees because daughter cells remain attached to their mothers through
rigid chitinous connections. A broken connection does not reform. Later macroscopic clusters can
remain physically intact after several of those connections fracture because branches intercalate
and become sterically entangled. The interface therefore never draws a retained contact as an
adhesive or repaired bond.

The detailed serial block-face electron microscopy entanglement result reported by Jacobeen and
colleagues concerns a late PA2 sample. It is evidence for the mechanism, not a measured
population-by-transfer endpoint. No population-specific entanglement percentage is inferred here.

## Deterministic geometry

Each population has a fixed seed and branch profile. Starting from a founder, candidate daughters
are placed around eligible parents. The generator balances growth across primary arms, limits local
offspring, and rejects candidates that collide too closely with existing cells. The same population,
transfer, and published inputs always produce the same geometry. Displayed cell count and radius
use the transformations documented in the historical v0.1 specification; neither represents an
estimated biological cell count or absolute cluster geometry.

## Packing stress test

For each displayed cell, the interface sums distance-weighted neighbours within a fixed screen-space
radius. It normalizes that local crowding within the current drawing and attenuates it with the
pre-existing packing-relief cue derived from aspect ratio:

```text
local load = normalized local crowding × (1 − 0.65 × packing relief)
```

Warm halos expose relative locations in the illustrative geometry that are locally crowded. They do
not measure force, stress, strain, cell-wall mechanics, or a causal effect.

## One-junction fracture stress test

The fracture view removes one deterministic parent–daughter edge and computes the subtree that
would disconnect from the founder in the clonal tree. Intact junctions retain pale collars; the cut
junction receives a red gap and stubs; cells in the detached tree turn coral.

The interface then searches only for close pairs that cross the two graph components. If the
illustrative geometry is sufficiently developed and such pairs exist, up to five are drawn as gold
dashed steric contacts and the component is labelled retained. Otherwise it is labelled detached.
The screen-space distance and eligibility rules are visualization criteria, not biological
thresholds, fitted parameters, probabilities, or new measurements.

## Systematic interface audit

The release audit covered all 195 combinations of five populations, 13 published transfer stages,
and three mechanism views. Every colony and packing state contained exactly one intact tree with
`cells − 1` junctions. Every fracture state contained one severed junction and `cells − 2` intact
junctions; steric contacts appeared only in retained fracture states. No browser console errors were
observed. This verifies interface invariants, not biological accuracy of the illustrative geometry.

## Primary sources

- Bozdag, G. O. et al. *De novo evolution of macroscopic multicellularity*. Nature 617, 747–754
  (2023). <https://doi.org/10.1038/s41586-023-06052-1>
- Jacobeen, S. et al. *Morphological entanglement in living systems*. Physical Review X 14 (2024).
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC11524534/>
