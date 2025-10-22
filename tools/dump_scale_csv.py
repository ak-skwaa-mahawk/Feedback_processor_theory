# tools/dump_scale_csv.py
import csv
from decimal import Decimal, getcontext
from core.scale import series, humanize_meters
from core.constants import DEFAULT_TOP_BANDS

getcontext().prec = 60

def main(n0=0, n1=DEFAULT_TOP_BANDS, out_path="scale_ladder.csv"):
    rows = [("band", "length_m_raw", "value", "unit")]
    for n, L in series(n0, n1):
        val, unit = humanize_meters(L, sig=6)
        rows.append((n, str(L), val, unit))
    with open(out_path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"Wrote {out_path} with {len(rows)-1} rows.")

if __name__ == "__main__":
    main()
