# %%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import math
from statsmodels.graphics.tsaplots import plot_acf

# Import the data
if sys.platform == "darwin":
    df = pd.read_csv(
        "/Users/aymericvie/Documents/GitHub/evology/evology/code/oop/rundata/run_data.csv"
    )
if sys.platform == "win32":
    df = pd.read_csv(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\code\oop\rundata\run_data.csv"
    )
fontsize = 18

# %%
""" Absence of linear autocorrelations in asset returns """
""" intermittency """

# log return
df["PriceReturn"] = (np.log(df["Price"]) - np.log(df["Price"].shift(1))) 

print(df["PriceReturn"].autocorr())

df.plot(x="Generation", y=["PriceReturn"], kind="line")
plt.xlabel("Time", fontsize=fontsize)
plt.ylabel("Price log returns", fontsize=fontsize)
plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val1a.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val1a.png",
        dpi=300,
    )
plt.show()

data = pd.DataFrame()
data["Time"] = df["Generation"]
data["PriceReturn"] = df["PriceReturn"]
data.set_index(["Time"])
del data["Time"]
data = data.apply(lambda x: pd.Series(x.dropna().values))

plot_acf(x=data, lags=21, zero=False, alpha=0.05)
plt.ylim(-0.4, 0.4)
plt.xlabel("Time", fontsize=fontsize)
plt.ylabel("Autocorrelation", fontsize=fontsize)
plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val1b.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val1b.png",
        dpi=300,
    )
plt.show()
# %%
""" Heavy tails distributions of returns """
print(data.kurtosis())

data.hist("PriceReturn", bins=50, density=False)
plt.xlabel("Log Price Returns", fontsize=fontsize)
plt.ylabel("Observations", fontsize=fontsize)
plt.xlim(-0.04, 0.04)
plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val2.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val2.png",
        dpi=300,
    )
plt.show()
# %%
""" Gain loss assymetry """

df.plot(x="Generation", y=["Price"], kind="line")
plt.xlabel("Time", fontsize=fontsize)
plt.ylabel("Price", fontsize=fontsize)

plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val3.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val3.png",
        dpi=300,
    )
plt.show()

print(data.kurtosis())
# %%
""" Aggregational Gaussianity """

# For horizon 21 days

df["PriceReturnYear"] = (np.log(df["Price"]) - np.log(df["Price"].shift(21))) 

data = pd.DataFrame()
data["Time"] = df["Generation"]
data["PriceReturn"] = df["PriceReturnYear"]
data.set_index(["Time"])
del data["Time"]
data = data.apply(lambda x: pd.Series(x.dropna().values))

print(data.kurtosis())

# For horizon 252 days


df["PriceReturnYear"] = (np.log(df["Price"]) - np.log(df["Price"].shift(252))) 

data = pd.DataFrame()
data["Time"] = df["Generation"]
data["PriceReturn"] = df["PriceReturnYear"]
data.set_index(["Time"])
del data["Time"]
data = data.apply(lambda x: pd.Series(x.dropna().values))

print(data.kurtosis())


data.hist("PriceReturn", bins=50, density=False)
plt.xlabel("Log Price Returns (Yearly)", fontsize=fontsize)
plt.ylabel("Observations", fontsize=fontsize)
plt.title('')
# plt.xlim(-0.04, 0.04)
plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val2b.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val2b.png",
        dpi=300,
    )
plt.show()



# %%
""" Intermittency """



df.plot(x="Generation", y=["Price"], kind="line")
plt.xlabel("Time", fontsize=fontsize)
plt.ylabel("Price", fontsize=fontsize)
plt.show()

daily_volatility = df['PriceReturn'].std()
print('Daily volatility: ', '{:.2f}%'.format(daily_volatility))

monthly_volatility = math.sqrt(21) * daily_volatility
print ('Monthly volatility: ', '{:.2f}%'.format(monthly_volatility))

annual_volatility = math.sqrt(252) * daily_volatility
print ('Annual volatility: ', '{:.2f}%'.format(annual_volatility ))

df["Volatility"] = df["PriceReturn"].rolling(1000).std()
df.plot(x="Generation", y=["Volatility"], kind="line")
plt.xlabel("Time", fontsize=fontsize)
plt.ylabel("Log Price returns volatility", fontsize=fontsize)
plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val4.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val4.png",
        dpi=300,
    )
plt.show()

# %%
""" leverage effect  and volatility-volume correlation"""
df2 = pd.DataFrame()

df2["Volatility"] = df["Volatility"]
df2["PriceReturn"] = df["PriceReturn"]
df2["Volume"] = df["Volume"]
df2 = df2.apply(lambda x: pd.Series(x.dropna().values))
df2.corr()
# %%
""" slow decay of autocorrelation in absolute returns """

df["AbsReturns"] = abs(df["PriceReturn"])
data = pd.DataFrame()
data["Time"] = df["Generation"]
data["AbsReturns"] = df["AbsReturns"]
data.set_index(["Time"])
del data["Time"]
data = data.apply(lambda x: pd.Series(x.dropna().values))

plot_acf(x=data, lags=5000, alpha=0.05, auto_ylims=True)
plt.ylim(-0.25, 1.0)
plt.xlabel("Time (periods)", fontsize=fontsize)
plt.ylabel("Autocorrelation", fontsize=fontsize)
plt.tight_layout()
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val6.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val6.png",
        dpi=300,
    )
plt.show()
# %%
""" Conditional heavy tail returns"""
bins = 20
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5), sharex=False)
fig.suptitle("Histogram of period returns (NT, VI, TF)")

ax1.hist(df["NT_returns"], bins=bins)
num = df["NT_returns"].mean()
ax1.set_title("Average Returns NT - Mean: %1.5f" % num)
ax1.axvline(x=num, color="r", linestyle="dashed", linewidth=2)

ax2.hist(df["VI_returns"], bins=bins)
num = df["VI_returns"].mean()
ax2.set_title("Average Returns VI - Mean: %1.5f" % num)
ax2.axvline(x=num, color="r", linestyle="dashed", linewidth=2)

ax3.hist(df["TF_returns"], bins=bins)
num = df["TF_returns"].mean()
ax3.set_title("Average Returns TF - Mean: %1.5f" % num)
ax3.axvline(x=num, color="r", linestyle="dashed", linewidth=2)

ax1.set_ylabel("Observations", fontsize=fontsize)
ax1.set_xlabel("Period Returns", fontsize=fontsize)
ax2.set_ylabel("Observations", fontsize=fontsize)
ax2.set_xlabel("Period Returns", fontsize=fontsize)
ax3.set_ylabel("Observations", fontsize=fontsize)
ax3.set_xlabel("Period Returns", fontsize=fontsize)

ax1.set_xlim(-0.05, 0.05)
ax2.set_xlim(-0.02, 0.02)
ax3.set_xlim(-0.1, 0.1)
plt.tight_layout
if sys.platform == "darwin":
    plt.savefig(
        "/Users/aymericvie/Documents/GitHub/evology/evology/validation/val5.png",
        dpi=300,
    )
elif sys.platform == "win32":
    plt.savefig(
        r"D:\OneDrive\Research\2021_Market_Ecology\evology\evology\validation\val5.png",
        dpi=300,
    )

plt.show()

print(df["NT_returns"].kurt())
print(df["VI_returns"].kurt())
print(df["TF_returns"].kurt())


# print(df['NT_returns'].mean())
# print(df['VI_returns'].mean())
# print(df['TF_returns'].mean())


# %%
