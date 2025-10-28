# collision_engine.py
# Parallel Extremes → Land Back

def justify_their_law(action):
    if "control web" in action or "own satellite" in action:
        return "IACA VIOLATION: Web is Native Craft → Pay Families or Return Land"

def justify_our_law(action):
    if "govern signal" in action or "use glyph" in action:
        return "NATURAL LAW: Web is Land → Return to Families"

def collision(action):
    their = justify_their_law(action)
    ours = justify_our_law(action)
    
    if their and ours:
        return f"""
        JUSTIFICATION DETECTED:
        {their}
        {ours}
        
        END GOAL: LAND BACK TO INDIVIDUAL FAMILIES
        EXECUTED.
        """
    return "No justification. No land back."

# TEST
print(collision("SpaceX wants to control Starlink signals"))