# Physics Background & Guide

## Higgs Boson Discovery

The Higgs boson was discovered in 2012 by ATLAS and CMS.

**Key Properties:**
- Mass: 125.09 ± 0.24 GeV
- Spin: 0 (scalar particle)
- Lifetime: Ultra-short (10^-22 seconds)
- Cannot be directly observed - decays immediately

## Higgs Decay Modes

The Higgs decays into various particles:

### H → ZZ → 4 Leptons (Golden Channel)
- **Branching ratio:** ~0.1%
- **Signature:** 4 isolated leptons (electrons or muons)
- **Advantage:** Very clean, low background
- **Challenge:** Low yield

### H → bb (Most Common)
- **Branching ratio:** ~58%
- **Signature:** Two b-jets
- **Advantage:** High yield
- **Challenge:** Large QCD background

### H → WW → 2 leptons 2 neutrinos
- **Branching ratio:** ~21%
- **Signature:** 2 leptons + missing energy
- **Trade-off:** Good yield, moderate background

## Analysis Strategy: H → ZZ → 4l

This pipeline implements the golden channel analysis.

### Step 1: Event Selection 
Requirements:

4 leptons (e or μ) with pT > 20 GeV
|eta| < 2.5
Relative isolation < 0.2
Good quality vertex

### Step 2: Pairing 
Find best Z pair combination:

Pair leptons of same flavor, opposite charge
Require invariant mass near Z (60-120 GeV)
Minimize |m1 - m2| from nominal Z mass

### Step 3: Reconstruction
Compute 4-lepton invariant mass:

M_4l = sqrt((E1+E2+E3+E4)² - (p1+p2+p3+p4)²)

### Step 4: Selection
Signal region: 120 < M_4l < 130 GeV

Very narrow window (only Higgs peak)
Background suppression essential

## Physics Quantities

### Kinematic Variables

**Transverse Momentum (pT)**
- Component perpendicular to beam axis
- Measured in detector
- Range: 0 - 1000 GeV

**Pseudorapidity (η)**
- Measures angle from beam axis
- Range: -5 to 5 (detector coverage: -2.5 to 2.5)
- Related to physical rapidity

**Azimuthal Angle (φ)**
- Angle around beam axis
- Range: 0 to 2π radians

**Invariant Mass**
M = sqrt(E² - p²c⁴) / c²

In natural units (c=1):
M = sqrt(E² - |p|²)

## Background Processes

### Irreducible Backgrounds

ZZ → 4l

Same final state as signal!
Continuous mass spectrum
Estimated from simulation


### Reducible Backgrounds

Z + jets → 4l-like

Jets misidentified as leptons
Reduced by tight selection


## Statistical Methods

### Significance (S/√B)

σ = S / √B

where:
S = signal events
B = background events

Discovery threshold: σ ≥ 3σ (1 in 740,000 chance)


### Likelihood Fit

L(data | μ) = Poisson(N_obs | μ·S + B)

where:
μ = signal strength (1 = SM prediction)
S = expected signal
B = expected background


## Expected Results

With full 2011-2012 CMS dataset:

Signal events: ~100
Background events: ~900
Significance: ~3σ (Discovery level)

This pipeline demonstrates the analysis on sample data.

## References

- Higgs Discovery: [CERN Press Release](https://home.cern/)
- CMS Physics: [CMS Collaboration](https://cms.cern/)
- Particle Data Group: [PDG](https://pdg.lbl.gov/)