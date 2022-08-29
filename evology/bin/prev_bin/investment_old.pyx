#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

cimport cythonized
import numpy as np
import time 
from libc.math cimport isnan, sqrt, exp
from parameters import INTEREST_RATE, SHIELD_DURATION, ShieldResults, ShieldInvestment
cdef float NAN
NAN = float("nan")

cdef double Barr = max(SHIELD_DURATION, ShieldResults) 

cdef double mean(double[:] x) nogil:
    cdef int N = len(x)
    cdef double out = 0.0
    cdef int i = 0
    for i in range(N):
        out += x[i]
    return out / N

cdef double std(double[:] x) nogil:
    cdef int N = len(x)
    cdef double _mean = mean(x)
    cdef double out = 0.0
    cdef int i = 0
    for i in range(N):
        out += (x[i] - _mean) ** 2
    return sqrt(out / N)

cdef double pearson(double[:] x, double[:] y) nogil:
    cdef int N = len(x)
    cdef double mx = mean(x)
    cdef double my = mean(y)
    cdef double num = 0.0
    cdef double denum1 = 0.0
    cdef double denum2 = 0.0
    cdef double result
    cdef double P

    for i in range(N):
        num += (x[i] - mx) * (y[i] - my)
        denum1 += (x[i] - mx) ** 2
        denum2 += (y[i] - my) ** 2

    result = num / sqrt(denum1 * denum2)

    if result < -1.1 or result > 1.1:
        raise ValueError('Pearson correlation out of bounds.')

    return result

cdef compute_sharpe(cythonized.Individual ind, double[:] DataSlice):
    cdef double std_value = std(DataSlice)
    if std_value != 0.0:
        ind.sharpe = mean(DataSlice) / std_value
    else:
        ind.sharpe = NAN
    return ind

cdef compare_sharpe(list pop, double[:,:] ReturnData, double InvestmentHorizon, double TestThreshold, double InvestmentIntensity):
    
    cdef cythonized.Individual ind
    cdef cythonized.Individual ind2
    cdef double T
    cdef double P 
    cdef double S 
    cdef double S2
    cdef double term
    cdef double total_tvalue_cpr = 0.0
    cdef double sum_inv_ratio = 0.0
    cdef double countSignif = 0.0
    cdef double sum_tvalue_cpr_abs = 0.0
    cdef double total_tvalue_cpr_neg = 0.0
    cdef double num_test = 0.0
    cdef double num_signif_test = 0.0
    cdef double SE 
    cdef list bounds
    cdef double number_deviations = 0.0
    cdef double sum_exp_tval = 0.0
    cdef double Sharpe_diff = 0.0

    #print("---")
    #print(TestThreshold)

    for i, ind in enumerate(pop):
        ind.tvalue_cpr = 0.0
        if isnan(ind.sharpe) == False:
            DataSlice = ReturnData[:,i]
            S = ind.sharpe
            ''' Then we compare to other funds with non-NAN Sharpes'''
            for j, ind2 in enumerate(pop):
                if j != i and isnan(ind2.sharpe) == False:
                    ''' We have selected another fund with defined Sharpe'''
                    DataSlice2 = ReturnData[:,j]
                    S2 = ind2.sharpe
                    if isnan(S2) == False:
                        # T test for similar variances (difference in std betw 0.5 and 2)
                        # T = (S - S2) / ((sqrt( ((InvestmentHorizon - 1.0) * (std(DataSlice) ** 2) + (InvestmentHorizon - 1.0) * (std(DataSlice2) ** 2)))/(2.0 * InvestmentHorizon - 2)) * sqrt (2.0 / InvestmentHorizon))                    
                        # Simple T Test
                        # T = (S - S2) / sqrt((2/InvestmentHorizon) * ((std(DataSlice) ** 2 + std(DataSlice2) ** 2) / 2))
                        
                        # Welch test (T test for unequal variances, difference in std > 2)
                        # T = (S - S2) / (sqrt((std(DataSlice) ** 2 + std(DataSlice2) ** 2) / (InvestmentHorizon)))
                        #if abs(T) > abs(TestThreshold):
                        #    num_signif_test += 1.0

                        # JKM test
                        P = pearson(DataSlice, DataSlice2)
                        if round(P,3) != 1.0:
                            # Necessary because otherwise, the fund is comparing itself to something exactly the same and SE = 0.
                            SE = sqrt((1.0 / InvestmentHorizon) * (2 - 2 * P + 0.5 * (S ** 2 + S2 ** 2 - 2 * S * S2 * (P ** 2))))
                            T = (S - S2) / SE

                            if SE == 0.0:
                                print([S, S2, 1.0 * InvestmentHorizon, P])
                                print(sqrt((1.0 / InvestmentHorizon) * (2 - 2 * P + 0.5 * (S ** 2 + S2 ** 2 - 2 * S * S2 * (P ** 2)))))
                                raise ValueError('Null SE for Sharpe test.')

                            if isnan(T) == True:
                                print(T)
                                print((S - S2))
                                print(SE)
                                print((1.0 / InvestmentHorizon))
                                print(P)
                                print((2 - 2 * P + 0.5 * (S ** 2 + S2 ** 2 - 2 * S * S2 * (P ** 2))))
                                print((1.0 / InvestmentHorizon) * (2 - 2 * P + 0.5 * (S ** 2 + S2 ** 2 - 2 * S * S2 * (P ** 2))))
                                raise ValueError('NAN T result')

                            ind.tvalue_cpr += T
                            number_deviations += abs(T)
                            num_test += 1.0
                            Sharpe_diff += abs(S - S2)

                            if T >= TestThreshold:
                                num_signif_test += 1.0
                            
                            

    for i, ind in enumerate(pop):
        if isnan(ind.tvalue_cpr) == False and isnan(ind.sharpe) == False:
            sum_tvalue_cpr_abs += abs(ind.tvalue_cpr)
            sum_exp_tval += exp(ind.tvalue_cpr * InvestmentIntensity)
            if isnan(sum_tvalue_cpr_abs) == True:
                raise ValueError('Nan sum tvalue copr abs')


            #if ind.tvalue_cpr > 0:
                # Apply the exponent Investment Intensity
            #    ind.tvalue_cpr = ind.tvalue_cpr ** InvestmentIntensity
            #    total_tvalue_cpr += ind.tvalue_cpr
            #if ind.tvalue_cpr < 0:
            #    # Apply the exponent Investment Intensity, keeping the negative sign of T value.
           #     total_tvalue_cpr_neg += ind.tvalue_cpr
            ##    ind.tvalue_cpr = - abs(abs(ind.tvalue_cpr) ** InvestmentIntensity)


    #if isnan(total_tvalue_cpr) == True:
    #    raise ValueError('Undefined total_tvalue_cpr')

    for i, ind in enumerate(pop):
        ind.investment_ratio = 0.0
        if isnan(ind.tvalue_cpr) == False and isnan(ind.sharpe) == False:
            ind.investment_ratio = (exp(ind.tvalue_cpr * InvestmentIntensity)) / sum_exp_tval
            #if ind.tvalue_cpr > 0:
            #    ind.investment_ratio = ind.tvalue_cpr / total_tvalue_cpr
            #if ind.tvalue_cpr < 0:
            #    ind.investment_ratio = - (abs(ind.tvalue_cpr / total_tvalue_cpr_neg))
            #    if ind.investment_ratio > 0:
            #        raise ValueError('Investment ratio positive despite negative T statistic value.')
            sum_inv_ratio += ind.investment_ratio 
    
    if sum_inv_ratio == 0.0:
        for ind in pop:
            ind.investment_ratio = 1.0 / len(pop)
            sum_inv_ratio += ind.investment_ratio 

        # print([round(ind.sharpe,2), round(ind.investment_ratio,2), round(ind.tvalue_cpr,2), round(total_tvalue_cpr,2)])

    #if round(sum_inv_ratio,3) < -1.0 or round(sum_inv_ratio,3) > 1.0:
    if round(sum_inv_ratio, 2) != 1.0:
        print(sum_inv_ratio)
        for ind in pop:
            print([ind.sharpe, ind.tvalue_cpr, ind.investment_ratio])
        #raise ValueError('Sum of investment ratios is outside bounds [-1,1].')
        ''' for minor problems we can multiply it all by 1/sum or something to normalise?'''
        raise ValueError('Sum of investment ratios is not 1.0')

    return pop, (sum_tvalue_cpr_abs / num_test), (100 * num_signif_test / num_test), number_deviations / num_test, Sharpe_diff / num_test

cdef DistributionInvestment(list pop, double InvestmentSupply):
    cdef cythonized.Individual ind 

    for ind in pop:
        amount = ind.investment_ratio * InvestmentSupply
        ind.investor_flow = amount
        ind.cash += amount
    return pop


def InvestmentProcedure(pop, generation, returns_tracker, InvestmentHorizon, InvestmentSupply, TestThreshold, InvestmentIntensity):
    if InvestmentHorizon > 0 and generation > Barr + InvestmentHorizon + ShieldInvestment and InvestmentHorizon != 1:
        pop, AvgValSignif, PerSignif, NumDev, SharpeDiff = Investment(returns_tracker, generation, InvestmentHorizon, pop, InvestmentSupply, TestThreshold, InvestmentIntensity)
    else:
        AvgValSignif, PerSignif, NumDev, SharpeDiff = 0, 0, 0, 0
    return pop, AvgValSignif, PerSignif, NumDev, SharpeDiff



cdef Investment(double[:, :] returns_tracker, int generation, int InvestmentHorizon, list pop, double InvestmentSupply, double TestThreshold, double InvestmentIntensity):
    cdef cythonized.Individual ind
    cdef double[:, :] ReturnData
    cdef int i = 0

    ReturnData = returns_tracker[generation-InvestmentHorizon:generation,:]
    # Control data size.
    if len(ReturnData) != InvestmentHorizon:
        print(len(ReturnData))
        print(len(InvestmentHorizon))
        raise ValueError('Length of Returndata did not match Investmtent Horizon.')

    for i, ind in enumerate(pop):
        ''' Compute the Sharpe ratio of the fund '''
        DataSlice = ReturnData[:,i]
        ind = compute_sharpe(ind, DataSlice)
        
    pop, AvgVal, PerSignif, NumDev, SharpeDiff = compare_sharpe(pop, ReturnData, InvestmentHorizon, TestThreshold, InvestmentIntensity)

    pop = DistributionInvestment(pop, InvestmentSupply)

    return pop, AvgVal, PerSignif, NumDev, SharpeDiff


def KellyInvestment(pop, InvestmentSupply, InvestmentIntensity, generation, InvestmentHorizon, returns_tracker, TestThreshold):
    if generation > InvestmentHorizon and InvestmentHorizon > 0:
        pop = ApplyKellyInvestment(pop, InvestmentSupply, InvestmentIntensity, generation, InvestmentHorizon)
    pop, AvgValSignif, PerSignif, NumDev = MeasureSignificance(returns_tracker, generation, InvestmentHorizon, pop, TestThreshold)
    return pop, AvgValSignif, PerSignif, NumDev


cdef ApplyKellyInvestment(list pop, double InvestmentSupply, double InvestmentIntensity, double generation, double InvestmentHorizon):

    # TODO implemenent effect of InvestmnetHorizon?
    # For Kelly investment, it just smoothes down the probabilities applied. Should not change drastically the results.

    cdef double total_wealth = 0.0
    cdef double sum_ir = 0.0
    cdef double amount = 0.0

    for ind in pop:
        if isnan(ind.wealth) == False:
            total_wealth += (ind.wealth ** InvestmentIntensity)
    
    if total_wealth != 0.0:
        for ind in pop:
            ind.investment_ratio = (ind.wealth ** InvestmentIntensity) / total_wealth
            sum_ir += ind.investment_ratio
            amount = ind.investment_ratio * InvestmentSupply
            ind.investor_flow = amount
            ind.cash += amount
    if round(sum_ir, 3) != 1:
        print(sum_ir)
        for ind in pop:
            print(ind.investment_ratio)
        raise ValueError('Sum of investment ratios is not one.')

    return pop


cdef MeasureSignificance(double[:,:] returns_tracker, int generation, int InvestmentHorizon, list pop, double TestThreshold):
    
    # Define results variables
    cdef int num_test = 0
    cdef int num_signif_test = 0
    cdef double number_deviations = 0.0
    cdef double sum_tvalue_cpr_abs = 0.0
    cdef cythonized.Individual ind
    cdef cythonized.Individual ind2
    cdef double T
    cdef double P 
    cdef double S 
    cdef double S2
    cdef double SE
    cdef int i = 0
    cdef double[:,:] ReturnData
    cdef list bounds
    cdef double NumDev = 0.0
    cdef double AvgValSignif = 0.0
    cdef double PerSignif = 0.0

    ReturnData = returns_tracker[generation-InvestmentHorizon:generation,:]

    # Compute sharpe ratios
    for i, ind in enumerate(pop):
        DataSlice = ReturnData[:,i]
        ind = compute_sharpe(ind, DataSlice)

    # Compare sharpe ratios
    for i, ind in enumerate(pop):
        if isnan(ind.sharpe) == False:
            ind.tvalue_cpr = 0.0
            DataSlice = ReturnData[:,i]
            S = ind.sharpe

            for j, ind2 in enumerate(pop):
                if j != i and isnan(ind2.sharpe) == False:
                    DataSlice2 = ReturnData[:,j]
                    S2 = ind2.sharpe
                    if isnan(S2) == False:
                        P = pearson(DataSlice, DataSlice2)
                        if P != 1.0:
                            SE = np.sqrt((1.0 / InvestmentHorizon) * (2 - 2 * P + 0.5 * (S ** 2 + S2 ** 2 - 2 * S * S2 * (P ** 2))))
                            T = (S - S2) / SE

                            if SE == 0.0:
                                print([S, S2, 1.0 * InvestmentHorizon, P])
                                print(np.sqrt((1.0 / InvestmentHorizon) * (2 - 2 * P + 0.5 * (S ** 2 + S2 ** 2 - 2 * S * S2 * (P ** 2)))))
                                raise ValueError('Null SE for Sharpe test.')

                            ind.tvalue_cpr += T
                            num_test += 1
                            bounds = [(S - S2) - TestThreshold * SE, (S - S2) + TestThreshold * SE]

                            if T > 0:
                                if bounds[0] > 0:
                                    num_signif_test += 1
                                    number_deviations += (bounds[0] / SE)
                            if T < 0:
                                if bounds[1] < 0:
                                    num_signif_test += 1
                                    number_deviations += abs(bounds[1] / SE)

    # Record some results
    for ind in pop:
        sum_tvalue_cpr_abs += abs(ind.tvalue_cpr)

    if num_test != 0:
        AvgValSignif = sum_tvalue_cpr_abs / num_test
        PerSignif = 100 * num_signif_test / num_test
    else:
        AvgValSignif = 0.0
        PerSignif = 0.0
    NumDev = number_deviations / len(pop)


    return pop, AvgValSignif, PerSignif, NumDev


def Profit_Investment(pop, ReinvestmentRate, returns_tracker, InvestmentHorizon, TestThreshold, generation):
    pop = Returns_Investment(pop, ReinvestmentRate)
    pop, AvgT, PropSignif, HighestT, AvgAbsT = ProfitSignificance(returns_tracker, generation, InvestmentHorizon, pop, TestThreshold)
    return pop, AvgT, PropSignif, HighestT, AvgAbsT


cdef ProfitSignificance(double[:,:] returns_tracker, int generation, int InvestmentHorizon, list pop, double TestThreshold):
    # print('Counting')
    # Define results variables
    cdef cythonized.Individual ind
    cdef cythonized.Individual ind2
    cdef double[:,:] ReturnData
    cdef list T_values = [0] * len(pop)
    cdef list MeanReturns = [0] * len(pop)
    cdef list StdReturns = [0] * len(pop)
    cdef int H = InvestmentHorizon
    cdef int i = 0
    cdef int j = 0
    cdef int NumSignif = 0
    cdef double PropSignif 
    cdef int CountTest = 0
    cdef double T
    cdef double fit
    cdef double SumT = 0.0

    #startTime = time.time()
    ReturnData = returns_tracker[generation-InvestmentHorizon:generation,:]

    # Compute mean and std of returns 
    for i, ind in enumerate(pop):
        DataSlice = ReturnData[:,i]
        #ind = compute_sharpe(ind, DataSlice)
        MeanReturns[i] = mean(DataSlice)
        StdReturns[i] = std(DataSlice)
    #print(time.time() - startTime)

    # Compute and record T statistic values
    #startTime = time.time()
    for i, ind in enumerate(pop):
        DataSlice = ReturnData[:,i]
        for j, ind2 in enumerate(pop):
            if j != i:
                DataSlice2 = ReturnData[:,j]
                T = (mean(DataSlice) - mean(DataSlice2)) / (std(DataSlice) + std(DataSlice2) / sqrt(H))
                T_values[i] += T
                CountTest += 1
                SumT += abs(T)
                if abs(T) >= TestThreshold:
                    NumSignif += 1
        ind.tvalue = T_values[i]
    #    # TODO: is there an issue with replacements and nan?
    #print(time.time() - startTime)
    
    # Record key results 
    #startTime = time.time()
    HighestT = max(T_values)
    AvgT = sum(T_values) / len(pop)
    PropSignif = NumSignif / CountTest
    AvgAbsT = SumT / len(pop)
    #print(time.time() - startTime)
    # Absolute sum of T?

    return pop, AvgT, PropSignif, HighestT, AvgAbsT

cdef Returns_Investment(list pop, double ReinvestmentRate):
    # apply investment
    for ind in pop:
        ind.investor_flow = 0.0
        fit = float('.'.join(str(ele) for ele in ind.fitness.values))
        # fitness depends on profits, and profits are W(t)-W(t-1). We might have a steanrioll issue.
        if isnan(fit) == False:
            ind.investor_flow = fit * (ReinvestmentRate - 1)
            ind.cash += ind.investor_flow
        #if isnan(fit) == True:
        #    print(fit)
        #    raise ValueError('NAN investor flow.') 
    return pop

