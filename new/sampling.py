from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
import numpy as np
import random
from operator import attrgetter
import parameters
import sys
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
creator.create("individual_ga", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = None, 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS, loan = 0, tsf = None, tsv = 0, edf = None, edv = 0)
# individual_ga is a list, individual_gp will be a gp.primitiveTree.

# Create the individual list 
toolbox.register("tf", random.randint, MIN_TIME_HORIZON, MAX_TIME_HORIZON)



toolbox.register("generate_tf_individual", tools.initCycle, creator.individual_ga, 
                 (toolbox.tf,), n=1)
toolbox.register("tf_population_creation", tools.initRepeat, list, toolbox.generate_tf_individual)
