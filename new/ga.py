from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
from sampling import *

def hypermutate(pop):
    round_replacements = 0
    pop_temp = list(map(toolbox.clone, pop))
    for i in range(0, len(pop_temp)):
        # if pop_temp[i][1] + pop_temp[i][9] <= 0:
        if pop_temp[i].wealth <= 0:
            pop_temp[i] = toolbox.gen_rd_ind()
            del pop_temp[i].fitness.values
            # global round_replacements
            round_replacements += 1
    pop[:] = pop_temp
    return pop, round_replacements

def compute_fitness(pop):
    for ind in pop:
        ema = (2 / (EMA_HORIZON + 1)) * (ind.profit - ind.ema) + ind.ema
        ind.ema = ema
        ind.fitness.values = ema,
    return ind