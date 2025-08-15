#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "charts.h"
#include <array>

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
  m.doc() = "Python bindings for libcharts";
  m.def("load_cell", &charts::load_cell, "Load a chart cell");
  m.def(
      "generate_tile",
      [](std::array<double, 4> bbox, int z, const std::string& fmt,
         const std::string& palette) {
        if (fmt == "png") {
          auto data = charts::render_tile_png(bbox[0], bbox[1], bbox[2],
                                              bbox[3], z, palette);
          return py::bytes(reinterpret_cast<const char*>(data.data()),
                           data.size());
        } else {
          auto data =
              charts::render_tile_mvt(bbox[0], bbox[1], bbox[2], bbox[3], z);
          return py::bytes(reinterpret_cast<const char*>(data.data()),
                           data.size());
        }
      },
      py::arg("bbox"), py::arg("z"), py::arg("fmt") = "png",
      py::arg("palette") = "day");
}
