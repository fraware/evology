import numpy as np

from parameters import *


def calculate_wealth(pop, price):
    for ind in pop:
        ind.wealth = ind.cash + ind.asset * price - ind.loan
    return ind

def calculate_ts_edf(pop, extended_price_history):
    for ind in pop:
        if ind.type == "tf":
            ind.tsv = (np.log2(extended_price_history[-1]) - np.log2(extended_price_history[-ind[0]])) 
            def func(p):
                return (ind.wealth * LAMBDA_TF / p) * (np.tanh(STRATEGY_AGGRESSIVENESS_TF * ind.tsv) + 0.5) - ind.asset 
            ind.edf = func
        elif ind.type == "vi":
            def func(p):
                return (ind.wealth * LAMBDA_VI / p) * (np.tanh(STRATEGY_AGGRESSIVENESS_VI * (np.log2(ind[0]) - np.log2(p))) + 0.5) - ind.asset 
            ind.edf = func
        elif ind.type == "nt":
            ind.process = ind.process + RHO_NT * (MU_NT - ind.process) + GAMMA_NT * random.normalvariate(0,1)
            print(ind.type)
            print(ind[0])
            print(ind.process)
            print((np.log2(ind[0] * ind.process)))
            print("--------------------")
            print(ind.wealth * LAMBDA_NT)
            print(np.tanh(STRATEGY_AGGRESSIVENESS_NT * (np.log2(ind[0] * ind.process))))
            def func(p):
                return (ind.wealth * LAMBDA_NT / p) * (np.tanh(STRATEGY_AGGRESSIVENESS_NT * (np.log2(ind[0] * ind.process)) -  np.log2(p)) + 0.5) - ind.asset 
            ind.edf = func            
    return ind

# def calculate_edf(pop):
#     for ind in pop:
#         def func(x):
#             return (ind.wealth * LAMBDA_TF / x) * (np.tanh(STRATEGY_AGGRESSIVENESS_TF * ind.tsv) + 0.5) - ind.asset
#         ind.edf = func
#     return ind

def calculate_edv(pop, price):
    for ind in pop:
        ind.edv = ind.edf(price)
