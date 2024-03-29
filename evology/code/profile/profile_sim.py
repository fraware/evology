import sys

sys.path.append("./evology/code/")
sys.path.append("/Users/aymericvie/Documents/GitHub/evology/evology/code")
sys.path.append("D:\\OneDrive\\Research\\2021_Market_Ecology\\evology\\evology\\code")

import cython
from tqdm import tqdm
from population import Population
from asset import Asset
import results
from investor import Investor
import sys


class Simulation:
    def __init__(
        self,
        max_generations,
        population_size,
        wealth_coords,
        interest_rate,
        investment_bool,
        seed,
        reset,
    ):
        self.max_generations = max_generations
        self.population_size = population_size
        self.interest_rate = interest_rate
        self.interest_rate_daily = ((1.0 + self.interest_rate) ** (1.0 / 252.0)) - 1.0
        self.seed = seed
        self.generation = 0
        self.data = None
        self.disable = Simulation.set_display(self)
        self.investment_bool = investment_bool
        self.wealth_coords = wealth_coords
        self.reset = reset
        self.noise_process = 0.0

    def set_display(self):
        """Controls whether we hide the TQDM progress bar during a run. Yes for linux because linux is for experiments"""
        if sys.platform == "darwin":
            return False
        elif sys.platform == "linux":
            return True

    @profile
    def simulate(self):
        """Contains all initialisation, simulations steps and results recording"""

        # Initialise results, assets, fund population, investor
        result = results.Result(self.max_generations)
        asset = Asset(self.max_generations, self.seed)
        pop = Population(
            self.population_size,
            self.max_generations,
            self.wealth_coords,
            self.interest_rate,
            asset.dividend_growth_rate_yearly,
            self.seed,
        )
        # NoiseTrader.process_series = NoiseTrader.compute_noise_process(
        #     self.max_generations, self.seed
        # )
        investor = Investor(self.investment_bool)
        pop.pop_init(asset.price)

        for self.generation in tqdm(range(self.max_generations), disable=self.disable):

            pop.replace_insolvent()
            if pop.shutdown == True:
                result.data = result.data[0 : self.generation]
                break
            if self.reset == True:
                pop.pop_init(asset.price)
            asset.get_dividend(self.generation)
            asset.compute_price_emas()
            pop.update_trading_signal(
                asset.dividend,
                self.interest_rate_daily,
                self.generation,
                asset.price,
                asset.price_emas,
            )
            pop.get_excess_demand_functions()
            pop.get_excess_aggregate_demand()
            pop.compute_liquidation(asset.volume)
            asset.market_clearing(pop)
            asset.mismatch = pop.compute_excess_demand_values(asset.price)
            asset.volume = pop.execute_excess_demand(asset.price)
            pop.cash_gains(asset.dividend, self.interest_rate_daily)
            pop.update_margin(asset.price)
            pop.clear_debt()
            pop.count_wealth(asset.price)
            pop.update_wealth_history(self.generation)
            pop.compute_average_return()
            pop.compute_profit()
            investor.investment_flows(pop)

            pop.count_wealth(asset.price)
            pop.get_returns_statistics()
            pop.get_wealth_statistics()
            pop.get_activity_statistics()
            pop.get_positions()
            pop.get_investment_flows()
            result.update_results(
                self.generation,
                asset.price,
                asset.dividend,
                asset.volume,
                self.noise_process,
                pop.VI_val,
                pop.wshareNT,
                pop.wshareVI,
                pop.wshareTF,
                pop.NT_flows,
                pop.VI_flows,
                pop.TF_flows,
                pop.NT_asset,
                pop.VI_asset,
                pop.TF_asset,
                pop.NT_cash,
                pop.VI_cash,
                pop.TF_cash,
                pop.NT_returns,
                pop.VI_returns,
                pop.TF_returns,
                pop.replacements,
            )

        self.data = result.convert_df()


if __name__ == "__main__":
    s = Simulation(
        max_generations=20000,
        population_size=10,
        wealth_coords=[1 / 4, 1 / 2, 1 / 4],
        interest_rate=0.01,
        investment_bool=False,
        seed=56615,
        reset=False,
    )
    s.simulate()
    df = s.data
