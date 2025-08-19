#pragma once
#include "wx.h"
#include <string>

class wxFileName {
public:
    wxFileName() = default;
    explicit wxFileName(const wxString& p): path(p) {}
    wxString GetFullPath() const { return path; }
    bool IsRelative() const { return false; }
private:
    wxString path;
};
