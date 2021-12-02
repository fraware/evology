#!/usr/bin/env python3
from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()
wealth_coordinates = [1/3, 1/3, 1/3]
wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
wealth_coordinates = [0.1585744310551549, 0.16814303540203004, 0.6732825335428151]

print(wealth_coordinates)

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth):

    if learning_mode == 0:
        df = main("static", TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 1:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 2:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    return df

df = run(100, 0, 20000, wealth_coordinates, tqdm_display=False, reset_wealth=False)
df.to_csv("evology/data/run_data.csv")





