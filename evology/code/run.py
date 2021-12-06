#!/usr/bin/env python3
from main import *
import pandas as pd
import random
from parameters import *

RANDOM_SEED = random.random()
wealth_coordinates = [1/3, 1/3, 1/3]
# wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()

print(wealth_coordinates)

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth):

    if learning_mode == 0:
        df = main("static", TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 1:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 2:
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    return df

df = run(100, 0, 252 * 6, wealth_coordinates, tqdm_display=False, reset_wealth=False)
df.to_csv("evology/data/run_data.csv")

print(df)

df['TF_DayReturns1'] = df['TF_DayReturns'] + 1
df['TF_DayReturns2'] = np.exp(df['TF_DayReturns'])
TF = (np.nanprod(df['TF_DayReturns1']) - 1) ** (1/len(df))
print(TF)
TF = (np.nanprod(df['TF_DayReturns2']) - 1) ** (1/len(df))
print(TF)
TF = np.nanmean(df['TF_DayReturns'])
print(TF)

print('---')
print(np.nanprod(df['TF_DayReturns1']))
print(np.nanprod(df['TF_DayReturns1']) - 1)
print( (1/len(df)))




