import numpy as np
from parameters import *
from market import *
import inspect
import math
np.seterr(divide = 'ignore') 

def clear_debt(pop, price):
    for ind in pop:
        # Attempt to clear debt
        if ind.loan > 0: # If the agent has outstanding debt:
            if ind.cash >= ind.loan + 100 * price: # If the agent has enough cash:
                ind.loan = 0
                ind.cash -= ind.loan
                print("Debt clear succesful for " + str(ind.type))
            if ind.cash < ind.loan + 100 * price : # If the agent does not have enough cash:
                ind.loan -= ind.cash - 100 * price
                ind.cash = 100 * price
                print("Debt clear unsuccesful for " + str(ind.type))
    return ind

def update_margin(pop, price):
    for ind in pop:
        # Update margins
        margin_objective = ind.asset_short * price # Margin amount to cover short position at current price.
        if margin_objective > ind.margin: # If our current margin is not enough:
            if ind.cash >= margin_objective - ind.margin: # If we have the cash to adjust:
                # We spend cash to refuel the margin.
                ind.margin += margin_objective - ind.margin
                ind.cash -= margin_objective - ind.margin
            if ind.cash < margin_objective - ind.margin: # If we don't have enough cash to adjust:
                # All available cash goes to the margin, and we have some loan.
                # Loan is a penalty on wealth notably for evaluating solvency.
                ind.margin += ind.cash
                ind.cash = 0
                ind.loan += margin_objective - ind.margin - ind.cash
                print("Margin update unsuccesful for " + str(ind.type))
        if margin_objective < ind.margin: # If our current margin is too high:
            # We get some of the margin back in the form of cash.
            ind.cash += ind.margin - margin_objective
            ind.margin -= ind.margin - margin_objective
    return ind

def calculate_wealth(pop, current_price):
    for ind in pop:


        # Update wealth
        ind.wealth = ind.cash + ind.asset_long * current_price - ind.loan
        # The amount due by short selling is equally captured by the margin, hence does not appear here.
    return ind

def calculate_ts(pop, extended_price_history):
    for ind in pop:

        if ind.type == "tf":
            if len(extended_price_history) >= max(1, ind[0]):
                ind.tsv = (np.log2(extended_price_history[-1]) - np.log2(extended_price_history[-ind[0]])) 
            elif len(extended_price_history) < max(1, ind[0]):
                ind.tsv = 0

        # elif ind.type == "vi":
            # ind.tsv = (np.log2(ind[0]) - np.log2(extended_price_history[-1]))

        elif ind.type == "nt":
            ind.process = ind.process + RHO_NT * (MU_NT - ind.process) + GAMMA_NT * random.normalvariate(0,1)
            # ind.tsv = np.log2(ind[0] * ind.process) -  np.log2(extended_price_history[-1])   
    return ind

# def calculate_edf(pop):
#     for ind in pop:
#         def func(x):
#             return (ind.wealth * LAMBDA_TF / x) * (np.tanh(SCALE_TF * ind.tsv) + 0.5) - ind.asset
#         ind.edf = func
#     return ind

def calculate_edv(pop, price, extended_price_history):
    for ind in pop:
        if ind.type == "tf":
            if len(extended_price_history) > max(1, ind[0]):
                def func_tf(p):
                    return (ind.wealth * LAMBDA_TF / p) * (np.tanh(SCALE_TF * ind.tsv) + 0.5) - (ind.asset_long - ind.asset_short) 
                ind.edf = func_tf
                ind.edv = ind.edf(price)
            else:
                ind.edf = 0
                ind.edv = 0
        
        if ind.type == "vi":
            ind.tsv = np.log2(ind[0]) - np.log2(price)
            def func_vi(p):
                return (ind.wealth * LAMBDA_VI / p) * (np.tanh(SCALE_VI * ind.tsv) + 0.5) - (ind.asset_long - ind.asset_short)  
            ind.edf = func_vi
            del func_vi
            ind.edv = ind.edf(price)

        if ind.type == "nt":
            ind.tsv = np.log2(ind[0] * ind.process) -  np.log2(price)  
            def func_nt(p):
                return (ind.wealth * LAMBDA_NT / p) * (np.tanh(SCALE_NT * ind.tsv) + 0.5) - (ind.asset_long - ind.asset_short)  
            ind.edf = func_nt 
            ind.edv = ind.edf(price)

            # ind.tsv = np.log2(ind[0] * ind.process) -  np.log2(price)
    return ind

def calculate_total_edv(pop):
    total = 0
    for ind in pop:
        total += ind.edv
    return total

def count_long_assets(pop):
    count = 0
    for ind in pop:
        if ind.asset_long > 0:
            count += ind.asset_long
    return count

def count_short_assets(pop):
    count = 0
    for ind in pop:
        if ind.asset_short > 0:
            count += ind.asset_short
    return count

def apply_edv(pop, asset_supply, price):
    num_sell, num_buy = 0, 0
    num_sell_tf, num_sell_vi, num_sell_nt = 0, 0, 0
    num_buy_tf, num_buy_vi, num_buy_nt = 0, 0, 0

    # Initialise variable edv
    for ind in pop:
        ind.edv_var = ind.edv



    # STEP 1 
    # BUY / SELL long positions (constrained by cash and selling volume)
    # We are constrained by cash, and availability of shares (= some agents selling)
    # However, selling is only constrained to buying. 
    # Thus, we constrained-buy now and sell accordingly later, by saving how much was actually bought.
    # We will then sell the same number of assets that were bought.

    # A - Know how much long positions agents want to buy
    total_buy = 0
    for ind in pop:
        if ind.edv_var > 0: # If we have assets to buy
            buy = min(ind.edv_var, ind.cash / price) # define how much we can buy
            if buy > 0 and buy < 1: # security to avoid negative infinitesimal orders
                buy = 0
            if buy < 0 and buy > -1:
                buy = 0
            total_buy += buy # Add to the total of buy-long orders

    # B - Know how much long positions agents want to sell
    total_sell = 0
    for ind in pop:
        if ind.edv_var < 0: # If we want to sell assets
            sell = min(abs(ind.edv_var), ind.asset_long) 
            if sell > 0 and sell < 1:  # security to avoid negative infinitesimal orders
                sell = 0
            if sell < 0 and sell > -1:
                sell = 0
            total_sell += sell

    # C - We have net buy and sell orders. Compute the ratio.
    if total_sell != 0:
        order_ratio = total_buy / total_sell 
    elif total_sell == 0:
        order_ratio = 0
        print("No exchange today (everyone selling or everyone buying)")

    if order_ratio < 0:
        for ind in pop:
            print("--- total buy, total sell, ind type, edv, edv_var, and feasible buy.sell order")
            print(total_buy)
            print(total_sell)
            print(ind.type)
            print(ind.edv)
            print(ind.edv_var)
            if ind.edv_var > 0:
                print(min(ind.edv_var, ind.cash / price))
            if ind.edv_var < 0:
                print(min(abs(ind.edv_var), ind.asset_long))
        raise ValueError('Negative order ratio (total sell/buy): ' + str(total_sell) + str(total_buy))

    
    # D - The order ratio determines how orders are impacted.
    # Each agent can execute the same fraction of orders, to not penalise agents with large orders.
    # We implement one single asset allocation proecedure with multipliers adjusted wrt the order ratio.
    
    if order_ratio == 0: #either noone buys, or no one sells
        multiplier_buy = 0
        multiplier_sell = 0
        # No orders will be executed (no supply or no demand)
    elif order_ratio < 1:
        multiplier_buy = 1
        multiplier_sell = order_ratio
        # Selling will be restricted according to demand
    elif order_ratio == 1 :
        multiplier_buy = 1
        multiplier_sell = 1
        # All orders will be executed (supply =  demand)
    elif order_ratio > 1:
        multiplier_buy = 1 / order_ratio
        multiplier_sell = 1
        # Buying will be restricted according to supply

    if multiplier_buy == None:
        raise ValueError('Multiplier Buy is not defined')
    if multiplier_buy < 0:
        raise ValueError('Multiplier Buy is negative')
    if multiplier_sell == None:
        raise ValueError('Multiplier Sell is not defined')
    if multiplier_sell < 0:
        raise ValueError('Multiplier Sell is negative')

    # E - Implement asset allocation under multipliers

    # # First verify that quantities will match after using math.floor
    # quantities_bought = 0
    # quantities_sold = 0
    # for ind in pop:
    #     if ind.edv_var > 0:
    #         quantities_bought += math.floor(min(ind.edv_var, ind.cash / price) * multiplier_buy)
    #     if ind.edv_var < 0:
    #         quantities_sold += math.floor(abs(ind.edv_var) * multiplier_sell)
    # if quantities_bought != quantities_sold:

    for ind in pop:
        # Exclude infinitesimal orders
        if ind.edv_var > 0 and ind.edv_var < 1:
            ind.edv_var = 0
        if ind.edv_var < 0 and ind.edv_var > -1:
            ind.edv_var = 0

    for ind in pop:
        # i) Buying orders
        if ind.edv_var > 0:
            # We determine effective bought amount, lose cash, gain shares, adjust demand
            quantity_bought = min(ind.edv_var, ind.cash / price) * multiplier_buy
            # print(ind.edv)
            # print(multiplier_buy)
            # print(quantity_bought)
            # print(ind.cash)
            ind.cash -= quantity_bought * price
            # print(ind.cash)

            if ind.cash < 0 and ind.cash > -0.01:
                ind.cash = 0
            if ind.cash > 0 and ind.cash < 0.01:
                ind.cash = 0

            if ind.cash < 0:
                print("ind type, cash, multiplier buy, qtty bought, value bought")
                print(ind.type)
                print(ind.cash)
                print(multiplier_buy)
                print(quantity_bought)
                print(quantity_bought * price - ind.cash)
                raise ValueError(str(ind.type) + ' Cash became negative at asset allocations under multiplier for agent with edv/edv_var/miltip ' + str(ind.edv) + " " + str(ind.edv_var) + " " + str(multiplier_buy))
            ind.asset_long += quantity_bought
            if quantity_bought != 0:
                print(str(ind.type) + " bought " + str(round(quantity_bought,2)))
            ind.edv_var -= quantity_bought
        
        # ii) Sell orders
        if ind.edv_var < 0:
            # We determine the effective sell amount, gain cash, lose shares, adjust our rolling demand
            quantity_sold = min(abs(ind.edv_var) * multiplier_sell, ind.asset_long)
            if quantity_sold < 0:
                raise ValueError('Negative quantity sold')
            ind.cash += quantity_sold * price
            ind.asset_long -= quantity_sold
            if quantity_sold != 0 :
                print(str(ind.type) + " sold " + str(round(quantity_sold, 2)))
            if ind.asset_long < 0:
                print(ind.asset_long)
                print(ind.edv)
                print(ind.edv_var)
                print(quantity_sold)
                print(multiplier_sell)
                raise ValueError('Agent long position became negative at asset allocations under multiplier')
            ind.edv_var += quantity_sold

    # STEP 2 
    # BUY / Close short positions (unconstrained)
    # Closing first makes sense to allow possible short sellings later (limit of short position size)
    # Buying a long / closing a short is here equivalent. We close first to simply the balance_sheets and
    # emphasize long positions.

    for ind in pop:
        if ind.edv_var > 0: # If we want to buy:
            if ind.asset_short > 0: # if we have short positions to clear:
                # print(ind.asset_short)
                buy_back = min(min(ind.edv_var, ind.asset_short), (ind.cash + ind.margin) / price) # Decide how much
                # print(buy_back)
                ind.asset_short -= buy_back # Apply the closing of the short position
                print(str(ind.type) + " closed " + str(round(buy_back,2)) + " shorts")
                # print(ind.asset_short)
                ind.edv_var -= buy_back # Adjust our excess demand after closing short positions
                # Apply the cost of closing the position
                if buy_back * price <= ind.margin: # if we have enough in the margin
                    ind.margin -= buy_back * price
                elif buy_back * price > ind.margin: # if we don't have enough in the margin
                    ind.cash -= (buy_back * price - ind.margin)
                    ind.margin = 0
            if ind.asset_short == 0: # If we have no short positions, clear the margin back into cash
                ind.cash += ind.margin
                ind.margin = 0
            if ind.asset_short < 0:
                raise ValueError('Negative short position')

    # STEP 3
    # SELL / Execute short selling (capacity constrained)
    # For selling agents, after the exchanges of long positions, some may still want to sell
    # No more exchange of long positions is available now. So they will consider short selling.

    total_short = 0
    for ind in pop:
        if ind.edv_var < 0: # If the agents still want to sell
            # Let's first determine how much they want to sell, 
            # # and see if it does not exceed the limit on short positions size.
            # If it exceeds, we make sure that the same fraction of orders is executed for all agents.
           short = abs(ind.edv_var)
           total_short += short
           if total_short < 0:
               raise ValueError('Total short below 0')

    short_limit = asset_supply * LIMIT_SHORT_POS_SIZE

    if short_limit < count_short_assets(pop):
        raise ValueError('Short position size limit not respected')
    
    if total_short != 0:
        if count_short_assets(pop) >= short_limit:
            # We have no room for more short positions.
            multiplier_short = 0

        elif count_short_assets(pop) < short_limit:
            # We have some room for more short positions.
            max_short = min(short_limit - count_short_assets(pop), total_short)
            multiplier_short = max_short / total_short

    # if count_short_assets(pop) + total_short <= short_limit:
    #     # Then the orders are all feasible.
    #     multiplier_short = 1

    # if count_short_assets(pop) + total_short > short_limit and count_short_assets(pop) < short_limit:
    #     if count_short_assets(pop) > short_limit:
    #         raise ValueError('Count short assets is above short limit')
    #     # Then the orders exceed our capacity and we apply our multiplier.
    #     # multiplier_short = (asset_supply * LIMIT_SHORT_POS_SIZE - count_short_assets(pop) ) / total_short
    #     multiplier_short = min((short_limit - count_short_assets(pop) / total_short),1)


        if multiplier_short > 1:
            raise ValueError('Multiplier short is above 1')
        if multiplier_short < 0:
            print(short_limit)
            print(count_short_assets(pop))
            print(total_short)
            print(multiplier_short)
            raise ValueError('Multiplier short is negative')
    # if multiplier_short = None:
    #     raise ValueError('Multiplier short is not defined')

    # Now we execute the short selling orders 
    for ind in pop:
        if ind.edv_var < 0: # if they still want to sell
            if ind.loan <= 0: # if the agents are not in debt (considered as risky)
                quantity_short_sold = (multiplier_short * abs(ind.edv_var))
                ind.asset_short += quantity_short_sold
                ind.edv_var -= quantity_short_sold
                ind.margin += quantity_short_sold * price
                print(str(ind.type) + " short selled " + str(round(quantity_short_sold, 2)) + " shares")
            elif ind.loan > 0:
                print(str(ind.type) + " prevented from short selling because of loan")

    if count_long_assets(pop) > asset_supply + 1:
        raise ValueError('Asset supply exceeded with value ' + str(count_long_assets(pop)))

    # TBD

    # """ everything below this line is not meant to be in the final code"""

    # # determine the amount of effective exchanges. This is captured by the buy/sell _factors
    # if bank_plus > bank_minus: # We have more buy orders than sell orders
    #     # Priority 1: exchange long positions
    #     # We will exchange bank_minus shares: everyone who wants to sell can sell, not everyone who wants can buy
    #     buy_factor = bank_minus / bank_plus
    #     sell_factor = 1
    # if bank_plus == bank_minus: # We live in a wonderful world
    #     buy_factor = 1
    #     sell_factor = 1
    # if bank_plus < bank_minus: # We have more sell orders than buy orders.
    #     # Exchange bank_plus shares, everyone who wants so can buy, not everyone who wants to sell can sell
    #     buy_factor = 1
    #     sell_factor = bank_plus / bank_minus

    # # Execute buying as it is the most constrained (cash) activity
    # assets_bought = 0
    # while assets_bought < bank_plus * buy_factor: # While we have not executed all feasible buy orders:
    #     for ind in pop:
    #         if ind.edv > 1

    # print(str(assets_bought) + " shares bought today.")

    # for ind in pop:
    #     if ind.edv > 0:  # the agent wants to buy
    #         i = 0
    #         while i < ind.edv:
    #             if count_positive_assets(pop) < asset_supply: # there are assets to buy
    #                 if ind.cash >= price: # the agent can afford to buy
    #                     ind.asset += 1
    #                     num_buy += 1
    #                     if ind.type == "tf":
    #                         num_buy_tf += 1
    #                     if ind.type == "vi":
    #                         num_buy_vi += 1
    #                     if ind.type == "nt":
    #                         num_buy_nt += 1
    #                     ind.cash -= price
    #             i += 1
    #     if ind.edv < 0:  # the agent wants to sell
    #         i = 0
    #         while i < abs(ind.edv):
    #             if ind.asset >= 1: # the agent can sell from inventory
    #                 ind.asset -= 1
    #                 num_sell += 1
    #                 if ind.type == "tf":
    #                     num_sell_tf += 1
    #                 if ind.type == "vi":
    #                     num_sell_vi += 1
    #                 if ind.type == "nt":
    #                     num_sell_nt += 1
    #                 ind.cash += price
    #             else: # the agent wants to short sell instead
    #                 if count_positive_assets(pop) > 0: # there are assets to borrow
    #                     if count_negative_assets(pop) < 10 * asset_supply: # we don't reach the cap on short position size
    #                         ind.asset -= 1
    #                         num_sell += 1
    #                         if ind.type == "tf":
    #                             num_sell_tf += 1
    #                         if ind.type == "vi":
    #                             num_sell_vi += 1
    #                         if ind.type == "nt":
    #                             num_sell_nt += 1
    #                         ind.margin += price
    #             i += 1

    #     # Clear margin if out of short position
    #     if ind.asset > 0:
    #         ind.cash += ind.margin
    #         ind.margin = 0
    return pop, num_buy, num_sell, num_buy_tf, num_buy_vi, num_buy_nt, num_sell_tf, num_sell_vi, num_sell_nt

# def update_margin(pop, price):
#     for ind in pop:
#         if ind.asset < 0:
#             ind.cash += ind.margin
#             ind.margin = abs(ind.asset) * price
#             ind.cash -= ind.margin
#             if ind.cash < 0:
#                 # The agent is insolvent and will try to buy back as much as possible
#                 # ind.edv = abs(ind.asset)
#                 ind.cash += ind.margin
#                 ind.margin = 0
#                 ind.loan += float('inf')
#     return ind

def wealth_earnings(pop, dividend, price):
    dividend, random_dividend = draw_dividend(dividend)
    for ind in pop:
        former_wealth = ind.wealth
        div_asset = ind.asset_long * dividend # Determine gain from dividends
        interest_cash = ind.cash * INTEREST_RATE # Determine gain from interest
        ind.cash += REINVESTMENT_RATE * (div_asset + interest_cash) # Apply reinvestment
        ind.wealth = ind.cash + ind.asset_long * price - ind.loan # Compute new wealth
        ind.profit = ind.wealth - former_wealth  # Compute profit as difference of wealth
    return pop, dividend, random_dividend

def pop_report(pop):
    for ind in pop:
        agent_report (ind)

def agent_report(ind):
    if ind.type == "tf":
        print("TF agent - Cash " + str(int(ind.cash)) + ", Asset_Long " + str(int(ind.asset_long)) + ", Asset_Short " + str(int(ind.asset_short)) + ", Wealth " + str(int(ind.wealth)) + ", TS " + str(round(ind.tsv,2)) + ", EV " + str(int(ind.edv)) + ", Margin " + str(int(ind.margin)) + ", Loan " + str(int(ind.loan)) )# + ", Profit " + str(int(ind.profit)) + ", Fitness " + str(ind.fitness))
    if ind.type == "vi":
        print("VI agent - Cash " + str(int(ind.cash)) + ", Asset_Long " + str(int(ind.asset_long)) + ", Asset_Short " + str(int(ind.asset_short)) + ", Wealth " + str(int(ind.wealth)) + ", TS " + str(round(ind.tsv,2)) + ", EV " + str(int(ind.edv)) + ", Margin " + str(int(ind.margin)) + ", Loan " + str(int(ind.loan)) )# )#", Profit " + str(int(ind.profit)) + ", Fitness " + str(ind.fitness))
    if ind.type == "nt":
        print("NT agent - Cash " + str(int(ind.cash)) + ", Asset_Long " + str(int(ind.asset_long)) + ", Asset_Short " + str(int(ind.asset_short)) + ", Wealth " + str(int(ind.wealth)) + ", TS " + str(round(ind.tsv,2)) + ", EV " + str(int(ind.edv)) + ", Margin " + str(int(ind.margin)) + ", Loan " + str(int(ind.loan)) )# )#", Profit " + str(int(ind.profit)) + ", Fitness " + str(ind.fitness))
  
def nt_report(pop):
    fval = 0
    num = 0
    for ind in pop:
        if ind.type == "nt":
            fval += ind.process * ind[0]
            num += 1
    if num != 0:
        fval_round = fval/num
    if num == 0:
        fval_round = 0
    return fval_round