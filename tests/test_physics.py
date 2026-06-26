import pytest
import numpy as np
from src.physics import LorentzVector, FourVectorMath

def test_invariant_mass():
    v1 = LorentzVector(pt=50, eta=0.5, phi=0.0, mass=0.1)
    v2 = LorentzVector(pt=40, eta=-0.3, phi=np.pi, mass=0.1)
    mass = FourVectorMath.invariant_mass([v1, v2])
    assert 0 < mass < 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])