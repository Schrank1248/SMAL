// Input/Output Definition and Execution (IODE) by David Cuntz 2026
#include "vector"
#include "string"
#include <Servo.h>

using namespace std;

// Number-Command-Mapping
// Minuszahlen: Variablen
// 0: log - LOG
// 1: setPin - Device-Number, value
// 2: switchPin - Device-Number
// 3: freeze - TIME
// 4: asyncDelay - TIME, EVENT
// 5: setServo - Device-Number, value
// 6: if - value1, Vergleichs-Art, value2, Event
// 7: setPinAnalog - Device, value
// 8: getPin - Device, var

// Vergleichs-Arten
// 0: ==
// 1: >=
// 2: <=
// 3: >
// 4: <

// Events:
// 0: init
// 1: Frame
// 2: Secondary Update
// 3: onPressed, Button-Number
// 4: onReleased, Button-Number

// Inputs:
// {Geraete}
// Geraet: {{Type}, {Parameter}}
// Types:
// 0: Input-PIN - PIN
// 1: Output-PIN - PIN
// 2: Servo - PIN
// 3: Analog-PIN - PIN

vector<vector<int>> deviceData = {};

/*
const vector<vector<vector<int>>> devices = {
  {{0}, {7}},
  {{1}, {8}},
  {{1}, {9}}
};
vector<int> vars = {0, 456};
const vector<vector<vector<vector<int>>>> prg = {
  {{{0}, {}}, {
    {0, -1}
  }},
  {{{2}, {}}, {
    {3, 1000}
  }},
  {{{3}, {0}}, {
    {1, 2, 1},
    {4, 5000, 10}
  }},
  {{{10}, {}}, {
    {1, 2, 0}
  }}
};
*/
const vector<vector<vector<int>>> devices = {
  {{3}, {A0}}
};
vector<int> vars = {0, 456};
const vector<vector<vector<vector<int>>>> prg = {
  {{{2}, {}}, {
    {9, 0, -1},
    {0, -1}
  }}
};

Servo servos[1];
byte servoCount = 0;

vector<vector<unsigned long>> cooldowns = {};

int getValue(int v) {
  if (v<0) {
    return vars[(0-v)-1];
  }
  return v;
}

void execute(vector<vector<int>> plist) {
  for (int j = 0; j < plist.size(); j++) {
    if (plist[j][0] == 0) {
      // log
      Serial.println(getValue(plist[j][1]));
    }
    if (plist[j][0] == 1) {
      // setPin
      if (devices[getValue(plist[j][1])][0][0] == 1) {
        deviceData[getValue(plist[j][1])][0] = getValue(plist[j][2]);
        digitalWrite(devices[getValue(plist[j][1])][1][0], getValue(plist[j][2]));
      }
    }
    if (plist[j][0] == 2) {
      // switchPin
      if (devices[getValue(plist[j][1])][0][0] == 1) {
        deviceData[getValue(plist[j][1])][0] = 1-deviceData[getValue(plist[j][1])][0];
        digitalWrite(devices[getValue(plist[j][1])][1][0], deviceData[getValue(plist[j][1])][0]);
      }
    }
    if (plist[j][0] == 3) {
      // freeze
      delay(getValue(plist[j][1]));
    }
    if (plist[j][0] == 4) {
      // asyncDelay
      cooldowns.push_back({getValue(plist[j][1])+millis(), getValue(plist[j][2])});
    }
    if (plist[j][0] == 5) {
      // setServo
      servos[deviceData[getValue(plist[j][1])][0]].write(getValue(plist[j][2]));
    }
    if (plist[j][0] == 6) {
      // setServo
      if (getValue(plist[j][2]) == 0) {
        //Serial.println(getValue(plist[j][1]));
        if (getValue(plist[j][1]) == getValue(plist[j][3])) {
          trigger(getValue(plist[j][4]), {});
        }
      }
      if (getValue(plist[j][2]) == 1) {
        //Serial.println(getValue(plist[j][1]));
        if (getValue(plist[j][1]) >= getValue(plist[j][3])) {
          trigger(getValue(plist[j][4]), {});
        }
      }
      if (getValue(plist[j][2]) == 2) {
        //Serial.println(getValue(plist[j][1]));
        if (getValue(plist[j][1]) <= getValue(plist[j][3])) {
          trigger(getValue(plist[j][4]), {});
        }
      }
      if (getValue(plist[j][2]) == 3) {
        //Serial.println(getValue(plist[j][1]));
        if (getValue(plist[j][1]) > getValue(plist[j][3])) {
          trigger(getValue(plist[j][4]), {});
        }
      }
      if (getValue(plist[j][2]) == 4) {
        //Serial.println(getValue(plist[j][1]));
        if (getValue(plist[j][1]) < getValue(plist[j][3])) {
          trigger(getValue(plist[j][4]), {});
        }
      }
    }
    if (plist[j][0] == 7) {
      // setPinAnalog
      if (devices[getValue(plist[j][1])][0][0] == 1) {
        analogWrite(devices[getValue(plist[j][1])][1][0], getValue(plist[j][2]));
      }
    }
    if (plist[j][0] == 8) {
      // getPin
      int var = plist[j][2];
      if (devices[getValue(plist[j][1])][0][0] == 0 && var<0) {
        vars[(0-var)-1] = !digitalRead(devices[getValue(plist[j][1])][1][0]);
      }
    }
    if (plist[j][0] == 9) {
      // getPinAnalog
      int var = plist[j][2];
      if (devices[getValue(plist[j][1])][0][0] == 3 && var<0) {
        vars[(0-var)-1] = analogRead(devices[getValue(plist[j][1])][1][0]);
      }
    }
  }
}

void trigger(int event, vector<int> params) {
  for (int i = 0; i < prg.size(); i++) {
    if (prg[i][0][0][0] == event && prg[i][0][1] == params) {
      execute(prg[i][1]);
    }
  }
}

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < devices.size(); i++) {
    if (devices[i][0][0] == 0) {
      // Input-PIN
      deviceData.push_back({1});
      pinMode(devices[i][1][0], INPUT_PULLUP);
    }
    if (devices[i][0][0] == 1) {
      // Output-PIN
      deviceData.push_back({0});
      pinMode(devices[i][1][0], OUTPUT);
      Serial.println("OUT");
    }
    if (devices[i][0][0] == 2) {
      // Servo
      deviceData.push_back({servoCount});
      servos[servoCount].attach(devices[i][1][0]);
      servoCount++;
      Serial.println("OUT");
    }
    if (devices[i][0][0] == 2) {
      // Analog-PIN
    }
  }

  trigger(0, {});
  Serial.println("INIT");
}

unsigned long secCooldown = 0;
unsigned long lasttime = 0;

bool frameUpdateEnabled = true;

void loop() {
  unsigned long time = millis();
  if (frameUpdateEnabled)
    trigger(1, {});
  if (time - secCooldown >= 1000) {
    trigger(2, {});
    secCooldown = millis();
  }

  vector<vector<unsigned long>> nCool = {};
  for (int c = 0; c < cooldowns.size(); c++) {
    if (cooldowns[c][0] <= time) {
      trigger(cooldowns[c][1], {});
    } else {
      nCool.push_back(cooldowns[c]);
    }
  }
  cooldowns = nCool;

  for (int b = 0; b < devices.size(); b++) {
    if (devices[b][0][0] == 0) {
      // Input-PIN
      int state = digitalRead(devices[b][1][0]);
      if (deviceData[b][0] != state) {
        if (state == 0) {
          // pressed
          trigger(3, {b});
        }
        if (state == 1) {
          // released
          trigger(4, {b});
        }
        deviceData[b][0] = state;
      }
    }
  }
  //Serial.println(millis()-time);
}
