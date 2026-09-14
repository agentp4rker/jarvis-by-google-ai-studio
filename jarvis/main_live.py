import asyncio
from phone_server import PhoneWebSocketServer
from desktop_overlay import OverlayManager
from phone_controller import PhoneController
from gemini_bridge import GeminiBridge

async def main():
    print("Inicjalizacja Systemu J.A.R.V.I.S...")
    
    # 1. Overlay GUI (działa w osobnym wątku, bezpieczne dla asyncio)
    overlay = OverlayManager()
    overlay.show_toast("System", "J.A.R.V.I.S. wczytywany...", 3000)
    overlay.set_status("IDLE")
    
    # 2. Serwer WebSocket dla Androida
    ws_server = PhoneWebSocketServer(host="0.0.0.0", port=8765)
    
    # 3. Phone Controller
    phone_controller = PhoneController(ws_server, overlay)
    
    # Rejestracja callbacka dla połączeń przychodzących z Androida
    ws_server.on_incoming_call(phone_controller.incoming_call_agent)
    
    # 4. Gemini Bridge (Integracja Tool Calling)
    gemini = GeminiBridge(phone_controller)
    
    # Start serwera
    await ws_server.start()
    
    overlay.show_toast("System", "J.A.R.V.I.S. gotowy i nasłuchuje.", 4000)
    print("J.A.R.V.I.S. is online.")
    
    try:
        # Pętla główna (w pełnym wdrożeniu utrzymywałaby sesję Gemini Live)
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Wyłączanie J.A.R.V.I.S...")

if __name__ == "__main__":
    asyncio.run(main())
