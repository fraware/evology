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
from initialisation import *
from tqdm import tqdm
from results import *

random.seed(random.random())

def main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    # Initialise important variables
    generation, current_price, dividend, asset_supply = 0, INITIAL_PRICE, INITIAL_DIVIDEND, POPULATION_SIZE * INITIAL_ASSETS
    
    # Create the population
    pop = sampling.create_pop(mode, POPULATION_SIZE)

    for generation in tqdm(range(MAX_GENERATIONS)):

        bs.determine_edf(pop, price_history)

        """ TODO: Price clearing will be ESL """
        current_price = leap_solver(pop, current_price)
        price_history.append(price)        

        bs.calculate_edv(pop, current_price)
        bs.calculate_wealth(pop, current_price) 

        """ TODO: rework apply_edv when market clearing is working and gives affordable excess demands"""
        """ TODO: we probably don't need all those output variables """
        pop, num_buy, num_sell, num_buy_tf, num_buy_vi, num_buy_nt, num_sell_tf, num_sell_vi, num_sell_nt = bs.apply_edv(pop, asset_supply, current_price) # Apply EDV orders

        pop, dividend, random_dividend = bs.wealth_earnings_profit(pop, dividend, current_price) #Earning, wealth, profit comput.
        bs.update_margin(pop, current_price)
        bs.clear_debt(pop, current_price)

        pop, round_replacements = hypermutate(pop, mode) # Replace insolvent agents
        compute_fitness(pop)
        pop = strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE)
        
        print(dividend_history)

        (dividend_history, random_dividend_history, meanFitnessValues, replacements, 
        positive_positions, negative_positions, fval_nt_history, mismatch_history,
        mean_wealth_history, num_tf_history, num_vi_history, num_nt_history, 
        wealth_share_tf_history
        ) = store_results(
        pop, dividend, random_dividend, round_replacements, generation, 
        dividend_history, random_dividend_history, meanFitnessValues, replacements, 
        positive_positions, negative_positions, fval_nt_history, mismatch_history, 
        mean_wealth_history, num_tf_history, num_vi_history, num_nt_history, 
        wealth_share_tf_history, wealth_share_vi_history, wealth_share_nt_history,
        wealth_tf_history, wealth_vi_history, wealth_nt_history, mean_tf_history,
        mean_vi_history, mean_nt_history, generation_history)
        # # results storage
        # sumfit = 0
        # for ind in pop:
        #     sumfit += ind.fitness.values[0]
        # meanFitness = sumfit / len(pop)
        # dividend_history.append(dividend)
        # random_dividend_history.append(random_dividend) 
        # meanFitnessValues.append(meanFitness)
        # replacements.append(round_replacements)
        # positive_positions.append(bs.count_long_assets(pop))
        # negative_positions.append(int(bs.count_short_assets(pop)))
        # fval_nt_history.append(round(bs.nt_report(pop),0))
        # mismatch_history.append(round(bs.calculate_total_edv(pop), 3))

        # mean_vi = 0
        # mean_nt = 0
        # mean_tf = 0
        # num_tf = 0
        # num_vi = 0
        # num_nt = 0
        # wealth_tf_sum = 0
        # wealth_vi_sum = 0
        # wealth_nt = 0
        # wealth_nt_sum = 0

        # for ind in pop:
        #     if ind.type == "tf":
        #         mean_tf += ind[0]
        #         num_tf += 1
        #         wealth_tf_sum += ind.wealth
        #     if ind.type == "vi":
        #         mean_vi += ind[0]
        #         num_vi += 1
        #         wealth_vi_sum += ind.wealth
        #     if ind.type == "nt":
        #         mean_nt += ind[0]
        #         num_nt += 1
        #         wealth_nt_sum += ind.wealth
        
        # if num_tf != 0: 
        #     wealth_tf = wealth_tf_sum / num_tf
        #     mean_tf = mean_tf / num_tf
        # if num_tf == 0: 
        #     wealth_tf = 0
        #     mean_tf = 0

        # if num_vi != 0:
        #     wealth_vi = wealth_vi_sum / num_vi
        #     mean_vi = mean_vi / num_vi
        # if num_vi == 0: 
        #     wealth_vi = 0
        #     mean_vi = 0

        # if num_nt != 0:
        #     wealth_nt = wealth_nt_sum / num_nt
        #     mean_nt = mean_nt / num_nt
        # if num_nt == 0:
        #     wealth_nt = 0
        #     mean_nt = 0

        # sum_wealth = 0
        # for ind in pop:
        #     sum_wealth += ind.wealth
        # mean_wealth_history.append(sum_wealth/len(pop))
        # share_wealth_tf = 100 * wealth_tf / sum_wealth
        # share_wealth_vi = 100 * wealth_vi / sum_wealth
        # share_wealth_nt = 100 * wealth_nt / sum_wealth

        # num_tf_history.append(num_tf)
        # num_vi_history.append(num_vi)
        # num_nt_history.append(num_nt)

        # wealth_share_tf_history.append(share_wealth_tf)
        # wealth_share_vi_history.append(share_wealth_vi)
        # wealth_share_nt_history.append(share_wealth_nt)

        # wealth_tf_history.append(wealth_tf)
        # wealth_vi_history.append(wealth_vi)
        # wealth_nt_history.append(wealth_nt)

        # mean_tf_history.append(mean_tf)
        # mean_vi_history.append(mean_vi)
        # mean_nt_history.append(mean_nt)


        # generation_history.append(generation)

        # Save and stop in case of insolvency
        if mode == "between" and round_replacements > 0:
            print("Simulation interrupted for insolvency.")
            break
        generation += 1
    
    df = data.generate_df(MAX_TIME_HORIZON, generation_history, price_history, mismatch_history, 
                              num_tf_history, num_vi_history, num_nt_history, mean_tf_history, mean_vi_history, mean_nt_history, 
                              mean_wealth_history,  wealth_tf_history, wealth_vi_history, wealth_nt_history,
                              wealth_share_tf_history, wealth_share_vi_history, wealth_share_nt_history,
                              meanFitnessValues, fval_nt_history,
                              dividend_history, random_dividend_history, 
                              positive_positions, negative_positions, replacements)

    # print("checking wealth and type")
    # print(pop)
    # for ind in pop:
    #     print("----")
    #     print(ind.type)
    #     print(ind.wealth)
    #     print(ind.cash)
    #     print(ind.asset)


    return df


