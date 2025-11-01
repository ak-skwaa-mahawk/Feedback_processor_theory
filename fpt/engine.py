# fpt/engine.py (example snippet)
from fpt.utils.handshake import handshake_message

def run_feedback_cycle(session_id: str, inputs):
    # Start receipt (Ignition)
    handshake_message(
        seed=f"FPT:cycle_start:{session_id}",
        log_file="logs/handshake_log.json"
    )

    # ... your processing here ...
    result = process(inputs)

    # End receipt (Seal/Return)
    handshake_message(
        seed=f"FPT:cycle_end:{session_id}|status=ok",
        log_file="logs/handshake_log.json"
    )
    return result