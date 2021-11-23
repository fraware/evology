import warnings
import numpy as np
import balance_sheet as bs
from parameters import MAX_ATTEMPTS, SHIELD_DURATION, SHIELD_TOLERANCE
from parameters import RefAssets, RefCash

# def determine_strat_size(pop):
#     size_nt, num_nt = 0, 0
#     size_vi, num_vi = 0, 0
#     size_tf, num_tf = 0, 0 
#     for ind in pop:
#         if ind.type == 'nt':
#             size_nt += ind.wealth
#             num_nt += 1
#         if ind.type == 'vi':
#             size_vi += ind.wealth
#             num_vi += 1
#         if ind.type == 'tf':
#             size_tf += ind.wealth
#             num_tf += 1
#     all_size = size_vi + size_tf + size_nt 
#     if all_size == 0:
#         raise ValueError('All size = 0')

#     current_nt = size_nt / all_size
#     current_vi = size_vi / all_size
#     current_tf = size_tf / all_size
#     currents = [current_nt, current_vi, current_tf]

#     return currents, size_nt, size_vi, size_tf, all_size, num_nt, num_vi, num_tf

# def determine_differences(coordinates, pop):
#     # Determine targets
#     target_nt = coordinates[0]
#     target_vi = coordinates[1]
#     target_tf = coordinates[2]
#     targets = [target_nt, target_vi, target_tf]

#     # Determine size of strategies
#     currents, size_nt, size_vi, size_tf, all_size, num_nt, num_vi, num_tf = determine_strat_size(pop)
#     sizes = [size_nt, size_vi, size_tf]
#     nums = [num_nt, num_vi, num_tf]

#     # print('Currents ' + str(currents))
#     # print('Targets ' + str(targets))

#     differences = [x1 - x2 for (x1, x2) in zip(currents, targets)]
#     return differences, targets, sizes, all_size, nums, currents

# def shield_wealth(generation, pop, coordinates:list, current_price, reset_wealth):

#     if sum(coordinates) > 1.0001:
#         raise ValueError('Sum coordinates higher than 1 ' + sum(coordinates) )

#     if 1 in coordinates: 
#         pass

#     else: 

#         if generation <= SHIELD_DURATION or reset_wealth == True:


#             # WealthShieldSimplified(pop, coordinates)

#             pop_types = ['nt','vi','tf']

#             differences, targets, sizes, all_size, nums, currents = determine_differences(coordinates, pop)
#             # print('Differences')
#             # print(differences)

#             attempt = 0
#             while any([abs(x) >= SHIELD_TOLERANCE for x in differences]) and attempt < MAX_ATTEMPTS:
#                 # We must continue to adjust wealth. 

#                 # Go through items of differences to see which strategies need a correction.
#                 for i in range(len(differences)):
#                     # If the absolute difference is above threshold and inferior, we bump this strategy.
#                     if abs(differences[i]) > SHIELD_TOLERANCE and differences[i] < 0:
#                     # Apply a correction round
#                         # if i == 0 # bumping nt
#                         # if i == 1 #bumping vi
#                         # if i == 2 #bumping tf
#                         amount = (targets[i] * all_size - sizes[i]) / (1 - targets[i])
#                         if amount < 0:
#                             raise ValueError('Negative bump size ' + str(amount))
#                         if nums[i] != 0:
#                             per_capita_amount = amount / nums[i]
#                         elif nums[i] == 0:
#                             per_capita_amount = 0
#                         for ind in pop:
#                             if ind.type == pop_types[i]:
#                                 ind.loan -= per_capita_amount
#                         break
                        

#                 # Recompute wealth, differences and attempts
#                 for ind in pop:
#                     ind.wealth = ind.cash + ind.asset * current_price - ind.loan
#                 differences, targets, sizes, all_size, nums, currents = determine_differences(coordinates, pop)
#                 # print('Current differences: ' + str(differences))
#                 attempt += 1

#             if attempt >= MAX_ATTEMPTS:
#                 print('Wealth adjustement not perfect after MAX_ATTEMPTS. ' + str(currents) + '/' + str(targets))

#         # print('Wealth shield deployed. ' + str(generation))




# def ShieldWealth(pop, coords, generation, reset_wealth):
#     if generation < SHIELD_DURATION or reset_wealth == True:
#         pop = IteratedShield(pop, coords)
#     return pop

# def IteratedShield(pop, coords):
#     diff, WealthSum, WealthNT, WealthVI, WealthTF = DetDifference(pop, coords)
#     attempts = 0
#     while sum([abs(item) for item in diff]) >= SHIELD_TOLERANCE and attempts < MAX_ATTEMPTS: 
#         pop = Shield(pop, coords, WealthSum, WealthNT, WealthVI, WealthTF)
#         diff, WealthSum, WealthNT, WealthVI, WealthTF = DetDifference(pop, coords)
#         attempts += 1
#     if attempts >= MAX_ATTEMPTS and sum([abs(item) for item in diff]) >= SHIELD_TOLERANCE:
#         warnings.warn('IteratedShield imperfect despite Max attempts executed.')
#     return pop

# def DetDifference(pop, coords):
#     TargetNT = coords[0]
#     TargetVI = coords[1]
#     TargetTF = coords[2]

#     WealthNT = bs.GetWealth(pop, 'nt')
#     WealthVI = bs.GetWealth(pop, 'vi')
#     WealthTF = bs.GetWealth(pop, 'tf')
#     WealthSum = WealthNT + WealthVI + WealthTF 

#     diff = [WealthNT / WealthSum - TargetNT, WealthVI / WealthSum - TargetVI, WealthTF/WealthSum - TargetTF]
#     return diff, WealthSum, WealthNT, WealthVI, WealthTF


# def Shield(pop, coords, WealthSum, WealthNT, WealthVI, WealthTF):
    
#     TargetNT = coords[0]
#     TargetVI = coords[1]
#     TargetTF = coords[2]

#     D = np.array([
#     [1-TargetNT,-TargetNT, -TargetNT], 
#     [-TargetVI, 1-TargetVI, -TargetNT],
#     [-TargetTF, -TargetTF, 1-TargetTF]]) 

#     Dx = np.array([
#     [TargetNT * WealthSum - WealthNT,-TargetNT, -TargetNT], 
#     [TargetVI * WealthSum - WealthVI, 1-TargetVI, -TargetNT],
#     [TargetTF * WealthSum - WealthTF, -TargetTF, 1-TargetTF]]) 

#     Dy = np.array([
#     [1-TargetNT, TargetNT * WealthSum - WealthNT, -TargetNT], 
#     [-TargetVI, TargetVI * WealthSum - WealthVI, -TargetNT],
#     [-TargetTF, TargetTF * WealthSum - WealthTF, 1-TargetTF]]) 

#     Dz = np.array([
#     [1-TargetNT, -TargetNT, TargetNT * WealthSum - WealthNT], 
#     [-TargetVI, 1-TargetVI, TargetVI * WealthSum - WealthVI],
#     [-TargetTF, -TargetTF, TargetTF * WealthSum - WealthTF]]) 

#     TransferNT = max((np.linalg.det(Dx)/np.linalg.det(D)),0)
#     TransferVI = max((np.linalg.det(Dy)/np.linalg.det(D)),0)
#     TransferTF = max((np.linalg.det(Dz)/np.linalg.det(D)),0)

#     NumNT = bs.GetNumber(pop, 'nt')
#     NumVI = bs.GetNumber(pop, 'vi')
#     NumTF = bs.GetNumber(pop, 'tf')

#     PcTransferNT = TransferNT / NumNT
#     PcTransferVI = TransferVI / NumVI
#     PcTransferTF = TransferTF / NumTF

#     if PcTransferNT < 0 or PcTransferNT < 0 or PcTransferTF < 0:
#         raise ValueError('Negative PcTransfer')

#     for ind in pop:
#         if ind.type =='nt':
#             ind.loan -= PcTransferNT
#         if ind.type == 'vi':
#             ind.loan -= PcTransferVI
#         if ind.type == 'tf':
#             ind.loan -= PcTransferTF

#     return pop





def WealthReset(pop, WealthCoords, generation, ResetWealth, price):

    if generation <= SHIELD_DURATION:
        OperateReset(pop, WealthCoords, price)
    else: 
        if ResetWealth == True:
            OperateReset(pop, WealthCoords, price)

    ''' optional bit just to check 
    wealthNT, wealthVI, wealthTF = 0,0,0
    for ind in pop:
        if ind.type == 'nt':
            wealthNT += ind.wealth
        if ind.type == 'vi':
            wealthVI += ind.wealth
        if ind.type == 'tf':
            wealthTF += ind.wealth
    totalW = wealthTF + wealthNT + wealthVI
    print('Current factors')
    print([wealthNT/totalW, wealthVI/totalW,wealthTF/totalW])
    '''

def OperateReset(pop, WealthCoords, price):
        # Determine total and strategy assets and cash
    TotalAsset, TotalCash = len(pop) * RefAssets, len(pop) * RefCash
    ShareNT, ShareVI, ShareTF = WealthCoords[0], WealthCoords[1], WealthCoords[2]

    NTAsset, NTCash = ShareNT * TotalAsset, ShareNT * TotalCash
    VIAsset, VICash = ShareVI * TotalAsset, ShareVI * TotalCash
    TFAsset, TFCash = ShareTF * TotalAsset, ShareTF * TotalCash

    NumNT = bs.GetNumber(pop, 'nt')
    NumVI = bs.GetNumber(pop, 'vi')
    NumTF = bs.GetNumber(pop, 'tf')

    PcNTCash = NTCash / NumNT
    PcVICash = VICash / NumVI
    PcTFCash = TFCash / NumTF

    PcNTAsset = NTAsset / NumNT
    PcVIAsset = VIAsset / NumVI
    PcTFAsset = TFAsset / NumTF

    for ind in pop:
        if ind.type == 'nt':
            ind.cash = PcNTCash 
            ind.asset = PcNTAsset
            ind.loan = 0
        if ind.type == 'vi':
            ind.cash = PcVICash 
            ind.asset = PcVIAsset
            ind.loan = 0
        if ind.type == 'tf':
            ind.cash = PcTFCash 
            ind.asset = PcTFAsset
            ind.loan = 0
        ind.wealth = ind.cash + ind.asset * price - ind.loan

