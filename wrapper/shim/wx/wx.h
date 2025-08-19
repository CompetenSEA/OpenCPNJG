#pragma once
#include "../strings.hpp"
#include "../log.hpp"
#include <cassert>

#define wxLogMessage(...) do { fprintf(stderr, __VA_ARGS__); fprintf(stderr, "\n"); } while(0)
#define wxLogError(...)   do { fprintf(stderr, __VA_ARGS__); fprintf(stderr, "\n"); } while(0)
#define wxASSERT(x) assert(x)
