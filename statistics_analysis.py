"""Στατιστική ανάλυση των 18 δοκιμών (διαφορές χρόνων άφιξης).

Χρήση:  python statistics_analysis.py measurements.csv
"""
import sys
import numpy as np
from scipy import stats

A = np.genfromtxt(sys.argv[1] if len(sys.argv) > 1 else "measurements.csv",
                  delimiter=",", skip_header=1)
trial, tE, tK, tP = A.T
n = len(trial)


def summary(x, name):
    m, s = x.mean(), x.std(ddof=1)
    sem = s / np.sqrt(n)
    h = stats.t.ppf(0.975, n - 1) * sem
    print(f"{name}: μέση {m:.1f}  s {s:.1f}  SEM {sem:.1f}  ΔΕ 95% {m-h:.1f}..{m+h:.1f} ms")


EK, PK, EP = tE - tK, tP - tK, tE - tP
for x, nm in [(EK, "tε−tκ"), (PK, "tπ−tκ"), (EP, "tε−tπ")]:
    summary(x, nm)
    print(f"   δοκιμές 1–9: {x[:9].mean():.1f}  10–18: {x[9:].mean():.1f}")
print("κυκλοειδής πρώτη έναντι ευθείας:", int((EK > 0).sum()), "/", n,
      "| πολυωνυμική έναντι ευθείας:", int((EP > 0).sum()), "/", n)
print("έλεγχος προσήμου p =", 2 * 0.5 ** n)
print("συσχέτιση (tε−tκ, tπ−tκ): r = %.2f, p = %.3f" % stats.pearsonr(EK, PK))
