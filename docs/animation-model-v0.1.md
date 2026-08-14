# Animation model specification v0.1

## Purpose and evidence boundary

The evolution chamber is an explanatory visualization of mechanisms discussed by Bozdag et al.
(2023), not a reconstruction of microscopy and not a population-genetic simulation. It makes two
published population means visible while keeping all unobserved visual structure explicitly
modelled.

| Layer | Quantity | Status |
| --- | --- | --- |
| Data | Mean cellular aspect ratio at each sampled transfer | Published measurement |
| Data | Biomass-weighted mean cluster radius at each sampled transfer | Published measurement |
| Model | Cell and branch positions | Illustrative, deterministic topology |
| Model | Packing-relief cue | Normalized explanatory mapping |
| Model | Retained branch contacts | Illustrative proximity rule |
| Model | Broken parent–daughter bonds | Illustrative late-stage rule |

The five populations do not have published time-resolved topology coordinates in the imported
figure-source sheets. Their different visual architectures must therefore not be interpreted as
observed differences between PA1–PA5.

## Empirical drivers

At the 50-transfer source points, the animation uses the published `aspect_ratio` and `radius_um`
values directly. Between source points, it linearly interpolates each quantity solely to produce a
smooth visual transition and marks the readout with an approximation symbol and an interpolation
notice. PA2 radius at transfer 400 is absent from the source workbook. The numerical readout remains
“Not reported”; only the animation bridges the neighbouring reported values at transfers 350 and
450.

Cluster display growth is a log mapping of radius because the measured range is too wide for a
linear screen representation:

```text
growth = clamp(log(radius / 16.7472384) / log(600 / 16.7472384), 0, 1)
displayed cells = round(18 + 125 × growth)
display radius = 72 + 190 × growth
```

Cell ellipses preserve approximate display area while changing elongation with the measured aspect
ratio `a`:

```text
rx = clamp(8.4 / sqrt(a), 4.2, 7.5)
ry = clamp(8.4 × sqrt(a), 9, 16)
```

These are display transformations, not estimates of cell number, biomass, or absolute geometry.

## Deterministic topology

Each population uses a fixed integer seed and a fixed parameter profile. A seeded pseudo-random
generator grows a parent–daughter tree from a central cell. Arm count, branching frequency,
curvature, and angular jitter differ between seeds so that users can recognize the five trajectories
without seeing the same template repeated. Redrawing the same population and transfer always
produces the same geometry. Seed identity is a user-interface device only.

## Mechanism cues

The paper reports that increased cellular elongation reduces packing-induced strain and that later
branch entanglement can preserve cluster integrity after individual cell–cell bonds fracture. The
interface turns that qualitative mechanism into inspectable cues:

```text
packing relief = clamp((aspect ratio − 1.25) / (3.20 − 1.25), 0, 1)
entanglement cue = clamp((growth − 0.38) / 0.62, 0, 1)
                     × (0.45 + 0.55 × packing relief)
```

The packing view colours a normalized strain cue. The fracture view introduces deterministic gaps
in a small subset of late-stage bonds and draws nearby non-parent branches as retained contacts.
Neither percentage is a measured rate, calibrated mechanical quantity, causal estimate, or new
result.

## Scientific rationale and limits

The visual sequence follows the mechanical interpretation in the primary paper: elongated cells can
reduce packing stress, and entangled branches can make large clusters damage-tolerant. It does not
claim that elongation alone caused macroscopic size, that entanglement followed the displayed timing
in every lineage, or that topology differed between populations in the illustrated way.

Primary source: Bozdag, G. O. et al. *De novo evolution of macroscopic multicellularity*. Nature
617, 747–754 (2023). <https://doi.org/10.1038/s41586-023-06052-1>
