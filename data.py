''' Here we consider the variables we recorded during the run, and we assemble 
them into a coherent dataframe for later statistical and graphical analysis'''

''' We want data on: [TO COMPLETE AS WE GO]

--- General ---
- Generation index
    
--- Economic variables ---
- Price 
- Dividend 
- Random dividend component 


--- Ecology variables ---
- Replacements 

'''

#  One large dataframe with all, or separate? TBD
# We can also adjust the variables order in the columns

import pandas as pd
import numpy as np

def generate_df(generation_history, price_history, mismatch_history, mean_theta, 
                asset_count_history,
                dividend_history, random_dividend_history, 
                size_pos_pos, size_neg_pos, replacements):
    df = pd.DataFrame()
    
    # General variables
    
    df["Gen"] = generation_history
    
    # Economic variables 
    df["Price"] = price_history
    df["Mismatch"] = mismatch_history
    df["LogP"] = np.log10(price_history)
    df["MeanT"] = mean_theta
    df["Q"] = asset_count_history
    df["Div"] = dividend_history
    df["RDiv"] = random_dividend_history
    df["Pos-Pos"] = size_pos_pos
    df["Neg-Pos"] = size_neg_pos
    
    # Ecology variables
    df ["Rep"] = replacements
    
    return df

def theta_stats(pop):
    sum_theta = 0
    for ind in pop:
        sum_theta += ind[0]
    return sum_theta / len(pop)