#!/usr/bin/env python3
from test_functions import *

# learning_runs(repetitions, time, agents)

print('Testing for 3 agents, 253 periods with 3 repetitions...')
test_learning(3, 253, 3)
print('...Succesful!')

print('Testing for 3 agents, 253 periods with 3 repetitions and resetW True...')
test_learning_reset(3, 253, 3)
print('...Succesful!')

print('Testing for 100 agents, 20,000 periods with 5 repetitions...')
test_learning(5, 20000, 100)
print('...Succesful!')



