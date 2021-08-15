import random
import numpy as np

RANDOM_SEED = 9 #random.random()

''' STRATEGY DISTRIBUTIONS '''
PROBA_GP = 0
PROBA_TF = 0.5
PROBA_VI = 0.4
PROBA_NT = 0.1

''' GA parmeters '''
POPULATION_SIZE = 4
MUTATION_RATE = 0.1
MAX_GENERATIONS = 3
CROSSOVER_RATE = 0.1
TOURNAMENT_SIZE = 3
PROBA_SELECTION = 0

''' GP PARAMETERS '''

''' STRATEGY PARAMETERS '''
MIN_TIME_HORIZON = 2
MAX_TIME_HORIZON = 10
LAMBDA_TF = 1


MIN_VALUATION_VI = 11
MAX_VALUATION_VI = 20
LAMBDA_VI = 1
STRATEGY_AGGRESSIVENESS_TF = 1
STRATEGY_AGGRESSIVENESS_VI = 1


MIN_VALUATION_NT = 11
MAX_VALUATION_NT = 20
LAMBDA_NT = 1
STRATEGY_AGGRESSIVENESS_NT = 1
GAMMA_NT = 0.12
MU_NT = 1
RHO_NT = 0.00045832561

''' MARKET PARAMETERS '''
TRADING_DAYS = 252
share_increment = 1
INITIAL_PRICE = 1 #100
price = INITIAL_PRICE
INITIAL_CASH = 10 #50_000_000
INITIAL_ASSETS = 5 #00_000
 # = Wealth of 100M; 100M is the threshold for US asset managers
short_bound = 1
CONSUMPTION_RATE = 1
 
REINVESTMENT_RATE = 1
INTEREST_RATE = 0.01 / TRADING_DAYS
EMA_HORIZON = 2 * TRADING_DAYS

DIVIDEND_GROWTH_RATE_G = 0.02
DIVIDEND_GROWTH_VOLATILITY = 0.06 / np.sqrt(TRADING_DAYS)
DIVIDEND_AUTOCORRELATION = 0.1 
INITIAL_DIVIDEND = 1 #100
INITIAL_RANDOM_DIVIDEND = 0
DIVIDEND_ATC_TAU = 3

''' RESULTS STORAGE '''
dividend_history = []
random_dividend_history = []
