""" #!/usr/bin/env python3 """
from main import *
from parameters import *

wealth_coordinates = np.random.dirichlet(np.ones(3), size=1)[0].tolist()
np.random.seed()
wealth_coordinates = [1/3,1/3,1/3]
print(wealth_coordinates)
df, pop = main(
    strategy = None,
    space = 'extended',
    wealth_coordinates=wealth_coordinates,
    POPULATION_SIZE = 1000,
    MAX_GENERATIONS = 10 * 252,
    tqdm_display=False,
    reset_wealth=False,
)

df.to_csv("rundata/run_data.csv")


