
import balance_sheet as bs
import ga as ga
import timeit
from parameters import *
import esl_market_clearing as esl_mc
import market as mk
import creation as cr
from scipy import optimize
import data
import pandas as pd
import random
from tqdm import tqdm
import warnings
import matplotlib 
import matplotlib.pyplot as plt
random.seed(random.random())


def ga_evolution(pop, mode, generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE):
    starttime = timeit.default_timer()
    if generation > SHIELD_DURATION:
        ga.compute_fitness(pop)
        pop = ga.strategy_evolution(mode, pop, PROBA_SELECTION, MUTATION_RATE, wealth_coordinates)
    timeC = timeit.default_timer() - starttime
    return pop, timeC

def decision_updates(pop, mode, price_history, dividend_history):
    starttime = timeit.default_timer()
    bs.DetermineTsvProc(mode, pop, price_history)
    bs.UpdateFval(pop, dividend_history)
    bs.DetermineEDF(pop)
    timeD = timeit.default_timer() - starttime
    return pop, timeD


def marketClearing(pop, current_price, price_history, spoils):
    starttime = timeit.default_timer()

    eslmc = True
    Initial = current_price

    if eslmc == True:
        ed_functions, ToLiquidate = bs.agg_ed_esl(pop, spoils)
        current_price = esl_mc.CircuitClearing(ed_functions, current_price)    
    elif eslmc == False:
        ed_functions, ToLiquidate = bs.agg_ed(pop, spoils)
        current_price = optimize.brentq(ed_functions[0], 0.5 * current_price, 2 * current_price)

    if current_price == Initial:
        warnings.warn('Same price as before.')
    #     print(ed_functions[0](0, Initial))
    # x = np.linspace(0,Initial*10,1000)
    # y = ed_functions[0](0,x)
    # fig = plt.figure()
    # ax = fig.add_subplot(1, 1, 1)
    # plt.plot(x,y, 'r')
    # plt.show()
    #     plt.plot(price_history)
    #     plt.show()
    #     print('---')
    #     for ind in pop:
    #         print(ind.type)
    #         print(ind.tsv)
    #         print(ind.edf(ind, current_price))
    #     raise ValueError('Price before and after market clearing are identical.')
    
    bs.calculate_tsv(pop, current_price, price_history)
    price_history.append(current_price)       
    pop, mismatch = bs.calculate_edv(pop, current_price)
    timeE = timeit.default_timer() - starttime
    return pop, mismatch, current_price, price_history, ToLiquidate, timeE


def marketActivity(pop, current_price, asset_supply, dividend, dividend_history, spoils, ToLiquidate):
    starttime = timeit.default_timer()
    pop, volume, spoils = mk.execute_ed(pop, current_price, asset_supply, spoils, ToLiquidate)
    pop, dividend, random_dividend = bs.earnings(pop, dividend) 
    dividend_history.append(dividend)
    bs.update_margin(pop, current_price)
    bs.clear_debt(pop, current_price)
    timeF = timeit.default_timer() - starttime
    return pop, volume, dividend, random_dividend, dividend_history, spoils, timeF


def update_wealth(pop, current_price, generation, wealth_coordinates, POPULATION_SIZE, reset_wealth):
    starttime = timeit.default_timer()
    bs.calculate_wealth(pop, current_price) # Compute agents' wealth
    bs.update_profit(pop)
    bs.ComputeReturn(pop)
    timeA = timeit.default_timer() - starttime
    return pop, timeA



