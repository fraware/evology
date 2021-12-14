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
        if ind.loan > 0: # If the agent has outstanding debt:
            if ind.cash >= ind.loan + 100 * price: # If the agent has enough cash:
                ind.loan = 0
                ind.cash -= ind.loan
            if ind.cash < ind.loan + 100 * price : # If the agent does not have enough cash:
                ind.loan -= ind.cash - 100 * price
                ind.cash = 100 * price
    return ind

def update_margin(pop, current_price):
    for ind in pop:
        ind.cash += ind.margin
        ind.margin = 0
        if ind.asset < 0:
            ind.margin += ind.asset * current_price
            ind.cash -= ind.asset * current_price
        if ind.cash < 0:
            ind.loan += abs(ind.cash)
            ind.cash = 0
    return ind

def UpdatePrevWealth(pop):
    for ind in pop:
        ind.prev_wealth = ind.wealth

def calculate_wealth(pop, current_price):
    for ind in pop:
        ind.wealth = ind.cash + ind.asset * current_price - ind.loan

def DetermineTsvProc(mode, pop, price_history):
    for ind in pop:
        if ind.type == "tf":
            if len(price_history) >= ind[0]:
                ind.tsv = np.log2(price_history[-1]) - np.log2(price_history[-ind[0]])
            elif len(price_history) < ind[0]:
                ind.tsv = 0
        if ind.type == "nt":
            ind.process = abs(ind.process + RHO_NT * (np.log2(MU_NT) - np.log2(ind.process)) + GAMMA_NT * random.normalvariate(0,1))
            if ind.process < 0:
                warnings.warn('Negative process value for NT')



def UpdateFval(pop, dividend_history):
    estimated_daily_div_growth = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1

    for ind in pop: 
        if len(dividend_history) >= 1:
            numerator = (1 + estimated_daily_div_growth) * dividend_history[-1]
        elif len(dividend_history) < 1:
            numerator = (1 + estimated_daily_div_growth) * INITIAL_DIVIDEND

        denuminator = (1 + (AnnualInterestRate + ind.strategy) - DIVIDEND_GROWTH_RATE_G) ** (1/252) - 1
        fval = numerator / denuminator

        if fval < 0:
            warnings.warn('Negative fval found in update_fval.')
    
        if ind.type == 'vi' or ind.type == 'nt':
            ind[0] = fval
    return pop


def DetermineEDF(pop):
    def edf(ind, p):
        if ind.type == "tf":
            return (LeverageTF * ind.wealth / p) * np.tanh(SCALE_TF * ind.tsv) - ind.asset
                
        elif ind.type == "vi":
            try:
                return (LeverageVI * ind.wealth / p) * np.tanh(SCALE_VI * (math.log2(ind[0]) - np.log2(p))) - ind.asset
            except:
                print(p)
                print(ind[0])
                print(math.log2(ind[0]) - math.log2(p))
                raise ValueError('math domain error')

        elif ind.type == "nt":
            try:
                return (LeverageNT * ind.wealth / p) * np.tanh(SCALE_NT * (math.log2(ind[0] * ind.process) - np.log2(p))) - ind.asset
            except:
                print('p, ind, indproc, ind . indproc, log2 of it, math log of it - log p')
                print(p)
                print(ind[0])
                print(ind.process)
                print(ind[0] * ind.process)
                print(np.log2(ind[0] * ind.process))
                print(math.log2(ind[0] * ind.process) - np.log2(p))
                raise ValueError('math domain error in nt edf')

    # Assign this function to be the agent's edf
    for ind in pop:
        ind.edf = edf
    return pop 

def calculate_edv(pop, price):
    total_edv = 0
    for ind in pop:
        ind.edv =  ind.edf(ind, price)
        total_edv += ind.edv
    return pop, total_edv

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
            fval += ind[0] * ind.process
            if fval < 0:
                warnings.warn('Negative NT signal')
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
            fval += (price_history[-1] / price_history[-ind[0]]) - 1
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

# def total_wealth(pop):
#     wealth = 0
#     for ind in pop:
#         if ind.wealth > 0:
#             wealth += ind.wealth
#     return wealth

def TotalWealth(pop):
    Wealth = 0
    for ind in pop:
        if ind.wealth > 0:
            Wealth += ind.wealth
    return Wealth

def WealthShare(pop, strat):
    TotalW = TotalWealth(pop)
    StratWealth = 0
    for ind in pop:
        if ind.type == strat and ind.wealth > 0:
            StratWealth += ind.wealth
    if StratWealth < 0:
        raise ValueError('Negative Strat wealth for type ' + str(strat))
    if TotalW == 0:
        Share = 0
    else:
        Share = 100 * StratWealth / TotalW
    return Share 



def agg_ed(pop, spoils): 
    functions = []
    ToLiquidate = 0

    if spoils > 0:
        ToLiquidate = - min(spoils, LIQUIDATION_ORDER_SIZE )
    elif spoils == 0:
        ToLiquidate = 0
    elif spoils < 0:
        ToLiquidate = min(abs(spoils), LIQUIDATION_ORDER_SIZE)

    def big_edf(price):
        result = ToLiquidate
        for ind in pop:
            if ind.edf(ind, 1) != np.nan:
                result += ind.edf(ind, price)
        return result
    functions.append(big_edf)
    return functions, ToLiquidate


def agg_ed_esl(pop, spoils): 
    functions = []
    ToLiquidate = 0

    if spoils > 0:
        ToLiquidate = - min(spoils, LIQUIDATION_ORDER_SIZE )
    elif spoils == 0:
        ToLiquidate = 0
    elif spoils < 0:
        ToLiquidate = min(abs(spoils), LIQUIDATION_ORDER_SIZE)

    def big_edf(asset_key, price):
        result = ToLiquidate
        for ind in pop:
            if ind.edf(ind, 1) != np.nan:
                result += ind.edf(ind, price)
        return result
    functions.append(big_edf)
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

def ReportReturn(pop, strat):
    num, Total = 0,0
    result = np.nan
    for ind in pop:
        if ind.type == strat and ind.prev_wealth != 0:
            num += 1
            Total += ind.DailyReturn
    if num != 0:
        result = Total / num
    return result
        
def ComputeReturn(pop):
    for ind in pop:
        if ind.prev_wealth > 0:
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

def GetWealth(pop, strat):
    TotalWealth = 0
    for ind in pop:
        if ind.type == strat:
            TotalWealth += ind.wealth
    return TotalWealth

def GetNumber(pop, strat):
    TotalNumber = 0
    for ind in pop:
        if ind.type == strat:
            TotalNumber += 1
    return TotalNumber