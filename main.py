import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from market_status import get_market_status

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@app.get("/")
async def home():
    return {
        "message": "Market Status Backend Running"
    }


@app.get("/market-status")
async def market_status():
    return get_market_status()


@app.websocket("/ws/market-status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            status = get_market_status()
            await websocket.send_json(status)
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def market_status_broadcast_loop():
    while True:
        status = get_market_status()
        await manager.broadcast(status)
        await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(market_status_broadcast_loop())