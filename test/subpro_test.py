import os
import sys
import subprocess

resultat = subprocess.run([sys.executable, 'code.py'], capture_output=True, text=True)
print(resultat)
print(resultat.stdout)
