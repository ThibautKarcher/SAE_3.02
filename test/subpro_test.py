import os
import subprocess

test = subprocess.run(["python", "hi.py"], capture_output=True, text=True)
print(test.stdout)