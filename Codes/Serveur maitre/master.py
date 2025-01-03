import socket
import threading
import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        ''' 
        Méthode d'initialisation de la fenêtre principale 
        contient l'ensemble des widgets de la fenêtre ainsi que leur position
        cette méthode permet aussi d'associer les boutons à leur méthode associés
        '''
        self.nbr_client = 0
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Serveur maitre")
        self.resize(700, 500)
        self.setCentralWidget(widget)

        '''
        Initialisation des widgets : 
        '''

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

        '''
        Positionnement des widgets dans la fenêtre :
        '''
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

        '''
        Association des boutons à la méthode associée de chacun :
        '''
        self.connect.clicked.connect(self.demarrage)
        self.close_window.clicked.connect(self.close)

    def demarrage(self):
        '''
        Methode de démarrage du serveur, elle permet la mise en route de l'écoute
        du serveur sur le port ouvert (ici 5555)
        Si le démarrage est établie sans erreur, la méthode d'acceptation de la connexion est appelée
        Une gestion des erreurs est aussi établie pour éviter le crash du serveur
        '''
        try:   
            self.connect.setEnabled(False)
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
        except Exception as e:
            print(f"Erreur : {e}")
            self.serv_state.setText(f"Erreur : {e}")
            self.serv_state.setStyleSheet("color: red")
        

    def accept(self, serveur_socket):
        '''
        Méthode d'acceptation en continu des connexions des clients et
        serveurs esclaves sur le port ouvert
        Si la connexion est correctement acceptée, la méthode de 
        détermination de la nature de l'équipement est appelée afin 
        de déterminer si l'équipement est un client ou un serveur esclave
        '''
        while True:
            try:
                conn, address = serveur_socket.accept()
                print(f"Connexion établie avec {address}")
                self.multi_client_thread = threading.Thread(target=MainWindow.nature_equipement, args=[self, conn, address])
                self.multi_client_thread.start()
            except OSError:
                break
            except Exception as e:
                print(f"Erreur de connexion : {e}")
                break

    def nature_equipement(self, conn, address):
        '''
        Méthode de détermination de la nature de l'équipement connecté
        Si l'équipement est un serveur esclave, il est ajouté à la liste des serveurs esclaves
        et son langage est déterminé à l'aide du script liste_serveur.txt
        Si l'équipement est un client, il est ajouté à la liste des clients connectés
        '''
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
                language_serv = ""
                for lang, ip in recherche_language_serv:
                    if ip == addr:
                        language_serv = lang
                        break
                self.slave_list.addItem(f"Serveur {language_serv} : {addr} connecté")
                if language_serv == "C":
                    self.serv_C = conn
                else :
                    self.serv_C = None
                if language_serv == "Java":
                    self.serv_Java = conn
                else :
                    self.serv_Java = None
                if language_serv == "C++":
                    self.serv_Cpp = conn
                else :
                    self.serv_Cpp = None
                if language_serv == "Python":
                    self.serv_Python = conn
                else :
                    self.serv_Python = None
                self.host = "Serveur"
                self.host_pos_in_list = self.slave_list.findItems(f"Serveur {language_serv} : {addr} connecté", Qt.MatchFlag.MatchExactly)[0]
            else :
                self.nbr_client += 1
                self.host_list.addItem(f"Client{self.nbr_client} : {addr} connecté")
                self.host_value.setText(str(self.nbr_client))
                self.host_pos_in_list = self.host_list.findItems(f"Client{self.nbr_client} : {addr} connecté", Qt.MatchFlag.MatchExactly)[0]
                self.host = "Client"
        print(f"Nature de l'équipement ayant l'adresse {address} : {self.host}")
        MainWindow.reception(self, conn, address)

    def reception(self, conn, address):
        '''
        Méthode de réception des messages envoyés par les clients
        Si le message est "fin", la connexion avec le client est fermée et 
        celui-ci est retiré de la liste des clients connectés
        Sinon, le message est conservé et est envoyé à la méthode de détermination
        du langage du code afin de savoir à quel serveur esclave envoyer le code
        '''
        while True:
            if self.host == "Client":
                try :
                    message = conn.recv(1024).decode()
                    if not message:
                        break
                    else:
                        self.output.append(f"Message reçu de {address} :\n{message}")
                        print(f"Nouveau message reçu : {message}")
                        if message == "fin":
                            print(f"Fin de connexion avec le client {address}")
                            conn.send("ok, fin".encode())
                            #conn.close()
                            self.nbr_client -= 1
                            self.host_list.takeItem(self.host_list.row(self.host_pos_in_list))      #https://stackoverflow.com/questions/23835847/how-to-remove-item-from-qlistwidget
                            break
                        else:
                            MainWindow.definir_language(self, message, conn, address)
                except Exception as e:
                    print(f"Erreur : {e}")
                    self.output.append(f"Erreur lors de la reception : {e}")
                    break
            else:
                break

    def definir_language(self, message, conn, address):
        '''
        Méthode de détermination du langage du code envoyé par le client
        Si le message contient des mots-clés propres à un langage de programmation
        le langage est déterminé et le code est envoyé au serveur esclave correspondant
        Sinon, un message d'erreur est envoyé au client
        '''
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
        MainWindow.send_to_slave(self, message, language, conn, address)

    def send_to_slave(self, message, language, conn, address):
        '''
        Méthode d'envoi du code au serveur esclave correspondant au langage du code
        Si le serveur esclave est connecté, le code est envoyé et le résultat de la compilation
        est renvoyé au client
        Sinon, un message d'erreur est envoyé au client afin d'éviter un potentiel crash du client
        ou du serveur lui-même
        '''
        try:
            if language == "Python":
                if self.serv_Python:
                    try:
                        self.serv_Python.send(message.encode())
                        print(f"Message envoyé au serveur Python : {message}")
                        output = self.serv_Python.recv(1024).decode()
                        print(f"Réponse du serveur Python : {output}")
                        self.output.append(f"Résultat du code envoyé : {output}")
                        self.send_result_to_client(output, conn, address)
                    except Exception as e:
                        print(f"Erreur d'envoi au serveur esclave : {e}")
                        conn.send("Serveur Python non disponible".encode())
                else:
                    self.output.append("Aucun serveur Python connecté, compilation du code impossible")
                    print("Aucun serveur Python connecté")
                    conn.send("Aucun serveur Python connecté".encode())
            elif language == "C":
                if self.serv_C:
                    try:
                        self.serv_C.send(message.encode())
                        print(f"Message envoyé au serveur C : {message}")
                        output = self.serv_C.recv(1024).decode()
                        print(f"Réponse du serveur C : {output}")
                        self.output.append(f"Résultat du code envoyé : {output}")
                        self.send_result_to_client(output, conn, address)
                    except Exception as e:
                        print(f"Erreur d'envoi au serveur esclave : {e}")
                        conn.send("Serveur C non disponible : ".encode())
                else:
                    self.output.append("Aucun serveur C connecté, compilation du code impossible")
                    print("Aucun serveur C connecté")
                    conn.send("Aucun serveur C connecté".encode())
            elif language == "C++":
                if self.serv_Cpp:
                    try:
                        self.serv_Cpp.send(message.encode())
                        print(f"Message envoyé au serveur C++ : {message}")
                        output = self.serv_Cpp.recv(1024).decode()
                        print(f"Réponse du serveur C++ : {output}")
                        self.output.append(f"Résultat du code envoyé : {output}")
                        self.send_result_to_client(output, conn, address)
                    except Exception as e:
                        print(f"Erreur d'envoi au serveur esclave : {e}")
                        conn.send("Serveur C++ non disponible".encode())
                else:
                    self.output.append("Aucun serveur C++ connecté, compilation du code impossible")
                    print("Aucun serveur C++ connecté")
                    conn.send("Aucun serveur C++ connecté".encode())
            elif language == "Java":
                if self.serv_Java:
                    try:
                        self.serv_Java.send(message.encode())
                        print(f"Message envoyé au serveur Java : {message}")
                        output = self.serv_Java.recv(1024).decode()
                        print(f"Réponse du serveur Java : {output}")
                        self.output.append(f"Résultat du code envoyé : {output}")
                        self.send_result_to_client(output, conn, address)
                    except Exception as e:
                        print(f"Erreur d'envoi au serveur esclave : {e}")
                        conn.send("Serveur Java non disponible".encode())
                else:
                    self.output.append("Aucun serveur Java connecté, compilation du code impossible")
                    print("Aucun serveur Java connecté")
                    conn.send("Aucun serveur Java connecté".encode())
        except Exception as e:
            print(f"Erreur d'envoi au serveur esclave : {e}")
            self.output.append(f"Erreur d'envoi au serveur esclave : {e}")
            conn.send("Erreur d'envoi au serveur esclave".encode())

    def send_result_to_client(self, message, conn, address):
        '''
        Méthode d'envoi du résultat de la compilation du code au client après 
        avoir obtenu la réponse lors de la méthode précédente
        Si la connexion avec le client est perdue, un message d'erreur est renvoyé
        '''
        try:
            conn.send(message.encode())
            print(f"Message envoyé au client : {message}")
        except Exception as e:
            print(f"Erreur d'envoi au client : {e}")


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