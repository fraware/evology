from parameters import *
from sampling import *
import sampling
from balance_sheet import *
from brownian_motion import *
from market_clearing import *
from ga import *


def main(MAX_GENERATIONS):
    
    # maxFitnessValues, meanFitnessValues, replacements, , price_history = [],[],[],[],[],[]   
    # , mismatch_history, asset_count_history, mean_theta, mean_wealth, size_pos_pos, size_neg_pos = [],[],[],[],[],[], []

    dividend_history, random_dividend_history, generation_history = [], [], []
    price = INITIAL_PRICE
    extended_price_history = generate_bm_series(MAX_TIME_HORIZON+1)
    extended_price_history = [abs(x) for x in extended_price_history]
    dividend = INITIAL_DIVIDEND
    generation = 0
    pop = sampling.toolbox.gen_rd_pop(n=POPULATION_SIZE) # Initialise market, population
    print(pop)
    for ind in pop:
        print(ind.type)
    asset_supply = count_assets(pop)

    calculate_wealth(pop, price)

    while generation < MAX_GENERATIONS:
        print("----------------------------------------------------------------------")
        print("Generation " + str(generation))

        calculate_ts_edf(pop, extended_price_history) # Compute TSV and EDF
        price = leap_solver(pop, price) # Clear the market
        print("Price is " + str(price))
        calculate_edv(pop, price) # Compute EDV

        update_margin(pop, price)
        pop, num_buy, num_sell = apply_edv(pop, asset_supply, price) # Apply EDV orders
        print("Buy orders: " + str(num_buy))
        print("Sell orders: " + str(num_sell))

        pop, dividend, random_dividend = wealth_earnings(pop, dividend, price) # Apply invest., IR, Div and compute profit
        print("Dividend is " + str(dividend))
        dividend_history.append(dividend)
        random_dividend_history.append(random_dividend)

        pop, round_replacements = hypermutate(pop) # Replace insolvent agents
        # TODO: do we need to set del ind.wealth too? Or is it fully replaced?
        print(str(round_replacements) + " replacements done")

        """ 8) Evolution block
            a. Fitness computation """

        compute_fitness(pop)

        """
            b. Adaptation
        """
        pop = strategy_evolution(pop, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE)

        # TODO: control that EDV, TS, Wealth, Profits, EMA are what they should be.

        generation_history.append(generation)
        generation += 1

main(10)