#include "bridge.h"
#include "mvt/empty_tile.hpp"

#include <mutex>
#include <unordered_map>
#include <zlib.h>
#include <cstring>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>


namespace {
std::mutex g_mutex;  // protects access to the handle map
std::unordered_map<std::string, std::string> g_charts;
unsigned long g_next_id = 1;

std::string gzip_compress(const std::string &input) {
  z_stream zs;
  std::memset(&zs, 0, sizeof(zs));
  if (deflateInit2(&zs, Z_BEST_COMPRESSION, Z_DEFLATED, 15 + 16, 8,
                   Z_DEFAULT_STRATEGY) != Z_OK) {
    return {};
  }
  gz_header header;
  std::memset(&header, 0, sizeof(header));
  header.os = 255;  // unknown
  deflateSetHeader(&zs, &header);
  zs.next_in = reinterpret_cast<Bytef *>(const_cast<char *>(input.data()));
  zs.avail_in = static_cast<uInt>(input.size());

  std::string out;
  out.resize(128);
  int ret;
  do {
    if (zs.total_out >= out.size()) {
      out.resize(out.size() * 2);
    }
    zs.next_out = reinterpret_cast<Bytef *>(&out[zs.total_out]);
    zs.avail_out = static_cast<uInt>(out.size() - zs.total_out);
    ret = deflate(&zs, Z_FINISH);
  } while (ret == Z_OK);
  deflateEnd(&zs);
  if (ret != Z_STREAM_END) {
    return {};
  }
  out.resize(zs.total_out);
  return out;
}
}  // namespace

std::string build_senc(const std::string &path) {
  std::lock_guard<std::mutex> lock(g_mutex);
  std::string handle = "senc_" + std::to_string(g_next_id++);
  g_charts[handle] = path;
  return handle;
}

std::vector<Feature> query_features(const std::string &handle,
                                   double minx,
                                   double miny,
                                   double maxx,
                                   double maxy,
                                   double scale) {
  std::lock_guard<std::mutex> lock(g_mutex);
  (void)minx;
  (void)miny;
  (void)maxx;
  (void)maxy;
  (void)scale;
  if (g_charts.find(handle) == g_charts.end()) {
    return {};
  }
  return {};
}

std::string query_tile_mvt(const std::string &handle, int z, int x, int y) {
  std::lock_guard<std::mutex> lock(g_mutex);
  (void)z;
  (void)x;
  (void)y;
  if (g_charts.find(handle) == g_charts.end()) {
    return {};
  }
  auto tile = ocpnmvt::build_empty_tile();
  return gzip_compress(tile);
}
=======

// Declarations of the stub functions located in stub/.
std::string build_senc(const std::string &chart_path,
                       const std::string &output_dir);
std::string query_tile_mvt(const std::string &senc_root,
                           int z, int x, int y);

namespace py = pybind11;

PYBIND11_MODULE(opencpn_bridge, m) {
  m.doc() = "Python bindings for the OpenCPN stub bridge";

  m.def("build_senc", &build_senc, py::arg("chart_path"),
        py::arg("output_dir"),
        "Build a stub SENC and write a dummy provenance.json, returning the output path");

  m.def(
      "query_tile_mvt",
      [](const std::string &senc_root, int z, int x, int y) {
        auto data = query_tile_mvt(senc_root, z, x, y);
        return py::bytes(data);
      },
      py::arg("senc_root"), py::arg("z"), py::arg("x"), py::arg("y"),
      "Return an empty Mapbox Vector Tile for the requested coordinates");
}
