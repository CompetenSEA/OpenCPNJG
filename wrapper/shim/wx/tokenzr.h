#pragma once
#include "wx.h"
class wxStringTokenizer {
public:
    wxStringTokenizer(const wxString& src, const wxString& delims)
        : tokens(wxStringTokenize(src, delims)), pos(0) {}
    bool HasMoreTokens() const { return pos < tokens.size(); }
    wxString GetNextToken() { return tokens[pos++]; }
private:
    std::vector<wxString> tokens;
    size_t pos;
};
