#include <fstream>
#include <filesystem>
#include <string>

namespace fs = std::filesystem;

std::string build_senc(const std::string &chart_path, const std::string &output_dir) {
    (void)chart_path; // unused in stub
    fs::create_directories(output_dir);
    std::ofstream(output_dir + "/provenance.json") << "{\"stub\": true}\n";
    return output_dir;
}

std::string query_tile_mvt(const std::string &senc_root, int z, int x, int y) {
    (void)senc_root; (void)z; (void)x; (void)y;
    // Return an empty protobuf tile
    return std::string();
}

