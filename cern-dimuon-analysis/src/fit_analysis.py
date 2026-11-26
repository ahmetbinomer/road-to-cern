import os
import ROOT
from data_loader import load_and_filter_data
from mc_background import generate_mc_background


def run_z_boson_fit():
    # Ensure the output directory exists without raising an error if it already does
    os.makedirs("outputs", exist_ok=True)

    # Disable the default ROOT statistics box to prevent overlap with our custom TPaveText
    ROOT.gStyle.SetOptStat(0)

    h_data = load_and_filter_data()
    h_mc_bkg = generate_mc_background(h_data)

    total_fit = None

    #Breit Wigner
    #total_fit = ROOT.TF1("total_fit", "breitwigner(0) + expo(3)", 60.0, 120.0)

    total_fit = ROOT.TF1("total_fit", "[0]*TMath::Voigt(x-[1],[2],[3]) + expo(4)", 60.0, 120.0)
    total_fit.SetNpx(1000)

    total_fit.SetParameters(2.6e6, 91.19, 1.5, 2.4952, 11.7, -0.06)
    total_fit.SetParLimits(1, 88.0, 94.0)
    total_fit.SetParLimits(2, 0.3, 5.0)

    # Z width is fixed to the PDG value, the fit measures mass and detector resolution
    total_fit.FixParameter(3, 2.4952)

    # Perform the fit over [60, 120] GeV ("R": use TF1 range, "S": return full fit result)
    fit_result = h_data.Fit(total_fit, "RS")

    # Extract fitted physics parameters and goodness of fit metrics
    z_mass = total_fit.GetParameter(1)
    z_mass_err = total_fit.GetParError(1)
    sigma = total_fit.GetParameter(2)
    sigma_err = total_fit.GetParError(2)
    chi2 = total_fit.GetChisquare()
    ndf = total_fit.GetNDF()

    print("\n" + "=" * 50)
    print(f"Fitted Z Mass  : {z_mass:.4f} +/- {z_mass_err:.4f} GeV (PDG: 91.1876 GeV)")
    print(f"Resolution (σ) : {sigma:.4f} +/- {sigma_err:.4f} GeV")
    print(f"Chi2 / ndf     : {chi2:.2f} / {ndf} = {chi2 / ndf:.2f}")
    print("=" * 50 + "\n")

    # 3. Compute the Pull distribution: (Data - Fit) / Data_Error
    n_bins = h_data.GetNbinsX()
    h_pull = ROOT.TH1D("h_pull", ";M_{#mu#mu} [GeV];Pull (#sigma)", n_bins, 60.0, 120.0)

    for i in range(1, n_bins + 1):
        data_val = h_data.GetBinContent(i)
        data_err = h_data.GetBinError(i)
        bin_center = h_data.GetBinCenter(i)
        fit_val = total_fit.Eval(bin_center)

        if data_err > 0:
            pull = (data_val - fit_val) / data_err
            h_pull.SetBinContent(i, pull)
            h_pull.SetBinError(i, 1.0)

    # 4. Creating Dual Pad Canvas (Top: Spectrum + Fit, Bottom: Pull Residuals)
    canvas = ROOT.TCanvas("c_z_fit", "CMS Z -> mu+ mu- Analysis", 950, 800)

    # Top pad (occupies upper 70% of the canvas)
    pad1 = ROOT.TPad("pad1", "Main Spectrum", 0.0, 0.30, 1.0, 1.0)
    pad1.SetBottomMargin(0.02)
    pad1.SetLeftMargin(0.12)
    pad1.Draw()
    pad1.cd()

    h_data.SetTitle("CMS Open Data (2012): Z #rightarrow #mu^{+}#mu^{-} Invariant Mass")
    h_data.GetXaxis().SetLabelSize(0)
    h_data.GetYaxis().SetTitle("Events / 0.6 GeV")
    h_data.GetYaxis().SetTitleSize(0.045)
    h_data.SetMarkerStyle(20)
    h_data.SetMarkerSize(0.75)
    h_data.Draw("E")

    #N ormalized MC background
    h_mc_bkg.SetLineColor(ROOT.kAzure + 1)
    h_mc_bkg.SetFillColorAlpha(ROOT.kAzure + 1, 0.30)
    h_mc_bkg.Draw("HIST SAME")

    # Total Breit Wigner + Exponential fit curve
    total_fit.SetLineColor(ROOT.kRed + 1)
    total_fit.SetLineWidth(2)
    total_fit.Draw("SAME")

    # Add legend
    legend = ROOT.TLegend(0.15, 0.68, 0.44, 0.87)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.AddEntry(h_data, "CMS 2012 Data (4.64M events)", "lep")
    #legend.AddEntry(total_fit, "Breit-Wigner + Expo Fit", "l")
    legend.AddEntry(total_fit, "Voignan + Expo Fit", "l")
    legend.AddEntry(h_mc_bkg, "MC Background (Sideband Norm.)", "f")
    legend.Draw()

    # Add custom physics results box (TPaveText)
    info_box = ROOT.TPaveText(0.60, 0.62, 0.88, 0.87, "NDC")
    info_box.SetBorderSize(1)
    info_box.SetFillColor(ROOT.kWhite)
    info_box.SetTextAlign(12)
    info_box.AddText(f"M_{{Z}} = {z_mass:.3f} #pm {z_mass_err:.3f} GeV")
    info_box.AddText(f"#sigma_{{det}} = {sigma:.3f} #pm {sigma_err:.3f} GeV")
    info_box.AddText("#Gamma_{Z} = 2.495 GeV (fixed)")
    info_box.AddText("PDG M_{Z} = 91.188 GeV")
    info_box.AddText(f"#chi^{{2}} / ndf = {chi2:.1f} / {ndf}")
    info_box.Draw()

    # Bottom pad (occupies lower 30% of the canvas)
    canvas.cd()
    pad2 = ROOT.TPad("pad2", "Pull Residuals", 0.0, 0.0, 1.0, 0.30)
    pad2.SetTopMargin(0.04)
    pad2.SetBottomMargin(0.32)
    pad2.SetLeftMargin(0.12)
    pad2.Draw()
    pad2.cd()

    h_pull.SetMarkerStyle(20)
    h_pull.SetMarkerSize(0.65)
    h_pull.GetYaxis().SetRangeUser(-5.0, 5.0)
    h_pull.GetYaxis().SetNdivisions(505)
    h_pull.GetYaxis().SetTitle("Pull (#sigma)")
    h_pull.GetYaxis().SetTitleSize(0.10)
    h_pull.GetYaxis().SetTitleOffset(0.50)
    h_pull.GetYaxis().SetLabelSize(0.09)
    h_pull.GetXaxis().SetTitle("M_{#mu#mu} [GeV]")
    h_pull.GetXaxis().SetTitleSize(0.11)
    h_pull.GetXaxis().SetLabelSize(0.10)
    h_pull.Draw("E1")

    # Draw dashed reference line at Pull = 0
    zero_line = ROOT.TLine(60.0, 0.0, 120.0, 0.0)
    zero_line.SetLineColor(ROOT.kRed + 1)
    zero_line.SetLineStyle(2)
    zero_line.Draw("SAME")

    canvas.SaveAs("outputs/z_boson_fit.png")
    print("[INFO] Saved publication fit plot -> outputs/z_boson_fit.png")


if __name__ == "__main__":
    run_z_boson_fit()