import sys

cmdPars = sys.argv

prg = []

with open(cmdPars[1]) as f:
  prg = f.readlines()

for i in range(len(prg)):
  prg[i] = prg[i][:-1]

prg.append("")

# // Number-Command-Mapping
# // Minuszahlen: Variablen
# // 0: log - LOG
# // 1: setPin - Device-Number, value
# // 2: switchPin - Device-Number
# // 3: freeze - TIME
# // 4: asyncDelay - TIME, EVENT
#
# // Events:
# // 0: init
# // 1: Frame
# // 2: Secondary Update
# // 3: onPressed, Button-Number
# // 4: onReleased, Button-Number


events = {
  "init":0,
  "frameUpdate":1,
  "secondUpdate":2,
  "onPressed":3,
  "onReleased":4
}
commands = {
  "log":0,
  "setPin":1,
  "switchPin":2,
  "freeze":3,
  "asyncDelay":4
}
parameterCount = {
  "log":1,
  "setPin":2,
  "switchPin":1,
  "freeze":1,
  "asyncDelay":2
}

scope = 0

allowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'"+'"'

strings = []
variables = ["par2", "par3"]

scopeBuffer = []
currentBlock = []

result = []

usedAdditionEventCounter = 101


def getPars(allowedC):
  global originalLine
  parts = []
  pa = ""
  state = 0
  for c in range(len(originalLine)):
    if state == 0:
      if originalLine[c] == "(":
        state = 1
    elif state == 1:
      if originalLine[c] in allowedC:
        pa += originalLine[c]
      elif originalLine[c] == " ":
        parts.append(pa)
        pa = ""
      elif originalLine[c] == ")":
        if pa != "":
          parts.append(pa)
        pa = ""
        state = 2
      else:
        print("Error in line "+str(line)+": Expected CHAR or SPACE or RIGHT_BRACKET, but got '"+originalLine[c]+"'")
        exit()
    elif state == 2:
      print("Error in line "+str(line)+": Expected END_OF_LINE, but got '"+originalLine[c]+"'")
      exit()
  return parts

def getVal(val):
  print("getVal() -->", val)
  if (val[0] == "'" or val[0] == '"') and (val[len(val)-1] == "'" or val[len(val)-1] == '"'):
    # String
    strings.append(val[:len(val)-1][1:])
    val = len(strings)-1
  elif not val.isdigit():
    # Variable
    if val in variables:
      val = -(variables.index(val)+1)
    else:
      print("Error in line "+str(line)+": "+val+" was not defined.")
      exit()
  elif val.isdigit():
    val = int(val)
  else:
    print("Error in line "+str(line)+": Unknown Error")
  return val

blockStack = []

for line in range(len(prg)):
  print("???", scopeBuffer)
  lineScope = 0
  for j in range(len(prg[line])):
    if prg[line][j] == " ":
      lineScope += 1
    else:
      break
  lineScope //= 2

  if lineScope <= scope:
    # print(scope-lineScope)
    # print(scopeBuffer)
    # print(scopeBuffer[:len(scopeBuffer)-(scope-lineScope)])
    for i in range(scope-lineScope):
      if scopeBuffer[len(scopeBuffer)-1][0] == "if":
        result.append([[[scopeBuffer[len(scopeBuffer)-1][1]], []], currentBlock])
        currentBlock = blockStack[-1]
        del blockStack[-1]
      if scopeBuffer[len(scopeBuffer)-1][0] == "event":
        result.append([[[scopeBuffer[len(scopeBuffer)-1][1]], scopeBuffer[len(scopeBuffer)-1][2:]], currentBlock])
        currentBlock = []
      scopeBuffer = scopeBuffer[:len(scopeBuffer)-1]
    scope = lineScope
    print("Parsing:", prg[line])
    originalLine = prg[line]
    l = ""
    for c in prg[line]:
      if c!=" ":
        l+=c
    prg[line] = l
    if prg[line] == "":
      pass
    elif prg[line][:2] == "if":
      if len(scopeBuffer) == 0:
        print("Error in line "+str(line)+": Regular code is only allowed in Events.")
        exit()
      pars = getPars("<>=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'"+'"')
      print("if ==>", pars)
      if len(pars) != 3:
        print("Error in line "+str(line)+": Expected VALUE EXP VALUE which are 3, but got "+str(len(pars))+" things.")
        exit()
      print("Calling getVal(", pars[0], ")")
      print("if ==>", getVal(pars[2]))
      exp = 0
      match pars[1]:
        case "==":
          exp = 0
        case ">=":
          exp = 1
        case "<=":
          exp = 2
        case ">":
          exp = 3
        case "<":
          exp = 4
      scope += 1
      scopeBuffer.append(["if", usedAdditionEventCounter])
      currentBlock.append([6, getVal(pars[0]), exp, getVal(pars[2]), usedAdditionEventCounter])
      usedAdditionEventCounter += 1
      blockStack.append(currentBlock)
      currentBlock = []
    elif prg[line][:3] == "for":
      if len(scopeBuffer) == 0:
        print("Error in line "+str(line)+": Regular code is only allowed in Events.")
        exit()
      pass # for
    elif prg[line][:5] == "while":
      if len(scopeBuffer) == 0:
        print("Error in line "+str(line)+": Regular code is only allowed in Events.")
        exit()
      pass # while
    elif prg[line][:5] == "event":
      # event
      scope += 1
      if len(scopeBuffer) > 0:
        print("Error in line "+str(line)+": Event declaration is only allowed in main Scope.")
        exit()

      parts = []
      pa = ""
      state = 0
      for c in range(len(prg[line])):
        if state == 0:
          if prg[line][c] == "(":
            state = 1
        elif state == 1:
          if prg[line][c] in allowedChars:
            pa += prg[line][c]
          elif prg[line][c] == ",":
            parts.append(pa)
            pa = ""
          elif prg[line][c] == ")":
            if pa != "":
              parts.append(pa)
            pa = ""
            state = 2
          else:
            print("Error in line "+str(line)+": Expected CHAR or COMMA or RIGHT_BRACKET, but got '"+prg[line][c]+"'")
            exit()
        elif state == 2:
          print("Error in line "+str(line)+": Expected END_OF_LINE, but got '"+prg[line][c]+"'")
          exit()
      print("E ===>", parts)
      for i in range(len(parts)):
        if i == 0:
          try:
            parts[i] = events[parts[i]]
          except KeyError:
            print("Error in line "+str(line)+": unknown Event '"+parts[i]+"'")
            exit()
        elif (parts[i][0] == "'" or parts[i][0] == '"') and (parts[i][len(parts[i])-1] == "'" or parts[i][len(parts[i])-1] == '"'):
          # String
          strings.append(parts[i][:len(parts[i])-1][1:])
          parts[i] = len(strings)-1
        elif not parts[i].isdigit():
          # Variable
          if parts[i] in variables:
            parts[i] = -(variables.index(parts[i])+1)
          else:
            print("Error in line "+str(line)+": "+parts[i]+" was not defined.")
            exit()
        elif parts[i].isdigit():
          parts[i] = int(parts[i])
        else:
          print("Error in line "+str(line)+": Unknown Error")
      print("EVENT -->", parts)
      #currentBlock.append(parts)

      sBa = ["event"]
      sBa.extend(parts)
      print("!!!!___!!!!", sBa)
      scopeBuffer.append(sBa)
    else:
      if len(scopeBuffer) == 0:
        print("Error in line "+str(line)+": Regular code is only allowed in Events.")
        exit()
      parts = []
      pa = ""
      state = 0
      for c in range(len(prg[line])):
        if state == 0:
          if prg[line][c] in allowedChars:
            pa += prg[line][c]
          elif prg[line][c] == "(":
            parts.append(pa)
            pa = ""
            state = 1
          else:
            print("Error in line "+str(line)+": Expected CHAR or LEFT_BRACKET, but got '"+prg[line][c]+"'")
            exit()
        elif state == 1:
          if prg[line][c] in allowedChars:
            pa += prg[line][c]
          elif prg[line][c] == ",":
            parts.append(pa)
            pa = ""
          elif prg[line][c] == ")":
            if pa != "":
              parts.append(pa)
            pa = ""
            state = 2
          else:
            print("Error in line "+str(line)+": Expected CHAR or COMMA or RIGHT_BRACKET, but got '"+prg[line][c]+"'")
            exit()
        elif state == 2:
          print("Error in line "+str(line)+": Expected END_OF_LINE, but got '"+prg[line][c]+"'")
          exit()
      print("===>", parts)
      for i in range(len(parts)):
        if i == 0:
          try:
            if len(parts)-1 > parameterCount[parts[i]]:
              print("Error in line "+str(line)+": Too many Parameters for '"+parts[i]+"'")
              exit()
            if len(parts)-1 < parameterCount[parts[i]]:
              print("Error in line "+str(line)+": Too few Parameters for '"+parts[i]+"'")
              exit()
            parts[i] = commands[parts[i]]
          except KeyError:
            print("Error in line "+str(line)+": unknown Command '"+parts[i]+"'")
            exit()
        elif (parts[i][0] == "'" or parts[i][0] == '"') and (parts[i][len(parts[i])-1] == "'" or parts[i][len(parts[i])-1] == '"'):
          # String
          strings.append(parts[i][:len(parts[i])-1][1:])
          parts[i] = len(strings)-1
        elif not parts[i].isdigit():
          # Variable
          if parts[i] in variables:
            parts[i] = -(variables.index(parts[i])+1)
          else:
            print("Error in line "+str(line)+": "+parts[i]+" was not defined.")
            exit()
        elif parts[i].isdigit():
          parts[i] = int(parts[i])
        else:
          print("Error in line "+str(line)+": Unknown Error")
      print("-->", parts)
      currentBlock.append(parts)

print("RESULT:", str(result).replace("[", "{").replace("]", "}"))
