# Current testing state

- Dividend, interest rate, wealth updates behave as expected (02.06.21)
- Trading signal, excess demand work well (02.06.21)
- For positive ED, reassignment to assets works well (02.06.21)

## Todo-ongoing

- [WFF] Short selling needs to be handled in some way (loans, margin)
- Main output must be a workable dataframe // continue adding columns until we can work with df only as output

## Notes

- wealth_earnings was temporarily disabled to facilitate analysis and testing

## Known issues

- Cash updates: as currently price is not handled by price clearing, there is a growing desiquilibrium.
For 5 generations, we get [Theta, 15.0, -12.5, 27.5, 0, 0, 7.5, 0, 0.0]
The price does not change, wealth does not change as the agent keeps going on loans to acquire new assets. 
The trading signal and the excess demand do not change either.

- Cash goes in the negatives, need a nonngeativity constraint

## Forthcoming

- Market clearing 2.0 (ESL)
