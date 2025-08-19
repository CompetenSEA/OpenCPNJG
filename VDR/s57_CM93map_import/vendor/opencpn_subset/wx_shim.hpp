#pragma once
#include <string>
#include <vector>

using wxString = std::string;
using wxChar = char;
#define _T(x) x

template<typename T> using wxArray = std::vector<T>;
template<typename T> using wxList = std::vector<T>;
using wxArrayPtrVoid = std::vector<void*>;

#define WX_DECLARE_OBJARRAY(type, name) using name = std::vector<type>;
#define WX_DEFINE_OBJARRAY(name)
