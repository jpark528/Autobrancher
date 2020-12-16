#
#   script.py
#   - Autodebugger for a simple python code using branch coverage
#

import random
import sys

#--------------- INPUTS ---------------#
TARGET_CODE         = sys.argv[1]
TARGET_LINE_BEGIN   = int(sys.argv[2])
TARGET_LINE_END     = int(sys.argv[3])

K = 1

#--------------- REFERENE VARIABLE ---------------#
def isFloat(symbol):
    if "." in symbol:
        x, y = symbol.split(".", 1)
        if x.isdigit() and y.isdigit():
            return True
        return False
    return symbol.isdigit()

def getGlobal(GLOBAL, symbol):
    if isFloat(symbol):
        return float(symbol)
    if symbol.isdigit():
        return int(symbol)
    if symbol in GLOBAL:
        return GLOBAL[symbol]
    return None

#--------------- DATA PARSE ---------------#
lines = []
with open(TARGET_CODE, 'r') as f:
    lines = f.readlines()
    for idx in range(len(lines)):
        lines[idx] = lines[idx].rstrip()
    lines = lines[TARGET_LINE_BEGIN-1:TARGET_LINE_END]

#--------------- CONDITION CLASS ---------------#
class Condition:
    def __init__(self, left, right, operator, parent, child, level):
        self.left = left
        self.right = right
        self.operator = operator
        self.parent = parent
        self.child = child
        self.level = level
    
    def calculate(self, GLOBAL):
        if self.operator == ">":
            return getGlobal(GLOBAL, self.left) > getGlobal(GLOBAL, self.right)
        elif self.operator == ">=":
            return getGlobal(GLOBAL, self.left) >= getGlobal(GLOBAL, self.right)
        elif self.operator == "<":
            return getGlobal(GLOBAL, self.left) < getGlobal(GLOBAL, self.right)
        elif self.operator == "<=":
            return getGlobal(GLOBAL, self.left) <= getGlobal(GLOBAL, self.right)
        elif self.operator == "==":
            return getGlobal(GLOBAL, self.left) == getGlobal(GLOBAL, self.right)
        elif self.operator == "!=":
            return getGlobal(GLOBAL, self.left) != getGlobal(GLOBAL, self.right)
    
    def distance(self, GLOBAL, K):
        if self.operator == ">":
            return getGlobal(GLOBAL, self.right) - getGlobal(GLOBAL, self.left) + K
        elif self.operator == ">=":
            return getGlobal(GLOBAL, self.right) - getGlobal(GLOBAL, self.left) + K
        elif self.operator == "<":
            return getGlobal(GLOBAL, self.left) - getGlobal(GLOBAL, self.right) + K
        elif self.operator == "<=":
            return getGlobal(GLOBAL, self.left) - getGlobal(GLOBAL, self.right) + K
        elif self.operator == "==":
            return abs(getGlobal(GLOBAL, self.left) - getGlobal(GLOBAL, self.right))
        elif self.operator == "!=":
            return -abs(getGlobal(GLOBAL, self.left) - getGlobal(GLOBAL, self.right))
    
    def fitness(self, GLOBAL, appLevel, K):
        if self.operator == None:
            return None
        f = self.distance(GLOBAL, K)
        return appLevel + (1 - 1.001**(-f))
    
    def __str__(self):
        if self.operator == None:
            return "Target"
        return " ".join([self.left, self.operator, self.right]) + " @ " + str(self.level)

#--------------- CREATE A CONDITIONAL TREE ---------------#
conditions = []
root = None
numerals = []
literals = []
target = None
for idx in range(len(lines)):
    line = lines[idx]

    level = (len(line) - len(line.lstrip())) / 4

    if line.lstrip()[:3] != 'if ':
        cond = Condition(None, None, None, None, None, level-1)
        conditions.append(cond)
        target = cond
        continue

    parent = None
    for i in range(idx-1, -1, -1):
        if conditions[i].operator != None and conditions[i].level == level - 1:
            parent = conditions[i]
            break
    statement = line.strip()[3:len(line.strip())-1]
    left, operator, right = statement.split()

    if isFloat(left):
        numerals.append(float(left))
    else:
        literals.append(left)
    if isFloat(right):
        numerals.append(float(right))
    else:
        literals.append(right)

    cond = Condition(left, right, operator, parent, None, int(level))
    if parent != None:
        parent.child = cond
    else:
        root = cond
    conditions.append(cond)

#--------------- TEST ---------------#
def getNeighbors(vars):
    keys = list(vars.keys())
    values = list(vars.values())
    neighbors = [values]
    for idx in range(len(values)):
        len_origin = len(neighbors)
        for jdx in range(len_origin):
            temp1 = neighbors[jdx][:]
            temp2 = neighbors[jdx][:]
            temp1[idx] += 1
            temp2[idx] -= 1
            neighbors.append(temp1)
            neighbors.append(temp2)
    
    dicts = []
    for neighbor in neighbors:
        d = {}
        for idx in range(len(keys)):
            d[keys[idx]] = neighbor[idx]
        dicts.append(d)

    return dicts

# Hill Climbing Algorithm

def fitness(n, K):
    cond = root
    while cond.calculate(n):
        cond = cond.child
        if cond.calculate(n) and cond.child == None:
            return 0
    return cond.fitness(n, target.level - cond.level, K)

def hillClimb(cond, K):
    global literals

    climb = True

    literals = list(set(literals))
    seed = {}
    for literal in literals:
        seed[literal] = random.randint(min(numerals) - 1, max(numerals) + 1)
    while not root.calculate(seed):
        for literal in literals:
            seed[literal] = random.randint(min(numerals) - 1, max(numerals) + 1)

    while climb:
        N = getNeighbors(seed)
        climb = False
        for n in N:
            if fitness(n, K) < fitness(seed, K):
                climb = True
                seed = n 
                break
    
    return seed

found = hillClimb(root, K)

#--------------- PRINT RESULT ---------------#
sorted = list(found.keys())
sorted.sort()

for key in sorted:
    print("%s = %d" % (key, found[key]))