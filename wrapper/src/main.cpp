#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include "emit_ndjson.hpp"
#include "attr_codec.hpp"
#include "bbox.hpp"

struct Args {
    std::string mode;
    std::string src;
    BBox bbox;
    bool has_bbox{false};
    bool full_attrs{false};
    bool gzip{false};
};

static void usage() {
    std::cerr << "usage: ocpn_min <s57|cm93> --src PATH [--bbox minx,miny,maxx,maxy] [--full-attrs] [--gzip]\n";
}

static bool parse_bbox(const std::string& s, BBox& out) {
    std::stringstream ss(s);
    char comma;
    if (ss >> out.minx >> comma >> out.miny >> comma >> out.maxx >> comma >> out.maxy)
        return true;
    return false;
}

static bool parse_args(int argc, char** argv, Args& a) {
    if (argc < 4) return false;
    a.mode = argv[1];
    for (int i = 2; i < argc; ++i) {
        std::string token = argv[i];
        if (token == "--src" && i + 1 < argc) {
            a.src = argv[++i];
        } else if (token == "--bbox" && i + 1 < argc) {
            a.has_bbox = parse_bbox(argv[++i], a.bbox);
        } else if (token == "--full-attrs") {
            a.full_attrs = true;
        } else if (token == "--gzip") {
            a.gzip = true;
        } else {
            return false;
        }
    }
    return !a.mode.empty() && !a.src.empty();
}

int main(int argc, char** argv) {
    Args args;
    if (!parse_args(argc, argv, args)) {
        usage();
        return 10; // bad args
    }

    emit_line("{\"type\":\"Dataset\",\"driver\":\"" + args.mode + "\"}");
    // Placeholder feature emission
    emit_line("{\"type\":\"Feature\",\"id\":\"stub\"}");
    return 0;
}
