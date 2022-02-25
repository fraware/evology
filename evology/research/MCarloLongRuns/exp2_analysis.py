import pandas as pd
data = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data/data2.csv")
print(data)
import matplotlib.pyplot as plt
import seaborn as sns


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


#######

def GenPlot(dataNT, dataVI, dataTF, title1, title2, title3, figname, bounds):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (15,6), sharey=True, sharex=True)
    cmap = 'seismic'
    if bounds == True:
        vmin = -0.2
        vmax = 0.2
        sns.heatmap(dataNT, ax=ax1, cmap = cmap, vmin=vmin, vmax=vmax)
        sns.heatmap(dataVI, ax=ax2, cmap = cmap, vmin=vmin, vmax=vmax)
        sns.heatmap(dataTF, ax=ax3, cmap = cmap, vmin=vmin, vmax=vmax)
    else:
        sns.heatmap(dataNT, ax=ax1, cmap = cmap)
        sns.heatmap(dataVI, ax=ax2, cmap = cmap)
        sns.heatmap(dataTF, ax=ax3, cmap = cmap)
    ax1.set_xlabel("Wealth Share NT", fontsize=fontsize)
    ax1.set_ylabel("Wealth Share VI", fontsize=fontsize)
    ax2.set_xlabel("Wealth Share VI", fontsize=fontsize)
    ax2.set_ylabel("Wealth Share NT", fontsize=fontsize)
    ax3.set_xlabel("Wealth Share TF", fontsize=fontsize)
    ax3.set_ylabel("Wealth Share NT", fontsize=fontsize)
    ax1.set_title(title1, fontsize=fontsize)
    ax2.set_title(title2, fontsize=fontsize)
    ax3.set_title(title3, fontsize=fontsize)
    ax1.invert_yaxis()
    ax2.invert_yaxis()
    ax3.invert_yaxis()

    plt.tight_layout()
    plt.savefig(figname, dpi=300)
    plt.show()


dataNT = heat_data(data, 'WS_NT_inital', 'WS_VI_inital', 'WS_NT_final')
dataVI = heat_data(data, 'WS_VI_inital', 'WS_NT_inital', 'WS_VI_final')
dataTF = heat_data(data, 'WS_TF_initial', 'WS_NT_inital', 'WS_TF_final')
fig = GenPlot(dataNT, dataVI, dataTF, "NT Wealth Share", "VI Wealth Share", "TF Wealth Share", 'Experiment2a.png', False)
