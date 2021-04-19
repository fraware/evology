import math
import random

import parameters

# =============================================================================
# Fixed parameters
# =============================================================================

# RANDOM_SEED = random.random()
# POPULATION_SIZE = 4
# MAX_TIME_HORIZON = 10
# MUTATION_RATE = 0
# MAX_GENERATIONS = 50
# CROSSOVER_RATE = 0
# MIN_WEALTH = 10
# MAX_WEALTH = 10
# MIN_TIME_HORIZON = 1
# INITIAL_PRICE = 1
# TOURNAMENT_SIZE = 3

REINVESTMENT_RATE = parameters.REINVESTMENT_RATE
INTEREST_RATE = parameters.REINVESTMENT_RATE

EMA_HORIZON = parameters.EMA_HORIZON


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def draw_dividend():
    '''
    @Maarten: issues with the equations defining  the dividend process
    I temporarily have a random dividend in (0,1)
    '''
    global dividend
    dividend = truncate(random.randint(0,1),3)
    print("Dividend today is " + str(dividend))
    return dividend

        
def wealth_earnings(pop):
    for ind in pop:
        # Update profit
        ind[7] = truncate(REINVESTMENT_RATE * (INTEREST_RATE * ind[2] + dividend * ind[3]),3)
        print("profit is " + str(ind[7]))
        
        # Update cash
        ind[2] += REINVESTMENT_RATE * (INTEREST_RATE * ind[2] + dividend * ind[3])
        ind[2] = truncate(ind[2],3)
    return ind

def update_wealth(pop, price):
    for ind in pop:
        ind[1] = truncate(ind[2] + ind[3] * price  - ind[4],3)
    return ind
        
def compute_ema(pop):
    for ind in pop:
        ind[8] = truncate((2 / (EMA_HORIZON + 1)) * (ind[7] - ind[8]) + ind[8],3)
    return ind