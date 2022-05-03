
import pandas as pd
df = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/icml/data/asym_dis_ext.csv")

# For scale = 100, 300 observations out of 5151 will stop at 
# Gen 0.0 because they are at the boundary. This is OK.