import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Import the data
df_nl = pd.read_csv("data/test_data.csv")
print(df_nl)

# Basic plots

df_nl.plot(x="Gen", y = ["Price"],
        kind="line", figsize=(15, 6))
plt.show()

df_nl.plot(x="Gen", y = ["Div"],
        kind="line", figsize=(15, 6))
plt.show()

df_nl.plot(x="Gen", y = ["Num_TF", "Num_VI", "Num_NT"],
        kind="line", figsize=(15, 6))
plt.show()

df_nl.plot(x="Gen", y = ["Wealth_TF", "Wealth_VI", "Wealth_NT"],
        kind="line", figsize=(15, 6))
plt.show()
