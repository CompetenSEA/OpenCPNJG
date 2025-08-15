#include "libcharts_api.h"
#include "charts.h"
#include <cstring>

extern "C" {

void charts_load_cell(const char *path) { charts::load_cell(path); }

unsigned char *charts_render_tile_png(double minx, double miny, double maxx,
                                      double maxy, int z, const char *palette,
                                      size_t *out_size) {
  auto data = charts::render_tile_png(minx, miny, maxx, maxy, z,
                                      palette ? palette : "day");
  unsigned char *buf = new unsigned char[data.size()];
  std::memcpy(buf, data.data(), data.size());
  if (out_size)
    *out_size = data.size();
  return buf;
}

unsigned char *charts_render_tile_mvt(double minx, double miny, double maxx,
                                      double maxy, int z, size_t *out_size) {
  auto data = charts::render_tile_mvt(minx, miny, maxx, maxy, z);
  unsigned char *buf = new unsigned char[data.size()];
  std::memcpy(buf, data.data(), data.size());
  if (out_size)
    *out_size = data.size();
  return buf;
}

void charts_free_buffer(unsigned char *buffer) { delete[] buffer; }

}  // extern "C"
