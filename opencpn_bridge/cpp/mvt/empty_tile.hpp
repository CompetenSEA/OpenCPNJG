#pragma once
#include <string>
#include "vtzero/builder.hpp"

namespace ocpnmvt {

inline std::string build_empty_tile() {
  vtzero::tile_builder builder;
  // no layers added -> empty tile
  return builder.serialize();
}

}  // namespace ocpnmvt
