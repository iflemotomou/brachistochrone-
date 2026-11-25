"""Εξαγωγή των προφίλ z(y) των τριών τροχιών από το αρχείο STL.

Χρήση:  python extract_profiles.py Brachistochrone_run.stl profiles.csv

Το STL είναι δυαδικό (binary). Για κάθε y κόβουμε το μοντέλο με επίπεδο y = σταθερό
και, σε λωρίδα ±1 mm γύρω από τον άξονα κάθε αυλακιού, κρατάμε το χαμηλότερο z
(πάνω από z = 4 mm, ώστε να αποκλειστεί η βάση). Οι θέσεις x των αξόνων είναι:
    ευθεία: x = 0,  κυκλοειδής: x = 17,5,  πολυωνυμική: x = 35  (mm, σύστημα STL)
"""
import sys
import numpy as np

LANES = {"straight": 0.0, "cycloid": 17.5, "polynomial": 35.0}


def read_binary_stl(path):
    with open(path, "rb") as f:
        f.seek(80)
        n = int(np.frombuffer(f.read(4), dtype="<u4")[0])
        rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        data = np.frombuffer(f.read(n * 50), dtype=rec)
    return data["v"].astype(float)          # (n, 3 κορυφές, 3 συντεταγμένες)


def section(v, ymin, ymax, yc):
    """Σημεία τομής των τριγώνων με το επίπεδο y = yc, ως (x, z)."""
    m = (ymin < yc) & (ymax > yc)
    t = v[m]
    out = []
    for i in range(3):
        a, b = t[:, i], t[:, (i + 1) % 3]
        da, db = a[:, 1] - yc, b[:, 1] - yc
        k = da * db < 0
        s = (da[k] / (da[k] - db[k]))[:, None]
        out.append((a[k] + s * (b[k] - a[k]))[:, [0, 2]])
    return np.vstack(out)


def main(stl, out_csv):
    v = read_binary_stl(stl)
    ymin, ymax = v[:, :, 1].min(1), v[:, :, 1].max(1)
    ys = np.arange(1, 222, 0.5)
    cols = {k: [] for k in LANES}
    for y in ys:
        p = section(v, ymin, ymax, y)
        for k, c in LANES.items():
            q = p[(abs(p[:, 0] - c) < 1.0) & (p[:, 1] > 4.0)]
            cols[k].append(q[:, 1].min() if len(q) else np.nan)
    arr = np.column_stack([ys] + [cols[k] for k in LANES])
    np.savetxt(out_csv, arr, delimiter=",", fmt="%.4f",
               header="y_mm,z_straight_mm,z_cycloid_mm,z_polynomial_mm", comments="")
    print("γράφτηκε", out_csv, arr.shape)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
