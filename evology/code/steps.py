
import balance_sheet as bs
import ga as ga
import timeit
from parameters import SHIELD_DURATION
import esl_market_clearing as esl_mc
import market as mk
import shield as sh
import creation as cr
from scipy import optimize

eslmc = True

def update_wealth(pop, current_price, generation, wealth_coordinates, POPULATION_SIZE, reset_wealth):
    starttime = timeit.default_timer()
    bs.calculate_wealth(pop, current_price) # Compute agents' wealth
    bs.update_profit(pop)
    bs.ComputeReturn(pop)
    # sh.WealthReset(pop, wealth_coordinates, generation, reset_wealth, current_price)
    pop = cr.WealthReset(pop, wealth_coordinates, generation, reset_wealth, current_price)

    # TODO: add one more compute wealth
    # TODO: wealth shiled creates returns
    # TODO" clean all code
    timeA = timeit.default_timer() - starttime
    return pop, timeA

def ga_evolution(pop, mode, generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE):
    starttime = timeit.default_timer()
    if generation > SHIELD_DURATION:
        ga.compute_fitness(pop)
        pop = ga.strategy_evolution(mode, pop, PROBA_SELECTION, MUTATION_RATE, wealth_coordinates)
    timeC = timeit.default_timer() - starttime
    return pop, timeC

def decision_updates(pop, mode, price_history, extended_dividend_history):
    starttime = timeit.default_timer()
    bs.determine_tsv_proc(mode, pop, price_history)
    bs.update_fval(pop, extended_dividend_history)
    bs.determine_edf(pop)
    timeD = timeit.default_timer() - starttime
    return pop, timeD

def marketClearing(pop, current_price, price_history, spoils):
    starttime = timeit.default_timer()

    if eslmc == True:
        ed_functions, ToLiquidate = bs.agg_ed_esl(pop, spoils)
        current_price = float(esl_mc.solve(ed_functions, current_price)[0])
    elif eslmc == False:
        ed_functions, ToLiquidate = bs.agg_ed(pop, spoils)
        agg_edf = ed_functions[0]
        current_price = optimize.brentq(agg_edf, 0.5 * current_price, 2 * current_price)
        # current_price = steff(agg_edf, x)
    
    bs.calculate_tsv(pop, current_price, price_history)
    price_history.append(current_price)       
    pop, mismatch = bs.calculate_edv(pop, current_price)
    timeE = timeit.default_timer() - starttime
    return pop, mismatch, current_price, price_history, ToLiquidate, timeE

def marketActivity(pop, current_price, asset_supply, dividend, dividend_history, extended_dividend_history, spoils, ToLiquidate):
    starttime = timeit.default_timer()
    pop, volume, spoils = mk.execute_ed(pop, current_price, asset_supply, spoils, ToLiquidate)
    pop, dividend, random_dividend = bs.earnings(pop, dividend) 
    dividend_history.append(dividend)
    extended_dividend_history.append(dividend)
    bs.update_margin(pop, current_price)
    bs.clear_debt(pop, current_price)
    timeF = timeit.default_timer() - starttime
    return pop, volume, dividend, random_dividend, dividend_history, extended_dividend_history, spoils, timeF

