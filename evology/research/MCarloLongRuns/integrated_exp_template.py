# Imports 
import numpy as np
import pandas as pd
import sys
if sys.platform == 'darwin':
    sys.path.append('/Users/aymericvie/Documents/GitHub/evology/evology/code')
    # Need to be executed from cd to MCarloLongRuns
if sys.platform == 'linux':
    sys.path.append('/home/vie/Documents/GitHub/evology/evology/code')
from main import main as evology
import multiprocessing as mp

TimeHorizon = 252 * 1 + 3 * 21 # 
PopulationSize = 3
Coordinates = [1/3, 1/3, 1/3]

def job(param):
    np.random.seed()
    # print(param)
    try:
        df, pop = evology(
            space = "scholl",
            solver = "esl.true",
            wealth_coordinates = Coordinates,
            POPULATION_SIZE = PopulationSize,
            MAX_GENERATIONS = TimeHorizon,
            PROBA_SELECTION = 0,
            MUTATION_RATE = 0,
            ReinvestmentRate = param[0],
            InvestmentHorizon = param[1],
            InvestorBehavior = 'JKM',
            tqdm_display = True,
            reset_wealth = False
            )
        result = [param[0], param[1], df['WShare_NT'].mean(), df['WShare_VI'].mean(), df['WShare_TF'].mean()]
        return result
    except Exception as e:
        print(e)
        # raise ValueError('Failed run') 
        print('Failed run' + str(param) + str(e))
        return [param[0], param[1], 0, 0, 0]

# Define the domains 
# domain_f = [x / 10.0 for x in range(0, 31, 1)]
# domain_H = [x / 1 for x in range(21, 252*3+1, 21)]
domain_f = [x / 10.0 for x in range(0, 31, 15)]
domain_H = [x / 1 for x in range(21, 252*3+1, 500)]
domain_H.insert(0, 10)
domain_H.insert(0, 5)
domain_H.insert(0, 2)

def GenerateParam(reps):
    param = []
    for i in range(len(domain_f)):
        for j in range(len(domain_H)):
            for _ in range(reps):
                config = [domain_f[i], domain_H[j]]
                param.append(config)
    return param

# print(param)

def main():
    p = mp.Pool()
    data = p.map(job, param)
    p.close()
    data = np.array(data)
    return data


reps = 2
param = GenerateParam(reps)
if __name__ == '__main__':
    data = main()
    df = pd.DataFrame()

    df['F'] = data[:,0]
    df['H'] = data[:,1]
    df['WShare_NT'] = data[:,2]
    df['WShare_VI'] = data[:,3]
    df['WShare_TF'] = data[:,4]
    print(df)

    df.to_csv("data/data.csv")