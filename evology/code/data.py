import pandas as pd
import numpy as np
import balance_sheet as bs


def create_df():
    df = pd.DataFrame(columns = [
    "Gen", "Price", "Mismatch", "Num_NT", "Num_VI", "Num_TF", 
    "Mean_TF", "Mean_VI", "Mean_NT", "Dividends", "RDiv", "WShare_TF", "WShare_VI",
    "WShare_NT", "Pos+", "Pos-", "Rep",
    'Volume',
    'NT_cash', 'NT_lending', 'NT_loans', 'NT_nav', 'NT_pnl', 'NT_signal', 'NT_stocks', 'NT_returns',
    'VI_cash', 'VI_lending', 'VI_loans', 'VI_nav', 'VI_pnl', 'VI_signal', 'VI_stocks', 'VI_returns',
    'TF_cash', 'TF_lending', 'TF_loans', 'TF_nav', 'TF_pnl', 'TF_signal', 'TF_stocks', 'TF_returns'
])
    return df

def update_results(df, generation, current_price, mismatch, pop, dividend, 
        random_dividend, replacements, volume, price_history): 
    
    df.loc[len(df.index)] = [generation, current_price, mismatch, 
        bs.count_nt(pop), bs.count_vi(pop), bs.count_tf(pop), 
        bs.mean_tf(pop), bs.mean_vi(pop), bs.mean_nt(pop), 
        dividend, random_dividend, bs.wealth_share_tf(pop), bs.wealth_share_vi(pop),
        bs.wealth_share_nt(pop), bs.count_long_assets(pop), 
        bs.count_short_assets(pop), replacements,
        volume,
        bs.report_nt_cash(pop), bs.report_nt_lending(pop), bs.report_nt_loan(pop),
            bs.report_nt_nav(pop, current_price), bs.report_nt_pnl(pop), 
            bs.report_nt_signal(pop), bs.report_nt_stocks(pop, current_price), bs.report_nt_return(pop),
        bs.report_vi_cash(pop), bs.report_vi_lending(pop), bs.report_vi_loan(pop), 
            bs.report_vi_nav(pop, current_price), bs.report_vi_pnl(pop), 
            bs.report_vi_signal(pop), bs.report_vi_stocks(pop, current_price),bs.report_vi_return(pop),
        bs.report_tf_cash(pop), bs.report_tf_lending(pop), bs.report_tf_loan(pop),
            bs.report_tf_nav(pop, current_price), bs.report_tf_pnl(pop), 
            bs.report_tf_signal(pop, price_history), bs.report_tf_stocks(pop, current_price), bs.report_tf_return(pop)
        ]
    
    df.set_index('Gen')
    