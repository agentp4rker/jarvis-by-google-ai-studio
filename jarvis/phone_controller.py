import asyncio
import json
from phone_server import PhoneWebSocketServer
from desktop_overlay import OverlayManager

class PhoneController:
    def __init__(self, ws_server: PhoneWebSocketServer, overlay: OverlayManager):
        self.ws = ws_server
        self.overlay = overlay
        
    async def make_call(self, number_or_contact: str) -> dict:
        self.overlay.show_toast("Telefon", f"Inicjowanie połączenia: {number_or_contact}")
        return await self.ws.send_command("make_call", {"target": number_or_contact})

    async def answer_call(self) -> dict:
        self.overlay.set_status("IN_CALL")
        return await self.ws.send_command("answer_call")

    async def hang_up(self) -> dict:
        self.overlay.set_status("IDLE")
        self.overlay.show_toast("Telefon", "Zakończono połączenie.")
        return await self.ws.send_command("hang_up")

    async def send_sms(self, recipient: str, message: str) -> dict:
        self.overlay.show_toast("SMS", f"Wysyłanie do {recipient}")
        return await self.ws.send_command("send_sms", {"recipient": recipient, "message": message})

    async def read_latest_sms(self, limit: int = 5) -> dict:
        return await self.ws.send_command("read_latest_sms", {"limit": limit})

    async def get_phone_status(self) -> dict:
        return await self.ws.send_command("get_phone_status")

    async def get_notifications(self) -> dict:
        return await self.ws.send_command("get_notifications")

    async def make_reservation(self, place_name: str, date_time: str, party_size: int, details: str = "") -> dict:
        instruction = f"Rezerwacja stolika w {place_name} na {date_time} dla {party_size} osób. Szczegóły: {details}"
        self.overlay.show_toast("J.A.R.V.I.S.", f"Rozpoczynam rezerwację: {place_name}")
        return await self.execute_autonomous_call(place_name, instruction)

    async def execute_autonomous_call(self, target_contact: str, goal_instruction: str) -> dict:
        # 1. Inicjuje połączenie
        await self.make_call(target_contact)
        self.overlay.set_status("IN_CALL")
        
        # 2. Aktywuje monitoring (symulacja oczekiwania na status "answered")
        await asyncio.sleep(2) 
        
        # W docelowym systemie tutaj byłby nasłuch na event "no_answer" po 30 sek lub "answered"
        # Przykład logiczny dla odebranego połączenia (otwarcie dwukierunkowego strumienia PCM):
        
        greeting = f"Cześć, nazywam się JARVIS, jestem osobistym asystentem Gracjana Pawła Nowackiego. Mam obowiązek zapytać: {goal_instruction}"
        print(f"[JARVIS SPEAKING]: {greeting}")
        self.overlay.show_toast("JARVIS", "Prowadzę autonomiczną rozmowę...", 8000)
        
        # 5. JARVIS słucha i analizuje w czasie rzeczywistym
        await asyncio.sleep(4) # Symulacja dialogu z Gemini Live
        
        # Po wyciągnięciu kompletnych informacji:
        goodbye = "Dziękuję bardzo za informację, przekażę wszystko Gracjanowi. Do widzenia."
        print(f"[JARVIS SPEAKING]: {goodbye}")
        
        # Rozłączenie
        await self.hang_up()
        
        # 8. Raportowanie na PC
        result_summary = "Uzyskano pomyślną odpowiedź." # Tu wchodziłoby podsumowanie od Gemini
        self.overlay.show_toast("Raport z rozmowy", f"Cel zrealizowany: {target_contact}\nPodsumowanie: {result_summary}", 6000)
        
        return {"status": "success", "summary": result_summary, "recipient": target_contact}

    async def incoming_call_agent(self, call_data: dict):
        caller = call_data.get("caller", "Nieznany")
        self.overlay.show_toast("Połączenie przychodzące", caller, 10000)
        
        # Oczekiwanie na decyzję użytkownika ("JARVIS, odbierz")
        await asyncio.sleep(2) 
        
        # W trybie auto / zgody:
        await self.answer_call()
        self.overlay.set_status("IN_CALL")
        
        greeting = "Cześć, nazywam się JARVIS, jestem osobistym asystentem Gracjana Pawła Nowackiego. Gracjan jest w tej chwili niedostępny. W jakim celu dzwonisz i co mam mu przekazać?"
        print(f"[JARVIS SPEAKING]: {greeting}")
        
        # Przesłuchanie rozmówcy (symulacja Live)
        await asyncio.sleep(4)
        
        reason = "Potrzebuję dokumentacji projektowej."
        urgency = "high"
        
        goodbye = "Dziękuję za informację. Zapisałem Twoją wiadomość i przekażę ją Gracjanowi, jak tylko będzie dostępny. Do widzenia."
        print(f"[JARVIS SPEAKING]: {goodbye}")
        
        await self.hang_up()
        
        report = {
            "caller": caller,
            "reason": reason,
            "urgency": urgency,
            "timestamp": "now"
        }
        
        # Trwałe powiadomienie ze streszczeniem
        self.overlay.show_toast("Podsumowanie połączenia", f"Od: {caller}\nPowód: {reason}\nPilność: {urgency}", 10000)
        return report
