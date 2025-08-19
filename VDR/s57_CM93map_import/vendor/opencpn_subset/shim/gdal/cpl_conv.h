#pragma once
#include <cstddef>
#include <cstdlib>
#include <cstring>

void *CPLMalloc(std::size_t nBytes);
void CPLFree(void *p);
void *CPLCalloc(std::size_t nCount, std::size_t nSize);
void *CPLRealloc(void *p, std::size_t nNewSize);
char *CPLStrdup(const char *s);
