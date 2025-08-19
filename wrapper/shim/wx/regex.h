#pragma once
#include "wx.h"
#include <regex>

class wxRegEx {
public:
    wxRegEx(const wxString& pattern) : re(pattern) {}
    bool Matches(const wxString& text) const {
        return std::regex_match(text, re);
    }
private:
    std::regex re;
};
