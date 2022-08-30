from types import FunctionType
from trend_follower import TrendFollower
from value_investor import ValueInvestor
from noise_trader import NoiseTrader
from fund import Fund
from math import isnan
import numpy as np
import warnings

class Population:
    """ This object contains Fund objects and execute functions on this group"""

    asset_supply = 0

    def __init__(
        self,
        population_size,
        max_generations,
        wealth_coords,
        interest_rate,
        dividend_growth_rate,
        seed,
    ):
        self.size = population_size
        self.max_generations = max_generations
        self.wealth_coords = wealth_coords
        self.agents = []
        self.interest_rate = interest_rate
        self.dividend_growth_rate = dividend_growth_rate
        self.seed = seed
        self.aggregate_demand = FunctionType
        self.spoils = 0
        self.shutdown = False

        # Create some population state variables to store as results
        self.wealthNT = 0.0
        self.wealthVI = 0.0
        self.wealthTF = 0.0
        self.wshareNT = 0.0
        self.wshareVI = 0.0
        self.wshareTF = 0.0
        self.VI_val = 0.0
        self.average_annual_return = 0.0
        self.NT_flows = 0.0
        self.VI_flows = 0.0
        self.TF_flows = 0.0
        self.NT_asset = 0.0
        self.VI_asset = 0.0
        self.TF_asset = 0.0
        self.NT_cash = 0.0
        self.VI_cash = 0.0
        self.TF_cash = 0.0
        self.NT_return = np.nan
        self.VI_return = np.nan
        self.TF_return = np.nan

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
                1)
        else:
            raise TypeError("Unrecognised requested type for create_fund.")
        return fund

    def create_pop(self):
        """ generates a population of funds basd on initial coordinates
        There is always at least one fund of each type. """

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
        total_cash = Fund.cash_nominal * self.size
        total_asset = Fund.asset_nominal * self.size
        # Initialise cash and assets wrt shares and numbers
        NT_cash, NT_asset = total_cash * shareNT / NumNT, total_asset * shareNT / NumNT
        VI_cash, VI_asset = total_cash * shareVI / NumVI, total_asset * shareVI / NumVI
        TF_cash, TF_asset = total_cash * shareTF / NumTF, total_asset * shareTF / NumTF

        for fund in self.agents:
            if isinstance(fund, NoiseTrader):
                fund.cash, fund.asset = NT_cash, NT_asset
            if isinstance(fund, ValueInvestor):
                fund.cash, fund.asset = VI_cash, VI_asset
            if isinstance(fund, TrendFollower):
                fund.cash, fund.asset = TF_cash, TF_asset

        Population.asset_supply = total_asset



    def count_wealth(self, price):
        """ Count wealth of funds in the population"""
        for ind in self.agents:
            ind.count_wealth(price)

    def update_trading_signal(
        self, dividend, interest_rate_daily, generation, price, price_ema
    ):
        """ Depending on fund types, compute their trading signals"""
        for ind in self.agents:
            ind.update_trading_signal(dividend, interest_rate_daily, generation, price, price_ema)

    def get_excess_demand_functions(self):
        for ind in self.agents:
            ind.excess_demand_function = ind.get_excess_demand_function()

    def get_excess_demand_functions(self):
        for ind in self.agents:
            ind.get_excess_demand_function()

    def get_excess_aggregate_demand(self):
        """ Creates the aggregate demand function from funds' individual demands"""
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

    def compute_excess_demand_values(self, price):
        """ Based on asset price, compute funds' excess demand values and mismatch"""
        mismatch = 0.0
        for ind in self.agents:
            if isinstance(ind, ValueInvestor):
                ind.compute_trading_signal(price)
            ind.compute_excess_demand(price)
            mismatch += ind.demand
        return mismatch

    def execute_excess_demand(self, price):
        """ Execute buy and sell orders of the funds, making sure they are balanced"""
        self.execute_balanced_orders()
        self.check_asset_supply()
        volume = self.volume_check(price)

        return volume

    def execute_balanced_orders(self):
        # Verify that excess demand orders balance out
        sum_demand = 0.0
        for ind in self.agents:
            sum_demand += ind.demand
        if abs(sum_demand) > 1:
            # We have an imbalance to solve.
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
                    ind.demand = ind.demand * multiplier_buy
                elif ind.demand < 0:
                    ind.demand = ind.demand * multiplier_sell


    def check_asset_supply(self):
        # Verify asset supply 
        total_assets = 0.0
        for ind in self.agents:
            total_assets += ind.asset

        if abs(total_assets - Population.asset_supply + self.spoils) >= 1:
            print("agent type, demand")
            for ind in self.agents:
                print(ind.type, ind.wealth, ind.asset, ind.demand)
            print('spoils', self.spoils)
            raise ValueError(
                "Asset supply violated", total_assets, Population.asset_supply
            )

    def volume_check(self, price):
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

    def cash_gains(self, dividend, interest_rate_daily):
        """ All funds receive their earnings"""
        for ind in self.agents:
            ind.cash_gains(dividend, interest_rate_daily)

    def count_assets(self):
        """ Count funds total assets"""
        total = 0.0
        for ind in self.agents:
            total += ind.get_assets()
        return total

    def update_margin(self, price):
        for ind in self.agents:
            ind.update_margin(price)

    def compute_profit(self):
        for ind in self.agents:
            ind.compute_profit()

    def update_wealth_history(self):
        for ind in self.agents:
            ind.update_wealth_history()

    def compute_average_return(self):
        """ Computes average fund performance in the population"""

        # Compute average annual return
        total_profit, count_funds = 0.0, 0
        for ind in self.agents:
            if isnan(ind.get_annual_return()) == False:
                total_profit += ind.get_annual_return()
                count_funds += 1
        if count_funds != 0:
            self.average_annual_return = total_profit / count_funds
        else:
            self.average_annual_return = np.nan

        # Compute average monthly return and excess annual return for funds
        total_profit, count_funds = 0.0, 0
        for ind in self.agents:
            # Measure excess annual return 
            ind.excess_annual_return = ind.annual_return - self.average_annual_return
            # Measure average monthly return
            if isnan(ind.get_monthly_return()) == False:
                total_profit += ind.get_monthly_return()
                count_funds += 1
        if count_funds != 0:
            self.average_monthly_return = total_profit / count_funds
        else:
            self.average_monthly_return = np.nan


    def get_returns_statistics(self):
        """ Measure returns by strategy type"""

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

        total_wealth = wealthNT + wealthVI + wealthTF

        self.wealthNT = wealthNT
        self.wealthVI = wealthVI
        self.wealthTF = wealthTF
        self.wshareNT = wealthNT / total_wealth
        self.wshareVI = wealthVI / total_wealth
        self.wshareTF = wealthTF / total_wealth

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
        """ Count short positions of funds"""
        total_short = 0
        for ind in self.agents:
            if ind.asset < 0:
                total_short += abs(ind.asset)
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


    def create_fractional_fund(self, index, divisions):
        """ Create fractional copies of a fund"""
        if isinstance(self.agents[index], NoiseTrader):
            new_half = self.create_fund("NT")
        elif isinstance(self.agents[index], ValueInvestor):
            new_half = self.create_fund("VI")
        elif isinstance(self.agents[index], TrendFollower):
            new_half = self.create_fund("TF")
        else:
            raise TypeError('Unrecognised agent type for create_fractional_fund')

        new_half.cash = self.agents[index].cash / divisions
        new_half.asset = self.agents[index].asset / divisions
        new_half.loan = self.agents[index].loan / divisions
        new_half.margin = self.agents[index].margin / divisions
        new_half.wealth = self.agents[index].wealth / divisions

        return new_half


    def replace_insolvent(self):
        """ Replace insolvent funds in the population by spliting the wealthiest fund"""

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
                for index in index_to_replace:
                    spoils += self.agents[index].asset
                    self.agents[index] = new_half_fund
                    
                    replacements += 1
                # FInally, add the last subdivision in place of the maximum fund.
                self.agents[MaxFund] = new_half_fund
                warnings.warn('Replacement done.')

                for ind in self.agents:
                    if ind.wealth < 0:
                        raise ValueError("Insolvent funds after hypermutation.")


            self.replacements = replacements # Count period replacements
            self.spoils += spoils # Add shares of the insolvent funds to the liquidation pool (spoils)
        return self.spoils, replacements

    def compute_liquidation(self, volume):
        """ Determine how many assets of insolvent funds are liquidated in the market today"""
        if self.spoils > 0:
            self.liquidation = - min(self.spoils, min(0.1 * volume, 10000))
        elif self.spoils == 0:
            self.liquidation = 0.
        elif self.spoils < 0:
            self.liquidation = min(abs(self.spoils), min(0.1 * volume, 10000))
