#!/usr/bin/env python3
from test_functions import *

# learning_runs(repetitions, time, agents)

print('Testing for 3 agents, 100 periods with 3 repetitions...')
test_nolearning(3, 100, 3)
print('...Succesful!')

print('Testing for 100 agents, 20,000 periods with 5 repetitions...')
test_nolearning(5, 20000, 100)
print('...Succesful!')


