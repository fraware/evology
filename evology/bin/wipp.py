domain_H = [x for x in range(21, 252*3+1, 21)]
add = [x for x in range(3, 21, 1)][::-1]
for i in range(len(add)):
    domain_H.insert(0, add[i])


