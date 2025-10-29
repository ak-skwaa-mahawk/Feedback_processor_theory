mkdir -p docs/theory src/scrape_theory src/adversarial_defense tests/scrape_theory
touch docs/theory/inverse_square_scrape_theory.md
touch docs/theory/isst_examples.md
touch src/scrape_theory/{__init__.py,scrape_detector.py,glyph_generator.py,coherence.py,codex.py,propagation.py}
touch src/adversarial_defense/isst_defense.py
touch tests/scrape_theory/test_inverse_square.py