from parameters import *

def draw_dividend(dividend):
    
    # global dividend
    global random_dividend

    DIVIDEND_GROWTH_RATE = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1
    
    random_dividend = random.normalvariate(0, 1)
    if len(random_dividend_history) > DIVIDEND_ATC_TAU:
        random_dividend = (1 - DIVIDEND_AUTOCORRELATION ** 2) * random_dividend + DIVIDEND_AUTOCORRELATION * random_dividend_history[len(random_dividend_history) - 1 - DIVIDEND_ATC_TAU]

    dividend = abs(dividend + DIVIDEND_GROWTH_RATE * dividend + DIVIDEND_GROWTH_VOLATILITY * dividend * random_dividend)

    return dividend, random_dividend

