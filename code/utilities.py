import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# def ema(values, period):
#     values = np.array(values)
#     return pd.ewm(values, span=period)[-1]

values = [9, 5, 10, 16, 5]
period = 5

df = pd.DataFrame({'V': values})
print(df)

df['V_ema'] = df.ewm(span = period).mean()
print(df)

df.plot(y=['V_ema', 'V'], use_index=True)
plt.show()

