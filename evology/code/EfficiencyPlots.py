#!/usr/bin/env python3

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
 
# Import the data
df = pd.read_csv("evology/data/run_data.csv")
print(df)

df.plot(x="Gen", y = ["TotalTime"],
        kind="line", figsize=(15, 6))
plt.show()

df.plot(x="Gen", y = ['TimeA', 'TimeB', 'TimeC', 'TimeD', 'TimeE', 'TimeF', 'TimeG'],
        kind="line", figsize=(15, 6))
plt.show()

