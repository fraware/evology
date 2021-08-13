""" main 2 """
from parameters import * #to import all functions and variables

"""
0) Initialisation of market, initialisation of population.  """
# pop = population_creation(n=POPULATION_SIZE)
    
## Requires a first wealth comput.
"""
1) Compute TS """
# compute_ts function
"""
2) Compute ED
3) Market clearing
4) Apply ED
5) Apply dividends, interest rate, reinvestment
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