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
        self.conn = QPushButton("Connexion")
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
        self.code_output.setReadOnly(True)
        self.close_button = QPushButton("Fermer")

        grid = QGridLayout()
        widget.setLayout(grid)
        grid.addWidget(self.host_label, 0, 0, 1, 1)
        grid.addWidget(self.host_value, 0, 1, 1, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.port_label, 1, 0, 1, 1)
        grid.addWidget(self.port_value, 1, 1, 1, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.conn, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.conn_state, 3, 0, 1, 1)
        grid.addWidget(self.choose_lang, 4, 0, 1, 1)
        grid.addWidget(self.code_label, 5, 0, 1, 1)
        grid.addWidget(self.code_input, 6, 0, 1, 1)
        grid.addWidget(self.code_send, 7, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.result_label, 0, 2, 1, 1)
        grid.addWidget(self.code_output, 1, 2, 1, 1)
        grid.addWidget(self.close_button, 10, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.conn.clicked.connect(self.connect)
        self.code_send.clicked.connect(self.envoi)

        self.host_value.setText("127.0.0.1")
        self.port_value.setText("5555")

    def connect(self):
        try :
            port = int(self.port_value.text())
            self.client_socket = socket.socket()
            self.client_socket.connect((self.host_value.text(), port))
            print(type(self.client_socket))
            self.conn_state.setText("Connexion réussie")
            self.conn_state.setStyleSheet("color: #01C38D")
            self.conn.setText("Déconnexion")
            self.conn.clicked.connect(self.disconnect)
            self.port_value.setReadOnly(True)
            self.host_value.setReadOnly(True)
            self.thread_envoi = threading.Thread(target = self.envoi)
            self.thread_envoi.start()

        except ValueError:
            self.conn_state.setText("Le port doit être un nombre")
            self.conn_state.setStyleSheet("color: red")
            return
        
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            self.conn_state.setText("Connexion échouée")
            self.conn_state.setStyleSheet("color: red")
    
    
    def envoi(self):
        message = self.code_input.toPlainText()
        print(message)
        try :
            self.client_socket.send(message.encode())
            print(f"Message envoyé : {message}")
            self.thread_envoi.join()
                    
        except Exception as e:
            print(f"Erreur d'envoi : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()