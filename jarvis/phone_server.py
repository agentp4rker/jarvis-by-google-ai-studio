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
        # System subskrypcji zdarzeń
        self.event_waiters: Dict[str, asyncio.Future] = {}

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
                
                print(f"[PhoneServer] Odebrano: {data}")

                # Obsługa zdarzeń nasłuchujących (np. w autonomicznych agentach)
                if event_type in self.event_waiters and not self.event_waiters[event_type].done():
                    self.event_waiters[event_type].set_result(data)
                
                # Zdarzenie dedykowane: incoming_call
                if event_type == "incoming_call" and self.incoming_call_callback:
                    asyncio.create_task(self.incoming_call_callback(data))
                
            except json.JSONDecodeError:
                print(f"[PhoneServer] Błąd dekodowania JSON: {message}")
            except Exception as e:
                print(f"[PhoneServer] Błąd przetwarzania: {e}")

    async def send_command(self, command: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.clients:
            return {"status": "error", "message": "Brak połączonego urządzenia (Android)"}
            
        data = {"command": command}
        if payload:
            data.update(payload)
            
        message = json.dumps(data)
        
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
                
        self.clients -= disconnected
        return {"status": "success", "command": command}

    async def wait_for_event(self, event_name: str, timeout: int = 30) -> Dict[str, Any]:
        """Zatrzymuje wykonanie do czasu otrzymania z telefonu ramki JSON z danym 'event'."""
        future = asyncio.get_event_loop().create_future()
        self.event_waiters[event_name] = future
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            return {"status": "timeout", "event": event_name}
        finally:
            self.event_waiters.pop(event_name, None)

    async def start(self):
        self.server = await websockets.serve(self.register, self.host, self.port)
        print(f"[PhoneServer] Nasłuchiwanie WebSocket uruchomione na ws://{self.host}:{self.port}")

    def on_incoming_call(self, callback: Callable[[Dict[str, Any]], None]):
        self.incoming_call_callback = callback
