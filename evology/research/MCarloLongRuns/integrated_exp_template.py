# Imports 
import numpy as np
import pandas as pd
import sys
import tqdm
import warnings
warnings.simplefilter("ignore")

if sys.platform == 'darwin':
    sys.path.append('/Users/aymericvie/Documents/GitHub/evology/evology/code')
    # Need to be executed from cd to MCarloLongRuns
if sys.platform == 'linux':
    sys.path.append('/home/vie/Documents/GitHub/evology/evology/code')
from main import main as evology
import multiprocessing as mp

TimeHorizon = 252 * 50 # + 3 * 21 # 
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
        result = [
            param[0], param[1], 
            df['WShare_NT'].mean(), df['WShare_VI'].mean(), df['WShare_TF'].mean(),
            df['SharpeNT'].mean(), df['SharpeVI'].mean(), df['SharpeTF'].mean(),
            np.nanmean(df['DeltaNTVI']), np.nanmean(df['DeltaNTTF']), np.nanmean(df['DeltaVITF']),
            df['AvgSignificance'].mean(), df['AvgNumberDev'].mean(), df['PerSignif'].mean()
        ]
        return result
    except Exception as e:
        print(e)
        # raise ValueError('Failed run') 
        print('Failed run' + str(param) + str(e))
        result = [param[0], param[1]]
        for _ in range(12):
            result.append(0)
        return result

# Define the domains 
domain_f = [x / 10.0 for x in range(0, 31, 1)]
domain_H = [x / 1 for x in range(21, 252*3+1, 21*2)]
# domain_f = [x / 10.0 for x in range(0, 31, 15)]
# domain_H = [x / 1 for x in range(21, 252*3+1, 500)]
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

def main():
    p = mp.Pool()
    data = p.map(job, tqdm.tqdm(param))
    p.close()
    data = np.array(data)
    return data

''' we are looking at reps of 10 for contunuous plots but 50 for ternaries'''
''' but lets not make too many runs when we dont have to. If we want to look at specific configs for scatterplots,
we can make dedicated experiments for that'''

''' change reps and time '''

reps = 5
param = GenerateParam(reps)
if __name__ == '__main__':
    data = main()
    df = pd.DataFrame()

    # Inputs 
    df['F'] = data[:,0]
    df['H'] = data[:,1]
    # Outputs 
    # Wealth share averages
    df['WShare_NT'] = data[:,2]
    df['WShare_VI'] = data[:,3]
    df['WShare_TF'] = data[:,4]
    # Sharpe ratios
    df['SharpeNT'] = data[:,5]
    df['SharpeVI'] = data[:,6]
    df['SharpeTF'] = data[:,7]
    # Delta measures 
    df['DeltaNTVI'] = data[:,8]
    df['DeltaNTTF'] = data[:,9]
    df['DeltaVITF'] = data[:,10]
    # Significance measures 
    df['AvgSignificance'] = data[:,11]
    df['AvgNumberDev'] = data[:,12]
    df['PerSignif'] = data[:,13]
    print(df)

    df.to_csv("data/data.csv")