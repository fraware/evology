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

    return multiplier_buy, multiplier_sell, total_buy, total_sell

def execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell, securities_contracts):




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
            # print('pop: type, short, edv, edv_var')
            # for ind in pop:
                
            #     print(ind.type)
            #     print(ind.asset_short)
            #     print(ind.edv)
            #     print(ind.edv_var)
            raise ValueError('Negative agent short ' + str(ind.type) + str(ind.asset_short))

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

    if count_long_assets(pop)  >= asset_supply + 1 or count_long_assets(pop) <= asset_supply - 1:
        print("volume buy, sell, ind type and asset_long")
        print(volume_buy)
        print(volume_sell)
        print('supply, long, short')
        print(asset_supply)
        print(count_long_assets(pop))
        print(count_short_assets(pop))
        print(securities_contracts)
        print('---------AGENTS: type, long, short , edv, edv_var -----')
        for ind in pop:
            print(str(ind.type) + ', ' + str(ind.asset_long) + ', ' + str(ind.asset_short) + ', ' + str(ind.edv) + ', ' + str(ind.edv_var))
        raise ValueError('Asset supply constraint violated')

def execute_buy(i, pop, current_price, leverage_limit, volume_buy, amount, securities_contracts):
    starting_volume = volume_buy

    # we start by closing some short positions if we have any
    to_buy = amount

    if pop[i].asset_short > 0: # If we have short positions to close
        for j in range(len(pop)):# iterate over the population to find who we are in debt with
                if securities_contracts[i,j] > 0: # If we owe shares to this trader j:
                    # Find someone who can sell us some shares so we can close our position
                    for n in range(len(pop)):
                        if pop[n].edv_var < 0 and pop[n].asset_long > 0:

                            # Determine the transaction amount
                            bought_back = min(securities_contracts[i,j], to_buy, abs(pop[n].edv_var), pop[n].asset_long) 

                            # i buys asset shares from n, and pays to n.

                            pop[n].asset_long -= bought_back
                            pop[n].cash += current_price * bought_back

                            if pop[i].margin >= current_price * bought_back:
                                pop[i].margin -= current_price * bought_back
                            elif pop[i].cash >= current_price * bought_back:
                                pop[i].cash -= current_price * bought_back
                            elif pop[i].cash < current_price * bought_back:
                                pop[i].loan += current_price * bought_back

                            pop[i].edv_var -= bought_back
                            pop[n].edv_var += bought_back

                            # i directly gives the asset share back to j. The contract is closed (up to the transaction amount)
                            pop[j].asset_long += bought_back

                            securities_contracts[i,j] -= bought_back
                            securities_contracts[j,i] += bought_back
                            pop[i].asset_short -= bought_back

                            # Globals
                            volume_buy += bought_back
                            to_buy -= bought_back
    
    # Next we have to buy to_buy long positions
    # We buy them in cash if we can
    if pop[i].cash >= current_price * to_buy: # Do we have the cash to buy?
        pop[i].cash -= current_price * to_buy
        pop[i].asset_long += to_buy
        pop[i].edv_var -= to_buy
        volume_buy += to_buy
    
    # We buy them wiht loans if we cannot use cash, and if we can extend our loan
    elif pop[i].cash < current_price * to_buy: 
        if pop[i].loan + current_price * to_buy <= leverage_limit: 
            pop[i].loan += current_price * to_buy
            pop[i].asset_long += to_buy
            pop[i].edv_var -= to_buy
            volume_buy += to_buy
        elif pop[i].loan + current_price * to_buy > leverage_limit: 
            raise ValueError('could not buy long because of loan limit')

    if volume_buy - starting_volume < amount - 0.001:
        raise ValueError('Did not execute all amount for buying ' + str(volume_buy - starting_volume - amount))
    return pop, volume_buy, securities_contracts

def execute_sell(i, pop, current_price, leverage_limit, volume_sell, volume_buy, amount, securities_contracts):
    starting_volume = volume_sell

    sold_this_round = 0

    # If we have enough long assets to sell the amount, then sell our long assets.
    if pop[i].asset_long >= amount: 
        pop[i].cash += current_price * amount
        pop[i].asset_long -= amount
        volume_sell += amount
        pop[i].edv_var += amount
        sold_this_round += amount

    # If we don't have enough long assets to sell the amount, we split and/or short sell.
    elif pop[i].asset_long < amount: 

        amount_sold = 0
        if pop[i].asset_long > 0:
            pop[i].cash += pop[i].asset_long * current_price
            volume_sell += pop[i].asset_long
            amount_sold = pop[i].asset_long
            sold_this_round += pop[i].asset_long
            pop[i].edv_var -= pop[i].asset_long 
            pop[i].asset_long -= 0

        amount_to_short = amount - amount_sold
        print('we have to short ' + str(amount_to_short))

        # Then attempt to short sell the rest
        if (pop[i].asset_short + amount_to_short) * current_price < leverage_limit: # If our short position is not too large
            to_short = amount_to_short

            if to_short > 0:
                for j in range(len(pop)):
                    if pop[j].asset_long > 0: # Find a fund that can lend us some shares
                        for m in range(len(pop)):
                            # if m != j:
                            if pop[m].edv_var > 0: # Find a fund that will buy the borrowed share

                                # Determine feasible short selling amount (something we want to, that we can buy, that we can sell)
                                feasible = min(pop[j].asset_long, to_short, pop[m].edv_var)
                                # print('feasible ' + str(feasible))

                                # i borrows a share from j
                                securities_contracts[i,j] += feasible
                                securities_contracts[j,i] -= feasible
                                pop[i].asset_short += feasible
                                pop[j].asset_long -= feasible
                                pop[i].edv_var += feasible
                                
                                # i sells the share to m. m pays its price to i, who saves it as margin.
                                
                                pop[i].margin += feasible * current_price
                                pop[m].asset_long += feasible
                                pop[m].loan += feasible * current_price
                                pop[m].edv_var -= feasible

                                # Globals
                                volume_buy += feasible
                                volume_sell += feasible
                                to_short -= feasible
                                sold_this_round += feasible
        else:
            print('could not short sell anything')
   
    if volume_sell - starting_volume < amount - 0.001:
        print('Individual i of type: ')
        print(i)
        print(pop[i].type)
        print('While pop has types, edv, edv_var and asset_long:')
        for ind in pop:
            print(ind.type)
            print(ind.edv)
            print(ind.edv_var)
            print(ind.asset_long)
        raise ValueError('Did not execute all amount for selling. Wanted to sell ' + str(amount) + ' and sold ' + str(volume_sell - starting_volume) + " // " + str(sold_this_round))

    return pop, volume_sell, volume_buy, securities_contracts

def execute_demand(pop, current_price, asset_supply, securities_contracts):

    # Determine balanced excess demand values 
    multiplier_buy, multiplier_sell, total_buy, total_sell = determine_multiplier(pop)
    print('total buy/sell: ' + str(total_buy * multiplier_buy) + ', ' + str(total_sell * multiplier_sell))
    volume_buy, volume_sell = 0, 0

    sum_plus = 0 
    sum_minus = 0
    for ind in pop:
        edv = ind.edv
        if edv > 0:
            ind.edv_var = edv * multiplier_buy
            sum_plus += ind.edv_var
        if edv < 0:
            ind.edv_var = edv * multiplier_sell
            sum_minus += ind.edv_var 
    if abs(sum_plus + sum_minus) > 0.001 : 
        raise ValueError('Imbalanced sum of ind.edv.var ' +str(sum_plus) + ', ' + str(sum_minus))
    

    
    for i in range(len(pop)):
        if pop[i].edv_var < 0: # agent wants to sell

            while pop[i].asset_long > 0 and pop[i].edv_var < -0.001: # if agent want / can sell from own inventory

                print('stuck in selling from inventory  (edvvar, long)' + str(pop[i].edv_var) + ', ' + str(pop[i].asset_long))
                # try to find an agent looking to buy
                for j in range(len(pop)):
                    if pop[j].edv_var > 0:
                        # determine transaction amount
                        amount = min(pop[i].asset_long, pop[j].edv_var, abs(pop[i].edv_var))
                        if amount < 0:
                            raise ValueError('Negative amount')
                        if amount > pop[i].asset_long: 
                            raise ValueError('Unfeasible long sell')

                        # Exchange assets 
                        pop[i].asset_long -= amount 
                        pop[j].asset_long += amount 

                        # Exchange money
                        pop[i].cash += amount * current_price
                        pop[j].loan += amount * current_price

                        # Update current excess demand orders and volume
                        pop[i].edv_var += amount 
                        pop[j].edv_var -= amount
                        volume_buy += amount
                        volume_sell += amount

                if pop[i].asset_long < 0:
                    raise ValueError('Negative long position')

            # if instead agents can no longer sell from own inventory, they will short sell
            if pop[i].asset_long == 0 and pop[i].edv_var < -0.001:
                # Find someone to borrow a share from
                for j in range(len(pop)):
                    if pop[j].asset_long > 0:
                        # Find someone to buy the borrowed share 
                        for m in range(len(pop)):
                            if pop[m].edv_var > 0:
                                # Determine transaction amount
                                amount = min(abs(pop[i].edv_var), pop[j].asset_long, pop[m].edv_var)
                                if amount < 0:
                                    raise ValueError('Negative amount for short selling')

                                # i borrows a share from j
                                securities_contracts[i,j] += amount
                                securities_contracts[j,i] -= amount
                                pop[i].asset_short += amount
                                pop[j].asset_long -= amount
                                pop[i].edv_var += amount

                                # i sells the share to m. m pays its price to i, who saves it as margin.  
                                pop[i].margin += amount * current_price
                                pop[m].asset_long += amount
                                pop[m].loan += amount * current_price
                                pop[m].edv_var -= amount
                                    
                                # Globals
                                volume_buy += amount
                                volume_sell += amount


                
                if pop[i].asset_short * current_price > pop[i].wealth * ind.leverage:
                    warnings.warn('Agent short position exceeds its leverage limit.')
                # We may want to include this in the regular code as a condition. 
                # After all, now that we do the regular matching, if agents can't trade, 
                # this does not result in an imbalance.

        # print('Successfuly went over selling')

        # for ind in pop:
        #     print('Agent type edv edv_var ' + str(ind.type) + ', ' + str(ind.edv) + ', ' + str(ind.edv_var))

        if pop[i].edv_var > 0: # if the agent wants to buy:
            while pop[i].asset_short > 0: # If we have short positons to close
                print('stuck in closing shorts')
                for j in range(len(pop)):
                    if securities_contracts[i,j] < 0: # If we owe to agent j:
                        # Find someone n who can sell us some shares so we can close our position to j
                        for n in range(len(pop)):
                            if pop[n].edv_var < 0 and pop[n].asset_long > 0:

                                # Determine the transaction amount
                                amount = min(securities_contracts[i,j], pop[i].asset_short, abs(pop[n].edv_var), pop[n].asset_long) 

                                # i buys asset shares from n, and pays to n.
                                pop[n].asset_long -= amount
                                pop[n].cash += current_price * amount

                                if pop[i].margin >= current_price * amount:
                                    pop[i].margin -= current_price * amount
                                elif pop[i].cash < current_price * amount:
                                    pop[i].loan += current_price * amount

                                pop[i].edv_var -= amount
                                pop[n].edv_var += amount

                                # i directly gives the asset share back to j. The contract is closed (up to the transaction amount)
                                pop[j].asset_long += amount
                                securities_contracts[i,j] -= amount
                                securities_contracts[j,i] += amount
                                pop[i].asset_short -= amount

                                if pop[i].asset_short < 0:
                                    raise ValueError('Negative agent short during closing')

                                # Globals
                                volume_buy += amount
                                volume_sell += amount # new addition
    
            if pop[i].edv_var > 0:
                # We should now have closed our short positions. We can buy long.    
                for j in range(len(pop)):
                    if pop[j].edv_var < 0 and pop[j].asset_long > 0:
                        # determine transaction amount
                        amount = min(pop[i].edv_var, abs(pop[j].edv_var), pop[j].asset_long)

                        # exchange assets and payment
                        pop[j].cash += amount * current_price 
                        pop[i].loan -= amount * current_price 
                        pop[i].asset_long += amount 
                        pop[j].asset_long -= amount 

                        # globals
                        volume_buy += amount 
                        volume_sell += amount
                        pop[i].edv_var -= amount 
                        pop[j].edv_var += amount 

    # ###############################################

    # # for ind in pop:
    # for i in range(len(pop)):

    #     # determine agent leverage limit 
    #     leverage_limit = pop[i].leverage * pop[i].wealth

    #     if pop[i].edv_var < 0: # if agent wants to sell
    #         # to_sell = abs(pop[i].edv_var) * multiplier_sell # adjust the amount to clear markets
    #         to_sell = abs(ind.edv_var)
    #         print('to sell ' + str(to_sell))
    #         ss = ORDER_BATCH_SIZE # execute clearing of orders
    #         while ss <= to_sell:
    #             pop, volume_sell, volume_buy, securities_contracts = execute_sell(i, pop, current_price, leverage_limit, 
    #             volume_sell, volume_buy, ORDER_BATCH_SIZE, securities_contracts)
    #             ss += ORDER_BATCH_SIZE
    #         reminder = to_sell - (ss - ORDER_BATCH_SIZE) 
    #         if reminder > 0:
    #             pop, volume_sell, volume_buy, securities_contracts = execute_sell(i, pop, current_price, leverage_limit, 
    #             volume_sell, volume_buy, reminder, securities_contracts)
    #         if reminder < 0:
    #             raise ValueError('Negative reminder')
    #         del reminder
                
    # for i in range(len(pop)):
    #     if pop[i].edv_var > 0: # if agent wants to buy
    #         # to_buy = pop[i].edv_var * multiplier_buy # revise order size to clear markets
    #         to_buy = ind.edv_var
    #         print('to buy '+ str(to_buy))
    #         bb = ORDER_BATCH_SIZE
    #         while bb <= to_buy: # execute as many orders as we can to speed up the process
    #             pop, volume_buy, securities_contracts = execute_buy(i, pop, current_price, leverage_limit, 
    #             volume_buy, ORDER_BATCH_SIZE, securities_contracts)
    #             bb += ORDER_BATCH_SIZE
    #         reminder = to_buy - (bb - ORDER_BATCH_SIZE) # clear the last orders 

    #         if reminder < 0:
    #             raise ValueError('Negative reminder')
    #         if reminder > 0:
    #             pop, volume_buy, securities_contracts = execute_buy(i, pop, current_price, leverage_limit, 
    #             volume_buy, reminder, securities_contracts)
    #         del reminder 

    # print('Succesfull went over buying')
    for ind in pop:
        if abs(ind.edv_var) > abs(ind.edv):
            warnings.warn('Ind edv var abs-higher than edv')
    execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell, securities_contracts)
    volume = volume_buy + volume_sell

    return pop, volume, securities_contracts

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
            warnings.warn('Wealth adjustement not perfect after MAX_ATTEMPTS.')

        # print('Wealth shield deployed. ' + str(generation))
            



        

        

