"""
 ## Market block 
 
The market folder contains the market functions.
1) Initialise market
2) Apply interest, dividends and reinvestment
3) Update wealth and profit
-) Compute excess demand functions
-) Market clearing algorithm
-) Apply excess demand 
-) Market parameters?

 ## Strategy block
A) Compute trading signal Phi


## Testing block
A testing folder that has a script for every script in the code, to test it 
does work well and normally.



 ## Learning block 
Organised in different cases depending on the learning algorithm we use.
- No learning - Maarten's model
- Genetic Programming (DEAP)
- Genetic algorithm (3 types, parametric evolution)
 

## Experiment block
The experiment folder contains folder experiments, one for each.
An experiment uses a market parameter, a learning parameter, a script.
Data and figures should be saved in separate folders for each experiment.




#### Next tasks

DEAP is constraining our job for the EAs. Why? Because of GP.
Should we start coding for the most constraining thing first? So that we can 
then have a structure as generalised as possible.

"""





"""

0) Initialisation of market, initialisation of population. 
## Requires a first wealth comput.
1) Compute TS
2) Compute ED
3) Market clearing
4) Apply ED
5) Apply dividends, interest rate, reinvestment
6) compute wealth, profits
## 7) hypermutate (initialise fitness as 0 to not impact evolution) LOC TBC ##
8) Evolution block
    a. Fitness
    b. Adaptation

"""