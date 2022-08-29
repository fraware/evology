from math import isnan


class Investor:
    def __init__(self, investment_bool):
        self.active = investment_bool

    def investment_flows(self, pop):
        # net capital flows based on Ka and Ho, 2019
        if self.active == True:
            for fund in pop.agents:
                if (
                    isnan(fund.excess_monthly_return) == False
                    and isnan(fund.monthly_return) == False
                ):
                    invested_amount = (
                        (-0.0012 + 0.1089 * fund.excess_monthly_return) / 21.0
                    ) * fund.wealth
                    fund.net_flow = invested_amount
                    fund.cash += fund.net_flow
