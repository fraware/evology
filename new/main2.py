from parameters import *
from sampling import *
from balance_sheet import *
from brownian_motion import *
from market_clearing import *
price = INITIAL_PRICE
extended_price_history = generate_bm_series(MAX_TIME_HORIZON+1)
extended_price_history = [abs(x) for x in extended_price_history]
# print(extended_price_history)
"""
0) Initialisation of market, initialisation of population.  """
pop = toolbox.tf_population_creation(n=10)
calculate_wealth(pop, price)

"""
1) Compute TS """

# temp
for ind in pop:
    ind.type = "tf"
# end temp  

calculate_ts(pop, extended_price_history)

"""
2) Compute ED """
calculate_edf(pop)
"""
3) Market clearing """
price = leap_solver(pop, price)
print(price)

""" 4) Apply ED """
calculate_edv(pop, price)

# temp
sum_edv = 0
for ind in pop:
    print("-------tsv, edv----------")
    print(ind.tsv)
    print(ind.edv)
    sum_edv += ind.edv
print(sum_edv)
# end temp

""" 5) Apply dividends, interest rate, reinvestment
6) compute wealth, profits
## 7) hypermutate (initialise fitness as 0 to not impact evolution) LOC TBC ##
8) Evolution block
    a. Fitness
    b. Adaptation




def update_excess_demand(pop):
    for ind in pop:
        ind[6] = truncate(ind[1] * LAMBDA_TF * (np.tanh(STRATEGY_AGGRESSIVENESS_TF * ind[5]) + 0.5),4)
    return ind
market.update_excess_demand(pop)
"""