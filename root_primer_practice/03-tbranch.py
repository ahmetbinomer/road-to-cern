import ROOT
import array

def write_tree(filename="my_data.root"):
    f = ROOT.TFile.Open(filename,"RECREATE")

    #First name second description
    tree = ROOT.TTree("Events","Mini Collision Data")

    #buffer = a temporary storage area in memory used to hold data during transfer between different devices or processes
    event_id = array.array("i", [0])
    pt = array.array("f", [0,0])
    eta = array.array("f", [0,0])
    energy = array.array("f", [0,0])

    tree.Branch("event_id", event_id, "event_id/I")
    tree.Branch("pt", pt, "pt/F")
    tree.Branch("eta",eta, "eta/F")
    tree.Branch("energy", energy, "energy/F")

    #Sample data
    for i in range(10):
        event_id[0] = i
        pt[0] = 20.0 + (i * 2.5)
        eta[0] = -1.5 + (i * 0.3)
        energy[0] = 50.0 + (i * 10.0)
        tree.Fill()

    tree.Write()
    f.Close()
    print(f"Dataset generated -> {filename}")

def read_and_inspect_tree(filename="my_data.root"):
    f = ROOT.TFile.Open(filename, "READ")

    if not f or f.IsZombie():
        print("Error: The File doesn't exist or corrupted.")

    tree = f.Get("Events")

    total_events = tree.GetEntries()
    print(f"\nTotal Events in Tree: {total_events}")

    #Random Access: 5th event directly
    target_entry = 4
    tree.GetEntry(target_entry)
    print(f"\nReading Spesific Entry: {target_entry}")
    print(f"Event ID: {tree.event_id}")
    print(f"pT:       {tree.pt}")
    print(f"eta:      {tree.eta}")
    print(f"Energy:   {tree.energy}")

    print("\nIteration All Over Entries")
    for i in range(total_events):
        tree.GetEntry(i)
        print(f"Entry {i:>2} -> ID={tree.event_id}, pt = {tree.pt:5.1f}, energy={tree.energy:5.1f}")

    f.Close()

if __name__ == "__main__":
    write_tree()
    read_and_inspect_tree()



