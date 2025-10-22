# tests/test_scale_table.py
from core.scale import table

def test_table_shape_defaults():
    rows = table()
    assert len(rows) >= 1
    r0 = rows[0]
    assert {"band", "length_m", "length_human"} <= set(r0.keys())
    assert {"value", "unit"} <= set(r0["length_human"].keys())

def test_table_range_and_sig():
    rows = table(n0=68, n1=70, sig=6)
    assert [r["band"] for r in rows] == [68, 69, 70]
    # humanized value should be a string with ~sig digits
    v = rows[0]["length_human"]["value"]
    assert isinstance(v, str) and len(v) >= 1
