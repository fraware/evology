from parameters import *
from sampling import *
import sampling
import pandas
from balance_sheet import *
from brownian_motion import *
from market_clearing import *
from ga import *
from data import *
import random

random.seed(9)


def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    
    # maxFitnessValues, meanFitnessValues, replacements, , price_history = [],[],[],[],[],[]   
    # , mismatch_history, asset_count_history, mean_theta, mean_wealth, size_pos_pos, size_neg_pos = [],[],[],[],[],[], []

    dividend_history, random_dividend_history, generation_history = [], [], []
    price_history, mismatch_history, meanFitnessValues = [], [], []
    replacements, mean_wealth = [], []
    num_tf_history, num_vi_history, num_nt_history = [], [], []
    mean_wealth_history, wealth_tf_history, wealth_vi_history, wealth_nt_history = [], [], [], []
    mean_tf_history, mean_vi_history, mean_nt_history = [], [], []


    price = INITIAL_PRICE
    # extended_price_history = generate_bm_series(MAX_TIME_HORIZON+1)
    # extended_price_history = [abs(x) for x in extended_price_history]
    extended_price_history = [INITIAL_PRICE] * 100
    price_history = extended_price_history.copy()
    dividend = INITIAL_DIVIDEND
    generation = 0

    if POPULATION_SIZE != 3: 
        pop = sampling.toolbox.gen_rd_pop(n=POPULATION_SIZE) # Initialise market, population
    elif POPULATION_SIZE == 3:
        pop = sampling.toolbox.gen_ref_pop() # Initialise market, population from Scholl et al. 2020

    pop = sampling.adjust_mode(pop, mode)

    print(pop)

    for ind in pop:
        print(ind.type)
    asset_supply = count_positive_assets(pop)

    calculate_wealth(pop, price)

    while generation < MAX_GENERATIONS:
        print("----------------------------------------------------------------------")
        print("Generation " + str(generation))

        calculate_ts_edf(pop, price_history) # Compute TSV and EDF

        # pop_report(pop)

        price = leap_solver(pop, price) # Clear the market
        price_history.append(price)
        print("Price is " + str(price))
        calculate_edv(pop, price) # Compute EDV
        mismatch_history.append(calculate_total_edv(pop))
        print("Mismatch is " + str(calculate_total_edv(pop)))

        pop_report(pop)

        update_margin(pop, price)
        pop, num_buy, num_sell, num_buy_tf, num_buy_vi, num_buy_nt, num_sell_tf, num_sell_vi, num_sell_nt = apply_edv(pop, asset_supply, price) # Apply EDV orders
        print("Buy orders: " + str(num_buy) + " (TF=" + str(num_buy_tf) + " ;VI=" + str(num_buy_vi) + " ;NT=" + str(num_buy_nt) +")") 
        print("Sell orders: " + str(num_sell) + " (TF=" + str(num_sell_tf) + " ;VI=" + str(num_sell_vi) + " ;NT=" + str(num_sell_nt) +")") 

        pop, dividend, random_dividend = wealth_earnings(pop, dividend, price) # Apply invest., IR, Div and compute profit
        print("Dividend is " + str(dividend))
        dividend_history.append(dividend)
        random_dividend_history.append(random_dividend)

        pop, round_replacements = hypermutate(pop) # Replace insolvent agents
        # TODO: do we need to set del ind.wealth too? Or is it fully replaced?
        print(str(round_replacements) + " replacements done")

        """ 8) Evolution block
            a. Fitness computation """

        compute_fitness(pop)

        """
            b. Adaptation
        """
        pop = strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE)
        compute_fitness(pop)
        # TODO: control that EDV, TS, Wealth, Profits, EMA are what they should be.

        # for ind in pop:
        #     print(ind.profit)
        #     print(ind.fitness.values)
        sumfit = 0
        for ind in pop:
            # print(ind.fitness.values)
            # print(ind.fitness.values[0])

            sumfit += ind.fitness.values[0]
        meanFitness = sumfit / len(pop)
        meanFitnessValues.append(meanFitness)
        replacements.append(round_replacements)

        mean_vi = 0
        mean_nt = 0
        mean_tf = 0
        num_tf = 0
        num_vi = 0
        num_nt = 0
        # wealth_tf = 0
        wealth_tf_sum = 0
        # wealth_vi = 0
        wealth_vi_sum = 0
        wealth_nt = 0
        wealth_nt_sum = 0

        for ind in pop:
            print(ind.type)

        for ind in pop:
            if ind.type == "tf":
                # print("tf found and computed")
                # print(ind.wealth)
                mean_tf += ind[0]
                num_tf += 1
                wealth_tf_sum += ind.wealth
            if ind.type == "vi":
                mean_vi += ind[0]
                num_vi += 1
                wealth_vi_sum += ind.wealth
            if ind.type == "nt":
                mean_nt += ind[0]
                num_nt += 1
                wealth_nt_sum += ind.wealth
        
        if num_tf != 0: 
            wealth_tf = wealth_tf_sum / num_tf
            mean_tf = mean_tf / num_tf
        if num_tf == 0: 
            wealth_tf = 0
            mean_tf = 0

        if num_vi != 0:
            wealth_vi = wealth_vi_sum / num_vi
            mean_vi = mean_vi / num_vi
        if num_vi == 0: 
            wealth_vi = 0
            mean_vi = 0

        if num_nt != 0:
            wealth_nt = wealth_nt_sum / num_nt
            mean_nt = mean_nt / num_nt
        if num_nt == 0:
            wealth_nt = 0
            mean_nt = 0

        sum_wealth = 0
        for ind in pop:
            sum_wealth += ind.wealth
        mean_wealth_history.append(sum_wealth/len(pop))

        num_tf_history.append(num_tf)
        num_vi_history.append(num_vi)
        num_nt_history.append(num_nt)

        wealth_tf_history.append(wealth_tf)
        wealth_vi_history.append(wealth_vi)
        wealth_nt_history.append(wealth_nt)

        mean_tf_history.append(mean_tf)
        mean_vi_history.append(mean_vi)
        mean_nt_history.append(mean_nt)


        generation_history.append(generation)
        if mode == "between" and round_replacements > 0:
            print("Simulation interrupted for insolvency.")
            break
        generation += 1
    
    df = generate_df(MAX_TIME_HORIZON, generation_history, price_history, mismatch_history, 
                              num_tf_history, num_vi_history, num_nt_history, mean_tf_history, mean_vi_history, mean_nt_history, 
                              mean_wealth_history,  wealth_tf_history, wealth_vi_history, wealth_nt_history,
                              meanFitnessValues,
                              dividend_history, random_dividend_history, 
                              replacements)

    # print("checking wealth and type")
    # print(pop)
    # for ind in pop:
    #     print("----")
    #     print(ind.type)
    #     print(ind.wealth)
    #     print(ind.cash)
    #     print(ind.asset)


    return df
# df = main(10, 0, 10, 0, 0)
# print(df)
# df.to_csv("new/data/run_data_no_learning.csv")