import numpy as np
from parameters import *

def calculate_wealth(pop, price):
    for ind in pop:
        ind.wealth = ind.cash + ind.asset * price - ind.loan
    return ind

def calculate_ts(pop, extended_price_history):
    for ind in pop:
        if ind.type == "tf":
            def func(x):
                return (np.log2(x[-1]) - np.log2(x[-ind[0]]))   
            ind.tsf = func
            ind.tsv = func(extended_price_history) 
    return ind

def calculate_edf(pop):
    for ind in pop:
        def func(x):
            return (ind.wealth * LAMBDA_TF / x) * (np.tanh(STRATEGY_AGGRESSIVENESS_TF * ind.tsv) + 0.5) - ind.asset
        ind.edf = func
    return ind

def calculate_edv(pop, price):
    for ind in pop:
        ind.edv = ind.edf(price)