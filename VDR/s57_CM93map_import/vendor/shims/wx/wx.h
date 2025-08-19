#pragma once
#include <string>
#include <vector>
#include <cstdint>
using wxString = std::string;
struct wxRect { int x{}, y{}, width{}, height{}; };
struct wxPoint { int x{}, y{}; };
inline void wxLogMessage(const char*) {}
inline void wxLogWarning(const char*) {}
inline void wxLogError(const char*) {}
