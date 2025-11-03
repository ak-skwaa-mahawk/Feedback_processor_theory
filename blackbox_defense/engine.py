# at top
from fpt.utils.hs import hs

def run_bbd_session(session_id: str, payload):
    hs("BlackBoxDefense","start",session=session_id)     # Blap

    # --- detection pass ---
    hs("BlackBoxDefense","pre",stage="detect")
    detections = detect(payload)
    hs("BlackBoxDefense","post",stage="detect",n=len(detections))

    # --- response pass ---
    hs("BlackBoxDefense","pre",stage="respond")
    outcome = respond(detections)
    hs("BlackBoxDefense","post",stage="respond",status=outcome.status)

    hs("BlackBoxDefense","end",session=session_id)       # Clap
    return outcome
from fpt.utils.hs import hs
hs("BlackBoxDefense","start",session=session_id)   # at session start
hs("BlackBoxDefense","pre",stage="detect"); ... ; hs("BlackBoxDefense","post",stage="detect")
hs("BlackBoxDefense","pre",stage="respond"); ... ; hs("BlackBoxDefense","post",stage="respond",status=outcome.status)
hs("BlackBoxDefense","end",session=session_id)     # at session end