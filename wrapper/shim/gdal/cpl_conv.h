#pragma once
#include "cpl_port.h"
#include <cstdlib>
#include <cstring>
inline void *CPLMalloc(size_t n){return std::malloc(n);} 
inline void CPLFree(void *p){std::free(p);} 
inline char *CPLStrdup(const char *s){return std::strdup(s);} 
