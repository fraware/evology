import matplotlib
import matplotlib.pyplot as plt

import sys
print(sys.path)
sys.path.insert(0,r"C:\Users\aymer\OneDrive\Research\2021_MarketEcology\EvoMarketEcology")

import test_module
test_module.foo()

# import code.market.dividend_series
# from .. code.market import dividend_series
from code import market

# from .. code import market
# from code.market import dividend_series
# from ...code import market 
# from code import market
# import evomarketecology 

# import market 
# from . import code.market
# from code import market

# from code.market import dividend_series
# Results section

# Market model outputs subsection


history = market.dividend_series(1000*252)
# plt.plot(history)



fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Horizontally stacked subplots')
ax1.plot(history)
ax2.plot(history)
plt.show()