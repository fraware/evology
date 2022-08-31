#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

# from fund import Fund
from fund cimport Fund
import numpy as np
from math import tanh, log2
import cython

cdef class NoiseTrader(Fund):
    """ A trader whose trading signal is a fundamental valuation perturbed by an Orstein-Uhlenbeck process"""

    # OU_mean = 1.0
    # OU_rho = 0.00045832561
    # OU_rho = 0.005
    # OU_gamma = 0.2 * np.sqrt(1.0 / 252.0)
    # process_series = []
    # noise_process = 0.0

    def __init__(
        self, cash, asset, req_rate_return, interest_rate, dividend_growth_rate
    ):
        super().__init__(cash, asset)
        self.type = "NT"
        self.valuation = 100.
        self.req_rate_return = req_rate_return
        self.discount_rate = (
            1.0 + (interest_rate + self.req_rate_return) - dividend_growth_rate
        ) ** (1.0 / 252.0) - 1.0
        self.OU_mean = 1.0
        # self.OU_rho = 0.00045832561
        self.OU_rho = 0.005
        self.OU_gamma = 0.2 * np.sqrt(1.0 / 252.0)
        self.process_series = []
        self.noise_process = 0.0

    # @classmethod
    def compute_noise_process(self, max_generations, seed):
        """ Generate an OU process for max_generation time periods"""
        rng = np.random.default_rng(seed=seed + 1)
        randoms = rng.standard_normal(max_generations)
        process_series = []
        # value = cls.OU_mean
        value = self.OU_mean

        for i in range(max_generations):
            value = abs(
                value
                + self.OU_rho * (log2(self.OU_mean) - log2(value))
                + self.OU_gamma * randoms[i]
                # + cls.OU_rho * (log2(cls.OU_mean) - log2(value))
                # + cls.OU_gamma * randoms[i]
            )
            process_series.append(value)

        return process_series

    def get_noise_process(self, generation):
        """ Access current value of the noise process"""
        
        self.trading_signal = self.process_series[generation]

    def update_valuation(self, dividend, interest_rate_daily):
        self.valuation = (
            dividend * (1.0 + interest_rate_daily) / self.discount_rate
        ) * self.trading_signal
        if self.valuation < 0:
            raise RuntimeError("Negative NT valuation", self.valuation)

    def get_excess_demand_function(self):
        """ Formulates excess demand for the asset"""
        self.trading_signal = self.valuation * self.trading_signal
        def func(price):
            signal = tanh(self.signal_scale * log2(self.trading_signal / max(price, 0.0001)))
            return self.leverage * signal * self.wealth / price - self.asset
        self.excess_demand = func

    def update_trading_signal(self, dividend, interest_rate_daily, generation, price, price_ema):
        self.get_noise_process(generation)
        self.update_valuation(dividend, interest_rate_daily)
