import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from app import app  # Tu app Flask

def run_flask():
    # '0.0.0.0' abre la puerta para que otros dispositivos (celular) entren
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Perfumería Magnate")
        self.resize(1200, 800)

        # El navegador de la PC sigue apuntando a local
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))
        
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    # Hilo para Flask
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Interfaz PyQt6
    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec())