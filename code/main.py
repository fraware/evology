from parameters import *
from sampling import *
import sampling
import pandas
import balance_sheet as bs
import ga as ga
import data
import random
import market as mk
from tqdm import tqdm
import esl_market_clearing as esl_mc

random.seed(random.random())

wealth_coordinates = [0.4, 0.3, 0.3]


def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    # Initialise important variables and dataframe to store results
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    df = data.create_df()
    price_history, dividend_history, process_history = [], [], []
    securities_contract = np.zeros((POPULATION_SIZE, POPULATION_SIZE)) # 1st Attempt into reconstructing ecology trading networkg
    extended_dividend_history = mk.dividend_series(1*252)

    # Create the population
    pop = sampling.create_pop(mode, POPULATION_SIZE)
    types = []
    for ind in pop:
        types.append(ind.type)
    print(types)

    for generation in tqdm(range(MAX_GENERATIONS)):
        bs.calculate_wealth(pop, current_price) # Compute agents' wealth
        bs.shield_wealth(generation, pop, wealth_coordinates, current_price)

        pop, replacements, spoils = ga.hypermutate(pop, mode) # Replace insolvent agents
        pop = bs.share_spoils(pop, spoils)
        ga.compute_fitness(pop)
        pop = ga.strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE)

        bs.determine_tsv_proc(pop, price_history, process_history)
        bs.update_fval(pop, extended_dividend_history)
        bs.determine_edf(pop)


        ed_functions = bs.agg_ed(pop)

        current_price = float(esl_mc.solve(ed_functions, current_price)[0])

        bs.calculate_tsv(pop, current_price, price_history)
        price_history.append(current_price)       


        bs.calculate_edv(pop, current_price)
        mismatch = bs.calculate_total_edv(pop) 

        # pop, volume, securities_contract = bs.execute_demand(pop, current_price, asset_supply, securities_contract)
        # pop, volume, securities_contract = mk.execute_demand(pop, current_price, asset_supply, securities_contract)
        pop, volume = mk.execute_ed(pop, current_price, asset_supply)
        volume = 0


        pop, dividend, random_dividend = bs.earnings(pop, dividend, current_price) 
        dividend_history.append(dividend)
        extended_dividend_history.append(dividend)
        bs.update_margin(pop, current_price)
        bs.clear_debt(pop, current_price)
        

        data.update_results(df, generation, current_price, mismatch, pop, dividend, 
            random_dividend, replacements, volume, price_history)

        # Save and stop in case of insolvency
        if mode == "between" and replacements > 0:
            print("Simulation interrupted for insolvency.")
            return df
            raise ValueError('Agent went insolvent')
    
    print(securities_contract)

        # long = 0
        # short = 0
        # for ind in pop:
        #     long += ind.asset_long 
        #     short += ind.asset_short
        # print('long, short')
        # print(long)
        # print(short)
        # print("----------------------")
        # for ind in pop:
        #     print(ind.type)
        #     print(ind.asset_long)
    return df
