#include <Arduino.h>
#include "AVector.h"
#include <string>
#include <LiquidCrystal_I2C.h>

namespace testLib {
  Array<LiquidCrystal_I2C*> LCDs = {};

  void init() {
    Serial.println("INITTTT");
  }
  bool processCommand(Array<int> cmd, const Array<Array<Array<int>>> devices, Array<Array<int>> deviceData, Array<std::string> strings) {
    if (cmd[0] == 15) {
      // Hello
      LCDs[deviceData[cmd[1]][0]]->init();
      LCDs[deviceData[cmd[1]][0]]->clear();
      LCDs[deviceData[cmd[1]][0]]->backlight();
      LCDs[deviceData[cmd[1]][0]]->print("Hello World!");
      return true;
    }
    if (cmd[0] == 16) {
      // Init
      LCDs[deviceData[cmd[1]][0]]->init();
      LCDs[deviceData[cmd[1]][0]]->clear();
      LCDs[deviceData[cmd[1]][0]]->backlight();
      return true;
    }
    if (cmd[0] == 15) {
      // Print
      LCDs[deviceData[cmd[1]][0]]->print("Hello World!");
      return true;
    }
    return false;
  }
  Array<Array<int>> processDevice(Array<Array<int>> dev) {
    if (dev[0][0] == 10) {
      Serial.println("LCD INIT!");
      LCDs.push_back(new LiquidCrystal_I2C(0x27, 16, 2));
      return {{true}, {LCDs.size()-1}};
    }
    return {{false}, {}};
  }
}
