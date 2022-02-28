''' ternary plot for final wealth shares '''

import pandas as pd
data = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data/data2.csv")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import ternary
import numpy as np
from ternary.helpers import simplex_iterator
sns.set(font_scale=1) 
fontsize = 18

# Removing the sum 0 or sum nan runs does not seem necessary

data_group = data.groupby(['WS_VI_initial', 'WS_TF_initial', 'WS_NT_initial'], as_index=False).mean()

def generate_random_heatmap_data(scale):
    tf_ws = dict()
    vi_ws = dict()
    nt_ws = dict()
    attractor = dict()
    l = 0
    for (i,j,k) in simplex_iterator(scale):
        nt_ws[(i,j)] = data_group.loc[l,"WS_NT_final"] 
        vi_ws[(i,j)] = data_group.loc[l,"WS_VI_final"] 
        tf_ws[(i,j)] = data_group.loc[l,"WS_TF_final"] 
        if data_group.loc[l,"WS_TF_final"] >= 90:
            attractor[(i,j)] = 0
        elif data_group.loc[l,"WS_TF_final"] > 10:
            attractor[(i,j)] = 1
        else:
            attractor[(i,j)] = 2
        l += 1
    return nt_ws, vi_ws, tf_ws, attractor
    
scale = 25 # for this experiment scale is 25!
nt_r, vi_r, tf_r, attractor = generate_random_heatmap_data(scale)
'''
figure, tax = ternary.figure(scale=scale)
figure.set_size_inches(10, 8)
tax.heatmap(nt_r, style='triangular')
tax.boundary()
tax.clear_matplotlib_ticks()
ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
tax.ticks(ticks = ticks, axis='blr', linewidth=1, multiple=10)
tax.bottom_axis_label("NT Initial Wealth Share (%)", fontsize = fontsize) 
tax.left_axis_label("VI Initial Wealth Share (%)", fontsize = fontsize) 
tax.right_axis_label("TF Initial Wealth Share (%)", fontsize = fontsize)
tax.get_axes().axis('off')
tax.set_title('NT final wealth share', fontsize = fontsize)
tax._redraw_labels()
plt.tight_layout()
plt.savefig('Experiment2_NT_ternary.png',dpi=300)
plt.show()

figure, tax = ternary.figure(scale=scale)
figure.set_size_inches(10, 8)
tax.heatmap(vi_r, style='triangular')
tax.boundary()
tax.clear_matplotlib_ticks()
ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
tax.ticks(ticks = ticks, axis='blr', linewidth=1, multiple=10)
tax.bottom_axis_label("NT Initial Wealth Share (%)", fontsize = fontsize) 
tax.left_axis_label("VI Initial Wealth Share (%)", fontsize = fontsize) 
tax.right_axis_label("TF Initial Wealth Share (%)", fontsize = fontsize)
tax.get_axes().axis('off')
tax.set_title('VI final wealth share', fontsize = fontsize)
tax._redraw_labels()
plt.tight_layout()
plt.savefig('Experiment2_VI_ternary.png',dpi=300)
plt.show()

figure, tax = ternary.figure(scale=scale)
figure.set_size_inches(10, 8)
tax.heatmap(tf_r, style='triangular')
tax.boundary()
tax.clear_matplotlib_ticks()
ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
tax.ticks(ticks = ticks, axis='blr', linewidth=1, multiple=10)
tax.bottom_axis_label("NT Initial Wealth Share (%)", fontsize = fontsize) 
tax.left_axis_label("VI Initial Wealth Share (%)", fontsize = fontsize) 
tax.right_axis_label("TF Initial Wealth Share (%)", fontsize = fontsize)
tax.get_axes().axis('off')
tax.set_title('TF final wealth share', fontsize = fontsize)
tax._redraw_labels()
plt.tight_layout()
plt.savefig('Experiment2_TF_ternary.png',dpi=300)
plt.show()
'''
from matplotlib.colors import ListedColormap
cmap = plt.get_cmap('inferno', 3)
cmap = ListedColormap(['red', 'grey', 'blue'])
figure, tax = ternary.figure(scale=scale)
figure.set_size_inches(7, 7)
tax.heatmap(attractor, style='triangular',cmap=cmap, colorbar=False)
tax.boundary()
tax.clear_matplotlib_ticks()
ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
tax.ticks(ticks = ticks, axis='blr', linewidth=1, multiple=10)
tax.bottom_axis_label("NT Initial Wealth Share (%)", fontsize = fontsize) 
tax.left_axis_label("VI Initial Wealth Share (%)", fontsize = fontsize) 
tax.right_axis_label("TF Initial Wealth Share (%)", fontsize = fontsize)
tax.get_axes().axis('off')
tax.set_title('Basins of attraction', fontsize = fontsize)
tax._redraw_labels()
plt.tight_layout()
plt.savefig('Experiment2_attractors.png',dpi=300)
plt.show()