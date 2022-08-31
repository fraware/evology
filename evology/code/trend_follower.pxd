from libc.math cimport tanh, fmax, log2, isnan
from fund cimport Fund 
cdef float NAN = float("nan")

cdef class TrendFollower(Fund):
    cdef public double time_horizon 

    cdef inline get_price_ema(self, price, price_ema):
        if isnan(price_ema) == False:
            self.trading_signal = log2(price / price_ema)
        else:
            self.trading_signal = NAN