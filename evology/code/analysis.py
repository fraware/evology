#!/usr/bin/env python3

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
 
# Import the data
df = pd.read_csv("evology/data/run_data.csv")
print(df)

# Basic plots

df.plot(x="Gen", y = ["Price"],
        kind="line", figsize=(15, 6))
plt.show()

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (10, 5), sharex = True)
fig.suptitle('Price, Positive positions, negative positions')
ax1.plot(df["Price"])
ax2.plot(df["Pos+"])
ax3.plot(df["Pos-"])
ax1.set_xlabel('Time (days)')
plt.show()

df.plot(x="Gen", y = ["Dividends"],
        kind="line", figsize=(15, 6))
plt.show()


df.plot(x="Gen", y = ["WShare_TF", "WShare_VI", "WShare_NT"],
        kind="line", figsize=(15, 6))
plt.show()

df.plot(x="Gen", y = ["NT_returns", "VI_returns", "TF_returns"],
        kind="line", figsize=(15, 6))
plt.show()

df['NT_returns_ema'] = df['NT_returns'].ewm(span = 252).mean()
df['VI_returns_ema'] = df['VI_returns'].ewm(span = 252).mean()
df['TF_returns_ema'] = df['TF_returns'].ewm(span = 252).mean()

df.plot(x="Gen", y = ["NT_returns_ema", "VI_returns_ema", "TF_returns_ema"],
        kind="line", figsize=(15, 6), ylim=[-0.01,0.01])
plt.show()

df.plot(x="Gen", y = ["NT_nav", "VI_nav", "TF_nav"],
        kind="line", figsize=(15, 6))
plt.show()



df['WShare_NT_mag'] = abs(np.diff(df['WShare_NT'], prepend = 0))
df['WShare_VI_mag'] = abs(np.diff(df['WShare_VI'], prepend = 0))
df['WShare_TF_mag'] = abs(np.diff(df['WShare_TF'], prepend = 0))
df['Sum_rel_mag'] = df['WShare_NT_mag'] + df['WShare_VI_mag'] + df['WShare_TF_mag']


df.plot(x="Gen", y = ['Sum_rel_mag'],
        kind="line", figsize=(15, 6), ylim = [0, 20], ylabel = 'Absolute sum of changes in relative wealth')
plt.show()


df['WShare_NT_mag_sq'] = np.square(np.diff(df['WShare_NT'], prepend = 0))
df['WShare_VI_mag_sq'] = np.square(np.diff(df['WShare_VI'], prepend = 0))
df['WShare_TF_mag_sq'] = np.square(np.diff(df['WShare_TF'], prepend = 0))
df['Sum_rel_mag_sq'] = df['WShare_NT_mag_sq'] + df['WShare_VI_mag_sq'] + df['WShare_TF_mag_sq']
df['Sum_rel_mag_sq_ema'] = df["Sum_rel_mag_sq"].ewm(span = 252).mean()


df.plot(x="Gen", y = ['Sum_rel_mag_sq', 'Sum_rel_mag_sq_ema'],
        kind="line", figsize=(15, 6), ylim = [0, 20], 
        ylabel = 'Squared sum of changes in relative wealth', 
        title='Squared sum of changes in relative wealth over time')
plt.show()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (10, 5), sharex = True)
fig.suptitle('Strategy wealth share and magnitude of changes')
ax1.plot(df["WShare_TF"], label = 'Wealth share TF')
ax1.plot(df["WShare_VI"], label = 'Wealth share VI')
ax1.plot(df["WShare_NT"], label = 'Wealth share NT')
ax2.plot(df["Sum_rel_mag_sq"], label = 'Variability')
ax2.plot(df["Sum_rel_mag_sq_ema"], label = 'Variability (EMA)')
ax1.legend()
ax2.legend()
ax2.set_ylim(0,15)
ax2.set_xlabel('Time (days)')
ax1.set_title('Wealth shares of strategies')
ax2.set_title('Squared sum of wealths share changes')
plt.show()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (10, 5), sharex = True)
fig.suptitle('Strategy wealth share and %neg')
ax1.plot(df["WShare_TF"], label = 'Wealth share TF')
ax1.plot(df["WShare_VI"], label = 'Wealth share VI')
ax1.plot(df["WShare_NT"], label = 'Wealth share NT')
ax2.plot(df["NegW_per"], label = 'Percentage')

ax1.legend()
ax2.legend()
ax2.set_xlabel('Time (days)')
ax1.set_title('Wealth shares of strategies')
ax2.set_title('Percentage of negative wealth')
plt.show()




