import inspect
import desktop_control
from phone_controller import PhoneController
from typing import Dict, Any, Callable

class GeminiBridge:
    def __init__(self, phone_controller: PhoneController):
        self.phone = phone_controller
        self.tools: Dict[str, Callable] = {}
        self._register_tools()

    def _register_tools(self):
        # Narzędzia Desktop Windows
        self.tools["focus_app"] = desktop_control.focus_app
        self.tools["close_app"] = desktop_control.close_app
        self.tools["resize_and_move_window"] = desktop_control.resize_and_move_window
        self.tools["control_media"] = desktop_control.control_media
        self.tools["take_screenshot"] = desktop_control.take_screenshot
        self.tools["lock_workstation"] = desktop_control.lock_workstation
        self.tools["execute_shell_command"] = desktop_control.execute_shell_command
        
        # Narzędzia Android Phone Controller
        self.tools["make_call"] = self.phone.make_call
        self.tools["answer_call"] = self.phone.answer_call
        self.tools["hang_up"] = self.phone.hang_up
        self.tools["send_sms"] = self.phone.send_sms
        self.tools["read_latest_sms"] = self.phone.read_latest_sms
        self.tools["get_phone_status"] = self.phone.get_phone_status
        self.tools["get_notifications"] = self.phone.get_notifications
        self.tools["make_reservation"] = self.phone.make_reservation
        self.tools["execute_autonomous_call"] = self.phone.execute_autonomous_call

    def get_tool_declarations(self) -> list:
        declarations = []
        for name, func in self.tools.items():
            declarations.append({
                "name": name,
                "description": func.__doc__ or f"Execute {name}"
            })
        return declarations

    async def handle_tool_call(self, tool_name: str, args: dict) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Narzędzie {tool_name} nie istnieje."}
            
        func = self.tools[tool_name]
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**args)
            else:
                result = func(**args)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
