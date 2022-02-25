domain_f = [x / 10.0 for x in range(1, 41, 2)]
domain_H = [x for x in range(21, 252, 21*3)]
def GenerateParam(reps):
    param = []
    for i in range(len(domain_f)):
        for j in range(len(domain_H)):
            for _ in range(reps):
                config = [domain_f[i], domain_H[j]]
                param.append(config)
    return param
reps = 5
param = GenerateParam(reps)
print(len(param))