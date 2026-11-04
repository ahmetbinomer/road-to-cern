import ROOT
import numpy as np

#If this file doesn't exist. It creates and writes on new file.
f = ROOT.TFile.Open("datas.root","RECREATE")

h = ROOT.TH1F("h_energy","Energy Distribution",50,0,100)
h.Fill(45.5)

#It writes on the file until we close the file
h.Write()

f.Close()

f = ROOT.TFile.Open("datas.root", "READ")

if not f or f.IsZombie():
    print("Error: File not found or corrupted.")
    exit()

print("TFile Directory")
f.ls()

obj = f.Get("h_energy")

if obj:
    print(f"\Succesfully loaded: {obj.GetName()}")
    print(f"Total entries: {obj.GetEntries()}")
    print(f"Mean: {obj.GetMean():.2f}")
    print(f"Std Dev: {obj.GetStdDev():.2f}")
else:
    print("Object key not found.")

f.Close()
