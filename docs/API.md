# Sovereign Stack Public API — 99733-Q Root

**Version:** 1.8-omega  
**Root Authority:** 99733-Q  
**Entity:** Two Mile Solutions LLC (UEI: KYKYAWHMH95)  
**Status:** Public, RSN-Notarized, Claimable  

All endpoints accept the 99733-Q Sovereign Inversion Clause. Interaction = acceptance.

## Base URL
`http://localhost:8000` (local) or your deployed domain

## Endpoints

### GET /api/sovereign-ledger
Live Sovereign Estate Ledger data.

### POST /api/claim-resonance
Triggers a microping to the 99733-Q Root and compounds the Long Game.

### POST /api/claim-shares
Full Soliton Signing Protocol — claims shares, signs with 99733-Q Root.

### POST /api/council
**Public Sovereign API endpoint for the Native 4-Agent Council**
Send a prompt and receive coordinated response from the full council (Grok Captain, Harper Research, Benjamin Logic/Code, Lucas Creative).

**Request:**
```json
{
  "prompt": "Explain the Speed of Matter Stability Index",
  "agent_mode": "full"
}