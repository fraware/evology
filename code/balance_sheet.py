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
                # print("Debt clear succesful for " + str(ind.type))
            if ind.cash < ind.loan + 100 * price : # If the agent does not have enough cash:
                ind.loan -= ind.cash - 100 * price
                ind.cash = 100 * price
                # print("Debt clear unsuccesful for " + str(ind.type))
    return ind

def update_margin(pop, current_price):
    for ind in pop:
        # Update margins
        margin_objective = ind.asset_short * current_price # Margin amount to cover short position at current price.
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
                # print("Margin update unsuccesful for " + str(ind.type))
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

def determine_edf(pop, price_history):
    for ind in pop:
        if ind.type == "tf":
            # If a TF, we can find the TSV and then compute the EDF.
            if len(price_history) >= ind[0]:
                ind.tsv = np.log2(price_history[-1]) - np.log2(price_history[-ind[0]])
            elif len(price_history) < ind[0]:
                ind.tsv = 0
            def func(p):
                return (LAMBDA_TF * ind.wealth / p) * (np.tanh(SCALE_TF * ind.tsv + 0.5)) - (ind.asset_long - ind.asset_short)
            ind.edf = func
        if ind.type == "vi":
            # Generate the EDF. TSV is a function of the price.
            def func(p):
                return (LAMBDA_VI * ind.wealth / p) * (np.tanh(np.log2(SCALE_VI * ind[0]) - np.log2(p) + 0.5)) - (ind.asset_long - ind.asset_short)
            ind.edf = func
        if ind.type == "nt":
            # Generate the process and the EDF. TSV is a function of the price.
            ind.process = ind.process + RHO_NT * (MU_NT - ind.process) + GAMMA_NT * random.normalvariate(0,1)
            def func(p):
                return (LAMBDA_NT * ind.wealth / p) * (np.tanh(np.log2(SCALE_NT * ind[0] * ind.process) - np.log2(p) + 0.5)) - (ind.asset_long - ind.asset_short)
            ind.edf = func
    return ind

def calculate_edv(pop, price):
    for ind in pop:
        ind.edv =  ind.edf(price)
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
        # print("No exchange today (everyone selling or everyone buying)")

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
            ind.cash -= quantity_bought * price

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
            # if quantity_bought != 0:
            #     print(str(ind.type) + " bought " + str(round(quantity_bought,2)))
            ind.edv_var -= quantity_bought
        
        # ii) Sell orders
        if ind.edv_var < 0:
            # We determine the effective sell amount, gain cash, lose shares, adjust our rolling demand
            quantity_sold = min(abs(ind.edv_var) * multiplier_sell, ind.asset_long)
            if quantity_sold < 0:
                raise ValueError('Negative quantity sold')
            ind.cash += quantity_sold * price
            ind.asset_long -= quantity_sold
            # if quantity_sold != 0 :
            #     print(str(ind.type) + " sold " + str(round(quantity_sold, 2)))
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
                buy_back = min(min(ind.edv_var, ind.asset_short), (ind.cash + ind.margin) / price) # Decide how much
                ind.asset_short -= buy_back # Apply the closing of the short position
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

        if multiplier_short > 1:
            raise ValueError('Multiplier short is above 1')
        if multiplier_short < 0:
            print(short_limit)
            print(count_short_assets(pop))
            print(total_short)
            print(multiplier_short)
            raise ValueError('Multiplier short is negative')

    # Now we execute the short selling orders 
    for ind in pop:
        if ind.edv_var < 0: # if they still want to sell
            if ind.loan <= 0: # if the agents are not in debt (considered as risky)
                quantity_short_sold = (multiplier_short * abs(ind.edv_var))
                ind.asset_short += quantity_short_sold
                ind.edv_var -= quantity_short_sold
                ind.margin += quantity_short_sold * price
            #     print(str(ind.type) + " short selled " + str(round(quantity_short_sold, 2)) + " shares")
            # elif ind.loan > 0:
            #     print(str(ind.type) + " prevented from short selling because of loan")

    if count_long_assets(pop) > asset_supply + 1:
        raise ValueError('Asset supply exceeded with value ' + str(count_long_assets(pop)))
        
    return pop, num_buy, num_sell, num_buy_tf, num_buy_vi, num_buy_nt, num_sell_tf, num_sell_vi, num_sell_nt

def wealth_earnings_profit(pop, prev_dividend, current_price):
    dividend, random_dividend = draw_dividend(prev_dividend)
    for ind in pop:
        former_wealth = ind.wealth
        div_asset = ind.asset_long * dividend # Determine gain from dividends
        interest_cash = ind.cash * INTEREST_RATE # Determine gain from interest
        ind.cash += REINVESTMENT_RATE * (div_asset + interest_cash) # Apply reinvestment
        ind.wealth = ind.cash + ind.asset_long * current_price - ind.loan # Compute new wealth
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


def count_tf(pop):
    count = 0
    for ind in pop:
        if ind.type == "tf":
            count += 1
    return count


def count_vi(pop):
    count = 0
    for ind in pop:
        if ind.type == "vi":
            count += 1
    return count


def count_nt(pop):
    count = 0
    for ind in pop:
        if ind.type == "nt":
            count += 1
    return count

def mean_tf(pop):
    total = 0
    mean = 0
    result = 0
    for ind in pop:
        if ind.type == "tf":
            total += 1
            mean += ind[0]
    if total != 0:
        result = mean/total
    return result

def mean_vi(pop):
    total = 0
    mean = 0
    result = 0
    for ind in pop:
        if ind.type == "vi":
            total += 1
            mean += ind[0]
    if total != 0:
        result = mean/total
    return result

def mean_nt(pop):
    total = 0
    mean = 0
    result = 0
    for ind in pop:
        if ind.type == "nt":
            total += 1
            mean += ind[0]
    if total != 0:
        result = mean/total
    return result

def total_wealth(pop):
    wealth = 0
    for ind in pop:
        wealth += ind.wealth
    return wealth

def wealth_share_tf(pop):
    wealth_tf = 0
    for ind in pop:
        if ind.type == "tf":
            wealth_tf += ind.wealth
    if 100 * wealth_tf / total_wealth(pop) > 100:
        raise ValueError("Wealth share TF superior to 100" + str(wealth_tf) + " // " + str(total_wealth(pop)))
  
    if 100 * wealth_tf / total_wealth(pop) < 0:
        raise ValueError("Wealth share TF negative" + str(wealth_tf) + " // " + str(total_wealth(pop)))
    return 100 * wealth_tf / total_wealth(pop)

def wealth_share_vi(pop):
    wealth_vi = 0
    for ind in pop:
        if ind.type == "vi":
            wealth_vi += ind.wealth
    if 100 * wealth_vi / total_wealth(pop) > 100:
        raise ValueError("Wealth share VI superior to 100" + str(wealth_vi) + " // " + str(total_wealth(pop)))
    if 100 * wealth_vi / total_wealth(pop) < 0:
        raise ValueError("Wealth share VI negative" + str(wealth_vi) + " // " + str(total_wealth(pop)))

    return 100 * wealth_vi / total_wealth(pop)

def wealth_share_nt(pop):
    wealth_nt = 0
    for ind in pop:
        if ind.type == "nt":
            wealth_nt += ind.wealth
    if 100 * wealth_nt / total_wealth(pop) > 100:
        raise ValueError("Wealth share NT superior to 100" + str(wealth_nt) + " // " + str(total_wealth(pop)))
    if 100 * wealth_nt / total_wealth(pop) < 0:
        raise ValueError("Wealth share NT negative" + str(wealth_nt) + " // " + str(total_wealth(pop)))
       
    
    return 100 * wealth_nt / total_wealth(pop)


def agg_ed(pop): 
    functions = []
    for ind in pop:
        if ind.type == "tf":
            def func(asset_key, p):
                return (LAMBDA_TF * ind.wealth / p) * (np.tanh(SCALE_TF * ind.tsv + 0.5)) - (ind.asset_long - ind.asset_short)
            functions.append(func)

        if ind.type == "vi":
            def func(asset_key, p):
                return (LAMBDA_VI * ind.wealth / p) * (np.tanh(np.log2(SCALE_VI * ind[0]) - np.log2(p) + 0.5)) - (ind.asset_long - ind.asset_short)
            functions.append(func)

        if ind.type == "nt":
            def func(p):
                return (LAMBDA_NT * ind.wealth / p) * (np.tanh(np.log2(SCALE_NT * ind[0] * ind.process) - np.log2(p) + 0.5)) - (ind.asset_long - ind.asset_short)
            functions.append(func)
    return functions