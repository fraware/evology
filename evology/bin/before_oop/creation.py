from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
import numpy as np
from math import isnan

toolbox = base.Toolbox()
from parameters import (
    min_nt_strat,
    max_nt_strat,
    min_vi_strat,
    max_vi_strat,
    tf_daily_ma_horizon_index,
    tf_daily_ma_horizons_probas,
)
from parameters import tf_daily_ma_horizons, RefAssets, RefCash, G, scholl_tf_strat
from parameters import scholl_tf_index
import cythonized


def DrawStrategy(strat, rng):
    index = 0
    if strat == "nt":
        # strategy = np.random.uniform(min_nt_strat, max_nt_strat) / 10
        strategy = rng.uniform(min_nt_strat, max_nt_strat) / 1000
    elif strat == "vi":
        strategy = rng.uniform(min_vi_strat, max_vi_strat) / 1000
    elif strat == "tf":
        # strategy = rng.integers(min_tf_strat, max_tf_strat + 1)
        """Discrete TF-substrategy space"""
        index = int(
            rng.choice(tf_daily_ma_horizon_index, 1, p=tf_daily_ma_horizons_probas)
        )
        strategy = tf_daily_ma_horizons[index]
    else:
        raise ValueError("Unrecognised type. " + str(strat))
    return strategy, index


creator.create("fitness_strategy", base.Fitness, weights=(1.0,))

creator.ind = cythonized.Individual

# TODO: individual_ga is a list, individual_gp will be a gp.primitiveTree.

toolbox.register("trader", np.random.randint, 0, 1)
toolbox.register("gen_ind", tools.initCycle, creator.ind, (toolbox.trader,), n=1)


def IndCreation(strat):
    ind = toolbox.gen_ind()
    if strat == "nt":
        ind.type = "nt"
        # ind.leverage = LeverageNT
        ind.type_as_int = cythonized.convert_ind_type_to_num("nt")
    elif strat == "vi":
        ind.type = "vi"
        # ind.leverage = LeverageVI
        ind.type_as_int = cythonized.convert_ind_type_to_num("vi")
    elif strat == "tf":
        ind.type = "tf"
        # ind.leverage = LeverageTF
        ind.type_as_int = cythonized.convert_ind_type_to_num("tf")
    elif strat == "av":
        ind.type = "av"
        ind.type_as_int = cythonized.convert_ind_type_to_num("av")
    elif strat == "bh":
        ind.type = "bh"
        ind.type_as_int = cythonized.convert_ind_type_to_num("bh")
        ind.tsv = 1.0
    elif strat == "ir":
        ind.type = "ir"
        ind.type_as_int = cythonized.convert_ind_type_to_num("ir")
        ind.tsv = 0.0
    # ind.process = 1.0
    return ind


def CreatePop(n, space, WealthCoords, CurrentPrice, strategy, rng, interest_year):

    if interest_year - G + min_vi_strat / 1000 <= 0:
        print(interest_year - G + min_vi_strat / 1000)
        raise RuntimeError("Interest rate - G < min VI val, hence negative valuations")

    if n < 3:
        raise ValueError("Cannot create diverse population with less than 3 agents. ")
    if sum(WealthCoords) > 1.001 or sum(WealthCoords) < 0.999:
        raise ValueError("Sum of wealth coordinates is higher than 1. ")

    # Determine total and strategy assets and cash
    TotalAsset, TotalCash = n * RefAssets, n * RefCash
    ShareNT, ShareVI, ShareTF = WealthCoords[0], WealthCoords[1], WealthCoords[2]

    NTAsset, NTCash = ShareNT * TotalAsset, ShareNT * TotalCash
    VIAsset, VICash = ShareVI * TotalAsset, ShareVI * TotalCash
    TFAsset, TFCash = ShareTF * TotalAsset, ShareTF * TotalCash

    # Draw
    pop = []

    NumNT, NumVI, NumTF = 0, 0, 0
    if WealthCoords[0] != 0:
        pop.append(IndCreation("nt"))
        NumNT += 1
    if WealthCoords[1] != 0:
        pop.append(IndCreation("vi"))
        NumVI += 1
    if WealthCoords[2] != 0:
        pop.append(IndCreation("tf"))
        NumTF += 1
    # Add a buy and hold agent (for benchmark)
    # pop.append(IndCreation('bh'))
    # Add a sell and deposit agent (for benchmark)
    # pop.append(IndCreation('ir'))

    if strategy != None:
        pop.append(IndCreation("av"))

    for i in range(n - (NumNT + NumVI + NumTF)):
        rd = rng.random()
        if rd <= ShareNT:
            pop.append(IndCreation("nt"))
            NumNT += 1
        elif rd > ShareNT and rd <= ShareNT + ShareVI:
            pop.append(IndCreation("vi"))
            NumVI += 1
        elif rd > ShareNT + ShareVI:
            pop.append(IndCreation("tf"))
            NumTF += 1

    if NumNT != 0:
        PcNTCash = NTCash / NumNT
        PcNTAsset = NTAsset / NumNT

    if NumVI != 0:
        PcVICash = VICash / NumVI
        PcVIAsset = VIAsset / NumVI

    if NumTF != 0:
        PcTFCash = TFCash / NumTF
        PcTFAsset = TFAsset / NumTF

    if space == "scholl":
        for ind in pop:
            if ind.type == "nt":
                ind.strategy = 0.01
            if ind.type == "vi":
                ind.strategy = 0.01
            if ind.type == "tf":
                ind.strategy = scholl_tf_strat
                ind.strategy_index = scholl_tf_index

    if space == "extended":
        for ind in pop:
            if ind.type == "nt":
                ind.strategy, ind.strategy_index = DrawStrategy("nt", rng)
            if ind.type == "vi":
                ind.strategy, ind.strategy_index = DrawStrategy("vi", rng)
            if ind.type == "tf":
                ind.strategy, ind.strategy_index = DrawStrategy("tf", rng)

    for ind in pop:
        ind.loan = 0.0
        ind.margin = 0.0
        if ind.type == "av":
            ind.cash = RefCash
            ind.asset = RefAssets
            ind.adaptive_strategy = strategy
        if ind.type == "bh":
            ind.cash = 0.0  # RefCash
            ind.asset = 1.0 * RefAssets
        if ind.type == "ir":
            ind.cash = 1.0 * RefCash
            ind.asset = 0.0  # RefAssets
        if ind.type == "nt":
            ind.cash = PcNTCash
            ind.asset = PcNTAsset
            ind.val_net = (1.0 + (interest_year + ind.strategy) - G) ** (
                1.0 / 252.0
            ) - 1.0
            if isnan(ind.val_net) == True or ind.val_net <= 0:
                print(ind.val_net)
                print(ind.strategy)
                raise RuntimeError("Negative or NaN ind.val_net (denominator) for NT")
        if ind.type == "vi":
            ind.cash = PcVICash
            ind.asset = PcVIAsset
            ind.val_net = (1.0 + (interest_year + ind.strategy) - G) ** (
                1.0 / 252.0
            ) - 1.0
            if isnan(ind.val_net) == True or ind.val_net <= 0:
                print(ind.val_net)
                print(ind.strategy)
                raise RuntimeError("Negative or NaN ind.val_net (denominator) for VI")
        if ind.type == "tf":
            ind.cash = PcTFCash
            ind.asset = PcTFAsset

    MoneySupply = 0.0

    for ind in pop:
        ind.wealth = ind.cash + ind.asset * CurrentPrice - ind.loan
        ind.prev_wealth = ind.wealth
        if ind.wealth < 0:
            raise ValueError("Negative wealth at population creation.")
        if ind.type == "nt":
            if ind.asset != PcNTAsset:
                raise RuntimeError("NT asset position mismatch.")
        if ind.type != "bh" or ind.type != "ir":
            MoneySupply += ind.cash

    return pop, TotalAsset, MoneySupply


def WealthReset(
    pop,
    popsize,
    space,
    WealthCoords,
    ResetWealth,
    CurrentPrice,
    strategy,
    rng,
    interest_year,
):
    # current_size = len(pop)
    # types = [ind.type for ind in pop]
    if ResetWealth == True:
        del pop
        pop, asset_supply, MoneySupply = CreatePop(
            popsize, space, WealthCoords, CurrentPrice, strategy, rng, interest_year
        )

    # if len(pop) != current_size:
    #     print([current_size, len(pop)])
    #     print([types, [ind.type for ind in pop]])
    #     raise ValueError('Wealth reset generated a population size mismatch.')
    return pop
