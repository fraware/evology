#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

import cython
from simulation import Simulation

def main(max_generations, population_size, wealth_coords, interest_rate, investment_bool, seed, reset):
    s = Simulation(
        max_generations=max_generations,
        population_size=population_size,
        wealth_coords=wealth_coords,
        interest_rate=interest_rate,
        investment_bool=investment_bool,
        seed=seed,
        reset=reset,
    )
    s.simulate()
    df = s.data
    return df

if __name__ == "__main__":
    df = main(
        max_generations=20000,
        population_size=3,
        wealth_coords= [1/4, 1/2, 1/4],
        interest_rate=0.01,
        investment_bool=False,
        seed=1,
        reset=False,
    )
    df.to_csv("rundata/run_data.csv")
    print(df)
