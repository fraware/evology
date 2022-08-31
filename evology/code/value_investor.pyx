#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

from fund cimport Fund
from libc.math cimport tanh, log2


cdef class ValueInvestor(Fund):
    """ Defines the value investor class"""
    def __init__(
        self, cash, asset, req_rate_return, interest_rate, dividend_growth_rate
    ):
        super().__init__(cash, asset)
        self.req_rate_return = req_rate_return
        self.type = "VI"
        self.valuation = 100.
        self.discount_rate = (
            1.0 + (interest_rate + self.req_rate_return) - dividend_growth_rate
        ) ** (1.0 / 252.0) - 1.0

    def update_valuation(self, dividend, interest_rate_daily):
        self.valuation = dividend * (1.0 + interest_rate_daily) / self.discount_rate
        if self.valuation < 0:
            raise RuntimeError("Negative VI valuation", self.valuation)


    def compute_trading_signal(self, price):
        self.trading_signal = log2(self.valuation / price)

    def get_excess_demand_function(self):

        def func(price):
            signal = tanh(self.signal_scale * log2((self.valuation) / max(price, 0.0001)))
            return self.leverage * signal * self.wealth / price - self.asset

        self.excess_demand = func

    def update_trading_signal(self, dividend, interest_rate_daily, generation, price, price_ema):
        self.update_valuation(dividend, interest_rate_daily)

