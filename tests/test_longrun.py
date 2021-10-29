#!/usr/bin/env python3
from test_functions import *

print('Long run - No learning')

print('Testing for NL - 100 agents, 50,000 periods with 5 repetitions...')
test_nolearning(5, 50000, 100)
print('...Succesful!')
print('Testing for NL - 100 agents, 100,000 periods with 3 repetitions...')
test_nolearning(3, 100000, 100)
print('...Succesful!')

print('------------')
print('Long run - Learning')

print('Testing for L - 100 agents, 50,000 periods with 5 repetitions...')
test_learning(5, 50000, 100)
print('...Succesful!')
print('Testing for L - 100 agents, 100,000 periods with 3 repetitions...')
test_learning(3, 100000, 100)
print('...Succesful!')