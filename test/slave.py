import sys
import os
import socket
import threading
import subprocess
import psutil
import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Serveur slave")
        self.resize(700, 500)
        self.setCentralWidget(widget)

        self.host_label = QLabel("Serveur maitre :")
        self.host_value = QLineEdit("")
        self.port_label = QLabel("Port :")
        self.port_value = QLineEdit("")
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
        self.output_label = QLabel("Résultats des codes :")
        self.output_value = QTextEdit("")
        self.output_value.setReadOnly(True)
        self.close_button = QPushButton("Fermer")

        grid = QGridLayout()
        widget.setLayout(grid)
        grid.addWidget(self.host_label, 0, 0)
        grid.addWidget(self.host_value, 0, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.port_label, 1, 0)
        grid.addWidget(self.port_value, 1, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.lang_slave, 2, 0)
        grid.addWidget(self.lang_slave_value, 3, 0, 1, 2)
        grid.addWidget(self.start, 4, 0, 1, 2)
        grid.addWidget(self.serv_state, 5, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.input_label, 6, 0, 1, 2)
        grid.addWidget(self.input_value, 7, 0, 5, 2)
        grid.addWidget(self.output_label, 0, 2)
        grid.addWidget(self.output_value, 1, 2, 11, 2)
        grid.addWidget(self.close_button, 13, 3, 1, 1)

        self.host_value.setText('192.168.1.16')
        self.port_value.setText('5555')

        self.start.clicked.connect(self.connection)
        self.close_button.clicked.connect(self.close)

    def connection(self):
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
                self.start.clicked.connect(self.deconnexion)
                self.receive_thread = threading.Thread(target = MainWindow.reception, args=[self])
                self.receive_thread.start()
            except ValueError :
                self.serv_state.setText("Le port doit obligatoirement être un nombre")
                self.serv_state.setStyleSheet("color: red")
            except ConnectionRefusedError:
                self.serv_state.setText("Connexion au serveur maitre refusée")
                self.serv_state.setStyleSheet("color: red")
            except Exception as e:
                print(f"Erreur de connexion : {e}")
                self.serv_state.setText("Connexion échouée")
                self.serv_state.setStyleSheet("color: red")

    def reception(self):
        while True:
            try:
                code = self.slave_socket.recv(1024).decode()
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
        try:
            if self.lang_slave_value.currentText() == "Python":
                print("compilation python")
                with open('code.py', 'w') as code_fichier:
                    code_fichier.write(code)
                resultat = subprocess.run([sys.executable, 'code.py'], capture_output=True, text=True)
                print(resultat)
                if resultat.stderr == "":
                    print(resultat.stdout)
                    result = resultat.stdout
                    print("Résultat compilé")
                else:
                    print(resultat.stderr)
                    result = resultat.stderr
                    print("Erreur de compilation")
            elif self.lang_slave_value.currentText() == "C":
                print("compilation C")
                with open('code.c','w') as code_fichier:
                    code_fichier.write(code)                                    #https://stackoverflow.com/questions/76090257/run-c-file-with-input-from-file-in-python-subprocess-library
                subprocess.run('gcc -o code code.c', shell=True)
                resultat = subprocess.run(['./code'], capture_output=True, text=True)
                print(resultat)
                if resultat.stderr == "":
                    print(resultat.stdout)
                    result = resultat.stdout
                    print("Résultat compilé")
                else:
                    print(resultat.stderr)
                    result = resultat.stderr
                    print("Erreur de compilation")
            elif self.lang_slave_value.currentText() == "C++":
                print("compilation C++")
                with open('code.cpp','w') as code_fichier:
                    code_fichier.write(code)
                subprocess.run('g++ -o code code.cpp', shell=True)
                resultat = subprocess.run(['./code'], capture_output=True, text=True)
                print(resultat)
                if resultat.stderr == "":
                    print(resultat.stdout)
                    result = resultat.stdout
                    print("Résultat compilé")
                else:
                    print(resultat.stderr)
                    result = resultat.stderr
                    print("Erreur de compilation")
            elif self.lang_slave_value.currentText() == "Java":
                print("compilation Java")
                nom_fich = re.findall("public class (.*) {", code)
                print(nom_fich)
                if nom_fich != None:
                    nom_fich = nom_fich[0]
                    print(nom_fich)
                else:
                    nom_fich = "code"
                with open(f'{nom_fich}.java','w') as code_fichier:
                    code_fichier.write(code)
                subprocess.run(f'javac {nom_fich}.java', shell=True)
                resultat = subprocess.run(['java', f'{nom_fich}'], capture_output=True, text=True)
                print(resultat)
                if resultat.stderr == "":
                    print(resultat.stdout)
                    result = resultat.stdout
                    print("Résultat compilé")
                else:
                    print(resultat.stderr)
                    result = resultat.stderr
                    print("Erreur de compilation")
                if os.path.exists(f'{nom_fich}.java'):
                    os.remove(f'{nom_fich}.java')
                else:
                    pass
            else:
                self.serv_state.setText("Langage non reconnu")
            self.envoi_resultat(result)
        except Exception as e:
            print(f"Erreur de compilation : {e}")
            self.output_value.append(f"Erreur de compilation : {e}")

    def envoi_resultat(self, code):
        print("Envoi du résultat")
        print(code)
        try:
            self.slave_socket.send(code.encode())
            print("Résultat envoyé")
            print(code)
        except Exception as e:
            print(f"Erreur d'envoi du résultat : {e}")
            self.output_value.append(f"Erreur d'envoi du résultat : {e}")

    def deconnexion(self):
        self.slave_socket.close()
        self.serv_state.setText("Déconnecté")
        self.serv_state.setStyleSheet("color: red")
        self.start.setText("Démarrage du serveur et connexion au serveur maitre")
        self.start.clicked.connect(self.connection)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())