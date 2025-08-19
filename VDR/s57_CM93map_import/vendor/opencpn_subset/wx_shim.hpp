#pragma once
#include <string>
// Minimal shim to satisfy OpenCPN subset without pulling wxWidgets.
using wxString = std::string;
inline wxString _(const char* s){ return wxString(s); }
