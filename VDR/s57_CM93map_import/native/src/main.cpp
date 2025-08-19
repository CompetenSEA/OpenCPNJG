#include <iostream>
#include <string>
#include "iso8211.h"

int main(int argc, char** argv) {
  if (argc > 1 && std::string(argv[1]) == "--probe") {
    if (argc < 3) {
      std::cerr << "--probe requires a file" << std::endl;
      return 1;
    }
    DDFModule module;
    if (!module.Open(argv[2], FALSE)) {
      std::cerr << "open failed" << std::endl;
      return 1;
    }
    std::cout << "fields=" << module.GetFieldCount() << std::endl;
    module.Close();
    return 0;
  }

  std::cout << "Usage: ocpn_min [--probe file]" << std::endl;
  return 0;
}
