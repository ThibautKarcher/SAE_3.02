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
