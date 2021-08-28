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

def generate_df(generation_history, price_history, mismatch_history, 
                num_tf_history, num_vi_history, num_nt_history, mean_tf_history, mean_vi_history, mean_nt_history, 
                mean_wealth_history,  wealth_tf_history, wealth_vi_history, wealth_nt_history,
                meanFitnessValues, 
                dividend_history, random_dividend_history, 
                replacements):
    df = pd.DataFrame()
    
    # General variables
    
    df["Gen"] = generation_history
    
    # Economic variables 
    df["Price"] = price_history
    df["Mismatch"] = mismatch_history
    df["LogP"] = np.log10(price_history)
    df["Num_TF"] = num_tf_history
    df["Num_VI"] = num_vi_history
    df["Num_NT"] = num_nt_history
    df["Mean_TF"] = mean_tf_history
    df["Mean_VI"] = mean_vi_history
    df["Mean_NT"] = mean_nt_history  
    df["Mean_W"] = mean_wealth_history
    df["Wealth_TF"] = wealth_tf_history
    df["Wealth_VI"] = wealth_vi_history
    df["Wealth_NT"] = wealth_nt_history

    df["MeanF"] = meanFitnessValues
    df["Div"] = dividend_history
    df["RDiv"] = random_dividend_history

    
    # Ecology variables
    df ["Rep"] = replacements


    # Df admin
    df.set_index('Gen')
    
    return df

def theta_stats(pop):
    sum_theta = 0
    for ind in pop:
        sum_theta += ind[0]
    return sum_theta / len(pop)