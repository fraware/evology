#!/usr/bin/env python3
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
import timeit
from steps import *
random.seed(random.random())

def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE, wealth_coordinates, tqdm_display):
    # Initialise important variables and dataframe to store results
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    results = np.zeros((MAX_GENERATIONS - SHIELD_DURATION, data.variables))
    price_history, dividend_history = [], []
    extended_dividend_history = mk.dividend_series(1*252)
    create_pop = cr.generate_creation_func(wealth_coordinates)
    # Create the population
    pop = create_pop(mode, POPULATION_SIZE)


    for generation in tqdm(range(MAX_GENERATIONS), disable=tqdm_display):

        pop, timeA = update_wealth(pop, current_price, generation, wealth_coordinates)
        pop, replacements, spoils, timeB = ga.hypermutate(pop, mode, asset_supply, current_price, generation) # Replace insolvent agents     
        pop, timeC = ga_evolution(pop, mode, generation, wealth_coordinates)
        pop, timeD  = decision_updates(pop, mode, price_history, extended_dividend_history)
        pop, mismatch, current_price, price_history, timeE = marketClearing(pop, current_price, price_history)

        pop, volume, dividend, random_dividend, dividend_history, extended_dividend_history, timeF = marketActivity(pop, 
            current_price, asset_supply, dividend, dividend_history, extended_dividend_history)

        results = data.record_results(results, generation, current_price, mismatch, 
        dividend, random_dividend, volume, replacements, pop, price_history, spoils, 
        timeA, timeB, timeC, timeD, timeE, timeF)

        if replacements > 0 and POPULATION_SIZE == 3 and mode == 'static':
            print('Error: Insolvency in the 3-strategy ecology')
            break

    df = pd.DataFrame(results, columns = data.columns)
    
    return df
