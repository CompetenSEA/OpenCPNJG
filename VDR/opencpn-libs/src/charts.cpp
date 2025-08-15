#include "charts.h"

namespace charts {

void load_cell(const std::string& path) { (void)path; }

std::vector<unsigned char> render_tile_png(double minx, double miny,
                                           double maxx, double maxy, int z,
                                           const std::string& palette) {
  (void)minx;
  (void)miny;
  (void)maxx;
  (void)maxy;
  (void)z;
  (void)palette;
  return std::vector<unsigned char>{'P', 'N', 'G'};
}

std::vector<unsigned char> render_tile_mvt(double minx, double miny,
                                           double maxx, double maxy, int z) {
  (void)minx;
  (void)miny;
  (void)maxx;
  (void)maxy;
  (void)z;
  return std::vector<unsigned char>{'M', 'V', 'T'};
}

}  // namespace charts
