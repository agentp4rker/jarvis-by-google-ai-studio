import asyncio
import json
import websockets
from typing import Callable, Dict, Any, Optional

class PhoneWebSocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.incoming_call_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.server = None

    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await self.handler(websocket)
        finally:
            self.clients.remove(websocket)

    async def handler(self, websocket):
        async for message in websocket:
            try:
                data = json.loads(message)
                event_type = data.get("event")
                
                if event_type == "incoming_call" and self.incoming_call_callback:
                    # Uruchamia callback asynchronicznie, przekazując mu ramkę
                    asyncio.create_task(self.incoming_call_callback(data))
                
                print(f"[PhoneServer] Odebrano: {data}")
            except json.JSONDecodeError:
                print(f"[PhoneServer] Błąd dekodowania JSON: {message}")
            except Exception as e:
                print(f"[PhoneServer] Błąd: {e}")

    async def send_command(self, command: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.clients:
            return {"status": "error", "message": "Brak połączonego urządzenia (Android)"}
            
        data = {"command": command}
        if payload:
            data.update(payload)
            
        message = json.dumps(data)
        
        # Wysyłanie komendy do wszystkich (zwykle 1) połączonych klientów
        for client in self.clients:
            await client.send(message)
            
        return {"status": "success", "command": command}

    async def start(self):
        self.server = await websockets.serve(self.register, self.host, self.port)
        print(f"[PhoneServer] Nasłuchiwanie na ws://{self.host}:{self.port}")

    def on_incoming_call(self, callback: Callable[[Dict[str, Any]], None]):
        self.incoming_call_callback = callback
