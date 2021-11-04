#!/usr/bin/env python3
import pandas as pd
import numpy as np
import balance_sheet as bs
import timeit




# def create_df():
#     df = pd.DataFrame(columns = [
#     "Gen", "Price", "Mismatch", "Num_NT", "Num_VI", "Num_TF", 
#     "Mean_TF", "Mean_VI", "Mean_NT", "Dividends", "RDiv", "WShare_TF", "WShare_VI",
#     "WShare_NT", "Pos+", "Pos-", "Rep", "NegW_per",
#     'Volume',
#     'NT_cash', 'NT_lending', 'NT_loans', 'NT_nav', 'NT_pnl', 'NT_signal', 'NT_stocks', 'NT_returns',
#     'VI_cash', 'VI_lending', 'VI_loans', 'VI_nav', 'VI_pnl', 'VI_signal', 'VI_stocks', 'VI_returns',
#     'TF_cash', 'TF_lending', 'TF_loans', 'TF_nav', 'TF_pnl', 'TF_signal', 'TF_stocks', 'TF_returns'
# ])
#     return df

# def update_results(df, generation, current_price, mismatch, pop, dividend, 
#         random_dividend, replacements, volume, price_history): 
    
#     df.loc[len(df.index)] = [generation, current_price, mismatch, 
#         bs.count_nt(pop), bs.count_vi(pop), bs.count_tf(pop), 
#         bs.mean_tf(pop), bs.mean_vi(pop), bs.mean_nt(pop), 
#         dividend, random_dividend, bs.wealth_share_tf(pop), bs.wealth_share_vi(pop),
#         bs.wealth_share_nt(pop), bs.count_long_assets(pop), 
#         bs.count_short_assets(pop), replacements, bs.report_negW(pop),
#         volume,
#         bs.report_nt_cash(pop), bs.report_nt_lending(pop), bs.report_nt_loan(pop),
#             bs.report_nt_nav(pop, current_price), bs.report_nt_pnl(pop), 
#             bs.report_nt_signal(pop), bs.report_nt_stocks(pop, current_price), bs.report_nt_return(pop),
#         bs.report_vi_cash(pop), bs.report_vi_lending(pop), bs.report_vi_loan(pop), 
#             bs.report_vi_nav(pop, current_price), bs.report_vi_pnl(pop), 
#             bs.report_vi_signal(pop), bs.report_vi_stocks(pop, current_price),bs.report_vi_return(pop),
#         bs.report_tf_cash(pop), bs.report_tf_lending(pop), bs.report_tf_loan(pop),
#             bs.report_tf_nav(pop, current_price), bs.report_tf_pnl(pop), 
#             bs.report_tf_signal(pop, price_history), bs.report_tf_stocks(pop, current_price), bs.report_tf_return(pop)
#         ]
    
#     df.set_index('Gen')


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
    'TimeA', 'TimeB', 'TimeC', 'TimeD', 'TimeE', 'TimeF', 'TimeG', 'TotalTime'
]

variables = len(columns)

def record_results(results, generation, current_price, mismatch, dividend,
    random_dividend, volume, replacements, pop, price_history, spoils,
    timeA, timeB, timeC, timeD, timeE, timeF
    ):
    starttime = timeit.default_timer()


    ''' Global variables '''
    results[generation, 0] = generation 
    results[generation, 1] = current_price
    results[generation, 2] = mismatch 
    results[generation, 3] = dividend
    results[generation, 4] = random_dividend
    results[generation, 5] = volume
    results[generation, 6] = replacements
    results[generation, 7] = bs.count_long_assets(pop)
    results[generation, 8] = bs.count_short_assets(pop)
    results[generation, 9] = bs.report_negW(pop)


    ''' General ecology variables '''
    results[generation, 10] = bs.count_nt(pop)
    results[generation, 11] = bs.count_vi(pop)
    results[generation, 12] = bs.count_tf(pop)
    results[generation, 13] = bs.mean_nt(pop)
    results[generation, 14] = bs.mean_vi(pop)
    results[generation, 15] = bs.mean_tf(pop)
    results[generation, 16] = bs.wealth_share_nt(pop)
    results[generation, 17] = bs.wealth_share_vi(pop)
    results[generation, 18] = bs.wealth_share_tf(pop)
    


    ''' Noise traders '''
    results[generation, 19] = bs.report_nt_cash(pop)
    results[generation, 20] = bs.report_nt_lending(pop)
    results[generation, 21] = bs.report_nt_loan(pop)
    results[generation, 22] = bs.report_nt_nav(pop, current_price)
    results[generation, 23] = bs.report_nt_pnl(pop)
    results[generation, 24] = bs.report_nt_signal(pop)
    results[generation, 25] = bs.report_nt_stocks(pop, current_price)
    results[generation, 26] = bs.report_nt_return(pop)

    ''' Value investors '''
    results[generation, 27] = bs.report_vi_cash(pop)
    results[generation, 28] = bs.report_vi_lending(pop)
    results[generation, 29] = bs.report_vi_loan(pop)
    results[generation, 30] = bs.report_vi_nav(pop, current_price)
    results[generation, 31] = bs.report_vi_pnl(pop)
    results[generation, 32] = bs.report_vi_signal(pop)
    results[generation, 33] = bs.report_vi_stocks(pop, current_price)
    results[generation, 34] = bs.report_vi_return(pop)

    ''' Trend followers '''
    results[generation, 35] = bs.report_tf_cash(pop)
    results[generation, 36] = bs.report_tf_lending(pop)
    results[generation, 37] = bs.report_tf_loan(pop)
    results[generation, 38] = bs.report_tf_nav(pop, current_price)
    results[generation, 39] = bs.report_tf_pnl(pop)
    results[generation, 40] = bs.report_tf_signal(pop, price_history)
    results[generation, 41] = bs.report_tf_stocks(pop, current_price)
    results[generation, 42] = bs.report_tf_return(pop)

    ''' Additional measures '''
    results[generation, 43] = ComputeAvgReturn(results, generation, pop)
    results[generation, 44] = spoils

    ''' Run time data '''
    results[generation, 45] = timeA
    results[generation, 46] = timeB
    results[generation, 47] = timeC
    results[generation, 48] = timeD
    results[generation, 49] = timeE
    results[generation, 50] = timeF
    timeG = timeit.default_timer() - starttime
    results[generation, 51] = timeG
    results[generation, 52] = timeA + timeB + timeC + timeD + timeE + timeF + timeG


    return results

def ComputeAvgReturn(results, generation, pop):
    AvgReturn = (results[generation, 10] * results[generation, 26] + results[generation, 11] * results[generation, 34] + results[generation, 12] * results[generation, 42]) / len(pop)
    return AvgReturn
    


