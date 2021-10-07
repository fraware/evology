from parameters import *
from sampling import *
import sampling
import pandas
import balance_sheet as bs
from brownian_motion import *
from market_clearing import *
from ga import *
import data
import random
from market import *
from tqdm import tqdm

random.seed(random.random())

def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    # Initialise important variables and dataframe to store results
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    df = data.create_df()
    price_history = []

    # Create the population
    pop = sampling.create_pop(mode, POPULATION_SIZE)

    for generation in tqdm(range(MAX_GENERATIONS)):
        bs.determine_edf(pop, price_history)

        """ TODO: Price clearing will be ESL """
        current_price = leap_solver(pop, current_price)
        price_history.append(price)       
        mismatch = bs.calculate_total_edv(pop) 

        bs.calculate_edv(pop, current_price)
        bs.calculate_wealth(pop, current_price) 

        """ TODO: rework apply_edv when market clearing is working and gives affordable excess demands"""
        """ TODO: we probably don't need all those output variables """
        pop, num_buy, num_sell, num_buy_tf, num_buy_vi, num_buy_nt, num_sell_tf, num_sell_vi, num_sell_nt = bs.apply_edv(pop, asset_supply, current_price) # Apply EDV orders

        pop, dividend, random_dividend = bs.wealth_earnings_profit(pop, dividend, current_price) #Earning, wealth, profit comput.
        bs.update_margin(pop, current_price)
        bs.clear_debt(pop, current_price)
        bs.calculate_wealth(pop, current_price) 

        pop, replacements = hypermutate(pop, mode) # Replace insolvent agents
        compute_fitness(pop)
        pop = strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE)

        # Save and stop in case of insolvency
        if mode == "between" and replacements > 0:
            print("Simulation interrupted for insolvency.")
            break

        data.update_results(df, generation, current_price, mismatch, pop, dividend, 
            random_dividend, replacements)
    return df


