def calculate_wealth(pop, price):
    for ind in pop:
        ind.wealth = ind.cash + ind.asset * price - ind.loan
    return ind
