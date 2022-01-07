import run
import line_profiler
profile = line_profiler.LineProfiler()
import numpy as np
np.random.seed(9)

@profile
def simulation(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates,):
    df, pop = run.run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, False, False)
    return df, pop

# simulation(100,0,1000,[1/3, 1/3, 1/3])

''' In command: kernprof -v -l evology/code/profile.py > profile.txt ; no need to be in python env first'''