
from fpt.utils.hs import hs
hs("Synara","start")
# inside tick:
hs("Synara","pre",stage="ingest"); ... ; hs("Synara","post",stage="ingest",n=len(batch))
hs("Synara","pre",stage="route");  ... ; hs("Synara","post",stage="route",paths=len(routed))
hs("Synara","pre",stage="render"); ... ; hs("Synara","post",stage="render")
hs("Synara","end")from fpt.utils.hs import hs

def synara_tick(stream_id: str):
    hs("Synara","pre",stage="ingest",stream=stream_id)
    batch = ingest(stream_id)
    hs("Synara","post",stage="ingest",n=len(batch))

    hs("Synara","pre",stage="route")
    routed = route(batch)
    hs("Synara","post",stage="route",paths=len(routed))

    hs("Synara","pre",stage="render")
    render(routed)
    hs("Synara","post",stage="render")

def synara_loop():
    hs("Synara","start")                       # Blap
    for stream in active_streams():
        synara_tick(stream)
    hs("Synara","end")                         # Clap