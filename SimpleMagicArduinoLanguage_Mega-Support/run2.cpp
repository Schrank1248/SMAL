//
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

Array<Array<unsigned long>> cooldowns = {};

int getValue(int v) {
  if (v<0) {
    return vars[(0-v)-1];
  }
  return v;
}

void execCMD(Array<int> cmd) {
  if (cmd[0] == 0) {
    // log
    Serial.println(getValue(cmd[1]));
  }
  if (cmd[0] == 1) {
    // setPin
    if (devices[getValue(cmd[1])][0][0] == 1) {
      deviceData[getValue(cmd[1])][0] = getValue(cmd[2]);
      digitalWrite(devices[getValue(cmd[1])][1][0], getValue(cmd[2]));
    }
  }
  if (cmd[0] == 2) {
    // switchPin
    if (devices[getValue(cmd[1])][0][0] == 1) {
      deviceData[getValue(cmd[1])][0] = 1-deviceData[getValue(cmd[1])][0];
      digitalWrite(devices[getValue(cmd[1])][1][0], deviceData[getValue(cmd[1])][0]);
    }
  }
  if (cmd[0] == 3) {
    // freeze
    delay(getValue(cmd[1]));
  }
  if (cmd[0] == 4) {
    // asyncDelay
    cooldowns.push_back({getValue(cmd[1])+millis(), getValue(cmd[2])});
  }
  if (cmd[0] == 5) {
    // setServo
    servos[deviceData[getValue(cmd[1])][0]].write(getValue(cmd[2]));
  }
  if (cmd[0] == 6) {
    // setServo
    if (getValue(cmd[2]) == 0) {
      //Serial.println(getValue(cmd[1]));
      if (getValue(cmd[1]) == getValue(cmd[3])) {
        trigger(getValue(cmd[4]), {});
      }
    }
    if (getValue(cmd[2]) == 1) {
      //Serial.println(getValue(cmd[1]));
      if (getValue(cmd[1]) >= getValue(cmd[3])) {
        trigger(getValue(cmd[4]), {});
      }
    }
    if (getValue(cmd[2]) == 2) {
      //Serial.println(getValue(cmd[1]));
      if (getValue(cmd[1]) <= getValue(cmd[3])) {
        trigger(getValue(cmd[4]), {});
      }
    }
    if (getValue(cmd[2]) == 3) {
      //Serial.println(getValue(cmd[1]));
      if (getValue(cmd[1]) > getValue(cmd[3])) {
        trigger(getValue(cmd[4]), {});
      }
    }
    if (getValue(cmd[2]) == 4) {
      //Serial.println(getValue(cmd[1]));
      if (getValue(cmd[1]) < getValue(cmd[3])) {
        trigger(getValue(cmd[4]), {});
      }
    }
  }
  if (cmd[0] == 7) {
    // setPinAnalog
    if (devices[getValue(cmd[1])][0][0] == 1) {
      analogWrite(devices[getValue(cmd[1])][1][0], getValue(cmd[2]));
    }
  }
  if (cmd[0] == 8) {
    // getPin
    int var = cmd[2];
    if (devices[getValue(cmd[1])][0][0] == 0 && var<0) {
      vars[(0-var)-1] = !digitalRead(devices[getValue(cmd[1])][1][0]);
    }
  }
  if (cmd[0] == 9) {
    // getPinAnalog
    int var = cmd[2];
    if (devices[getValue(cmd[1])][0][0] == 3 && var<0) {
      vars[(0-var)-1] = analogRead(devices[getValue(cmd[1])][1][0]);
    }
  }
}

void execute(Array<Array<int>> plist) {
  for (int j = 0; j < plist.size(); j++) {
    if (commandLib(plist[j])) {
      return;
    }
    execCMD(plist[j]);
  }
}

void trigger(int event, Array<int> params) {
  for (int i = 0; i < prg.size(); i++) {
    if (prg[i][0][0][0] == event && prg[i][0][1] == params) {
      execute(prg[i][1]);
    }
  }
}

void setup() {
  Serial.begin(9600);

  initLib();

  for (int i = 0; i < devices.size(); i++) {
    Array<Array<int>> devres = deviceLib(devices[i]);
    if (devres[0][0] == true) {
      deviceData.push_back(devres[1]);
      break;
    }
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

  Array<Array<unsigned long>> nCool = {};
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
