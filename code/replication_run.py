import numpy as np

P = []
with open('data/replication/sample2/output/prices.txt', 'r') as content_file:
    for l in content_file.readlines():
        P.append(float(l.split('USD(')[1].split(')')[0]))
offset_prices = 0 
prices = np.array(P)[offset_prices:-1]