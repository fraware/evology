from main import *
from parameters import *
import random
random.seed = random.random()

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def test_runs(repetitions, time):

    went_smoothly = True

    # Model without learning
    i = 0
    while i < repetitions:
        try: 
            df = main("between", time, 0, 100, 0, 0)
        except: 
            went_smoothly = False
            print('Failure on regular run')
            break
        i += 1

    # Model with learning
    j = 0
    while j < repetitions:
        try:
            df = main("between", time, PROBA_SELECTION, 100, 0, MUTATION_RATE)
        except: 
            went_smoothly = False
            print('Failure on learning')
            break
        j += 1

    return went_smoothly

def testing(repetitions, time):
    went_smoothly = runs(repetitions, time)
    assert went_smoothly == True

testing(1,10)