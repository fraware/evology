#cython: boundscheck=False, wraparound=False, initializedcheck=False

from libc.math cimport isnan
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
        self.constant_history = rng.normal(-0.0094, 0.005, self.max_generations)
        self.month_coeff_history = rng.normal(0.1673, 0.096, self.max_generations)
        self.year_coeff_history = rng.normal(0.0044, 0.02, self.max_generations)

    def investment_flows(self, pop, int generation):
        cdef fund.Fund ind
        cdef double invested_amount

        # We need to have the 10Y return as fund variable
        # Double check the monthly return as fund variable

        if self.active == True:
            for ind in pop.agents:
                if (
                    isnan(ind.excess_monthly_return) == False
                    and isnan(ind.monthly_return) == False
                ):
                    invested_amount = (
                        (self.constant_history[generation] + self.month_coeff_history[generation] * ind.excess_monthly_return) / 21.0
                    ) * ind.wealth
                    ind.net_flow = invested_amount
                    ind.cash += ind.net_flow
        
