from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def run(POPULATION_SIZE, learning_mode, TIME):

    if learning_mode == 'no learning':
        df, pop = main("between", TIME, 0, POPULATION_SIZE, 0, 0)
    if learning_mode == 'switch':
        df, pop = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, MUTATION_RATE)
    return df

df = run(100, 'switch', 10_000)

df.to_csv("data/run_data.csv")
print(df)


