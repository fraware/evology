cdef class Fund:
    cdef public double cash
    cdef public double asset
    cdef public double loan
    cdef public double margin
    cdef public double wealth
    cdef public double trading_signal
    cdef public object type
    cdef public double leverage
    cdef public double signal_scale
    cdef public double demand 
    cdef public double previous_wealth
    cdef public double annual_return
    cdef public double daily_return
    cdef public double monthly_return
    # cdef public double excess_annual_return
    cdef public double excess_10y_return
    cdef public double return_10y
    cdef public double excess_monthly_return
    cdef public list wealth_history_year
    cdef public list wealth_history_month
    cdef public double net_flow 
    cdef public double max_short_size
    cdef public object excess_demand
    cdef public int age
