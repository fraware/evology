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
# data_plus = data[data["interest_rate"] > 0]
# data_plus2 = data[data["interest_rate"] > 0.005]

# %%
fontsize = 20
sns.set_style("whitegrid")
# print(data.columns)
plt.rcParams["axes.labelsize"] = fontsize
plt.rcParams['axes.titlepad'] = fontsize


# %%
# Final wealth shares

sns_fontsize = 2

fig, axs = plt.subplots(ncols=3, sharex=True, figsize=(20, 8))
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'WS_NT_final', data = data,
showfliers=False, ax=axs[0])
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'WS_VI_final', data = data,
showfliers=False,ax=axs[1])
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'WS_TF_final', data = data,
showfliers=False,ax=axs[2])
sns.set(font_scale = sns_fontsize)

axs[0].set(xlabel='NT')
axs[1].set(xlabel='VI')
axs[2].set(xlabel='TF')
fig.suptitle('Wealth Share (NT, VI, TF) vs Interest Rate')
for ax in axs:
    ax.set(ylabel=None)
plt.savefig('/Users/aymericvie/Documents/GitHub/evology/evology/research/interest_rates/figures/WS.png',dpi=300)
plt.tight_layout()
plt.show()

fig, axs = plt.subplots(ncols=3, sharex=True, figsize=(20, 8))
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'WS_NT_final', data = data,
showfliers=True, ax=axs[0])
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'WS_VI_final', data = data,
showfliers=True,ax=axs[1])
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'WS_TF_final', data = data,
showfliers=True,ax=axs[2])
sns.set(font_scale = sns_fontsize)

axs[0].set(xlabel='NT')
axs[1].set(xlabel='VI')
axs[2].set(xlabel='TF')
fig.suptitle('Wealth Share (NT, VI, TF) vs Interest Rate')
for ax in axs:
    ax.set(ylabel=None)
# plt.savefig('/Users/aymericvie/Documents/GitHub/evology/evology/research/interest_rates/figures/WS.png',dpi=300)
plt.tight_layout()
plt.show()

# %%

sns.boxplot(x = 'interest_rate', y = 'Avg_Price', data = data,
showfliers=False)
plt.show()

sns.boxplot(x = 'interest_rate', y = 'Avg_Trend_Duration', data = data,
showfliers=False)
plt.show()

# %%
# Mispricing and volatility


fig, axs = plt.subplots(ncols=2, sharex=True, figsize=(13, 8))
sns.boxplot(x = 'interest_rate', y = 'Mispricing', data = data,
showfliers=False,ax=axs[0])
# plt.show()
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'Volatility', data = data,
showfliers=False,ax=axs[1])
sns.set(font_scale = sns_fontsize)
axs[0].set(xlabel='Mispricing')
axs[1].set(xlabel='Volatility')
fig.suptitle('Market malfunction vs Interest Rate')
for ax in axs:
    ax.set(ylabel=None)
plt.savefig('/Users/aymericvie/Documents/GitHub/evology/evology/research/interest_rates/figures/MM.png',dpi=300)
plt.show()

# %%
# Returns
fig, axs = plt.subplots(ncols=3, sharex=True, sharey=True,figsize=(20, 8))
sns.boxplot(x = 'interest_rate', y = 'NT_returns_avg', data = data,
showfliers=False,ax=axs[0])
# plt.show()
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'VI_returns_avg', data = data,
showfliers=False,ax=axs[1])
# plt.show()
sns.set(font_scale = sns_fontsize)
sns.boxplot(x = 'interest_rate', y = 'TF_returns_avg', data = data,
showfliers=False,ax=axs[2])
sns.set(font_scale = sns_fontsize)
axs[0].set(xlabel='NT')
axs[1].set(xlabel='VI')
axs[2].set(xlabel='TF')
fig.suptitle('Returns vs Interest Rate')
for ax in axs:
    ax.set(ylabel=None)
plt.savefig('/Users/aymericvie/Documents/GitHub/evology/evology/research/interest_rates/figures/returns.png',dpi=300)
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
data03 = data[data["interest_rate"] == 0.03]
data025 = data[data["interest_rate"] == 0.025]
data01 = data[data["interest_rate"] == 0.01]
data015 = data[data["interest_rate"] == 0.015]
data02 = data[data["interest_rate"] == 0.02]

avg03 = 1/3 * (data03["NT_returns_avg"].mean() + data03["VI_returns_avg"].mean() + data03["TF_returns_avg"].mean())
avg01 = 1/3 * (data01["NT_returns_avg"].mean() + data01["VI_returns_avg"].mean() + data01["TF_returns_avg"].mean())
avg02 = 1/3 * (data02["NT_returns_avg"].mean() + data02["VI_returns_avg"].mean() + data02["TF_returns_avg"].mean())
avg025 = 1/3 * (data025["NT_returns_avg"].mean() + data025["VI_returns_avg"].mean() + data025["TF_returns_avg"].mean())
avg015 = 1/3 * (data015["NT_returns_avg"].mean() + data015["VI_returns_avg"].mean() + data015["TF_returns_avg"].mean())


NT_net_return = []
VI_net_return = []
TF_net_return = []
for i in range(len(data["interest_rate"])):
    if data["interest_rate"].iloc[i] == 0.01:
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg01)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg01)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg01)
    if data["interest_rate"].iloc[i] == 0.015:
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg015)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg015)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg015)
    elif data["interest_rate"].iloc[i] == 0.02: 
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg02)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg02)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg02)
    elif data["interest_rate"].iloc[i] == 0.03: 
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg03)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg03)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg03)
    elif data["interest_rate"].iloc[i] == 0.025: 
        NT_net_return.append(data["NT_returns_avg"].iloc[i] - avg025)
        VI_net_return.append(data["VI_returns_avg"].iloc[i] - avg025)
        TF_net_return.append(data["TF_returns_avg"].iloc[i] - avg025)
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
