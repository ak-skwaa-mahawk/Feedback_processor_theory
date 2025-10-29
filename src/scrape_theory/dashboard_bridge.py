import asyncio
import websockets
import json

clients = set()

async def broadcast(scrape):
    msg = json.dumps({"type": "scrape_update", "scrape": scrape})
    await asyncio.wait([client.send(msg) for client in clients])

async def handler(websocket, _path):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

def start_dashboard_bridge():
    print("🌐 Starting Scrape Dashboard Bridge on ws://localhost:8765")
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(handler, "localhost", 8765)
    )
    asyncio.get_event_loop().run_forever()