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
wealth_coordinates = [1 / 3, 1 / 3, 1 / 3]
print(wealth_coordinates)
df, pop = run(
    3, 0, 20000, wealth_coordinates, tqdm_display=False, reset_wealth=False, 
    ReinvestmentRate = 1.5, InvestmentHorizon = 255, InvestorBehavior = 'profit')

df.to_csv("rundata/run_data.csv")
print(df)


