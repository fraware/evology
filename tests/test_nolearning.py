#!/usr/bin/env python3
from test_functions import *

print('Testing for 3 agents, 100 periods with 3 repetitions...')
test_nolearning(3, 100, 3)
print('...Succesful!')
print('Testing for 4 agents, 1000 periods with 5 repetitions...')
test_nolearning(5, 1000, 4)
print('...Succesful!')
print('Testing for 10 agents, 20,000 periods with 5 repetitions...')
test_nolearning(5, 20000, 10)
print('...Succesful!')


