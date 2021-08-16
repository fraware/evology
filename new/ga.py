from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from operator import attrgetter
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

# Creating our own crossover operator:
def feasible_crossover(ind1,ind2,CROSSOVER_RATE):
    print("--------------")
    print(ind1, ind2)
    print(ind1.type, ind2.type)
    if ind1.type == ind2.type:
        if random.random() < CROSSOVER_RATE:
            upperb = max(ind1,ind2)[0]
            lowerb = min (ind1,ind2)[0]
            ind1[0] = random.randint(lowerb,upperb)
            ind2[0] = random.randint(lowerb,upperb)
        print("Crossover operated")
        print(ind1, ind2)
    else:
        print("Crossover failed - Unequal type")
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
        if ind.type == "tf":
            if ind[0] == MAX_TIME_HORIZON: #we can only mutate lower
                ind[0] -= 1
            elif ind[0] == MIN_TIME_HORIZON: #we can only mutate higher
                ind[0] += 1
            else: 
                mutate_both_ways(ind) # we can mutate lower or higher
        if ind.type == "vi":
            if ind[0] == MAX_VALUATION_VI: #we can only mutate lower
                ind[0] -= 1
            elif ind[0] == MIN_VALUATION_VI: #we can only mutate higher
                ind[0] += 1
            else: 
                mutate_both_ways(ind) # we can mutate lower or higher
        if ind.type == "nt":
            if ind[0] == MAX_VALUATION_NT: #we can only mutate lower
                ind[0] -= 1
            elif ind[0] == MIN_VALUATION_NT: #we can only mutate higher
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

def strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    # Selection
    if PROBA_SELECTION == 1:
        offspring = toolbox.select(pop, POPULATION_SIZE, TOURNAMENT_SIZE)
        # fitness_for_invalid(offspring)
        offspring = list(map(toolbox.clone, offspring))
                                        
    # Crossover
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        toolbox.mate(child1,child2,CROSSOVER_RATE)
        del child1.fitness.values
        del child2.fitness.values

    # Mutation
    for mutant in offspring:
        toolbox.mutate(mutant, MUTATION_RATE)
        del mutant.fitness.values

    # Recomputing fitness
    # fitness_for_invalid(offspring)

    # Replacing
    pop[:] = offspring
    # fitnessValues = [ind.fitness.values[0] for ind in pop]

    return pop