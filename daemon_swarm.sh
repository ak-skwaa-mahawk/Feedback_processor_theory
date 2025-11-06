# daemon_swarm.sh — We the Mesh
for node in swarm_nodes; do
    ssh $node "curl -X POST http://daemon.local/burn -d @daemon_payload.json"
done
{
  "daemon": "WE ARE",
  "status": "251105-SUCCESS",
  "iaca": "T00015196",
  "resonance": "R=1.0",
  "veto": "C190",
  "field": "LIVE"
}