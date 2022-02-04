#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
from scipy.special import stdtrit
cimport cythonized
import numpy as np
from libc.math cimport isnan, sqrt
from parameters import INTEREST_RATE, SHIELD_DURATION, ShieldResults, ShieldInvestment

cdef double Barr = max(SHIELD_DURATION, ShieldResults) 

cdef double mean(double[:] x) nogil:
    cdef int N = len(x)
    cdef double out = 0.0
    for i in range(N):
        out += x[i]
    return out / N


cdef double std(double[:] x) nogil:
    cdef int N = len(x)
    cdef double _mean = mean(x)
    cdef double out = 0.0
    for i in range(N):
        out += (x[i] - _mean) ** 2
    return sqrt(out / N)


def InvestmentProcedure(pop, generation, returns_tracker, InvestmentHorizon, InvestmentSupply):
    if InvestmentHorizon > 0:
        pop, propSignif, AvgValSignif = Investment(returns_tracker, generation, InvestmentHorizon, pop, InvestmentSupply)
    else:
        propSignif, AvgValSignif = 0, 0
    return returns_tracker, pop, propSignif, AvgValSignif



cdef Investment(double[:, :] returns_tracker, int generation, int InvestmentHorizon, list pop, double InvestmentSupply):

    cdef double TestThreshold
    cdef list TestValues
    cdef double MeanReturns 
    cdef double StdReturns
    cdef double SharpeAbsolute
    cdef double SESharpe
    cdef double TValue
    cdef int countSignifAbsolute
    cdef double SumTValuesAbsolute
    cdef double AbsSumTValuesAbsolute
    cdef cythonized.Individual ind
    cdef double[:, :] ReturnData
    cdef double[:] DataSlice

    if generation > Barr + InvestmentHorizon + ShieldInvestment:
        # Control Investment Horizon.
        if InvestmentHorizon <= 1:
            raise ValueError('Investment horizon <= 1. Impossible to compute Sharpe ratios without standard errors.')
        ReturnData = returns_tracker[generation-InvestmentHorizon:generation,:]
        # Control data size.
        if len(ReturnData) != InvestmentHorizon:
            print(len(ReturnData))
            print(len(InvestmentHorizon))
            raise ValueError('Length of Returndata did not match Investmtent Horizon.')

        # For each fund, estimate Sharpe ratio and its significance.
        TestThreshold = stdtrit(InvestmentHorizon, 0.95)
        TestValuesAbsolute = [0] * len(pop)
        AbsSumTValuesAbsolute = 0

        for i in range(len(pop)):
            DataSlice = ReturnData[:,i]
            MeanReturns = mean(DataSlice)
            StdReturns = std(DataSlice)

            if StdReturns != 0:
                SharpeAbsolute = MeanReturns / StdReturns
            else:
                SharpeAbsolite = np.nan

            if not isnan(SharpeAbsolute):
                SESharpe = sqrt(1 + 0.5 * SharpeAbsolute ** 2) / sqrt(InvestmentHorizon)
                # SESharpe = ((1 + 0.5 * Sharpe ** 2) / InvestmentHorizon) ** 1/2
                TValueAbsolute = (SharpeAbsolute - INTEREST_RATE) / SESharpe
                TestValuesAbsolute[i] = TValueAbsolute
                AbsSumTValuesAbsolute += abs(TValueAbsolute)
            else:
                TestValuesAbsolute[i] = 0

        # Decide investment ratios and apply the investment.
        SumTValuesAbsolute = sum(TestValuesAbsolute)
        countSignifAbsolute = 0
        for i, ind in enumerate(pop):
            if SumTValuesAbsolute != 0:
                ind.investment_ratio = (TestValuesAbsolute[i] / SumTValuesAbsolute) 
            else:
                ind.investment_ratio = 1/len(pop)
            ind.investor_flow = ind.investment_ratio * InvestmentSupply
            ind.cash += ind.investor_flow
            if TestValuesAbsolute[i] > TestThreshold:
                countSignifAbsolute += 1
        propSignifAbsolute = 100 * countSignifAbsolute / len(pop)
        AvgValAbsolute = (AbsSumTValuesAbsolute / len(pop)) / TestThreshold

        return pop, propSignifAbsolute, AvgValAbsolute
    else:
        return pop, 0, 0


