import random
import seaborn as sns
sns.set_theme(style="darkgrid")
import genetic_algorithm_functions as ga
import market as market
import parameters

RANDOM_SEED = parameters.RANDOM_SEED
POPULATION_SIZE = parameters.POPULATION_SIZE
MAX_TIME_HORIZON = parameters.MAX_TIME_HORIZON
MUTATION_RATE = parameters.MUTATION_RATE
MAX_GENERATIONS = parameters.MAX_GENERATIONS
CROSSOVER_RATE = parameters.CROSSOVER_RATE
MIN_WEALTH = parameters.MIN_WEALTH
MAX_WEALTH = parameters.MAX_WEALTH
MIN_TIME_HORIZON = parameters.MIN_TIME_HORIZON
INITIAL_PRICE = parameters.INITIAL_PRICE
TOURNAMENT_SIZE = parameters.TOURNAMENT_SIZE 
INITIAL_DIVIDEND = parameters.INITIAL_DIVIDEND
INTEREST_RATE = parameters.INTEREST_RATE


def main():
    random.seed(RANDOM_SEED)
    
    # Create the population and the results accumulators
    pop = ga.toolbox.population_creation(n=POPULATION_SIZE)
    initial_pop = pop.copy()
    generationCounter = 1
    price = INITIAL_PRICE
    maxFitnessValues = []
    meanFitnessValues = []
    replacements = []
    dividend_history = []
    random_dividend_history = []

    
    # Temp
    agent0_profit = []
    agent0_ema = []
    
    dividend_history.append(INITIAL_DIVIDEND)
    
    print(pop)
    
    fitnessValues = list(map(ga.toolbox.evaluate, pop))
    for individual, fitnessValue in zip(pop, fitnessValues):
        individual.fitness.values = fitnessValue
    fitnessValues = [individual.fitness.values[0] for individual in pop]
    
    maxFitness = max(fitnessValues)
    meanFitness = sum(fitnessValues) / len(pop)
    maxFitnessValues.append(maxFitness)
    meanFitnessValues.append(meanFitness)
    replacements.append(0)
    # Temp
    agent0_profit.append(pop[0][7])
    agent0_ema.append(pop[0][8])
    
    while generationCounter < MAX_GENERATIONS:
        print("--------------------------")
        print("Generation " + str(generationCounter))
        generationCounter += 1
        
        
        '''
        Here we will need to
        A) Draw dividends
        B) Apply dividends, interest rate and reinvestment
        C) Update wealth sums
        D) Hypermutation (+ update wealth?)
        
    
        @Maarten: where does the extra money from f, r, D(t) go? In the cash?
        D) I'll need to write the dividends, f, r allocation mechanism
        '''
        market.determine_dividend_growth()
        
        global dividend
        dividend, random_dividend = market.draw_dividend()
        dividend_history.append(dividend)
        random_dividend_history.append(random_dividend)
        
        market.wealth_earnings(pop)
        market.update_wealth(pop, price)
        
        
        print(pop)

        
        # Hypermutation
        global round_replacements
        round_replacements = 0
        ga.hypermutate(pop)
        # Recomputing fitness
        ga.fitness_for_invalid(pop)
        
        
        '''
        E) Update trading signals
        F) Deduce excess demand
        G) Clear the market
        H) Update inventories
        I) Update wealth
        J) Update profits
        K) Deduce fitness as EMA
        J) GA
    '''
        
        # price = market_clearing_function()
        
        market.compute_ema(pop)
        print("after ema")
        
        fitnessValues = list(map(ga.toolbox.evaluate, pop))
        for individual, fitnessValue in zip(pop, fitnessValues):
            individual.fitness.values = fitnessValue
        fitnessValues = [individual.fitness.values[0] for individual in pop]
    
        print(pop)
        print(fitnessValues)
    
    
        # Selection
        
        '''
        Need to add a probability of selection (1 or 0 is enough) to be able to model a case without any learning.
        If selection_priba is 0, offspring is just a copy of the population.
        
        We will also be needing to add these key parameters as arguments to main
        '''
        
        offspring = ga.toolbox.select(pop, POPULATION_SIZE, TOURNAMENT_SIZE)
        print("offspring")
        print(offspring)
        ga.fitness_for_invalid(offspring)
        offspring = list(map(ga.toolbox.clone, offspring))
        
        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            ga.toolbox.mate(child1,child2,CROSSOVER_RATE)
            del child1.fitness.values
            del child2.fitness.values
        
        # Mutation
        for mutant in offspring:
            ga.toolbox.mutate(mutant, MUTATION_RATE)
            del mutant.fitness.values
    
        # Recomputing fitness
        ga.fitness_for_invalid(offspring)

        # Replacing
        pop[:] = offspring
        fitnessValues = [ind.fitness.values[0] for ind in pop]
                
        
        # Print some results
        maxFitness = max(fitnessValues)
        meanFitness = sum(fitnessValues) / len(pop)
        maxFitnessValues.append(maxFitness)
        meanFitnessValues.append(meanFitness)
        replacements.append(round_replacements)
                # Temp
        agent0_profit.append(pop[0][7])
        agent0_ema.append(pop[0][8])
        #  Could this print results be automated? We have it twice
        
        print("- Generation {}: Max Fitness = {}, Avg Fitness = {}".format(generationCounter, maxFitness, meanFitness))
        
                
        # Temporary function to apply some fixed cost
        # if generationCounter > 0:
        #     for ind in pop:
        #         ind[1] -= 1

    
    return initial_pop, pop, maxFitnessValues, meanFitnessValues, replacements, agent0_profit, agent0_ema, dividend_history, random_dividend_history