# def GenerateParam(reps, increment):
#     param = []

#     iteration = [x for x in range(0, 101, increment)]
#     print(iteration)
    
#     for i in iteration:
#         start = [i, 0, 100-i]
#         for _ in range(reps):
#             print(start)
#             param.append(start)

#         while start[2] >= increment and start[1] < 100 - increment and sum(start) == 100:
#             start[1] += increment 
#             start[2] -= increment 
#             for _ in range(reps):
#                 print(start)
#                 param.append(start)

#         del start
#     return param

# reps = 2
# increment = 10 #in percent
# param = GenerateParam(reps, increment)
# print(len(param))
# print("param")
# print(param)

# print(param[0])


import ternary
from ternary.helpers import simplex_iterator

# def GenerateCoords(reps, scale):
#     param = []
#     for (i,j,k) in simplex_iterator(scale):
#         for _ in range(reps):
#             param.append([i/scale,j/scale,k/scale])
#     return param

# param = GenerateCoords(1,2)
# print(param)
# print(len(param))

for (i,j,k) in simplex_iterator(50):
    print(i,j,k)