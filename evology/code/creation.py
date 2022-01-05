from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
import numpy as np
import random
toolbox = base.Toolbox()
from parameters import *


def DrawReturnRate(strat):
    if strat == 'vi':
        rate = np.random.uniform(MIN_RR_VI, MAX_RR_VI) / 1000
    if strat == 'nt':
        rate = np.random.uniform(MIN_RR_NT, MAX_RR_NT) / 1000
    else:
        rate = np.random.uniform(MIN_RR_TF, MAX_RR_TF) / 1000
    return rate

creator.create("fitness_strategy", base.Fitness, weights=(1.0,))

creator.create("ind_tf", list, typecode = 'd', fitness=creator.fitness_strategy, 
    strategy = 0,
    wealth = 0, 
    type = "tf", 
    cash = 0, 
    asset = 0, 
    loan = RefLoan, 
    margin = 0, 
    tsv = 0, 
    edf = None, 
    edv = 0, 
    process = 1, 
    ema = 0, 
    profit = 0, 
    prev_wealth = 0, 
    DailyReturn = 0,
    leverage = LeverageTF)

creator.create("ind_vi", list, typecode = 'd', fitness=creator.fitness_strategy, 
    strategy = 0,
    wealth = 0, 
    type = "vi", 
    cash = 0, 
    asset = 0, 
    loan = RefLoan, 
    margin = 0, 
    tsv = 0, 
    edf = None, 
    edv = 0, 
    process = 1, 
    ema = 0, 
    profit = 0, 
    prev_wealth = 0, 
    DailyReturn = 0,
    leverage = LeverageVI)

creator.create("ind_nt", list, typecode = 'd', fitness=creator.fitness_strategy, 
    strategy = 0,
    wealth = 0, 
    type = "nt", 
    cash = 0, 
    asset = 0, 
    loan = RefLoan, 
    margin = 0, 
    tsv = 0, 
    edf = None, 
    edv = 0, 
    process = 1, 
    ema = 0, 
    profit = 0, 
    prev_wealth = 0, 
    DailyReturn = 0,
    leverage = LeverageNT)

# TODO: individual_ga is a list, individual_gp will be a gp.primitiveTree.

toolbox.register("tf", np.random.randint, MIN_THETA, MAX_THETA+1)
toolbox.register("gen_tf_ind", tools.initCycle, creator.ind_tf, (toolbox.tf,), n=1)

toolbox.register("vi", np.random.randint, 100, 100+1)
toolbox.register("gen_vi_ind", tools.initCycle, creator.ind_vi, (toolbox.vi,), n=1)

toolbox.register("nt", np.random.randint, 100, 100+1)
toolbox.register("gen_nt_ind", tools.initCycle, creator.ind_nt, (toolbox.nt,), n=1)

def gen_rd_ind(Coords):
    rd = np.random.random()
    if rd <= Coords[0]:
        return toolbox.gen_nt_ind()
    elif rd > Coords[0] and rd <= Coords[0] + Coords[1]:
        return toolbox.gen_vi_ind()
    elif rd > Coords[0] + Coords[1] and rd <= Coords[2] + Coords[1] + Coords[0]:
        return toolbox.gen_tf_ind()

toolbox.register("gen_rd_ind", gen_rd_ind)


def CreatePop(n, space, WealthCoords):

    if n < 3:
        raise ValueError('Cannot create diverse population with less than 3 agents. ')
    if sum(WealthCoords) > 1.001 or sum(WealthCoords) < 0.999:
        raise ValueError('Sum of wealth coordinates is higher than 1. ')

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
        pop.append(toolbox.gen_nt_ind())
        NumNT += 1
    if WealthCoords[1] != 0:
        pop.append(toolbox.gen_vi_ind())
        NumVI += 1
    if WealthCoords[2] != 0:
        pop.append(toolbox.gen_tf_ind())
        NumTF += 1

    for i in range(n- (NumNT + NumVI + NumTF)):
        rd = np.random.random()
        if rd <= ShareNT:
            pop.append(toolbox.gen_nt_ind())
            NumNT += 1
        elif rd > ShareNT and rd <= ShareNT + ShareVI:
            pop.append(toolbox.gen_vi_ind())
            NumVI += 1
        elif rd > ShareNT + ShareVI:
            pop.append(toolbox.gen_tf_ind())
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

    if space == 'scholl':
        for ind in pop:
            if ind.type == 'nt':
                ind.strategy = 0.01
                ind[0] = 100
            if ind.type == 'vi':
                ind.strategy = 0.01
                ind[0] = 100
            if ind.type == 'tf':
                ind.strategy = 0.01
                ind[0] = 2

    if space == 'extended':
        for ind in pop:
            if ind.type == 'nt':
                ind.strategy = DrawReturnRate('nt')
                ind[0] = 100
            if ind.type == 'vi':
                ind.strategy = DrawReturnRate('vi')
                ind[0] = 100
            if ind.type == 'tf':
                ind.strategy = DrawReturnRate('tf')

    for ind in pop:
        if ind.type == 'nt':
            ind.cash = PcNTCash 
            ind.asset = PcNTAsset
        if ind.type == 'vi':
            ind.cash = PcVICash 
            ind.asset = PcVIAsset
        if ind.type == 'tf':
            ind.cash = PcTFCash 
            ind.asset = PcTFAsset

    

    return pop, TotalAsset

def WealthReset(pop, space, WealthCoords, generation, ResetWealth):
    if generation > 1 and generation <= SHIELD_DURATION:
        pop, asset_supply = CreatePop(len(pop), space, WealthCoords)
    else: 
        if ResetWealth == True:
            pop, asset_supply = CreatePop(len(pop), space, WealthCoords)
    return pop