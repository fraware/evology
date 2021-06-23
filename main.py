import random
import seaborn as sns
# sns.set_theme(style="darkgrid")
import matplotlib.pyplot as plt
import numpy as np
import genetic_algorithm_functions as ga
import market 
import market_clearing_leap as mc_leap
import parameters
import data
import brownian_motion as bm

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
share_increment = parameters.share_increment
short_bound = parameters.short_bound


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
    extended_price_history = bm.generate_bm_series(MAX_TIME_HORIZON)
    plt.plot(extended_price_history)
    plt.show()
    generation_history = []
    mismatch_history = []
    asset_count_history = []
    mean_theta = []
    size_pos_pos = []
    size_neg_pos = []
    
    assetQ = market.count_assets(pop)
    
    # Temp
    agent0_profit = []
    agent0_ema = []
    dividend = INITIAL_DIVIDEND
    
    print("Initial population")
    print(('{}\n'*len(pop)).format(*pop))
    print("Agent representation")
    print("[Theta Wealth Cash Asset Loan TradingSignal RawExcessDemand     Profit     EMA profit   Margin]")
    print("[ 0       1     2    3     4         5             6           7            8              9]")
    
    fitnessValues = list(map(ga.toolbox.evaluate, pop))
    for individual, fitnessValue in zip(pop, fitnessValues):
        individual.fitness.values = fitnessValue
    fitnessValues = [individual.fitness.values[0] for individual in pop]
    
    maxFitness = max(fitnessValues)
    meanFitness = sum(fitnessValues) / len(pop)
    maxFitnessValues.append(maxFitness)
    meanFitnessValues.append(meanFitness)
    agent0_profit.append(pop[0][7])
    agent0_ema.append(pop[0][8])
    
    while generationCounter < MAX_GENERATIONS:
        print("----------------------------------------------------------------------")
        print("Generation " + str(generationCounter))
        # print(('{}\n'*len(pop)).format(*pop))
        
        ''' A) Draw dividends '''       
        DIVIDEND_GROWTH_RATE = market.determine_dividend_growth(DIVIDEND_GROWTH_RATE_G)
        dividend, random_dividend = market.draw_dividend(DIVIDEND_GROWTH_RATE)
        dividend_history.append(dividend)
        print("dividend is " + str(dividend))
        random_dividend_history.append(random_dividend)
        
        ''' B) Apply dividends, interest rate and reinvestment, update profit '''
        # market.wealth_earnings(pop, dividend)
        
        ''' C) Update wealth and margin as a function of price '''
        market.update_wealth(pop, price) 
        market.update_margin(pop, price)
        
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
        
        # print("After fitness, dividends, wealth, hypermuation updates")
        # print(('{}\n'*len(pop)).format(*pop))
        
        '''  F) GA evolution of strategies with last period fitness  '''

        # Selection
        if selection_proba == 1:
            offspring = ga.toolbox.select(pop, POPULATION_SIZE, TOURNAMENT_SIZE)
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
        # print(extended_price_history)
        market.update_trading_signal(pop, extended_price_history)
        
        ''' H) Deduce excess demand and create an order book of ED functions of price''' 

        market.update_excess_demand(pop)
        list_excess_demand_func = market.order_excess_demand(pop)
        ''' list_excess_demand_func is now the list of ED functions '''
        # aggregate_ed = market.compute_aggregate_excess_demand(pop)
        aggregate_ed = market.compute_aggregate_excess_demand(pop, list_excess_demand_func)
        
        # print("After trading signal, GA, ED update, right before clearing")
        # print(('{}\n'*len(pop)).format(*pop))

        ''' I) Clear the market with the aggregate ED, obtain the new price ''' 
        
        price = mc_leap.leap_solver(pop, price)
        # price = mc_leap.solver_linear_shortcut(pop, price)
        print("Price is " + str(price))
        
        # testing block
        
        # sum_ag = 0
        # for i in range(POPULATION_SIZE):
        #     sum_ag += list_excess_demand_func[i](price)
        #     print("Agent " + str(i) + " ED(pt+1) is " + str(list_excess_demand_func[i](price)))
        # print("Sum AG " + str(sum_ag))
        extended_price_history = np.append(extended_price_history, price)
        price_history.append(price)
        
        ''' J) Update inventories ''' 
        market.update_inventory(pop, price, assetQ,share_increment, short_bound)
        
        ''' K) Record results '''
        maxFitness = max(fitnessValues)
        meanFitness = sum(fitnessValues) / len(pop)
        maxFitnessValues.append(maxFitness)
        meanFitnessValues.append(meanFitness)
        replacements.append(round_replacements)
        asset_count_history.append(market.count_assets(pop))
        mean_theta.append(data.theta_stats(pop))
                
        size_pos_pos.append(market.count_assets(pop))
        size_neg_pos.append(market.count_size_short(pop))
        
        # print("agg_price before mismatch")
        # print(aggregate_ed(price))
        # print(abs(market.truncate(aggregate_ed(price),3)))
        mismatch_history.append(abs(market.truncate(aggregate_ed(price),3)))
                # Temp
        agent0_profit.append(pop[0][7])
        agent0_ema.append(pop[0][8])
        #  Could this print results be automated? We have it twice
        
        print("- Generation {}: Max Fitness = {}, Avg Fitness = {}".format(generationCounter, maxFitness, meanFitness))
        generation_history.append(generationCounter)
        generationCounter += 1
                
        # Temporary function to apply some fixed cost
        # if generationCounter > 0:
        #     for ind in pop:
        #         ind[1] -= 1

        df = data.generate_df(generation_history, price_history, mismatch_history, mean_theta, asset_count_history, 
                              dividend_history, random_dividend_history, replacements,
                              size_pos_pos, size_neg_pos)
    # return 
    
    # return price, initial_pop, pop, maxFitnessValues, meanFitnessValues, replacements, agent0_profit, agent0_ema, dividend_history, price_history, random_dividend_history, list_excess_demand_func, aggregate_ed, df
    print(('{}\n'*len(pop)).format(*pop))
    return df, extended_price_history