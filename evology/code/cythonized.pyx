#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
# See https://stackoverflow.com/questions/30564253/cython-boundscheck-true-faster-than-boundscheck-false
from libc.math cimport tanh

cpdef _big_edf(
    double ToLiquidate,
    double SCALE_TF,
    double LeverageTF,
    double LeverageVI,
    double LeverageNT,
    long[:] types,
    double[:] wealths,
    double[:] assets,
    double[:] tsvs,
    double[:] index_zeros,
    double[:] processes,
    double price,
):
    cdef double result = ToLiquidate
    cdef int i
    cdef long t
    for i in range(len(types)):
        t = types[i]
        if t == 0:
            LeverageTF
            wealths[i]
            result += (LeverageTF * wealths[i] / price) * tanh(SCALE_TF * tsvs[i]) - assets[i]
        elif t == 1:
            result += (LeverageVI * wealths[i] / price) * tanh((5/index_zeros[i]) * (index_zeros[i] - price)) - assets[i]
        elif t == 2:
            result += (LeverageNT * wealths[i] / price) * tanh((5/(index_zeros[i] * processes[i])) * (index_zeros[i] * processes[i] - price)) - assets[i]
    return result
