#!/usr/bin/env python3
import pandas as pd
import numpy as np
import balance_sheet as bs
import timeit
from parameters import *

columns = [ 
    # Global variables
    'Gen', 'Price', 'Mismatch', 'Dividends', 'RDividend', 'Volume',
    'Rep', 'Pos+', 'Pos-', 
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
    'PerSpoils', 'NT_DayReturns', 'VI_DayReturns', 'TF_DayReturns', 'AvgDayReturn', 
    # Measures of adaptation
    'CountSelected', 'CountMutated', 'CountCrossed', 'TowardsNT', 'TowardsVI', 'TowardsTF', 'FromNT', 'FromVI', 'FromTF'


    # TODO: add monthly returns back just as exponentiation of daily (because we would not track funds for this)
]
variables = len(columns)

''' We only record results after a year to avoid transient period biases. '''
Barr = max(SHIELD_DURATION, ShieldResults)


def ResultsProcess(pop, spoils, price):

    LongAssets, ShortAssets = 0,0
    NTcount, VIcount, TFcount = 0,0,0
    MeanNT, MeanVI, MeanTF = 0,0,0
    WSNT, WSVI, WSTF = 0,0,0
    NTcash, NTlend, NTloan, NTnav, NTpnl, NTsignal, NTstocks, NTreturn = 0,0,0,0,0,0,0,np.nan
    VIcash, VIlend, VIloan, VInav, VIpnl, VIsignal, VIstocks, VIreturn = 0,0,0,0,0,0,0,np.nan
    TFcash, TFlend, TFloan, TFnav, TFpnl, TFsignal, TFstocks, TFreturn = 0,0,0,0,0,0,0,np.nan


    for ind in pop:

        if ind.asset > 0:
            LongAssets += ind.asset
        if ind.asset < 0:
            ShortAssets += abs(ind.asset)

        if ind.type == 'nt':
            NTcount += 1
            MeanNT += ind[0]
            NTcash += ind.cash
            NTlend += ind.margin
            NTloan += ind.loan
            NTnav += ind.wealth #before, we imposed w>0
            if ind.wealth > 0:
                WSNT += ind.wealth
            NTpnl += ind.profit
            NTsignal += ind[0] * ind.process #already included?
            NTstocks += price * ind.asset
            if ind.prev_wealth != 0:
                NTreturn += ind.DailyReturn

        if ind.type == 'vi':
            VIcount += 1
            MeanVI += ind[0]
            VIcash += ind.cash
            VIlend += ind.margin
            VIloan += ind.loan
            VInav += ind.wealth #before, we imposed w>0
            if ind.wealth > 0:
                WSVI += ind.wealth
            VIpnl += ind.profit
            # VIsignal += ind[0] #double with MeanVI
            VIstocks += price * ind.asset
            if ind.prev_wealth != 0:
                VIreturn += ind.DailyReturn

        if ind.type == 'tf':
            TFcount += 1
            MeanTF += ind[0]
            TFcash += ind.cash
            TFlend += ind.margin
            TFloan += ind.loan
            TFnav += ind.wealth #before, we imposed w>0
            if ind.wealth > 0:
                WSTF += ind.wealth
            TFpnl += ind.profit
            TFsignal += ind.tsv
            TFstocks += price * ind.asset
            if ind.prev_wealth != 0:
                TFreturn += ind.DailyReturn

    if NTcount != 0:
        NTcash = NTcash / NTcount
        NTlend = NTlend / NTcount 
        NTloan = NTloan / NTcount
        NTnav = NTnav / NTcount
        NTpnl = NTpnl / NTcount
        NTstocks = NTstocks / NTcount
        NTreturn = NTreturn / NTcount
        NTsignal = NTsignal / NTcount
        MeanNT = MeanNT / NTcount

    if VIcount != 0:
        VIcash = VIcash / VIcount
        VIlend = VIlend / VIcount 
        VIloan = VIloan / VIcount
        VInav = VInav / VIcount
        VIpnl = VIpnl / VIcount
        VIstocks = VIstocks / VIcount
        VIreturn = VIreturn / VIcount
        MeanVI = MeanVI / VIcount
    
    if TFcount != 0:
        TFcash = TFcash / TFcount
        TFlend = TFlend / TFcount 
        TFloan = TFloan / TFcount
        TFnav = TFnav / TFcount
        TFpnl = TFpnl / TFcount
        TFstocks = TFstocks / TFcount
        TFreturn = TFreturn / TFcount
        TFsignal = TFsignal / TFcount
        MeanTF = MeanTF / TFcount

    if spoils > 0:
        LongAssets += spoils
    if spoils < 0:
        ShortAssets += abs(spoils)

    VIsignal = MeanVI
    
    WSNT_ = (100 * WSNT) / (WSNT + WSVI + WSTF)
    WSVI_ = (100 * WSVI) / (WSNT + WSVI + WSTF)
    WSTF_ = (100 * WSTF) / (WSNT + WSVI + WSTF)
    WSNT = WSNT_
    WSVI = WSVI_
    WSTF = WSTF_
    if abs(100 - (WSNT + WSVI + WSTF)) > 1:
        raise ValueError('Sum of wealth shares superior to 100. ' + str([WSNT + WSVI + WSTF])) 
    if WSNT < 0 or WSNT < 0 or WSNT < 0:
        raise ValueError("Negative wealth share. " + str([WSNT,WSVI,WSTF]))

    ListOutput = [LongAssets, ShortAssets,
        NTcount, VIcount, TFcount, MeanNT, MeanVI, MeanTF, 
        WSNT, WSVI, WSTF,
        NTcash, NTlend, NTloan, NTnav, NTpnl, NTsignal, NTstocks, NTreturn,
        VIcash, VIlend, VIloan, VInav, VIpnl, VIsignal, VIstocks, VIreturn,
        TFcash, TFlend, TFloan, TFnav, TFpnl, TFsignal, TFstocks, TFreturn
        ]

    return ListOutput

def record_results(results, generation, current_price, mismatch, dividend,
    random_dividend, volume, replacements, pop, spoils, asset_supply,
    ReturnsNT, ReturnsVI, ReturnsTF,
    CountSelected, CountMutated, CountCrossed, StratFlow
    ):

    if generation >= Barr:

        ListOutput = ResultsProcess(pop, spoils, price)

        starttime = timeit.default_timer()

        current = generation - Barr

        DailyNTReturns = FillList(GetDayReturn(pop, 'nt'), len(pop))
        ReturnsNT[current, :] = DailyNTReturns

        DailyVIReturns = FillList(GetDayReturn(pop, 'vi'), len(pop))
        ReturnsVI[current, :] = DailyVIReturns

        DailyTFReturns = FillList(GetDayReturn(pop, 'tf'), len(pop))
        ReturnsTF[current, :] = DailyTFReturns

        ''' Global variables '''
        results[current, 0] = generation - Barr 
        results[current, 1] = current_price
        results[current, 2] = mismatch 
        results[current, 3] = dividend
        results[current, 4] = random_dividend
        results[current, 5] = volume
        results[current, 6] = replacements
        results[current, 7] = ListOutput[0]  #bs.count_long_assets(pop, spoils)
        results[current, 8] = ListOutput[1]  #bs.count_short_assets(pop, spoils)


        ''' General ecology variables '''
        results[current, 9] = ListOutput[2]  #bs.count_nt(pop)
        results[current, 10] = ListOutput[3]  #bs.count_vi(pop)
        results[current, 11] = ListOutput[4]  #bs.count_tf(pop)
        results[current, 12] = ListOutput[5]  #bs.mean_nt(pop)
        results[current, 13] = ListOutput[6]  #bs.mean_vi(pop)
        results[current, 14] = ListOutput[7]  #bs.mean_tf(pop)
        results[current, 15] = ListOutput[8]  #bs.WealthShare(pop, 'nt') 
        results[current, 16] = ListOutput[9]  #bs.WealthShare(pop, 'vi') 
        results[current, 17] = ListOutput[10]  #bs.WealthShare(pop, 'tf') 
        
        ''' Noise traders '''
        results[current, 18] = ListOutput[11]  #bs.report_nt_cash(pop)
        results[current, 19] = ListOutput[12]  #bs.report_nt_lending(pop)
        results[current, 20] = ListOutput[13]  #bs.report_nt_loan(pop)
        results[current, 21] = ListOutput[14]  #bs.report_nt_nav(pop, current_price)
        results[current, 22] = ListOutput[15]  #bs.report_nt_pnl(pop)
        results[current, 23] = ListOutput[16]  #bs.report_nt_signal(pop)
        results[current, 24] = ListOutput[17]  #bs.report_nt_stocks(pop, current_price)
        results[current, 25] = ListOutput[18]  #bs.ReportReturn(pop, 'nt')

        ''' Value investors '''
        results[current, 26] = ListOutput[19]  #bs.report_vi_cash(pop)
        results[current, 27] = ListOutput[20]  #bs.report_vi_lending(pop)
        results[current, 28] = ListOutput[21]  #bs.report_vi_loan(pop)
        results[current, 29] = ListOutput[22]  #bs.report_vi_nav(pop, current_price)
        results[current, 30] = ListOutput[23]  #bs.report_vi_pnl(pop)
        results[current, 31] = ListOutput[24]  #bs.report_vi_signal(pop)
        results[current, 32] = ListOutput[25]  #bs.report_vi_stocks(pop, current_price)
        results[current, 33] = ListOutput[26]  #bs.ReportReturn(pop, 'vi')

        ''' Trend followers '''
        results[current, 34] = ListOutput[27]  #bs.report_tf_cash(pop)
        results[current, 35] = ListOutput[28]  #bs.report_tf_lending(pop)
        results[current, 36] = ListOutput[29]  #bs.report_tf_loan(pop)
        results[current, 37] = ListOutput[30]  #bs.report_tf_nav(pop, current_price)
        results[current, 38] = ListOutput[31]  #bs.report_tf_pnl(pop)
        results[current, 39] = ListOutput[32]  #bs.report_tf_signal(pop, price_history)
        results[current, 40] = ListOutput[33]  #bs.report_tf_stocks(pop, current_price)
        results[current, 41] = ListOutput[34]  #bs.ReportReturn(pop, 'tf')

        ''' Additional measures '''
        results[current, 42] = ComputeAvgReturn(results, current, pop)
        results[current, 43] = spoils

        ''' Run time data '''
        results[current, 44] = 0 #timeA
        results[current, 45] = 0 #timeB
        results[current, 46] = 0 #timeC
        results[current, 47] = 0 #timeD
        results[current, 48] = 0 #timeE
        results[current, 49] = 0 #timeF
        timeG = 0 #timeit.default_timer() - starttime
        results[current, 50] = 0 #timeG
        results[current, 51] = 0 #timeA + timeB + timeC + timeD + timeE + timeF + timeG

        ''' More measures '''
        results[current, 52] = abs(100 * spoils / asset_supply)
        results[current, 53] = np.nanmean(DailyNTReturns) 
        results[current, 54] = np.nanmean(DailyVIReturns) 
        results[current, 55] = np.nanmean(DailyTFReturns) 
        results[current, 56] = (results[current, 54] + results[current, 55] + results[current, 56]) / 3

        ''' Measures of adaptation '''
        results[current, 57] = CountSelected
        results[current, 58] = CountMutated
        results[current, 59] = CountCrossed
        results[current, 60] = StratFlow[0]
        results[current, 61] = StratFlow[1]
        results[current, 62] = StratFlow[2]
        results[current, 63] = StratFlow[3]
        results[current, 64] = StratFlow[4]
        results[current, 65] = StratFlow[5]




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
    


