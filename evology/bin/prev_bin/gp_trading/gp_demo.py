import operator
import math
import numpy as np
from deap import algorithms
from deap.algorithms import varAnd
from deap import base
from deap import creator
from deap import tools
from deap import gp
import warnings
import scipy
from math import isnan
import sys
sys.path.append('/Users/aymericvie/Documents/GitHub/evology/evology/code')
from main import main as evology

# Adding some new packages for results visualisation
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout # This is essential import, not nx.nx_agraph.

# Define new functions
def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1



pset = gp.PrimitiveSet("MAIN", 14)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 2)
pset.addPrimitive(operator.neg, 1)
# pset.addPrimitive(math.cos, 1)
# pset.addPrimitive(math.sin, 1)
# pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))
pset.renameArguments(ARG0='p1')
pset.renameArguments(ARG1='p2')
pset.renameArguments(ARG2='p3')
pset.renameArguments(ARG3='p4')
pset.renameArguments(ARG4='p5')
pset.renameArguments(ARG5='p6')
pset.renameArguments(ARG6='p7')
pset.renameArguments(ARG7='p8')
pset.renameArguments(ARG8='p9')
pset.renameArguments(ARG9='p10')
pset.renameArguments(ARG10='d')
pset.renameArguments(ARG11='v')
pset.renameArguments(ARG12='g')
pset.renameArguments(ARG13='r')
''' (p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, d, v, g, r) '''

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def main_eval(func):
    # takes a trading function and evaluates it
    fitness = 0
    for _ in range(1): # Number of repetitions of the evology simulation
        df, pop, = evology(func, 'extended', [1/3, 1/3, 1/3], 100, 252 * 5, np.random.seed(), True, False)
        # fitness += np.nanmean(df["AV_return"])
        df["AV_return_1"] = df["AV_return"].add(1)
        fitness = ((scipy.stats.gmean(df["AV_return_1"])) - 1) / df["AV_return"].std()
        if isnan(fitness) == True:
            print(fitness)
            print(df["AV_return"])
            print(df["AV_return_1"])
            print(df["AV_return"].std())
            for i, item in enumerate(df["AV_return_1"]):
                if item < 0:
                    print([i, item])
                    break
                if isnan(item) == True:
                    print([i, item])
                    print(df["AV_return"].iloc[i])
                    break
                if item == 0:
                    print([i, item])
                    print(np.log(item))
                    break
                    
            raise ValueError('Nan fitness')
        if df["AV_WShare"].iloc[0] >= 10:
            warnings.warn('AV wshare above 10%')
    return fitness 

def evalSymbReg(individual):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # fsum = func(p1, p2, p3)
    fsum = main_eval(func)
    return fsum, #math.fsum(sqerrors) / len(points),

toolbox.register("evaluate", evalSymbReg)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=4)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=5)) #max_value is max depth (+1 for a terminal)
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=5))

def round_mean(x):
    return round(np.mean(x), 2)
def round_std(x):
    return round(np.std(x), 2)
def round_min(x):
    return round(np.min(x), 2)
def round_max(x):
    return round(np.max(x), 2)

def main():
    # https://github.com/DEAP/deap/blob/eba726cf2ee64acba221213ccacaa74f63cfd174/deap/algorithms.py
    np.random.seed(8)

    population = toolbox.population(n=50)
    halloffame = tools.HallOfFame(1)
    verbose = True
    ngen = 50
    cxpb = 0.5
    mutpb = 0.05

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", round_mean)
    mstats.register("std", round_std)
    mstats.register("min", round_min)
    mstats.register("max", round_max)

            # pop, log = algorithms.eaSimple(pop, toolbox, 0.8, 0.1, 20, stats=mstats,
            #                                halloffame=hof, verbose=True)
    # print log
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (mstats.fields if mstats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = mstats.compile(population) if mstats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print (logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Vary the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)
            print(halloffame[0])

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = mstats.compile(population) if mstats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print (logbook.stream)

    return population, logbook, halloffame
    # return pop, log, hof

if __name__ == "__main__":
    pop, log, hof = main()

    # Show fitness curve
    gen = log.select("gen")
    fit_mins = log.chapters["fitness"].select("min")
    fit_max = log.chapters["fitness"].select("max")
    fit_avg = log.chapters["fitness"].select("avg")
    size_avgs = log.chapters["size"].select("avg")
    fig, ax1 = plt.subplots()
    line1 = ax1.plot(gen, fit_max, "b-", label="Maximum Fitness")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Fitness", color="b")
    for tl in ax1.get_yticklabels():
        tl.set_color("b")
    ax2 = ax1.twinx()
    line2 = ax2.plot(gen, size_avgs, "r-", label="Average Size")
    ax2.set_ylabel("Size", color="r")
    for tl in ax2.get_yticklabels():
        tl.set_color("r")
    lns = line1 + line2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="center right")
    plt.savefig('fitness_size.png', dpi=300)
    plt.show()

    # Show best function
    bests = tools.selBest(pop, k=1)
    print(bests[0])
    
    nodes, edges, labels = gp.graph(hof[0])
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    pos = graphviz_layout(graph, prog = 'dot') # prog="twopi")  # run dot -c in conda prompt #"dot"
    plt.figure(figsize=(7, 7))
    nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="skyblue", node_shape='o', edgecolors='black')
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, labels)
    plt.axis("off")
    plt.savefig('best_strategy.png', dpi=300)
    plt.show()