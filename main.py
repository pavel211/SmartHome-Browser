import os
import sys
import configparser

os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

from PySide6.QtCore import Qt, QUrl, QTimer, QEvent
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QStyle
)
from PySide6.QtWebEngineWidgets import QWebEngineView


# ---------------- CONFIG PATH (FIXED) ----------------

APP_DIR = os.path.join(
    os.getenv("APPDATA"),
    "SmartHomeBrowser"
)

os.makedirs(APP_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(APP_DIR, "config.ini")
SERVER_NAME = "smart_home_browser"


class SettingsDialog(QDialog):
    """Простое окно настроек"""

    def __init__(self, parent, url, width, height):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.url_edit = QLineEdit(url)
        self.width_edit = QLineEdit(str(width))
        self.height_edit = QLineEdit(str(height))

        form = QFormLayout()
        form.addRow("URL:", self.url_edit)
        form.addRow("Width:", self.width_edit)
        form.addRow("Height:", self.height_edit)

        btn = QPushButton("Save")
        btn.clicked.connect(self.accept)

        form.addWidget(btn)
        self.setLayout(form)

    def get_values(self):
        return (
            self.url_edit.text(),
            int(self.width_edit.text()),
            int(self.height_edit.text())
        )


class SmartHomeBrowser(QWidget):

    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.load_config()

        self._ignore_focus_loss = False

        self.init_ui()
        self.init_tray()
        self.init_ipc()

    # ---------------- CONFIG ----------------

    def load_config(self):

        if not os.path.exists(CONFIG_FILE):
            self.create_default_config()

        self.config.read(CONFIG_FILE, encoding="utf-8")

        self.url = self.config.get("Browser", "url", fallback="https://google.com")
        self.window_width = self.config.getint("Window", "width", fallback=1200)
        self.window_height = self.config.getint("Window", "height", fallback=800)

    def create_default_config(self):

        self.config["Browser"] = {"url": "https://google.com"}
        self.config["Window"] = {"width": "1200", "height": "800"}

        self.save_config_file()

    def save_config_file(self):

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)

    def save_runtime_config(self):

        self.config["Browser"]["url"] = self.url
        self.config["Window"]["width"] = str(self.width())
        self.config["Window"]["height"] = str(self.height())

        self.save_config_file()

    # ---------------- UI ----------------

    def init_ui(self):

        self.setWindowTitle("Умный дом")

        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.resize(self.window_width, self.window_height)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        self.browser.load(QUrl(self.url))

        self.layout.addWidget(self.browser)

        self.installEventFilter(self)

    # ---------------- IPC ----------------

    def init_ipc(self):

        self.server = QLocalServer(self)
        QLocalServer.removeServer(SERVER_NAME)

        self.server.newConnection.connect(self.handle_connection)
        self.server.listen(SERVER_NAME)

    def handle_connection(self):

        socket = self.server.nextPendingConnection()
        socket.waitForReadyRead()

        cmd = bytes(socket.readAll()).decode().strip()

        if cmd == "show":
            self.show_window()
        elif cmd == "hide":
            self.hide()

        socket.disconnectFromServer()

    # ---------------- SHOW / HIDE ----------------

    def show_window(self):

        self._ignore_focus_loss = True

        self.show()

        QTimer.singleShot(0, self.place_window)

        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)

        QTimer.singleShot(800, self.unlock)

    def place_window(self):

        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()

        x = 0
        y = geo.y() + geo.height() - self.height()

        self.move(x, y)

    def unlock(self):
        self._ignore_focus_loss = False

    # ---------------- AUTO HIDE ----------------

    def eventFilter(self, obj, event):

        if event.type() == QEvent.WindowDeactivate:
            if not self._ignore_focus_loss:
                self.hide()
                return True

        return super().eventFilter(obj, event)

    # ---------------- SETTINGS ----------------

    def open_settings(self):

        dlg = SettingsDialog(self, self.url, self.width(), self.height())

        if dlg.exec():

            url, w, h = dlg.get_values()

            self.url = url
            self.resize(w, h)

            self.browser.load(QUrl(url))

            self.save_runtime_config()

    # ---------------- TRAY ----------------

    def init_tray(self):

        self.tray = QSystemTrayIcon(self)

        icon = QIcon("icon.ico") if os.path.exists("icon.ico") else QApplication.style().standardIcon(
            QStyle.SP_ComputerIcon
        )

        self.tray.setIcon(icon)
        self.tray.setToolTip("Smart Home Browser")

        self.menu = QMenu()

        self.action_show = QAction("Show")
        self.action_show.triggered.connect(self.show_window)

        self.action_hide = QAction("Hide")
        self.action_hide.triggered.connect(self.hide)

        self.action_settings = QAction("Settings")
        self.action_settings.triggered.connect(self.open_settings)

        self.action_exit = QAction("Exit")
        self.action_exit.triggered.connect(self.exit_app)

        self.menu.addAction(self.action_show)
        self.menu.addAction(self.action_hide)
        self.menu.addSeparator()
        self.menu.addAction(self.action_settings)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_tray_click)
        self.tray.show()

    def on_tray_click(self, reason):

        if reason == QSystemTrayIcon.Trigger:
            self.show_window()

        elif reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()

    # ---------------- EXIT ----------------

    def exit_app(self):
        self.save_runtime_config()
        QApplication.quit()

    def closeEvent(self, event):
        self.save_runtime_config()
        event.ignore()
        self.hide()

# ---------------- SINGLE INSTANCE ----------------

def already_running():

    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)

    if socket.waitForConnected(300):

        # уже запущено -> показать окно
        socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(300)

        socket.disconnectFromServer()

        return True

    return False


# ---------------- MAIN ----------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    # уже есть экземпляр?
    if already_running():
        sys.exit(0)

    w = SmartHomeBrowser()

    QTimer.singleShot(0, w.show_window)

    sys.exit(app.exec())

