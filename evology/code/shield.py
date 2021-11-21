import warnings
import numpy as np
import balance_sheet as bs
from parameters import MAX_ATTEMPTS, SHIELD_DURATION, SHIELD_TOLERANCE

def ShieldWealth(pop, coords, generation, reset_wealth):
    if generation < SHIELD_DURATION or reset_wealth == True:
        pop = IteratedShield(pop, coords)
    return pop

def IteratedShield(pop, coords):
    diff, WealthSum, WealthNT, WealthVI, WealthTF = DetDifference(pop, coords)
    attempts = 0
    while sum([abs(item) for item in diff]) >= SHIELD_TOLERANCE and attempts < MAX_ATTEMPTS: 
        pop = Shield(pop, coords, WealthSum, WealthNT, WealthVI, WealthTF)
        diff, WealthSum, WealthNT, WealthVI, WealthTF = DetDifference(pop, coords)
        attempts += 1
    if attempts >= MAX_ATTEMPTS and sum([abs(item) for item in diff]) >= SHIELD_TOLERANCE:
        warnings.warn('IteratedShield imperfect despite Max attempts executed.')
    return pop

def DetDifference(pop, coords):
    TargetNT = coords[0]
    TargetVI = coords[1]
    TargetTF = coords[2]

    WealthNT = bs.GetWealth(pop, 'nt')
    WealthVI = bs.GetWealth(pop, 'vi')
    WealthTF = bs.GetWealth(pop, 'tf')
    WealthSum = WealthNT + WealthVI + WealthTF 

    diff = [WealthNT / WealthSum - TargetNT, WealthVI / WealthSum - TargetVI, WealthTF/WealthSum - TargetTF]
    return diff, WealthSum, WealthNT, WealthVI, WealthTF


def Shield(pop, coords, WealthSum, WealthNT, WealthVI, WealthTF):
    
    TargetNT = coords[0]
    TargetVI = coords[1]
    TargetTF = coords[2]

    D = np.array([
    [1-TargetNT,-TargetNT, -TargetNT], 
    [-TargetVI, 1-TargetVI, -TargetNT],
    [-TargetTF, -TargetTF, 1-TargetTF]]) 

    Dx = np.array([
    [TargetNT * WealthSum - WealthNT,-TargetNT, -TargetNT], 
    [TargetVI * WealthSum - WealthVI, 1-TargetVI, -TargetNT],
    [TargetTF * WealthSum - WealthTF, -TargetTF, 1-TargetTF]]) 

    Dy = np.array([
    [1-TargetNT, TargetNT * WealthSum - WealthNT, -TargetNT], 
    [-TargetVI, TargetVI * WealthSum - WealthVI, -TargetNT],
    [-TargetTF, TargetTF * WealthSum - WealthTF, 1-TargetTF]]) 

    Dz = np.array([
    [1-TargetNT, -TargetNT, TargetNT * WealthSum - WealthNT], 
    [-TargetVI, 1-TargetVI, TargetVI * WealthSum - WealthVI],
    [-TargetTF, -TargetTF, TargetTF * WealthSum - WealthTF]]) 

    TransferNT = max((np.linalg.det(Dx)/np.linalg.det(D)),0)
    TransferVI = max((np.linalg.det(Dy)/np.linalg.det(D)),0)
    TransferTF = max((np.linalg.det(Dz)/np.linalg.det(D)),0)

    NumNT = bs.GetNumber(pop, 'nt')
    NumVI = bs.GetNumber(pop, 'vi')
    NumTF = bs.GetNumber(pop, 'tf')

    PcTransferNT = TransferNT / NumNT
    PcTransferVI = TransferVI / NumVI
    PcTransferTF = TransferTF / NumTF

    if PcTransferNT < 0 or PcTransferNT < 0 or PcTransferTF < 0:
        raise ValueError('Negative PcTransfer')

    for ind in pop:
        if ind.type =='nt':
            ind.loan -= PcTransferNT
        if ind.type == 'vi':
            ind.loan -= PcTransferVI
        if ind.type == 'tf':
            ind.loan -= PcTransferTF

    return pop

# WealthSum = WealthNT + WealthVI + WealthTF 
# print([WealthNT / WealthSum, WealthVI / WealthSum, WealthTF / WealthSum])


# if TargetTF + TargetVI + TargetNT != 1:
#     raise ValueError('Target coordinates do not sum to 1.')

# D = np.array([
# [1-TargetNT,-TargetNT, -TargetNT], 
# [-TargetVI, 1-TargetVI, -TargetNT],
# [-TargetTF, -TargetTF, 1-TargetTF]]) 

# Dx = np.array([
# [TargetNT * WealthSum - WealthNT,-TargetNT, -TargetNT], 
# [TargetVI * WealthSum - WealthVI, 1-TargetVI, -TargetNT],
# [TargetTF * WealthSum - WealthTF, -TargetTF, 1-TargetTF]]) 

# Dy = np.array([
# [1-TargetNT, TargetNT * WealthSum - WealthNT, -TargetNT], 
# [-TargetVI, TargetVI * WealthSum - WealthVI, -TargetNT],
# [-TargetTF, TargetTF * WealthSum - WealthTF, 1-TargetTF]]) 

# Dz = np.array([
# [1-TargetNT, -TargetNT, TargetNT * WealthSum - WealthNT], 
# [-TargetVI, 1-TargetVI, TargetVI * WealthSum - WealthVI],
# [-TargetTF, -TargetTF, TargetTF * WealthSum - WealthTF]]) 

# ### 

# TransferNT = np.linalg.det(Dx)/np.linalg.det(D)
# TransferVI = np.linalg.det(Dy)/np.linalg.det(D)
# TransferTF = np.linalg.det(Dz)/np.linalg.det(D)

# # NewWealthNT = WealthNT + TransferNT
# # NewWealthVI = WealthVI + TransferVI
# # NewWealthTF = WealthTF + TransferTF
# # print([NewWealthNT, NewWealthVI,NewWealthTF])
# # NewSumWealth = NewWealthNT + NewWealthVI + NewWealthTF

# # print(TransferNT, TransferVI, TransferTF)
# # print([TargetNT, TargetVI, TargetTF])
# # print([NewWealthNT / NewSumWealth, NewWealthVI / NewSumWealth, NewWealthTF / NewSumWealth])

# print(TransferNT, TransferVI, TransferTF)

# TransferNT = max((np.linalg.det(Dx)/np.linalg.det(D)),0)
# TransferVI = max((np.linalg.det(Dy)/np.linalg.det(D)),0)
# TransferTF = max((np.linalg.det(Dz)/np.linalg.det(D)),0)

# NewWealthNT = WealthNT + TransferNT
# NewWealthVI = WealthVI + TransferVI
# NewWealthTF = WealthTF + TransferTF
# # print([NewWealthNT, NewWealthVI,NewWealthTF])
# NewSumWealth = NewWealthNT + NewWealthVI + NewWealthTF

# print(TransferNT, TransferVI, TransferTF)
# print([TargetNT, TargetVI, TargetTF])
# print([NewWealthNT / NewSumWealth, NewWealthVI / NewSumWealth, NewWealthTF / NewSumWealth])




