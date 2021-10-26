''' copy main '''
import timeit

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
    
    starttime = timeit.default_timer()
    
    # Initialise important variables and dataframe to store results
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    df = data.create_df()
    price_history, dividend_history = [], []
    extended_dividend_history = mk.dividend_series(1*252)

    # Create the population
    pop = sampling.create_pop(mode, POPULATION_SIZE)
    types = []
    for ind in pop:
        types.append(ind.type)
    print(types)

    print("Initialisation time is :", timeit.default_timer() - starttime)


    for generation in tqdm(range(MAX_GENERATIONS)):
        
        big_starttime = timeit.default_timer()


        starttime = timeit.default_timer()
        # small_starttime = timeit.default_timer()
        bs.calculate_wealth(pop, current_price) # Compute agents' wealth
        # print("calc w time :", timeit.default_timer() - small_starttime)

        # small_starttime = timeit.default_timer()
        bs.update_profit(pop)
        # print("profit time :", timeit.default_timer() - small_starttime)

        # small_starttime = timeit.default_timer()
        bs.shield_wealth(generation, pop, wealth_coordinates, current_price)
        # print("shield :", timeit.default_timer() - small_starttime)

        # small_starttime = timeit.default_timer()
        pop, replacements = ga.hypermutate(pop, mode, asset_supply) # Replace insolvent agents
        # print("hyperm time :", timeit.default_timer() - small_starttime)


        # small_starttime = timeit.default_timer()
        # pop = bs.share_spoils(pop, spoils, asset_supply)
        # print("share spoils time :", timeit.default_timer() - small_starttime)

        print("Wealth comput, shield, hyperm time is :", timeit.default_timer() - starttime)
        


        if generation > SHIELD_DURATION:
            starttime = timeit.default_timer()
            ga.compute_fitness(pop)
            pop = ga.strategy_evolution(mode, pop, PROBA_SELECTION, POPULATION_SIZE, 
                CROSSOVER_RATE, MUTATION_RATE)
            print("GA time :", timeit.default_timer() - starttime)


        starttime = timeit.default_timer()
        # small_starttime = timeit.default_timer()
        bs.determine_tsv_proc(mode, pop, price_history)
        # print("det tsv proc mc :", timeit.default_timer() - small_starttime)

        # small_starttime = timeit.default_timer()
        bs.update_fval(pop, extended_dividend_history)
        # print("update fval  :", timeit.default_timer() - small_starttime)

        # small_starttime = timeit.default_timer()
        bs.determine_edf(pop)
        # print("det edf  :", timeit.default_timer() - small_starttime)

        print("tsv fval edf time :", timeit.default_timer() - starttime)
        # print(':::::::::::')


        starttime = timeit.default_timer()
        ed_functions = bs.agg_ed(pop)
        current_price = float(esl_mc.solve(ed_functions, current_price)[0])
        print("mk clearing time :", timeit.default_timer() - starttime)

        starttime = timeit.default_timer()
        bs.calculate_tsv(pop, current_price, price_history)
        price_history.append(current_price)       
        pop, mismatch = bs.calculate_edv(pop, current_price)
        # mismatch = bs.calculate_total_edv(pop) 
        print("tsv,edv, mismatch :", timeit.default_timer() - starttime)



        starttime = timeit.default_timer()

        pop, volume = mk.execute_ed(pop, current_price, asset_supply)
        pop, dividend, random_dividend = bs.earnings(pop, dividend) 
        dividend_history.append(dividend)
        extended_dividend_history.append(dividend)
        bs.update_margin(pop, current_price)
        bs.clear_debt(pop, current_price)
        print("exec dmd, margin, debt... time :", timeit.default_timer() - starttime)


        # bs.calculate_wealth(pop, current_price)
        starttime = timeit.default_timer()
        data.update_results(df, generation, current_price, mismatch, pop, dividend, 
            random_dividend, replacements, volume, price_history)
        print("data update time :", timeit.default_timer() - starttime)


        # Save and stop in case of insolvency
        if mode == "between" and replacements > 0 and POPULATION_SIZE == 3:
            print("Simulation interrupted for insolvency.")
            return df
            raise ValueError('Agent went insolvent')

        print("round time :", timeit.default_timer() - big_starttime)
        print('-------')
    
    return df, pop



def efficient_test_run(POPULATION_SIZE, learning_mode, TIME):

    if learning_mode == 'no learning':
        df, pop = main("between", TIME, 0, POPULATION_SIZE, 0, 0)
    if learning_mode == 'switch':
        df, pop = main("between", TIME, PROBA_SELECTION, POPULATION_SIZE, 0, MUTATION_RATE)
    

efficient_test_run(50000, 'switch', 25)