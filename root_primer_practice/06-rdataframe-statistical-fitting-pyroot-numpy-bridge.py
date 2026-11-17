import ROOT
import array
import numpy as np

def generate_z_boson_sample(filename="z_boson_data.root", n_events=10000):
    f = ROOT.TFile.Open(filename,"RECREATE")
    tree = ROOT.TTree("Events","Z -> mu+ mu- Synthetic Dataset")

    #Buffers
    mu1_pt = array.array("f", [0.0])
    mu1_eta = array.array("f", [0.0])
    mu1_phi = array.array("f", [0.0])
    mu1_q = array.array("i", [0])

    mu2_pt = array.array("f", [0.0])
    mu2_eta = array.array("f", [0.0])
    mu2_phi = array.array("f", [0.0])
    mu2_q = array.array("i", [0])

    #Assigning buffers to tree
    for name, buf, leaf in [
        ("mu1_pt",mu1_pt,"mu1_pt/F"),
        ("mu1_eta",mu1_eta,"mu1_pt/F"),
        ("mu1_phi",mu1_phi,"mu1_phi/F"),
        ("mu1_q",mu1_q,"mu1_q/I"),

        ("mu2_pt",mu2_pt,"mu2_pt/F"),
        ("mu2_eta",mu2_eta,"mu2_eta/F"),
        ("mu2_phi",mu2_phi,"mu2_phi/F"),
        ("mu2_q",mu2_q,"mu2_q/I")
    ]:
        tree.Branch(name,buf,leaf)

    #Sample Data Creator
    rng = np.random.default_rng(42)

    for i in range(n_events):
        #%40 Z bozon signal (around 91.4 GeV), %60 background noise
        is_signal = (i % 5 < 2)
        if is_signal:
            # mass of Z = 91.19 GeV, width = 2.5 GeV
            target_mass = rng.normal(91.19, 2.5)
            pt1 = rng.uniform(30.0, 60.0)
            eta1 = rng.uniform(-2.0, 2.0)
            phi1 = rng.uniform(-np.pi, np.pi)
            eta2 = rng.uniform(-2.0, 2.0)
            phi2 = phi1 + np.pi + rng.normal(0, 0.2) # back to back
            # M^2 = 2 * pt1 * pt2 * (cosh(deta) - cos(dphi)) we take pt2 from this formulate:
            denom = 2.0 * pt1 * (np.cosh(eta1 - eta2) - np.cos(phi1 - phi2))
            pt2 = max(10.0, (target_mass ** 2) / denom)
            q1, q2 = 1, -1
        else:
            pt1 = rng.exponential(20.0) + 15.0
            pt2 = rng.exponential(18.0) + 15.0
            eta1, eta2 = rng.uniform(-2.4, 2.4, 2)
            phi1, phi2 = rng.uniform(-np.pi, np.pi, 2)
            q1 = 1
            q2 = -1 if rng.random() > 0.3 else 1

        mu1_pt[0], mu1_eta[0], mu1_phi[0], mu1_q[0] = pt1, eta1, phi1, q1
        mu2_pt[0], mu2_eta[0], mu2_phi[0], mu2_q[0] = pt2, eta2, phi2, q2
        tree.Fill()

    tree.Write()
    f.Close()
    print(f"[INFO] Generated {n_events} events -> {filename}")

def run_modern_analysis(filename="z_boson_data.root"):
    #Enabling multi-thread engine
    ROOT.EnableImplicitMT()

    #You don't need to open the file and bring the tree. RDataFrame can do.
    df = ROOT.RDataFrame("Events", filename)

    # 3. Chained Analyse:
    # - Filter 1: Opposite charges ("mu1_q * mu2_q == -1")
    # - Filter 2: High momentum ("mu1_pt > 25.0 && mu2_pt > 25.0")
    # - Define: ("dimuon_mass"):
    #           "sqrt(2.0 * mu1_pt * mu2_pt * (cosh(mu1_eta - mu2_eta) - cos(mu1_phi - mu2_phi)))"
    # - Histo1D: ("h_zmass", "Z Boson Invariant Mass;M_{#mu#mu} [GeV];Events / 1 GeV", 60, 60.0, 120.0)
    h_mass_rdf = (
        df.Filter("mu1_q * mu2_q == -1")
        .Filter("mu1_pt > 25.0 && mu2_pt > 25.0")
        .Define("dimuon_mass","sqrt(2.0 * mu1_pt * mu2_pt * (cosh(mu1_eta - mu2_eta) - cos(mu1_phi - mu2_phi)))")
        .Histo1D(("h_zmass", "Z Boson Invariant Mass;M_{#mu#mu} [GeV];Events / 1 GeV", 60, 60.0, 120.0),"dimuon_mass")
    )

    hist = h_mass_rdf.GetValue()

    #TF1 = 1 Dimension Function
    fit_func = ROOT.TF1("fit_func", "gaus(0) + expo(3)", 60.0, 120.0)
    fit_func.SetParNames("Amplitude", "Z_mass", "Z_width", "Bg_const", "Bg_slope")

    #initial guesses
    fit_func.SetParameters(250.0, 91.2, 2.5, 5.0, -0.03)
    fit_func.SetLineColor(ROOT.kRed)
    fit_func.SetLineWidth(2)

    fit_result = hist.Fit(fit_func, "S")

    z_mass = fit_func.GetParameter(1)
    z_mass_err = fit_func.GetParError(1)
    z_width = fit_func.GetParameter(2)

    #total error
    chi2 = fit_func.GetChisquare()

    #Number of Degrees of Freedom
    ndf = fit_func.GetNDF()

    print("\n--- FIT RESULTS ---")
    print(f"Measured Z Mass : {z_mass:.2f} +/- {z_mass_err:.2f} GeV (PDG: 91.19 GeV)")
    print(f"Measured Width  : {z_width:.2f} GeV")
    #chi2 / ndf shows degree of adaptation
    print(f"Chi2 / ndf      : {chi2:.2f} / {ndf} = {chi2/ndf:.2f}")

    # PyROOT -> NumPy Bridge (Zero-copy buffer view):
    # ROOT TH1D stores bin contents in a contiguous C++ double array of size (n_bins + 2),
    # prepending an underflow bin (index 0, < 60 GeV) and appending an overflow bin (index 61, > 120 GeV).
    # We read all (n_bins + 2) elements from the C++ pointer and slice [1:-1] to keep only the 60 visible bins.
    n_bins = hist.GetNbinsX()
    bin_contents = np.frombuffer(hist.GetArray(), dtype=np.float64, count=n_bins+2)[1:-1]

    print("\nPYROOT -> NUMPY BRIDGE")
    print(f"NumPy array shape : {bin_contents.shape}")
    print(f"Max bin count : {np.max(bin_contents):.0f} events")
    print(f"Total events in hist (NumPy sum): {np.sum(bin_contents):.0f}") 

    #Visualization
    ROOT.gStyle.SetOptFit(1111)
    canvas = ROOT.TCanvas("c_zfit", "Z Boson Fit", 900, 650)
    hist.SetMarkerStyle(20)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.Draw("E") #Error lines

    canvas.SaveAs("z_boson_fit.png")
    print("[INFO] Saved fit plot -> z_boson_fit.png")

if __name__ == "__main__":
    generate_z_boson_sample()
    run_modern_analysis()




