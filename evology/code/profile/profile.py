import sys

sys.path.append("./evology/code/")
sys.path.append("/Users/aymericvie/Documents/GitHub/evology/evology/code")
from simulation import Simulation

@profile
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
        population_size=10,
        wealth_coords= [1/4, 1/4, 1/2],
        interest_rate=0.01,
        investment_bool=True,
        seed=56615,
        reset=False,
    )
    print(df)


""" In command: 
kernprof -v -l evology/code/profile/profile.py > evology/code/profile/profile.txt

# For cythonized
cd evology/code
cythonize -i cythonized.pyx
chmod +x ./profile/profile.py
kernprof -v -l profile/profile.py > profile/profile.txt
 ; no need to be in python env first"""


"""
Annotation ]

cythonize -a -i yourmod.pyx

"""

"""
Using Black in the terminal

aymericvie@vie GitHub % black evology/evology/code

"""
