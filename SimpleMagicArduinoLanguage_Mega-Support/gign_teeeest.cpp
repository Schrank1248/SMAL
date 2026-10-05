#include "testLib.h"
Array<Array<int>> deviceLib(Array<Array<int>> args) {
  Array<Array<int>> res;
  res = testLib::processDevice(args);
  if (res[0][0] == 1) {return res;}
  return {{false}, {}};
}
bool commandLib(Array<int> args) {
  if (testLib::processCommand(args) == true) {return true;}
  return false;
}
void initLib() {
  testLib::init();
}
const Array<Array<Array<Array<int>>>> prg = {{{{2}, {}}, {{15, 0}}}};
const Array<Array<Array<int>>> devices = {{{1}, {2}}};
Array<int> vars = {};
Servo servos[0];
byte servoCount = 0;
