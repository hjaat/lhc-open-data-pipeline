from src.config import PhysicsConstants
from src.physics import LorentzVector, FourVectorMath

def test_week1_complete():
    assert PhysicsConstants.HIGGS_MASS == 125.09
    v1 = LorentzVector(pt=50, eta=0.5, phi=0.0, mass=0.1)
    v2 = LorentzVector(pt=40, eta=-0.3, phi=3.14, mass=0.1)
    mass = FourVectorMath.invariant_mass([v1, v2])
    assert mass > 0
    print("✓ Week 1 complete!")