#!/usr/bin/env python3
from parameters import *
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

def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth):
    # Initialise important variables and dataframe to store results
    ReturnsNT, ReturnsVI, ReturnsTF = np.zeros((MAX_GENERATIONS - SHIELD_DURATION, POPULATION_SIZE)), np.zeros((MAX_GENERATIONS - SHIELD_DURATION, POPULATION_SIZE)), np.zeros((MAX_GENERATIONS - SHIELD_DURATION, POPULATION_SIZE))
    generation, current_price, dividend, spoils = 0, InitialPrice, INITIAL_DIVIDEND, 0
    results = np.zeros((MAX_GENERATIONS - SHIELD_DURATION, data.variables))
    price_history, dividend_history = [], []
    extended_dividend_history = mk.dividend_series(1*252)

    pop, asset_supply = cr.CreatePop(POPULATION_SIZE, wealth_coordinates, current_price)
    bs.calculate_wealth(pop, current_price)
    bs.UpdatePrevWealth(pop)


    for generation in tqdm(range(MAX_GENERATIONS), disable=tqdm_display):
        pop, replacements, spoils, timeB = ga.hypermutate(pop, mode, asset_supply, current_price, generation, spoils, wealth_coordinates) # Replace insolvent agents     
        pop, timeC = ga_evolution(pop, mode, generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE)

        pop = cr.WealthReset(pop, wealth_coordinates, generation, reset_wealth, current_price)
        bs.calculate_wealth(pop, current_price)
        bs.UpdatePrevWealth(pop)

        # pop, timeA = update_wealth(pop, current_price, generation, wealth_coordinates, POPULATION_SIZE, reset_wealth)
        # pop, replacements, spoils, timeB = ga.hypermutate(pop, mode, asset_supply, current_price, generation, spoils, wealth_coordinates) # Replace insolvent agents     
        # pop, timeC = ga_evolution(pop, mode, generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE)
        pop, timeD  = decision_updates(pop, mode, price_history, extended_dividend_history)
        pop, mismatch, current_price, price_history, ToLiquidate, timeE = marketClearing(pop, current_price, price_history, spoils)

        pop, volume, dividend, random_dividend, dividend_history, extended_dividend_history, spoils, timeF = marketActivity(pop, 
            current_price, asset_supply, dividend, dividend_history, extended_dividend_history, spoils, ToLiquidate)
        
        pop, timeA = update_wealth(pop, current_price, generation, wealth_coordinates, POPULATION_SIZE, reset_wealth)

        results, ReturnsNT, ReturnsVI, ReturnsTF = data.record_results(results, generation, current_price, mismatch, 
        dividend, random_dividend, volume, replacements, pop, price_history, spoils, 
        asset_supply, timeA, timeB, timeC, timeD, timeE, timeF, ReturnsNT, ReturnsVI, ReturnsTF)

    df = pd.DataFrame(results, columns = data.columns)
    
    return df
