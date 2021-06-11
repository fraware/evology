import market
import numpy as np

'''
Here is a simple optimisation solver for the market clearing algorithm. 
We minimise the squared of aggregate excess demand, under the constraint of
a Limit-Up-Limit-Down (LU-LD) circuit breaker, which limits prices to 
[LD*p(t-1), LU*p(t-1)], with LD=1/2 and LU = 2
'''

from leap_ec import ops
from leap_ec.context import context
from leap_ec.algorithm import generational_ea
from leap_ec.real_rep.ops import mutate_gaussian
from leap_ec.representation import Representation
from leap_ec.individual import Individual
from leap_ec.problem import FunctionProblem
from leap_ec.decoder import IdentityDecoder
from leap_ec.real_rep.initializers import create_real_vector

def ea_solve_noverbose(function, bounds, generations=100, pop_size=2,
             mutation_std=1.0, maximize=False, viz=False, viz_ylim=(0, 1)):
    pipeline = [
        ops.tournament_selection,
        ops.clone,
        mutate_gaussian(std=mutation_std),
        ops.uniform_crossover(p_swap=0.4),
        ops.evaluate,
        ops.pool(size=pop_size)
    ]
    ea = generational_ea(generations=generations, pop_size=pop_size,
                         problem=FunctionProblem(function, maximize),

                         representation=Representation(
                             individual_cls=Individual,
                             decoder=IdentityDecoder(),
                             initialize=create_real_vector(bounds=bounds)
                         ),

                         pipeline=pipeline)
    best_genome = None
    for g, ind in ea:
        best_genome = ind.genome
    return best_genome


def leap_solver(aggregate_ed, price):
    ''' First define squared aggregate demand '''
    def squared_agg_ed(x):
        result = aggregate_ed(x) ** 2
        return result
    
    ''' Then define the circuit breaker bounds '''
    limit_down = price * 0.5
    limit_up = price * 2.0
    
    ''' Run the solver '''
    best_genome = ea_solve_noverbose(squared_agg_ed,
          bounds=[(limit_down, limit_up)], generations = 50, pop_size = 500,
          mutation_std=0)
    
    ''' Return the clearing price '''
    ''' TODO: replace this clearing by the better ESL solver '''
    return(market.truncate(best_genome[0],3))

def solver_linear_shortcut(pop, price):
    cum_sum = 0
    cum_own = 0
    for ind in pop:
        cum_sum += ind[6]
        cum_own += ind[3]
        
    candidate = (cum_sum / cum_own)
    
    limit_down = price * 0.5
    limit_up = price * 2.0
    
    if candidate < limit_down:
        candidate = limit_down
    if candidate > limit_up:
        candidate = limit_up
        
    new_price = candidate
        
    return new_price 