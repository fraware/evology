#!/usr/bin/env python3
import pandas as pd
import numpy as np
import balance_sheet as bs
import timeit
from parameters import *

columns = [ 
    # Global variables
    'Gen', 'Price', 'Mismatch', 'Dividends', 'RDividend', 'Volume',
    'Rep', 'Pos+', 'Pos-', 'NegW_per',
    # General ecology variables
    'Num_NT', 'Num_VI', 'Num_TF', 'Mean_NT', 'Mean_VI', 'Mean_TF',
    'WShare_NT', 'WShare_VI', 'WShare_TF', 
    # Noise traders
    'NT_cash', 'NT_lending', 'NT_loans', 'NT_nav', 'NT_pnl', 'NT_signal', 
    'NT_stocks', 'NT_returns',
    # Value investors
    'VI_cash', 'VI_lending', 'VI_loans', 'VI_nav', 'VI_pnl', 'VI_signal',
    'VI_stocks', 'VI_returns',
    # Trend followers
    'TF_cash', 'TF_lending', 'TF_loans', 'TF_nav', 'TF_pnl', 'TF_signal',
    'TF_stocks', 'TF_returns',
    # Additional measures
    'MeanReturn', 'Spoils',
    # Run time data
    'TimeA', 'TimeB', 'TimeC', 'TimeD', 'TimeE', 'TimeF', 'TimeG', 'TotalTime',
    # More measures
    'PerSpoils', 'NT_DayReturns', 'VI_DayReturns', 'TF_DayReturns', 'AvgDayReturn'

    # TODO: add monthly returns back just as exponentiation of daily (because we would not track funds for this)
]

variables = len(columns)

def record_results(results, generation, current_price, mismatch, dividend,
    random_dividend, volume, replacements, pop, price_history, spoils, asset_supply,
    timeA, timeB, timeC, timeD, timeE, timeF,
    ReturnsNT, ReturnsVI, ReturnsTF
    ):

    if generation >= SHIELD_DURATION:
        starttime = timeit.default_timer()

        current = generation - SHIELD_DURATION

        DailyNTReturns = FillList(GetDayReturn(pop, 'nt'), len(pop))
        ReturnsNT[current, :] = DailyNTReturns

        DailyVIReturns = FillList(GetDayReturn(pop, 'vi'), len(pop))
        ReturnsVI[current, :] = DailyVIReturns

        DailyTFReturns = FillList(GetDayReturn(pop, 'tf'), len(pop))
        ReturnsTF[current, :] = DailyTFReturns

        ''' Global variables '''
        results[current, 0] = generation - SHIELD_DURATION 
        results[current, 1] = current_price
        results[current, 2] = mismatch 
        results[current, 3] = dividend
        results[current, 4] = random_dividend
        results[current, 5] = volume
        results[current, 6] = replacements
        results[current, 7] = bs.count_long_assets(pop, spoils)
        results[current, 8] = bs.count_short_assets(pop, spoils)
        results[current, 9] = bs.report_negW(pop)


        ''' General ecology variables '''
        results[current, 10] = bs.count_nt(pop)
        results[current, 11] = bs.count_vi(pop)
        results[current, 12] = bs.count_tf(pop)
        results[current, 13] = bs.mean_nt(pop)
        results[current, 14] = bs.mean_vi(pop)
        results[current, 15] = bs.mean_tf(pop)
        results[current, 16] = bs.wealth_share_nt(pop)
        results[current, 17] = bs.wealth_share_vi(pop)
        results[current, 18] = bs.wealth_share_tf(pop)
        


        ''' Noise traders '''
        results[current, 19] = bs.report_nt_cash(pop)
        results[current, 20] = bs.report_nt_lending(pop)
        results[current, 21] = bs.report_nt_loan(pop)
        results[current, 22] = bs.report_nt_nav(pop, current_price)
        results[current, 23] = bs.report_nt_pnl(pop)
        results[current, 24] = bs.report_nt_signal(pop)
        results[current, 25] = bs.report_nt_stocks(pop, current_price)
        results[current, 26] = bs.ReportReturn(pop, 'nt')

        ''' Value investors '''
        results[current, 27] = bs.report_vi_cash(pop)
        results[current, 28] = bs.report_vi_lending(pop)
        results[current, 29] = bs.report_vi_loan(pop)
        results[current, 30] = bs.report_vi_nav(pop, current_price)
        results[current, 31] = bs.report_vi_pnl(pop)
        results[current, 32] = bs.report_vi_signal(pop)
        results[current, 33] = bs.report_vi_stocks(pop, current_price)
        results[current, 34] = bs.ReportReturn(pop, 'vi')

        ''' Trend followers '''
        results[current, 35] = bs.report_tf_cash(pop)
        results[current, 36] = bs.report_tf_lending(pop)
        results[current, 37] = bs.report_tf_loan(pop)
        results[current, 38] = bs.report_tf_nav(pop, current_price)
        results[current, 39] = bs.report_tf_pnl(pop)
        results[current, 40] = bs.report_tf_signal(pop, price_history)
        results[current, 41] = bs.report_tf_stocks(pop, current_price)
        results[current, 42] = bs.ReportReturn(pop, 'tf')

        ''' Additional measures '''
        results[current, 43] = ComputeAvgReturn(results, current, pop)
        results[current, 44] = spoils

        ''' Run time data '''
        results[current, 45] = timeA
        results[current, 46] = timeB
        results[current, 47] = timeC
        results[current, 48] = timeD
        results[current, 49] = timeE
        results[current, 50] = timeF
        timeG = timeit.default_timer() - starttime
        results[current, 51] = timeG
        results[current, 52] = timeA + timeB + timeC + timeD + timeE + timeF + timeG

        ''' More measures '''
        results[current, 53] = abs(100 * spoils / asset_supply)
        results[current, 54] = np.nanmean(DailyNTReturns) 
        results[current, 55] = np.nanmean(DailyVIReturns) 
        results[current, 56] = np.nanmean(DailyTFReturns) 
        results[current, 57] = (results[current, 54] + results[current, 55] + results[current, 56]) / 3





    return results, ReturnsNT, ReturnsVI, ReturnsTF

def GetDayReturn(pop, strat):
    lis = []
    for ind in pop:
        if ind.type == strat:
            lis.append(ind.DailyReturn)
    return lis

def FillList(lis, n):
    while len(lis) < n:
        lis.append(np.nan)
    return lis

def ComputeAvgReturn(results, generation, pop):
    AvgReturn = (results[generation, 10] * results[generation, 26] + results[generation, 11] * results[generation, 34] + results[generation, 12] * results[generation, 42]) / len(pop)
    return AvgReturn

def ComputeAvgMonReturn(results, generation, pop):
    AvgReturn = (results[generation, 10] * results[generation, 54] + results[generation, 11] * results[generation, 55] + results[generation, 12] * results[generation, 56]) / len(pop)
    return AvgReturn
    


