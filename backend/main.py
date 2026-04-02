from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from runner.run_router import router as run_router
from websocket_handlers import router as websocket_router
from room_manager import room_manager
from ai.ai_router import router as ai_router

app = FastAPI(title="Collaborative IDE Backend MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router)
app.include_router(websocket_router)
app.include_router(ai_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str):
    room_id = room_id.strip()
    return room_manager.get_room_response(room_id)


@app.get("/api/rooms/{room_id}/leaderboard")
async def get_leaderboard(room_id: str):
    room_id = room_id.strip()
    return {
        "roomId": room_id,
        "leaderboard": room_manager.get_leaderboard(room_id),
    }