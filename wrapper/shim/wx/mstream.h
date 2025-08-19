#pragma once
#include "wx.h"
#include <sstream>

class wxMemoryOutputStream {
public:
    std::ostringstream ss;
    void Write(const void* data, size_t size) { ss.write(static_cast<const char*>(data), size); }
};

class wxMemoryInputStream {
public:
    wxMemoryInputStream(const char* data, size_t size) : ss(std::string(data, size)) {}
    std::istringstream ss;
};
