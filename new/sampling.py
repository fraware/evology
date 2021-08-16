from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
import numpy as np
import random
toolbox = base.Toolbox()
from parameters import *

# Create the fitness object
creator.create("fitness_strategy", base.Fitness, weights=(1.0,))

# Create the individual object
""" Agent attributes
- type 
- wealth, cash, asset, loan
- tsf, tsv
- edf, edv
"""

creator.create("ind_tf", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type ="tf", 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, margin = 0, tsf = None, tsv = 0, edf = None, edv = 0, process = 0, ema = 0)

creator.create("ind_vi", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = "vi", 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, margin = 0, tsf = None, tsv = 0, edf = None, edv = 0, process = 0, ema = 0)

creator.create("ind_nt", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = "nt", 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, margin = 0, tsf = None, tsv = 0, edf = None, edv = 0, process = 1, ema = 0)
# individual_ga is a list, individual_gp will be a gp.primitiveTree.

# Create the individual list 
toolbox.register("tf", random.randint, MIN_TIME_HORIZON, MAX_TIME_HORIZON)
toolbox.register("gen_tf_ind", tools.initCycle, creator.ind_tf, (toolbox.tf,), n=1)
toolbox.register("gen_tf_pop", tools.initRepeat, list, toolbox.gen_tf_ind)

toolbox.register("vi", random.randint, MIN_VALUATION_VI, MAX_VALUATION_VI)
toolbox.register("gen_vi_ind", tools.initCycle, creator.ind_vi, (toolbox.vi,), n=1)
toolbox.register("gen_vi_pop", tools.initRepeat, list, toolbox.gen_vi_ind)

toolbox.register("nt", random.randint, MIN_VALUATION_NT, MAX_VALUATION_NT)
toolbox.register("gen_nt_ind", tools.initCycle, creator.ind_nt, (toolbox.nt,), n=1)
toolbox.register("gen_nt_pop", tools.initRepeat, list, toolbox.gen_nt_ind)

def gen_rd_ind(PROBA_TF, PROBA_VI, PROBA_NT):
        rd = random.random()
        if rd <= PROBA_TF:
            return toolbox.gen_tf_ind()
        elif rd > PROBA_TF and rd <= PROBA_TF + PROBA_VI:
            return toolbox.gen_vi_ind()
        elif rd > PROBA_TF + PROBA_VI and rd <= PROBA_TF + PROBA_VI + PROBA_NT:
            return toolbox.gen_nt_ind()
    
# toolbox.register("rd", rd_strategy, PROBA_TF, PROBA_VI)

toolbox.register("gen_rd_ind", gen_rd_ind, PROBA_TF, PROBA_VI, PROBA_NT)
toolbox.register("gen_rd_pop", tools.initRepeat, list, toolbox.gen_rd_ind)


# pop = toolbox.gen_rd_pop(n=10)
# print(pop)
# for ind in pop:
#     print (ind.type)