import os
import subprocess

subprocess.run(['g++', '-o', 'code', 'hi.c'])
resultat = subprocess.run(['./code'], capture_output=True, text=True)
print(resultat.stdout)