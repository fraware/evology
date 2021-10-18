import numpy as np
import pandas as pd

''' Price '''
# Data type for price: (0, [USD(102.55)])
P = []
with open('data/replication/sample2/output/volatility_illustration/prices.txt', 'r') as content_file:
    for l in content_file.readlines():
        P.append(float(l.split('USD(')[1].split(')')[0]))
offset_prices = 0 
prices = np.array(P)[offset_prices:-1]
print(prices)

''' Dividends '''
# Data type for div: (0, 0.003983)
D = []
with open('data/replication/sample2/output/volatility_illustration/0_dividend.txt', 'r') as content_file:
    for l in content_file.readlines():
        D.append(float(l.split(',')[1].split(')')[0])) 
dividends = np.array(D)[offset_prices::2] 
print(dividends)

''' Volume ''' # Data type (0, [961837])
V = []
with open('data/replication/sample2/output/volatility_illustration/volumes.txt', 'r') as content_file:
    for l in content_file.readlines():
        V.append(int(l.split(', [')[1].split('])')[0]))
volumes = np.array(V)[offset_prices::2] 
print(volumes)

''' Noise trader '''
# Cash
NTC = []
with open('data/replication/sample2/output/volatility_illustration/_2__cash.txt', 'r') as content_file:
    for l in content_file.readlines():
        NTC.append(float(l.split('USD(')[1].split(')')[0]))
offset_prices = 0 
nt_cash = np.array(NTC)[offset_prices:-1]
print(nt_cash)


