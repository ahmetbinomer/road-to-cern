# Event Selection for Z -> mu+ mu-
#
# 1. pT > 25 GeV:
# High transverse momentum cuts out low-energy detector noise and QCD background.
# Decay products of a heavy particle like the Z boson have significant transverse momentum.
#
# 2. Opposite Charge (q1 * q2 == -1):
# The neutral Z boson must decay into two muons with opposite signs to conserve charge.
# Same-sign pairs cannot come from a single Z decay and are discarded as random background.

import ROOT
import numpy as np
import array

def generate_dimuon_data(filename="dimuon_events.root"):
    f = ROOT.TFile.Open(filename,"RECREATE")
    tree = ROOT.TTree("Events", "Di-muon Collison Events")

    #Buffers
    mu1_pt = array.array("f", [0.0])
    mu1_charge = array.array("i", [0])
    mu2_pt = array.array("f", [0.0])
    mu2_charge = array.array("i", [0])

    #Defining the tree
    tree.Branch("mu1_pt",mu1_pt,"mu1_pt/F")
    tree.Branch("mu1_charge",mu1_charge,"mu1_charge/I")
    tree.Branch("mu2_pt",mu2_pt,"mu2_pt/I")
    tree.Branch("mu2_charge",mu2_charge,"mu2_charge/I")

    #Mock dataset
    for i in range(100):
        #We test that the system eleminates same charge cases or don't
        mu1_charge[0] = 1
        mu2_charge[0] = -1 if (i % 2 == 0) else 1

        mu1_pt[0] = 10.0 + (i * 0.4)
        mu2_pt[0] = 50.0 - (i * 0.3)

        tree.Fill()

    tree.Write()
    f.Close()
    print(f"Sample data successfully generated -> {filename}")

def apply_selection_cuts(filename="dimuon_events.root"):
    f = ROOT.TFile.Open(filename,"READ")

    if not f or f.IsZombie():
        print("The file doesn't exist or corrupted.")
        return

    tree = f.Get("Events")
    total_entries = tree.GetEntries()

    #The first histogram is unfiltered
    #The second histogram is filtered
    h_before = ROOT.TH1F("h_before","Before Cuts;Muon 1 p_{T} [GeV];Events",40,0.0,60.0)
    h_after = ROOT.TH1F("h_after","After Cuts (OS + p_{T}>25);Muon 1 p_{T} [GeV];Events", 40, 0.0, 60.0)

    passed_count = 0

    for i in range(total_entries):
        tree.GetEntry(i)

        h_before.Fill(tree.mu1_pt)

        is_opposite_sign = (tree.mu1_charge * tree.mu2_charge == -1)
        is_high_pt = (tree.mu1_pt > 25.0 and tree.mu2_pt > 25.0)

        if not (is_opposite_sign and is_high_pt):
            continue  

        passed_count += 1
        h_after.Fill(tree.mu1_pt)

    print(f"Total Events: {total_entries}")
    print(f"Passed Cuts: {passed_count}, ({passed_count / total_entries * 100:.1f}%)")

    canvas = ROOT.TCanvas("c_cuts","Cuts Selection",1000,500)
    canvas.Divide(2,1)

    canvas.cd(1)
    h_before.SetLineColor(ROOT.kRed)
    h_before.Draw("HIST")

    canvas.cd(2)
    h_after.SetLineColor(ROOT.kBlue)
    h_after.Draw("HIST")

    canvas_name = "cuts_comparison.png"
    canvas.SaveAs(canvas_name)
    print(f"Plot Saved -> {canvas_name}")

if __name__ == "__main__":
    generate_dimuon_data()
    apply_selection_cuts()



        