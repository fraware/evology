cdef class Asset:
    cdef public double dividend_growth_rate_yearly
    cdef public double dividend_growth_rate_daily
    cdef public double dividend_volatility
    cdef public double dividend_autocorrelation
    cdef public int dividend_autocorrelation_lag
    cdef public int ema_horizons
    cdef public int time_horizon
    cdef public double ema_smoothing_factor
    cdef public double initial_price
    cdef public double initial_dividend
    cdef public double price
    cdef public double dividend
    cdef public int seed
    cdef public double volume 
    cdef public double mismatch
    cdef public double price_emas
    cdef public double[:,:] dividend_series