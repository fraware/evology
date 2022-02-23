import pandas as pd
data = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data/data1.csv")
print(data)
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter


sns.set(font_scale=1) 
fontsize = 18
sigma = 1


def heat_data(original_data, columnX, columnY, columnZ):
    data2 = original_data.copy()
    data_temp = pd.DataFrame()
    data_temp['Gen'] = data2['Unnamed: 0']
    data_temp['F'] = data2[columnX]
    data_temp['H'] = data2[columnY]
    data_temp['T'] = data2[columnZ]

    data_temp2 = data_temp.groupby(['F', 'H'], as_index=False).mean()
    #data_temp2 = data_temp.copy()
    data_ready = data_temp2.pivot(index='H', columns='F', values = 'T')
    return data_ready


dataNT = heat_data(data, 'WS_NT', 'WS_VI', 'NT_returns_mean')
dataVI = heat_data(data, 'WS_VI', 'WS_TF', 'VI_returns_mean')
dataTF = heat_data(data, 'WS_TF', 'WS_NT', 'TF_returns_mean')
dataNT2 = heat_data(data, 'WS_NT', 'WS_TF', 'NT_returns_mean')
dataVI2 = heat_data(data, 'WS_VI', 'WS_NT', 'VI_returns_mean')
dataTF2 = heat_data(data, 'WS_TF', 'WS_VI', 'TF_returns_mean')

# print(dataNT)

# fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize = (15,8), sharey=True, sharex=True)
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (15,6), sharey=True, sharex=True)
cmap = 'seismic'
model = sns.heatmap(dataNT, ax=ax1, cmap = cmap)
sns.heatmap(dataVI, ax=ax2, cmap = cmap)
sns.heatmap(dataTF, ax=ax3, cmap = cmap)
# sns.heatmap(gaussian_filter(dataNT,sigma=sigma), ax=ax1, cmap = cmap)
# sns.heatmap(gaussian_filter(dataVI,sigma=sigma), ax=ax2, cmap = cmap)
# sns.heatmap(gaussian_filter(dataTF,sigma=sigma), ax=ax3, cmap = cmap)
# ax1.set_yticklabels(model.get_yticklabels(), rotation = 0)
# ax2.set_yticklabels(model.get_yticklabels(), rotation = 0)
# ax3.set_yticklabels(model.get_yticklabels(), rotation = 0)
# ax1.set_xticklabels(model.get_xticklabels(), rotation = 90)
# ax2.set_xticklabels(model.get_xticklabels(), rotation = 90)
# ax3.set_xticklabels(model.get_xticklabels(), rotation = 90)
ax1.set_xlabel("Wealth Share NT", fontsize=fontsize)
ax1.set_ylabel("Wealth Share VI", fontsize=fontsize)
ax2.set_xlabel("Wealth Share VI", fontsize=fontsize)
ax2.set_ylabel("Wealth Share TF", fontsize=fontsize)
ax3.set_xlabel("Wealth Share TF", fontsize=fontsize)
ax3.set_ylabel("Wealth Share NT", fontsize=fontsize)
ax1.set_title("NT_returns_mean", fontsize=fontsize)
ax2.set_title("VI_returns_mean", fontsize=fontsize)
ax3.set_title("TF_returns_mean", fontsize=fontsize)
ax1.invert_yaxis()
ax2.invert_yaxis()
ax3.invert_yaxis()
plt.show()

''' fig with alternative wshare
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (15,6), sharey=True, sharex=True)
cmap = 'seismic'
model = sns.heatmap(dataNT2, ax=ax1, cmap = cmap)
sns.heatmap(dataVI2, ax=ax2, cmap = cmap)
sns.heatmap(dataTF2, ax=ax3, cmap = cmap)
# sns.heatmap(gaussian_filter(dataNT,sigma=sigma), ax=ax1, cmap = cmap)
# sns.heatmap(gaussian_filter(dataVI,sigma=sigma), ax=ax2, cmap = cmap)
# sns.heatmap(gaussian_filter(dataTF,sigma=sigma), ax=ax3, cmap = cmap)
# ax1.set_yticklabels(model.get_yticklabels(), rotation = 0)
# ax2.set_yticklabels(model.get_yticklabels(), rotation = 0)
# ax3.set_yticklabels(model.get_yticklabels(), rotation = 0)
# ax1.set_xticklabels(model.get_xticklabels(), rotation = 90)
# ax2.set_xticklabels(model.get_xticklabels(), rotation = 90)
# ax3.set_xticklabels(model.get_xticklabels(), rotation = 90)
ax1.set_xlabel("Wealth Share NT", fontsize=fontsize)
ax1.set_ylabel("Wealth Share TF", fontsize=fontsize)
ax2.set_xlabel("Wealth Share VI", fontsize=fontsize)
ax2.set_ylabel("Wealth Share NT", fontsize=fontsize)
ax3.set_xlabel("Wealth Share TF", fontsize=fontsize)
ax3.set_ylabel("Wealth Share VI", fontsize=fontsize)
ax1.set_title("NT_returns_mean", fontsize=fontsize)
ax2.set_title("VI_returns_mean", fontsize=fontsize)
ax3.set_title("TF_returns_mean", fontsize=fontsize)
ax1.invert_yaxis()
ax2.invert_yaxis()
ax3.invert_yaxis()
plt.show()
 '''