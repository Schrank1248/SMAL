import copy

def getLen(L):
  if len(L) == 0:
    return [0]
  if type(L[0]) != list:
    return [len(L)]
  r = []
  for e in L:
    res = getLen(e)
    if len(r) < len(res):
      while len(r) < len(res):
        r.append(0)
    for i in range(len(res)):
      if res[i] > r[i]:
        r[i] = res[i]
  return [len(L)]+r

def getArrayDef(LIST):
  ll = getLen(LIST)
  res = ""
  for i in ll:
    res += "["+str(i)+"]"
  return res

print(getArrayDef([[[[2], []], [[2, 0]]]]))
