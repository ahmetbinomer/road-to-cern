import ROOT


def generate_mc_background(h_data, n_mc_events=500000, decay_slope=0.035, seed=42):
    """
    Generates a synthetic exponential background histogram using ROOT.TRandom3
    and normalizes it to the real CMS data in the signal-free sideband regions:
    [60, 75] GeV and [105, 120] GeV.
    """
    # Initialize ROOT's Mersenne Twister random number generator with seed
    rng = ROOT.TRandom3(seed)

    # Create background histogram matching h_data binning (100 bins, 60 to 120 GeV)
    h_mc_bkg = ROOT.TH1D(
        "h_mc_bkg",
        "Synthetic MC Background;M_{#mu#mu} [GeV];Events / 0.6 GeV",
        100,
        60.0,
        120.0,
    )
    h_mc_bkg.SetDirectory(0)

    # Generate exponentially falling background events in [60, 120] GeV
    max_cdf = 1.0 - ROOT.TMath.Exp(-decay_slope * 60.0)
    for _ in range(n_mc_events):
        u = rng.Rndm()
        mass = 60.0 - ROOT.TMath.Log(1.0 - u * max_cdf) / decay_slope
        h_mc_bkg.Fill(mass)

    # Find the bin indices corresponding to the sideband boundaries
    b_60 = h_data.FindBin(60.0)
    b_75 = h_data.FindBin(75.0) - 1
    b_105 = h_data.FindBin(105.0)
    b_120 = h_data.FindBin(120.0) - 1

    # Calculate total events in sidebands for both real data and MC background
    data_sideband_yield = h_data.Integral(b_60, b_75) + h_data.Integral(b_105, b_120)
    mc_sideband_yield = h_mc_bkg.Integral(b_60, b_75) + h_mc_bkg.Integral(b_105, b_120)

    # Compute the scale factor and apply it to h_mc_bkg
    scale_factor = data_sideband_yield / mc_sideband_yield
    h_mc_bkg.Scale(scale_factor)

    print(f"[INFO] MC Background scaled by factor: {scale_factor:.4f} (Sideband yield: {data_sideband_yield:.0f})")
    return h_mc_bkg