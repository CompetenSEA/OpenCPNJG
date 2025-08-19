#include "ndjson.hpp"
#include <ctime>

static std::string now_iso8601() {
  std::time_t t = std::time(nullptr);
  char buf[32];
  std::strftime(buf, sizeof(buf), "%FT%TZ", std::gmtime(&t));
  return buf;
}

void write_dataset(std::ostream& os, const DatasetInfo& ds) {
  os << "{";
  os << "\"type\":\"Dataset\",";
  os << "\"driver\":\"" << ds.driver << "\",";
  os << "\"dataset\":\"" << ds.dataset << "\",";
  os << "\"bounds\":[0,0,0,0],";
  os << "\"commit\":\"ocpn:stub\",";
  os << "\"time\":\"" << now_iso8601() << "\"";
  os << "}" << '\n';
}

void write_feature(std::ostream& os, const DatasetInfo& ds, const Feature& f) {
  os << "{";
  os << "\"type\":\"Feature\",";
  os << "\"id\":\"" << ds.driver << ":" << ds.dataset << ":RCID=" << f.id << "\",";
  os << "\"geometry\":{\"type\":\"Point\",\"coordinates\":[" << f.lon << "," << f.lat << "]},";
  os << "\"properties\":{\"dataset\":\"" << ds.dataset << "\",\"cell\":\"" << ds.dataset
     << "\",\"objl\":1,\"rcid\":1,\"atts\":[";
  bool first = true;
  for (auto& a : f.atts) {
    if (!first) os << ','; first=false;
    os << "{\"k\":\"" << a.k << "\",\"t\":\"" << a.t << "\",\"v\":\"" << a.v << "\"}";
  }
  os << "]}}" << '\n';
}
