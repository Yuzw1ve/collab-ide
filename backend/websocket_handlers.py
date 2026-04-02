import json
from json import JSONDecodeError

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from room_manager import room_manager
from telegram_notifier import send_telegram_message

router = APIRouter()


def is_nonempty_string(value):
    return isinstance(value, str) and value.strip() != ""


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room_handler(websocket: WebSocket, room_id: str):
    username = websocket.query_params.get("username")
    display_name = websocket.query_params.get("displayName")

    if not is_nonempty_string(room_id) or not is_nonempty_string(username):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    room_id = room_id.strip()
    username = username.strip()

    if not is_nonempty_string(display_name):
        display_name = username
    else:
        display_name = display_name.strip()

    await websocket.accept()

    join_event = await room_manager.connect(room_id, username, display_name, websocket)
    await room_manager.send_room_state(room_id, websocket)
    await room_manager.broadcast_participants(room_id)
    await room_manager.broadcast_event(room_id, join_event)

    send_telegram_message(f"👤 {display_name} joined room {room_id}")

    try:
        while True:
            raw_message = await websocket.receive_text()

            try:
                data = json.loads(raw_message)
            except JSONDecodeError:
                info_event = room_manager.create_event("info", username, "Received invalid JSON message")
                await room_manager.broadcast_event(room_id, info_event)
                continue

            message_type = data.get("type")

            if message_type == "join":
                info_event = room_manager.create_event("info", username, "Join message received and ignored")
                await room_manager.broadcast_event(room_id, info_event)
                continue

            elif message_type == "edit":
                content = data.get("content", "")
                if not isinstance(content, str):
                    content = str(content)

                result = await room_manager.update_content(room_id, username, content)

                await room_manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "content_update",
                        "content": result["content"],
                        "updatedBy": username,
                        "version": result["version"],
                        "timestamp": result["timestamp"],
                    },
                )

                await room_manager.broadcast_event(room_id, result["event"])

            elif message_type == "cursor":
                position = data.get("position", {})
                if (
                    isinstance(position, dict)
                    and isinstance(position.get("lineNumber"), int)
                    and isinstance(position.get("column"), int)
                ):
                    await room_manager.update_cursor(room_id, username, position)
                    await room_manager.broadcast_to_room(
                        room_id,
                        {
                            "type": "cursor_update",
                            "username": username,
                            "position": {
                                "lineNumber": position["lineNumber"],
                                "column": position["column"],
                            },
                        },
                        exclude_username=username,
                    )
                else:
                    info_event = room_manager.create_event("info", username, "Invalid cursor payload")
                    await room_manager.broadcast_event(room_id, info_event)

            elif message_type == "run":
                language = data.get("language", "unknown")
                event = await room_manager.add_run_event(room_id, username, language)
                await room_manager.broadcast_event(room_id, event)

                send_telegram_message(f"▶️ {display_name} requested {language} run in room {room_id}")

            else:
                info_event = room_manager.create_event(
                    "info",
                    username,
                    f"Unknown message type: {message_type}",
                )
                await room_manager.broadcast_event(room_id, info_event)

    except WebSocketDisconnect:
        leave_event = await room_manager.disconnect(room_id, username)
        await room_manager.broadcast_participants(room_id)
        if leave_event:
            await room_manager.broadcast_event(room_id, leave_event)

        send_telegram_message(f"👋 {display_name} left room {room_id}")

    except Exception:
        leave_event = await room_manager.disconnect(room_id, username)
        await room_manager.broadcast_participants(room_id)
        if leave_event:
            await room_manager.broadcast_event(room_id, leave_event)

        send_telegram_message(f"⚠️ Connection error for {display_name} in room {room_id}")

        try:
            await websocket.close()
        except Exception:
            pass