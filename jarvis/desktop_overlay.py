import sys
import threading
from typing import Optional
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QColor, QFont

class OverlaySignals(QObject):
    show_toast = pyqtSignal(str, str, int)
    update_status = pyqtSignal(str)

class ToastNotification(QWidget):
    def __init__(self, title: str, message: str, duration_ms: int):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(10, 20, 30, 220);
                border: 2px solid #00FFFF;
                border-radius: 10px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #00FFFF; font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("color: white; font-size: 14px;")
        self.message_label.setWordWrap(True)
        self.layout.addWidget(self.message_label)
        
        self.adjustSize()
        
        screen = QApplication.primaryScreen().geometry()
        self.start_x = screen.width()
        self.target_x = screen.width() - self.width() - 20
        self.y_pos = 100
        
        self.setGeometry(self.start_x, self.y_pos, self.width(), self.height())
        
        self.anim_in = QPropertyAnimation(self, b"geometry")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(QRect(self.start_x, self.y_pos, self.width(), self.height()))
        self.anim_in.setEndValue(QRect(self.target_x, self.y_pos, self.width(), self.height()))
        self.anim_in.start()
        
        QTimer.singleShot(duration_ms, self.close_animation)
        
    def close_animation(self):
        self.anim_out = QPropertyAnimation(self, b"geometry")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(QRect(self.target_x, self.y_pos, self.width(), self.height()))
        self.anim_out.setEndValue(QRect(self.start_x, self.y_pos, self.width(), self.height()))
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()

class HUDOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.status_label = QLabel("JARVIS: IDLE")
        self.status_label.setStyleSheet("""
            color: #00FFFF;
            font-size: 18px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 150);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #00FFFF;
        """)
        self.layout.addWidget(self.status_label)
        
        self.adjustSize()
        
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 20)
        
    def update_status(self, status: str):
        color_map = {
            "LISTENING": "#00FF00",
            "PROCESSING": "#00FFFF",
            "SPEAKING": "#FF00FF",
            "IN_CALL": "#FF0000",
            "IDLE": "#888888"
        }
        color = color_map.get(status, "#00FFFF")
        self.status_label.setText(f"JARVIS: {status}")
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-size: 18px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 150);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid {color};
        """)

class OverlayManager:
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.hud: Optional[HUDOverlay] = None
        self.signals = OverlaySignals()
        self.toasts = []
        
        self.thread = threading.Thread(target=self._run_app, daemon=True)
        self.thread.start()
        
    def _run_app(self):
        self.app = QApplication(sys.argv)
        self.hud = HUDOverlay()
        self.hud.show()
        
        self.signals.show_toast.connect(self._create_toast)
        self.signals.update_status.connect(self.hud.update_status)
        
        self.app.exec()
        
    def _create_toast(self, title: str, message: str, duration_ms: int):
        toast = ToastNotification(title, message, duration_ms)
        toast.show()
        self.toasts.append(toast)
        # Oczyszczanie nieaktywnych powiadomień
        self.toasts = [t for t in self.toasts if t.isVisible()]

    def show_toast(self, title: str, message: str, duration_ms: int = 4000):
        self.signals.show_toast.emit(title, message, duration_ms)
        
    def set_status(self, status: str):
        self.signals.update_status.emit(status)
