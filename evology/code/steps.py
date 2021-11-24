
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
        agg_edf, ToLiquidate = bs.agg_ed(pop, spoils)
        # current_price = optimize.brentq(agg_edf, 0.5 * current_price, 2 * current_price)
        # current_price = steff(agg_edf, x)

    # print(agg_edf)
    # print(agg_edf(1))
    # if current_price < 0:
    #     raise ValueError('Negative current price before esl solve. ' + str(bs.report_types(pop)))
    # 
    
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





# from typing import Callable, Iterator
# Func = Callable[[float], float]

# def g(f: Func, x: float, fx: float) -> Func:
#     """First-order divided difference function.

#     Arguments:
#         f: Function input to g
#         x: Point at which to evaluate g
#         fx: Function f evaluated at x 
#     """
#     return lambda x: f(x + fx) / fx - 1

# def steff(f: Func, x: float) -> Iterator[float]:
#     """Steffenson algorithm for finding roots.

#     This recursive generator yields the x_{n+1} value first then, when the generator iterates,
#     it yields x_{n+2} from the next level of recursion.

#     Arguments:
#         f: Function whose root we are searching for
#         x: Starting value upon first call, each level n that the function recurses x is x_n
#     """
#     while True:    
#         fx = f(x)
#         gx = g(f, x, fx)(x)
#         if gx == 0:
#             break
#         else:
#             x = x - fx / gx    # Update to x_{n+1}
#             yield x            # Yield value