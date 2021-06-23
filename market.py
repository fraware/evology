import math
import random
import parameters
import numpy as np

REINVESTMENT_RATE = parameters.REINVESTMENT_RATE
INTEREST_RATE = parameters.INTEREST_RATE
EMA_HORIZON = parameters.EMA_HORIZON
DIVIDEND_GROWTH_RATE_G = parameters.DIVIDEND_GROWTH_RATE_G
DIVIDEND_GROWTH_VOLATILITY = parameters.DIVIDEND_GROWTH_VOLATILITY
DIVIDEND_AUTOCORRELATION = parameters.DIVIDEND_AUTOCORRELATION

dividend_history = parameters.dividend_history
random_dividend_history = parameters.random_dividend_history
random_dividend = parameters.INITIAL_RANDOM_DIVIDEND
dividend = parameters.INITIAL_DIVIDEND
DIVIDEND_ATC_TAU = parameters.DIVIDEND_ATC_TAU
TRADING_DAYS = parameters.TRADING_DAYS
LAMBDA_TF = parameters.LAMBDA_TF
STRATEGY_AGGRESSIVENESS_TF = parameters.STRATEGY_AGGRESSIVENESS_TF

# Agent representaiton:
#     [Theta Wealth Cash Asset Loan TradingSignal ExcessDemand     Profit     EMA profit]
#     [ 0       1     2    3     4         5             6           7            8 ]

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def determine_dividend_growth(DIVIDEND_GROWTH_RATE_G):
    global DIVIDEND_GROWTH_RATE
    DIVIDEND_GROWTH_RATE = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1
    return DIVIDEND_GROWTH_RATE

'''
def draw_dividend(DIVIDEND_GROWTH_RATE):
    
    global dividend
    global random_dividend
    random_dividend = random.normalvariate(0, 1)
    if len(random_dividend_history) > DIVIDEND_ATC_TAU:
        random_dividend = (1 - DIVIDEND_AUTOCORRELATION ** 2) * random.normalvariate(0,1) + DIVIDEND_AUTOCORRELATION * random_dividend_history[-1 - DIVIDEND_ATC_TAU]
    dividend = abs(dividend + DIVIDEND_GROWTH_RATE * dividend + DIVIDEND_GROWTH_VOLATILITY * dividend * random_dividend)
    # print("Dividend today is " + str(dividend))
    return dividend, random_dividend
'''

def draw_dividend(DIVIDEND_GROWTH_RATE):
    
    global dividend
    global random_dividend
    
    random_dividend = truncate(random.normalvariate(0, 1),3)
    if len(random_dividend_history) > DIVIDEND_ATC_TAU:
        random_dividend = (1 - DIVIDEND_AUTOCORRELATION ** 2) * random_dividend + DIVIDEND_AUTOCORRELATION * random_dividend_history[len(random_dividend_history) - 1 - DIVIDEND_ATC_TAU]
    # wiener.append(random_dividend)
    
    dividend = abs(dividend + DIVIDEND_GROWTH_RATE * dividend + DIVIDEND_GROWTH_VOLATILITY * dividend * random_dividend)
    dividend = truncate(dividend, 3)
    return dividend, random_dividend

        
def wealth_earnings(pop, dividend):
    # print(INTEREST_RATE)
    # print(REINVESTMENT_RATE)
    for ind in pop:
        # Update profit
        ind[7] = truncate(REINVESTMENT_RATE * (INTEREST_RATE * ind[2] + dividend * ind[3]),3)
        # print("profit is " + str(ind[7]))
        
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
        ind[8] = truncate((2 / (EMA_HORIZON + 1)) * (ind[7] - ind[8]) + ind[8],4)
    return ind

        # Agent representaiton:
#     [Theta Wealth Cash Asset Loan TradingSignal ExcessDemand     Profit     EMA profit]
#     [ 0       1     2    3     4         5             6           7            8 ]

def update_trading_signal(pop, extended_price_history):
    '''
    Will require an update once we add different strategies
    '''

    for ind in pop:
        if len(extended_price_history) > 1:
            if len(extended_price_history) > ind[0]:
                ind[5] = truncate(np.log2(extended_price_history[-1]) - np.log2(extended_price_history[-ind[0]]),3)
            if len(extended_price_history) <= ind[0]:
                # The trader does not have the information to run her strategy. She waits in indifference.
                ind[5] = 0
        if len(extended_price_history) <= 1:
            ind[5] = 0
    return ind

def update_excess_demand(pop):
    for ind in pop:
        ind[6] = truncate(ind[1] * LAMBDA_TF * (np.tanh(STRATEGY_AGGRESSIVENESS_TF * ind[5]) + 0.5),4)
    return ind

def order_excess_demand(pop):
    list_excess_demand_func = []
    for ind in pop:

        
        def ed(x):
            
            return truncate((ind[6] / x) - ind[3],4)
        list_excess_demand_func.append(ed)
        print(ed(1))
        del ed
    return list_excess_demand_func

def compute_aggregate_excess_demand(pop, list_excess_demand_func):
    def aggregate_ed(x):
        result = 0
        for i in range(len(pop)):
            result += list_excess_demand_func[i](x)
        return result
    return aggregate_ed

def count_assets(pop):
    count = 0
    for ind in pop:
        count += ind[3]
    return count


def update_inventory (pop, price, assetQ):
    for ind in pop:
        former_asset = ind[3]
        former_loan = ind[4]
        realised_ed = truncate(ind[6] / price - ind[3],4)
        print("agent wants up to " + str(realised_ed)) #this is correct
        
        
        ''' If we want to buy assets: non-negative cash buying procedure '''
        cash = ind[2] + ind[3] * price + former_loan - ind[4]
        i = 0
        # print("agent wants up to " + str(realised_ed))
        while i < realised_ed:
            if cash - price > 0:
                if count_assets(pop) < assetQ:
                    ind[3] += 1
                    cash -= price
            i += 1
        ind[2] = cash 
        print("agent got " + str(ind[3] - former_asset))

        
        # If short selling, set some margin aside
        if ind[3] < 0:
            ind[9] += ind[3] * price
        
        # Update new cash if result is positive
        # new_cash = truncate(ind[2] - (ind[3] - former_asset) * price - ind[4] + former_loan - ind[9],3)
        # if new_cash >= 0:
        #     ind[2] = new_cash 
        # else: 
        #     print("Error negative cash" + str(ind))
        #     print(realised_ed)
        
        #	 Clear the margin if we are out of the short position
        if ind[3] >= 0:
            ind[2] += ind[9]
            ind[9] = 0
    return ind

