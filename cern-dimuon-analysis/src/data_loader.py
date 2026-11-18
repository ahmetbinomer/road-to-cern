import ROOT

def load_and_filter_data(
    source_url="root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root",
):
    ROOT.ROOT.EnableImplicitMT()
    print(f"[INFO] Connecting to CMS Open Data stream:\n       {source_url}")

    df = ROOT.RDataFrame("Events", source_url)

    #The 4 kinematic cuts sequentially:
    #1) Exactly 2 muons in the event: "nMuon == 2"
    #2) Opposite electric charges: "Muon_charge[0] != Muon_charge[1]"
    #3) High transverse momentum (> 25 GeV for both): "Muon_pt[0] > 25 && Muon_pt[1] > 25"
    #4) Detector acceptance region (|eta| < 2.4 for both): "abs(Muon_eta[0]) < 2.4 && abs(Muon_eta[1]) < 2.4"
    df_filtered = (
        df.Filter("nMuon == 2")
        .Filter("Muon_charge[0] != Muon_charge[1]")
        .Filter("Muon_pt[0] > 25 && Muon_pt[1] > 25")
        .Filter("abs(Muon_eta[0]) < 2.4 && abs(Muon_eta[1]) < 2.4")
    )

    #The relativistic invariant mass formula:
    # Formula: sqrt(2.0 * Muon_pt[0] * Muon_pt[1] * (cosh(Muon_eta[0] - Muon_eta[1]) - cos(Muon_phi[0] - Muon_phi[1])))
    df_mass = df_filtered.Define("dimuon_mass","sqrt(2.0 * Muon_pt[0] * Muon_pt[1] * (cosh(Muon_eta[0] - Muon_eta[1]) - cos(Muon_phi[0] - Muon_phi[1])))")

    #Title: "CMS Open Data (2012): Z -> #mu^{+}#mu^{-};M_{#mu#mu} [GeV];Events / 0.6 GeV"
    #Bins: 100 bins, Range: 60.0 to 120.0 GeV
    h_mass_ptr = df_mass.Histo1D(
        ("h_data_mass", "CMS Open Data (2012): Z -> #mu^{+}#mu^{-};M_{#mu#mu} [GeV];Events / 0.6 GeV", 100, 60.0, 120.0),
        "dimuon_mass",
    )

    h_mass = h_mass_ptr.GetValue()
    h_mass.SetDirectory(0)

    print(f"[INFO] Selected dimuon events in [60, 120] GeV: {int(h_mass.GetEntries())}")
    return h_mass

if __name__ == "__main__":
    hist = load_and_filter_data()
    c = ROOT.TCanvas("c_spectrum", "CMS Dimuon Mass Spectrum", 800, 600)
    hist.Draw("E")
    c.SaveAs("outputs/dimuon_mass_spectrum.png")
    print("[INFO] Saved test plot -> outputs/dimuon_mass_spectrum.png")