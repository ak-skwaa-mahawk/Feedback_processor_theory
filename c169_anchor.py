# c169_anchor.py
def hasC169Compliance(anchors):
    return any("C169" in a["hash"] for a in anchors)  # Oracle stub