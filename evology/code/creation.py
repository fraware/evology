from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap import gp
import numpy as np
import random
toolbox = base.Toolbox()
from parameters import *

creator.create("fitness_strategy", base.Fitness, weights=(1.0,))

creator.create("ind_tf", list, typecode = 'd', fitness=creator.fitness_strategy, 
    wealth = 0, 
    type = "tf", 
    MonReturn = 0,
    cash = 0, 
    asset = 0, 
    loan = RefLoan, 
    margin = 0, 
    tsf = None, 
    tsv = 0, 
    edf = None, 
    MonWealth = np.zeros((1, 21)),
    edv = 0, 
    process = 1, 
    ema = 0, 
    profit = 0, 
    prev_wealth = 0, 
    leverage = LeverageNT)

creator.create("ind_vi", list, typecode = 'd', fitness=creator.fitness_strategy, 
    wealth = 0, 
    type = "vi", 
    MonReturn = 0,
    cash = 0, 
    asset = 0, 
    loan = RefLoan, 
    margin = 0, 
    tsf = None, 
    tsv = 0, 
    edf = None, 
    MonWealth = np.zeros((1, 21)),
    edv = 0, 
    process = 1, 
    ema = 0, 
    profit = 0, 
    prev_wealth = 0, 
    leverage = LeverageVI)

creator.create("ind_nt", list, typecode = 'd', fitness=creator.fitness_strategy, 
    wealth = 0, 
    type = "nt", 
    MonReturn = 0,
    cash = 0, 
    asset = 0, 
    loan = RefLoan, 
    margin = 0, 
    tsf = None, 
    tsv = 0, 
    edf = None, 
    MonWealth = np.zeros((1, 21)),
    edv = 0, 
    process = 1, 
    ema = 0, 
    profit = 0, 
    prev_wealth = 0, 
    leverage = LeverageTF)

# TODO: individual_ga is a list, individual_gp will be a gp.primitiveTree.
# TODO: add the procedure for larger strategy space. Maybe a mode to select the 
# Tight or Expanded strategy space. 

toolbox.register("tf", random.randint, MIN_TIME_HORIZON, MAX_TIME_HORIZON)
toolbox.register("gen_tf_ind", tools.initCycle, creator.ind_tf, (toolbox.tf,), n=1)

toolbox.register("vi", random.randint, MIN_VALUATION_VI, MAX_VALUATION_VI)
toolbox.register("gen_vi_ind", tools.initCycle, creator.ind_vi, (toolbox.vi,), n=1)

toolbox.register("nt", random.randint, MIN_VALUATION_NT, MAX_VALUATION_NT)
toolbox.register("gen_nt_ind", tools.initCycle, creator.ind_nt, (toolbox.nt,), n=1)

def gen_rd_ind(Coords):
    rd = random.random()
    if rd <= Coords[0]:
        return toolbox.gen_nt_ind()
    elif rd > Coords[0] and rd <= Coords[0] + Coords[1]:
        return toolbox.gen_vi_ind()
    elif rd > Coords[0] + Coords[1] and rd <= Coords[2] + Coords[1] + Coords[0]:
        return toolbox.gen_tf_ind()

toolbox.register("gen_rd_ind", gen_rd_ind)


def CreatePop(n, WealthCoords, price):

    if n < 3:
        raise ValueError('Cannot create diverse population with less than 3 agents.')

    # Determine total and strategy assets and cash
    TotalAsset, TotalCash = n * RefAssets, n * RefCash
    ShareNT, ShareVI, ShareTF = WealthCoords[0], WealthCoords[1], WealthCoords[2]

    NTAsset, NTCash = ShareNT * TotalAsset, ShareNT * TotalCash
    VIAsset, VICash = ShareVI * TotalAsset, ShareVI * TotalCash
    TFAsset, TFCash = ShareTF * TotalAsset, ShareTF * TotalCash

    # Draw 
    pop = []
    pop.append(toolbox.gen_nt_ind())
    pop.append(toolbox.gen_vi_ind())
    pop.append(toolbox.gen_tf_ind())
    NumNT, NumVI, NumTF = 1, 1, 1

    for i in range(n-3):
        rd = random.random()
        if rd <= ShareNT:
            pop.append(toolbox.gen_nt_ind())
            NumNT += 1
        elif rd > ShareNT and rd <= ShareNT + ShareVI:
            pop.append(toolbox.gen_vi_ind())
            NumVI += 1
        elif rd > ShareNT + ShareVI and rd <= ShareTF + ShareVI + ShareNT:
            pop.append(toolbox.gen_tf_ind())
            NumTF += 1

    PcNTCash = NTCash / NumNT
    PcVICash = VICash / NumVI
    PcTFCash = TFCash / NumTF

    PcNTAsset = NTAsset / NumNT
    PcVIAsset = VIAsset / NumVI
    PcTFAsset = TFAsset / NumTF

    #TODO:  We may have to change what ind[0] means for VI/NT when opening to residual rates of return.

    # We adjust agent cash asset prev_wealth wrt their strategy.
    # We stay in the small strategy space and adjust agent strategies.
    for ind in pop:
        if ind.type == 'nt':
            ind[0] = 100
            ind.cash = PcNTCash 
            ind.asset = PcNTAsset
        if ind.type == 'vi':
            ind[0] = 100
            ind.cash = PcVICash 
            ind.asset = PcVIAsset
        if ind.type == 'tf':
            ind[0] = 2
            ind.cash = PcTFCash 
            ind.asset = PcTFAsset
        ind.prev_wealth = ind.cash + ind.asset * price 
        ind.wealth = ind.cash + ind.asset * price - ind.loan


    ''' optional bit just to check 
    wealthNT, wealthVI, wealthTF = 0,0,0
    for ind in pop:
        if ind.type == 'nt':
            wealthNT += ind.prev_wealth
        if ind.type == 'vi':
            wealthVI += ind.prev_wealth
        if ind.type == 'tf':
            wealthTF += ind.prev_wealth
    totalW = wealthTF + wealthNT + wealthVI
    print('Current factors')
    print([wealthNT/totalW, wealthVI/totalW,wealthTF/totalW])
    '''

    return pop, TotalAsset

def WealthReset(pop, WealthCoords, generation, ResetWealth, price):
    if generation <= SHIELD_DURATION:
        pop, asset_supply = CreatePop(len(pop), WealthCoords, price)
    else: 
        if ResetWealth == True:
            pop, asset_supply = CreatePop(len(pop), WealthCoords, price)
    return pop