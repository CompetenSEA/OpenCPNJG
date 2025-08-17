#include "bridge.h"

#include <mutex>
#include <unordered_map>

// Internal storage for chart handles.  Each handle maps to the
// original chart path.  No chart data is actually parsed in this
// stub implementation.
namespace {
std::mutex g_mutex;  // protects access to the handle map
std::unordered_map<std::string, std::string> g_charts;
unsigned long g_next_id = 1;
}

// Build an in-memory SENC from the chart at `path`.
// In this simplified bridge we merely store the path and return
// a generated handle.  Thread safe.
std::string build_senc(const std::string &path) {
  std::lock_guard<std::mutex> lock(g_mutex);
  std::string handle = "senc_" + std::to_string(g_next_id++);
  g_charts[handle] = path;
  return handle;
}

// Query features inside `bbox` for the given chart handle.
// This stub returns an empty feature set.  The function is
// thread safe and may be called concurrently with build_senc.
std::vector<Feature> query_features(const std::string &handle,
                                   double minx,
                                   double miny,
                                   double maxx,
                                   double maxy,
                                   double scale) {
  std::lock_guard<std::mutex> lock(g_mutex);
  (void)minx; (void)miny; (void)maxx; (void)maxy; (void)scale;
  // Real implementation would use S57/CM93 logic here.
  if (g_charts.find(handle) == g_charts.end()) {
    return {};
  }
  return {};
}
