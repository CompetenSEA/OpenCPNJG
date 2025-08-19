#include "cpl_conv.h"

void *CPLMalloc(std::size_t nBytes) { return std::malloc(nBytes); }
void CPLFree(void *p) { std::free(p); }
void *CPLCalloc(std::size_t nCount, std::size_t nSize) { return std::calloc(nCount, nSize); }
void *CPLRealloc(void *p, std::size_t nNewSize) { return std::realloc(p, nNewSize); }
char *CPLStrdup(const char *s) { return s ? std::strdup(s) : nullptr; }
