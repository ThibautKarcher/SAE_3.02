import socket
import threading
import sys
import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setWindowTitle("Test")
        self.resize(900, 600)
        self.setCentralWidget(widget)
        widget.setStyleSheet(Path('style.qss').read_text())

        self.host_label = QLabel("Serveur :")
        self.host_value = QLineEdit("")
        self.port_label = QLabel("Port :")
        self.port_value = QLineEdit("")
        self.conn = QPushButton("Connexion")
        self.conn.setCheckable(True)
        self.conn_state = QLabel("")
        self.choose_lang = QComboBox()
        self.choose_lang.addItem("--Selectionnez un langage--")
        self.choose_lang.addItem("Python")
        self.choose_lang.addItem("C")
        self.choose_lang.addItem("Java")
        self.choose_lang.addItem("C++")
        self.choose_lang.addItem("Texte")
        self.lang_status = QLabel("")
        self.code_label = QLabel("Inserez un code à executer :")
        self.code_input = QTextEdit("")
        self.import_file = QPushButton("Importer un fichier")
        self.code_send = QPushButton("Executer")
        self.filler = QLabel("")
        self.result_label = QLabel("Résultat en sortie :")
        self.code_output = QTextEdit("")
        self.code_output.setReadOnly(True)
        self.close_button = QPushButton("Fermer")

        grid = QGridLayout()
        widget.setLayout(grid)
        grid.addWidget(self.host_label, 0, 0)
        grid.addWidget(self.host_value, 0, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.port_label, 1, 0)
        grid.addWidget(self.port_value, 1, 1, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self.conn, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.conn_state, 3, 0, 1, 2)
        grid.addWidget(self.choose_lang, 4, 0)
        grid.addWidget(self.lang_status, 5, 0)
        grid.addWidget(self.code_label, 6, 0)
        grid.addWidget(self.code_input, 7, 0, 1, 2)
        grid.addWidget(self.import_file, 8, 0, 1, 2)
        grid.addWidget(self.code_send, 9, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(self.result_label, 0, 2, 1, 2)
        grid.addWidget(self.code_output, 1, 2, 8, 2)
        grid.addWidget(self.close_button, 9, 3, 1, 1)

        
        self.conn.clicked.connect(self.etat_bouton)
        self.code_send.clicked.connect(self.detect_language)
        self.import_file.clicked.connect(self.inserer_fichier)

        self.close_button.clicked.connect(self.fermeture)

        self.host_value.setText("127.0.0.1")
        self.port_value.setText("5555")

    def inserer_fichier(self):              # https://www.pythontutorial.net/pyqt/pyqt-qfiledialog/
        try:
            fichier = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier",
                "",
                "Fichier texte (*.txt);; Python (*.py);; C (*.c);; Java (*.java);; C++ (*.cpp *.cc)"
            )
            if fichier :
                fichier = fichier[0]
                with open(fichier, 'r') as file:
                    self.code_input.setText(file.read())
        except FileNotFoundError:
            self.conn_state.setText("Fichier non trouvé")
            self.conn_state.setStyleSheet("color: red")
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier : {e}")
            self.code_input.setText("Erreur lors de l'ouverture du fichier")

    def etat_bouton(self):
        if self.conn.isChecked():
            self.conn.setText("Déconnexion")
            self.connexion()
            if self.connecté:
                self.port_value.setReadOnly(False)
                self.host_value.setReadOnly(False)
                self.close_button.setEnabled(True)
            else:
                self.conn.setText("Connexion")
                self.conn.setChecked(False)
        else:
            self.conn.setText("Connexion")
            self.deconnexion()
            self.port_value.setReadOnly(True)
            self.host_value.setReadOnly(True)

    def fermeture(self):
        if self.conn.isChecked():
            self.conn_state.setText("Impossible de fermer la fenêtre en étant encore connecté au serveur")
            self.conn_state.setStyleSheet("color: red")
        else:
            self.close()        # Permet la fermeture de la fenêtre

    def connexion(self):
        try :
            port = int(self.port_value.text())
            self.client_socket = socket.socket()
            self.client_socket.connect((self.host_value.text(), port))
            self.conn_state.setText("Connexion réussie")
            self.conn_state.setStyleSheet("color: #01C38D")
            self.connecté = True         
        except ValueError:
            self.conn_state.setText("Le port doit être un nombre")
            self.conn_state.setStyleSheet("color: red")
            self.connecté = False
            return
        except ConnectionRefusedError:
            self.conn_state.setText("Connexion refusée")
            self.conn_state.setStyleSheet("color: red")
            self.connecté = False
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            self.conn_state.setText("Connexion échouée")
            self.conn_state.setStyleSheet("color: red")
            self.connecté = False

    def detect_language(self, message):
        message = self.code_input.toPlainText()
        if re.search("printf", message):
            language = "C"
            self.choose_lang.setCurrentText("C")
            self.lang_status.setText("")
            MainWindow.envoi(self, message)
        elif re.search("System.out.println", message):
            language = "Java"
            self.choose_lang.setCurrentText("Java")
            self.lang_status.setText("")
            MainWindow.envoi(self, message)
        elif re.search("cout", message):
            language = "C++"
            self.choose_lang.setCurrentText("C++")
            self.lang_status.setText("")
            MainWindow.envoi(self, message)
        elif re.search("print", message):
            language = "Python"
            self.choose_lang.setCurrentText("Python")
            self.lang_status.setText("")
            MainWindow.envoi(self, message)
        elif message == "":
            language = None
        else :
            language = "Texte"
            self.choose_lang.setCurrentText("Texte")
            self.lang_status.setText("Langage non reconnu, votre code sera traité comme du texte, changer le langage si nécessaire")
            self.lang_status.setStyleSheet("color: red")
        print(language)
    
    
    def envoi(self, message):
        try :
            print(self.client_socket)
            print(type(self.client_socket))
            self.client_socket.send(message.encode())
            print(f"Message envoyé : {message}")
            MainWindow.reponse(self)
        except Exception as e:
            print(f"Erreur d'envoi : {e}")

    def reponse(self):
        while True:
            try:
                resultat = self.client_socket.recv(1024).decode()
                if not resultat:
                    break
                else :
                    self.code_output.append(resultat)
                    print(f"Resultat du code : {resultat}")
                    break
            except Exception as e:
                print(f"Erreur lors de la réception du résultat : {e}")
                self.code_output.append(f"Erreur lors de la réception du résultat : {e}")
                break

    def deconnexion(self):
        try:
            message_fin_conn = "fin"
            self.client_socket.send(message_fin_conn.encode())
            if self.client_socket.recv(1024).decode() == "ok, fin":
                self.client_socket.close()
                self.conn_state.setText("Déconnecté")
                self.conn_state.setStyleSheet("color: red")
            else:
                self.conn_state.setText("Erreur lors de la déconnexion")
                self.conn_state.setStyleSheet("color: red")
        except OSError:
            self.conn_state.setText("Erreur lors de la déconnexion, problème de socket")
            self.conn_state.setStyleSheet("color: red")
        except Exception as e:
            print(f"Erreur lors de la déconnexion : {e}")
            self.conn_state.setText(f"Erreur lors de la déconnexion : {e}")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()