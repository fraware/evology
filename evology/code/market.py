from parameters import *
import matplotlib
import matplotlib.pyplot as plt
import warnings
import balance_sheet as bs

def draw_dividend(dividend):
    global random_dividend

    DIVIDEND_GROWTH_RATE = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1
    
    random_dividend = random.normalvariate(0, 1)
    if len(random_dividend_history) > DIVIDEND_ATC_TAU:
        # random_dividend = (1 - DIVIDEND_AUTOCORRELATION ** 2) * random_dividend + DIVIDEND_AUTOCORRELATION * random_dividend_history[len(random_dividend_history) - 1 - DIVIDEND_ATC_TAU]
        random_dividend = (1 - DIVIDEND_AUTOCORRELATION ** 2) * random_dividend + DIVIDEND_AUTOCORRELATION * random_dividend_history[- 1 - DIVIDEND_ATC_TAU]

    dividend = abs(dividend + DIVIDEND_GROWTH_RATE * dividend + DIVIDEND_GROWTH_VOLATILITY * dividend * random_dividend)

    return dividend, random_dividend

def dividend_series(horizon):
    history = []
    dividend = INITIAL_DIVIDEND
    for i in range(horizon):
        dividend, rdiv = draw_dividend(dividend)
        history.append(dividend)
    return history



def determine_multiplier(pop):

    total_buy = 0
    total_sell = 0

    for ind in pop:
        if ind.edv > 0:
            # total_buy += math.floor(ind.edv)
            total_buy += (ind.edv)
        elif ind.edv < 0:
            # total_sell += math.floor(abs(ind.edv))
            total_sell += abs(ind.edv)


    if total_sell != 0:
        order_ratio = total_buy / total_sell 
    elif total_sell == 0:
        order_ratio = 0

    if order_ratio < 0:
            raise ValueError('Negative order ratio (total sell/buy): ' + str(total_sell) + str(total_buy))


    if order_ratio == 0: #either noone buys, or no one sells
        multiplier_buy = 0
        multiplier_sell = 0
        # No orders will be executed (no supply or no demand)
    elif order_ratio < 1:
        multiplier_buy = 1
        multiplier_sell = order_ratio
        # Selling will be restricted according to demand
    elif order_ratio == 1 :
        multiplier_buy = 1
        multiplier_sell = 1
        # All orders will be executed (supply =  demand)
    elif order_ratio > 1:
        multiplier_buy = 1 / order_ratio
        multiplier_sell = 1
        # Buying will be restricted according to supply

    if multiplier_buy == None:
        raise ValueError('Multiplier Buy is not defined')
    if multiplier_buy < 0:
        raise ValueError('Multiplier Buy is negative')
    if multiplier_sell == None:
        raise ValueError('Multiplier Sell is not defined')
    if multiplier_sell < 0:
        raise ValueError('Multiplier Sell is negative')

    return multiplier_buy, multiplier_sell


def execute_ed(pop, current_price, asset_supply):

    # Determine adjustements to edv if we have some mismatch
    multiplier_buy, multiplier_sell = determine_multiplier(pop)
    volume = 0


    for ind in pop:
        amount = 0

        # print(ind.edv)

        if ind.edv > 0:
            amount = ind.edv * multiplier_buy
        
        if ind.edv < 0:
            amount = ind.edv * multiplier_sell
            
        ind.asset += amount 
        ind.cash -= amount * current_price
        volume += abs(amount)

        # Apply some some readjustment to avoid negative cash
        if ind.cash < 0:
            ind.loan += abs(ind.cash)
            ind.cash = 0
        
    if bs.count_long_assets(pop) > asset_supply + 1 or bs.count_long_assets(pop) < asset_supply - 1:
        raise ValueError('Asset supply cst violated ' +str(bs.count_long_assets(pop)) + '/' + str(asset_supply))

    return pop, volume