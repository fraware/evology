#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

from libc.math cimport log2, tanh, isnan
from fund cimport Fund
import cython 
cdef float NAN = float("nan")

cdef class TrendFollower(Fund):
    """ Defines the momentum trader class"""
    
    def __init__(self, double cash, double asset, int time_horizon):
        super().__init__(cash, asset)
        self.time_horizon = time_horizon # Changing time horizon needs to change the ema horizon in asset.pyx
        self.type = "TF"

    def get_price_ema(self, price, price_ema):
        self.price_ema = price_ema
        if isnan(price_ema) == False:
            # TFs stay around an allocation of 50% stocks, 50% bonds/cash
            # If price > price_ema, buy signal // inverse is a sell signal
            # TF size needs to stay low enough otherwise signal snowballs
            self.trading_signal = 0.5 + (price / price_ema) - 1.
        else:
            self.trading_signal = NAN

    def get_excess_demand_function(self):

        def func(price):
            if isnan(self.trading_signal) == False:
                # signal = tanh(self.signal_scale * (self.trading_signal + 0.0)) + 0.0
                # return self.leverage * signal * self.wealth / price - self.asset
                return self.leverage * tanh(log2(price / self.price_ema)) * self.wealth / price - self.asset
            else:
                return 0

        self.excess_demand = func

    def update_trading_signal(self, double dividend, double interest_rate_daily, int generation, double price, double price_ema):
        if generation >= self.time_horizon:
            self.get_price_ema(price, price_ema)
        else:
            self.get_price_ema(price, NAN)

