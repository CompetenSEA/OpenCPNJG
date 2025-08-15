#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/attr.h>
#include "libcharts_api.h"
#include <array>

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
  m.doc() = "Python bindings for libcharts";
  m.def(
      "load_cell",
      [](const std::string &path) { charts_load_cell(path.c_str()); },
      "Load a chart cell");
  m.def(
      "generate_tile",
      [](std::array<double, 4> bbox, int z, py::dict options) {
        std::string fmt = "png";
        std::string palette = "day";
        double safety = 0.0;
        if (options.contains("format"))
          fmt = py::cast<std::string>(options["format"]);
        if (options.contains("palette"))
          palette = py::cast<std::string>(options["palette"]);
        if (options.contains("safetyContour"))
          safety = py::cast<double>(options["safetyContour"]);

        if (fmt != "png" && fmt != "mvt")
          throw std::invalid_argument("format must be 'png' or 'mvt'");
        if (palette != "day" && palette != "dusk" && palette != "night")
          throw std::invalid_argument(
              "palette must be 'day', 'dusk', or 'night'");
        (void)safety;  // currently unused

        size_t size = 0;
        unsigned char *buf = nullptr;
        if (fmt == "png") {
          buf = charts_render_tile_png(bbox[0], bbox[1], bbox[2], bbox[3], z,
                                       palette.c_str(), &size);
        } else {
          buf = charts_render_tile_mvt(bbox[0], bbox[1], bbox[2], bbox[3], z,
                                       &size);
        }
        py::bytes result(reinterpret_cast<const char *>(buf), size);
        charts_free_buffer(buf);
        return result;
      },
      py::arg("bbox"), py::arg("z"), py::arg("options") = py::dict());
}
