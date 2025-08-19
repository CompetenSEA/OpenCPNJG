#pragma once
#include "cpl_port.h"
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>

inline char **CSLAddString(char **papszList, const char *pszStr) {
    size_t n = 0;
    if (papszList) { while(papszList[n]) n++; }
    char **pnew = (char**)std::realloc(papszList, (n+2)*sizeof(char*));
    pnew[n] = std::strdup(pszStr);
    pnew[n+1] = nullptr;
    return pnew;
}

inline void CSLDestroy(char **papszList) {
    if (!papszList) return;
    for(char **p = papszList; *p; ++p) std::free(*p);
    std::free(papszList);
}

inline int CSLCount(char **papszList) {
    int n=0; if(papszList) while(papszList[n]) n++; return n;
}

inline char **CSLTokenizeStringComplex(const char *pszString, const char *pszDelimiters, int, int) {
    char *dup = std::strdup(pszString);
    char *token = std::strtok(dup, pszDelimiters);
    char **list = nullptr;
    while(token){ list = CSLAddString(list, token); token = std::strtok(nullptr, pszDelimiters); }
    std::free(dup);
    return list;
}
