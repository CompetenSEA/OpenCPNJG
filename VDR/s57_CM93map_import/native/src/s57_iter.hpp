#pragma once
#include "types.hpp"
#include <string>

struct ReaderS57 {
  std::string src;
  int count = 0;
};

ReaderS57 open_s57(const std::string& src);
bool s57_next(ReaderS57& r, Feature& out);
