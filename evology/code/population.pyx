#cython: boundscheck=False, wraparound=False, initializedcheck=False

import cython
cdef float NAN = float("nan")
from trend_follower import TrendFollower
from value_investor import ValueInvestor
from noise_trader import NoiseTrader
from fund import Fund
from libc.math cimport isnan, fabs, fmax
import numpy as np
import warnings


cdef class Population:
    """ This object contains Fund objects and execute functions on this group"""

    def __init__(
        self,
        population_size,
        max_generations,
        wealth_coords,
        interest_rate,
        dividend_growth_rate,
        seed,
    ):
        self.cash_nominal = 50_000_000.
        self.asset_nominal = 500_000.
        self.size = population_size
        self.max_generations = max_generations
        self.wealth_coords = wealth_coords
        self.agents = []
        self.interest_rate = interest_rate
        self.dividend_growth_rate = dividend_growth_rate
        self.seed = seed
        # self.aggregate_demand = FunctionType
        self.spoils = 0.
        self.shutdown = False
        self.asset_supply = 0

        # Create some population state variables to store as results
        self.wealthNT = 0.0
        self.wealthVI = 0.0
        self.wealthTF = 0.0
        self.wshareNT = 0.0
        self.wshareVI = 0.0
        self.wshareTF = 0.0
        self.VI_val = 0.0
        self.average_10annual_return = 0.0
        self.NT_flows = 0.0
        self.VI_flows = 0.0
        self.TF_flows = 0.0
        self.NT_asset = 0.0
        self.VI_asset = 0.0
        self.TF_asset = 0.0
        self.NT_cash = 0.0
        self.VI_cash = 0.0
        self.TF_cash = 0.0
        self.NT_return = NAN
        self.VI_return = NAN
        self.TF_return = NAN

    def create_fund(self, type):
        """ A function taking a type as argument and returning a corresponding Fund"""
        if type == "NT":
            fund = NoiseTrader(
                0,
                0,
                0.01,
                self.interest_rate,
                self.dividend_growth_rate,
            )
        elif type == "VI":
            fund = ValueInvestor(
                0,
                0,
                0.01,
                self.interest_rate,
                self.dividend_growth_rate,
            )
        elif type == "TF":
            fund = TrendFollower(
                0, 
                0, 
                252)
        else:
            raise TypeError("Unrecognised requested type for create_fund.")
        return fund

    def create_pop(self):
        cdef int NumNT
        cdef int NumVI
        cdef int NumTF
        """ generates a population of funds basd on initial coordinates
        There is always at least one fund of each type. """
        self.agents = []

        # Check we can create a diverse population
        if self.size < 3:
            raise RuntimeError('Population size cannot be inferior to 3.')
        [shareNT, shareVI, shareTF] = self.wealth_coords
        if shareNT + shareVI + shareTF > 1.00001:
            raise RuntimeError("Wealth coordinates sum is higher than 1.")
        if shareNT + shareVI + shareTF < 0.99999:
            raise RuntimeError("Wealth coordinates sum is lower than 1.")
        if shareNT <= 0 or shareVI <= 0 or shareTF <= 0:
            raise RuntimeError('Strategy initial condition <= 0')

        if self.size > 3:
            warnings.warn("Pop size superior to 3, features may encounter issues. Please use the model with 3 agent and aggregate sizes, since there is no individual level heterogeneity.")

        # Start the population with three agents of each type.
        self.agents.append(self.create_fund("NT"))
        self.agents.append(self.create_fund("VI"))
        self.agents.append(self.create_fund("TF"))

        # Fill the rest of the population
        NumNT, NumVI, NumTF = 1, 1, 1
        rng = np.random.default_rng(seed=self.seed + 2)
        for _ in range(self.size - 3):
            rd = rng.random()
            if rd <= shareNT:
                self.agents.append(self.create_fund("NT"))
                NumNT += 1
            elif rd > shareNT and rd <= shareNT + shareVI:
                self.agents.append(self.create_fund("VI"))
                NumVI += 1
            elif rd > shareNT + shareVI:
                self.agents.append(self.create_fund("TF"))
                NumTF += 1

        # Amount of cash/asset to split within each subpopulation
        total_cash = self.cash_nominal * self.size
        total_asset = self.asset_nominal * self.size
        # Initialise cash and assets wrt shares and numbers
        NT_cash, NT_asset = total_cash * shareNT / NumNT, total_asset * shareNT / NumNT
        VI_cash, VI_asset = total_cash * shareVI / NumVI, total_asset * shareVI / NumVI
        TF_cash, TF_asset = total_cash * shareTF / NumTF, total_asset * shareTF / NumTF

        for fund in self.agents:
            if isinstance(fund, NoiseTrader):
                fund.cash, fund.asset = NT_cash, NT_asset
                fund.process_series = fund.compute_noise_process(self.max_generations, self.seed)
                self.noise_process = fund.process_series
            if isinstance(fund, ValueInvestor):
                fund.cash, fund.asset = VI_cash, VI_asset
            if isinstance(fund, TrendFollower):
                fund.cash, fund.asset = TF_cash, TF_asset

        self.asset_supply = total_asset



    def count_wealth(self, double price):
        """ Count wealth of funds in the population"""
        for ind in self.agents:
            ind.count_wealth(price)

    def update_trading_signal(
        self, double dividend, double interest_rate_daily, int generation, double price, double price_ema
    ):
        """ Depending on fund types, compute their trading signals"""
        for ind in self.agents:
            # print(ind, ind.type)
            ind.update_trading_signal(dividend, interest_rate_daily, generation, price, price_ema)
            # print("done")
                
    def get_excess_demand_functions(self):
        for ind in self.agents:
            ind.excess_demand_function = ind.get_excess_demand_function()

    def get_excess_demand_functions(self):
        for ind in self.agents:
            ind.get_excess_demand_function()

    def get_excess_aggregate_demand(self):
        """ Creates the aggregate demand function from funds' individual demands"""
        cdef double result 
        cdef object func
        
        def func(price):
            result = 0.0
            for ind in self.agents:
                try:
                    result += ind.excess_demand(price)
                except Exception as e:
                    print(e)
                    raise RuntimeError(
                        "Failed to get demand(price) from agent.", ind.type, price
                    )
            return result
        self.aggregate_demand = func

    def compute_excess_demand_values(self, double price):
        cdef double mismatch
        """ Based on asset price, compute funds' excess demand values and mismatch"""
        mismatch = 0.0
        for ind in self.agents:
            if isinstance(ind, ValueInvestor):
                ind.compute_trading_signal(price)
            ind.compute_excess_demand(price)
            mismatch += ind.demand
        return mismatch

    def execute_excess_demand(self, double price):
        """ Execute buy and sell orders of the funds, making sure they are balanced"""
        cdef double volume
        self.execute_balanced_orders()
        self.check_asset_supply()
        volume = self.volume_check(price)

        return volume

    def execute_balanced_orders(self):
        cdef double sum_demand
        cdef double order_ratio
        cdef double buy_orders
        cdef double sell_orders
        cdef double multiplier_buy
        cdef double multiplier_sell

        # Verify that excess demand orders balance out
        sum_demand, prev_dmd = 0.0, 0.0
        for ind in self.agents:
            sum_demand += ind.demand
            prev_dmd += ind.demand
        if sum_demand != 0:
            buy_orders = 0.
            sell_orders = 0.
            for ind in self.agents:
                if ind.demand > 0:
                    buy_orders += ind.demand
                elif ind.demand < 0:
                    sell_orders += abs(ind.demand)
            if sell_orders != 0:
                order_ratio = buy_orders / sell_orders
            else:
                order_ratio = 0

            multiplier_buy = 0.
            multiplier_sell = 0.
            if order_ratio == 0.:  # either noone buys, or no one sells
                warnings.warn("No orders will be executed (no supply or no demand)")
            elif order_ratio < 1.:
                multiplier_buy = 1.
                multiplier_sell = order_ratio
                # Selling will be restricted according to demand
            elif order_ratio == 1:
                multiplier_buy = 1.
                multiplier_sell = 1.
                # All orders will be executed (supply =  demand)
            elif order_ratio > 1:
                multiplier_buy = 1. / order_ratio
                multiplier_sell = 1.
                # Buying will be restricted according to supply
            else:
                raise ValueError("order_ratio has a strange value: " + str(order_ratio))

            for ind in self.agents:
                if ind.demand > 0:
                    dmd = ind.demand * multiplier_buy
                    ind.demand = dmd
                elif ind.demand < 0:
                    ind.demand = ind.demand * multiplier_sell

    def check_asset_supply(self):
        # Verify asset supply 
        cdef double total_asset
        total_assets = 0.0
        for ind in self.agents:
            total_assets += ind.asset

        if abs(total_assets - self.asset_supply + self.spoils) >= 1:
            print("agent type, demand")
            for ind in self.agents:
                print(ind.type, ind.wealth, ind.asset, ind.demand)
            print('spoils', self.spoils)

            sum_demand = 0.0
            for ind in self.agents:
                sum_demand += ind.demand
            print("sum demand", sum_demand)
            raise ValueError(
                "Asset supply violated", total_assets, self.asset_supply
            )

    def volume_check(self, double price):
        cdef double volume
        # Measure volume and check it is not 0 + implement orders
        volume = 0.0
        for ind in self.agents:
            volume += abs(ind.demand)  # abs: buy & sell don't cancel out
            ind.execute_excess_demand(price)
        if volume == 0:
            warnings.warn('Volume is 0. Shuting down...')
            self.shutdown = True
        return volume

    def clear_debt(self):
        """ All funds clear their debt"""
        for ind in self.agents:
            ind.clear_debt()

    def cash_gains(self, double dividend, double interest_rate_daily):
        """ All funds receive their earnings"""
        for ind in self.agents:
            ind.cash_gains(dividend, interest_rate_daily)

    def count_assets(self):
        """ Count funds total assets"""
        total = 0.0
        for ind in self.agents:
            total += ind.get_assets()
        return total

    def update_margin(self, double price):
        for ind in self.agents:
            ind.update_margin(price)

    def compute_profit(self):
        for ind in self.agents:
            ind.compute_profit()

    def update_wealth_history(self, double generation):
        for ind in self.agents:
            ind.update_wealth_history(generation)

    def compute_average_return(self):
        """ Computes average fund performance in the population"""

        cdef double total_profit
        cdef double count_funds

        # Compute average annual return
        total_profit, count_funds = 0.0, 0.0
        for ind in self.agents:
            if isnan(ind.get_annual_return()) == False:
                total_profit += ind.get_annual_return() * ind.wealth
                count_funds += ind.wealth
        if count_funds != 0:
            self.average_10annual_return = total_profit / count_funds
        else:
            self.average_10annual_return = NAN

        # Compute average monthly return and excess annual return for funds
        total_profit, count_funds = 0.0, 0.0
        for ind in self.agents:
            # Measure excess annual return 
            ind.excess_10y_return = ind.return_10y - self.average_10annual_return
            # Measure average monthly return
            if isnan(ind.get_monthly_return()) == False:
                total_profit += ind.get_monthly_return() * ind.wealth
                count_funds += ind.wealth
            
        if count_funds != 0:
            self.average_monthly_return = total_profit / count_funds
            for ind in self.agents:
                ind.excess_monthly_return = ind.monthly_return - self.average_monthly_return

        else:
            self.average_monthly_return = NAN



    def get_returns_statistics(self):
        """ Measure returns by strategy type"""

        cdef double returnNT
        cdef double returnVI
        cdef double returnTF
        cdef double countNT
        cdef double countVI
        cdef double countTF

        returnNT = 0.0
        returnVI = 0.0
        returnTF = 0.0
        countNT, countVI, countTF = 0, 0, 0

        for ind in self.agents:
            if isinstance(ind, NoiseTrader):
                returnNT += ind.daily_return
                countNT += 1
            elif isinstance(ind, ValueInvestor):
                returnVI += ind.daily_return
                countVI += 1
            elif isinstance(ind, TrendFollower):
                returnTF += ind.daily_return
                countTF += 1

        if countNT != 0:
            self.NT_returns = returnNT / countNT
        else:
            self.NT_returns = np.nan
        if countVI != 0:
            self.VI_returns = returnVI / countVI
        else:
            self.VI_returns = np.nan
        if countTF != 0:
            self.TF_returns = returnTF / countTF
        else:
            self.TF_returns = np.nan

    def get_wealth_statistics(self):
        """ Measure various metrics about funds wealth"""

        cdef double wealthNT
        cdef double wealthVI
        cdef double wealthTF
        cdef double total_wealth

        wealthNT = 0.0
        wealthVI = 0.0
        wealthTF = 0.0

        for ind in self.agents:
            if isinstance(ind, NoiseTrader):
                wealthNT += ind.wealth
            elif isinstance(ind, ValueInvestor):
                wealthVI += ind.wealth
            elif isinstance(ind, TrendFollower):
                wealthTF += ind.wealth

        total_wealth = fmax(0,wealthNT) + fmax(0,wealthVI) + fmax(0,wealthTF)

        self.wealthNT = wealthNT
        self.wealthVI = wealthVI
        self.wealthTF = wealthTF
        self.wshareNT = fmax(0,wealthNT / total_wealth)
        self.wshareVI = fmax(0,wealthVI / total_wealth)
        self.wshareTF = fmax(0,wealthTF / total_wealth)

        if self.wshareNT < 0.001 and  self.wshareVI < 0.001:
            warnings.warn('NT and VI are extinct. Shuting down...')
            self.shutdown = True
        if self.wshareNT < 0.001 and  self.wshareTF < 0.001:
            warnings.warn('NT and TF are extinct. Shuting down...')
            self.shutdown = True
        if self.wshareVI < 0.001 and  self.wshareTF < 0.001:
            warnings.warn('TF and VI are extinct. Shuting down...')
            self.shutdown = True

    def get_short_positions(self):
        cdef double total_short
        """ Count short positions of funds"""
        total_short = 0.
        for ind in self.agents:
            if ind.asset < 0:
                total_short += fabs(ind.asset)
        return total_short

    def get_activity_statistics(self):
        """ Measure various metrics about funds' trading activity"""
        VI_val, VI_count = 0, 0
        for ind in self.agents:
            if isinstance(ind, ValueInvestor):
                VI_val += ind.valuation * ind.wealth
                VI_count += ind.wealth
        if VI_count != 0:
            self.VI_val = VI_val / VI_count
        else:
            self.VI_val = np.nan

    def get_investment_flows(self):
        """ Measure investment flows per agent type"""

        cdef double NTflows
        cdef double VIflows
        cdef double TFflows
        NTflows, VIflows, TFflows = 0.0, 0.0, 0.0
        for ind in self.agents:
            if isinstance(ind, NoiseTrader):
                NTflows += ind.net_flow
            elif isinstance(ind, ValueInvestor):
                VIflows += ind.net_flow
            elif isinstance(ind, TrendFollower):
                TFflows += ind.net_flow

        total_flows = abs(NTflows) + abs(VIflows) + abs(TFflows)
        if total_flows != 0:
            self.NT_flows = NTflows / total_flows
            self.VI_flows = VIflows / total_flows
            self.TF_flows = TFflows / total_flows
        else:
            self.NT_flows, self.VI_flows, self.TF_flows = 0.0, 0.0, 0.0

    def get_positions(self):

        cdef double NT_asset
        cdef double VI_asset
        cdef double TF_asset
        cdef double NT_cash
        cdef double VI_cash
        cdef double TF_cash

        """ Measure positions of the funds"""
        NT_asset, VI_asset, TF_asset = 0.0, 0.0, 0.0
        NT_cash, VI_cash, TF_cash = 0.0, 0.0, 0.0

        for ind in self.agents:
            if isinstance(ind, NoiseTrader):
                NT_asset += ind.asset
                NT_cash += ind.cash
            elif isinstance(ind, ValueInvestor):
                VI_asset += ind.asset
                VI_cash += ind.cash
            elif isinstance(ind, TrendFollower):
                TF_asset += ind.asset
                TF_cash += ind.cash

        self.NT_asset = NT_asset
        self.VI_asset = VI_asset
        self.TF_asset = TF_asset
        self.NT_cash = NT_cash
        self.VI_cash = VI_cash
        self.TF_cash = TF_cash


    def create_fractional_fund(self, int index, int divisions):
        
        """ Create fractional copies of a fund"""
        if isinstance(self.agents[index], NoiseTrader):
            new_half = self.create_fund("NT")
            
        elif isinstance(self.agents[index], ValueInvestor):
            new_half = self.create_fund("VI")
        elif isinstance(self.agents[index], TrendFollower):
            new_half = self.create_fund("TF")
        else:
            raise TypeError('Unrecognised agent type for create_fractional_fund')

        new_half.cash = float(self.agents[index].cash / divisions)
        new_half.asset = float(self.agents[index].asset / divisions)
        new_half.loan = float(self.agents[index].loan / divisions)
        new_half.margin = float(self.agents[index].margin / divisions)
        new_half.wealth = float(self.agents[index].wealth / divisions)

        return new_half


    def replace_insolvent(self):
        """ Replace insolvent funds in the population by spliting the wealthiest fund"""

        cdef int replacements
        cdef list index_to_replace
        cdef list wealth_list
        cdef int NumberReplace
        cdef int MaxFund
        cdef double spoils
        cdef int NT
        cdef int VI
        cdef int TF

        index_to_replace = []
        wealth_list = []
        spoils = 0
        replacements = 0

        for i, fund in enumerate(self.agents):
            wealth_list.append(fund.wealth)
            if fund.wealth < 0:
                index_to_replace.append(i)

        MaxFund = wealth_list.index(max(wealth_list))
        if len(index_to_replace) == len(self.agents):
            for ind in self.agents:
                print(ind.type, ind.wealth, ind.asset)
            print(self.spoils)
            self.agents = []
            self.shutdown = True
            self.replacements = len(self.agents)
            warnings.warn("Evology wiped out during insolvency resolution.")

        else:
            MaxFund = wealth_list.index(max(wealth_list))
            NumberReplace = len(index_to_replace)

            if NumberReplace != 0:
                new_half_fund = self.create_fractional_fund(MaxFund, NumberReplace + 1)
                # If we have created a new NT, we need to give it a noise process list (identical to all NT)
                if isinstance(new_half_fund, NoiseTrader):
                    new_half_fund.process_series = self.noise_process

                for index in index_to_replace:
                    spoils += self.agents[index].asset
                    warnings.warn('Replacement done.')
                    print(self.agents[index].type, new_half_fund.type)
                    self.agents[index] = new_half_fund
                    
                    replacements += 1
                # FInally, add the last subdivision in place of the maximum fund.
                self.agents[MaxFund] = new_half_fund

                for ind in self.agents:
                    if ind.wealth < 0:
                        raise ValueError("Insolvent funds after hypermutation.")


            self.replacements = replacements # Count period replacements
            self.spoils += spoils # Add shares of the insolvent funds to the liquidation pool (spoils)

            # Verify that the replacement did not cause a type to go extinct
            NT, VI, TF = 0, 0, 0
            for ind in self.agents:
                if isinstance(ind, NoiseTrader):
                    NT += 1
                elif isinstance(ind, ValueInvestor):
                    VI += 1
                elif isinstance(ind, TrendFollower):
                    TF += 1
                else:
                    print(ind)
                    raise TypeError("Unrecognised type")
                if NT > 0 and VI > 0 and TF > 0:
                    break
            if NT == 0 or VI == 0 or TF == 0:
                warnings.warn("Replacement caused a type extinction. Shutting down..." )
                self.shutdown = True


    def compute_liquidation(self, double volume):
        """ Determine how many assets of insolvent funds are liquidated in the market today"""
        if self.spoils > 0:
            self.liquidation = - min(self.spoils, min(0.1 * volume, 10000))
        elif self.spoils == 0:
            self.liquidation = 0.
        elif self.spoils < 0:
            self.liquidation = min(abs(self.spoils), min(0.1 * volume, 10000))

    def update_previous_wealth(self):
        for fund in self.agents:
            fund.previous_wealth = fund.wealth

    def pop_init(self, double price):
        self.create_pop()
        self.count_wealth(price)
        self.update_previous_wealth()
