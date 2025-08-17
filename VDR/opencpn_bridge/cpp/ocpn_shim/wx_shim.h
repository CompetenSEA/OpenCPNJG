#pragma once

#include <string>
#include <cassert>

using wxString = std::string;
using wxChar = char;

#define wxT(x) x
#define _(x) x
#define wxASSERT(expr) assert(expr)
#define wxLogMessage(...)

struct wxPoint {
  int x{0};
  int y{0};
  wxPoint() = default;
  wxPoint(int x_, int y_) : x(x_), y(y_) {}
};

struct wxSize {
  int x{0};
  int y{0};
  wxSize() = default;
  wxSize(int x_, int y_) : x(x_), y(y_) {}
};

struct wxRect {
  int x{0};
  int y{0};
  int width{0};
  int height{0};
  wxRect() = default;
  wxRect(int x_, int y_, int w_, int h_) : x(x_), y(y_), width(w_), height(h_) {}
};

inline wxString wxStringFromUTF8(const char* s) { return s ? wxString(s) : wxString(); }
