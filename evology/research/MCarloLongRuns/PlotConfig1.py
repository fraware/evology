import sys
import pandas as pd
sys.path.insert(0, '/Users/aymericvie/Documents/GitHub/evology/evology/code/')
import ternary
import numpy as np
import matplotlib.pyplot as plt
import platform
print(platform.system())

def PathPoints(MCNT, MCVI, MCTF):
    points = []
    for i in range(len(MCNT.columns) - 1):
        x = MCNT['Rep%s' % i].mean()
        y = MCVI['Rep%s' % i].mean()
        z = MCTF['Rep%s' % i].mean()
        points.append((x,y,z))
    return points

def FinalPoints(MCNT, MCVI, MCTF):
    points = []
    for i in range(len(MCNT.columns) - 1):
        x = MCNT['Rep%s' % i].iloc[-1]
        y = MCVI['Rep%s' % i].iloc[-1]
        z = MCTF['Rep%s' % i].iloc[-1]
        points.append((x,y,z))
    return points

if platform.system() == 'Darwin':
    MCNT1 = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data_config1/MC_NT.csv")
    MCVI1 = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data_config1/MC_VI.csv")
    MCTF1 = pd.read_csv("/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data_config1/MC_TF.csv")

else: 
    MCNT1 = pd.read_csv("/home/vie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data_config1/MC_NT.csv")
    MCVI1 = pd.read_csv("/home/vie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data_config1/MC_VI.csv")
    MCTF1 = pd.read_csv("/home/vie/Documents/GitHub/evology/evology/research/MCarloLongRuns/data_config1/MC_TF.csv")

points1 = PathPoints(MCNT1, MCVI1, MCTF1)
finals1 = FinalPoints(MCNT1, MCVI1, MCTF1)


scale = 100
fontsize = 20

def TernaryPlot(scale, points, fontsize,title):
    origin = [((100/3, 100/3, 100/3))]
    # origin = [((40, 40, 20))]
    # origin = [((20,40,40))]
    figure, tax = ternary.figure(scale=scale)
    figure.set_size_inches(10, 8)
    tax.gridlines(color="gray", multiple=10)
    tax.boundary()
    tax.left_axis_label("TF (%)", fontsize = fontsize)
    tax.right_axis_label("VI (%)", fontsize = fontsize)
    tax.bottom_axis_label("NT (%)", fontsize = fontsize)
    tax.scatter(points, marker='D', color='red', label="Simulations")
    tax.scatter(origin, marker='D', color='black', label="Initial condition")
    ticks = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    tax.ticks(ticks = ticks, axis='lbr', linewidth=1, multiple=10)
    tax.get_axes().axis('off')
    # tax.clear_matplotlib_ticks()
    tax.set_title(title, fontsize=fontsize)
    plt.legend(loc='upper right', fontsize=fontsize)
    plt.tight_layout()
    tax._redraw_labels()
    return figure, tax

figure, tax = TernaryPlot(scale, points1, fontsize, 'Config1')
if platform.system() == 'Linux':
    path = '/home/vie/Documents/GitHub/evology/evology/research/MCarloLongRuns/path_figs/Path1.png'
    plt.savefig(path, dpi=300)
if platform.system() == 'Darwin':
    path = '/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/path_figs/Path1.png'
    plt.savefig(path, dpi=300)

figure, tax = TernaryPlot(scale, finals1, fontsize, 'Config1')
if platform.system() == 'Linux':
    path = '/home/vie/Documents/GitHub/evology/evology/research/MCarloLongRuns/path_figs/Final1.png'
    plt.savefig(path, dpi=300)
if platform.system() == 'Darwin':
    path = '/Users/aymericvie/Documents/GitHub/evology/evology/research/MCarloLongRuns/path_figs/Final1.png'
    plt.savefig(path, dpi=300)