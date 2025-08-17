#pragma once
#include <string>
#include <vector>

// Simple feature representation returned by query_features.
struct Feature {
  std::string id;  // arbitrary identifier
  double x;        // longitude
  double y;        // latitude
};

// Build an in-memory SENC from the chart at `path`.
// `chart_type` may be "s57" or "cm93" and is used to select the
// appropriate ingestion path.  The returned string is an opaque
// handle identifying the loaded chart.
// The caller owns the returned handle and should keep it until
// all queries are finished. Handles are released automatically
// when the process exits.
std::string build_senc(const std::string &path,
                       const std::string &chart_type);

// Query features from the chart identified by `handle` intersecting
// the bounding box.  `scale` is the desired display scale.
// Thread safe: internal state is protected by a mutex.
std::vector<Feature> query_features(const std::string &handle,
                                   double minx,
                                   double miny,
                                   double maxx,
                                   double maxy,
                                   double scale);
