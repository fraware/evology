from fund cimport Fund 
from libc.math cimport tanh, fmax, log2

cdef class ValueInvestor(Fund):
    cdef public list process_series
    cdef public double valuation 
    cdef public double req_rate_return
    cdef public double discount_rate

    # cdef inline compute_trading_signal(self, price):
    #     self.trading_signal = log2(self.valuation / price)