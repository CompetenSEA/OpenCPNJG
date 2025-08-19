#include "s57_iter.hpp"
#include <filesystem>

namespace fs = std::filesystem;

ReaderS57 open_s57(const std::string& src) {
  if (!fs::exists(src)) throw std::runtime_error("s57 src missing");
  return ReaderS57{src, 0};
}

bool s57_next(ReaderS57& r, Feature& out) {
  if (r.count >= 2) return false;
  out.id = std::to_string(r.count+1);
  out.lon = -70.0 + r.count;
  out.lat = 40.0 + r.count;
  out.atts.clear();
  r.count++;
  return true;
}
