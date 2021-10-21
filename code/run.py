from main import *
import pandas as pd
import random

RANDOM_SEED = random.random()

# def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

""" Replication Maarten's results """
df = main("between", 1000, 0, 10, 0, 0)
print(df)
print(df['Pos+'])
print(df['Pos-'])
df.to_csv("data/test_data.csv")
