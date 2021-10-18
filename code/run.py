from main import *
import pandas as pd
import random

RANDOM_SEED = random.random()

# def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

""" Replication Maarten's results """
df = main("between", 3 , 0, 3, 0, 0)
print(df)
print(df['VI_signal'])
df.to_csv("data/test_data.csv")
