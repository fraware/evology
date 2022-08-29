from steps import *


def main(
    strategy,
    space,
    wealth_coordinates,
    POPULATION_SIZE,
    MAX_GENERATIONS,
    interest_year,
    investment,
    seed,
    tqdm_display,
    reset_wealth,
):
    # Initialisation
    generation, CurrentPrice, dividend, spoils = 0, InitialPrice, INITIAL_DIVIDEND, 0.0
    results = np.zeros((MAX_GENERATIONS - data.Barr, data.variables))
    replace, volume = 0, 0.0

    # Random generator
    rng = np.random.default_rng(seed=seed)
    np.random.seed(seed)

    # Population creation
    pop, asset_supply, MoneySupply = cr.CreatePop(
        POPULATION_SIZE,
        space,
        wealth_coordinates,
        CurrentPrice,
        strategy,
        rng,
        interest_year,
    )
    # print(MoneySupply)

    # Dividend and NT process generation
    # price_history = prc.FictiousPriceSeries(rng)
    price_history = []
    price_emas = [InitialPrice] * len(tf_daily_ma_horizons)

    dividend_series, rd_dividend_series = div.ExogeneousDividends(MAX_GENERATIONS, rng)
    rng = np.random.default_rng(seed=seed + 1)
    process_series = prc.ExogeneousProcess(MAX_GENERATIONS, rng)
    rng = np.random.default_rng(seed=seed)

    # interest_day = interest_year / 252.0
    interest_day = ((1.0 + interest_year) ** (1.0 / 252.0)) - 1.0

    for generation in tqdm(
        range(MAX_GENERATIONS), disable=tqdm_display, miniters=100, mininterval=0.5
    ):
        # for generation in range(MAX_GENERATIONS):
        # print(CurrentPrice)
        # Population reset

        if generation == 0:
            mismatch = 0
            random_dividend = 0
            replacements = 0
            Liquidations = 0
            total_cash = 0

        if generation >= 1:

            pop = cr.WealthReset(
                pop,
                POPULATION_SIZE,
                space,
                wealth_coordinates,
                reset_wealth,
                CurrentPrice,
                strategy,
                rng,
                interest_year,
            )

            # Hypermutation
            pop, replacements, spoils = ga.hypermutate(pop, spoils, replace)
            if replacements < 0:
                break

            # Strategy evolution
            # pop = fit.ComputeFitness(pop, 252)

            # pop, CountSelected, CountMutated, CountCrossed, StratFlow = ga_evolution(
            #    pop,
            #    space,
            #    generation,
            #    wealth_coordinates,
            #    PROBA_SELECTION,
            #    MUTATION_RATE,
            #    252,
            # )

            # Market decisions

            pop, replace = bsc.UpdateFullWealth(pop, CurrentPrice)
            pop = bsc.UpdateFval(pop, dividend, interest_year)
            price_emas = bsc.price_emas(CurrentPrice, price_emas)
            pop = bsc.CalculateTSV_staticf(
                pop,
                price_history,
                CurrentPrice,
                process_series[generation],
                rng,
                price_emas,
            )
            pop = bsc.CalculateTSV_avf(
                pop, generation, strategy, price_history, dividend, interest_day
            )
            ToLiquidate = bsc.DetermineLiquidation(spoils, volume)

            # ''' for VI on contemporaneous price '''
            # ed_functions = bsc.agg_ed_esl(pop, ToLiquidate)
            # CurrentPrice = mc.esl_solver(ed_functions, CurrentPrice)
            ed_functions = cz.agg_ed(
                pop,
                ToLiquidate,
                asset_supply,
                spoils,
                bsc.count_short_assets(pop, spoils),
            )
            NewPrice = mc.scipy_solver(ed_functions, CurrentPrice)
            pop, mismatch = cz.calculate_edv(pop, NewPrice)
            # print(NewPrice)

            # Market activity
            dividend, random_dividend = (
                dividend_series[0, generation],
                rd_dividend_series[0, generation],
            )
            pop, volume, spoils, Liquidations = mk.execute_ed(
                pop, NewPrice, asset_supply, spoils, ToLiquidate
            )

            """
            if mismatch > 1000:
                print('Type, W, EDV, TSV, S')
                print([generation, mismatch])
                print(asset_supply, asset_supply * Short_Size_Percent / 100)
                for ind in pop:

                    print([ind.type, ind.wealth, ind.edv, ind.tsv, ind.asset])

                raise RuntimeError('Mismatch today.')
            """

            # if volume != 0:
            #     CurrentPrice = NewPrice
            CurrentPrice = NewPrice

            # print('---- GENERATION ' + str(generation) + ' ----')
            # print('Price: ' + str(CurrentPrice))
            # for ind in pop:
            #     print([ind.type, ind.edv, ind.asset, ind.wealth])

            price_history = bsc.UpdatePriceHistory(price_history, CurrentPrice)

            if generation == 1:
                print("Warning: earnings are turned off.")
            pop = mk.earnings(pop, dividend, interest_day)
            # pop = mk.update_margin(pop, CurrentPrice)
            pop = bsc.clear_debt(pop, CurrentPrice, interest_day)

            pop, replace = bsc.UpdateWealthProfitAge(pop, CurrentPrice)
            pop = bsc.UpdateQuarterlyWealth(pop, generation)
            pop = bsc.UpdateWealthSeries(pop)

            if generation >= ShieldInvestment and investment != None:
                pop = iv.Emp_Investment(pop, rng)

            """
            # Wealth normalisation
            pop, total_cash = bsc.Wealth_Normalisation(
                pop,
                MoneySupply,
                CurrentPrice
            )
            """
            total_cash = 0

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
            process_series[generation],
            total_cash,
            MoneySupply,
        )
        if volume == 0 and generation >= 1:
            print("Type, W, EDV, TSV, S")
            print(
                asset_supply,
                asset_supply * Short_Size_Percent / 100,
                bsc.count_short_assets(pop, spoils),
            )
            for ind in pop:

                print([ind.type, ind.wealth, ind.edv, ind.tsv, ind.asset])
            print(("Null volume today."))
            # break
            raise RuntimeError("Null volume today.")

        if sim_break == 1 and reset_wealth != True:
            print(generation)
            warnings.warn("Only one base strategy left.")
            break

        if CurrentPrice >= 10_000_000:
            warnings.warn("Simulation break: price above 10M.")
            # raise RuntimeError('Price above 1M')
            break

    if generation < MAX_GENERATIONS - data.Barr:
        results = results[0 : generation + 1]

    df = pd.DataFrame(results, columns=data.columns)

    # av_stats = [df["AV_wealth"].iloc[-1] / df["AV_wealth"].iloc[0] - 1, round(df["AV_return"].mean(),4), round(df["AV_return"].std(),3),
    # df["AV_wealth"].iloc[0], df["AV_wealth"].iloc[-1]]

    return df, pop  # , av_stats
