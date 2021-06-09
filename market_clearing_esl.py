# import esl
# from esl.law import property
# from esl.simulation import identity
# from esl.economics import price
# from esl.economics import currencies
# from esl.economics.markets import quote
# from esl.economics.markets.walras import excess_demand_model, differentiable_order_message

# def solve(excess_demand_functions: list):
#     i  = identity([0, 1])
#     p  = property(i)
#     initial_price = price(int(1.23 * currencies.USD.denominator), currencies.USD)
#     initial_quote = quote(initial_price)
#     market_agent = esl.simulation.identity([0])
#     excess_demand_functions = []
#     model = excess_demand_model({p: initial_quote})

#     # for i, ed in enumerate(my_excess_demand_functions):

#     #     order = ed(esl.simulation.identity([i+1]), market_agent, 0, 0)

#     #     excess_demand_functions.append(order) 

#     model.excess_demand_functions = excess_demand_functions
#     multipliers = model.compute_clearing_quotes() 

#     prices = []

#     for k, v in multipliers.items():

#         prices.append(price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD))


#     del model
#     return prices

# def aggregate_ed1(x):
#     return 3 * x - 10

# def aggregate_ed2(x):
#     return 5 * x - 7

# aggregate_ed = [aggregate_ed1, aggregate_ed2]

# prices = solve(aggregate_ed)
# print(prices)

''' As understood on 09/06: ed1, ed2 would have to be orders, not functions '''

import esl
from esl.law import property
from esl.simulation import identity
from esl.economics import price
from esl.economics import currencies
from esl.economics.markets import quote
from esl.economics.markets.walras import excess_demand_model, differentiable_order_message

class my_order(differentiable_order_message):
    def __init__(self, sender, recipient, sent, received):
        super().__init__(sender, recipient, sent, received)
        # TODO (Maarten): this should be exposed through base class
        self.sender = sender

    def excess_demand(self, quotes) -> float:
        print(f"The Walrasian price setter suggests the following prices: {quotes}")
        ed = {k: ((i+3.) - (float(v[0]) * v[1])) for i,  (k, v) in enumerate(quotes.items())}
        print(f"Agent {self.sender}'s excess demand at these prices is: {ed}")
        return ed
    
# order = my_order(trader_agent, market_agent, current_time, current_time)

def solve(my_excess_demand_functions: list):
    
     i  = identity([0, 1])
     p  = property(i)
     initial_price = price(int(1.23 * currencies.USD.denominator), currencies.USD)
     initial_quote = quote(initial_price)
     model = excess_demand_model({p: initial_quote})
    
     market_agent = esl.simulation.identity([0])
     excess_demand_functions = []
     for i, ed in enumerate(my_excess_demand_functions):
         order = ed(esl.simulation.identity([i+1]), market_agent, 0, 0)
         excess_demand_functions.append(order) 
     model.excess_demand_functions = excess_demand_functions
     print(excess_demand_functions)
     multipliers = model.compute_clearing_quotes() 
     prices = []
     for k, v in multipliers.items():
         prices.append(price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD))
     del model
     return prices

def ed1(x):
    return 3 * x - 10

def ed2(x):
    return 5 * x - 7

functions = [ed1, ed2]

solve(functions)