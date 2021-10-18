import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Import the data
run = pd.read_csv("data/test_data.csv")
ref = pd.read_csv('data/replication_data.csv')

''' Dividends '''
data = df = pd.DataFrame()
data['Dividends (Reference)'] = ref['Dividends']
data['Dividends (Simulation)'] = run['Dividends']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["Dividends (Reference)", "Dividends (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of dividends', )
plt.xlabel('Generations')
plt.ylabel('Daily dividend')
plt.show()

''' Price '''
data['Price (Reference)'] = ref['Price']
data['Price (Simulation)'] = run['Price']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["Price (Reference)", "Price (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of price', )
plt.xlabel('Generations')
plt.ylabel('Price')
plt.show()

''' Volume '''
data['Volume (Reference)'] = ref['Volume']
data['Volume (Simulation)'] = run['Volume']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["Volume (Reference)", "Volume (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of volume', )
plt.xlabel('Generations')
plt.ylabel('Volume')
plt.show()