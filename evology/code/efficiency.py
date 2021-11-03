#!/usr/bin/env python3

import timeit
from parameters import *
from sampling import *
import sampling
import pandas as pd
import balance_sheet as bs
import ga as ga
import data
import random
import market as mk
from tqdm import tqdm
import esl_market_clearing as esl_mc
import creation as cr
import matplotlib
import matplotlib.pyplot as plt

random.seed(random.random())
wealth_coordinates = [1/3, 1/3, 1/3]
        # small_starttime = timeit.default_timer()
        # print("share spoils time :", timeit.default_timer() - small_starttime)

        
partA = []
partB = []
partC = []
partD = []
partE = []
partF = []
runt = []


def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE, wealth_coordinates, tqdm_display):
    # Initialise important variables and dataframe to store results
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    df = data.create_df()
    price_history, dividend_history = [], []
    extended_dividend_history = mk.dividend_series(1*252)
    create_pop = cr.generate_creation_func(wealth_coordinates)

    # Create the population
    pop = create_pop(mode, POPULATION_SIZE)
    types = []
    for ind in pop:
        types.append(ind.type)
    print(types)

    for generation in tqdm(range(MAX_GENERATIONS), disable=tqdm_display):

        big_starttime = timeit.default_timer()
        small_starttime = timeit.default_timer()
        bs.calculate_wealth(pop, current_price) # Compute agents' wealth
        bs.update_profit(pop)
        bs.shield_wealth(generation, pop, wealth_coordinates, current_price)
        # bs.pop_report(pop)
        time = timeit.default_timer() - small_starttime
        # print(" Part A (wealth) :", time)
        partA.append(time)


        big_starttime = timeit.default_timer()
        pop, replacements = ga.hypermutate(pop, mode, asset_supply, current_price, generation) # Replace insolvent agents
        # replacements = 0       
        if generation > SHIELD_DURATION:
            ga.compute_fitness(pop)
            pop = ga.strategy_evolution(mode, pop, PROBA_SELECTION, MUTATION_RATE, wealth_coordinates)
        time = timeit.default_timer() - small_starttime
        # print(" Part B (evo) :", time)
        partB.append(time)

        small_starttime = timeit.default_timer()
        bs.determine_tsv_proc(mode, pop, price_history)
        bs.update_fval(pop, extended_dividend_history)
        bs.determine_edf(pop)
        time = timeit.default_timer() - small_starttime
        # print(" Part C (tsv edf) :", time)
        partC.append(time)


        small_starttime = timeit.default_timer()
        ed_functions = bs.agg_ed(pop)
        if current_price < 0:
            raise ValueError('Negative current price before esl solve. ' + str(bs.report_types(pop)))
        current_price = float(esl_mc.solve(ed_functions, current_price)[0])
        bs.calculate_tsv(pop, current_price, price_history)
        price_history.append(current_price)  
        time = timeit.default_timer() - small_starttime
        # print(" Part D (MC) :", time)
        partD.append(time)
     

        small_starttime = timeit.default_timer()
        pop, mismatch = bs.calculate_edv(pop, current_price)
        pop, volume = mk.execute_ed(pop, current_price, asset_supply)
        pop, dividend, random_dividend = bs.earnings(pop, dividend) 
        dividend_history.append(dividend)
        extended_dividend_history.append(dividend)
        bs.update_margin(pop, current_price)
        bs.clear_debt(pop, current_price)
        time = timeit.default_timer() - small_starttime
        # print(" Part E (post MC) :", time)
        partE.append(time)


        small_starttime = timeit.default_timer()
        data.update_results(df, generation, current_price, mismatch, pop, dividend, 
            random_dividend, replacements, volume, price_history)
        time = timeit.default_timer() - small_starttime
        # print(" Part F (update results) :", time)
        partF.append(time)


        # Save and stop in case of insolvency
        if mode == "between" and replacements > 0 and POPULATION_SIZE == 3:
            print("Simulation interrupted for insolvency.")
            return df, pop
            raise ValueError('Agent went insolvent')


        time = timeit.default_timer() - big_starttime
        # print("round " + str(generation) + " time :", time)
        runt.append(time)
        # print('--------------------')
    
    return df


def efficient_test_run(POPULATION_SIZE, learning_mode, TIME):

    if learning_mode == 'no learning':  
        df = main("between", TIME, 0, POPULATION_SIZE, 0, 0, wealth_coordinates, False)
    if learning_mode == 'switch':
        df = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, MUTATION_RATE, wealth_coordinates, False)
    return df
    

df_efficiency = efficient_test_run(10, 'switch', 50000)

df_efficiency.to_csv("evology/data/df_efficiency.csv")

df = pd.DataFrame()
df['A'] = partA
df['B'] = partB
df['C'] = partC
df['D'] = partD
df['E'] = partE
df['F'] = partF
df['Total'] = runt
df.to_csv("evology/data/efficiency_data.csv")


plt.plot(partA, label = 'A')
plt.plot(partB, label = 'B')
plt.plot(partC, label = 'C')
plt.plot(partD, label = 'D')
plt.plot(partE, label = 'E')
plt.plot(partF, label = 'F')
plt.legend()
plt.ylim((0, 0.02))
plt.savefig("evology/figures/speed_parts.png", dpi = 300)
plt.show()


plt.plot(runt, label = 'RunTime')
plt.legend()
plt.ylim((0, 0.02))
plt.savefig("evology/figures/speed_total.png", dpi = 300)
plt.show()