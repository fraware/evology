# Results section

# Market model outputs subsection

from market import *
history = dividend_series(1000*252)
# plt.plot(history)



fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Horizontally stacked subplots')
ax1.plot(history)
ax2.plot(history)
plt.show()