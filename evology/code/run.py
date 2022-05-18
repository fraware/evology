from main import *
from parameters import *

wealth_coordinates = np.random.dirichlet(np.ones(3), size=1)[0].tolist()
np.random.seed(8)
# wealth_coordinates = [1/3,1/3,1/3]
wealth_coordinates = [0.35980457948740263, 0.1503673717372929, 0.48982804877530445]
print(wealth_coordinates)

def func(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, d, v, g, r):
    return 0
df, pop, av_stats = main(
    strategy = None, #func, #None, #func,
    space = 'extended', # 'extended',
    wealth_coordinates=wealth_coordinates,
    POPULATION_SIZE = 100,
    MAX_GENERATIONS = 40000, #50 * 252, #20000, #1000 * 252,
    tqdm_display=False,
    reset_wealth=False,
)

print(df)
df.to_csv("rundata/run_data.csv")

print(av_stats)

df["Mispricing"] = (df["Mean_VI"] / df["Price"]) - 1
df["LogPriceReturns"] = np.log(df["Price"]/df["Price"].shift(1))

df["Volatility"] = df["LogPriceReturns"].rolling(window=252).std()*np.sqrt(252)
volatiltiy = df["Volatility"].mean()
print(volatiltiy)

print([df["NT_nav"].iloc[-1] / df["NT_nav"].iloc[0],
            df["VI_nav"].iloc[-1] / df["VI_nav"].iloc[0], 
            df["TF_nav"].iloc[-1] / df["TF_nav"].iloc[0], 
            df["BH_wealth"].iloc[-1] / df["BH_wealth"].iloc[0], 
            df["IR_wealth"].iloc[-1] / df["IR_wealth"].iloc[0] ])