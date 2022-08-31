#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

from libc.math cimport log2, tanh, isnan
from fund cimport Fund
import cython 
cdef float NAN = float("nan")

cdef class TrendFollower(Fund):
    """ Defines the momentum trader class"""
    
    def __init__(self, cash, asset, time_horizon):
        super().__init__(cash, asset)
        self.time_horizon = time_horizon
        self.type = "TF"

    # def get_price_ema(self, price, price_ema):
    #     if isnan(price_ema) == False:
    #         self.trading_signal = log2(price / price_ema)
    #     else:
    #         self.trading_signal = np.nan

    def get_excess_demand_function(self):

        def func(price):
            if isnan(self.trading_signal) == False:
                signal = self.signal_scale * (self.trading_signal + 0.5)
                return self.leverage * signal * self.wealth / price - self.asset
            else:
                return 0

        self.excess_demand = func

    def update_trading_signal(self, dividend, interest_rate_daily, generation, price, price_ema):
        if generation >= self.time_horizon:
            self.get_price_ema(price, price_ema)
        else:
            self.get_price_ema(price, NAN)

