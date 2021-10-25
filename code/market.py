from parameters import *
import matplotlib
import matplotlib.pyplot as plt
import warnings
import balance_sheet as bs

def draw_dividend(dividend):
    global random_dividend

    DIVIDEND_GROWTH_RATE = ((1 + DIVIDEND_GROWTH_RATE_G) ** (1 / TRADING_DAYS)) - 1
    
    random_dividend = random.normalvariate(0, 1)
    if len(random_dividend_history) > DIVIDEND_ATC_TAU:
        random_dividend = (1 - DIVIDEND_AUTOCORRELATION ** 2) * random_dividend + DIVIDEND_AUTOCORRELATION * random_dividend_history[len(random_dividend_history) - 1 - DIVIDEND_ATC_TAU]

    dividend = abs(dividend + DIVIDEND_GROWTH_RATE * dividend + DIVIDEND_GROWTH_VOLATILITY * dividend * random_dividend)

    return dividend, random_dividend

def dividend_series(horizon):
    history = []
    dividend = INITIAL_DIVIDEND
    for i in range(horizon):
        dividend, rdiv = draw_dividend(dividend)
        history.append(dividend)
    return history




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

# def execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell, securities_contracts):




#     for ind in pop:
#         if ind.cash < 0:
#             print("Current price, type, edv, cash, asset_long, pop edvs")
#             print(ind.type)
#             print(ind.edv)
#             print(ind.cash)
#             print(ind.asset_long)
#             raise ValueError('Negative agent cash ')
#         if ind.asset_long < 0: 
#             print("Current price, type, edv, cash, asset_long, pop edvs")
#             print(ind.type)
#             print(ind.edv)
#             print(ind.cash)
#             print(ind.asset_long)
#             for ind in pop:
#                 print("pop")
#                 print(ind.type)
#                 print(ind.edv)
#             raise ValueError('Negative agent long ' )
#         if ind.asset_short < 0:
#             # print('pop: type, short, edv, edv_var')
#             # for ind in pop:
                
#             #     print(ind.type)
#             #     print(ind.asset_short)
#             #     print(ind.edv)
#             #     print(ind.edv_var)
#             raise ValueError('Negative agent short ' + str(ind.type) + str(ind.asset_short))

#     # if count_long_assets(pop) >= asset_supply + 1 or count_long_assets(pop) <= asset_supply - 1:
#     #     print("volume buy, sell, ind type and asset_long")
#     #     print(volume_buy)
#     #     print(volume_sell)
#     #     for ind in pop:
#     #         print(ind.type)
#     #         print(ind.asset_long)
#     #     print('long, short, +, -')
#     #     print(count_long_assets(pop))
#     #     print(count_long_assets(pop) + count_short_assets(pop))
#     #     print(count_long_assets(pop) - count_short_assets(pop))
#     #     raise ValueError('Asset supply constraint violated')

#     # if count_long_assets(pop)  >= asset_supply + 1 or count_long_assets(pop) <= asset_supply - 1:
#     #     print("volume buy, sell, ind type and asset_long")
#     #     print(volume_buy)
#     #     print(volume_sell)
#     #     print('supply, long, short')
#     #     print(asset_supply)
#     #     print(count_long_assets(pop))
#     #     print(count_short_assets(pop))
#     #     print(securities_contracts)
#     #     print('---------AGENTS: type, long, short , edv, edv_var -----')
#     #     for ind in pop:
#     #         print(str(ind.type) + ', ' + str(ind.asset_long) + ', ' + str(ind.asset_short) + ', ' + str(ind.edv) + ', ' + str(ind.edv_var))
#     #     raise ValueError('Asset supply constraint violated')

#     if bs.count_long_assets(pop) > asset_supply + 0.001: #+ count_short_assets(pop) > asset_supply + 0.001:
#         print('indm type, long, short, edv_var')
#         for ind in pop:
#             print('ind ' + str(ind.type) + ', ' + str(ind.asset_long) + ', ' + str(ind.asset_short) + ', ' + str(ind.edv_var))
#         raise ValueError('Asset supply violated (too many assets)' + str(bs.count_long_assets(pop) + bs.count_short_assets(pop)))
#     if bs.count_long_assets(pop) + bs.count_short_assets(pop) < asset_supply - 0.001:
#         raise ValueError('Asset supply violated (too few assets)' + str(bs.count_long_assets(pop) + bs.count_short_assets(pop)))

# def execute_demand(pop, current_price, asset_supply, securities_contracts):

#     # Determine balanced excess demand values 
#     multiplier_buy, multiplier_sell, total_buy, total_sell = determine_multiplier(pop)
#     # print('total buy/sell: ' + str(total_buy * multiplier_buy) + ', ' + str(total_sell * multiplier_sell))
#     volume_buy, volume_sell = 0, 0

#     sum_plus = 0 
#     sum_minus = 0
#     for ind in pop:
#         edv = ind.edv
#         if edv > 0:
#             ind.edv_var = edv * multiplier_buy
#             sum_plus += ind.edv_var
#         if edv < 0:
#             ind.edv_var = edv * multiplier_sell
#             sum_minus += ind.edv_var 
#     if abs(sum_plus + sum_minus) > 0.001 : 
#         raise ValueError('Imbalanced sum of ind.edv.var ' +str(sum_plus) + ', ' + str(sum_minus))

#     print('total long positions now ' +str(bs.count_long_assets(pop)))

#     print('ind: edv vars, long, short')
#     for ind in pop:
#         print(str(ind.type) + ', ' + str(ind.edv_var) + ', ' + str(ind.asset_long) + ', ' + str(ind.asset_short)) 

#     for i in range(len(pop)):
#         while pop[i].edv_var < -0.00001: # agent wants to sell
#             print('431')
#             while pop[i].asset_long > 0 and pop[i].edv_var < -0.00001:
#                 # print('sell long')
#                 # Agent will sell from inventory
#                 # Find a buyer
#                 print('scanning for buyer ' + str(pop[i].asset_long) + ', ' + str(pop[i].edv_var))
#                 for j in range(len(pop)):
#                     print('scanning')
#                     if pop[j].edv_var > 0:
#                         print(' found buyer ')
#                         # Determine transaction amount
#                         amount = min(abs(pop[i].edv_var), pop[i].asset_long, pop[j].edv_var)
#                         print(amount)

#                         # Exchange assets 
#                         pop[i].asset_long -= amount 
#                         pop[j].asset_long += amount 

#                         # Exchange money
#                         pop[i].cash += amount * current_price
#                         pop[j].loan += amount * current_price

#                         # TODO: make sure corrections to edv_var are going in the right way (less orders to execute)

#                         # Update current excess demand orders and volume
#                         pop[i].edv_var += amount 
#                         pop[j].edv_var -= amount
#                         volume_buy += amount
#                         volume_sell += amount
                    
                        
#                     # break # Break to check whether we want to sell.

#                 # if pop[i].edv_var == 0 or pop[i].asset_long == 0:
#                 #     break # If EDV_VAR is no longer negative, exit the loop

#                 if pop[i].edv_var > 0:
#                     raise ValueError('neg edv-var turned positive')
#                 if pop[i].asset_long < 0:
#                     raise ValueError('Asset long position turned negative')
            
#             # Now, we should still want to sell, but we don't have any long.
#             # Hence we short sell.

#             while pop[i].edv_var < -0.00001:
#                 leverage_limit = pop[i].leverage * pop[i].wealth
                    
#                 attempt = 0
#                 # Find someone to borrow a share from
#                 for j in range(len(pop)):
#                     if pop[i].edv_var < 0:
#                         print('scanning for someone to borrow a share from ' + str(pop[i].edv_var) + ', ' + str(pop[i].asset_long))

#                         if pop[j].asset_long > 0:
#                             print('found a j')
#                             # Find someone to buy the borrowed share 
#                             for m in range(len(pop)):
                                
#                                 if pop[m].edv_var > 0:
#                                     print('found a m')

#                                     # Determine transaction amount
#                                     amount = min(abs(pop[i].edv_var), pop[j].asset_long, pop[m].edv_var)
#                                     print('amount is ' +str(amount))
#                                     if amount < 0:
#                                         raise ValueError('Negative amount for short selling')

#                                     # new new new
#                                     # if (pop[i].asset_short + amount) * current_price <= leverage_limit:

#                                     # if (pop[i].asset_short + amount) * current_price <= leverage_limit:
                                    
#                                     # i borrows a share from j
#                                     securities_contracts[i,j] += amount
#                                     securities_contracts[j,i] -= amount
#                                     pop[i].asset_short += amount
#                                     pop[j].asset_long -= amount
#                                     pop[i].edv_var += amount

#                                     # i sells the share to m. m pays its price to i, who saves it as margin.  
#                                     pop[i].margin += amount * current_price
#                                     pop[m].asset_long += amount
#                                     pop[m].loan += amount * current_price
#                                     pop[m].edv_var -= amount
                                        
#                                     # Globals
#                                     volume_buy += amount
#                                     volume_sell += amount
                                


#                     attempt += 1  
#                 if attempt == 100:
#                     print('ind, type, edv, edv_var, assset_long')
#                     for ind in pop:
#                         print('ind ' + str(ind.type) + ', ' + str(ind.edv) + ', ' + str(ind.edv_var) + ', ' + str(ind.asset_long))
#                     raise ValueError(' Could not resolve short selling operation')
                    
            
#     # Now we are out of the loop. We went through all negative ED orders, so we should be balanced.
#     for ind in pop:
#         if abs(ind.edv_var) > 0.001:
#             print(ind.type)
#             print(ind.edv_var)
#             raise ValueError('Still edv var absolutely positive.')

#     # Now, try to close the short positions if we can.
#     for i in range(len(pop)):
#         if pop[i].asset_long > 0 and pop[i].asset_short > 0:
#             print('closing short (long / short' + str(pop[i].asset_long) + ', ' + str(pop[i].asset_short))
#             for j in range(len(pop)):
#                 if securities_contracts[i,j] > 0:
#                     amount = min(pop[i].asset_long, pop[i].asset_short, securities_contracts[i,j])
#                     pop[j].asset_long += amount 
#                     pop[i].asset_long -= amount ###
#                     pop[i].asset_short -= amount 
#                     securities_contracts[i,j] -= amount 
#                     securities_contracts[j,i] += amount 
#                 break

#     for ind in pop:
#         if abs(ind.edv_var) > abs(ind.edv):
#             warnings.warn('Ind edv var abs-higher than edv')
#     execute_demand_error_messages(pop, asset_supply, volume_buy, volume_sell, securities_contracts)
#     volume = volume_buy + volume_sell

#     if volume < 0:
#         raise ValueError('Negative volume')

#     return pop, volume, securities_contracts

def execute_ed(pop, current_price, asset_supply):

    # Determine adjustements to edv if we have some mismatch
    multiplier_buy, multiplier_sell, total_buy, total_sell = determine_multiplier(pop)
    volume = 0

    for ind in pop:
        if ind.edv > 0:
            amount = ind.edv * multiplier_buy
        
        if ind.edv < 0:
            amount = ind.edv * multiplier_sell
            
        ind.asset += amount 
        ind.cash -= amount * current_price
        volume += abs(amount)

        # Apply some some readjustment to avoid negative cash
        if ind.cash < 0:
            ind.loan += abs(ind.cash)
            ind.cash = 0
        
    if bs.count_long_assets(pop) > asset_supply + 0.001 or bs.count_long_assets(pop) < asset_supply - 0.001:
        raise ValueError('Asset supply cst violated ' +str(bs.count_long_assets(pop)))

    return pop, volume