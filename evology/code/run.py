#!/usr/bin/env python3
from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()
# wealth_coordinates = [0.42, 0.33, 0.25]
wealth_coordinates = [0.1, 0.1, 0.8]
# NT VI TF
# wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
print(wealth_coordinates)

# def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE, wealth_coordinates, tqdm_display):

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display):

    if learning_mode == 0:
        df = main("static", TIME, 0, POPULATION_SIZE, 0, 0, wealth_coordinates, tqdm_display)
    if learning_mode == 1:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, MUTATION_RATE, wealth_coordinates, tqdm_display)
    return df

df = run(100, 0, 5000, wealth_coordinates, False)

df.to_csv("evology/data/run_data.csv")
# print(df)



