import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Import the data
run = pd.read_csv("data/test_data.csv")
ref = pd.read_csv('data/replication_data.csv')

''' Dividends '''
data = df = pd.DataFrame()
data['Dividends (Reference)'] = ref['Dividends']
data['Dividends (Simulation)'] = run['Dividends']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["Dividends (Reference)", "Dividends (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of dividends', 
        color = ['black','black'],
        style = [':','-'])
plt.xlabel('Generations')
plt.ylabel('Daily dividend')
plt.show()

''' Price '''
data['Price (Reference)'] = ref['Price']
data['Price (Simulation)'] = run['Price']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["Price (Reference)", "Price (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of price', 
        color = ['black','black'],
        style = [':','-'])
plt.xlabel('Generations')
plt.ylabel('Price')
plt.show()

''' Volume '''
data['Volume (Reference)'] = ref['Volume']
data['Volume (Simulation)'] = run['Volume']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["Volume (Reference)", "Volume (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of volume', 
        color = ['black','black'],
        style = [':','-'])
plt.xlabel('Generations')
plt.ylabel('Volume')
plt.show()

''' Cash '''
data['NT Cash (Reference)'] = ref['NT_cash']
data['NT Cash (Simulation)'] = run['NT_cash']
data['VI Cash (Reference)'] = ref['VI_cash']
data['VI Cash (Simulation)'] = run['VI_cash']
data['TF Cash (Reference)'] = ref['TF_cash']
data['TF Cash (Simulation)'] = run['TF_cash']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["NT Cash (Reference)", "NT Cash (Simulation)","VI Cash (Reference)", 
    "VI Cash (Simulation)","TF Cash (Reference)", "TF Cash (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of agent cash', 
        color = ['r', 'r', 'g', 'g', 'b', 'b'],
        style = [':', '-', ':', '-', ':', '-'])
plt.xlabel('Generations')
plt.ylabel('Cash')
plt.show()

''' Lending (value of short positions) = margin'''
data['NT Lending (Reference)'] = abs(ref['NT_lending'])
data['NT Lending (Simulation)'] = run['NT_lending']
data['VI Lending (Reference)'] = abs(ref['VI_lending'])
data['VI Lending (Simulation)'] = run['VI_lending']
data['TF Lending (Reference)'] = abs(ref['TF_lending'])
data['TF Lending (Simulation)'] = run['TF_lending']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["NT Lending (Reference)", "NT Lending (Simulation)","VI Lending (Reference)", 
    "VI Lending (Simulation)","TF Lending (Reference)", "TF Lending (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of agent lending', 
        color = ['r', 'r', 'g', 'g', 'b', 'b'],
        style = [':', '-', ':', '-', ':', '-'])
plt.xlabel('Generations')
plt.ylabel('Lending')
plt.show()

''' Loans '''
data['NT Loans (Reference)'] = ref['NT_loan']
data['NT Loans (Simulation)'] = run['NT_loans']
data['VI Loans (Reference)'] = ref['VI_loan']
data['VI Loans (Simulation)'] = run['VI_loans']
data['TF Loans (Reference)'] = ref['TF_loan']
data['TF Loans (Simulation)'] = run['TF_loans']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["NT Loans (Reference)", "NT Loans (Simulation)","VI Loans (Reference)", 
    "VI Loans (Simulation)","TF Loans (Reference)", "TF Loans (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of agent loans', 
        color = ['r', 'r', 'g', 'g', 'b', 'b'],
        style = [':', '-', ':', '-', ':', '-'])
plt.xlabel('Generations')
plt.ylabel('Loans')
plt.show()

''' Net asset value (i.e. asset long * price) '''
data['NT NAV (Reference)'] = ref['NT_nav']
data['NT NAV (Simulation)'] = run['NT_nav']
data['VI NAV (Reference)'] = ref['VI_nav']
data['VI NAV (Simulation)'] = run['VI_nav']
data['TF NAV (Reference)'] = ref['TF_nav']
data['TF NAV (Simulation)'] = run['TF_nav']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["NT NAV (Reference)", "NT NAV (Simulation)","VI NAV (Reference)", 
    "VI NAV (Simulation)","TF NAV (Reference)", "TF NAV (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of agent net asset values', 
        color = ['r', 'r', 'g', 'g', 'b', 'b'],
        style = [':', '-', ':', '-', ':', '-'])
plt.xlabel('Generations')
plt.ylabel('Net asset value')
plt.show()


''' Profit and losses '''
data['NT PNL (Reference)'] = ref['NT_pnl']
data['NT PNL (Simulation)'] = run['NT_pnl']
data['VI PNL (Reference)'] = ref['VI_pnl']
data['VI PNL (Simulation)'] = run['VI_pnl']
data['TF PNL (Reference)'] = ref['TF_pnl']
data['TF PNL (Simulation)'] = run['TF_pnl']
data['Gen'] = run['Gen']
data.plot(x="Gen", y = ["NT PNL (Reference)", "NT PNL (Simulation)","VI PNL (Reference)", 
    "VI PNL (Simulation)","TF PNL (Reference)", "TF PNL (Simulation)"],
        kind="line", figsize=(15, 6), title='Comparison of agent profit and losses', 
        color = ['r', 'r', 'g', 'g', 'b', 'b'],
        style = [':', '-', ':', '-', ':', '-'])
plt.xlabel('Generations')
plt.ylabel('Profit and losses')
plt.show()