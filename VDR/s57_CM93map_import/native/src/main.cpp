#include <filesystem>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cctype>

#include "iso8211.h"

namespace fs = std::filesystem;

static bool file_exists(const fs::path& p) {
  std::error_code ec;
  return fs::exists(p, ec) && fs::is_regular_file(p, ec);
}

static bool dir_exists(const fs::path& p) {
  std::error_code ec;
  return fs::exists(p, ec) && fs::is_directory(p, ec);
}

static int probe_cm93(const std::string& root_in) {
  fs::path root = fs::path(root_in);

  if (!dir_exists(root)) {
    std::cerr << "probe-cm93: not a directory: " << root << "\n";
    return 11; // src invalid
  }

  // CM93 dictionaries usually live at dataset root
  const fs::path dic1 = root / "CM93OBJ.DIC";
  const fs::path dic2 = root / "ATTRLUT.DIC";

  bool has_dic1 = file_exists(dic1);
  bool has_dic2 = file_exists(dic2);

  // If not in root, search one level deep (some dumps place them in a subdir)
  if (!has_dic1 || !has_dic2) {
    for (auto& entry : fs::directory_iterator(root)) {
      if (!dir_exists(entry.path())) continue;
      if (!has_dic1 && file_exists(entry.path() / "CM93OBJ.DIC")) has_dic1 = true;
      if (!has_dic2 && file_exists(entry.path() / "ATTRLUT.DIC")) has_dic2 = true;
    }
  }

  if (!has_dic1 || !has_dic2) {
    std::cerr << "probe-cm93: missing dictionaries (CM93OBJ.DIC / ATTRLUT.DIC)\n";
    // still print a minimal JSON so logs show where we looked
    std::cout << "{"
              << "\"type\":\"CM93Dataset\",\"root\":\"" << root.string() << "\"," 
              << "\"dictionaries\":{\"CM93OBJ.DIC\":" << (has_dic1?"true":"false")
              << ",\"ATTRLUT.DIC\":" << (has_dic2?"true":"false") << "},"
              << "\"ok\":false}"
              << "\n";
    return 11;
  }

  // Count cells by scale tier Z..G under all numeric region folders
  std::unordered_map<std::string, uint64_t> by_scale;
  const char* scales[] = {"Z","A","B","C","D","E","F","G"};
  for (auto s : scales) by_scale[s] = 0;

  uint64_t regions = 0;
  uint64_t total_cells = 0;

  for (auto& region : fs::recursive_directory_iterator(root)) {
    if (!region.is_directory()) continue;

    // Region folders are typically numeric (e.g., 00300000)
    const std::string dirname = region.path().filename().string();
    bool looks_numeric = !dirname.empty() &&
                         std::all_of(dirname.begin(), dirname.end(),
                                     [](unsigned char c){ return std::isdigit(c); });

    if (!looks_numeric) continue;
    ++regions;

    // Inside a region we expect subfolders named Z..G
    for (auto s : scales) {
      fs::path tier = region.path() / s;
      if (!dir_exists(tier)) continue;

      for (auto& f : fs::directory_iterator(tier)) {
        if (!f.is_regular_file()) continue;

        // Filter out obvious non-cell sidecars if present
        const std::string fname = f.path().filename().string();
        if (fname == "CM93OBJ.DIC" || fname == "ATTRLUT.DIC") continue;
        if (fname.size() >= 4) {
          std::string suffix = fname.substr(fname.size() - 4);
          if (suffix == ".DIC" || suffix == ".TXT") continue;
        }

        by_scale[s] += 1;
        total_cells += 1;
      }
    }
  }

  // Emit summary JSON (one line, NDJSON-friendly)
  std::cout << "{"
            << "\"type\":\"CM93Dataset\"," 
            << "\"root\":\"" << root.string() << "\"," 
            << "\"dictionaries\":{\"CM93OBJ.DIC\":true,\"ATTRLUT.DIC\":true},"
            << "\"regions\":" << regions << ","
            << "\"cells\":{"
            << "\"Z\":" << by_scale["Z"] << ","
            << "\"A\":" << by_scale["A"] << ","
            << "\"B\":" << by_scale["B"] << ","
            << "\"C\":" << by_scale["C"] << ","
            << "\"D\":" << by_scale["D"] << ","
            << "\"E\":" << by_scale["E"] << ","
            << "\"F\":" << by_scale["F"] << ","
            << "\"G\":" << by_scale["G"] << "},"
            << "\"cells_total\":" << total_cells << ","
            << "\"ok\":" << (total_cells>0 ? "true" : "false")
            << "}"
            << "\n";

  if (total_cells == 0) {
    std::cerr << "probe-cm93: dictionaries found but no cell files detected under Z..G\n";
    return 12; // parse/discovery error
  }
  return 0;
}

int main(int argc, char** argv) {
  if (argc >= 3 && std::string(argv[1]) == "probe-iso8211") {
    DDFModule module;
    if (!module.Open(argv[2], FALSE)) {
      std::cerr << "open failed" << std::endl;
      return 1;
    }
    std::cout << "fields=" << module.GetFieldCount() << std::endl;
    module.Close();
    return 0;
  }

  if (argc >= 3 && std::string(argv[1]) == "probe-cm93") {
    return probe_cm93(argv[2]);
  }

  std::cerr << "Usage:\n"
               "  ocpn_min probe-iso8211 <cell.000>\n"
               "  ocpn_min probe-cm93    <cm93_root>\n";
  return 10; // bad args
}

