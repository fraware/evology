from parameters import *
from sampling import *
import sampling
import pandas
import balance_sheet as bs
import ga as ga
import data
import random
from market import *
from tqdm import tqdm
import esl_market_clearing as esl_mc

random.seed(random.random())

def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    # Initialise important variables and dataframe to store results
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    df = data.create_df()
    price_history, div_g_estimation, dividend_history = [], [], []

    # Create the population
    pop = sampling.create_pop(mode, POPULATION_SIZE)

    for generation in tqdm(range(MAX_GENERATIONS)):
        # print("-----------------------------------------")

        bs.calculate_wealth(pop, current_price) # Compute agents' wealth

        """ remove evolution for now """
        pop, replacements, spoils = ga.hypermutate(pop, mode) # Replace insolvent agents
        pop = bs.share_spoils(pop, spoils)
        ga.compute_fitness(pop)
        pop = ga.strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE)

        bs.determine_tsv_proc(pop, price_history)
        bs.update_fval(pop, dividend_history, div_g_estimation)
        bs.determine_edf(pop)


        ed_functions = bs.agg_ed(pop)
        new_price = esl_mc.solve(ed_functions, current_price)

        current_price = float(new_price[0])
        price_history.append(current_price)       

        bs.calculate_edv(pop, current_price)


        mismatch = bs.calculate_total_edv(pop) 

        """ TODO: rework apply_edv when market clearing is working and gives affordable excess demands"""
        """ TODO: we probably don't need all those output variables """
        # pop, num_buy, num_sell, num_buy_tf, num_buy_vi, num_buy_nt, num_sell_tf, num_sell_vi, num_sell_nt = bs.apply_edv(pop, asset_supply, current_price) # Apply EDV orders
        

        # print("Running demands")
        # sum = 0
        # for ind in pop:
        #   print(ind.type)
        #   sum += ind.edv
        #   print(ind.edv)
        # print("Sum of edv is " + str(sum))
        pop, volume = bs.execute_demand(pop, current_price, asset_supply)



        pop, dividend, random_dividend = bs.earnings(pop, dividend, current_price) 
        dividend_history.append(dividend)
        bs.update_margin(pop, current_price)
        bs.clear_debt(pop, current_price)
        

        data.update_results(df, generation, current_price, mismatch, pop, dividend, 
            random_dividend, replacements, volume)

        # Save and stop in case of insolvency
        if mode == "between" and replacements > 0:
            print("Simulation interrupted for insolvency.")
            return df
            raise ValueError('Agent went insolvent')



        # print("----------------------")
    return df
