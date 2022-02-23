import pandas as pd
data = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data/data1.csv")
# print(data)
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter
import ternary

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

# print(dataNT)
def GenPlot(dataNT, dataVI, dataTF):
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
    ax2.set_ylabel("Wealth Share NT", fontsize=fontsize)
    ax3.set_xlabel("Wealth Share TF", fontsize=fontsize)
    ax3.set_ylabel("Wealth Share NT", fontsize=fontsize)
    ax1.set_title("NT_returns_mean", fontsize=fontsize)
    ax2.set_title("VI_returns_mean", fontsize=fontsize)
    ax3.set_title("TF_returns_mean", fontsize=fontsize)
    ax1.invert_yaxis()
    ax2.invert_yaxis()
    ax3.invert_yaxis()
    plt.show()

dataNT = heat_data(data, 'WS_NT', 'WS_VI', 'NT_returns_mean')
dataVI = heat_data(data, 'WS_VI', 'WS_NT', 'VI_returns_mean')
dataTF = heat_data(data, 'WS_TF', 'WS_NT', 'TF_returns_mean')
# fig = GenPlot(dataNT, dataVI, dataTF)


# fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (15,6), sharex=True)
# sns.scatterplot(x="WS_NT", y="NT_returns_mean", data=data, ax=ax1)
# sns.scatterplot(x="WS_VI", y="VI_returns_mean", data=data, ax=ax2)
# sns.scatterplot(x="WS_TF", y="TF_returns_mean", data=data, ax=ax3)
# plt.show()

# data1 = data.loc[data['WS_NT'] == 0.3]
# fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (15,6), sharex=True)
# sns.scatterplot(x="WS_NT", y="NT_returns_mean", data=data1, ax=ax1)
# sns.scatterplot(x="WS_VI", y="VI_returns_mean", data=data1, ax=ax2)
# sns.scatterplot(x="WS_TF", y="TF_returns_mean", data=data1, ax=ax3)
# plt.show()

data_group = data.copy()
print(data_group)
data_group = data_group.groupby(['WS_NT', 'WS_VI', 'WS_TF'], as_index=False).mean()
print(data_group)

def generate_random_heatmap_data(scale):
    tf_r = dict()
    vi_r = dict()
    nt_r = dict()

    for l in range(len(data_group['WS_NT'])):
        (i,j,k) = (int(data_group.loc[l,'WS_VI'] * scale), int(data_group.loc[l,'WS_TF'] * scale), int(data_group.loc[l,'WS_NT'] * scale))
        nt_r[(i,j)] = data_group.loc[l,"NT_returns_mean"]
        vi_r[(i,j)] = data_group.loc[l,"VI_returns_mean"]
        tf_r[(i,j)] = data_group.loc[l,"TF_returns_mean"]
    return tf_r, vi_r, nt_r



def GenerateTernary(data, title):
    figure, tax = ternary.figure(scale=scale)
    figure.set_size_inches(10, 8)
    tax.heatmap(data, style='triangular')
    tax.boundary()
    tax.clear_matplotlib_ticks()
    # ticks = [i for i in range(99)]
    ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    tax.ticks(ticks = ticks, axis='lbr', linewidth=1, multiple=10)
    tax.bottom_axis_label("VI (%)", fontsize = fontsize)
    tax.left_axis_label("NT (%)", fontsize = fontsize)
    tax.right_axis_label("TF (%)", fontsize = fontsize)
    tax.get_axes().axis('off')
    tax.set_title(title, fontsize = fontsize)
    plt.tight_layout()
    tax._redraw_labels()
    return figure, tax
    
scale = 50
tf_r, vi_r, nt_r = generate_random_heatmap_data(scale)
fig, tax = GenerateTernary(nt_r, 'NT returns')
tax.show()

fig, tax = GenerateTernary(vi_r, 'VI returns')
tax.show()

fig, tax = GenerateTernary(tf_r, 'TF returns')
tax.show()
''' something is wrong '''

# print(data.columns)
# data2 = data_group.loc[(data_group['WS_NT'] > 0.55) & (data_group['WS_NT'] < 0.6)]
# print(data2)

