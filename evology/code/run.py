''' #!/usr/bin/env python3 '''
from main import *
from parameters import *

np.random.seed(9)
wealth_coordinates = [1/3, 1/3, 1/3]
# wealth_coordinates = [0.10293443867756183, 0.21651059179931073, 0.6805549695231274]
# wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()

print(wealth_coordinates)


# main(mode, space, solver, circuit, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth):

def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth):

    if learning_mode == 0:
        df,pop = main("static", 'scholl', 'newton', False, TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 1:
        df,pop = main("between", 'scholl', 'esl', False, TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 2:
        df,pop = main("between", 'scholl', 'esl', False, TIME, PROBA_SELECTION, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 3:
        df,pop = main("static", 'extended', 'esl', False, TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 4:
        df,pop = main("between", 'extended', 'esl', False, TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)

    return df, pop

df,pop = run(100, 0, 1000, wealth_coordinates, tqdm_display=False, reset_wealth=False)
df.to_csv("evology/data/run_data.csv")
print(df['Dividends'])

    