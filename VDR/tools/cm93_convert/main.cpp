#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <sqlite3.h>

struct Feature {
  int id;
  std::string geojson;
};

using FeatureList = std::vector<Feature>;

static FeatureList load_csv(const std::filesystem::path& file,
                            const std::string& geom_type) {
  FeatureList feats;
  std::ifstream ifs(file);
  if (!ifs.is_open()) return feats;
  std::string line;
  int id = 1;
  while (std::getline(ifs, line)) {
    std::stringstream ss(line);
    std::vector<double> nums;
    std::string tok;
    while (std::getline(ss, tok, ',')) {
      try {
        nums.push_back(std::stod(tok));
      } catch (...) {
        nums.push_back(0.0);
      }
    }
    std::ostringstream geom;
    if (geom_type == "Point" && nums.size() >= 2) {
      geom << "{\"type\":\"Point\",\"coordinates\":[" << nums[0] << ","
           << nums[1] << "]}";
    } else if (geom_type == "LineString" && nums.size() >= 4) {
      geom << "{\"type\":\"LineString\",\"coordinates\":[[" << nums[0] << ","
           << nums[1] << "],[" << nums[2] << "," << nums[3] << "]]}";
    } else if (geom_type == "Polygon" && nums.size() >= 6) {
      geom << "{\"type\":\"Polygon\",\"coordinates\":[[[" << nums[0] << ","
           << nums[1] << "],[" << nums[2] << "," << nums[3] << "],[" << nums[4]
           << "," << nums[5] << "]]]}";
    } else {
      continue;
    }
    std::ostringstream feat;
    feat << "{\"type\":\"Feature\",\"geometry\":" << geom.str()
         << ",\"properties\":{\"id\":" << id++ << "}}";
    feats.push_back({id - 1, feat.str()});
  }
  return feats;
}

static void write_geojson(const std::filesystem::path& file,
                          const FeatureList& feats) {
  std::ofstream ofs(file);
  ofs << "{\"type\":\"FeatureCollection\",\"features\":[";
  for (size_t i = 0; i < feats.size(); ++i) {
    if (i) ofs << ",";
    ofs << feats[i].geojson;
  }
  ofs << "]}";
}

static void write_gpkg(const std::filesystem::path& file,
                       const std::string& table, const FeatureList& feats) {
  sqlite3* db = nullptr;
  if (sqlite3_open(file.c_str(), &db) != SQLITE_OK) return;
  std::string create = "CREATE TABLE IF NOT EXISTS " + table +
                       "(id INTEGER PRIMARY KEY, geojson TEXT)";
  sqlite3_exec(db, create.c_str(), nullptr, nullptr, nullptr);
  std::string insert = "INSERT INTO " + table + "(id, geojson) VALUES (?, ?)";
  sqlite3_stmt* stmt = nullptr;
  sqlite3_prepare_v2(db, insert.c_str(), -1, &stmt, nullptr);
  for (const auto& f : feats) {
    sqlite3_bind_int(stmt, 1, f.id);
    sqlite3_bind_text(stmt, 2, f.geojson.c_str(), -1, SQLITE_STATIC);
    sqlite3_step(stmt);
    sqlite3_reset(stmt);
  }
  sqlite3_finalize(stmt);
  sqlite3_close(db);
}

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
    std::cerr
        << "usage: cm93_convert --src <cm93_root> --out <dir> --schema vdr"
        << std::endl;
    return 1;
  }

  std::filesystem::create_directories(out);
  auto pts = load_csv(std::filesystem::path(src) / "pts.csv", "Point");
  auto ln = load_csv(std::filesystem::path(src) / "ln.csv", "LineString");
  auto ar = load_csv(std::filesystem::path(src) / "ar.csv", "Polygon");

  write_geojson(std::filesystem::path(out) / "pts.geojson", pts);
  write_geojson(std::filesystem::path(out) / "ln.geojson", ln);
  write_geojson(std::filesystem::path(out) / "ar.geojson", ar);

  auto gpkg = std::filesystem::path(out) / "cm93.gpkg";
  write_gpkg(gpkg, "cm93_pts", pts);
  write_gpkg(gpkg, "cm93_ln", ln);
  write_gpkg(gpkg, "cm93_ar", ar);
  return 0;
}
