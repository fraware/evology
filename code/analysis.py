import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
 
# Import the data
df = pd.read_csv("data/run_data.csv")
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


