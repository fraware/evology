import random
import numpy as np

RANDOM_SEED = 9 #random.random()

''' STRATEGY DISTRIBUTIONS '''
PROBA_GP = 0
PROBA_TF = 0.5
PROBA_VI = 0.4
PROBA_NT = 0.1

''' GA parmeters '''
POPULATION_SIZE = 10
MUTATION_RATE = 1/21
MAX_GENERATIONS = 3
CROSSOVER_RATE = 1/21
TOURNAMENT_SIZE = 3
PROBA_SELECTION = 1/21

''' GP PARAMETERS '''

''' STRATEGY PARAMETERS '''

# General parameters

LAMBDA_TF = 2/3
LAMBDA_VI = 3
LAMBDA_NT = 2/3
SCALE_TF = 4
SCALE_VI = 3
SCALE_NT = 5

GAMMA_NT = 0.012
MU_NT = 1
RHO_NT = 0.00045832561

# For within evolution
MIN_TIME_HORIZON = 2
MAX_TIME_HORIZON = 10

MIN_VALUATION_VI = 11
MAX_VALUATION_VI = 20

MIN_VALUATION_NT = 11
MAX_VALUATION_NT = 20

''' MARKET PARAMETERS '''
TRADING_DAYS = 252
share_increment = 1
INITIAL_PRICE = 100

price = INITIAL_PRICE
INITIAL_CASH = 50_000_000
INITIAL_ASSETS = 500_000
short_bound = 1
CONSUMPTION_RATE = 0
LIMIT_SHORT_POS_SIZE = 10
 
REINVESTMENT_RATE = 1
INTEREST_RATE = 0.01 / TRADING_DAYS
EMA_HORIZON = 2 * TRADING_DAYS

DIVIDEND_GROWTH_RATE_G = 0.01
EQUITY_COST = 0.02
DIVIDEND_GROWTH_VOLATILITY = (0.06 / np.sqrt(TRADING_DAYS))
DIVIDEND_AUTOCORRELATION = 0.1 
INITIAL_DIVIDEND = 0.003983
INITIAL_RANDOM_DIVIDEND = 0
DIVIDEND_ATC_TAU = 1
dividend = INITIAL_DIVIDEND

ORDER_BATCH_SIZE = 1000

''' RESULTS STORAGE '''
dividend_history = []
random_dividend_history = []

