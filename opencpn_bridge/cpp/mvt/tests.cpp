#include "bridge.h"
#include <zlib.h>
#include <cstdint>
#include <cassert>

uint32_t crc32_of(const std::string &data) {
  return ::crc32(0L, reinterpret_cast<const Bytef*>(data.data()), data.size());
}

int main() {
  auto handle = build_senc("/path/chart.000");
  auto gz = query_tile_mvt(handle, 0, 0, 0);
  assert(gz.size() < 2048u);
  uint32_t hash = crc32_of(gz);
  assert(hash == 2836143055u);
  return 0;
}
