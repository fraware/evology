import matplotlib
import matplotlib.pyplot as plt



# from . import code.market
# from code import market

from code.market import dividend_series
# Results section

# Market model outputs subsection





history = market.dividend_series(1000*252)
# plt.plot(history)



fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Horizontally stacked subplots')
ax1.plot(history)
ax2.plot(history)
plt.show()