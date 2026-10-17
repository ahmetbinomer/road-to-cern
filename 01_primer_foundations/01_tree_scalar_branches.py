"""
01_tree_scalar_branches.py: Simulates particle collision events and stores them
in a columnar TTree structure.
"""
import ROOT
import array
import math

def generate_collision_data(filename: str = "events_scalar.root", n_events: int = 10000):
    output_file = ROOT.TFile.Open(filename, "RECREATE")
    tree = ROOT.TTree("Events", "Simulated Collision Scalar Events")
    
    event_id = array.array('i', [0])
    n_particles = array.array('i', [0])
    pt = array.array('f', [0.0])       # Transverse momentum (GeV)
    eta = array.array('f', [0.0])      # Pseudorapidity
    phi = array.array('f', [0.0])      # Azimuthal angle [-pi, pi]
    
    tree.Branch("event_id", event_id, "event_id/I")
    tree.Branch("n_particles", n_particles, "n_particles/I")
    tree.Branch("pt", pt, "pt/F")
    tree.Branch("eta", eta, "eta/F")
    tree.Branch("phi", phi, "phi/F")
    
    rng = ROOT.TRandom3(42)
    
    print(f"{n_events} olay üretiliyor...")
    for i in range(n_events):
        event_id[0] = i
        n_particles[0] = int(rng.Poisson(4))
        pt[0] = rng.Exp(25.0)  # TRandom3 üstsel fonksiyonu: Exp()
        eta[0] = rng.Gaus(0.0, 1.5)
        phi[0] = rng.Uniform(-math.pi, math.pi)
        tree.Fill()
        
    tree.Write()
    output_file.Close()
    print(f"Başarıyla kaydedildi -> {filename}")

if __name__ == "__main__":
    generate_collision_data()
