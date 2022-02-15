# Define the domains 
domain_f = [x / 10.0 for x in range(0, 31, 1)]
domain_H = [x / 1 for x in range(21, 252*3+1, 21)]
domain_H.insert(0, 10)
domain_H.insert(0, 5)
domain_H.insert(0, 2)

def GenerateParam(reps):
    param = []
    for i in range(len(domain_f)):
        for j in range(len(domain_H)):
            for _ in range(reps):
                config = [domain_f[i], domain_H[j]]
                param.append(config)
    return param
param = GenerateParam(1)
print(param)

print(len(param))


domain_f = [x / 10.0 for x in range(0, 31, 10)]
domain_H = [x / 1 for x in range(21, 252*3+1, 210)]
domain_H.insert(0, 10)
domain_H.insert(0, 5)
domain_H.insert(0, 2)
def GenerateParam(reps):
    param = []
    for i in range(len(domain_f)):
        for j in range(len(domain_H)):
            for _ in range(reps):
                config = [domain_f[i], domain_H[j]]
                param.append(config)
    return param
param = GenerateParam(2)
print(len(param))