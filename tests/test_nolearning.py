#!/usr/bin/env python3

import sys
print(sys.version)
sys.path.append('./evology/code/')
from main import *
import random
random.seed = random.random()
from parameters import *

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def nolearning_runs(repetitions, time, agents):

    went_smoothly = True
    i = 0
    while i < repetitions:
        try: 
            df = main("between", time, 0, agents, 0, 0)
            print('Process ' + str(i) + ' ran succesfully.')
        except Exception as e: 
            went_smoothly = False
            print('Process ' + str(i) + ' encoutered an exception.')
            print(str(e))
            break
        i += 1
    return went_smoothly

def test_nolearning(repetitions, time, agents):
    went_smoothly = nolearning_runs(repetitions, time, agents)
    assert went_smoothly == True

test_nolearning(3, 100, 3)
test_nolearning(5, 10000, 4)
test_nolearning(5, 10000, 50)
test_nolearning(5, 50000, 100)