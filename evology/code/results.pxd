cimport numpy as np

cdef class Result:
    cdef public int max_generations
    # cdef public np.ndarray[double, ndim=2] data
    cdef public double[:,:] data
    cdef public list variables