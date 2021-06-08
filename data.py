''' Here we consider the variables we recorded during the run, and we assemble 
them into a coherent dataframe for later statistical and graphical analysis'''

''' We want data on:
    
--- Economic variables ---
- Price series

--- Ecology variables ---

'''

#  One large dataframe with all, or separate? TBD
# We can also adjust the variables order in the columns

import pandas as pd

def generate_df(generation_history, price_history, dividend_history, replacements):
    df = pd.DataFrame()
    
    # General variables
    
    df["Gen"] = generation_history
    
    # Economic variables 
    df["Price"] = price_history
    df["Div"] = dividend_history
    
    # Ecology variables
    df ["Rep"] = replacements
    
    return df