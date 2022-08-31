import cython
cimport numpy as np
import pandas as pd
import numpy as np
DTYPE = np.intc
DTYPE=np.float64

cdef list variables


cdef class Result:
    """ Stores simulation results in a large nparray, updated at each period"""

    def __init__(self, max_generations):
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
            ]
        # self.data = np.zeros((self.max_generations, len(self.variables)), dtype=FTYPE)
        self.data = self.create_data(self.max_generations, len(self.variables))
    
    def create_data(self, gen, var):

        cdef Py_ssize_t x_max = gen
        cdef Py_ssize_t y_max = var
        result = np.zeros((x_max, y_max), dtype=DTYPE)
        # print(result)
        # result = np.zeros((gen, var), dtype=DTYPE)
        return result 

    def update_results(
        self,
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
        replacements
    ):
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
            replacements
        ]
        # print(arr)
        # self.data[int(generation), :] = arr
        for i in range(len(arr)):
            self.data[generation, i] = arr[i]

    def convert_df(self):
        # print(self.data)
        df = pd.DataFrame(np.asarray(self.data), columns=self.variables)
        return df
