# Current testing state

- Dividend, interest rate, wealth updates behave as expected (02.06.21)
- Trading signal, excess demand work well (02.06.21)
- For positive ED, reassignment to assets works well (02.06.21)

## Todo-ongoing

- [WFF] Short selling needs to be handled in some way (loans, margin)
- Main output must be a workable dataframe // continue adding columns until we can work with df only as output
- LEAP_EC 0.6 update should be live soon https://pypi.org/project/leap-ec/

## To watch
- non negative cash for asset purchases is now implemented, but say vigilant 

## Notes
- wealth_earnings was temporarily disabled to facilitate analysis and testing

## Known issues

- Price (& wealth) either goes to 0 or to infinity. Very unstable.
- Fixed supply of assets does not seem enforced
- list_ed_func seem to deliver identical functions, while agents with diff trading signals should not have the same

## Forthcoming

- Market clearing 2.0 (ESL)
