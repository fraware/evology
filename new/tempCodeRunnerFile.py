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
- wealth, cash, asset
"""
creator.create("individual_ga", list, typecode = 'd', fitness=creator.fitness_strategy, wealth=0, type = None, 
    cash = INITIAL_CASH, asset = INITIAL_ASSETS)
