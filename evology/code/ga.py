from math import nan
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from operator import attrgetter
from creation import *
import balance_sheet as bs
import timeit
import warnings

'''
def adjust_mode(pop, mode):
    if mode == "between":
        for ind in pop:
            if ind.type == "tf":
                ind[0] = 2
            if ind.type == "vi":
                ind[0] = 100
            if ind.type == "nt":
                ind[0] = 100
    return pop'''

def hypermutate(pop, mode, asset_supply, current_price, generation, spoils, wealth_coordinates):

    starttime = timeit.default_timer()
    round_replacements = 0
    ''' 
    hyperm = False

    if hyperm == True:
        for i in range(0, len(pop)):
            
            if pop[i].wealth < 0:
                warnings.warn("Replacing // Gen " + str(generation) + " // Type: " + str(pop[i].type) + ", C: " + str(int(pop[i].cash)) + ", S+: " + str(int(pop[i].asset)) + ", L: " + str(int(pop[i].loan)) + ", M: " + str(int(pop[i].margin)) + ", W: " + str(int(pop[i].wealth)))
                spoils += pop[i].asset
                pop[i] = toolbox.gen_rd_ind(wealth_coordinates)
                pop[i].cash = 50_000_000
                pop[i].wealth = pop[i].cash + pop[i].asset * current_price - pop[i].loan
                pop[i].MonWealth = np.zeros((1, 21))[0]
                pop[i].prev_wealth = 0
                del pop[i].fitness.values
                round_replacements += 1
        
        if mode == "between":
            pop = adjust_mode(pop, mode)

    if hyperm == False:
        replaced = False
        ReplacedCount = 0
        for ind in pop:
            if ind.wealth < 0:
                ReplacedCount += 1
                replaced = True
                ind.loan -= 2 * abs(ind.wealth)
                ind.wealth = ind.cash + ind.asset * current_price - ind.loan
                    
        if replaced == True:
            print('Bailed out today (' + str(ReplacedCount) + ').')

    '''
    timeB = timeit.default_timer() - starttime
    return pop, round_replacements, spoils, timeB

def compute_fitness(pop):
    for ind in pop:
        
        ema = (2 / (EMA_HORIZON + 1)) * (ind.profit - ind.ema) + ind.ema
        ind.ema = ema
        ind.fitness.values = ema,
    return ind

# Creating our own crossover operator:
def feasible_crossover(ind1,ind2,CROSSOVER_RATE):
    if ind1.type == ind2.type:
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
    global number
    if low >= 0 and high >= 0:
        number = float(random.randint(round(low*1000),round(high*1000))/1000)
    if low < 0 and high < 0:
        number = - float(random.randint(round(-low*1000),round(-high*1000))/1000)
    return number


def selRandom(individuals, k):
    return [random.choice(individuals) for i in range(k)]

def strategy_evolution(mode, pop, PROBA_SELECTION, MUTATION_RATE, wealth_coordinates):
    
    if mode == 'between':
        # Individuals can select & imitate, and switch

        # Selection
        for i in range(len(pop)):
            if random.random() < PROBA_SELECTION: # Social learning
                # Create the tournament and get the winner
                aspirants = selRandom(pop, TOURNAMENT_SIZE-1) 
                aspirants.append(pop[i])
                winner = max(aspirants, key=attrgetter("fitness"))

                # Imitate the winner's type and strategy
                pop[i].type = winner.type
                pop[i][0] = winner[0]
        
        # Mutation
        types = ['nt', 'vi', 'tf']
        cum_proba = [0, 0, 0]
        cum_proba[0] = wealth_coordinates[0]
        i = 1
        while i < len(wealth_coordinates):
            cum_proba[i] = cum_proba[i-1] + wealth_coordinates[i]
            if cum_proba[i] > 1.0001:
                raise ValueError('Cum proba > 1 ' + str(cum_proba))
            i += 1
        if sum(cum_proba) == 0:
            raise ValueError('Sum cumproba = 0')

        for i in range(len(pop)):
            if random.random() < MUTATION_RATE:
                # Change type totally randomly 
                n = random.random()
                ty = 0
                while cum_proba[ty] < n:
                    ty += 1
                pop[i].type = types[ty]
                if pop[i].type =='tf':
                    pop[i][0] = 2
                elif pop[i].type == 'nt' or pop[i].type == 'vi':
                    pop[i][0] = 100
    return pop