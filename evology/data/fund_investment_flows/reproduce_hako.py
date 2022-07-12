#
# %%
import pandas as pd
import seaborn as sns
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# %%
path = 'D:\\OneDrive\Research\\2021_Market_Ecology\\evology\\evology\\data\\fund_investment_flows\\hako_data.csv'
hako_data = pd.read_csv(path)
print(hako_data)

# %%
# Remove funds not used in observations 

print(len(hako_data))
hako_data = hako_data[hako_data.Obs_included == 1]
print(len(hako_data))
# %%
# Remove excessive net flows
print(len(hako_data))
hako_data = hako_data[hako_data.Net_flows <= 1]
print(len(hako_data))

# %%
hako_data.hist("Net_flows", bins = 100, range=(-0.25, 0.25))
# %%
hako_data.hist("Monthly_returns", bins = 100, range=(-0.25, 0.25))
# %%
sns.scatterplot("Monthly_returns", "Net_flows", data=hako_data, size=1)
# %%
# sns.regplot( y="Net_flows", x="Monthly_returns", data=hako_data)
# %%
from sklearn import datasets, linear_model
regr = linear_model.LinearRegression()
# x = hako_data.Monthly_returns.reshape(len(hako_data.Monthly_returns.reshape), 1)
# y = hako_data.Net_flows.reshape(len(hako_data.Net_flows.reshape), 1)
# print(x.shape)
x = hako_data[["Monthly_returns"]]
y = hako_data[["Net_flows"]]
regr.fit(x, y)
# The coefficients
print("Coefficients: \n", regr.coef_)
print("Intercept: \n", regr.intercept_)

plt.scatter(x, y, color = 'red')
plt.plot(x, regr.predict(x), color = 'blue')
plt.xlabel('Monthly returns')
plt.ylabel('Net flows')
plt.show()
# %%
regr = linear_model.LinearRegression()
# x = hako_data.Monthly_returns.reshape(len(hako_data.Monthly_returns.reshape), 1)
# y = hako_data.Net_flows.reshape(len(hako_data.Net_flows.reshape), 1)
# print(x.shape)
x = hako_data[["Objective_monthly_returns"]]
y = hako_data[["Net_flows"]]
regr.fit(x, y)
# The coefficients
print("Coefficients: \n", regr.coef_)
print("Intercept: \n", regr.intercept_)

plt.scatter(x, y, color = 'red')
plt.plot(x, regr.predict(x), color = 'blue')
plt.xlabel('Objective-adjusted Monthly returns')
plt.ylabel('Net flows')
plt.show()

# %%
sns.scatterplot("Monthly_returns", "Objective_monthly_returns", data=hako_data, size=1)
# %%
# Now, we want to quantify the noise.
# It could be regressing the variance on the x on bins

hako_data['bin_return'] = pd.qcut(hako_data['Monthly_returns'], q=20, precision=1)
# print(hako_data)

# print(hako_data['bin_return'].unique())


df = pd.DataFrame()
df["bins"] = hako_data['bin_return'].unique()

means, variances, means_returns, stds = [], [], [], []

for bin in hako_data['bin_return'].unique():
    # print(bin)
    df2 = pd.DataFrame()
    # for i in range(len(hako_data)):
    df2 = hako_data[hako_data['bin_return'] == bin]
    means.append(np.mean(df2["Net_flows"]))
    variances.append(np.var(df2["Net_flows"])/ abs(np.mean(df2["Monthly_returns"])))
    means_returns.append(np.mean(df2["Monthly_returns"]))
    stds.append(np.std(df2["Net_flows"]) / abs(np.mean(df2["Monthly_returns"])))
df["mean_return"] = means_returns
df["means"] = means
df["variances(cond)"] = variances
df["std(cond)"] = stds 
df = df.sort_values(by='mean_return')
print(df)

regr = linear_model.LinearRegression()
# x = hako_data.Monthly_returns.reshape(len(hako_data.Monthly_returns.reshape), 1)
# y = hako_data.Net_flows.reshape(len(hako_data.Net_flows.reshape), 1)
# print(x.shape
# 
# )
y = df[["variances(cond)"]]
# y = df[["std(cond)"]]
x = df[["mean_return"]]
regr.fit(x, y)
# The coefficients
print("Coefficients: \n", regr.coef_)
print("Intercept: \n", regr.intercept_)

plt.scatter(x, y, color = 'red')
plt.plot(x, regr.predict(x), color = 'blue')
plt.xlabel('Monthly returns')
plt.ylabel('var')
plt.show()


# %%
xx = np.linspace(0.001, 0.15, 100)
print(xx)
def func(arg):
    return 2 * (1/((1+abs(arg)) ** 20))

z = [func(xxx) for xxx in xx]
plt.scatter(x, y, color = 'red')
plt.plot(z)
plt.xlim(-0.15, 0.15)
plt.xlabel('Monthly returns')
plt.ylabel('variances')
plt.show()
# %%
from scipy.optimize import curve_fit
def func(x, a, b):
    return (a / (x)) ** b
    
    
xdata = np.linspace(0.051, 0.12, 100)
# ydata = func(xdata, 2.5, 1.3)
ydata = df["std(cond)"]
plt.plot(xdata, ydata, 'b-', label='data')

popt, pcov = curve_fit(func, xdata, ydata)
print(popt)

plt.plot(xdata, func(xdata, *popt), 'g--',
         label='fit: a=%5.3f, b=%5.3f' % tuple(popt))
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()
# %%
