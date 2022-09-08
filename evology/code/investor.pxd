cimport fund
from libc.math cimport isnan
cimport cython

cdef class Investor:
    cdef object active
    cdef int seed
    cdef double max_generations
    cdef object rng
    cdef list constant_history
    cdef list month_coeff_history
    cdef list year_coeff_history

