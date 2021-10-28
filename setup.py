import os
os.system("pip install numpy")
os.system("pip install matplotlib")
os.system("pip install deap")
os.system("pip install pandas")
os.system("pip install -i https://test.pypi.org/simple/ eslpy==0.0.145")
os.system("pip install tqdm")

os.system("pip freeze > requirements.txt")