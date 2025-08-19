#pragma once
#include <string>
#include <vector>

// Minimal replacements for wxWidgets string utilities used by the vendored
// OpenCPN sources.  The goal is to keep the wrapper self contained without a
// wxWidgets dependency.
namespace ocpn { using String = std::string; }

using wxString = std::string;
using wxChar = char;

#define wxT(x) x
#define _T(x) x

inline std::string wxStringToStdString(const wxString& s) { return s; }
inline const char* wxCString(const wxString& s) { return s.c_str(); }

// A trivial tokenizer used by some OpenCPN code paths.
inline std::vector<std::string> wxStringTokenize(const wxString& s, const wxString& delim) {
    std::vector<std::string> out;
    size_t start = 0, end;
    while ((end = s.find_first_of(delim, start)) != std::string::npos) {
        out.push_back(s.substr(start, end - start));
        start = end + 1;
    }
    out.push_back(s.substr(start));
    return out;
}
