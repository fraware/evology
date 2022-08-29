import sys
sys.path.append('./evology/code')
import numpy as np
from main import main as model
import multiprocessing as mp

np.random.seed()

# # TODO: add a determinism test as well?

def random_bool():
    n = np.random.random()
    if n <= 0.5:
        return True
    else:
        return False 

def job1(param):
    went_smoothly = True
    time, agents = 1000, 3
    try: 
        seed = np.random.randint(0,100000)
        wealth_coords = np.random.dirichlet(np.ones(3), size=1)[0].tolist()
        np.random.seed(seed)
        inv_bool = random_bool()
        df = model(time, agents, wealth_coords, 0.01, inv_bool, seed)
    except Exception as e: 
        went_smoothly = False
        print('Investment Bool ' + str(inv_bool))
        print('Seed ' + str(seed))
        print('Coords ' + str(wealth_coords))
        print(str(e))
        went_smoothly = False
    assert went_smoothly == True
        
def job2(param):
    went_smoothly = True
    time, agents = 100000, 10
    try: 
        seed = np.random.randint(0,100000)
        wealth_coords = np.random.dirichlet(np.ones(3), size=1)[0].tolist()
        np.random.seed(seed)
        inv_bool = random_bool()
        df = model(time, agents, wealth_coords, 0.01, inv_bool, seed)
    except Exception as e: 
        went_smoothly = False
        print('Investment Bool ' + str(inv_bool))
        print('Seed ' + str(seed))
        print('Coords ' + str(wealth_coords))
        print(str(e))
        went_smoothly = False
    assert went_smoothly == True
    


# Run experiment
def main():
    repetitions1, repetitions2 = 30, 5
    p = mp.Pool()
    p.map(job1, list(range(repetitions1)))
    p.map(job2, list(range(repetitions2)))
    p.close()


if __name__ == "__main__":
    data = main()