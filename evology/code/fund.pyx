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
        self.monthly_return = 0.0
        self.excess_annual_return = 0.0
        self.excess_monthly_return = 0.0
        self.wealth_history_year = []
        self.wealth_history_month = []
        self.net_flow = 0.0
        self.max_short_size = 500000.

    def count_wealth(self, double price):
        """ Measure the wealth of the fund and raises error if it is NAN"""
        self.wealth = self.cash + self.asset * price - self.loan + self.margin
        if isnan(self.wealth) == True:
            print(self.type)
            print(self.wealth)
            print(self.cash) 
            print(self.asset)
            print(price)
            print(self.loan) 
            print(self.margin)
            raise ValueError('NAN wealth.')

    def compute_excess_demand(self, price):
        self.demand = self.excess_demand(price)

    def execute_excess_demand(self, price):
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

    def cash_gains(self, dividend, interest_rate_daily):
        """ Earn dividends on shares and interest on cash"""
        self.cash += interest_rate_daily * self.cash
        self.cash += dividend * self.asset

    def update_margin(self, price):
        """ Update margin account value if a short position is open"""
        self.cash += self.margin
        self.margin = 0.0
        if self.asset < 0:
            self.margin = abs(self.asset) * price
            self.cash -= abs(self.asset) * price
        if self.margin < 0:
            raise RuntimeError("Negative margin", self.type, self.margin)




    def compute_profit(self):

        # np.prod seemed to slow down the code

        cdef array.array hist = array.array('f', self.wealth_history_year)
        cdef array.array hist_month = array.array('f', self.wealth_history_month)
        

        # Compute daily return
        if self.previous_wealth != 0:
            self.daily_return = (
                (self.wealth - self.net_flow) / self.previous_wealth
            ) - 1.0
        else:
            self.daily_return = NAN



        # Compute annual return
        # if len(self.wealth_history_year) == 252:
        if len(hist) == 252:   

            # Compute annualised geometric mean of daily returns
            self.annual_return = (
                1.0 + ((prod(hist)) ** (1.0 / 252.0) - 1.0)
            ) ** 252.0 - 1.0

        if len(hist_month) == 21:
            # Compute monthly geometric mean of daily returns
            self.monthly_return = (
                1.0 + ((prod(hist_month)) ** (1.0 / 21.0) - 1.0)
            ) ** 21.0 - 1.0

        else:
            self.annual_return = NAN

        # Update previous wealth to current wealth
        self.previous_wealth = self.wealth

    def update_wealth_history(self):
        # Make a history of daily returns

        if isnan(self.daily_return) == False:
            entry = float(self.daily_return) + 1.0
            self.wealth_history_year.append(entry)
            self.wealth_history_month.append(entry)

        if len(self.wealth_history_year) > 252:
            # Erase observations older than a year
            del self.wealth_history_year[0]

        if len(self.wealth_history_month) > 21:
            # Erase observations older than a month
            del self.wealth_history_month[0]

    def get_assets(self):
        return self.asset

    def get_annual_return(self):
        return self.annual_return

    def get_monthly_return(self):
        return self.monthly_return

cpdef prod(array.array arr):
    cdef double result = 1.
    cdef int i
    cdef int length = len(arr)
    for i in range(length):
        result = result + result * arr[i]
    return result 