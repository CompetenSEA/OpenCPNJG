#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>

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

