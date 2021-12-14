
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


def ga_evolution(pop, mode, space, generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE):
    starttime = timeit.default_timer()
    if generation > SHIELD_DURATION:
        ga.compute_fitness(pop)
        pop, CountSelected, CountMutated, CountCrossed, StratFlow = ga.strategy_evolution(mode, space, pop, PROBA_SELECTION, MUTATION_RATE, wealth_coordinates, generation)
    else:
        CountSelected, CountMutated, CountCrossed = 0,0,0
        StratFlow = 6 * [0]
    timeC = timeit.default_timer() - starttime
    return pop, timeC, CountSelected, CountMutated, CountCrossed, StratFlow

def decision_updates(pop, mode, price_history, dividend_history):
    starttime = timeit.default_timer()
    bs.DetermineTsvProc(mode, pop, price_history)
    bs.UpdateFval(pop, dividend_history)
    bs.DetermineEDF(pop)
    timeD = timeit.default_timer() - starttime
    return pop, timeD


def marketClearing(pop, current_price, price_history, spoils):
    starttime = timeit.default_timer()
    eslmc = False
    newton = True
    if eslmc == True:
        # starttime1 = timeit.default_timer()
        ed_functions, ToLiquidate = bs.agg_ed_esl(pop, spoils)
        # print('bs_agg_ed ' + str(timeit.default_timer() - starttime1))
        # starttime1 = timeit.default_timer()
        current_price = esl_mc.CircuitClearing(ed_functions, current_price)    
        # print('Circuit Clearing MC ' + str(timeit.default_timer() - starttime1))
    elif eslmc == False and newton == True:
        # starttime1 = timeit.default_timer()
        ed_functions, ToLiquidate = bs.agg_ed(pop, spoils)
        # print('bs_agg_ed ' + str(timeit.default_timer() - starttime1))
        # starttime1 = timeit.default_timer()
        if ed_functions[0](1) == np.nan:
            raise ValueError('Aggregate ED function at 1 equals NaN.')
        try: 
            current_price = optimize.newton(ed_functions[0], current_price, tol = 10_000, maxiter = 1000, disp=True)
            current_price = max(current_price, 0.01)
        except: 
            ''' Current price stays the same if the algorithm has not converged '''
            pass
        # current_price = optimize.brentq(ed_functions[0], 0.5 * current_price, 2 * current_price)
        # print('Newton method with tol and maxiter ' + str(timeit.default_timer() - starttime1))
    # starttime1 = timeit.default_timer()
    bs.calculate_tsv(pop, current_price, price_history)
    # print('Calc TSV ' + str(timeit.default_timer() - starttime1))
    # starttime1 = timeit.default_timer()
    price_history.append(current_price)       
    pop, mismatch = bs.calculate_edv(pop, current_price)
    # print('Price append and calc edv ' + str(timeit.default_timer() - starttime1))
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



