import sys, json

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
  "getPin":8,
  "switchPin":2,
  "freeze":3,
  "asyncDelay":4
}
parameterCount = {
  "log":1,
  "setPin":2,
  "getPin":2,
  "switchPin":1,
  "freeze":1,
  "asyncDelay":2
}
deviceMapping = {
  "InputPin":0,
  "OutputPin":1,
  "Servo":2,
  "AnalogPin":3
}
# // 0: Input-PIN - PIN
# // 1: Output-PIN - PIN
# // 2: Servo - PIN
# // 3: Analog-PIN - PIN

scope = 0

allowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'"+'"'

strings = []
variables = []
vVals = []

scopeBuffer = []
currentBlock = []

result = []

usedAdditionEventCounter = 101

devices = []

usedLibs = []
initLibs = []
libCMD = []
libDEV = []
#libCMDNum = []

servoCount = 0


def loadLib(dat, NAME):
  for e in dat["events"]:
    events[e[0]] = e[1]
  for e in dat["commands"]:
    # libCMD.append("  "+NAME+"::"+e[0]+",\n")
    # libCMDNum.append("  "+str(e[1])+",\n")
    commands[e[0]] = e[1]
  for e in dat["parameterCount"]:
    parameterCount[e[0]] = e[1]
  for e in dat["deviceMapping"]:
    deviceMapping[e[0]] = e[1]


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

def getVal(val, replA = False):
  if (val[0] == "'" or val[0] == '"') and (val[len(val)-1] == "'" or val[len(val)-1] == '"'):
    # String
    strings.append(val[:len(val)-1][1:])
    val = len(strings)-1
  elif not val.isdigit():
    # Variable
    if val in variables:
      val = -(variables.index(val)+1)
    else:
      if not replA and val[0] == "A" and val[1:].isdigit():
        return val
      print("Error in line "+str(line)+": "+val+" was not defined.")
      exit()
  elif val.isdigit():
    val = int(val)
  else:
    print("Error in line "+str(line)+": Unknown Error")
  return val

blockStack = []

for line in range(len(prg)):
  if len(prg[line]) > 0 and prg[line][0] == "@":
    # Ausnahmen
    if prg[line][:4] == "@var":
      vname = ""
      for i in range(len(prg[line][5:])):
        if prg[line][5:][i] == " ":
          variables.append(vname)
          vVals.append(getVal(prg[line][5:][i+1:]))
        vname += prg[line][5:][i]
    if prg[line][:4] == "@use":
      with open(prg[line][5:]+".json", "r") as file:
        data = json.load(file)
      loadLib(data, prg[line][5:])
      usedLibs.append('#include "'+prg[line][5:]+'.h"\n')
      initLibs.append("  "+prg[line][5:]+"::init();\n")
      libCMD.append("  if ("+prg[line][5:]+"::processCommand(args, devices, deviceData, strings) == true) {return true;}\n")
      libDEV.append("  res = "+prg[line][5:]+"::processDevice(args);\n"+"  if (res[0][0] == 1) {return res;}\n")
    if prg[line][:7] == "@device":
      originalLine = prg[line]
      pars = getPars("@abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'"+'"')
      args = []
      for p in pars[1:]:
        args.append(getVal(p))
      try:
        devices.append([[deviceMapping[pars[0]]], args])
        if pars[0] == "Servo":
          servoCount += 1
      except KeyError:
        print("Error in line "+str(line)+": Unknown Device-Name '"+pars[0]+"'")
        exit()

  else:
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
        if len(pars) != 3:
          print("Error in line "+str(line)+": Expected VALUE EXP VALUE which are 3, but got "+str(len(pars))+" things.")
          exit()
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
        #currentBlock.append(parts)

        sBa = ["event"]
        sBa.extend(parts)
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
        currentBlock.append(parts)

# print("RESULT:")
# print("const Array<Array<Array<Array<int>>>> prg = "+str(result).replace("[", "{").replace("]", "}").replace("'", "")+";")
# print("const Array<Array<Array<int>>> devices = "+str(devices).replace("[", "{").replace("]", "}").replace("'", "")+";")
# print("Array<int> vars = "+str(vVals).replace("[", "{").replace("]", "}").replace("'", "")+";")
# print("Servo servos["+str(servoCount)+"];")
# print("byte servoCount = "+str(servoCount)+";")

with open(cmdPars[2], "w") as f:
  f.writelines(usedLibs+[
    "const Array<Array<Array<Array<int>>>> prg = "+str(result).replace("[", "{").replace("]", "}").replace("'", "")+";\n",
    "const Array<Array<Array<int>>> devices = "+str(devices).replace("[", "{").replace("]", "}").replace("'", "")+";\n",
    "Array<int> vars = "+str(vVals).replace("[", "{").replace("]", "}").replace("'", "")+";\n",
    "Servo servos["+str(servoCount)+"];\n",
    "byte servoCount = "+str(servoCount)+";\n",
    "Array<string> strings = "+str(strings).replace("[", "{").replace("]", "}").replace("'", "")+";\n",

    "Array<Array<int>> deviceLib(Array<Array<int>> args) {\n  Array<Array<int>> res;\n"]+libDEV+["  return {{false}, {}};\n}\n",
    "bool commandLib(Array<int> args) {\n"]+libCMD+["  return false;\n}\n",
    "void initLib() {\n"]+initLibs+["}\n",
  ])
