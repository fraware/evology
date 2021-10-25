from operator import index
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
- wealth, cash, asset_long, asset_short, loan
- tsf, tsv
- edf, edv
"""

creator.create("ind_tf", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type ="tf", 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, margin = 0, tsf = None, tsv = 0, edf = None, 
    edv = 0, process = 0, ema = 0, profit = 0, prev_wealth = 0, leverage = 1)

creator.create("ind_vi", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = "vi", 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, margin = 0, tsf = None, tsv = 0, edf = None, 
    edv = 0, process = 0, ema = 0, profit = 0, prev_wealth = 0, leverage = 1)

creator.create("ind_nt", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = "nt", 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, margin = 0, tsf = None, tsv = 0, edf = None, 
    edv = 0, process = 1, ema = 0, profit = 0, prev_wealth = 0, leverage = 1)
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

toolbox.register("gen_rd_ind", gen_rd_ind, PROBA_TF, PROBA_VI, PROBA_NT)
toolbox.register("gen_rd_pop", tools.initRepeat, list, toolbox.gen_rd_ind)


def gen_ref_pop():
    pop = []
    pop.append(toolbox.gen_tf_ind())
    pop.append(toolbox.gen_vi_ind())
    pop.append(toolbox.gen_nt_ind())
    return pop
toolbox.register("gen_ref_pop", gen_ref_pop) 

def adjust_mode(pop, mode):
    if mode == "between":
        for ind in pop:
            if ind.type == "tf":
                ind[0] = 2
            if ind.type == "vi":
                ind[0] = INITIAL_DIVIDEND / EQUITY_COST - DIVIDEND_GROWTH_RATE_G
            if ind.type == "nt":
                ind[0] = INITIAL_DIVIDEND / EQUITY_COST - DIVIDEND_GROWTH_RATE_G
    return pop

def create_pop(mode, POPULATION_SIZE):
    if POPULATION_SIZE == 3 and mode == "between":
        # Create a Scholl et al. like population
        pop = adjust_mode(toolbox.gen_ref_pop(), mode)
        count_tf, count_vi, count_nt = 0, 0, 0
        for ind in pop:
            if ind.type == "tf":
                count_tf += 1
            if ind.type == "vi":
                count_vi += 1
            if ind.type == "nt":
                count_nt += 1
        if count_tf == 1 and count_nt == 1 and count_vi == 1:
            pass
        else:
            raise ValueError('Population of 3 from Scholl et al. is not balanced.')
    if POPULATION_SIZE != 3 and mode == "between":
        # Create a random population with unique strategy per type
        pop = adjust_mode(toolbox.gen_rd_pop(n=POPULATION_SIZE), mode)
    if POPULATION_SIZE != 3 and mode != "between":
        # Create a random population with diversity within each type
        pop = toolbox.gen_rd_pop(n=POPULATION_SIZE)

    for ind in pop:
        if ind.type == 'tf':
            ind.leverage = LAMBDA_TF
        if ind.type == 'vi':
            ind.leverage = LAMBDA_VI
        if ind.type == 'nt':
            ind.leverage = LAMBDA_NT

    return pop
