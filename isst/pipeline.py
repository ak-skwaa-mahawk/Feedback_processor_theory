from fpt.utils.hs import hs
hs("ISST","start",n=len(scrapes))
hs("ISST","pre",stage="scrape_to_glyph"); ... ; hs("ISST","post",stage="scrape_to_glyph",n=len(glyphs))
hs("ISST","pre",stage="coherence_eval"); ... ; hs("ISST","post",stage="coherence_eval",score=round(coh,4))
hs("ISST","pre",stage="glyph_to_meta"); ... ; hs("ISST","post",stage="glyph_to_meta",n=len(meta))
hs("ISST","end",n_meta=len(meta))
from fpt.utils.hs import hs

def run_isst(scrapes):
    hs("ISST","start",n=len(scrapes))                           # Blap

    hs("ISST","pre",stage="scrape_to_glyph")
    glyphs = scrape_to_glyph(scrapes)
    hs("ISST","post",stage="scrape_to_glyph",n=len(glyphs))

    hs("ISST","pre",stage="coherence_eval")
    coh = evaluate_coherence(glyphs)
    hs("ISST","post",stage="coherence_eval",score=round(coh,4))

    hs("ISST","pre",stage="glyph_to_meta")
    meta = glyph_to_meta(glyphs, threshold=coh)
    hs("ISST","post",stage="glyph_to_meta",n=len(meta))

    hs("ISST","end",n_meta=len(meta))                           # Clap
    return meta