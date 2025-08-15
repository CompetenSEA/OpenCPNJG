#pragma once
#include <string>
#include <vector>

namespace charts {
void load_cell(const std::string& path);
std::vector<unsigned char> render_tile_png(double minx, double miny,
                                           double maxx, double maxy, int z,
                                           const std::string& palette = "day");
std::vector<unsigned char> render_tile_mvt(double minx, double miny,
                                           double maxx, double maxy, int z);
}  // namespace charts
