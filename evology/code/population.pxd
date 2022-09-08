cdef class Population:
    cdef public double cash_nominal
    cdef public double asset_nominal
    cdef public int size 
    cdef public int max_generations
    cdef public list wealth_coords
    cdef public list agents
    cdef public double interest_rate
    cdef public double dividend_growth_rate
    cdef public int seed 
    cdef public object aggregate_demand 
    cdef public double spoils
    cdef public object shutdown
    cdef public double wealthNT
    cdef public double wealthVI 
    cdef public double wealthTF
    cdef public double wshareNT
    cdef public double wshareVI
    cdef public double wshareTF
    cdef public double VI_val 
    cdef public double average_10annual_return 
    cdef public double NT_flows 
    cdef public double VI_flows 
    cdef public double TF_flows 
    cdef public double NT_asset 
    cdef public double VI_asset 
    cdef public double TF_asset 
    cdef public double NT_cash 
    cdef public double VI_cash 
    cdef public double TF_cash 
    cdef public double NT_return 
    cdef public double VI_return 
    cdef public double TF_return 
    cdef public double asset_supply
    cdef public int replacements
    cdef public list noise_process
    cdef public double liquidation 
    cdef public double average_monthly_return
    cdef public double NT_returns
    cdef public double VI_returns
    cdef public double TF_returns