from operator import index
import numpy as np
from numpy.core.fromnumeric import mean
from parameters import *
from market import *
import inspect
import math
import warnings
import random
import timeit

def clear_debt(pop, price):
    for ind in pop:
        # Attempt to clear debt
        if ind.loan > 0: # If the agent has outstanding debt:
            if ind.cash >= ind.loan + 100 * price: # If the agent has enough cash:
                ind.loan = 0
                ind.cash -= ind.loan
                # print("Debt clear succesful for " + str(ind.type))
            if ind.cash < ind.loan + 100 * price : # If the agent does not have enough cash:
                ind.loan -= ind.cash - 100 * price
                ind.cash = 100 * price
                # print("Debt clear unsuccesful for " + str(ind.type))
    return ind

def update_margin(pop, current_price):
    for ind in pop:
        # If we have a short position, update the margin
        if ind.asset < 0:
            margin_objective = abs(ind.asset) * current_price # Margin amount to cover short position at current price.
            if margin_objective > ind.margin: # If our current margin is not enough:
                ind.cash -= margin_objective - ind.margin 
                ind.margin = margin_objective
                if ind.cash < 0:
                    ind.loan += abs(ind.cash)
                    ind.cash = 0
            # If our margin is too high, gain the excedent as cash.
            elif margin_objective < ind.margin:
                ind.cash += ind.margin - margin_objective
                ind.margin = margin_objective
        if ind.asset >= 0 and ind.margin > 0:
            ind.cash += ind.margin
            ind.margin = 0

    return ind

def calculate_wealth(pop, current_price):
    timeA1, timeA2 = 0, 0
    for ind in pop:
        # Update wealth

        # starttime1 = timeit.default_timer()

        ind.prev_wealth = ind.wealth
        ind.wealth = ind.cash + ind.asset * current_price - ind.loan

        # timeA1 += timeit.default_timer() - starttime1
        
        # del ind.MonWealth[-1]
        # ind.MonWealth.insert(0, ind.wealth)

        # starttime2 = timeit.default_timer()
        # ind.MonWealth = np.insert(ind.MonWealth, 0, ind.wealth)[:-1]
        # timeA2 += timeit.default_timer() - starttime2
        
        # if len(ind.MonWealth) != 21:
        #     raise ValueError('Wealth monthly history len is not equal to 21 ' + str(ind.MonWealth))
        # The amount due by short selling is equally captured by the margin, hence does not appear here.
    ''' Iteration time    
    # print('Time A1 A2')
    # print(timeA1 * 100000)
    # print(timeA2 * 100000) ''' 

    return ind

def determine_tsv_proc(mode, pop, price_history):
    # For TFs to have a TSV before determining their edf.
    if mode == 'between':
        if len(price_history) >= 2:
            tf_basic = np.log2(price_history[-1]) - np.log2(price_history[-2])
            # tf_basic = price_history[-1] - price_history[-2]
        else: 
            tf_basic = 0
        for ind in pop:
            if ind.type == "tf":   
                ind.tsv = tf_basic
            if ind.type == "nt":
                ind.process = abs(ind.process + RHO_NT * (np.log2(MU_NT) - np.log2(abs(ind.process))) + GAMMA_NT * random.normalvariate(0,1))



    else:
        for ind in pop:
            if ind.type == "tf":
                if len(price_history) >= ind[0]:
                    ind.tsv = np.log2(price_history[-1]) - np.log2(price_history[-ind[0]])
                elif len(price_history) < ind[0]:
                    ind.tsv = 0
            if ind.type == "nt":
                ind.process = abs(ind.process + RHO_NT * (np.log2(MU_NT) - np.log2(abs(ind.process))) + GAMMA_NT * random.normalvariate(0,1))


def update_fval(pop, extended_dividend_history):
    estimated_daily_div_growth = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1
    # annualised_estimated_daily_div_growth = (1 + estimated_daily_div_growth) ** 252 - 1
    numerator = (1 + estimated_daily_div_growth) * extended_dividend_history[-1]
    denuminator = (1 + EQUITY_COST - DIVIDEND_GROWTH_RATE_G) ** (1/252) - 1
    fval = numerator / denuminator

    if fval < 0:
        warnings.warn('Negative fval found in update_fval')

    for ind in pop: 
        if ind.type == 'vi' or ind.type == 'nt':
            ind[0] = fval
    return pop


def determine_edf(pop):

    # Define a function wrt agent type
    def edf(ind, p):
        if ind.type == "tf":
            try:
                return (LeverageTF * ind.wealth / p) * (np.tanh(SCALE_TF * ind.tsv + 0.5)) - ind.asset
            except: 
                warnings.warn('TF Error')
                return (LeverageTF * ind.wealth / p) * (np.tanh(0.5)) - ind.asset
                # return (LeverageTF * ind.wealth / p) * (np.tanh(ind.tsv + 0.5)) - ind.asset
                

        elif ind.type == "vi":
            try:
                return (LeverageVI * ind.wealth / p) * (np.tanh(SCALE_VI * (math.log2(ind[0]) - math.log2(p)) + 0.5)) - ind.asset
            except:
                warnings.warn('VI Error')
                return (LeverageVI * ind.wealth / p) * (0.5) - ind.asset
                # return (LeverageVI * ind.wealth / p) * (ind.tsv + 0.5) - ind.asset



        elif ind.type == "nt":
            try:
                return (LeverageNT * ind.wealth / p) * (np.tanh(SCALE_NT * (math.log2(ind[0] * abs(ind.process)) - math.log2(p)) + 0.5)) - ind.asset
            except:
                warnings.warn('NT Error')
                return (LeverageNT * ind.wealth / p) * (0.5) - ind.asset
                # return (LeverageNT * ind.wealth / p) * (ind.tsv + 0.5) - ind.asset
                

    # Assign this function to be the agent's edf
    for ind in pop:
        ind.edf = edf
    return pop 

''' removing logs did not work
def determine_edf(pop):
    def edf(ind, p):
        if ind.type == "tf":
            return (LeverageTF * ind.wealth / p) * (np.tanh(SCALE_TF * ind.tsv + 0.5)) - ind.asset

        elif ind.type == "vi":
            return (LeverageVI * ind.wealth / p) * (np.tanh(SCALE_VI * (ind[0] - p) + 0.5)) - ind.asset

        elif ind.type == "nt":
            return (LeverageNT * ind.wealth / p) * (np.tanh((SCALE_NT * (ind[0] * abs(ind.process)) - p) + 0.5)) - ind.asset


    for ind in pop:
        ind.edf = edf
    return pop '''

def calculate_edv(pop, price):
    total_edv = 0
    for ind in pop:
        ind.edv =  ind.edf(ind, price)
        total_edv += ind.edv
    return pop, total_edv

# def calculate_total_edv(pop):
#     total = 0
#     for ind in pop:
#         total += ind.edv
#     return total

def count_pop_long_assets(pop):
    count = 0
    for ind in pop:
        count += ind.asset
    return count

def count_long_assets(pop, spoils):
    count = 0
    for ind in pop:
        count += ind.asset
    count += spoils
    return count

def count_short_assets(pop, spoils):
    count = 0
    for ind in pop:
        if ind.asset < 0:
            count += abs(ind.asset)
    if spoils < 0:
        count += abs(spoils)
    return count

def count_pop_short_assets(pop):
    count = 0
    for ind in pop:
        if ind.asset < 0:
            count += abs(ind.asset)
    return count



def earnings(pop, prev_dividend):
    dividend, random_dividend = draw_dividend(prev_dividend)
    for ind in pop:
        div_asset = ind.asset * dividend # Determine gain from dividends
        interest_cash = ind.cash * INTEREST_RATE # Determine gain from interest
        ind.cash += REINVESTMENT_RATE * (div_asset + interest_cash) # Apply reinvestment

    return pop, dividend, random_dividend


def pop_report(pop):
    for ind in pop:
        agent_report (ind)

def agent_report(ind):
    if ind.type == "tf":
        print("TF agent - " + str(round(ind[0],2)) + ", Cash " + str(int(ind.cash)) + ", Asset_Long " + str(int(ind.asset)) + ", Wealth " + str(int(ind.wealth)) + ", TS " + str(round(ind.tsv,2)) + ", EV " + str(int(ind.edv)) + ", Margin " + str(int(ind.margin)) + ", Loan " + str(int(ind.loan)) )# + ", Profit " + str(int(ind.profit)) + ", Fitness " + str(ind.fitness))
    if ind.type == "vi":
        print("VI agent - " + str(round(ind[0],2)) + ", Cash " + str(int(ind.cash)) + ", Asset_Long " + str(int(ind.asset)) + ", Wealth " + str(int(ind.wealth)) + ", TS " + str(round(ind.tsv,2)) + ", EV " + str(int(ind.edv)) + ", Margin " + str(int(ind.margin)) + ", Loan " + str(int(ind.loan)) )# )#", Profit " + str(int(ind.profit)) + ", Fitness " + str(ind.fitness))
    if ind.type == "nt":
        print("NT agent - " + str(round(ind[0],2)) + ", Cash " + str(int(ind.cash)) + ", Asset_Long " + str(int(ind.asset)) + ", Wealth " + str(int(ind.wealth)) + ", TS " + str(round(ind.tsv,2)) + ", EV " + str(int(ind.edv)) + ", Margin " + str(int(ind.margin)) + ", Loan " + str(int(ind.loan)) + ', Process: ' + str(round(ind.process,2)))# )#", Profit " + str(int(ind.profit)) + ", Fitness " + str(ind.fitness))
  
def report_nt_signal(pop):
    fval = 0
    num = 0
    fval_round = 0
    for ind in pop:
        if ind.type == "nt":
            fval += ind[0] * abs(ind.process)
            if fval < 0:
                raise ValueError('Negative NT signal')
            num += 1
    if num != 0:
        fval_round = fval/num
    return fval_round

def report_vi_signal(pop):
    fval = 0
    num = 0
    fval_round = 0
    for ind in pop:
        if ind.type == "vi":
            fval += ind[0]
            num += 1
    if num != 0:
        fval_round = fval/num
    return fval_round

def report_tf_signal(pop, price_history):
    fval = 0
    num = 0
    fval_round = 0

    for ind in pop:
        if len(price_history) > ind[0] and ind.type == 'tf':
            fval += price_history[-1] / price_history[-ind[0]] - 1
            num += 1
    if num != 0:
        fval_round = fval/num
    return fval_round

def calculate_tsv(pop, price, price_history):

    if price < 0:
        warnings.warn('Negative price '+ str(price) )

    for ind in pop:
        if ind.type == 'vi':
            ind.tsv = np.log2(ind[0]) - np.log2(price)
        if ind.type == 'nt':
            ind.tsv = np.log2(ind[0] * abs(ind.process)) - np.log2(price)
    return ind



def count_tf(pop):
    count = 0
    for ind in pop:
        if ind.type == "tf":
            count += 1
    return count


def count_vi(pop):
    count = 0
    for ind in pop:
        if ind.type == "vi":
            count += 1
    return count


def count_nt(pop):
    count = 0
    for ind in pop:
        if ind.type == "nt":
            count += 1
    return count

def mean_tf(pop):
    total = 0
    mean = 0
    result = 0
    for ind in pop:
        if ind.type == "tf":
            total += 1
            mean += ind[0]
    if total != 0:
        result = mean/total
    return result

def mean_vi(pop):
    total = 0
    mean = 0
    result = 0
    for ind in pop:
        if ind.type == "vi":
            total += 1
            mean += ind[0]
    if total != 0:
        result = mean/total
    return result

def mean_nt(pop):
    total = 0
    mean = 0
    result = 0
    for ind in pop:
        if ind.type == "nt":
            total += 1
            mean += ind[0]
    if total != 0:
        result = mean/total
    return result

def total_wealth(pop):
    wealth = 0
    for ind in pop:
        if ind.wealth > 0:
            wealth += ind.wealth
    return wealth

def wealth_share_tf(pop):
    wealth_tf = 0
    for ind in pop:
        if ind.type == "tf" and ind.wealth > 0:
            wealth_tf += ind.wealth

    if 100 * wealth_tf / total_wealth(pop) > 100.01:
        for ind in pop:
            print(ind.type)
            print(ind.wealth)
        print(100 * wealth_tf / total_wealth(pop))
        print(total_wealth(pop))
        raise ValueError("Wealth share TF superior to 100" + str(wealth_tf) + " // " + str(total_wealth(pop)))
  
    if 100 * wealth_tf / total_wealth(pop) < -0.01:
        raise ValueError("Wealth share TF negative" + str(wealth_tf) + " // " + str(total_wealth(pop)))
    return 100 * wealth_tf / total_wealth(pop)

def wealth_share_vi(pop):
    wealth_vi = 0
    for ind in pop:
        if ind.type == "vi" and ind.wealth > 0:
            wealth_vi += ind.wealth
    if 100 * wealth_vi / total_wealth(pop) > 100.01:
        for ind in pop:
            print(ind.type)
            print(ind.wealth)
        print(100 * wealth_vi / total_wealth(pop))
        print(total_wealth(pop))
        raise ValueError("Wealth share VI superior to 100" + str(wealth_vi) + " // " + str(total_wealth(pop)))
    if 100 * wealth_vi / total_wealth(pop) < -0.01:
        raise ValueError("Wealth share VI negative" + str(wealth_vi) + " // " + str(total_wealth(pop)))

    return 100 * wealth_vi / total_wealth(pop)

def wealth_share_nt(pop):
    wealth_nt = 0
    for ind in pop:
        if ind.type == "nt" and ind.wealth > 0:
            wealth_nt += ind.wealth

    if 100 * wealth_nt / total_wealth(pop) > 100.01:
        for ind in pop:
            print(ind.type)
            print(ind.wealth)
        print(100 * wealth_nt / total_wealth(pop))
        print(total_wealth(pop))
        raise ValueError("Wealth share NT superior to 100" + str(wealth_nt) + " // " + str(total_wealth(pop)))
    if 100 * wealth_nt / total_wealth(pop) < -0.01:
        raise ValueError("Wealth share NT negative" + str(wealth_nt) + " // " + str(total_wealth(pop)))
    return 100 * wealth_nt / total_wealth(pop)


def agg_ed(pop, spoils): 
    # functions = []
    ToLiquidate = 0

    ###
    # edf_functions = np.empty(len(pop))
    edf_functions = []
    for i, ind in enumerate(pop):
        def ind_edf(price):
            return ind.edf(ind, price)
        edf_functions.append(ind_edf)
    ###

    if spoils > 0:
        ToLiquidate = - min(spoils, LIQUIDATION_ORDER_SIZE )
    elif spoils == 0:
        ToLiquidate = 0
    elif spoils < 0:
        ToLiquidate = min(abs(spoils), LIQUIDATION_ORDER_SIZE)

    def big_edf(price):
        result = ToLiquidate
        for ind in pop:
            result += ind.edf(ind, price)
        return result

    return big_edf, ToLiquidate


def agg_ed_esl(pop, spoils): 
    functions = []
    ToLiquidate = 0

    if spoils == 0:
        def big_edf(asset_key, price):
        # def big_edf(price):
            result = 0
            for ind in pop:
                result += ind.edf(ind, price)
            return result

    if spoils > 0:
        ToLiquidate = min(spoils, LIQUIDATION_ORDER_SIZE )
        # Spoils are positive. We want to sell some long shares in the market. Hence AdminEDV = -TL.
        def big_edf(asset_key, price):
        # def big_edf(price):
            result = - ToLiquidate
            for ind in pop:
                result += ind.edf(ind, price)
            return result

    if spoils < 0:
        ToLiquidate = min(abs(spoils), LIQUIDATION_ORDER_SIZE)
        # Spoils are negative. We want to buy some long shares in the market to close shorts. Hence AdminEDV = +TL.
        def big_edf(asset_key, price):
        # def big_edf(price):
            result = ToLiquidate
            for ind in pop:
                result += ind.edf(ind, price)
            return result
    functions.append(big_edf)

    # print('Spoils is ' + str(spoils))
    # print('Liquidation today is ' +str(ToLiquidate))

    return functions, ToLiquidate



def report_nt_cash(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.cash
    if num != 0:
        cash = total / num
    return cash

def report_vi_cash(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.cash
    if num != 0:
        cash = total / num
    return cash

def report_tf_cash(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.cash
    if num != 0:
        cash = total / num
    return cash

def report_nt_lending(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.margin
    if num != 0:
        cash = total / num
    return cash

def report_vi_lending(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.margin
    if num != 0:
        cash = total / num
    return cash

def report_tf_lending(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.margin
    if num != 0:
        cash = total / num
    return cash
    
def report_nt_loan(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.loan
    if num != 0:
        cash = total / num
    return cash

def report_vi_loan(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.loan
    if num != 0:
        cash = total / num
    return cash

def report_tf_loan(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.loan
    if num != 0:
        cash = total / num
    return cash

def report_nt_nav(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt' and ind.wealth > 0:
            num += 1
            total += ind.wealth
    if num != 0:
        cash = total / num
    return cash

def report_vi_nav(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi' and ind.wealth > 0:
            num += 1
            total += ind.wealth
    if num != 0:
        cash = total / num
    return cash

def report_tf_nav(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf' and ind.wealth > 0:
            num += 1
            total += ind.wealth
    if num != 0:
        cash = total / num
    return cash

def report_nt_pnl(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.profit
    if num != 0:
        cash = total / num
    return cash

def report_vi_pnl(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.profit
    if num != 0:
        cash = total / num
    return cash

def report_tf_pnl(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.profit
    if num != 0:
        cash = total / num
    return cash

def report_nt_stocks(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt' and ind.asset > 0:
            num += 1
            total += ind.asset * price
    if num != 0:
        cash = total / num
    return cash

def report_vi_stocks(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi' and ind.asset > 0:
            num += 1
            total += ind.asset * price
    if num != 0:
        cash = total / num
    return cash

def report_tf_stocks(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf' and ind.asset > 0:
            num += 1
            total += ind.asset * price
    if num != 0:
        cash = total / num
    return cash

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
#     return differences, targets, sizes, all_size, nums 

# def DetRatio(x,y):
#     return np.linalg.det(x)/np.linalg.det(y)

# def WealthShieldSimplified(pop, coordinates):
#     currents, WealthNT, WealthVI, WealthTF, all_size, NumNT, NumVI, NumTF = determine_strat_size(pop)

#     TargetNT = coordinates[0]
#     TargetVI = coordinates[1]
#     TargetTF = coordinates[2]

#     WealthSum = WealthNT + WealthVI + WealthTF 

#     if TargetTF + TargetVI + TargetNT != 1:
#         raise ValueError('Target coordinates do not sum to 1.')

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

#     TransferNT = DetRatio(Dx,D) 
#     TransferVI = DetRatio(Dy,D)
#     TransferTF = DetRatio(Dz,D)

#     PcTransferNT = TransferNT / NumNT
#     PcTransferVI = TransferVI / NumVI
#     PcTransferTF = TransferTF / NumTF

#     for ind in pop:
#         if ind.type == 'nt':
#             ind.loan -= PcTransferNT
#         if ind.type == 'vi':
#             ind.loan -= PcTransferVI
#         if ind.type == 'tf':
#             ind.loan -= PcTransferTF

# def shield_wealth(generation, pop, coordinates:list, current_price, reset_wealth):

#     if sum(coordinates) > 1.0001:
#         raise ValueError('Sum coordinates higher than 1 ' + sum(coordinates) )

#     if 1 in coordinates: 
#         pass

#     else: 

#         if generation <= SHIELD_DURATION or reset_wealth == True:


#             # WealthShieldSimplified(pop, coordinates)

#             pop_types = ['nt','vi','tf']

#             differences, targets, sizes, all_size, nums = determine_differences(coordinates, pop)
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
#                 calculate_wealth(pop, current_price) # Compute agents' wealth
#                 differences, targets, sizes, all_size, nums = determine_differences(coordinates, pop)
#                 # print('Current differences: ' + str(differences))
#                 attempt += 1

#             if attempt >= MAX_ATTEMPTS:
#                 print('Wealth adjustement not perfect after MAX_ATTEMPTS.')

#         # print('Wealth shield deployed. ' + str(generation))
            


def report_nt_return(pop):
    num = 0
    returns = np.nan
    sum_returns = 0
    for ind in pop:
        if ind.type == 'nt' and ind.prev_wealth != 0:
            num += 1
            sum_returns += ind.wealth / ind.prev_wealth
    if num != 0:
        returns = sum_returns / num - 1
    return returns

def report_vi_return(pop):
    num = 0
    returns = np.nan
    sum_returns = 0
    for ind in pop:
        if ind.type == 'vi' and ind.prev_wealth != 0:
            num += 1
            sum_returns += ind.wealth / ind.prev_wealth
    if num != 0:
        returns = sum_returns / num - 1
    return returns

def report_tf_return(pop):
    num = 0
    returns = np.nan
    sum_returns = 0
    for ind in pop:
        if ind.type == 'tf' and ind.prev_wealth != 0:
            num += 1
            sum_returns += ind.wealth / ind.prev_wealth
    if num != 0:
        returns = sum_returns / num - 1
    return returns

        
def ComputeReturn(pop):
    for ind in pop:
        if ind.prev_wealth != 0:
            ind.DailyReturn = (ind.wealth / ind.prev_wealth) - 1
        else:
            ind.DailyReturn = np.nan

def update_profit(pop):
    for ind in pop:
        ind.profit = ind.wealth - ind.prev_wealth

        
def report_types(pop):
    num_tf = 0
    num_vi = 0
    num_nt = 0
    for ind in pop:
        if ind.type == 'tf':
            num_tf += 1
        if ind.type == 'vi':
            num_vi += 1
        if ind.type == 'nt':
            num_nt += 1
    print("TF: " + str(num_tf) + ', VI: ' + str(num_vi) + ', NT: ' + str(num_nt)) 

def report_negW(pop):
    count_neg = 0
    for ind in pop:
        if ind.wealth <= 0:
            count_neg += 1
    prop = 100 * count_neg / len(pop)
    return prop


def GetWealth(pop, type):
    TotalWealth = 0
    for ind in pop:
        if ind.type == type:
            TotalWealth += ind.wealth
    return TotalWealth

def GetNumber(pop, type):
    TotalNumber = 0
    for ind in pop:
        if ind.type == type:
            TotalNumber += 1
    return TotalNumber