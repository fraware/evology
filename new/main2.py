from parameters import *
from sampling import *
import sampling
from balance_sheet import *
from brownian_motion import *
from market_clearing import *
from ga import *

price = INITIAL_PRICE
extended_price_history = generate_bm_series(MAX_TIME_HORIZON+1)
extended_price_history = [abs(x) for x in extended_price_history]
# print(extended_price_history)

"""
0) Initialisation of market, initialisation of population.  """
pop = sampling.toolbox.gen_rd_pop(n=10)
print(pop)
for ind in pop:
    print (ind.type)

calculate_wealth(pop, price)

"""
1) 2) Compute TS and ED """

calculate_ts_edf(pop, extended_price_history)

""" 3) Market clearing """
price = leap_solver(pop, price)
print("Price is " + str(price))

""" 4) Apply ED """
calculate_edv(pop, price)

for ind in pop:
    print(ind.edv)

# TODO: apply the edv request, towards ind.asset and ind.cash

# temp
# sum_edv = 0
# for ind in pop:
#     print("-------tsv, edv----------")
#     print(ind.tsv)
#     print(ind.edv)
#     sum_edv += ind.edv
# print(sum_edv)
# end temp

""" 5) Apply dividends, interest rate, reinvestment
6) compute wealth, profits
## 7) hypermutate (initialise fitness as 0 to not impact evolution) LOC TBC ## """

pop, round_replacements = hypermutate(pop)
print(str(round_replacements) + " replacements done")

""" 8) Evolution block
    a. Fitness
    b. Adaptation
"""