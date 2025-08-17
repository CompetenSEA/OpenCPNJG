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
// Returns a string handle identifying the loaded chart.
// The caller owns the returned handle and should keep it until
// all queries are finished. Handles are released automatically
// when the process exits.
std::string build_senc(const std::string &path);

// Query features from the chart identified by `handle` intersecting
// the bounding box.  `scale` is the desired display scale.
// Thread safe: internal state is protected by a mutex.
std::vector<Feature> query_features(const std::string &handle,
                                   double minx,
                                   double miny,
                                   double maxx,
                                   double maxy,
                                   double scale);

// Produce a Mapbox Vector Tile for the given z/x/y using vtzero.
// The tile is gzip-compressed and may be empty if the handle is unknown.
std::string query_tile_mvt(const std::string &handle,
                           int z,
                           int x,
                           int y);
