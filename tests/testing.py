import sys
sys.path.append('./evology/code/')
from main import *
import random
random.seed = random.random()

df = main("between", 10, 0, 5, 0, 0)
print(df)

# main(mode, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, CROSSOVER_RATE, MUTATION_RATE):

def runs(repetitions, time):

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

# def testing(repetitions, time):
#     went_smoothly = test_runs(repetitions, time)
#     assert went_smoothly == True


def test_runs():
    assert runs(1,10) == True

