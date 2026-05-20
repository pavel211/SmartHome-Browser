from PySide6.QtNetwork import QLocalSocket
import sys

SERVER_NAME = "smart_home_browser"

sock = QLocalSocket()
sock.connectToServer(SERVER_NAME)

if sock.waitForConnected(1000):
    sock.write(b"show")
    sock.flush()
    sock.waitForBytesWritten(1000)
    sock.disconnectFromServer()

sys.exit(0)