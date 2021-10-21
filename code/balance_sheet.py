from operator import index
import numpy as np
from numpy.core.fromnumeric import mean
from parameters import *
from market import *
import inspect
import math
import warnings
# np.seterr(divide = 'ignore') 

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
        ind.prev_wealth = ind.wealth
        ind.wealth = ind.cash + ind.asset_long * current_price - ind.loan
        # The amount due by short selling is equally captured by the margin, hence does not appear here.
    return ind

def determine_tsv_proc(pop, price_history, process_history):
    # For TFs to have a TSV before determining their edf.
    for ind in pop:
        if ind.type == "tf":
            if len(price_history) >= ind[0]:
                ind.tsv = np.log2(price_history[-1]) - np.log2(price_history[-ind[0]])
            elif len(price_history) < ind[0]:
                ind.tsv = 0
        if ind.type == "nt":
            #ind.process = abs(ind.process + RHO_NT * (MU_NT - ind.process) + GAMMA_NT * random.normalvariate(0,1))
            # ind.process = ind.process + RHO_NT * (np.log2(MU_NT) - np.log2(ind.process)) + GAMMA_NT * ind.process * random.normalvariate(0,1)
            if len(process_history) > 1:
                ind.process = ind.process + RHO_NT * (MU_NT - process_history[-2]) + GAMMA_NT * random.normalvariate(0,1)
            elif len(process_history) <= 1:
                ind.process = ind.process + GAMMA_NT * random.normalvariate(0,1)
            process_history.append(ind.process)

def update_fval(pop, extended_dividend_history):
    estimated_daily_div_growth = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1
    annualised_estimated_daily_div_growth = (1 + estimated_daily_div_growth) ** 252 - 1

    numerator = (1 + estimated_daily_div_growth) * extended_dividend_history[-1] # correct
    denuminator = (1 + EQUITY_COST - annualised_estimated_daily_div_growth) ** (1/252) - 1
    fval = numerator / denuminator

    for ind in pop: 
        if ind.type == 'vi' or ind.type == 'nt':
            ind[0] = fval
    return pop

def record_fval(pop):
    fval = 0
    for ind in pop:
        if ind.type == 'nt' or ind.type == 'vi':
            fval = ind[0]
    return fval

def determine_edf(pop):
    def edf(ind, p):
        if ind.type == "tf":
            return (LAMBDA_TF * ind.wealth / p) * (np.tanh(SCALE_TF * ind.tsv + 0.5)) - (ind.asset_long - ind.asset_short)
        elif ind.type == "vi":
            return (LAMBDA_VI * ind.wealth / p) * (np.tanh(SCALE_VI * (np.log2(ind[0]) - np.log2(p)) + 0.5)) - (ind.asset_long - ind.asset_short)
        elif ind.type == "nt":
            return (LAMBDA_NT * ind.wealth / p) * (np.tanh(SCALE_NT * (np.log2(ind[0] * abs(ind.process)) - np.log2(p)) + 0.5)) - (ind.asset_long - ind.asset_short)
    for ind in pop:
        ind.edf = edf
    return pop

def calculate_edv(pop, price):
    for ind in pop:
        ind.edv =  ind.edf(ind, price)
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

def determine_multiplier(pop):

    total_buy = 0
    total_sell = 0

    for ind in pop:
        if ind.edv > 0:
            # total_buy += math.floor(ind.edv)
            total_buy += (ind.edv)
        elif ind.edv < 0:
            # total_sell += math.floor(abs(ind.edv))
            total_sell += abs(ind.edv)


    if total_sell != 0:
        order_ratio = total_buy / total_sell 
    elif total_sell == 0:
        order_ratio = 0

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

    return multiplier_buy, multiplier_sell

def execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell):




    for ind in pop:
        if ind.cash < 0:
            print("Current price, type, edv, cash, asset_long, pop edvs")
            print(ind.type)
            print(ind.edv)
            print(ind.cash)
            print(ind.asset_long)
            raise ValueError('Negative agent cash ')
        if ind.asset_long < 0: 
            print("Current price, type, edv, cash, asset_long, pop edvs")
            print(ind.type)
            print(ind.edv)
            print(ind.cash)
            print(ind.asset_long)
            for ind in pop:
                print("pop")
                print(ind.type)
                print(ind.edv)
            raise ValueError('Negative agent long ' )
        if ind.asset_short < 0:
            raise ValueError('Negative agent short')

    # if count_long_assets(pop) >= asset_supply + 1 or count_long_assets(pop) <= asset_supply - 1:
    #     print("volume buy, sell, ind type and asset_long")
    #     print(volume_buy)
    #     print(volume_sell)
    #     for ind in pop:
    #         print(ind.type)
    #         print(ind.asset_long)
    #     print('long, short, +, -')
    #     print(count_long_assets(pop))
    #     print(count_long_assets(pop) + count_short_assets(pop))
    #     print(count_long_assets(pop) - count_short_assets(pop))
    #     raise ValueError('Asset supply constraint violated')

    if count_long_assets(pop) - count_short_assets(pop) >= asset_supply + 1 or count_long_assets(pop) - count_short_assets(pop) <= asset_supply - 1:
        print("volume buy, sell, ind type and asset_long")
        print(volume_buy)
        print(volume_sell)
        for ind in pop:
            print(ind.type)
            print(ind.asset_long)
        print('supply, long, short, +, -')
        print(asset_supply)
        print(count_long_assets(pop))
        print(count_short_assets(pop))
        print(count_long_assets(pop) + count_short_assets(pop))
        print(count_long_assets(pop) - count_short_assets(pop))
        raise ValueError('Asset supply constraint violated')

def execute_buy(ind, current_price, leverage_limit, volume_buy, amount):
    if ind.asset_short < amount:
        if ind.cash >= current_price * amount:
            ind.cash -= current_price * amount
            ind.asset_long += amount
            volume_buy += amount
        elif ind.cash < current_price * amount:
            if ind.loan + current_price * amount <= leverage_limit:
                ind.loan += current_price * amount
                ind.asset_long += amount
                volume_buy += amount
    elif ind.asset_short >= amount:
        if ind.margin >= current_price * amount:
            ind.asset_short -= amount
            ind.margin -= current_price * amount
            volume_buy += amount
        elif ind.margin < current_price * amount:
            if ind.cash >= current_price * amount:
                ind.cash -= current_price * amount
                ind.asset_short -= amount
                volume_buy += amount
            elif ind.cash < current_price * amount:
                if ind.loan + current_price  * amount < leverage_limit:
                    ind.loan += current_price * amount
                    ind.asset_short -= amount
                    volume_buy += amount
    return ind, volume_buy

def execute_sell(ind, current_price, leverage_limit, volume_sell, amount):
    if ind.asset_long >= amount:
        ind.cash += current_price * amount
        ind.asset_long -= amount
        volume_sell += amount
    elif ind.asset_long < amount:
        if (ind.asset_short + amount) * current_price < leverage_limit:
            ind.asset_short += amount
            ind.margin += current_price * amount
            volume_sell += amount
    return ind, volume_sell

def execute_demand(pop, current_price, asset_supply):

    # Determine balanced excess demand values 
    multiplier_buy, multiplier_sell = determine_multiplier(pop)
    volume_buy, volume_sell = 0, 0

    for ind in pop:

        leverage_limit = ind.leverage * ind.wealth

        if ind.edv > 0:
            to_buy = ind.edv * multiplier_buy
            # print('to_buy' + str(to_buy))
            j = ORDER_BATCH_SIZE
            while j <= to_buy:
                ind, volume_buy = execute_buy(ind, current_price, leverage_limit, volume_buy, ORDER_BATCH_SIZE)
                j += ORDER_BATCH_SIZE
            
            reminder = to_buy - (j - ORDER_BATCH_SIZE)
            if reminder < 0:
                raise ValueError('Negative reminder')
            if reminder > 0:
                ind, volume_buy = execute_buy(ind, current_price, leverage_limit, volume_buy, reminder)
            del reminder 

        if ind.edv < 0:
            to_sell = abs(ind.edv) * multiplier_sell
            # print('to sell ' + str(to_sell))
            s = ORDER_BATCH_SIZE
            while s <= to_sell:
                ind, volume_sell = execute_sell(ind, current_price, leverage_limit, volume_sell, ORDER_BATCH_SIZE)
                s += ORDER_BATCH_SIZE

            reminder = to_sell - (s - ORDER_BATCH_SIZE) 
            if reminder > 0:
                ind, volume_sell = execute_sell(ind, current_price, leverage_limit, volume_sell, reminder)
            if reminder < 0:
                raise ValueError('Negative reminder')
            del reminder
                
    execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell)
    volume = volume_buy + volume_sell

    return pop, volume

def earnings(pop, prev_dividend, current_price):
    dividend, random_dividend = draw_dividend(prev_dividend)
    for ind in pop:
        # former_wealth = ind.wealth
        div_asset = ind.asset_long * dividend # Determine gain from dividends
        interest_cash = ind.cash * INTEREST_RATE # Determine gain from interest
        ind.cash += REINVESTMENT_RATE * (div_asset + interest_cash) # Apply reinvestment
        # ind.wealth = ind.cash + ind.asset_long * current_price - ind.loan # Compute new wealth
        # ind.profit = ind.wealth - former_wealth  # Compute profit as difference of wealth
        
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
  
def report_nt_signal(pop):
    fval = 0
    num = 0
    fval_round = 0
    for ind in pop:
        if ind.type == "nt":
            fval += ind[0] * ind.process
            num += 1
    if num != 0:
        fval_round = fval/num
    return fval_round

def report_vi_signal(pop):
    fval = 0
    num = 0
    fval_round = 0
    for ind in pop:
        if ind.type == "vi":
            fval += ind[0]
            num += 1
    if num != 0:
        fval_round = fval/num
    return fval_round

def report_tf_signal(pop):
    fval = 0
    num = 0
    fval_round = 0
    for ind in pop:
        if ind.type == "tf":
            fval += ind.tsv
            num += 1
    if num != 0:
        fval_round = fval/num
    return fval_round

def calculate_tsv(pop, price, price_history):
    for ind in pop:
        if ind.type == 'tf':
            pass # TSV already computed in calcualte_tsv_proc
        if ind.type == 'vi':
            ind.tsv = np.log2(ind[0]) - np.log2(price)
        if ind.type == 'nt':
            ind.tsv = np.log2(ind[0] * abs(ind.process)) - np.log2(price)
    return ind



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
    def big_edf(asset_key, price):
        result = 0
        for ind in pop:
            result += ind.edf(ind, price)
        return result
    functions.append(big_edf)
    return functions


def share_spoils(pop, spoils):
    if spoils > 0:
        print('Allocating ' + str(spoils) + ' spoils')
        per_ind_spoil = spoils / len(pop)
        for ind in pop:
            ind.asset_long += per_ind_spoil
    return pop

def report_nt_cash(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.cash
    if num != 0:
        cash = total / num
    return cash

def report_vi_cash(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.cash
    if num != 0:
        cash = total / num
    return cash

def report_tf_cash(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.cash
    if num != 0:
        cash = total / num
    return cash

def report_nt_lending(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.margin
    if num != 0:
        cash = total / num
    return cash

def report_vi_lending(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.margin
    if num != 0:
        cash = total / num
    return cash

def report_tf_lending(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.margin
    if num != 0:
        cash = total / num
    return cash
    
def report_nt_loan(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.loan
    if num != 0:
        cash = total / num
    return cash

def report_vi_loan(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.loan
    if num != 0:
        cash = total / num
    return cash

def report_tf_loan(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.loan
    if num != 0:
        cash = total / num
    return cash

def report_nt_nav(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.wealth
    if num != 0:
        cash = total / num
    return cash

def report_vi_nav(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.wealth
    if num != 0:
        cash = total / num
    return cash

def report_tf_nav(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.wealth
    if num != 0:
        cash = total / num
    return cash

def report_nt_pnl(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.profit
    if num != 0:
        cash = total / num
    return cash

def report_vi_pnl(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.profit
    if num != 0:
        cash = total / num
    return cash

def report_tf_pnl(pop):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.profit
    if num != 0:
        cash = total / num
    return cash

def report_nt_stocks(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'nt':
            num += 1
            total += ind.asset_long * price
    if num != 0:
        cash = total / num
    return cash

def report_vi_stocks(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'vi':
            num += 1
            total += ind.asset_long * price
    if num != 0:
        cash = total / num
    return cash

def report_tf_stocks(pop, price):
    total = 0
    num = 0
    cash = 0
    for ind in pop:
        if ind.type == 'tf':
            num += 1
            total += ind.asset_long * price
    if num != 0:
        cash = total / num
    return cash

def determine_strat_size(pop):
    size_nt, num_nt = 0, 0
    size_vi, num_vi = 0, 0
    size_tf, num_tf = 0, 0 
    for ind in pop:
        if ind.type == 'nt':
            size_nt += ind.wealth
            num_nt += 1
        if ind.type == 'vi':
            size_vi += ind.wealth
            num_vi += 1
        if ind.type == 'tf':
            size_tf += ind.wealth
            num_tf += 1
    all_size = size_vi + size_tf + size_nt 
    if all_size == 0:
        raise ValueError('All size = 0')

    current_nt = size_nt / all_size
    current_vi = size_vi / all_size
    current_tf = size_tf / all_size
    currents = [current_nt, current_vi, current_tf]

    return currents, size_nt, size_vi, size_tf, all_size, num_nt, num_vi, num_tf

def determine_differences(coordinates, pop):
    # Determine targets
    target_nt = coordinates[0]
    target_vi = coordinates[1]
    target_tf = coordinates[2]
    targets = [target_nt, target_vi, target_tf]

    # Determine size of strategies
    currents, size_nt, size_vi, size_tf, all_size, num_nt, num_vi, num_tf = determine_strat_size(pop)
    sizes = [size_nt, size_vi, size_tf]
    nums = [num_nt, num_vi, num_tf]

    # print('Currents ' + str(currents))
    # print('Targets ' + str(targets))

    differences = [x1 - x2 for (x1, x2) in zip(currents, targets)]
    return differences, targets, sizes, all_size, nums 

def shield_wealth(generation, pop, coordinates:list, current_price):

    if sum(coordinates) > 1:
        raise ValueError('Sum coordinates higher than 1')

    if generation <= SHIELD_DURATION:
        pop_types = ['nt','vi','tf']

        differences, targets, sizes, all_size, nums = determine_differences(coordinates, pop)
        # print('Differences')
        # print(differences)

        attempt = 0
        while any([abs(x) >= SHIELD_TOLERANCE for x in differences]) and attempt < MAX_ATTEMPTS:
            # We must continue to adjust wealth. 

            # Go through items of differences to see which strategies need a correction.
            for i in range(len(differences)):
                # If the absolute difference is above threshold and inferior, we bump this strategy.
                if abs(differences[i]) > SHIELD_TOLERANCE and differences[i] < 0:
                # Apply a correction round
                    # if i == 0 # bumping nt
                    # if i == 1 #bumping vi
                    # if i == 2 #bumping tf
                    amount = (targets[i] * all_size - sizes[i]) / (1 - targets[i])
                    if amount < 0:
                        raise ValueError('Negative bump size ' + str(amount))
                    per_capita_amount = amount / nums[i]
                    for ind in pop:
                        if ind.type == pop_types[i]:
                            ind.loan -= per_capita_amount
                    

            # Recompute wealth, differences and attempts
            calculate_wealth(pop, current_price) # Compute agents' wealth
            differences, targets, sizes, all_size, nums = determine_differences(coordinates, pop)
            # print('Current differences: ' + str(differences))
            attempt += 1

        if attempt >= MAX_ATTEMPTS:
            raise ValueError('Wealth adjustement unsuccesful after MAX_ATTEMPTS.')

        # print('Wealth shield deployed. ' + str(generation))
            



        

        

