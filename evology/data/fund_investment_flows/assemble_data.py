# %%
import pandas as pd

nport_data = pd.read_csv(
    "D:\\OneDrive\Research\\2021_Market_Ecology\\evology\\evology\\data\\fund_investment_flows\\nport_data.csv",
    encoding='windows-1254'
    )
print(nport_data)

# %%

path2 = 'D:\\OneDrive\Research\\2021_Market_Ecology\\evology\\evology\\data\\fund_investment_flows\\hako_data.xlsx'
hako_data = pd.read_excel(path2,
    sheet_name='DATA_3562fund')
print(hako_data)
# %%


hako_data.columns = [
    "Fund_code",
    "Month",
    "Investment_Style",
    "TNA_month_t",
    "TNA_month_t1",
    "Monthly_returns",
    "Age(months)",
    "Expense_ratio",
    "New_sales",
    "Redeemed_cash",
    "Est_Net_flows",
    "Net_flows",
    "Inflows", #sales/TNA
    "Outflows", #redeemed/TNA
    "Objective_monthly_returns",
    "Objective_monthly_agg_net_flows",
    "Obs_included"

]

# %%
print(hako_data)
# %%
hako_data.to_csv("hako_data.csv")
# %%
