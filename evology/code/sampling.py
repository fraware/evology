# from operator import index


# import sys
# sys.path.append('/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')


# from deap import base
# from deap import creator
# from deap import tools
# from deap import algorithms
# from deap import gp
# import numpy as np
# import random
# toolbox = base.Toolbox()
# from parameters import *

# # Create the fitness object
# creator.create("fitness_strategy", base.Fitness, weights=(1.0,))

# # Create the individual object
# """ Agent attributes
# - type 
# - wealth, cash, asset_long, asset_short, loan
# - tsf, tsv
# - edf, edv
# """

# creator.create("ind_tf", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type ="tf", MonReturn = 0,
#     cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = INITIAL_LOAN, margin = 0, tsf = None, tsv = 0, edf = None, MonWealth = np.zeros((1, 21)),
#     edv = 0, process = 1, ema = 0, profit = 0, prev_wealth = INITIAL_CASH + INITIAL_ASSETS * INITIAL_PRICE, leverage = 1)

# creator.create("ind_vi", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = "vi", MonReturn = 0,
#     cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = INITIAL_LOAN, margin = 0, tsf = None, tsv = 0, edf = None, MonWealth = np.zeros((1, 21)),
#     edv = 0, process = 1, ema = 0, profit = 0, prev_wealth = INITIAL_CASH + INITIAL_ASSETS * INITIAL_PRICE, leverage = 1)

# creator.create("ind_nt", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = "nt", MonReturn = 0,
#     cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = INITIAL_LOAN, margin = 0, tsf = None, tsv = 0, edf = None, MonWealth = np.zeros((1, 21)),
#     edv = 0, process = 1, ema = 0, profit = 0, prev_wealth = INITIAL_CASH + INITIAL_ASSETS * INITIAL_PRICE, leverage = 1)
# # individual_ga is a list, individual_gp will be a gp.primitiveTree.

# # Create the individual list 
# toolbox.register("tf", random.randint, MIN_TIME_HORIZON, MAX_TIME_HORIZON)
# toolbox.register("gen_tf_ind", tools.initCycle, creator.ind_tf, (toolbox.tf,), n=1)
# toolbox.register("gen_tf_pop", tools.initRepeat, list, toolbox.gen_tf_ind)

# toolbox.register("vi", random.randint, MIN_VALUATION_VI, MAX_VALUATION_VI)
# toolbox.register("gen_vi_ind", tools.initCycle, creator.ind_vi, (toolbox.vi,), n=1)
# toolbox.register("gen_vi_pop", tools.initRepeat, list, toolbox.gen_vi_ind)

# toolbox.register("nt", random.randint, MIN_VALUATION_NT, MAX_VALUATION_NT)
# toolbox.register("gen_nt_ind", tools.initCycle, creator.ind_nt, (toolbox.nt,), n=1)
# toolbox.register("gen_nt_pop", tools.initRepeat, list, toolbox.gen_nt_ind)



# def gen_ref_pop():
#     pop = []
#     pop.append(toolbox.gen_tf_ind())
#     pop.append(toolbox.gen_vi_ind())
#     pop.append(toolbox.gen_nt_ind())
#     return pop
# toolbox.register("gen_ref_pop", gen_ref_pop) 

# def adjust_mode(pop, mode):
#     if mode == "between":
#         for ind in pop:
#             if ind.type == "tf":
#                 ind[0] = 2
#             if ind.type == "vi":
#                 ind[0] = 100
#             if ind.type == "nt":
#                 ind[0] = 100
#     return pop

