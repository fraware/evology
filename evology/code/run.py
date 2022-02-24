""" #!/usr/bin/env python3 """
from main import *
from parameters import *

def run(
    POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth, ReinvestmentRate, InvestmentHorizon, InvestorBehavior,
):
    if learning_mode == 0:
        df, pop = main(
            "scholl",
            "esl.true",
            wealth_coordinates,
            POPULATION_SIZE,
            TIME,
            0,
            0,
            ReinvestmentRate,
            InvestmentHorizon,
            InvestorBehavior,
            tqdm_display,
            reset_wealth
        )

    if learning_mode == 1:
        df, pop = main(
            "scholl",
            "esl.true",
            wealth_coordinates,
            POPULATION_SIZE,
            TIME,
            PROBA_SELECTION,
            MUTATION_RATE,
            ReinvestmentRate,
            InvestmentHorizon,
            InvestorBehavior,
            tqdm_display,
            reset_wealth,
        )
    return df, pop

wealth_coordinates = np.random.dirichlet(np.ones(3), size=1)[0].tolist()
np.random.seed(9)
# wealth_coordinates = [1 / 3, 1 / 3, 1 / 3]
np.random.seed()
wealth_coordinates=[0.12, 0.04, 0.84]
print(wealth_coordinates)
df, pop = run(
    3, 0, 100000, wealth_coordinates, tqdm_display=False, reset_wealth=False, 
    ReinvestmentRate = 1.0, InvestmentHorizon = 252, InvestorBehavior = 'profit')

df.to_csv("rundata/run_data.csv")
print(df)
print([df['NT_returns'].mean(), df['VI_returns'].mean(), df['TF_returns'].mean()])
obs = 500
# diffreturn = (df['NT_returns'].tail(obs).mean() - df['VI_returns'].tail(obs).mean())**2 + (df['NT_returns'].tail(obs).mean() - df['TF_returns'].tail(obs).mean())**2 + (df['VI_returns'].tail(obs).mean()-df['TF_returns'].tail(obs).mean())**2
# print(diffreturn)
print(df['DiffReturns'].tail(100).mean())
print

