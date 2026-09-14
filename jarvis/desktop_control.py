import os
import ctypes
import subprocess
import json
import psutil
import pyautogui
import time
from typing import Dict, Any, Optional

try:
    import win32gui
    import win32con
    import win32api
    import win32process
except ImportError:
    # Ignorowane na systemach innych niż Windows w celu zachowania możliwości analizy kodu
    pass

def get_hwnds_for_pid(pid: int) -> list:
    hwnds = []
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def find_window_by_name(name: str) -> Optional[int]:
    name_lower = name.lower()
    target_hwnd = None
    
    # 1. Szukanie po fragmencie tytułu okna
    def callback(hwnd, extra):
        nonlocal target_hwnd
        if target_hwnd is not None:
            return True
        title = win32gui.GetWindowText(hwnd).lower()
        if win32gui.IsWindowVisible(hwnd) and name_lower in title:
            target_hwnd = hwnd
        return True
    win32gui.EnumWindows(callback, None)
    
    if target_hwnd:
        return target_hwnd

    # 2. Szukanie po nazwie procesu (.exe)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and name_lower in proc.info['name'].lower():
                hwnds = get_hwnds_for_pid(proc.info['pid'])
                if hwnds:
                    return hwnds[0]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    return None

def focus_app(application_name: str) -> Dict[str, Any]:
    try:
        hwnd = find_window_by_name(application_name)
        if not hwnd:
            return {"status": "error", "message": f"Nie znaleziono okna dla '{application_name}'."}
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        title = win32gui.GetWindowText(hwnd)

        # Przywrócenie okna, jeśli jest zminimalizowane
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Omijanie "Focus Stealing Prevention"
        current_thread_id = win32api.GetCurrentThreadId()
        foreground_hwnd = win32gui.GetForegroundWindow()
        window_thread_id = win32gui.GetWindowThreadProcessId(foreground_hwnd)[0] if foreground_hwnd else 0
        
        if current_thread_id != window_thread_id and window_thread_id != 0:
            win32process.AttachThreadInput(current_thread_id, window_thread_id, True)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            win32process.AttachThreadInput(current_thread_id, window_thread_id, False)
        else:
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)

        return {"status": "focused", "title": title, "pid": pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def close_app(application_name: str) -> Dict[str, Any]:
    try:
        hwnd = find_window_by_name(application_name)
        if hwnd:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            win32api.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return {"status": "closed", "method": "WM_CLOSE", "pid": pid}
        
        # Fallback - siłowe zamknięcie przez psutil
        name_lower = application_name.lower()
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and name_lower in proc.info['name'].lower():
                    proc.kill()
                    killed.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        if killed:
            return {"status": "closed", "method": "process_kill", "pids": killed}
            
        return {"status": "error", "message": f"Nie znaleziono aplikacji '{application_name}'."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def resize_and_move_window(application_name: str, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    try:
        hwnd = find_window_by_name(application_name)
        if not hwnd:
            return {"status": "error", "message": f"Nie znaleziono okna dla '{application_name}'."}
        
        if win32gui.IsZoomed(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, width, height, win32con.SWP_SHOWWINDOW)
        title = win32gui.GetWindowText(hwnd)
        return {"status": "moved_and_resized", "title": title, "rect": {"x": x, "y": y, "width": width, "height": height}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def control_media(action: str) -> Dict[str, Any]:
    try:
        VK_MEDIA_PLAY_PAUSE = 0xB3
        VK_MEDIA_NEXT_TRACK = 0xB0
        VK_MEDIA_PREV_TRACK = 0xB1
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF

        action_map = {
            "play_pause": VK_MEDIA_PLAY_PAUSE,
            "next": VK_MEDIA_NEXT_TRACK,
            "previous": VK_MEDIA_PREV_TRACK,
            "mute": VK_VOLUME_MUTE,
            "volume_down": VK_VOLUME_DOWN,
            "volume_up": VK_VOLUME_UP
        }

        if action not in action_map:
            return {"status": "error", "message": f"Nieznana akcja '{action}'"}
            
        vk_code = action_map[action]
        win32api.keybd_event(vk_code, win32api.MapVirtualKey(vk_code, 0), 0, 0)
        win32api.keybd_event(vk_code, win32api.MapVirtualKey(vk_code, 0), win32con.KEYEVENTF_KEYUP, 0)
        
        return {"status": "success", "action": action}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def take_screenshot(output_path: str = "screenshot.png") -> Dict[str, Any]:
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(output_path)
        return {"status": "success", "path": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def lock_workstation() -> Dict[str, Any]:
    try:
        ctypes.windll.user32.LockWorkStation()
        return {"status": "success", "action": "locked"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_shell_command(command: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "status": "executed",
            "command": command,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
