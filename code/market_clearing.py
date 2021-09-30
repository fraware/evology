from parameters import *
import numpy as np
import os
os.system("pip install --index-url https://test.pypi.org/simple/ eslpy --force")
import esl
print(f"We are running version {esl.version()}")
from esl.economics.markets.walras import excess_demand_model, differentiable_order_message
from esl.law import property
from esl.simulation import identity
from esl.economics.markets import quote
from esl.economics import price
from esl.economics import currencies
import numpy as np

i  = identity([0, 1])
p  = property(i)
i  = identity([0, 1])
p  = property(i)
initial_price = price(10000, currencies.USD)
initial_quote = quote(initial_price)
model = excess_demand_model({p: initial_quote}) # for one asset
 
def solve(my_excess_demand_functions: list):

    # i  = identity([0, 1])
    # p  = property(i)
    # initial_price = price(10000, currencies.USD)
    # initial_quote = quote(initial_price)
    # model = excess_demand_model({p: initial_quote}) # for one asset

    market_agent = esl.simulation.identity([0])
    excess_demand_functions = []

    class OrderWrapper(differentiable_order_message):
        def __init__(self, function, sender, recipient, sent, received):
            super().__init__(sender, recipient, sent, received)
            # TODO (Maarten): this should be exposed through base class
            self.sender = sender
            self.function = function

        def excess_demand(self, quotes) -> dict:
            """
            :param quotes: A dict with property_identifier keys and pairs (quote, variable)
            :return:
            """
            ed = {k: self.function(k, float(v[0]) * v[1]) for i,  (k, v) in enumerate(quotes.items())}
            return ed

    for i, edf in enumerate(my_excess_demand_functions):
        order = OrderWrapper(edf, esl.simulation.identity([i+1]), market_agent, 0, 0)
        excess_demand_functions.append(order) 

    model.excess_demand_functions = excess_demand_functions
    multipliers = model.compute_clearing_quotes() 
    prices = []

    for k, v in multipliers.items():
        prices.append(price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD))
    return prices

def func1(asset_key, price): #value investor
  return ((50_000_000 + 500_000 * price) / price) * (np.tanh(np.log2(10_000) - np.log2(price)) + 0.5) - 500_000

def func2(asset_key, price): #noise trader
  return ((50_000_000 + 500_000 * price) / price) * (np.tanh(np.log2(10_000) - np.log2(price)) + 0.5) - 500_000

def func3(asset_key, price): #trend follower
  return ((50_000_000 + 500_000 * price) / price) * (np.tanh(0) + 0.5) - 500_000


functions = [func1, func2, func3]
new_price = solve(functions)
print(new_price)
print(float(new_price[0]))
print(func1(i, float(new_price[0])))
print(func2(i, float(new_price[0])))
print(func3(i, float(new_price[0])))
    




























##############################
import esl
from esl.economics.markets.walras import excess_demand_model, differentiable_order_message
from esl.law import property
from esl.simulation import identity
from esl.economics.markets import quote
from esl.economics import price
from esl.economics import currencies


# Market clearing for a single asset

def solve(current_price, my_excess_demand_functions: list):

    i  = identity([0, 1])
    p  = property(i)
    initial_price = price(current_price * 100, currencies.USD)
    initial_quote = quote(initial_price)
    model = excess_demand_model({p: initial_quote}) # for one asset

    market_agent = esl.simulation.identity([0])
    excess_demand_functions = []

    class OrderWrapper(differentiable_order_message):
        def __init__(self, function, sender, recipient, sent, received):
            super().__init__(sender, recipient, sent, received)
            # TODO (Maarten): this should be exposed through base class
            self.sender = sender
            self.function = function

        def excess_demand(self, quotes) -> dict:
            """
            :param quotes: A dict with property_identifier keys and pairs (quote, variable)
            :return:
            """
            ed = {k: self.function(k, float(v[0]) * v[1]) for i,  (k, v) in enumerate(quotes.items())}
            return ed

    for i, edf in enumerate(my_excess_demand_functions):
        order = OrderWrapper(edf, esl.simulation.identity([i+1]), market_agent, 0, 0)
        excess_demand_functions.append(order) 

    model.excess_demand_functions = excess_demand_functions
    multipliers = model.compute_clearing_quotes() 
    prices = []

    for k, v in multipliers.items():
        prices.append(price(round(float(initial_price) * v * currencies.USD.denominator), currencies.USD))
    del model
    return prices

def import_edf(pop):
    edf_functions = []
    for ind in pop:
        
        if ind.type == "tf":
            def func_tf(asset_key, p):
                return (ind.wealth * LAMBDA_TF / p) * (np.tanh(SCALE_TF * ind.tsv) + 0.5) - (ind.asset_long - ind.asset_short) 
        edf_functions.append(func_tf)

        if ind.type == "vi":
            def func_vi(asset_key, p):
                return (ind.wealth * LAMBDA_VI / p) * (np.tanh(SCALE_VI * (np.log2(ind[0]) - np.log2(p))) + 0.5) - (ind.asset_long - ind.asset_short)  
            edf_functions.append(func_vi)

        if ind.type == "nt":
            def func_nt(asset_key, p):
                return (ind.wealth * LAMBDA_NT / p) * (np.tanh(SCALE_NT * (np.log2(ind[0] * ind.process) -  np.log2(p))) + 0.5) - (ind.asset_long - ind.asset_short)  
            edf_functions.append(func_nt)
    return edf_functions

def esl_solver(current_price, pop):
    return solve(current_price, import_edf(pop))







'''
Here is a simple optimisation solver for the market clearing algorithm. 
We minimise the squared of aggregate excess demand, under the constraint of
a Limit-Up-Limit-Down (LU-LD) circuit breaker, which limits prices to 
[LD*p(t-1), LU*p(t-1)], with LD=1/2 and LU = 2
'''
from leap_ec import Individual, Representation
from leap_ec import ops, probe
from leap_ec.algorithm import generational_ea
from leap_ec.problem import FunctionProblem
from leap_ec.real_rep import create_real_vector
from leap_ec.real_rep.ops import mutate_gaussian

def ea_solve_noverbose(function, bounds, generations, pop_size,
             mutation_std, maximize=False,
             hard_bounds = True):
    

    if hard_bounds:
        mutation_op = mutate_gaussian(std=mutation_std, hard_bounds=bounds,
                        expected_num_mutations='isotropic')
    else:
        mutation_op = mutate_gaussian(std=mutation_std,
                        expected_num_mutations='isotropic')

    pipeline = [
        ops.tournament_selection,
        ops.clone,
        mutation_op,
        ops.uniform_crossover(p_swap=0.4),
        ops.evaluate,
        ops.pool(size=pop_size)
    ]

    ea = generational_ea(max_generations=generations,
                         pop_size=pop_size,
                         problem=FunctionProblem(function, maximize),
                         stop=lambda pop: (max(pop).fitness < 1),

                         representation=Representation(
                             individual_cls=Individual,
                             initialize=create_real_vector(bounds=bounds)
                         ),

                         pipeline=pipeline)

    best_genome = None
    # print('generation, bsf')
    for g, ind in ea:
        # print(f"{g}, {ind.fitness}")
        best_genome = ind.genome

    return best_genome

def leap_solver(pop, price):
    
    ''' Define squared aggregate ED function '''
    # cum_sum = 0
    # cum_own = 0
    # for ind in pop:
    #     cum_sum += ind[6]
    #     cum_own += ind[3]
    # def agg_ed_solver(x):
    #     return cum_sum / sum(x) - cum_own
    
    def squared_agg_ed(p): # CAREFUL NO LEVERAGE
        result = 0
        for ind in pop:
            # result += (ind.edf(x)) ** 2
                if ind.type == "tf":
                    result += ((ind.cash + ind.asset_long * p - ind.loan) / p) * (np.tanh(SCALE_TF * ind.tsv) + 0.5) - (ind.asset_long - ind.asset_short)
                if ind.type == "vi":
                    result += ((ind.cash + ind.asset_long * p - ind.loan) / p) * (np.tanh(SCALE_VI * (np.log2(ind[0]) - np.log2(p))) + 0.5) - (ind.asset_long - ind.asset_short) 
                if ind.type == "nt":
                    result += ((ind.cash + ind.asset_long * p - ind.loan) / p) * (np.tanh(SCALE_NT * (np.log2(ind[0] * ind.process) -  np.log2(p))) + 0.5) - (ind.asset_long - ind.asset_short)

        # result = result ** 2
        return result
    
    ''' Define the circuit breaker bounds '''
    limit_down = price * 0.5
    # limit_down = 0
    limit_up = price * 2.0
    # limit_up = price * 10.0
    # limit_up = 100_000

    mutation_rate = 100
    
    ''' Run the solver on the squared agg ED function'''
    best_genome = ea_solve_noverbose(squared_agg_ed,
          bounds=[(limit_down, limit_up)], generations = 200, pop_size = 100,
          mutation_std=mutation_rate, hard_bounds = True)
    
    ''' Return the clearing price '''
    return best_genome[0]

# def f(x):
#     return sum(x)**2
# best_genome = ea_solve_noverbose(f,
#           bounds=[(1.1111, 10)], generations = 50, pop_size = 50,
#           mutation_std=0.1, hard_bounds = True) #max = False
# print(best_genome)

def linear_solver(pop, price):

    limit_down = price * 0.5
    limit_up = price * 2.0

    # ED function is (W(p) * Lambda / p)*(tanh(c.phi) +0.5) - S_net
    # We reformulate it to allow for linear solution
    # Assuming no leverage and that phi(t) is constant wrt p(t). 
 
    # Careful, it excludes leverage
    A, B = 0, 0
    for ind in pop:
        if ind.type == "tf":
            A += (np.tanh(SCALE_TF * ind.tsv) + 0.5) * (ind.cash - ind.loan)
            B += (np.tanh(SCALE_TF * ind.tsv) - 0.5) * ind.asset_long + ind.asset_short
        if ind.type == "vi":
            A += (np.tanh(SCALE_VI * ind.tsv) + 0.5) * (ind.cash - ind.loan)
            B += (np.tanh(SCALE_VI * ind.tsv) - 0.5) * ind.asset_long + ind.asset_short
        if ind.type == "nt":
            A += (np.tanh(SCALE_NT * ind.tsv) + 0.5) * (ind.cash - ind.loan)
            B += (np.tanh(SCALE_NT * ind.tsv) - 0.5) * ind.asset_long + ind.asset_short

    price = - A / B
    print("price, A/P +B, A, B")
    print(price)
    print(A / price + B)
    print(A)
    print(B)

    if price > limit_up:
        price = limit_up
        print("limit_up applied " + str(limit_up))
    elif price < limit_down:
        price = limit_down
        print("limit_down applied " + str(limit_down))
    return price

def absolute_solver(pop):
    def squared_agg_ed(p): # CAREFUL NO LEVERAGE
        result = 0
        for ind in pop:
            # result += (ind.edf(x)) ** 2
                if ind.type == "tf":
                    result += ((ind.cash + ind.asset_long * p - ind.loan) / p) * (np.tanh(SCALE_TF * ind.tsv) + 0.5) - (ind.asset_long - ind.asset_short)
                if ind.type == "vi":
                    result += ((ind.cash + ind.asset_long * p - ind.loan) / p) * (np.tanh(SCALE_VI * (np.log2(ind[0]) - np.log2(p))) + 0.5) - (ind.asset_long - ind.asset_short) 
                if ind.type == "nt":
                    result += ((ind.cash + ind.asset_long * p - ind.loan) / p) * (np.tanh(SCALE_NT * (np.log2(ind[0] * ind.process) -  np.log2(p))) + 0.5) - (ind.asset_long - ind.asset_short)

        # result = result ** 2
        return result
    
        ''' Run the solver on the squared agg ED function'''
    best_genome = ea_solve_noverbose(squared_agg_ed,
          bounds = [(0, 50000)],
          generations = 200, pop_size = 100,
          mutation_std=100, hard_bounds = True)
    
    ''' Return the clearing price '''
    return best_genome[0]







# def f(x):
#     """A real-valued function to optimized."""
#     return sum(x)**2


# best_genome = ea_solve_noverbose(f,
#         bounds = [(0, 20000)],
#         generations = 200, pop_size = 100,
#         mutation_std=0.1, hard_bounds = True)

# ''' Return the clearing price '''
# print("STD 0.1")
# print(best_genome[0])

# best_genome = ea_solve_noverbose(f,
#         bounds = [(0, 20000)],
#         generations = 200, pop_size = 100,
#         mutation_std=1, hard_bounds = True)

# ''' Return the clearing price '''
# print("STD 1")
# print(best_genome[0])

# best_genome = ea_solve_noverbose(f,
#         bounds = [(0, 20000)],
#         generations = 200, pop_size = 100,
#         mutation_std=100, hard_bounds = True)

# ''' Return the clearing price '''
# print("STD 100")
# print(best_genome[0])