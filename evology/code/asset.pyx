#cython: boundscheck=False, wraparound=False, initializedcheck=False

import cython
from libc.math cimport sqrt
import numpy as np
from scipy.optimize import root
import warnings


cdef class Asset:

    """ The Asset class defines a company stock. """

    def __init__(self, time_horizon, seed):
        """ Create an asset object and draw its dividend for time_horizon steps"""
        self.time_horizon = time_horizon
        self.initial_price = 100.
        self.initial_dividend = 0.003983
        self.price = self.initial_price 
        self.dividend = self.initial_dividend  
        self.seed = seed
        self.dividend_growth_rate_yearly = 0.01
        self.dividend_growth_rate_daily = (
            (1.0 + self.dividend_growth_rate_yearly) ** (1.0 / 252.0)
        ) - 1.0
        
        self.dividend_volatility = 0.1 / sqrt(252)
        self.dividend_autocorrelation = 0.1
        self.dividend_autocorrelation_lag = 1
        self.ema_horizons = 2 
        self.ema_smoothing_factor = 2 / 3
        self.dividend_series = self.compute_dividend_series()
        self.price_emas = self.price  
        self.volume = 0.0
        self.mismatch = 0.0
        


    def get_dividend(self, generation):
        """ Get the dividend value at a specific time period"""
        self.dividend = self.dividend_series[0, generation]

    def compute_dividend_series(self):
        """ Compute the dividends from an autocorrelated Geometric Brownian Motion"""
        dividend_series = np.zeros((1, self.time_horizon))
        rd_dividend_series = np.zeros((1, self.time_horizon))
        rng = np.random.default_rng(seed=self.seed)
        z_process = rng.standard_normal(self.time_horizon)
        dividend_series[0, 0] = self.dividend
        rd_dividend_series[0, 0] = z_process[0]
        cdef double dividend = self.dividend
        cdef int i
        cdef double wiener_back

        for i in range(self.time_horizon):
            wiener_back = z_process[i]
            if i > self.dividend_autocorrelation_lag:
                wiener_back = (1.0 - self.dividend_autocorrelation**2.) * z_process[
                    i
                ] + self.dividend_autocorrelation * rd_dividend_series[
                    0, i - self.dividend_autocorrelation_lag - 1
                ]
            dividend = abs(
                dividend
                + self.dividend_growth_rate_daily * dividend
                + self.dividend_volatility * dividend * wiener_back
            )
            dividend_series[0, i] = dividend
            rd_dividend_series[0, i] = wiener_back

        return dividend_series

    def compute_price_emas(self):
        """ Compute the current EMA of the asset price for momentum funds"""
        self.price_emas = (
                self.price * self.ema_smoothing_factor
                + self.price_emas * (1.0 - self.ema_smoothing_factor)
            )
        
    def market_clearing(self, pop):
        """ Finds the clearing price for the asset based on population supply and demand
        By finding the root of the excess demand function.
        For now, circuit breaking is not necessary to stabilise price movements."""

        cdef double liquidation = pop.liquidation
        
        def aggregate_demand(double price):
            cdef double result = pop.aggregate_demand(price) + liquidation 
            return result
            
        self.price = root(aggregate_demand, self.price, method="hybr").x
        if self.price < 0:
            self.price = 0.01
            warnings.warn("Negative price converted to 0.01")
