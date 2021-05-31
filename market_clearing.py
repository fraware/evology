# !pip install eslpy
# !pip3 install --index-url https://test.pypi.org/simple/ eslpy --force --user
import esl
print(esl.version())
# !pip3 show eslpy
print(f"We are running version {esl.version()}")

'''
Property ID
Abstract base class for all things that can be owned by economic agents.
FUngible (one property identifier for an entire type) and infugible (unique items, one property identifier per instance)
COmpany shares are fungible, so share the same property identifier.
ientity 0: first non empty identity; property identity 0-0, 0(1+ for other financial instruments)

'''
from esl.law import property, property_identity
i  = property_identity([0, 1])
i2 = property_identity([0, 2])
p  = property(i)
p2 = property(i2)

from esl.economics import price
from esl.economics import currencies
initial_price = price(123, currencies.USD)
# # if we are not afraid of floating point truncation, we could also write:
# initial_price = price.approximate(1.23, currencies.USD)
# # or if we want to do a conversion ourselves:
# initial_price = price(int(1.23 * currencies.USD.denominator), currencies.USD)
print(initial_price)

'''
Quotes
Define a market interaction.
- A vendor sells apples at $2.00 for 6 apples. The quote is 6 apples@$2.00
- The derivatives dealer sells an Apple,INC call option with strike $160.00 and expiry 2021-09-17, the market convention is to quote in Black-Scholes volatility, the quote is
 EuropeanCallOptionContract('AAPL', '2021-09-17', $160.00, buyer)@29.9% Black-Scholes 

We maintain a dictionary of property ID and quotes which contain a price.
'''
from esl.economics.markets import quote
initial_quote = quote(initial_price)
print(f"The initial quote is {initial_quote}, the lot size is {initial_quote.lot}") 


'''
Balance sheet class
Only a summary statistics.

'''


''' 
Short selling
- Agent borrows from any agent that has a long position
- An agent with positive excess demand buys from agents with negative excess demand.
- not being able to set aside the required margin amount is the common way that agents with a short position default. 

'''
from esl.economics.markets.walras import excess_demand_model, differentiable_order_message
model = excess_demand_model({p: initial_quote, p2: initial_quote})


market_agent = esl.simulation.identity([0])
trader_agent = esl.simulation.identity([1])

class my_order(differentiable_order_message):
    def __init__(self, sender, recipient, sent, received):
        super().__init__(sender, recipient, sent, received)
        # TODO (Maarten): this should be exposed through base class
        self.sender = sender

    def excess_demand(self, quotes) -> float:
        """
            This is our excesss demand function. It receives a dict with:
            - keys being the property identifiers
            - values being a tuple with the previous quote, and a real number variable such that
                float(quote) * variable
                is a real number that we can use to give demand in real numbers
                (in essence, a continuous function rather than a function with discrete steps)
            In this example, the demand function is simply $3.00 - p(t) for the first property, $4.00 - p(t) for the second,
            and so on.
        :param quotes: A dict with property_identifier keys and pairs (quote, variable)
        :return:
        """
        print(f"The Walrasian price setter suggests the following prices: {quotes}")
        ed = {k: ((i+3.) - (float(v[0]) * v[1])) for i,  (k, v) in enumerate(quotes.items())}
        print(f"Agent {self.sender}'s excess demand at these prices is: {ed}")
        return ed

# def dmd1(x):
#     return -5/x + 5
# def dmd2 (x):
#     return -5/x + 5
# def dmd3 (x):
#     return -5/x + 5

# excess_demand_functions = [dmd1, dmd2, dmd3]

# def clear_market(initial_prices, excess_demand_functions):
#     model = excess_demand_model(initial_prices)
#     model.excess_demand_functions = excess_demand_functions

#     # change other settings for the solver, such as circuit breaker

#     model.circuit_breaker = (0.5, 2.0)
#     return model.compute_clearing_quotes()

# clear_market(initial_price, excess_demand_functions)

# normally the simulation::model class would determine the time, but this is a one-period example
current_time = 0

# The order is sent (at current_time) and received (at current_time), i.e. immediately
message = my_order(trader_agent, market_agent, current_time, current_time)

# We give the message to the model. Normally, we'd use a market agent (esl.economics.markets.walras.price_setter) to do this
model.excess_demand_functions = [message]

multipliers = model.compute_clearing_quotes()

# multipliers
# print(multipliers)

# Since the result is a floating number multiplier to the initial price, we need to decide carefully
# how to round the result back to dollars and cents
for k, v in multipliers.items():

    new_price = price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD)
    print(f"New price for property {k}: {new_price}")


print("We can access the numeric value of the price with float(new_price) = " + str(float(new_price)))

''' IMPORTANT: We may have to del model afterwards, or put it inside a function, 
so that we don't have the error attempt to activate an adept when one is already active in this thread'''
del model

