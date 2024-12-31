import sys
import os
import socket
import threading
import subprocess
import psutil
import re
import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    '''
    Classe principale de l'application
    '''
    def __init__(self):
        '''
        Iinitialisation de la fenêtre principale, ainsi que de tout les widgets necessaires
        ainsi que leur position dans la fenêtre
        Attribution des actions aux boutons
        '''
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Serveur slave")
        self.resize(700, 500)
        self.setCentralWidget(widget)

        '''
        creation des widgets : labels, boutons, zones de texte, barre de progression, etc...
        '''

        self.host_label = QLabel("Serveur maitre :")
        self.host_value = QLineEdit("")
        self.port_label = QLabel("Port :")
        self.port_value = QLineEdit("")
        self.nbr_prog_label = QLabel("Nombre de programmes simultanés max :")
        self.nbr_prog_value = QLineEdit("")  
        self.lang_slave = QLabel("Selection du langage accepté par ce serveur :")
        self.lang_slave_value = QComboBox()
        self.lang_slave_value.addItem("--Selectionnez un langage--")
        self.lang_slave_value.addItem("Python")
        self.lang_slave_value.addItem("C")
        self.lang_slave_value.addItem("Java")
        self.lang_slave_value.addItem("C++")
        self.start = QPushButton("Démarrage du serveur et connexion au serveur maitre")
        self.serv_state = QLabel("")
        self.input_label = QLabel("Codes reçus :")
        self.input_value = QTextEdit("")
        self.input_value.setReadOnly(True)
        self.nbr_prog_actuel_label = QLabel("Nombre de programmes actuellement en cours :")
        self.nbr_prog_actuel_value = QLineEdit("0")
        self.nbr_prog_actuel_value.setReadOnly(True)
        self.cpu_label = QLabel("Charge CPU :")
        self.cpu_value = QProgressBar()
        self.cpu_value.setMinimum(0)
        self.cpu_value.setMaximum(50)
        self.close_button = QPushButton("Fermer")

        '''
        Positionnement des widgets dans la fenêtre via la grille de positionnement :
        '''

        grid = QGridLayout()
        widget.setLayout(grid)
        grid.addWidget(self.host_label, 0, 0)
        grid.addWidget(self.host_value, 0, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.port_label, 1, 0)
        grid.addWidget(self.port_value, 1, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lang_slave, 2, 0)
        grid.addWidget(self.nbr_prog_label, 0, 2)
        grid.addWidget(self.nbr_prog_value, 0, 3, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.nbr_prog_actuel_label, 1, 2)
        grid.addWidget(self.nbr_prog_actuel_value, 1, 3, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.cpu_label, 2, 2)
        grid.addWidget(self.cpu_value, 3, 2, 1, 2)
        grid.addWidget(self.lang_slave_value, 3, 0, 1, 2)
        grid.addWidget(self.start, 4, 0, 1, 2)
        grid.addWidget(self.serv_state, 5, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.input_label, 6, 0, 1, 2)
        grid.addWidget(self.input_value, 7, 0, 6, 4)
        grid.addWidget(self.close_button, 13, 3, 1, 1)

        '''
        Mise en place de valeurs par défaut et attribution des actions aux boutons :
        '''

        self.host_value.setText('127.0.0.1')
        self.port_value.setText('5555')
        self.nbr_prog_value.setText('5')

        self.start.clicked.connect(self.connection)
        self.close_button.clicked.connect(self.close)

    def connection(self):
        '''
        Méthode de connexion au serveur maitre
        Une fois que le langage compilable par le serveur est selectionné, le serveur se connecte au serveur maitre 
        Si la connexion est réussie, le serveur est prêt à recevoir des codes à compiler
        sinon un message d'erreur est affiché
        '''
        if self.lang_slave_value.currentText() == "--Selectionnez un langage--":
            self.serv_state.setText("Veuillez selectionner un langage pour ce serveur")
            self.serv_state.setStyleSheet("color: red")
        else:
            try:
                port = int(self.port_value.text())
                self.slave_socket = socket.socket()
                self.slave_socket.connect((self.host_value.text(), port))
                self.serv_state.setText("Connecté au serveur maitre")
                self.serv_state.setStyleSheet("color: green")
                self.start.setText("Arrêt du serveur")
                self.receive_thread = threading.Thread(target = MainWindow.reception, args=[self])
                self.receive_thread.start()
                self.connecté = True
            except ValueError :
                self.serv_state.setText("Le port doit obligatoirement être un nombre")
                self.serv_state.setStyleSheet("color: red")
                self.connecté = False
            except ConnectionRefusedError:
                self.serv_state.setText("Connexion au serveur maitre refusée")
                self.serv_state.setStyleSheet("color: red")
                self.connecté = False
            except Exception as e:
                print(f"Erreur de connexion : {e}")
                self.serv_state.setText("Connexion échouée")
                self.serv_state.setStyleSheet("color: red")
                self.connecté = False       

    def reception(self):
        '''
        Méthode de réception des codes à compiler
        Si le CPU est surchargé ou si le nombre max de programmes simultanés est atteint,
        un message d'erreur est envoyé au serveur maitre et le serveur ne compilera pas le code
        Sinon, le code est envoyé vers la méthode de compilation
        '''
        while True:
            try:
                self.charge = int(psutil.cpu_percent())
                print(f"Pourcentage CPU actuellement utilisé : {self.charge}")
                code = self.slave_socket.recv(1024).decode()
                if self.charge >= 50:
                    self.serv_state.setText("Impossible de compiler plus de programmes, CPU surchargé")
                    self.serv_state.setStyleSheet("color: red")
                    message_erreur = "CPU surchargé"
                    self.slave_socket.send(message_erreur.encode())
                elif int(self.nbr_prog_actuel_value.text()) >= int(self.nbr_prog_value.text()):
                    self.serv_state.setText("Impossible de compiler plus de programmes, nombre de programmes max atteint")
                    self.serv_state.setStyleSheet("color: red")
                    message_erreur = "Nombre de programmes max atteint"
                    self.slave_socket.send(message_erreur.encode())
                else:
                    pass
                    self.charge = self.charge * 2
                    self.charge = int(self.charge)
                    #self.cpu_value.setValue(self.charge)           #erreur à cause des threads
                    time.sleep(2)
                    if not code:
                        break
                    else :
                        self.input_value.append(code)
                        self.compilation_thread = threading.Thread(target = MainWindow.compilation, args=[self, code])
                        self.compilation_thread.start()
            except Exception as e:
                print(f"Erreur de réception : {e}")
                self.serv_state.setText("Erreur lors de la réception")
                self.serv_state.setStyleSheet("color: red")
    
    def compilation(self, code):
        '''
        Méthode de compilation des codes reçus
        Le code est compilé avec le compilateur correspondant en fonction du
        language selectionné à compiler
        Si la compilation est réussie, le résultat est envoyé au serveur maitre
        Sinon, un message d'erreur est envoyé
        '''
        try:
            if self.lang_slave_value.currentText() == "Python":
                with open('code.py', 'w') as code_fichier:
                    code_fichier.write(code)
                resultat = subprocess.run([sys.executable, 'code.py'], capture_output=True, text=True)
                if resultat.stderr == "":
                    result = resultat.stdout
                else:
                    result = resultat.stderr
            elif self.lang_slave_value.currentText() == "C":
                with open('code.c','w') as code_fichier:
                    code_fichier.write(code)                                    #https://stackoverflow.com/questions/76090257/run-c-file-with-input-from-file-in-python-subprocess-library
                subprocess.run('gcc -o code code.c', shell=True)
                resultat = subprocess.run(['./code'], capture_output=True, text=True)
                if resultat.stderr == "":
                    result = resultat.stdout
                else:
                    result = resultat.stderr
            elif self.lang_slave_value.currentText() == "C++":
                with open('code.cpp','w') as code_fichier:
                    code_fichier.write(code)
                subprocess.run('g++ -o code code.cpp', shell=True)
                resultat = subprocess.run(['./code'], capture_output=True, text=True)
                if resultat.stderr == "":
                    result = resultat.stdout
                else:
                    result = resultat.stderr
            elif self.lang_slave_value.currentText() == "Java":
                nom_fich = re.findall("public class (.*) {", code)
                if nom_fich != None:
                    nom_fich = nom_fich[0]
                else:
                    nom_fich = "code"
                with open(f'{nom_fich}.java','w') as code_fichier:
                    code_fichier.write(code)
                subprocess.run(f'javac {nom_fich}.java', shell=True)
                resultat = subprocess.run(['java', f'{nom_fich}'], capture_output=True, text=True)
                if resultat.stderr == "":
                    result = resultat.stdout
                else:
                    result = resultat.stderr
                if os.path.exists(f'{nom_fich}.java'):
                    os.remove(f'{nom_fich}.java')
                else:
                    pass
            else:
                self.serv_state.setText("Langage non reconnu")
            self.envoi_resultat(result)
        except Exception as e:
            print(f"Erreur de compilation : {e}")

    def envoi_resultat(self, code):
        '''
        Méthode d'envoi des résultats de la compilation
        Si la connexion avec le serveur maitre est encore en cours, 
        le résultat est envoyé au serveur maitre qui joue le role de passrelle vers le client.
        Si l'envoi est réussi, le résultat est affiché
        Sinon, un message d'erreur est affiché
        '''
        try:
            self.slave_socket.send(code.encode())
            print("Résultat envoyé : ")
            print(code)
        except Exception as e:
            print(f"Erreur d'envoi du résultat : {e}")

    def deconnexion(self):
        '''
        Méthode de déconnexion du serveur
        '''
        try:
            self.slave_socket.close()
            self.serv_state.setText("Déconnecté")
            self.serv_state.setStyleSheet("color: red")
        except Exception as e:
            print(f"Erreur de déconnexion : {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())