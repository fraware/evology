cimport fund
from libc.math cimport isnan
cimport cython

cdef class Investor:
    cdef object active

    # cdef inline investment_flows(self, list pop):
    #     cdef fund.Fund ind
    #     cdef double invested_amount
    #     # net capital flows based on Ka and Ho, 2019
    #     if self.active == True:
    #         for ind in pop.agents:
    #             if (
    #                 isnan(ind.excess_monthly_return) == False
    #                 and isnan(ind.monthly_return) == False
    #             ):
    #                 invested_amount = (
    #                     (-0.0012 + 0.1089 * ind.excess_monthly_return) / 21.0
    #                 ) * ind.wealth
    #                 ind.net_flow = invested_amount
    #                 ind.cash += ind.net_flow

