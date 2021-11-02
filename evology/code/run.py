#!/usr/bin/env python3
from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()
wealth_coordinates = [0.3, 0.4, 0.3]
# NT VI TF
wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
print(wealth_coordinates)

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, wealth_coordinates, MUTATION_RATE):

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display):

    if learning_mode == 'no learning':
        df = main("between", TIME, 0, POPULATION_SIZE, 0, 0, wealth_coordinates, tqdm_display)
    if learning_mode == 'switch':
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, MUTATION_RATE, wealth_coordinates, tqdm_display)
    return df

df = run(3, 'switch', 10, wealth_coordinates, False)

df.to_csv("evology/data/run_data.csv")
print(df)


