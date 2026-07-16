from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.ws_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
