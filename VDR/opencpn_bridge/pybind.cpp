#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "bridge.h"

namespace py = pybind11;

PYBIND11_MODULE(opencpn_bridge, m) {
  m.doc() = "Minimal OpenCPN chart bridge";
  m.def("build_senc", &build_senc, py::arg("path"),
        "Load a chart and build an in-memory SENC, returning a handle");

  m.def(
      "query_features",
      [](const std::string &handle, std::tuple<double, double, double, double> bbox,
         double scale) {
        auto feats = query_features(handle, std::get<0>(bbox), std::get<1>(bbox),
                                    std::get<2>(bbox), std::get<3>(bbox), scale);
        py::dict out;
        for (const auto &f : feats) {
          py::dict geom;
          geom["x"] = f.x;
          geom["y"] = f.y;
          out[py::str(f.id)] = geom;
        }
        return out;
      },
      py::arg("handle"), py::arg("bbox"), py::arg("scale"),
      "Query chart features intersecting the bounding box");
}
