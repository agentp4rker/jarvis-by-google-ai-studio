import asyncio
from phone_server import PhoneWebSocketServer
from desktop_overlay import OverlayManager
from phone_controller import PhoneController
from gemini_bridge import GeminiBridge
import desktop_control

async def main():
    print("==================================================")
    print(" INICJALIZACJA SYSTEMU J.A.R.V.I.S. (Windows 10)  ")
    print("==================================================")
    
    try:
        # 1. Start Overlay GUI (działa w osobnym wątku, bezpieczne dla asyncio)
        overlay = OverlayManager()
        overlay.show_toast("J.A.R.V.I.S.", "Inicjalizacja systemów rdzennych...", 3000)
        overlay.set_status("INITIALIZING")
        
        # 2. Serwer WebSocket dla komunikacji z Androidem
        ws_server = PhoneWebSocketServer(host="0.0.0.0", port=8765)
        
        # 3. Phone Controller (Automatyzacja połączeń / SMS)
        phone_controller = PhoneController(ws_server, overlay)
        
        # Przypisanie zdarzenia przychodzącego połączenia do Asystenta
        ws_server.on_incoming_call(phone_controller.incoming_call_agent)
        
        # 4. Gemini Bridge (Dyspozytor narzędzi Function Calling)
        gemini = GeminiBridge(phone_controller)
        
        # Uruchomienie serwera
        await ws_server.start()
        
        overlay.set_status("IDLE")
        overlay.show_toast("J.A.R.V.I.S.", "System online. Nasłuchuję połączeń i komend...", 5000)
        desktop_control.speak_on_pc("System JARVIS jest online i gotowy do pracy.")
        print("[✓] J.A.R.V.I.S. is online and ready.")
        
        # Pętla główna utrzymująca asynchroniczny proces przy życiu
        await asyncio.Future()
        
    except KeyboardInterrupt:
        print("\\n[!] Wyłączanie systemu J.A.R.V.I.S...")
        if 'overlay' in locals():
            overlay.set_status("OFFLINE")
            overlay.show_toast("System", "Zamykanie...", 2000)
    except Exception as e:
        print(f"[ERROR] Krytyczny błąd systemu: {e}")

if __name__ == "__main__":
    # Uruchomienie pętli asynchronicznej
    asyncio.run(main())
