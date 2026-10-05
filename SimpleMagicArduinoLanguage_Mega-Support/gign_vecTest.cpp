#include <iostream>
#include "AVector.h"

int main() {
  std::cout << "Hello World!\n";

  Array<Array<int>> L = {{1, 2}, 3};

  std::cout << L[0][1] << std::endl;

  return 0;
}
