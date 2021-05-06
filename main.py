import random
import seaborn as sns
sns.set_theme(style="darkgrid")
import numpy as np
import genetic_algorithm_functions as ga
import market as market
import parameters

RANDOM_SEED = parameters.RANDOM_SEED
POPULATION_SIZE = parameters.POPULATION_SIZE
MAX_TIME_HORIZON = parameters.MAX_TIME_HORIZON
# MUTATION_RATE = parameters.MUTATION_RATE
MAX_GENERATIONS = parameters.MAX_GENERATIONS
# CROSSOVER_RATE = parameters.CROSSOVER_RATE
MIN_TIME_HORIZON = parameters.MIN_TIME_HORIZON
INITIAL_PRICE = parameters.INITIAL_PRICE
TOURNAMENT_SIZE = parameters.TOURNAMENT_SIZE 
INITIAL_DIVIDEND = parameters.INITIAL_DIVIDEND
INTEREST_RATE = parameters.INTEREST_RATE
DIVIDEND_GROWTH_RATE_G = parameters.DIVIDEND_GROWTH_RATE_G


def main(selection_proba, CROSSOVER_RATE, MUTATION_RATE):
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
    price_history = []

    
    # Temp
    agent0_profit = []
    agent0_ema = []
    
    dividend = INITIAL_DIVIDEND
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
        
        
        ''' A) Draw dividends '''       
        DIVIDEND_GROWTH_RATE = market.determine_dividend_growth(DIVIDEND_GROWTH_RATE_G)
        dividend, random_dividend = market.draw_dividend(DIVIDEND_GROWTH_RATE)
        dividend_history.append(dividend)
        random_dividend_history.append(random_dividend)
        
        ''' B) Apply dividends, interest rate and reinvestment, update profit '''
        market.wealth_earnings(pop)
        
        ''' C) Update wealth sum as a function of price '''
        market.update_wealth(pop, price) 
        # print(pop)
        
        ''' D) Hypermutation operator '''
        global round_replacements
        round_replacements = 0
        ga.hypermutate(pop)
        # Recomputing fitness
        ga.fitness_for_invalid(pop)
        
        ''' E) Deduce fitness as EMA ''' 
        market.compute_ema(pop)
        fitnessValues = list(map(ga.toolbox.evaluate, pop))
        for individual, fitnessValue in zip(pop, fitnessValues):
            individual.fitness.values = fitnessValue
        fitnessValues = [individual.fitness.values[0] for individual in pop]
        #turn this into a one-line function?
        print(pop)
        # print(fitnessValues)
        
        '''  F) GA evolution of strategies with last period fitness  '''

        # Selection
        if selection_proba == 1:
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
                
        
        ''' G) Actions are now set. Update trading signals '''
        market.update_trading_signal(pop, price_history)
        
        ''' H) Deduce excess demand ''' 
        market.update_excess_demand(pop)
        
        ''' I) Clear the market ''' 
        # In progress with Maarten
        # Outputs new_price
        
        #temp
        new_price = generationCounter
        
        price_history.append(new_price)
        
        ''' J) Update inventories ''' 
        
        
        ''' K) Record results '''
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
        generationCounter += 1
                
        # Temporary function to apply some fixed cost
        # if generationCounter > 0:
        #     for ind in pop:
        #         ind[1] -= 1

    
    return initial_pop, pop, maxFitnessValues, meanFitnessValues, replacements, agent0_profit, agent0_ema, dividend_history, price_history, random_dividend_history