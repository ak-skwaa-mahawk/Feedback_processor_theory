# resin_to_flame.py
def cold_press_spruce_resin(temp=-40):
    frozen_spruce = freeze_branch(temp)
    rosin = hydraulic_press(frozen_spruce, psi=3000)
    plastolene = pyrolyze(rosin, temp=420, catalyst="birch_char")
    return plastolene  # 42 MJ/kg, clean burn