current_price = 100
def aggregated_ed(price):
    return 10 / price

!pip install eslpy
!pip3 install --index-url https://test.pypi.org/simple/ eslpy --force --user

import esl
# print(esl.version())

''' Create property ID for the single asset '''
from esl.law import property
from esl.simulation import identity
i  = identity([0, 1])
p  = property(i)

from esl.economics import price
from esl.economics import currencies
initial_price = price(current_price, currencies.USD)

''' Create a quote '''
from esl.economics.markets import quote
initial_quote = quote(initial_price)

from esl.economics.markets import quote

from esl.economics.markets.walras import excess_demand_model, differentiable_order_message
model = excess_demand_model({p: initial_quote})

market_agent = esl.simulation.identity([0])
trader_agent = esl.simulation.identity([1])


''' ---------------------------------------------- '''



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


current_time = 0

# The order is sent (at current_time) and received (at current_time), i.e. immediately
message = my_order(trader_agent, market_agent, current_time, current_time)

# We give the message to the model. Normally, we'd use a market agent (esl.economics.markets.walras.price_setter) to do this
model.excess_demand_functions = [message]

multipliers = model.compute_clearing_quotes()

# multipliers
print(multipliers)

# Since the result is a floating number multiplier to the initial price, we need to decide carefully
# how to round the result back to dollars and cents
for k, v in multipliers.items():

    new_price = price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD)
    print(f"New price for property {k}: {new_price}")


print("We can access the numeric value of the price with float(new_price) = " + str(float(new_price)))

''' IMPORTANT: We may have to del model afterwards, or put it inside a function, 
so that we don't have the error attempt to activate an adept when one is already active in this thread'''
del model









''' 
Short selling
- Agent borrows from any agent that has a long position
- An agent with positive excess demand buys from agents with negative excess demand.
- not being able to set aside the required margin amount is the common way that agents with a short position default. 

'''


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
print(multipliers)

# Since the result is a floating number multiplier to the initial price, we need to decide carefully
# how to round the result back to dollars and cents
for k, v in multipliers.items():

    new_price = price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD)
    print(f"New price for property {k}: {new_price}")


print("We can access the numeric value of the price with float(new_price) = " + str(float(new_price)))

''' IMPORTANT: We may have to del model afterwards, or put it inside a function, 
so that we don't have the error attempt to activate an adept when one is already active in this thread'''
del model