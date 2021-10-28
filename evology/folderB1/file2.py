import os
def tree_printer(root):
    for root, dirs, files in os.walk(root):
        for d in dirs:
            print os.path.join(root, d)    
        for f in files:
            print os.path.join(root, f)
tree_printer('.')


import sys
print(sys.path)
sys.path.append("evology/folderA1")

print(sys.path)

import file1


def double_add(x,y):
    return file1.add(x,y) * file1.add(x,y)

print(double_add(3,3))

import sys
print(sys.path)
sys.path.append("evology")
print(sys.path)

from folderA1 import file1


def double_add(x,y):
    return file1.add(x,y) * file1.add(x,y)

print(double_add(3,3))
