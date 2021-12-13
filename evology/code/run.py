#!/usr/bin/env python3
from main import *
from parameters import *

RANDOM_SEED = random.random()
wealth_coordinates = [1/3, 1/3, 1/3]
wealth_coordinates = [0.2795763465816647, 0.6094501805144131, 0.1109734729039221]
# wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()

print(wealth_coordinates)

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth):

    if learning_mode == 0:
        df,pop = main("static", 'scholl', TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 1:
        df,pop = main("between", 'scholl', TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 2:
        df,pop = main("between", 'scholl', TIME, PROBA_SELECTION, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 3:
        df,pop = main("static", 'extended', TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 4:
        df,pop = main("between", 'extended', TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)

    return df, pop

df,pop = run(100, 0, 20000, wealth_coordinates, tqdm_display=False, reset_wealth=False)
df.to_csv("evology/data/run_data.csv")

print(df)



# print('Arithmetic average TF NT VI')
# TF = np.nanmean(df['TF_DayReturns'])
# print(TF)
# TF = np.nanmean(df['NT_DayReturns'])
# print(TF)
# TF = np.nanmean(df['VI_DayReturns'])
# print(TF)



# TF_strat = []
# VI_strat = []
# NT_strat = []

# for ind in pop:
#     if ind.type == 'tf':
#         TF_strat.append(ind[0])
#     if ind.type == 'vi': 
#         VI_strat.append(ind.strategy)
#     if ind.type == 'nt':
#         NT_strat.append(ind.strategy)

# plt.hist(TF_strat)
# plt.show()
# plt.hist(VI_strat)
# plt.show()
# plt.hist(NT_strat)
# plt.show()

# for ind in pop:
#     print(ind.type)
#     print(ind[0])
#     print(ind.tsv)
#     print(ind.edv)
#     print('-')
    