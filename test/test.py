import sys
import socket
import threading
from PyQt6.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Serveur maitre")
        self.resize(700, 500)
        self.setCentralWidget(widget)

        self.host_label = QLabel("Nombre de clients connectés :")
        self.host_value = QLineEdit("")
        self.host_value.setReadOnly(True)
        self.port_label = QLabel("Port ouvert pour connexion clients :")
        self.port_value = QLineEdit("")
        self.port_value.setReadOnly(True)
        self.serv_state = QLabel("")
        self.conn = QPushButton("Démarrer le serveur")
        self.host_list_label = QLabel("Liste des clients connectés :")
        self.host_list = QListWidget()
        self.slave_list_label = QLabel("Liste des serveurs esclaves disponibles :")
        self.slave_list = QListWidget()
        self.output_label = QLabel("Historique des communications :")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.close_window = QPushButton("Fermer")

        grid = QGridLayout()
        widget.setLayout(grid)
        grid.addWidget(self.port_label, 0, 0)
        grid.addWidget(self.port_value, 0, 1)
        grid.addWidget(self.host_label, 1, 0)
        grid.addWidget(self.host_value, 1, 1)
        grid.addWidget(self.serv_state, 2, 0, 1, 2)
        grid.addWidget(self.conn, 3, 0, 1, 2)
        grid.addWidget(self.host_list_label, 4, 0)
        grid.addWidget(self.host_list, 5, 0, 1, 2)
        grid.addWidget(self.slave_list_label, 6, 0)
        grid.addWidget(self.slave_list, 7, 0, 1, 2)
        grid.addWidget(self.output_label, 0, 2, 1, 2)
        grid.addWidget(self.output, 1, 2, 7, 2)
        grid.addWidget(self.close_window, 8, 3, 1, 1)

        self.conn.clicked.connect(self.demarrage)

    def demarrage(self, port = 5555) :
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        print("Serveur démarré et en écoute")
        threading.Thread(target=self, args=[self]).start()
        conn, addr = server_socket.accept()
        print(f"Connexion établie avec {addr}")
        MainWindow.reception(self, conn, server_socket)

    def reception(self, conn, socket) :
        while True:
            message = conn.recv(1024).decode()
            if not message:
                break
            print(f"Nouveau message reçu : {message}")
            if message == "deco-server":
                reply = "Fin de la connexion"
                conn.send(reply.encode())
                print("Fin de la connexion avec le client")
                conn.close()
                socket.close()
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    app.exec()