import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Import the data
df = pd.read_csv("run_data.csv")
print(df)

# Basic plots

df.plot(x="Gen", y = ["Price"],
        kind="line", figsize=(15, 6))
plt.show()

df.plot(x="Gen", y = ["Wealth_TF", "Wealth_VI", "Wealth_NT"],
        kind="line", figsize=(15, 6))
plt.show()