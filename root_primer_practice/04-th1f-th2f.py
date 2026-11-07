import ROOT
import numpy as np

def generate_and_visulaze(filename = "my_data.root"):
    f = ROOT.TFile.Open(filename ,"READ")

    if not f or f.IsZombie():
        print("The file doesn't exist or corrupted.")
        return

    tree = f.Get("Events")

    h_pt = ROOT.TH1F("h_pt" ,"Transverse Momentum; p_{T} [GeV]; Events", 20, 15.0, 45.0)

    total_events = tree.GetEntries()
    for i in range(total_events):
        tree.GetEntry(i)
        h_pt.Fill(tree.pt)

    canvas = ROOT.TCanvas("c1", "pT Distribution", 800, 600)

    h_pt.SetMarkerStyle(20)
    h_pt.SetMarkerColor(ROOT.kBlue)

    h_pt.Draw("E")

    canvas.SaveAs("pt_distribution.png")

    integral = h_pt.Integral()
    if integral > 1:
        h_pt.Scale(1.0/integral)

    h_pt.GetYaxis().SetTitle("Probability Density")

    h_pt.Draw("E")
    canvas.SaveAs("pt_distribution_normalized.png")

    print("Plots are Saved")
    f.Close()

if __name__ == "__main__":
    generate_and_visulaze()