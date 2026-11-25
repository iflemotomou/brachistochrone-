"""Αριθμητικός υπολογισμός του χρόνου κύλισης συμπαγούς σφαίρας σε κάθε τροχιά.

Χρήση:  python model_times.py profiles.csv

Βήματα:
 1. Προφίλ πυθμένα z(y) από το STL· φίλτρο διαμέσου (5 σημείων) για μεμονωμένα
    άκυρα σημεία και μονότονα φθίνουσα μορφή (np.minimum.accumulate).
 2. Παρεμβολή PCHIP. Η ευθεία δίνεται αναλυτικά: z = 145,837 − 0,6369·y (κλίση 32,5°).
 3. Καμπύλη κέντρου: μετατόπιση του πυθμένα κατά r = 7,5 mm στην κάθετο.
 4. Εκκίνηση με το κέντρο στο z0 (147,1 mm· ±1 mm για εύρος).
 5. v = sqrt(2 g h / k), k = 1,4 (συμπαγής σφαίρα, κύλιση, επαφή σε ένα σημείο),
    όπου h η κατακόρυφη πτώση του κέντρου από την εκκίνηση.
 6. T = Σ ds / v  (ds τα μικρά τμήματα της καμπύλης του κέντρου, έως y = 220 mm).
"""
import sys
import numpy as np
from scipy.signal import medfilt
from scipy.interpolate import PchipInterpolator

g, k, r = 9.81, 1.4, 7.5
P = np.genfromtxt(sys.argv[1] if len(sys.argv) > 1 else "profiles.csv",
                  delimiter=",", skip_header=1)
ys = P[:, 0]
COL = {"straight": 1, "cycloid": 2, "polynomial": 3}
Y_START, Z_START_GROOVE = 4.0, 143.29     # αρχή του αυλακιού (y, z) σε mm


def lane(key, y0=7.0):
    z = P[:, COL[key]]
    if key == "straight":                  # ευθεία κλίσης 32,5° (τιμές σχεδίασης)
        y = np.array([Y_START, 220.0])
        return y, 145.837 - 0.6369 * y
    ok = ~np.isnan(z) & (ys >= y0) & (ys <= 220)
    y, zz = ys[ok], z[ok]
    keep = abs(zz - medfilt(zz, 5)) < 0.6
    y, zz = y[keep], np.minimum.accumulate(zz[keep])
    return np.r_[Y_START, y], np.r_[Z_START_GROOVE, zz]


def centre_path(y, z, n=60000):
    f = PchipInterpolator(y, z)
    yy = np.linspace(y[0], 220, n)
    zz, dz = f(yy), f(yy, 1)
    nx, nz = -dz / np.hypot(1, dz), 1 / np.hypot(1, dz)
    return yy + r * nx, zz + r * nz


def travel_time(key, z0c):
    yc, zc = centre_path(*lane(key))
    if zc[0] < z0c:
        yc, zc = np.r_[yc[0], yc], np.r_[z0c, zc]
    else:
        i = np.argmax(zc <= z0c)
        yc, zc = yc[i:], zc[i:]
    ds = np.hypot(np.diff(yc), np.diff(zc))
    h = np.maximum(zc[0] - 0.5 * (zc[1:] + zc[:-1]), 1e-4)       # mm
    v = np.sqrt(2 * g * h / 1000 / k)                              # m/s
    return np.sum(ds / 1000 / v) * 1000                            # ms


if __name__ == "__main__":
    for z0c in (146.1, 147.1, 148.1):
        t = {q: travel_time(q, z0c) for q in COL}
        print(f"z0 = {z0c}: T_straight {t['straight']:.1f}, T_cycloid {t['cycloid']:.1f}, "
              f"T_polynomial {t['polynomial']:.1f} ms | "
              f"E-K {t['straight']-t['cycloid']:.1f}, P-K {t['polynomial']-t['cycloid']:.1f}, "
              f"E-P {t['straight']-t['polynomial']:.1f}")
