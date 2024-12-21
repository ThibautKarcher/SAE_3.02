import sys
import socket
import threading
import re
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
        self.connect = QPushButton("Démarrer le serveur")
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
        grid.addWidget(self.connect, 3, 0, 1, 2)
        grid.addWidget(self.host_list_label, 4, 0)
        grid.addWidget(self.host_list, 5, 0, 1, 2)
        grid.addWidget(self.slave_list_label, 6, 0)
        grid.addWidget(self.slave_list, 7, 0, 1, 2)
        grid.addWidget(self.output_label, 0, 2, 1, 2)
        grid.addWidget(self.output, 1, 2, 7, 2)
        grid.addWidget(self.close_window, 8, 3, 1, 1)

        self.connect.clicked.connect(self.__demarrage)

    def __demarrage(self):
        self.connect.setText('Arrêt du serveur')
        self.serv_state.setText('Serveur ON')
        accept = threading.Thread(target = MainWindow.__accept, args=[self])
        accept.start()

    def __accept(self, port = 5555):
        serveur_socket = socket.socket()
        serveur_socket.bind(('0.0.0.0', port))
        serveur_socket.listen()
        print("Serveur démarré")
        conn, address = serveur_socket.accept()
        addr = re.search(r"\d.*[.].[0-9]*", str(address)).group()
        print(addr)
        print(f"Connexion établie avec {address}")
        with open('liste_serveur.txt', 'r') as serv:
            lecture = serv.read()
            match_addr = re.search(addr, lecture).group()
            print(match_addr)
            if addr == match_addr:
                recherche_language_serv = re.findall(r"^Serveur (.*)\s\:[ ]?(.*[.].[0-9]*)", lecture)
                language_serv = ""
                for lang, ip in recherche_language_serv:
                    if ip == addr:
                        language_serv = lang
                        break
                print(language_serv)
                self.slave_list.addItem(f" Serveur {language_serv} : {addr} connecté")
                nature_equipement = "Serveur"
            else :
                i=1
                self.host_list.addItem(f"Client{i} : {addr} connecté")
                i+=1
                nature_equipement = "Client"
        MainWindow.reception(self, conn, address, nature_equipement)

    def reception(self, conn, address, nature_equipement):
        while True:
            message = conn.recv(1024).decode()
            if not message:
                break
            else :
                self.output.append(f"Message reçu de {address} : {message}")
                print(f"Nouveau message reçu : {message}")
                if nature_equipement == "Client":
                    MainWindow.definir_language(self, message)
                elif nature_equipement == "Serveur":
                    MainWindow.envoi(self, message)
                else :
                    raise Exception("Nature de l'équipement inconnue")

    

    #def definir_language(self, message):

#A faire dans les serveurs slaves
"""
    def envoi_resultat(self, code):
        with open('code.py') as code_fichier:       # explication fonction with : https://www.freecodecamp.org/news/with-open-in-python-with-statement-syntax-example/
            code_fichier.write(code)
"""      



if __name__ == "__main__":
    app = QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    app.exec()