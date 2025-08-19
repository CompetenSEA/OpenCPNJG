#pragma once
#include <string>
#include <vector>

struct Attr {
  std::string k;
  std::string t;
  std::string v;
};

struct Feature {
  std::string id;
  double lon;
  double lat;
  std::vector<Attr> atts;
};

struct DatasetInfo {
  std::string driver;
  std::string dataset;
};
