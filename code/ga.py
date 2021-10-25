from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from operator import attrgetter
from sampling import *

def hyper_correct_ind(ind):
    ind.asset_long = 0
    ind.asset_short = 0
    ind.loan = 0
    ind.cash = 100_000_000
    return ind

def hypermutate(pop, mode):
    round_replacements = 0
    spoils = 0
    pop_temp = list(map(toolbox.clone, pop))
    for i in range(0, len(pop_temp)):
        if pop_temp[i].wealth <= 0:
            print("Info on replacement")
            print("Type: " + str(pop_temp[i].type) + ", C: " + str(int(pop_temp[i].cash)) + ", S+: " + str(int(pop_temp[i].asset_long)) + ", S-: " + str(int(pop_temp[i].asset_short)) + ", L: " + str(int(pop_temp[i].loan)) + ", M: " + str(int(pop_temp[i].margin)) + ", W: " + str(int(pop_temp[i].wealth)))
            spoils += pop_temp[i].asset_long
            pop_temp[i] = toolbox.gen_rd_ind()
            pop_temp[i] = hyper_correct_ind(pop_temp[i])
            del pop_temp[i].fitness.values
            
           
            round_replacements += 1
            
    pop[:] = pop_temp
    if mode == "between":
        pop = adjust_mode(pop, mode)
    return pop, round_replacements, spoils

def compute_fitness(pop):
    for ind in pop:
        ind.profit = ind.wealth - ind.prev_wealth
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

# Creation of our customised selection operator (outnrament) that handles positive & negative fitness values
def selTournament(pop, k, tournsize, fit_attr="fitness"):
    chosen = []
    for i in range(k):
        chosen_i = []
        aspirants = selRandom(pop, tournsize-1) 
        aspirants.append(pop[i])
        chosen_i = max(aspirants, key=attrgetter(fit_attr))

        # print('chosen i asset precondserved '+str(chosen_i.asset))
        # print('pop i asset ' + str(pop[i].asset))

        # Conserve most variables
        chosen_i.asset = pop[i].asset
        chosen_i.wealth = pop[i].asset
        chosen_i.process = pop[i].process
        chosen_i.tsf = pop[i].tsf
        chosen_i.edf = pop[i].edf
        chosen_i.edv = pop[i].edv
        chosen_i.tsv = pop[i].tsv
        chosen_i.loan = pop[i].loan
        chosen_i.cash = pop[i].cash
        chosen_i.margin = pop[i].margin
        chosen_i.margin = pop[i].margin
        chosen_i.ema = pop[i].ema
        chosen_i.profit = pop[i].profit

        # print('chosen i type '+str(chosen_i.type))
        # print('pop i type ' + str(pop[i].type))

        # print('chosen i asset '+str(chosen_i.asset))
        # print('pop i asset ' + str(pop[i].asset))

        # print('chosen i edv '+str(chosen_i.edv))
        # print('pop i edv ' + str(pop[i].edv))

        # print('chosen i strat '+str(chosen_i[0]))
        # print('pop i strat ' + str(pop[i][0]))
        # print('-----')

        # Imitate type and strategy
        # chosen_i[0] = max(aspirants, key=attrgetter(fit_attr))[0]
        # chosen_i.type = max(aspirants, key=attrgetter(fit_attr))[0].type

        # Append to list of selected individuals
        chosen.append(chosen_i)
    return chosen

toolbox.register("selTournament", selTournament)
toolbox.register("select", toolbox.selTournament)

def strategy_evolution(mode, pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):
    
    if mode == 'between':
        # Individuals can select & imitate, and switch

        # Selection
        if PROBA_SELECTION == 1:
            offspring = toolbox.select(pop, POPULATION_SIZE, TOURNAMENT_SIZE)
            offspring = list(map(toolbox.clone, offspring))
        if PROBA_SELECTION == 0:
            offspring = pop.copy()
    
    else: 
        # TODO: under development for when we have within mode
        # Selection
        if PROBA_SELECTION == 1:
            offspring = toolbox.select(pop, POPULATION_SIZE, TOURNAMENT_SIZE)
            # fitness_for_invalid(offspring)
            offspring = list(map(toolbox.clone, offspring))
        if PROBA_SELECTION == 0:
            offspring = pop.copy()
                                            
        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            toolbox.mate(child1,child2,CROSSOVER_RATE)

        # Mutation
        for mutant in offspring:
            toolbox.mutate(mutant, MUTATION_RATE)

    # Replace pop by offspring
    pop[:] = offspring

    return pop