from math import sqrt
import numpy as np
from scipy.optimize import root
import warnings
from population import Population


class Asset:

    """ The Asset class defines a company stock. """

    dividend_growth_rate_yearly = 0.01
    dividend_growth_rate_daily = (
        (1.0 + dividend_growth_rate_yearly) ** (1.0 / 252.0)
    ) - 1.0
    dividend_volatility = 0.1 / sqrt(252)
    dividend_autocorrelation = 0.1
    dividend_autocorrelation_lag = 1
    ema_horizons = 2 
    ema_smoothing_factor = 2 / 3
    initial_price = 100
    initial_dividend = 0.003983

    def __init__(self, time_horizon, seed):
        """ Create an asset object and draw its dividend for time_horizon steps"""
        self.time_horizon = time_horizon
        self.price = Asset.initial_price 
        self.dividend = Asset.initial_dividend  
        self.seed = seed
        self.dividend_series = self.compute_dividend_series(
            self.time_horizon, self.seed
        )
        self.price_emas = self.price  
        self.volume = 0.0
        self.mismatch = 0.0

    def get_dividend(self, generation):
        """ Get the dividend value at a specific time period"""
        self.dividend = self.dividend_series[0, generation]

    def compute_dividend_series(self, time_horizon, seed):
        """ Compute the dividends from an autocorrelated Geometric Brownian Motion"""
        dividend_series = np.zeros((1, time_horizon))
        rd_dividend_series = np.zeros((1, time_horizon))
        rng = np.random.default_rng(seed=seed)
        z_process = rng.standard_normal(time_horizon)
        dividend_series[0, 0] = self.dividend
        rd_dividend_series[0, 0] = z_process[0]
        dividend = self.dividend

        for i in range(time_horizon):
            wiener_back = z_process[i]
            if i > Asset.dividend_autocorrelation_lag:
                wiener_back = (1.0 - Asset.dividend_autocorrelation**2) * z_process[
                    i
                ] + Asset.dividend_autocorrelation * rd_dividend_series[
                    0, i - Asset.dividend_autocorrelation_lag - 1
                ]
            dividend = abs(
                dividend
                + Asset.dividend_growth_rate_daily * dividend
                + Asset.dividend_volatility * dividend * wiener_back
            )
            dividend_series[0, i] = dividend
            rd_dividend_series[0, i] = wiener_back

        return dividend_series

    def compute_price_emas(self):
        """ Compute the current EMA of the asset price for momentum funds"""
        self.price_emas = (
                self.price * Asset.ema_smoothing_factor
                + self.price_emas * (1.0 - Asset.ema_smoothing_factor)
            )
        

    def market_clearing(self, pop):
        """ Finds the clearing price for the asset based on population supply and demand
        By finding the root of the excess demand function."""
        
        def pod_aggregate_demand(price):
            return pop.aggregate_demand(price) + pop.liquidation 

        self.price = root(pod_aggregate_demand, self.price, method="hybr").x
        # TODO: do we need circuit breaker?
        if self.price < 0:
            self.price = 0.01
            warnings.warn("Negative price converted to 0.01")
