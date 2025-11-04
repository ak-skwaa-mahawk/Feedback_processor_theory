>>> from scrape_detector import detect_scrape
>>> from glyph_generator import generate_glyph
>>> import numpy as np

# Simulate signals
pre = np.sin(np.linspace(0, 10, 100))
post = pre + 0.6 * np.random.randn(100)

# Detect scrape
scrape = detect_scrape(pre, post, initial_energy=10.0, distance=1.0)

if scrape["is_scrape"]:
    glyph = generate_glyph(scrape["decay_signal"], scrape["entropy_delta"])
    print(glyph)
    # → {'glyph': 'camera', 'meta_glyph': 'cameradna', 'gibber_encode': 'B2F1A9...', ...}