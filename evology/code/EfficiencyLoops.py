#!/usr/bin/env python3
import creation as cr
import timeit
import numpy as np

wealth_coordinates = [1/3, 1/3, 1/3]
POP_SIZE = 1_000_000
current_price = 100

create_pop = cr.generate_creation_func(wealth_coordinates)
pop = create_pop('between', POP_SIZE)

def standard_wealth_update(pop, current_price):
    for ind in pop:
        ind.prev_wealth = ind.wealth
        ind.wealth = ind.cash + ind.asset * current_price - ind.loan
    return ind


starttime = timeit.default_timer()
standard_wealth_update(pop, current_price)
print("std wealth update :", timeit.default_timer() - starttime)

def wealth_update2(pop, current_price):
    for ind in pop:
        update2(ind, current_price)
    return pop

def update2(ind, current_price):
    ind.prev_wealth = ind.wealth
    ind.wealth = ind.cash + ind.asset * current_price - ind.loan
    return ind

starttime = timeit.default_timer()
pop = wealth_update2(pop, current_price)
print(" wealth update2 :", timeit.default_timer() - starttime)


def np_update_wealth(array, current_price):
    for i in range(len(array)):
        array[i, 10] = array[i,9] * current_price + array[i,11]
    return array 

np_bs = np.random.rand(POP_SIZE,40)
starttime = timeit.default_timer()
pop = np_update_wealth(np_bs, current_price)
print(" wealth np :", timeit.default_timer() - starttime)


def np_update_wealth2(array, current_price):
    array[:, 10] = array[:, 9] * current_price + array[:, 11]


np_bs = np.random.rand(POP_SIZE,40)
starttime = timeit.default_timer()
pop = np_update_wealth2(np_bs, current_price)
print(" wealth np 2:", timeit.default_timer() - starttime)