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

# There will be no replacements in the setup of Scholl 2020
# df_nl.plot(x="Gen", y = ["Rep"],
#         kind="line", figsize=(15, 6))
# plt.show()

# df_nl.plot(x="Gen", y = ["Num_TF", "Num_VI", "Num_NT"],
#         kind="line", figsize=(15, 6))
# plt.show()

# df_nl.plot(x="Gen", y = ["Wealth_TF", "Wealth_VI", "Wealth_NT"],
#         kind="line", figsize=(15, 6))
# plt.show()

df_nl.plot(x="Gen", y = ["WShare_TF", "WShare_VI", "WShare_NT"],
        kind="line", figsize=(15, 6))
plt.show()
