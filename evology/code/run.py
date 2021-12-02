#!/usr/bin/env python3
from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()
wealth_coordinates = [1/3, 1/3, 1/3]
# wealth_coordinates = [0.43, 0.34, 0.23]
# wealth_coordinates = [0.39169568280217376, 0.27892544279331255, 0.32937887440451374]
# wealth_coordinates = [0.18276920410580527, 0.08369636854672699, 0.7335344273474677]

wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
wealth_coordinates = [0.31476316799528176, 0.48832755570430747, 0.19690927630041072]

print(wealth_coordinates)

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth):

    if learning_mode == 0:
        df = main("static", TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 1:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 2:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    return df

df = run(100, 2, 20000, wealth_coordinates, tqdm_display=False, reset_wealth=False)
df.to_csv("evology/data/run_data.csv")





