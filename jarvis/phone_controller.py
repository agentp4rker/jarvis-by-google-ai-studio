import asyncio
import json
from phone_server import PhoneWebSocketServer
from desktop_overlay import OverlayManager
import desktop_control

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
        self.overlay.show_toast("J.A.R.V.I.S.", f"Rozpoczynam rezerwację: {place_name}", duration_ms=6000)
        return await self.execute_autonomous_call(place_name, instruction)

    async def execute_autonomous_call(self, target_contact: str, goal_instruction: str) -> dict:
        """
        Złożony proces autonomicznego agenta wychodzącego.
        Opiera się na komunikacji z serwerem WebSocket i obsłudze asynchronicznych eventów.
        """
        try:
            # 1. Inicjuje połączenie
            await self.make_call(target_contact)
            self.overlay.set_status("IN_CALL")
            
            # 2. Oczekujemy na odpowiedź o statusie połączenia
            call_event = await self.ws.wait_for_event("call_status", timeout=35)
            
            # 3. Weryfikacja statusu
            if call_event.get("status") == "timeout" or call_event.get("call_state") != "answered":
                await self.hang_up()
                msg = f"Brak odpowiedzi od {target_contact}"
                self.overlay.show_toast("Połączenie przerwane", msg, 5000)
                desktop_control.speak_on_pc(f"Gracjan, połączenie z {target_contact} nie zostało odebrane.")
                return {"status": "no_answer", "recipient": target_contact}

            # 4. Odebrano. Przekazujemy wymaganą formułkę.
            greeting = f"Cześć, nazywam się JARVIS, jestem osobistym asystentem Gracjana Pawła Nowackiego. Mam obowiązek zapytać: {goal_instruction}"
            await self.ws.send_command("speak_audio", {"text": greeting})
            self.overlay.set_status("SPEAKING")
            
            # 5. JARVIS słucha odpowiedzi
            self.overlay.set_status("LISTENING")
            self.overlay.show_toast("J.A.R.V.I.S. nasłuchuje", "Oczekiwanie na odpowiedź rozmówcy...", 8000)
            
            transcription_event = await self.ws.wait_for_event("transcription", timeout=60)
            
            if transcription_event.get("status") == "timeout":
                user_reply = "Rozmówca milczał lub nie zrozumiano wypowiedzi."
            else:
                user_reply = transcription_event.get("text", "Brak transkrypcji.")

            # 6. Zakończenie
            self.overlay.set_status("SPEAKING")
            goodbye = "Dziękuję bardzo za informację, przekażę wszystko Gracjanowi. Do widzenia."
            await self.ws.send_command("speak_audio", {"text": goodbye})
            await asyncio.sleep(4) # Czekamy aż TTS na telefonie wybrzmi
            
            await self.hang_up()
            
            # 7. Raportowanie na PC
            self.overlay.show_toast("Raport JARVIS", f"Rozmowa z {target_contact} zakończona.\\nOdpowiedź: {user_reply}", 10000)
            desktop_control.speak_on_pc(f"Gracjan, rozmawiałem z {target_contact}. Odpowiedział: {user_reply}")
            
            return {"status": "success", "summary": user_reply, "recipient": target_contact}

        except Exception as e:
            self.overlay.set_status("IDLE")
            return {"status": "error", "message": f"Wystąpił błąd w autonomicznej rozmowie: {str(e)}"}

    async def incoming_call_agent(self, call_data: dict):
        """
        Złożony proces automatycznej sekretarki wchodzącej.
        """
        try:
            caller = call_data.get("caller", "Nieznany Numer")
            self.overlay.show_toast("Połączenie przychodzące", f"Dzwoni: {caller}\\nTrwa analiza dyspozycji...", 10000)
            
            # Oczekiwanie krótkie przed odebraniem (np. na reakcję ręczną użytkownika)
            await asyncio.sleep(3) 
            
            # JARVIS odbiera
            await self.answer_call()
            self.overlay.set_status("IN_CALL")
            
            # Formułka powitalna
            self.overlay.set_status("SPEAKING")
            greeting = "Cześć, nazywam się JARVIS, jestem osobistym asystentem Gracjana Pawła Nowackiego. Gracjan jest w tej chwili niedostępny. W jakim celu dzwonisz i co mam mu przekazać?"
            await self.ws.send_command("speak_audio", {"text": greeting})
            
            # Nasłuch
            self.overlay.set_status("LISTENING")
            transcription_event = await self.ws.wait_for_event("transcription", timeout=45)
            reason = transcription_event.get("text", "Nie zdołano zarejestrować wiadomości.")
            
            # Formułka pożegnalna
            self.overlay.set_status("SPEAKING")
            goodbye = "Dziękuję za informację. Zapisałem Twoją wiadomość i przekażę ją Gracjanowi, jak tylko będzie dostępny. Do widzenia."
            await self.ws.send_command("speak_audio", {"text": goodbye})
            await asyncio.sleep(5)
            
            await self.hang_up()
            
            # Raport JSON
            report = {
                "caller": caller,
                "reason": reason,
                "urgency": "medium",
                "timestamp": "now"
            }
            
            # Raportowanie na PC
            self.overlay.show_toast("Nowa Wiadomość Głosowa", f"Od: {caller}\\nTreść: {reason}", 15000)
            desktop_control.speak_on_pc(f"Gracjan, odebrałem połączenie od {caller}. Zostawił wiadomość: {reason}")
            
            return report
        except Exception as e:
            self.overlay.set_status("IDLE")
            print(f"[Agent Przychodzący] Błąd: {e}")
