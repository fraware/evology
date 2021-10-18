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

def determine_tsv_proc(pop, price_history):
    # For TFs to have a TSV before determining their edf.
    for ind in pop:
        if ind.type == "tf":
            if len(price_history) >= ind[0]:
                ind.tsv = np.log2(price_history[-1]) - np.log2(price_history[-ind[0]])
            elif len(price_history) < ind[0]:
                ind.tsv = 0
        if ind.type == "nt":
            ind.process = abs(ind.process + RHO_NT * (MU_NT - ind.process) + GAMMA_NT * random.normalvariate(0,1))
            # if ind.process < 0:
            #     ind.process = 1

def update_fval(pop, dividend_history, div_g_estimation):
    # Update the vector of growth rate estimation
    # Run a new estimation
    # if len(dividend_history) <= 1:
    #     new_estimation = 0.01
    # if len(dividend_history) > 1:
    #     new_estimation = (dividend_history[-1] / dividend_history[-2]) - 1
    # div_g_estimation.append(new_estimation)
    # print(len(dividend_history))
    # if len(dividend_history) > 1:
    #     div_g_estimation = np.diff(np.log(dividend_history))
    #     # print(div_g_estimation)
    # elif len(dividend_history) <= 1:
    #     div_g_estimation.append(((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1)
    
    # # print(div_g_estimation)

    div_g_estimation = math.exp(mean(np.diff(np.log(dividend_history)))) - 1

    print(div_g_estimation)

    # print(div_g_estimation)
    # Remove an old estimation
    # if len(div_g_estimation) > LENGTH_DIVIDEND_ESTIMATION:
    #     del div_g_estimation[0]
    # Update agent fundamental values
    for ind in pop: 
        if ind.type == 'vi' or ind.type == 'nt':
            if len(dividend_history) > 0:
                ind[0] = ((1 + mean(div_g_estimation)) *  dividend_history[-1]) / (EQUITY_COST - (1 + mean(div_g_estimation)) ** 252 -1)
                ind[0] = 100
            # print(ind[0])
            if len(dividend_history) == 0:
                ind[0] = ((1 + mean(div_g_estimation)) * (INITIAL_DIVIDEND)) / (EQUITY_COST - ((1 + mean(div_g_estimation)) ** 252 -1))
                ind[0] = 100
    return pop, div_g_estimation

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
            return (LAMBDA_NT * ind.wealth / p) * (np.tanh(SCALE_NT * (np.log2(ind[0] * ind.process) - np.log2(p)) + 0.5)) - (ind.asset_long - ind.asset_short)
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
            total_buy += math.floor(ind.edv)
        elif ind.edv < 0:
            total_sell += math.floor(abs(ind.edv))

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
        print('long, short, +, -')
        print(count_long_assets(pop))
        print(count_long_assets(pop) + count_short_assets(pop))
        print(count_long_assets(pop) - count_short_assets(pop))
        raise ValueError('Asset supply constraint violated')
def execute_demand(pop, current_price, asset_supply):

    print('price ' + str(current_price))

    # Determine balanced excess demand values 
    multiplier_buy, multiplier_sell = determine_multiplier(pop)
    volume_buy, volume_sell = 0, 0

    for ind in pop:

        leverage_limit = ind.leverage * ind.wealth

        if ind.edv > 0:
            to_buy = ind.edv * multiplier_buy
            print('to_buy ' + str(to_buy))
            # print('value of the desired action vs what we dispose of')
            # print(to_buy * current_price)
            # print(ind.cash + leverage_limit - ind.loan)

            
            for j in range(math.floor(to_buy)):
                if ind.asset_short < 1:
                    if ind.cash >= current_price:
                        ind.cash -= current_price
                        ind.asset_long += 1
                        volume_buy += 1
                    elif ind.cash < current_price:
                        if ind.loan + current_price <= leverage_limit:
                            ind.loan += current_price
                            ind.asset_long += 1
                            volume_buy += 1
                elif ind.asset_short >= 1:
                    if ind.margin >= current_price:
                        ind.asset_short -= 1
                        ind.margin -= current_price
                        volume_buy += 1
                    elif ind.margin < current_price:
                        if ind.cash >= current_price:
                            ind.cash -= current_price
                            ind.asset_short -= 1
                            volume_buy += 1
                        elif ind.cash < current_price:
                            if ind.loan + current_price < leverage_limit:
                                ind.loan += current_price
                                ind.asset_short -= 1
                                volume_buy += 1
            print('Realised ' + str(volume_buy) + ' bought')
            # print('new cash and loan and leverage')
            # print(ind.cash)
            # print(ind.loan)
            # print(leverage_limit)
            # print(ind.leverage)

        
        if ind.edv < 0:
            to_sell = abs(ind.edv) * multiplier_sell
            print('to_sell ' + str(to_sell))
            for s in range(math.floor(to_sell)):
                if ind.asset_long >= 1:
                    ind.cash += current_price
                    ind.asset_long -= 1
                    volume_sell += 1
                elif ind.asset_long < 1:
                    if ind.asset_short * current_price < leverage_limit:
                        ind.asset_short += 1
                        ind.margin += current_price
                        volume_sell += 1
            print('Realised ' + str(volume_sell) + ' sold')
                
    execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell)

    volume = volume_buy + volume_sell



    # count_sold = 0
    
    # for ind in pop:
    #     if ind.edv < 0:
    #         to_sell = abs(ind.edv) * multiplier_sell
    #         before_long = ind.asset_long
    #         if ind.asset_long >= to_sell: 
    #             ind.cash += to_sell * current_price
    #             ind.asset_long -= to_sell
    #             count_sold += to_sell
    #         elif ind.asset_long < to_sell:
    #             # print('agent needs short sell')
    #             # print(to_sell)
    #             # print(ind.asset_long)
    #             ind.cash += ind.asset_long * current_price
                
    #             count_sold += ind.asset_long
    #             ind.asset_long = 0 

    #             to_short_sell = to_sell - ind.asset_long
                
    #             if ind.type == 'tf':
    #                 short_lambda = LAMBDA_TF
    #             if ind.type == 'nt':
    #                 short_lambda = LAMBDA_NT
    #             if ind.type == 'vi':
    #                 short_lambda = LAMBDA_VI

    #             short_limit = asset_supply + short_lambda

    #             if count_short_assets(pop) + to_sell <= short_limit:
    #                 ind.asset_short += to_short_sell
    #                 ind.margin += to_short_sell * current_price
    #             elif count_short_assets(pop) < short_limit and count_short_assets(pop) + to_sell > short_limit:
    #                 feasible_short_sell = min(to_short_sell, short_limit - count_short_assets(pop))
    #                 ind.asset_short += feasible_short_sell
    #                 ind.margin += feasible_short_sell * current_price
    #         # print('Agent ' + str(ind.type) + ' long changed by ' + str(ind.asset_long - before_long))
    #     # TODO: needs buyback of short positions
    # # print(count_sold)
    # if total_sell * multiplier_sell != 0:
    #     effective_buy_sell_ratio = count_sold / (total_sell * multiplier_sell)
    # elif total_sell * multiplier_sell == 0:
    #     effective_buy_sell_ratio = 0
    
    # if effective_buy_sell_ratio > 1.1:
    #     raise ValueError('buy sell effective ratio above 1')
    # if count_sold >= total_sell * multiplier_sell + 1:
    #     raise ValueError('Count sold higher than total sell multiplied')

    # # print('total sold and adjusted total buy')
    # # print(count_sold)
    # # print(effective_buy_sell_ratio)
    # # print(total_buy * multiplier_buy * effective_buy_sell_ratio)

    # for ind in pop:

    #     if ind.type == 'tf':
    #         loan_lambda = LAMBDA_TF
    #     if ind.type == 'nt':
    #         loan_lambda = LAMBDA_NT
    #     if ind.type == 'vi':
    #         loan_lambda = LAMBDA_VI

    #     ind.edv_var = ind.edv
    #     if ind.edv > 0:
    #         before_long = ind.asset_long
    #         to_buy = ind.edv * multiplier_buy * effective_buy_sell_ratio
    #         # if we have enough cash, this is easy
    #         if ind.cash >= to_buy * current_price:
    #             ind.cash -= to_buy * current_price
    #             ind.asset_long += to_buy
    #             ind.edv_var -= to_buy
    #         elif ind.cash < to_buy * current_price:
    #             if ind.loan (to_buy * current_price) < loan_lambda * ind.wealth: 
    #                 ind.asset_long += to_buy
    #                 ind.edv_var -= to_buy
    #                 ind.loan += (to_buy * current_price) - ind.cash
    #                 ind.cash = 0
    #         # print('Agent ' + str(ind.type) + ' long changed by ' + str(ind.asset_long - before_long))

    # # Buy back of short positions
    # bought_back = 0
    # for ind in pop:
    #     if ind.edv_var > 0:
    #         if ind.asset_short > 0:
    #             i = 0
    #             arr = np.array(ind.asset_short, ind.edv_var)
                
    #             for i in range(math.floor(min(ind.asset_short, ind.edv_var))):
    #                 while ind.cash + ind.margin > current_price:
    #                     if ind.margin >= current_price:
    #                         ind.asset_short -= 1
    #                         ind.margin -= current_price
    #                         bought_back += 1
    #                     elif ind.margin < current_price:
    #                         ind.cash -= current_price - ind.margin
    #                         ind.asset_short -= 1
    #                         ind.margin = 0
    #                         bought_back += 1
    # # print(str(bought_back) + ' short positions have been closed.')

    # # TODO: correct that
    # volume = total_buy * multiplier_buy + total_sell * multiplier_sell

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
            fval += ind.tsv
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
            fval += ind.tsv
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
            ind.tsv = np.log2(ind[0] * ind.process) - np.log2(price)
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
            total += ind.asset_long * price
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
            total += ind.asset_long * price
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
            total += ind.asset_long * price
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