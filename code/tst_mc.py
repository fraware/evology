from esl_market_clearing import *

def func1(asset_key, price): #value investor
  return (2/3 * (50_000_000 + 500_000 * float(initial_price)) / price ) * (5 * np.tanh(np.log2(10000) - np.log2(price) + 0.5)) - 500_000

def func2(asset_key, price): #noise trader
  return ((5 * 50_000_000 + 500_000 * float(initial_price)) / price) * (4 * np.tanh(np.log2(10000) - np.log2(price) + 0.5)) - 500_000

def func3(asset_key, price): #trend follower
  return (3 * (50_000_000 + 500_000 * float(initial_price)) / price ) * (np.tanh(0 + 0.5)) - 500_000 


current_price = 100
functions = [func1, func2, func3]
initial_price = price(int(current_price * 100), currencies.USD)
new_price = solve(functions, 100)
print(new_price)
print(float(new_price[0]))
a = func1(i, float(new_price[0]))
print(a)
b = func2(i, float(new_price[0]))
print(b)
c = func3(i, float(new_price[0]))
print(c)
print(a+b+c)


# new_price = solve(functions, 164.14)
# print(new_price)
# print(float(new_price[0]))
# print(func1(i, float(new_price[0])))
# print(func2(i, float(new_price[0])))
# print(func3(i, float(new_price[0])))