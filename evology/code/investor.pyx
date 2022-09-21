#cython: boundscheck=False, wraparound=False, initializedcheck=False

from libc.math cimport isnan, log
cimport cython
cimport fund
import numpy as np

cdef class Investor:
    """ Creates the investor object, who invests in funds based on their performance
    net flows based on analysis based on the data of Ka and Ho, 2019 """
    def __init__(self, investment_bool, seed, max_generations):
        self.active = investment_bool
        self.seed = seed
        self.max_generations = max_generations
        rng = np.random.default_rng(seed=seed + 2)
        #self.constant_history = rng.normal(-0.0094, 0.005, self.max_generations)
        #self.month_coeff_history = rng.normal(0.1673, 0.096, self.max_generations)
        #self.year_coeff_history = rng.normal(0.0044, 0.02, self.max_generations)

    def investment_flows(self, pop, int generation):
        cdef fund.Fund ind
        cdef double flow_fraction
        if self.active == True:
            for ind in pop.agents:
                if (
                    isnan(ind.excess_monthly_return) == False and ind.previous_wealth > 0
                ):
                    flow_fraction= (
                        (
                            1.3401
                            + 0.1649 * ind.excess_monthly_return * 100.
                            + 0.0248 * ((ind.excess_monthly_return * 100.) ** 2.)
                            - 1.2968 * log(ind.age / 252.)
                            + 0.2946 * log(ind.previous_wealth / 1000000.)
                            ) / 21.0
                    ) 

                    if isnan(flow_fraction) == True:
                        print(ind.excess_monthly_return)
                        print(ind.age / 252.)
                        print(ind.previous_wealth / 1000000.)
                        raise RuntimeError('NaN flow fraction')
                    ind.net_flow = flow_fraction / 100.
                    ind.cash += ind.net_flow * ind.previous_wealth
        
