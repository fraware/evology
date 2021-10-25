from main import *
import pandas as pd
import random

RANDOM_SEED = random.random()

# def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

""" Replication Maarten's results """
df, pop = main("between", 10000, 0, 100, 0, 0)
print(df)


for ind in pop:
    print(ind.type)
    print(ind.asset)

df.to_csv("data/test_data.csv")
