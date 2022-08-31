from fund cimport Fund 

cdef class NoiseTrader(Fund):
    cdef public list process_series
    cdef public double valuation 
    cdef public double req_rate_return
    cdef public double discount_rate
    cdef public double OU_mean 
    cdef public double OU_rho 
    cdef public double OU_gamma
    cdef public double noise_process
