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


pop = sampling.toolbox.gen_rd_pop(n=10) # Initialise market, population
calculate_wealth(pop, price)
calculate_ts_edf(pop, extended_price_history) # Compute TSV and EDF
price = leap_solver(pop, price) # Clear the market
print("Price is " + str(price))
calculate_edv(pop, price) # Compute EDV


# TODO: apply the edv request, towards ind.asset and ind.cash


""" 5) Apply dividends, interest rate, reinvestment
6) compute wealth, profits
## 7) hypermutate (initialise fitness as 0 to not impact evolution) LOC TBC ## """

pop, round_replacements = hypermutate(pop) # Replace insolvent agents
print(str(round_replacements) + " replacements done")

""" 8) Evolution block
    a. Fitness
    b. Adaptation
"""