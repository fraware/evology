#!/usr/bin/env python

import sys
print(sys.version)
sys.path.append('./evology/code/')
from main import *
import random
random.seed = random.random()
from parameters import *

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def learning_runs(repetitions, time, agents):

    went_smoothly = True
    i = 0
    while i < repetitions:
        try: 
            df = main("between", time, PROBA_SELECTION, agents, 0, MUTATION_RATE, False)
            # print('Process ' + str(i) + ' ran succesfully.')
        except Exception as e: 
            went_smoothly = False
            print('Process ' + str(i) + ' encoutered an exception.')
            print(str(e))
            break
        i += 1
    return went_smoothly

def test_learning(repetitions, time, agents):
    went_smoothly = learning_runs(repetitions, time, agents)
    assert went_smoothly == True

print('Testing for 3 agents, 100 periods with 3 repetitions...')
test_learning(3, 100, 3)
print('...Succesful!')
print('Testing for 4 agents, 10,000 periods with 5 repetitions...')
test_learning(5, 10000, 4)
print('...Succesful!')
print('Testing for 50 agents, 10,000 periods with 5 repetitions...')
test_learning(5, 10000, 50)
print('...Succesful!')
print('Testing for 100 agents, 50,000 periods with 5 repetitions...')
test_learning(5, 50000, 100)
print('...Succesful!')
print('Testing for 100 agents, 100,000 periods with 1 repetition...')
test_learning(5, 100000, 100)
print('...Succesful!')