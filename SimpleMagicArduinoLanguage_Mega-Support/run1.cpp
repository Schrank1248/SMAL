// Input/Output Definition and Execution (IODE) by David Cuntz 2026
#include "AVector.h"
#include "string"
#include <Servo.h>
#include "testLib.h"

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
// 9: getPinAnalog - Device, var

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

Array<Array<int>> deviceData = {};

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

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Replace with generated Lists
