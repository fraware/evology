import os
os.system("pip install numpy")
os.system("pip install matplotlib")
os.system("pip install deap")
os.system("pip install leap_ec")
os.system("pip install pandas")

os.system("pip install --index-url https://test.pypi.org/simple/ eslpy --force")

os.system("pip freeze > requirements.txt")


