#!/usr/bin/env python3

import sys
print(sys.version)
sys.path.append('./evology/code/')
from main import *
import random
import numpy as np
random.seed = random.random()
from parameters import *
import traceback

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def learning_runs(repetitions, time, agents):
    went_smoothly = True
    i = 0
    while i < repetitions:
        wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
        print(wealth_coordinates)
        try: 
            df,pop = main("between", 'scholl', time, PROBA_SELECTION, agents, MUTATION_RATE, wealth_coordinates, tqdm_display=True, reset_wealth = False)

            # print('Process ' + str(i) + ' ran succesfully.')
        except Exception as e: 
            went_smoothly = False
            print('Process ' + str(i) + ' encoutered an exception.')
            print(str(e))
            traceback.print_exc()
            break
        i += 1
    return went_smoothly

def test_learning(repetitions, time, agents):
    went_smoothly = learning_runs(repetitions, time, agents)
    assert went_smoothly == True

def learning_runs_reset(repetitions, time, agents):
    went_smoothly = True
    i = 0
    while i < repetitions:
        wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
        print(wealth_coordinates)
        try: 
            df,pop = main("between", 'scholl', time, PROBA_SELECTION, agents, MUTATION_RATE, wealth_coordinates, tqdm_display=True, reset_wealth = True)

            # print('Process ' + str(i) + ' ran succesfully.')
        except Exception as e: 
            went_smoothly = False
            print('Process ' + str(i) + ' encoutered an exception.')
            print(str(e))
            traceback.print_exc()
            break
        i += 1
    return went_smoothly

def test_learning_reset(repetitions, time, agents):
    went_smoothly = learning_runs_reset(repetitions, time, agents)
    assert went_smoothly == True

def nolearning_runs(repetitions, time, agents):

    went_smoothly = True
    i = 0
    while i < repetitions:
        try: 
            wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
            print(wealth_coordinates)
            df,pop = main("static", 'scholl', time, 0, agents, 0, wealth_coordinates, tqdm_display=True, reset_wealth = False)

            # print('Process ' + str(i) + ' ran succesfully.')
        except Exception as e: 
            went_smoothly = False
            print('Process ' + str(i) + ' encoutered an exception.')
            print(str(e))
            traceback.print_exc()
            break
        i += 1
    return went_smoothly


def test_nolearning(repetitions, time, agents):
    went_smoothly = nolearning_runs(repetitions, time, agents)
    assert went_smoothly == True


def nolearning_runs_reset(repetitions, time, agents):

    went_smoothly = True
    i = 0
    while i < repetitions:
        try: 
            wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()
            print(wealth_coordinates)
            df,pop = main("static", 'scholl', time, 0, agents, 0, wealth_coordinates, tqdm_display=True, reset_wealth = True)

            # print('Process ' + str(i) + ' ran succesfully.')
        except Exception as e: 
            went_smoothly = False
            print('Process ' + str(i) + ' encoutered an exception.')
            print(str(e))
            traceback.print_exc()
            break
        i += 1
    return went_smoothly


def test_nolearning_reset(repetitions, time, agents):
    went_smoothly = nolearning_runs_reset(repetitions, time, agents)
    assert went_smoothly == True