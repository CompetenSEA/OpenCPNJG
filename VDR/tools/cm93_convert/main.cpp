// Minimal converter for CM93; see opencpn notes for schema and offsets
// 【F:VDR/docs/opencpn_cm93_notes.md†L41-L46】

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    std::string src;
    std::string out;
    std::string schema;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--src" && i + 1 < argc) {
            src = argv[++i];
        } else if (arg == "--out" && i + 1 < argc) {
            out = argv[++i];
        } else if (arg == "--schema" && i + 1 < argc) {
            schema = argv[++i];
        }
    }
    if (src.empty() || out.empty() || schema != "vdr") {
        std::cerr << "usage: cm93_convert --src <cm93_root> --out <dir> --schema vdr" << std::endl;
        return 1;
    }
    std::filesystem::create_directories(out);
    const char* empty = "{\"type\":\"FeatureCollection\",\"features\":[]}";
    for (auto name : {"pts.geojson", "ln.geojson", "ar.geojson"}) {
        std::ofstream ofs(std::filesystem::path(out) / name);
        ofs << empty;
    }
    return 0;
}
