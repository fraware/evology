import matplotlib.pyplot as plt
import main
import parameters


MAX_GENERATIONS = parameters.MAX_GENERATIONS
RANDOM_SEED = parameters.RANDOM_SEED

# Optional because they are arguments to main
CROSSOVER_RATE = parameters.CROSSOVER_RATE
MUTATION_RATE = parameters.MUTATION_RATE 
PROBA_SELECTION = parameters.PROBA_SELECTION

# price, initial_pop, pop, maxFitnessValues, meanFitnessValues, replacements, agent0_profit, agent0_ema, dividend_history, price_history, random_dividend_history, list_excess_demand_func, aggregate_ed, df = main.main(PROBA_SELECTION, CROSSOVER_RATE, MUTATION_RATE)
df, extended_price_history, pop_ex = main.main("extended", PROBA_SELECTION, CROSSOVER_RATE, MUTATION_RATE)

print(df)
print("--------------------------")

df.plot(x="Gen", y = ["Price"],
        kind="line", figsize=(15, 6))
plt.show()

df.plot(x="Gen", y = ["LogP"],
        kind="line", figsize=(15, 6))
plt.show()

df.plot(x="Gen", y = ["MeanT"],
        kind="line", figsize=(15, 6))
plt.show()

plt.plot(extended_price_history)
plt.show()


print("-----------------------")


print(('{}\n'*len(pop_ex)).format(*pop_ex))
print(type(pop_ex))
print(type(pop_ex[0]))

pop = pop_ex.copy()
del pop[0]
print(('{}\n'*len(pop)).format(*pop))
print("Deleting is succesful")

import genetic_algorithm_functions as ga
pop = pop_ex.copy()
del pop[0]
add = ga.toolbox.generate_hyper_tf_individual()
print(add)
pop.append(add)
print(('{}\n'*len(pop)).format(*pop))
print(type(pop_ex[3]))
print("Deleting and adding a new DEAP individual is succesful")
