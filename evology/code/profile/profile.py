import sys
sys.path.append('./evology/code/')
from steps import *

@profile 
def main(mode, space, solver, circuit, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth):
    # Initialise important variables and dataframe to store results
    ReturnsNT, ReturnsVI, ReturnsTF = np.zeros((MAX_GENERATIONS - data.Barr, POPULATION_SIZE)), np.zeros((MAX_GENERATIONS - data.Barr, POPULATION_SIZE)), np.zeros((MAX_GENERATIONS - data.Barr, POPULATION_SIZE))
    generation, CurrentPrice, dividend, spoils = 0, InitialPrice, INITIAL_DIVIDEND, 0
    results = np.zeros((MAX_GENERATIONS - data.Barr, data.variables))
    price_history, dividend_history = [], []

    pop, asset_supply = cr.CreatePop(POPULATION_SIZE, space, wealth_coordinates)
    bs.calculate_wealth(pop, CurrentPrice)
    bs.UpdatePrevWealth(pop)

    for generation in tqdm(range(MAX_GENERATIONS), disable=tqdm_display, miniters = 100, mininterval=0.5):

        # Population reset
        pop = cr.WealthReset(pop, space, wealth_coordinates, generation, reset_wealth)

        # Hypermutation
        pop, replacements, spoils= ga.hypermutate(pop, mode, asset_supply, CurrentPrice, generation, spoils, wealth_coordinates) # Replace insolvent agents     
        
        # Strategy evolution
        pop, CountSelected, CountMutated, CountCrossed, StratFlow = ga_evolution(pop, mode, space, 
            generation, wealth_coordinates, PROBA_SELECTION, MUTATION_RATE)

        # Calculate wealth and previous wealth
        bs.calculate_wealth(pop, CurrentPrice)
        bs.UpdatePrevWealth(pop)

        # Market decisions (tsv, proc, edf)
        pop= decision_updates(pop, mode, price_history, dividend_history)

        # Market clearing 
        pop, mismatch, CurrentPrice, price_history, ToLiquidate= marketClearing(pop, CurrentPrice, price_history, spoils, solver, circuit)

        # Market execution
        pop, volume, dividend, random_dividend, dividend_history, spoils= marketActivity(pop, 
            CurrentPrice, asset_supply, dividend, dividend_history, spoils, ToLiquidate)
        
        # Earnings, compute profits
        pop= update_wealth(pop, CurrentPrice, generation, wealth_coordinates, POPULATION_SIZE, reset_wealth)

        # Record results
        results, ReturnsNT, ReturnsVI, ReturnsTF = data.record_results(results, generation, CurrentPrice, mismatch, 
        dividend, random_dividend, volume, replacements, pop, spoils, 
        asset_supply, ReturnsNT, ReturnsVI, ReturnsTF,
        CountSelected, CountMutated, CountCrossed, StratFlow)

    df = pd.DataFrame(results, columns = data.columns)
    
    return df, pop

from parameters import *


np.random.seed(8)
wealth_coordinates = [1/3, 1/3, 1/3]
# wealth_coordinates = [0.20899108903451205, 0.1210376286378561, 0.6699712823276319]
wealth_coordinates = np.random.dirichlet(np.ones(3),size=1)[0].tolist()

print(wealth_coordinates)


# main(mode, space, solver, circuit, MAX_GENERATIONS, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth):
@profile
def run(POPULATION_SIZE, learning_mode, TIME, wealth_coordinates, tqdm_display, reset_wealth):

    if learning_mode == 0:
        df,pop = main("static", 'scholl', 'esl.true', False, TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 1:
        df,pop = main("between", 'scholl', 'esl.true', False, TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 2:
        df,pop = main("between", 'scholl', 'esl.true', False, TIME, PROBA_SELECTION, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 3:
        df,pop = main("static", 'extended', 'esl', False, TIME, 0, POPULATION_SIZE, 0, wealth_coordinates, tqdm_display, reset_wealth)
    if learning_mode == 4:
        df,pop = main("between", 'extended', 'esl', False, TIME, PROBA_SELECTION, POPULATION_SIZE, MUTATION_RATE, wealth_coordinates, tqdm_display, reset_wealth)

    return df, pop

df,pop = run(100, 1, 10000, wealth_coordinates, tqdm_display=False, reset_wealth=False)




''' In command: 
kernprof -v -l evology/code/profile/profile.py > evology/code/profile/profile.txt
'''
'''
kernprof -v -l evology/code/profile.py
kernprof -v -l evology/code/run.py
kernprof -v -l evology/code/run.py > evology/code/profile.txt
 ; no need to be in python env first'''
