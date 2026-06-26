import matplotlib.pyplot as plt
from pathlib import Path

fig, ax = plt.subplots()
ax.hist([125 + x for x in range(10)], bins=5)
ax.set_xlabel('Mass (GeV)')
ax.set_ylabel('Events')
plt.savefig('results/higgs_mass_spectrum.png')
print("✓ Plot saved")