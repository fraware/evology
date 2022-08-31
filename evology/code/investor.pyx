#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

from libc.math cimport isnan
cimport cython
cimport fund

cdef class Investor:
    """ Creates the investor object, who invests in funds based on their performance"""
    def __init__(self, investment_bool):
        self.active = investment_bool

    def investment_flows(self, pop):
        cdef fund.Fund ind
        cdef double invested_amount
        # net capital flows based on Ka and Ho, 2019
        if self.active == True:
            for ind in pop.agents:
                if (
                    isnan(ind.excess_monthly_return) == False
                    and isnan(ind.monthly_return) == False
                ):
                    invested_amount = (
                        (-0.0012 + 0.1089 * ind.excess_monthly_return) / 21.0
                    ) * ind.wealth
                    ind.net_flow = invested_amount
                    ind.cash += ind.net_flow
        
