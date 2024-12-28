import sys
import socket
import threading
import re
from PyQt6.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        self.nbr_client = 0
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Serveur maitre")
        self.resize(700, 500)
        self.setCentralWidget(widget)

        self.host_label = QLabel("Nombre de clients connectés :")
        self.host_value = QLineEdit(str(self.nbr_client))
        self.host_value.setReadOnly(True)
        self.port_label = QLabel("Port ouvert pour connexion clients :")
        self.port_value = QLineEdit("5555")
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

        self.connect.clicked.connect(self.demarrage)
        self.close_window.clicked.connect(self.close)

    def demarrage(self):
        try:   
            self.connect.setText('Arrêt du serveur')
            self.serv_state.setText('Serveur ON')
            self.connect.clicked.connect(self.deconnexion)
            port = int(self.port_value.text())
            self.serveur_socket = socket.socket()
            self.serveur_socket.bind(('0.0.0.0', port))
            self.serveur_socket.listen()
            print("Serveur démarré")
            self.accept_thread = threading.Thread(target = MainWindow.accept, args=[self, self.serveur_socket])
            self.accept_thread.start()
        except OSError:
            print("Erreur de démarrage du serveur")
            self.serv_state.setText("Erreur de démarrage du serveur")
            self.serv_state.setStyleSheet("color: red")
        

    def accept(self, serveur_socket):
        while True:
            try:
                conn, address = serveur_socket.accept()
                print(f"Connexion établie avec {address}")
                self.multi_client_thread = threading.Thread(target=MainWindow.nature_equipement, args=[self, conn, address])
                self.multi_client_thread.start()
            except OSError:
                break

    def nature_equipement(self, conn, address):
        addr = re.search(r"\d.*[.].[0-9]*", str(address)).group()
        with open('liste_serveur.txt', 'r') as serv:
            lecture = serv.read()
            match_addr = re.search(addr, lecture)
            if match_addr != None:
                match_addr = match_addr.group()
            else:
                pass
            if addr == match_addr:
                recherche_language_serv = re.findall(r"Serveur (.*)\s\:[ ]?(.*[.].[0-9]*)", lecture)
                print(recherche_language_serv)
                language_serv = ""
                for lang, ip in recherche_language_serv:
                    if ip == addr:
                        language_serv = lang
                        break
                print(language_serv)
                self.slave_list.addItem(f"Serveur {language_serv} : {addr} connecté")
                if language_serv == "C":
                    self.serv_C = conn, address
                    print(self.serv_C)
                else :
                    self.serv_C = None
                if language_serv == "Java":
                    self.serv_Java = addr
                else :
                    self.serv_Java = None
                if language_serv == "C++":
                    self.serv_Cpp = addr
                else :
                    self.serv_Cpp = None
                if language_serv == "Python":
                    print("Python here")
                    self.serv_Python = conn
                    print(self.serv_Python)
                else :
                    self.serv_Python = None
                #self.host = "Serveur"
            else :
                self.nbr_client += 1
                self.host_list.addItem(f"Client{self.nbr_client} : {addr} connecté")
                self.host_value.setText(str(self.nbr_client))
                self.serv_C = None
                self.serv_Java = None
                self.serv_Cpp = None
                self.serv_Python = None
                #self.host = "Client"
        MainWindow.reception(self, conn, address)

    def reception(self, conn, address):
        while True:
            message = conn.recv(1024).decode()
            if not message:
                break
            else:
                self.output.append(f"Message reçu de {address} :\n{message}")
                print(f"Nouveau message reçu : {message}")
                try:
                    MainWindow.definir_language(self, message)
                except Exception as e:
                    print(f"Erreur : {e}")
                    self.output.append(f"Erreur : {e}")

        #conn.close()    # A voir si vraiment utile ou a deplacer

    def definir_language(self, message):
        try:
            if re.search("printf", message):
                language = "C"
            elif re.search("System.out.println", message):
                language = "Java"
            elif re.search("cout", message):
                language = "C++"
            elif re.search("print", message):
                language = "Python"
        except Exception as e:
            print(f"Language non reconnu: {e}")
            self.output.append(f"Erreur : Langage non reconnu")
        MainWindow.send_to_slave(self, message, language)

    def send_to_slave(self, message, language):
        print("send to slave")
        print(language)
        print(message)
        print("end send to slave")
        try:
            if language == "Python":
                print("Python here too")
                print(self.serv_Python)
                print(type(self.serv_Python))
                print("no more")
                if self.serv_Python != None:
                    self.serv_Python.send(message.encode())
                    print(f"Message envoyé au serveur Python : {message}")
                    output = self.slave_socket.recv(1024).decode()
                    print(f"Réponse du serveur Python : {output}")
                    self.output.append(f"Résultat du code envoyé : {output}")
                else:
                    self.output.append("Aucun serveur Python connecté, compilation du code impossible")
                    print("Aucun serveur Python connecté")
                  
        except Exception as e:
            print(f"Erreur d'envoi au serveur esclave : {e}")

    def deconnexion(self):
        self.connect.setText('Démarrer le serveur')
        self.serv_state.setText('Serveur OFF')
        self.accept_thread.join()
        self.multi_client_thread.join()
        self.serveur_socket.close()
        


if __name__ == "__main__":
    app = QApplication([])
    Window = MainWindow()
    Window.show()
    app.exec()


# A implementer et modif
    """
    def send_to_slave(self, message, language):
        print("send to slave")
        print(language)
        print(message)
        print("end send to slave")
        try :
            if language == "C":
                self.slave_socket = socket.socket()
                self.slave_socket.connect((self.serv_C, 3333))
            elif language == "Java":
                self.slave_socket = socket.socket()
                self.slave_socket.connect((self.serv_Java, 4444))
            elif language == "C++":
                self.slave_socket = socket.socket()
                self.slave_socket.connect((self.serv_Cpp, 2222))
            elif language == "Python":
                self.slave_socket = socket.socket()
                self.slave_socket.connect((self.serv_Python, 1111))
        except Exception as e:
            print(f"Erreur de connexion : {e}")
    
    """