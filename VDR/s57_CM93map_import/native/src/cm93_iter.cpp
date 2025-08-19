#include "cm93_iter.hpp"
#include <filesystem>

namespace fs = std::filesystem;

ReaderCM93 open_cm93(const std::string& root) {
  if (!fs::exists(root)) throw std::runtime_error("cm93 root missing");
  return ReaderCM93{root,0};
}

bool cm93_next(ReaderCM93& r, Feature& out) {
  if (r.count >= 2) return false;
  out.id = std::to_string(r.count+1);
  out.lon = -60.0 + r.count;
  out.lat = 50.0 + r.count;
  out.atts.clear();
  r.count++;
  return true;
}
