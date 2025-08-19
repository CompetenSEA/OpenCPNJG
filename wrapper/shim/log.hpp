#pragma once
#include <iostream>

namespace ocpn {
inline void log(const std::string& m) { std::cerr << m << std::endl; }
inline void log_error(const std::string& m) { std::cerr << "error: " << m << std::endl; }
inline void log_info(const std::string& m) { std::cerr << "info: " << m << std::endl; }
}
