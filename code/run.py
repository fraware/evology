from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()

# def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

# """ Replication Maarten's results """
# df, pop = main("between", 12500, 0, 3, 0, 0)
# print(df)

# df.to_csv("data/pop3_static.csv")

# """ Multi agent without learning """
# df, pop = main("between", 12500, 0, 100, 0, 0)
# print(df)

# df.to_csv("data/pop100_static.csv")

""" Multi agent learning """
df, pop = main("between", 12500, 1, 100, 0, MUTATION_RATE)
print(df)

df.to_csv("data/pop100_learning_csv")
