from steps import *


def main(
    space,
    solver,
    wealth_coordinates,
    POPULATION_SIZE,
    MAX_GENERATIONS,
    PROBA_SELECTION,
    MUTATION_RATE,
    tqdm_display,
    reset_wealth,
):
    # Initialisation
    generation, CurrentPrice, dividend, spoils = 0, InitialPrice, INITIAL_DIVIDEND, 0
    results = np.zeros((MAX_GENERATIONS - data.Barr, data.variables))
    price_history, dividend_history, replace, volume, avg_phi = [], [], 0, 0.0, 0.0

    # Population creation
    pop, asset_supply = cr.CreatePop(POPULATION_SIZE, space, wealth_coordinates, CurrentPrice)

    for generation in tqdm(
        range(MAX_GENERATIONS), disable=tqdm_display, miniters=100, mininterval=0.5
    ):
        if CurrentPrice >= 1_000_000:
            warnings.warn('Simulation break: price above 1M.')
            break

        # Population reset
        pop = cr.WealthReset(pop, space, wealth_coordinates, generation, reset_wealth)

        # Hypermutation
        
        pop, replacements, spoils = ga.hypermutate(
            pop, spoils, replace
        ) 
        if replacements < 0:
            break


        # Strategy evolution
        pop = fit.ComputeFitness(pop, 252)
        pop, CountSelected, CountMutated, CountCrossed, StratFlow = ga_evolution(
            pop,
            space,
            generation,
            wealth_coordinates,
            PROBA_SELECTION,
            MUTATION_RATE,
            252,
        )

        # Market decisions 
        pop, replace = bsc.UpdateFullWealth(pop, CurrentPrice)
        pop = bsc.NoiseProcess(pop)
        pop = bsc.UpdateFval(pop, dividend)
        pop = bsc.CalculateTSV(pop, price_history, dividend_history, CurrentPrice)
        pop = bsc.DetermineEDF(pop)
        

        # Market clearing
        pop, mismatch, CurrentPrice, price_history, ToLiquidate = marketClearing(
            pop, CurrentPrice, price_history, spoils, solver, volume
        )

        pop = bsc.CalculateEDV(pop, CurrentPrice)

        # Market activity
        (
            pop,
            volume,
            dividend,
            random_dividend,
            dividend_history,
            spoils,
            Liquidations,
        ) = mk.MarketActivity(
            pop,
            CurrentPrice,
            asset_supply,
            dividend,
            dividend_history,
            spoils,
            ToLiquidate,
            random_dividend_history
        )
        pop, replace = bsc.UpdateWealthProfitAge(pop, CurrentPrice)
        pop = bsc.UpdateQuarterlyWealth(pop, generation)
        pop = bsc.UpdateWealthSeries(pop)

        # Investment
        ''' former investment process
        (pop, AvgT, PropSignif, HighestT, AvgAbsT) = iv.Profit_Investment(
        pop, ReinvestmentRate, InvestmentHorizon, generation
        )
        '''

        pop = iv.Emp_Investment(pop)
        AvgT, PropSignif, HighestT, AvgAbsT = 0, 0, 0, 0

        # Record results 
        results, sim_break = data.record_results(
            results,
            generation,
            CurrentPrice,
            mismatch,
            dividend,
            random_dividend,
            volume,
            replacements,
            pop,
            spoils,
            Liquidations,
            asset_supply,
            CountSelected,
            CountMutated,
            CountCrossed,
            StratFlow,
            AvgT,
            PropSignif,
            HighestT,
            AvgAbsT,
        )

        if sim_break == True:
            warnings.warn('Simulation break: one of the 3 strategy types is extinct.')
            break

    if generation < MAX_GENERATIONS - data.Barr:
        results = results[0:generation+1]

    df = pd.DataFrame(results, columns=data.columns)

    return df, pop
