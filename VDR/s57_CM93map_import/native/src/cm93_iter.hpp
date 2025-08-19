#pragma once
#include "types.hpp"
#include <string>

struct ReaderCM93 {
  std::string root;
  int count = 0;
};

ReaderCM93 open_cm93(const std::string& root);
bool cm93_next(ReaderCM93& r, Feature& out);
