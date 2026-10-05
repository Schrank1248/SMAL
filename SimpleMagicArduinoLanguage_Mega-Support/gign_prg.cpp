const Array<Array<Array<Array<int>>>> prg = {{{{2}, {}}, {{2, 0}}}};
const Array<Array<Array<int>>> devices = {{{1}, {2}}};
Array<int> vars = {};
Servo servos[0];
byte servoCount = 0;
Array<string> strings = {};
Array<Array<int>> deviceLib(Array<Array<int>> args) {
  Array<Array<int>> res;
  return {{false}, {}};
}
bool commandLib(Array<int> args) {
  return false;
}
void initLib() {
}
