cimport fund
from libc.math cimport isnan
cimport cython

cdef class Investor:
    cdef object active
    cdef int seed
    cdef int max_generations
    cdef object rng
    cdef object constant_history
    cdef object month_coeff_history
    cdef object year_coeff_history

