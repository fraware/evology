from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
import random
from operator import attrgetter
import parameters


# # =============================================================================
# # Fixed parameters
# # =============================================================================

RANDOM_SEED = parameters.RANDOM_SEED
POPULATION_SIZE = parameters.POPULATION_SIZE
MAX_TIME_HORIZON = parameters.MAX_TIME_HORIZON
MUTATION_RATE = parameters.MUTATION_RATE
MAX_GENERATIONS = parameters.MAX_GENERATIONS
CROSSOVER_RATE = parameters.CROSSOVER_RATE
MIN_TIME_HORIZON = parameters.MIN_TIME_HORIZON
INITIAL_PRICE = parameters.INITIAL_PRICE
TOURNAMENT_SIZE = parameters.TOURNAMENT_SIZE 
INITIAL_ASSETS = parameters.INITIAL_ASSETS
INITIAL_CASH = parameters.INITIAL_CASH

toolbox = base.Toolbox()

# Create the fitness object
creator.create("fitness_strategy", base.Fitness, weights=(1.0,))
# Create the individual object
creator.create("individual", list, typecode = 'd', fitness=creator.fitness_strategy)
# Create the individual list 
toolbox.register("generate_strategy", random.randint, MIN_TIME_HORIZON, MAX_TIME_HORIZON)
toolbox.register("generate_wealth", random.randint, 0, 0)
toolbox.register("generate_cash", random.randint, INITIAL_CASH, INITIAL_CASH)
toolbox.register("generate_asset", random.randint, INITIAL_ASSETS, INITIAL_ASSETS)
toolbox.register("generate_loan", random.randint, 0, 0)
toolbox.register("generate_trading_signal", random.randint, 0, 0)
toolbox.register("generate_excess_demand", random.randint, 0, 0)
toolbox.register("generate_profit", random.randint, 0, 0)
toolbox.register("generate_ema", random.randint, 0, 0)
toolbox.register("generate_margin", random.randint, 0, 0)

toolbox.register("generate_individual", tools.initCycle, creator.individual, 
                 (toolbox.generate_strategy, toolbox.generate_wealth, 
                  toolbox.generate_cash, toolbox.generate_asset, 
                  toolbox.generate_loan, toolbox.generate_trading_signal, 
                  toolbox.generate_excess_demand,toolbox.generate_profit,
                  toolbox.generate_ema, toolbox.generate_margin), n=1)
toolbox.register("population_creation", tools.initRepeat, list, toolbox.generate_individual)

toolbox.register("generate_no_asset", random.randint, 0, 0)

toolbox.register("generate_hyper_individual", tools.initCycle, creator.individual, 
                 (toolbox.generate_strategy, toolbox.generate_wealth, 
                  toolbox.generate_cash, toolbox.generate_no_asset, 
                  toolbox.generate_loan, toolbox.generate_trading_signal, 
                  toolbox.generate_excess_demand,toolbox.generate_profit,
                  toolbox.generate_ema, toolbox.generate_margin), n=1)

# Fitness definition
def ema_fitness(individual):
    return individual[8],

toolbox.register("evaluate", ema_fitness)

# Creating our own crossover operator:
def feasible_crossover(ind1,ind2,CROSSOVER_RATE):
    if random.random() < CROSSOVER_RATE:
        upperb = max(ind1,ind2)[0]
        lowerb = min (ind1,ind2)[0]
        ind1[0] = random.randint(lowerb,upperb)
        ind2[0] = random.randint(lowerb,upperb)
        return ind1[0], ind2[0]

toolbox.register("feasible_crossover", feasible_crossover)
toolbox.register("mate", toolbox.feasible_crossover)

# Creating our own mutation operator
def mutate_both_ways(ind):
    if random.random() < 0.5:
        ind[0] -= 1
    else: 
        ind[0] += 1

def feasible_mutation(ind, MUTATION_RATE):
    if random.random() < MUTATION_RATE:
        if ind[0] == MAX_TIME_HORIZON: #we can only mutate lower
            ind[0] -= 1
        elif ind[0] == 1: #we can only mutate higher
            ind[0] += 1
        else: 
            mutate_both_ways(ind) # we can mutate lower or higher
    return(ind)

toolbox.register("feasible_mutation", feasible_mutation)
toolbox.register("mutate", toolbox.feasible_mutation)

def random_decimal(low, high):
    # number = float(random.randint(low*1000, high*1000))/1000
    global number
    if low >= 0 and high >= 0:
        number = float(random.randint(round(low*1000),round(high*1000))/1000)
    if low < 0 and high < 0:
        number = - float(random.randint(round(-low*1000),round(-high*1000))/1000)
    return number


def selRandom(individuals, k):
    return [random.choice(individuals) for i in range(k)]

# Creation of our customised selection operator (outnrament) that handles positive & negative fitness values
def selTournament(individuals, k, tournsize, fit_attr="fitness"):
    chosen = []
    for i in range(k):
        chosen_i = []
        aspirants = selRandom(individuals, tournsize-1) 
        aspirants.append(individuals[i])
        chosen_i = max(aspirants, key=attrgetter(fit_attr))
        chosen_i[1:10] = individuals[i][1:10]
        chosen.append(chosen_i)
    return chosen

toolbox.register("selTournament", selTournament)
toolbox.register("select", toolbox.selTournament)

# Define the hypermutation (insolvency) parameter
round_replacements = 0
def hypermutate(pop):
    pop_temp = list(map(toolbox.clone, pop))
    round_replacements = 0
    for i in range(0, len(pop_temp)):
        # if pop_temp[i][1] + pop_temp[i][9] <= 0:
        if pop_temp[i][1] <= 0:
            pop_temp[i] = toolbox.generate_hyper_individual()
            del pop_temp[i].fitness.values
            # global round_replacements
            round_replacements += 1
    pop[:] = pop_temp
    return pop, round_replacements
toolbox.register("hypermutate", hypermutate)

# Function to recompute fitness of invalid individuals
def fitness_for_invalid(offspring):
    freshIndividuals = [ind for ind in offspring if not ind.fitness.valid]
    freshFitnessValues = list(map(toolbox.evaluate, freshIndividuals))
    for individual, fitnessValue in zip(freshIndividuals, freshFitnessValues):
        individual.fitness.values = fitnessValue
