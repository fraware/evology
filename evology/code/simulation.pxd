cdef class Simulation:
    cdef public int max_generations
    cdef public int population_size
    cdef public double interest_rate
    cdef public double interest_rate_daily
    cdef public int seed
    cdef public int generation
    cdef public object data 
    cdef public object disable 
    cdef public object investment_bool
    cdef public list wealth_coords
    cdef public object reset 
    cdef public double noise_process