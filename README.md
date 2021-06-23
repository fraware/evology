# Known issues

- Does hypermutation creates unintended assets? Seems like it uses the same initialisation with 5 assets
- How can replacements be negative?

- Price (& wealth) goes to infinity

``` Mechanism: we are now strictly enforcing the fixed asset supply Q. Given we don't have prior price series, all start with trading signals equal to 0, and want to buy assets. This is not possible, as noone is selling. The agents gain cash, dividend, interest at each turn, augmenting their excess demand, augmenting the clearing price. As a result, there is a positive trend in prices, hence trading signals become positive, the agents keep wanting more assets and it is still impossible for them to buy any, as noone is selling and current ownerships saturate the fixed asset supply.```

Idea: if we generate a "balanced" price series before (Brownian motion generator?), we give agents the possibility of having a "balanced market". If the prior time series is balanced enough between increase & decrease, some agents will buy, and others will sell.
But won't this issue appear as soon as we saturate the Q constraint even once?

Is this issue natural to a trend-following ecology initialised on a specific trend? This is possible. And if that's the case, it is nice because it means we truly have somethign that works.

# Todo-ongoing

- [WFF] Short selling needs to be handled in some way (loans, margin)

# To watch
- non negative cash for asset purchases is now implemented, but say vigilant 
- list_ed_func looks fixed now
- fixed supply of assets is now enforced
- LEAP updated to 0.6.0, no issues to report after corrections

# Notes


# Current testing state

- Dividend, interest rate, wealth updates behave as expected (02.06.21)
- Trading signal, excess demand work well (02.06.21)
- For positive ED, reassignment to assets works well (02.06.21)


## Forthcoming

- Market clearing 2.0 (ESL)
- Redo plots for analysis from df
