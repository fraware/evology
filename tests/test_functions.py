#!/usr/bin/env python

import sys
print(sys.version)
sys.path.append('./evology/code/')
from main import *
import random
import numpy as np
random.seed = random.random()
from parameters import *

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):



def learning_runs(repetitions, time, agents):

    went_smoothly = True
    i = 0
    while i < repetitions:
        try: 
            wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0]
            print(wealth_coordinates)
            df = main("between", time, PROBA_SELECTION, agents, 0, MUTATION_RATE, wealth_coordinates, True)
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

def nolearning_runs(repetitions, time, agents):

    went_smoothly = True
    i = 0
    while i < repetitions:
        try: 
            wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0]
            print(wealth_coordinates)
            df = main("between", time, 0, agents, 0, 0, wealth_coordinates, True)
            # print('Process ' + str(i) + ' ran succesfully.')
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