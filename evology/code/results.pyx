#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

import cython
import pandas as pd
import numpy as np
DTYPE=np.float64


cdef class Result:
    """ Stores simulation results in a large nparray, updated at each period"""

    def __init__(self, int max_generations):
        self.max_generations = max_generations
        self.variables = [
            "Generation",
            "Price",
            "Dividend",
            "Volume",
            "NT_process",
            "VI_val",
            "WShare_NT",
            "WShare_VI",
            "WShare_TF",
            "NT_flows",
            "VI_flows",
            "TF_flows",
            "NT_asset",
            "VI_asset",
            "TF_asset",
            "NT_cash",
            "VI_cash",
            "TF_cash",
            "NT_returns",
            "VI_returns",
            "TF_returns",
            "Replacements",
            "Price_ema"
            ]
        # self.data = np.zeros((self.max_generations, len(self.variables)), dtype=FTYPE)
        self.data = self.create_data(self.max_generations, len(self.variables))
    
    def create_data(self, int gen, int var):

        cdef Py_ssize_t x_max = gen
        cdef Py_ssize_t y_max = var
        result = np.zeros((x_max, y_max), dtype=DTYPE)
        # print(result)
        # result = np.zeros((gen, var), dtype=DTYPE)
        return result 

    def update_results(
        self,
        int generation,
        double price,
        double dividend,
        double volume,
        double NT_process,
        double VI_val,
        double wshareNT,
        double wshareVI,
        double wshareTF,
        double NTflows,
        double VIflows,
        double TFflows,
        double NT_asset,
        double VI_asset,
        double TF_asset,
        double NT_cash,
        double VI_cash,
        double TF_cash,
        double NT_returns,
        double VI_returns,
        double TF_returns,
        int replacements,
        double price_ema,
    ):
        cdef int i
        cdef list arr

        arr = [
            generation,
            price,
            dividend,
            volume,
            NT_process,
            VI_val,
            wshareNT,
            wshareVI,
            wshareTF,
            NTflows,
            VIflows,
            TFflows,
            NT_asset,
            VI_asset,
            TF_asset,
            NT_cash,
            VI_cash,
            TF_cash,
            NT_returns,
            VI_returns,
            TF_returns,
            replacements,
            price_ema
        ]
        # print(arr)
        # self.data[int(generation), :] = arr
        for i in range(len(arr)):
            self.data[generation, i] = arr[i]

    def convert_df(self):
        # print(self.data)
        df = pd.DataFrame(np.asarray(self.data), columns=self.variables)
        return df
