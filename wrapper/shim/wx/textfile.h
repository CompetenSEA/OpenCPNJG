#pragma once
#include <string>
#include <vector>
#include "wx.h"

class wxTextFile {
public:
    bool Open(const wxString&){return true;}
    void Close(){}
    size_t GetLineCount() const {return lines.size();}
    wxString GetLine(size_t i) const {return lines[i];}
    void AddLine(const wxString& s){lines.push_back(s);}
    std::vector<wxString> lines;
};
