#include "charts.h"
#include <cstdint>

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
  static const unsigned char png_data[] = {
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00,
      0x0d, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
      0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89,
      0x00, 0x00, 0x00, 0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63,
      0x60, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0xe5, 0x27, 0xd4, 0x9b,
      0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60,
      0x82};
  return std::vector<unsigned char>(png_data, png_data + sizeof(png_data));
}

namespace {
// helpers for encoding protobuf varints
void writeVarint(std::vector<unsigned char>& buf, uint64_t value) {
  while (value > 0x7F) {
    buf.push_back(static_cast<unsigned char>((value & 0x7F) | 0x80));
    value >>= 7;
  }
  buf.push_back(static_cast<unsigned char>(value));
}

void writeTag(std::vector<unsigned char>& buf, uint32_t field, uint32_t type) {
  writeVarint(buf, (field << 3) | type);
}

void writeBytesField(std::vector<unsigned char>& buf, uint32_t field,
                     const std::vector<unsigned char>& bytes) {
  writeTag(buf, field, 2);
  writeVarint(buf, bytes.size());
  buf.insert(buf.end(), bytes.begin(), bytes.end());
}

void writeStringField(std::vector<unsigned char>& buf, uint32_t field,
                      const std::string& str) {
  writeTag(buf, field, 2);
  writeVarint(buf, str.size());
  buf.insert(buf.end(), str.begin(), str.end());
}
} // namespace

std::vector<unsigned char> render_tile_mvt(double minx, double miny,
                                           double maxx, double maxy, int z,
                                           double safety_contour) {
  (void)minx;
  (void)miny;
  (void)maxx;
  (void)maxy;
  (void)z;

  // For the MVP, create a single sounding feature at tile center with depth 5m
  const double depth = 5.0;
  bool is_shallow = depth < safety_contour;

  // --- Build Feature ---
  std::vector<unsigned char> feature;
  // id = 1
  writeTag(feature, 1, 0);
  writeVarint(feature, 1);

  // tags: key index 0, value index 0
  std::vector<unsigned char> tags;
  writeVarint(tags, 0);
  writeVarint(tags, 0);
  writeBytesField(feature, 2, tags);

  // geometry type = Point (1)
  writeTag(feature, 3, 0);
  writeVarint(feature, 1);

  // geometry commands: MoveTo(2048,2048)
  std::vector<unsigned char> geom;
  const uint32_t move_to = (1 << 3) | 1; // MoveTo, 1 point
  writeVarint(geom, move_to);
  auto zz = [](int32_t v) { return (static_cast<uint32_t>(v) << 1) ^ (v >> 31); };
  writeVarint(geom, zz(2048));
  writeVarint(geom, zz(2048));
  writeBytesField(feature, 4, geom);

  // --- Build Layer ---
  std::vector<unsigned char> layer;
  // name = SOUNDG
  writeStringField(layer, 1, "SOUNDG");
  // features
  writeBytesField(layer, 2, feature);
  // keys
  writeStringField(layer, 3, "isShallow");
  // values
  std::vector<unsigned char> value;
  writeTag(value, 7, 0); // bool_value
  writeVarint(value, is_shallow ? 1 : 0);
  writeBytesField(layer, 4, value);
  // version = 2
  writeTag(layer, 15, 0);
  writeVarint(layer, 2);

  // --- Build Tile ---
  std::vector<unsigned char> tile;
  writeBytesField(tile, 3, layer);
  return tile;
}

}  // namespace charts
