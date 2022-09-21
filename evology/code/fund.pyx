#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

import numpy as np
from libc.math cimport isnan
import cython
cdef float NAN = float("nan")
from cpython cimport array
import array

cdef class Fund:
    """ Creates a Fund object, without specifying its strategy"""

    def __init__(self, cash, asset):

        self.cash = cash
        self.asset = asset
        self.loan = 0.0
        self.margin = 0.0
        self.wealth = 0.0
        self.trading_signal = 0.0
        self.type = str
        self.leverage = 1.0
        self.signal_scale = 1.0
        self.demand = 0.0
        self.previous_wealth = 0.0
        self.annual_return = 0.0
        self.daily_return = 0.0
        self.monthly_return = NAN
        self.excess_10y_return = NAN
        self.return_10y = NAN
        self.excess_monthly_return = NAN
        self.wealth_history_year = []
        self.wealth_history_month = []
        self.net_flow = 0.0
        self.max_short_size = 500000.
        self.age = 0

    def count_wealth(self, double price):
        """ Measure the wealth of the fund and raises error if it is NAN"""
        self.wealth = self.cash + self.asset * price - self.loan + self.margin
        if isnan(self.wealth) == True:
            print(self.type)
            print(self.wealth)
            print(self.net_flow)
            print(self.cash) 
            print(self.asset)
            print(price)
            print(self.loan) 
            print(self.margin)
            raise ValueError('NAN wealth.')

    def compute_excess_demand(self, double price):
        self.demand = self.excess_demand(price)

    def execute_excess_demand(self, double price):
        self.asset += self.demand
        self.cash -= self.demand * price

    def clear_debt(self):
        """ Try to clear fund debt with cash"""
        if self.loan > 0 and self.cash > 0:
            self.cash -= self.loan
            self.loan = 0
        if self.loan < 0:
            self.cash += self.loan
            self.loan = 0

    def cash_gains(self, double dividend, double interest_rate_daily):
        """ Earn dividends on shares and interest on cash"""
        self.cash += interest_rate_daily * self.cash
        self.cash += dividend * self.asset

    def update_margin(self, double price):
        """ Update margin account value if a short position is open"""
        self.cash += self.margin
        self.margin = 0.0
        if self.asset < 0:
            self.margin = abs(self.asset) * price
            self.cash -= abs(self.asset) * price
        if self.margin < 0:
            raise RuntimeError("Negative margin", self.type, self.margin)

    def compute_profit(self):
        cdef double return_prod 
        cdef double return10
        cdef double wealth_before
        cdef double wealth_now
        cdef int length 

        # Compute daily return
        if self.previous_wealth != 0:
            self.daily_return = (
                (self.wealth - self.net_flow) / self.previous_wealth
            ) - 1.0
        else:
            self.daily_return = NAN

        # print("Section:")

        # Compute annual return
        # length = len(self.wealth_history_year)
        # if length == 21: #252:   
        #     return_prod = prod_lis(self.wealth_history_year)
        #     annual_return = geom_mean(return_prod, 21.) #252.)
        #     self.annual_return = annual_return
        # else:
        #     self.annual_return = NAN

        if len(self.wealth_history_year) == 10:
            # print(self.wealth_history_year)
            wealth_before = self.wealth_history_year[0]
            # print(wealth_before)
            wealth_now = self.wealth_history_year[9]
            # print(wealth_now)
            return10 = (wealth_now - wealth_before) / wealth_before
            # print(return10)
            self.return_10y = return10
        else:
            self.return_10y = NAN

        # print("108")
        if len(self.wealth_history_month) == 21:
            wealth_before = self.wealth_history_month[0]
            wealth_now = self.wealth_history_month[20]
            self.monthly_return =  (wealth_now - wealth_before) / wealth_before
        else:
            self.monthly_return = NAN


        # Update previous wealth to current wealth
        self.previous_wealth = self.wealth

    def update_wealth_history(self, double generation):
        cdef double entry
        # Make a history of daily returns
        # if isnan(self.daily_return) == False:
            # entry = float(self.daily_return) + 1.0
        self.wealth_history_month.append(self.wealth - self.net_flow * self.wealth)

        # Make a history of yearly NAV once a year, for 10 years
        if generation % 252 == 0:
            self.wealth_history_year.append(self.wealth - self.net_flow * self.wealth)
            # print(self.wealth_history_year)


        if len(self.wealth_history_year) > 10: 
            # Erase observations older than 10 years
            del self.wealth_history_year[0]

        if len(self.wealth_history_month) > 21:
            # Erase observations older than a month
            del self.wealth_history_month[0]

    def get_assets(self):
        return self.asset

    def get_annual_return(self):
        return self.return_10y

    def get_monthly_return(self):
        return self.monthly_return

cpdef prod_lis(list arr):
    cdef double result = 1.
    cdef int i
    cdef int length = len(arr)
    for i in range(length):
        result = result + result * arr[i]
    return result 

cpdef geom_mean(double product, double periods):
    cdef double result
    result =  (1.0 + (product ** (1.0 / periods) - 1.0)) ** periods - 1.0
    return result 