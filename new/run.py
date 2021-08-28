from main2 import *
import pandas as pd

# def main(MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):


df = main(100, 0, 100, 0, 0)
print(df)
df.to_csv("new/data/run_data_no_learning.csv")

df = main(100, 1, 100, 0.1, 0.01)
print(df)
df.to_csv("new/data/run_data_learning.csv")