domain_f = [x / 100.0 for x in range(1, 41, 5)]
domain_H = [x for x in range(21, 252*3+1, 21)]
add = [x for x in range(2, 21, 1)][::-1]
for i in range(len(add)):
    domain_H.insert(0, add[i])

def GenerateParam(reps):
    param = []
    for i in range(len(domain_f)):
        for j in range(len(domain_H)):
            for _ in range(reps):
                config = [domain_f[i], domain_H[j]]
                param.append(config)
    return param
reps = 15
param = GenerateParam(reps)
print(len(param))