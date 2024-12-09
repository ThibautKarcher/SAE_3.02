import socket
import threading
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Test")
        self.resize(700, 500)
        self.setCentralWidget(widget)
        widget.setStyleSheet(Path('style.css').read_text())

        self.host_label = QLabel("Serveur :")
        self.host_value = QLineEdit("")
        self.port_label = QLabel("Port :")
        self.port_value = QLineEdit("")
        self.conn_state = QLabel("")
        self.choose_lang = QComboBox()
        self.choose_lang.addItem("Python")
        self.choose_lang.addItem("C")
        self.choose_lang.addItem("Java")
        self.choose_lang.addItem("C++")
        self.code_label = QLabel("Inserez un code à executer :")
        self.code_input = QTextEdit("")
        self.code_send = QPushButton("Executer")
        self.filler = QLabel("")
        self.result_label = QLabel("Résultat en sortie :")
        self.code_output = QTextEdit("")
        self.close_button = QPushButton("Fermer")

        grid = QGridLayout()
        widget.setLayout(grid)
        grid.addWidget(self.host_label, 0, 0)
        grid.addWidget(self.host_value, 0, 1)
        grid.addWidget(self.port_label, 1, 0)
        grid.addWidget(self.port_value, 1, 1)
        grid.addWidget(self.choose_lang, 2, 0, 1, 2)
        grid.addWidget(self.conn_state, 3, 0, 1, 2)
        grid.addWidget(self.code_label, 4, 0, 1, 2)
        grid.addWidget(self.code_input, 5, 0, 1, 2)
        grid.addWidget(self.code_send, 6, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.filler, 7, 0, 1, 2)
        grid.addWidget(self.result_label, 8, 0, 1, 2)
        grid.addWidget(self.code_output, 9, 0, 1, 2)
        grid.addWidget(self.close_button, 10, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)


    def connect(self):
        port = int(self.port_value.text())
        serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveur_socket.bind(('0.0.0.0', port))
        serveur_socket.listen()
        print("Server started")
        conn, address = serveur_socket.accept()
        print(f"Connexion établie avec {address}")

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()