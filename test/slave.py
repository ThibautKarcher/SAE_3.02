


def envoi_resultat(self, code):
        with open('code.py') as code_fichier:       # explication fonction with : https://www.freecodecamp.org/news/with-open-in-python-with-statement-syntax-example/
            code_fichier.write(code)