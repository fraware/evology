#!/usr/bin/env python3
from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def run(POPULATION_SIZE, learning_mode, TIME, tqdm_display):

    if learning_mode == 'no learning':
        df = main("between", TIME, 0, POPULATION_SIZE, 0, 0, tqdm_display)
    if learning_mode == 'switch':
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, MUTATION_RATE, tqdm_display)
    return df

df = run(4, 'no learning', 50, False)

df.to_csv("evology/data/run_data.csv")
print(df)


