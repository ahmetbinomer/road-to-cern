# Z Boson Invariant Mass Reconstruction and Statistical Fit on CMS Open Data

An end to end, modular particle physics analysis pipeline built with **PyROOT**, **RDataFrame**, and **XRootD**. This project streams 2012 proton proton collision events ($\sqrt{s} = 8\text{ TeV}$) directly from the CERN Open Data portal, reconstructs $Z \rightarrow \mu^+\mu^ $ decays, models the continuum background via sideband normalized Monte Carlo sampling, and extracts the $Z$ boson mass ($M_Z$) and decay width ($\Gamma_Z$) using a joint Relativistic Breit Wigner and Exponential fit.

![Z Boson Invariant Mass Fit](outputs/z_boson_fit.png)

## Physics Motivation & Dataset

* **Dataset:** CMS 2012 RunB/RunC DoubleMuParked Derived NanoAOD (`Run2012BC_DoubleMuParked_Muons.root`), accessed remotely via the XRootD protocol (`eospublic.cern.ch`).
* **Signal Process:** $pp \rightarrow Z/\gamma^* \rightarrow \mu^+\mu^-$
* **Kinematic Event Selection:**
  * Exactly two reconstructed muons per event (`nMuon == 2`)
  * Opposite electric charges (`Muon_charge[0] != Muon_charge[1]`)
  * High transverse momentum (`Muon_pt > 25 GeV` for both muons)
  * Central CMS muon chamber acceptance (`|Muon_eta| < 2.4` for both muons)
  * Selected dimuon yield in $[60, 120]\text{ GeV}$: **4,635,768 events**

## Repository Architecture

```text
cern-dimuon-analysis/
├── algorithms/
│   ├── data_loader_algorithm.py       # Step by step documentation of data streaming & cuts
│   ├── mc_background_algorithm.py     # Inverse transform sampling & sideband normalization logic
│   └── fit_analysis_algorithm.py      # Composite fitting & pull residual calculation workflow
├── outputs/
│   ├── dimuon_mass_spectrum.png       # Raw invariant mass distribution (4.64M events)
│   └── z_boson_fit.png                # Publication style dual pad fit and pull residual plot
├── src/
│   ├── data_loader.py                 # Multi threaded RDataFrame filtering and 4 vector mass calculation
│   ├── mc_background.py               # TRandom3 exponential background generator and sideband scaler
│   └── fit_analysis.py                # Minuit2 joint fit, parameter extraction, and TPad visualization
├── requirements.txt                   # Conda environment specification
└── README.md