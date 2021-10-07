import pandas as pd
import numpy as np
import balance_sheet as bs

# columns = [
#     "Gen", "Price", "Mismatch", "Val_NT", "Num_TF", "Num_VI", "Num_NT",
#     "Mean_TF", "Mean_VI", "Mean_NT", "Div", "RDiv", "WShare_TF", "WShare_VI",
#     "WShare_NT", "Pos+", "Pos-", "Rep"
# ]

def create_df():
    df = pd.DataFrame(columns = [
    "Gen", "Price", "Mismatch", "Val_NT", "Num_TF", "Num_VI", "Num_NT",
    "Mean_TF", "Mean_VI", "Mean_NT", "Div", "RDiv", "WShare_TF", "WShare_VI",
    "WShare_NT", "Pos+", "Pos-", "Rep"
])
    return df

def update_results(df, generation, current_price, mismatch, pop, dividend, 
        random_dividend, replacements): 
    
    df.loc[len(df.index)] = [generation, current_price, mismatch, 
        round(bs.nt_report(pop),0), bs.count_tf(pop), bs.count_vi(pop), 
        bs.count_nt(pop), bs.mean_tf(pop), bs.mean_vi(pop), bs.mean_nt(pop), 
        dividend, random_dividend, bs.wealth_share_tf(pop), bs.wealth_share_vi(pop),
        bs.wealth_share_nt(pop), bs.count_long_assets(pop), 
        bs.count_short_assets(pop), replacements]
    