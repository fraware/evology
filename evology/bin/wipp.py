domain_f = [x / 10.0 for x in range(1, 41, 1)]
add = [x / 20.0 for x in range(21, 41, 2)]
for i in range(len(add)):
    domain_f.append(add[i])

domain_H = [x for x in range(21, 252*2+1, 21)]
add = [x for x in range(2, 21, 2)][::-1]
for i in range(len(add)):
    domain_H.insert(0, add[i])
add = [x for x in range(252*2, 252*3+1, 21*3)]
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
reps = 10
param = GenerateParam(reps)
print(len(param))

print(domain_f)
print(domain_H)
print([len(domain_f), len(domain_H)])