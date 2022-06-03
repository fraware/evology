# %%
# Data and modules imports

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import isnan
data = pd.read_csv(
    "/Users/aymericvie/Documents/GitHub/evology/evology/research/interest_rates/data/ir_noinv.csv"
)
fontsize = 15
sns.set_style("whitegrid")
# print(data.columns)
plt.rcParams["axes.labelsize"] = 15
data = data[data["interest_rate"] != -0.01]

# %%
# Final wealth shares

sns.boxplot(x = 'interest_rate', y = 'WS_NT_final', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'WS_VI_final', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'WS_TF_final', data = data,
showfliers=False)
plt.show()

# %%
# Mispricing and volatility

sns.boxplot(x = 'interest_rate', y = 'Mispricing', data = data,
showfliers=False)
plt.show()

sns.boxplot(x = 'interest_rate', y = 'Volatility', data = data,
showfliers=False)
plt.show()

# %%
# Returns
sns.boxplot(x = 'interest_rate', y = 'NT_returns_avg', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'VI_returns_avg', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'TF_returns_avg', data = data,
showfliers=False)
plt.show()
# %%
# Substrategies
sns.boxplot(x = 'interest_rate', y = 'Mean_NT_final', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'Mean_VI_final', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'Mean_TF_final', data = data,
showfliers=False)
plt.show()

# %%
sns.boxplot(x = 'interest_rate', y = 'Gen', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'DiffReturns', data = data,
showfliers=False)
plt.show()
# %%
# Returns
data00 = data[data["interest_rate"] == 0.01]
data01 = data[data["interest_rate"] == 0.01]
data02 = data[data["interest_rate"] == 0.02]

avg00 = 1/3 * (data00["NT_returns_avg"].mean() + data00["VI_returns_avg"].mean() + data00["TF_returns_avg"].mean())
avg01 = 1/3 * (data01["NT_returns_avg"].mean() + data01["VI_returns_avg"].mean() + data01["TF_returns_avg"].mean())
avg02 = 1/3 * (data02["NT_returns_avg"].mean() + data02["VI_returns_avg"].mean() + data02["TF_returns_avg"].mean())

NT_net_return = []
VI_net_return = []
TF_net_return = []
for i in range(len(data["interest_rate"])):
    if data["interest_rate"].iloc[i] == 0.01:
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg01)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg01)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg01)
    elif data["interest_rate"].iloc[i] == 0.02: 
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg02)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg02)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg02)
    elif data["interest_rate"].iloc[i] == 0.00: 
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg00)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg00)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg00)
data["net_NT_return"] = NT_net_return
data["net_VI_return"] = VI_net_return
data["net_TF_return"] = TF_net_return


sns.boxplot(x = 'interest_rate', y = 'net_NT_return', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'net_VI_return', data = data,
showfliers=False)
plt.show()
sns.boxplot(x = 'interest_rate', y = 'net_TF_return', data = data,
showfliers=False)
plt.show()
# %%
