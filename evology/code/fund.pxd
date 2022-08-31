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

    # cdef count_wealth(self, price)
    # cdef compute_excess_demand(self, price)
    # cdef execute_excess_demand(self, price)
    # cdef clear_debt(self)
    # cdef cash_gains(self, dividend, interest_rate_daily)
    # cdef update_margin(self, price)
    # cdef compute_profit(self)
    # cdef update_wealth_history(self)
    # cdef get_assets(self)
    # cdef get_annual_return(self)
    # cdef get_monthly_return(self)
