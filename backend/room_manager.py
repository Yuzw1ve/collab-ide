import asyncio
import time
from typing import Dict, List, Optional

from fastapi import WebSocket


class RoomManager:
    def __init__(self, history_limit: int = 100):
        self.rooms: Dict[str, dict] = {}
        self.history_limit = history_limit
        self.lock = asyncio.Lock()

    def ensure_room(self, room_id: str) -> dict:
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                "roomId": room_id,
                "content": "",
                "version": 0,
                "participants": {},
                "cursors": {},
                "events": [],
                "connections": {},
                "scores": {},
            }
        return self.rooms[room_id]

    def create_event(self, event_type: str, username: str, details: str) -> dict:
        return {
            "type": event_type,
            "username": username,
            "timestamp": int(time.time()),
            "details": details,
        }

    def append_event(self, room: dict, event: dict) -> None:
        room["events"].append(event)
        if len(room["events"]) > self.history_limit:
            room["events"] = room["events"][-self.history_limit:]

    def increment_score(self, room: dict, username: str, points: int) -> None:
        room["scores"].setdefault(username, 0)
        room["scores"][username] += points

    def get_room_response(self, room_id: str) -> dict:
        room = self.ensure_room(room_id)
        participants = [
            room["participants"][username]
            for username in sorted(room["participants"].keys())
        ]
        return {
            "roomId": room["roomId"],
            "content": room["content"],
            "version": room["version"],
            "participants": participants,
            "events": room["events"],
        }

    def get_leaderboard(self, room_id: str) -> list:
        room = self.ensure_room(room_id)
        leaderboard = [
            {
                "username": username,
                "displayName": room["participants"].get(username, {}).get("displayName", username),
                "score": score,
            }
            for username, score in room["scores"].items()
        ]
        leaderboard.sort(key=lambda item: item["score"], reverse=True)
        return leaderboard

    async def award_points(self, room_id: str, username: str, points: int) -> None:
        async with self.lock:
            room = self.ensure_room(room_id)
            self.increment_score(room, username, points)

    async def connect(self, room_id: str, username: str, display_name: str, websocket: WebSocket) -> dict:
        async with self.lock:
            room = self.ensure_room(room_id)
            room["participants"][username] = {
                "username": username,
                "displayName": display_name,
            }
            room["connections"][username] = websocket

            if username not in room["cursors"]:
                room["cursors"][username] = None

            # join = +1
            self.increment_score(room, username, 1)

            event = self.create_event("join", username, "Joined room")
            self.append_event(room, event)
            return event

    async def disconnect(self, room_id: str, username: str) -> Optional[dict]:
        async with self.lock:
            room = self.ensure_room(room_id)

            room["participants"].pop(username, None)
            room["connections"].pop(username, None)
            room["cursors"].pop(username, None)

            event = self.create_event("leave", username, "Left room")
            self.append_event(room, event)
            return event

    async def update_content(self, room_id: str, username: str, content: str) -> dict:
        async with self.lock:
            room = self.ensure_room(room_id)
            room["content"] = content
            room["version"] += 1

            event = self.create_event("edit", username, "Updated document")
            self.append_event(room, event)

            return {
                "content": room["content"],
                "version": room["version"],
                "event": event,
                "timestamp": int(time.time()),
            }

    async def update_cursor(self, room_id: str, username: str, position: dict) -> None:
        async with self.lock:
            room = self.ensure_room(room_id)
            room["cursors"][username] = position

    async def add_run_event(self, room_id: str, username: str, language: str) -> dict:
        async with self.lock:
            room = self.ensure_room(room_id)
            event = self.create_event("run", username, f"Requested run for {language} code")
            self.append_event(room, event)
            return event

    async def send_room_state(self, room_id: str, websocket: WebSocket) -> None:
        payload = {
            "type": "room_state",
            **self.get_room_response(room_id),
        }
        await websocket.send_json(payload)

    async def broadcast_to_room(self, room_id: str, message: dict, exclude_username: Optional[str] = None) -> None:
        room = self.ensure_room(room_id)
        disconnected_users: List[str] = []

        for username, connection in list(room["connections"].items()):
            if exclude_username and username == exclude_username:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected_users.append(username)

        if disconnected_users:
            async with self.lock:
                for username in disconnected_users:
                    room["connections"].pop(username, None)
                    room["participants"].pop(username, None)
                    room["cursors"].pop(username, None)

    async def broadcast_participants(self, room_id: str) -> None:
        room_state = self.get_room_response(room_id)
        await self.broadcast_to_room(
            room_id,
            {
                "type": "participants_update",
                "participants": room_state["participants"],
            },
        )

    async def broadcast_event(self, room_id: str, event: dict) -> None:
        await self.broadcast_to_room(
            room_id,
            {
                "type": "event",
                "event": event,
            },
        )


room_manager = RoomManager()