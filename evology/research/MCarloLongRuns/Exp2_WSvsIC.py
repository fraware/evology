# Imports 
import numpy as np
import pandas as pd
import sys
import tqdm
import warnings
import time
import ternary
from ternary.helpers import simplex_iterator
import multiprocessing as mp
warnings.simplefilter("ignore")

if sys.platform == 'darwin':
    sys.path.append('/Users/aymericvie/Documents/GitHub/evology/evology/code')
    # Need to be executed from cd to MCarloLongRuns
if sys.platform == 'linux':
    sys.path.append('/home/vie/Documents/GitHub/evology/evology/code')
from main import main as evology


startTime = time.time()
TimeHorizon = 100_000
PopulationSize = 3
obs = 10000

def job(coords):
    np.random.seed()
    try:
        df, pop = evology(
            space = "scholl",
            solver = "esl.true",
            wealth_coordinates = coords,
            POPULATION_SIZE = PopulationSize,
            MAX_GENERATIONS = TimeHorizon,
            PROBA_SELECTION = 0,
            MUTATION_RATE = 0,
            ReinvestmentRate = 1.0,
            InvestmentHorizon = 252,
            InvestorBehavior = 'profit',
            tqdm_display = True,
            reset_wealth = False
            )
        result = [
            coords[0], coords[1], coords[2],
            df['WShare_NT'].tail(obs).mean(), df['WShare_VI'].tail(obs).mean, df['WShare_TF'].tail(obs).mean(),
            df['NT_returns'].tail(obs).mean(), df['VI_returns'].tail(obs).mean(), df['TF_returns'].tail(obs).mean(),
            df['DiffReturns'].tail(obs).mean()
        ]
        return result
    except Exception as e:
        print(e)
        print('Failed run' + str(coords) + str(e))
        result = [coords[0], coords[1], coords[2]]
        for _ in range(6):
            result.append(0)
        return result

# Define the domains 

def GenerateCoords(reps, scale):
    param = []
    for (i,j,k) in simplex_iterator(scale):
        for _ in range(reps):
            param.append([i/scale,j/scale,k/scale])
    return param

reps = 1
scale = 2 # increment = 1/scale
param = GenerateCoords(reps,scale)
# print(param)
print(len(param))

# Run experiment
def main():
    p = mp.Pool()
    data = p.map(job, tqdm.tqdm(param))
    p.close()
    data = np.array(data)
    return data

if __name__ == '__main__':
    data = main()
    df = pd.DataFrame()
    # Inputs 
    df['WS_NT_inital'] = data[:,0]
    df['WS_VI_inital'] = data[:,1]
    df['WS_TF_initial'] = data[:,2]
    # Outputs 
    df['WS_NT_final'] = data[:,3]
    df['WS_VI_final'] = data[:,4]
    df['WS_TF_final'] = data[:,5]
    df['NT_returns_final'] = data[:,6]
    df['NT_returns_final'] = data[:,7]
    df['NT_returns_final'] = data[:,8]
    df['DiffReturns'] = data[:,9]
    print(df)

    df.to_csv("data/data2.csv")
    print("Completion time: " + str(time.time() - startTime))