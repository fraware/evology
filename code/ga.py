from math import nan
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from operator import attrgetter
from sampling import *
import balance_sheet as bs

''' old hypermutate that we adjust for speed below '''
# def hypermutate(pop, mode, asset_supply):
#     round_replacements = 0
#     spoils = 0
#     pop_temp = list(map(toolbox.clone, pop))
#     for i in range(0, len(pop_temp)):
#         if pop_temp[i].wealth <= 0:
#             # print("Info on replacement")
#             # print("Type: " + str(pop_temp[i].type) + ", C: " + str(int(pop_temp[i].cash)) + ", S+: " + str(int(pop_temp[i].asset)) + ", L: " + str(int(pop_temp[i].loan)) + ", M: " + str(int(pop_temp[i].margin)) + ", W: " + str(int(pop_temp[i].wealth)))
#             spoils += pop_temp[i].asset
#             pop_temp[i] = toolbox.gen_rd_ind()
#             pop_temp[i] = hyper_correct_ind(pop_temp[i])
#             pop_temp[i].asset = 0
#             del pop_temp[i].fitness.values
            
#             # print('REPLACED')
#             round_replacements += 1
            
#     pop[:] = pop_temp
#     if mode == "between":
#         pop = adjust_mode(pop, mode)
#     return pop, round_replacements, spoils

def hypermutate(pop, mode, asset_supply):
    round_replacements = 0
    spoils = 0

    
    for i in range(0, len(pop)):
        if pop[i].wealth <= 0:
            # print("Info on replacement")
            # print("Type: " + str(pop_temp[i].type) + ", C: " + str(int(pop_temp[i].cash)) + ", S+: " + str(int(pop_temp[i].asset)) + ", L: " + str(int(pop_temp[i].loan)) + ", M: " + str(int(pop_temp[i].margin)) + ", W: " + str(int(pop_temp[i].wealth)))
            spoils += pop[i].asset
            pop[i] = toolbox.gen_rd_ind()
            pop[i].asset = 0
            del pop[i].fitness.values
            round_replacements += 1

    if abs(spoils) > 0:
        per_ind_spoil = spoils / len(pop)
        for ind in pop:
            ind.asset += per_ind_spoil

            
    if mode == "between":
        pop = adjust_mode(pop, mode)
    return pop, round_replacements

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
    # number = float(random.randint(low*1000, high*1000))/1000
    global number
    if low >= 0 and high >= 0:
        number = float(random.randint(round(low*1000),round(high*1000))/1000)
    if low < 0 and high < 0:
        number = - float(random.randint(round(-low*1000),round(-high*1000))/1000)
    return number


def selRandom(individuals, k):
    return [random.choice(individuals) for i in range(k)]

# # Creation of our customised selection operator (outnrament) that handles positive & negative fitness values
# def selTournament(pop, tournsize, fit_attr="fitness"):
#     chosen = []
#     for i in range(len(pop)):
#         popi_assets = pop[i].asset
#         # print('popi')
#         # print(popi_assets)

#         # print('-----')
#         # print(i)
#         # print('pop[i] asset ' + str(i) + ', ' +str(pop[i].type) + ', ' + str(pop[i].asset))

#         # chosen_i = []
#         aspirants = selRandom(pop, tournsize-1) 
#         aspirants.append(pop[i])
#         chosen_i = max(aspirants, key=attrgetter(fit_attr))

#         # print(type(pop[i]))
#         # print(type(chosen_i))

#         # print('chosen i asset precondserved '+str(chosen_i.asset))
#         # print('pop i asset ' + str(pop[i].asset))

#         # Conserve most variables
#         # print(chosen_i.asset)
        
#         chosen_i.asset = pop[i].asset
#         chosen_i.asset = popi_assets

#         # print(chosen_i.asset)

#         chosen_i.wealth = pop[i].asset
#         chosen_i.process = pop[i].process
#         chosen_i.tsf = pop[i].tsf
#         chosen_i.edf = pop[i].edf
#         chosen_i.edv = pop[i].edv
#         chosen_i.tsv = pop[i].tsv
#         chosen_i.loan = pop[i].loan
#         chosen_i.cash = pop[i].cash
#         chosen_i.margin = pop[i].margin
#         chosen_i.margin = pop[i].margin
#         chosen_i.ema = pop[i].ema
#         chosen_i.profit = pop[i].profit

#         # Append to list of selected individuals
#         chosen.append(chosen_i)
#         del chosen_i
#         # print('chosen i asset ' + str(chosen_i.asset))
#     return chosen

# toolbox.register("selTournament", selTournament)
# toolbox.register("select", toolbox.selTournament)

def strategy_evolution(mode, pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    
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
        for i in range(len(pop)):
            if random.random() < MUTATION_RATE:
                # Change type totally randomly 
                ty = random.randint(0,2)
                pop[i].type = types[ty]
                if pop[i].type =='tf':
                    pop[i][0] = 2
                elif pop[i].type == 'nt' or pop[i].type == 'vi':
                    pop[i][0] = 100
    return pop