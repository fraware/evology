from fund cimport Fund 
from libc.math cimport tanh, fmax, log2

cdef class NoiseTrader(Fund):
    cdef public list process_series
    cdef public double valuation 
    cdef public double req_rate_return
    cdef public double discount_rate
    cdef public double OU_mean 
    cdef public double OU_rho 
    cdef public double OU_gamma
    cdef public double noise_process



    # cdef inline get_excess_demand_function(self):
    #     """ Formulates excess demand for the asset"""
    #     self.trading_signal = self.valuation * self.trading_signal
    #     def func(price):
    #         signal = tanh(self.signal_scale * log2(self.trading_signal / fmax(price, 0.0001)))
    #         return self.leverage * signal * self.wealth / price - self.asset
    #     self.excess_demand = func

    # cdef inline update_trading_signal(self, dividend, interest_rate_daily, generation, price, price_ema):
    #     self.get_noise_process(generation)
    #     self.update_valuation(dividend, interest_rate_daily)