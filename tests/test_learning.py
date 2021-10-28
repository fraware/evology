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
            df = main("between", time, PROBA_SELECTION, agents, 0, MUTATION_RATE)
        except Exception as e: 
            went_smoothly = False
            print('Failure on regular run')
            print(str(e))
            break
        i += 1
    return went_smoothly

def test_nolearning(repetitions, time, agents):
    went_smoothly = learning_runs(repetitions, time, agents)
    assert went_smoothly == True

test_nolearning(10, 50, 4)