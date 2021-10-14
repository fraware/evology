import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Import the data
df_nl = pd.read_csv("data/test_data.csv")
print(df_nl)

# Basic plots

df_nl.plot(x="Gen", y = ["Price"],
        kind="line", figsize=(15, 6))
plt.show()

# df_nl.plot(x="Gen", y = ["Pos+", "Pos-"],
#         kind="line", figsize=(15, 6))
# plt.show()

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (10, 5), sharex = True)
fig.suptitle('Price, Positive positions, negative positions')
ax1.plot(df_nl["Price"])
ax2.plot(df_nl["Pos+"])
ax3.plot(df_nl["Pos-"])
ax1.set_xlabel('Time (days)')
plt.show()

df_nl.plot(x="Gen", y = ["Div"],
        kind="line", figsize=(15, 6))
plt.show()


df_nl.plot(x="Gen", y = ["WShare_TF", "WShare_VI", "WShare_NT"],
        kind="line", figsize=(15, 6))
plt.show()
