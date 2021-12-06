#!/usr/bin/env python3
from steps import *

def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth):
    # Initialise important variables and dataframe to store results
    ReturnsNT, ReturnsVI, ReturnsTF = np.zeros((MAX_GENERATIONS - data.Barr, POPULATION_SIZE)), np.zeros((MAX_GENERATIONS - data.Barr, POPULATION_SIZE)), np.zeros((MAX_GENERATIONS - data.Barr, POPULATION_SIZE))
    generation, CurrentPrice, dividend, spoils = 0, InitialPrice, INITIAL_DIVIDEND, 0
    results = np.zeros((MAX_GENERATIONS - data.Barr, data.variables))
    price_history, dividend_history = [], []

    pop, asset_supply = cr.CreatePop(POPULATION_SIZE, wealth_coordinates)
    bs.calculate_wealth(pop, CurrentPrice)
    bs.UpdatePrevWealth(pop)

    for generation in tqdm(range(MAX_GENERATIONS), disable=tqdm_display, miniters = 100, mininterval=0.5):

        # Population reset
        pop = cr.WealthReset(pop, wealth_coordinates, generation, reset_wealth)

        # Hypermutation
        pop, replacements, spoils, timeB = ga.hypermutate(pop, mode, asset_supply, CurrentPrice, generation, spoils, wealth_coordinates) # Replace insolvent agents     
        
        # Strategy evolution
        pop, timeC = ga_evolution(pop, mode, generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE)

        # Calculate wealth and previous wealth
        bs.calculate_wealth(pop, CurrentPrice)
        bs.UpdatePrevWealth(pop)

        # Market decisions (tsv, proc, edf)
        pop, timeD  = decision_updates(pop, mode, price_history, dividend_history)

        # Market clearing 
        pop, mismatch, CurrentPrice, price_history, ToLiquidate, timeE = marketClearing(pop, CurrentPrice, price_history, spoils)

        # Market execution
        pop, volume, dividend, random_dividend, dividend_history, spoils, timeF = marketActivity(pop, 
            CurrentPrice, asset_supply, dividend, dividend_history, spoils, ToLiquidate)
        
        # Earnings, compute profits
        pop, timeA = update_wealth(pop, CurrentPrice, generation, wealth_coordinates, POPULATION_SIZE, reset_wealth)

        # Record results
        results, ReturnsNT, ReturnsVI, ReturnsTF = data.record_results(results, generation, CurrentPrice, mismatch, 
        dividend, random_dividend, volume, replacements, pop, price_history, spoils, 
        asset_supply, timeA, timeB, timeC, timeD, timeE, timeF, ReturnsNT, ReturnsVI, ReturnsTF)

    df = pd.DataFrame(results, columns = data.columns)
    
    return df
